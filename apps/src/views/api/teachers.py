import math
from re import search
import time
from django.contrib.auth import authenticate
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.core.mail import message
from django.http import response
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_405_METHOD_NOT_ALLOWED
)
from rest_framework.response import Response
from apps.src.decorators.teachers_api import validate_teachers_api, validatePOST
from utils.helper import *
from ...models import *
import json
from rest_framework.renderers import JSONRenderer
from django.http import JsonResponse
import ast
from django.db.models import F


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    if request.data.get("username") == '':  
        return Response({'message': 'Please provide username', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("password") == '':
        return Response({'message': 'Please provide password', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("username") is None or request.data.get("password") is None:
        return Response({'message': 'Please provide both username and password', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    
    try:
        user_details = SpUsers.objects.filter(status=1, user_type=1, official_email=request.data.get("username")).first()
    except SpUsers.DoesNotExist:
        user_details = None
    if user_details:
        username = request.data.get("username")
    else:        
        username = None
    error_msg = 'Invalid Email Id'

    if not user_details:
        return Response({'message': error_msg, 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)

    username = username
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'message': 'Invalid Credentials', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)

    token, _ = Token.objects.get_or_create(user=user)
    fireBaseToken = request.data.get('firebase_token')
    if SpUsers.objects.filter(id=user.id).exclude(firebase_token=None).exists():
        firebase_token = SpUsers.objects.filter(id=user.id).exclude(firebase_token=None).first()
        if firebase_token:
            if firebase_token.firebase_token == fireBaseToken:
                pass
            else:
                SpUsers.objects.filter(id=user.id).update(firebase_token=fireBaseToken)
    else:
        SpUsers.objects.filter(id=user.id).update(firebase_token=fireBaseToken)
    user_details = SpUsers.objects.filter(status=1, id=user.id).values()
    if user.middle_name:
        user_name   = user.first_name+' '+user.middle_name+' '+user.last_name
    else:
        user_name   = user.first_name+' '+user.last_name
    heading     = user_name+' has been logged In'
    activity    = user_name+' has been logged In on '+ datetime.now().strftime('%d/%m/%Y | %I:%M %p') 

    saveActivity('Login', 'Login', heading, activity, user.id, user_name, 'login.png', '2', 'app.png')

    if request.data.get("device_id") != '' :
        current_user = SpUsers.objects.get(id=user.id)
        current_user.device_id = request.data.get("device_id")
        current_user.save()

    token_update = SpUsers.objects.get(id=user.id)
    token_update.api_token = token.key
    token_update.save()
    branches = TblBranch.objects.filter(college_id = user_details[0]['organization_id'])
    branch_data = []
    for each_branch in branches:
        branch_json  = {}
        branch_json['id'] = each_branch.id
        branch_json['branch_name'] = each_branch.abbr
        branch_data.append(branch_json)
    
    all_support_staff = SpUsers.objects.raw(""" SELECT * FROM sp_users WHERE organization_id = %s AND id <> %s ORDER By first_name ASC;""", (user_details[0]['organization_id'], user_details[0]['id'], ) )
    support_data = []
    for each_support in all_support_staff:
        support_staff_json = {}
        support_staff_json['id'] = each_support.id
        support_staff_json['name'] = getModelColumnById(SpUsers, each_support.id, 'first_name')+" "+getModelColumnById(SpUsers, each_support.id, 'middle_name')+" "+getModelColumnById(SpUsers, each_support.id, 'last_name')
        support_data.append(support_staff_json)

    semester_data = []
    all_semester = TblSemester.objects.filter(type = "semester")
    for each_semester in all_semester:
            semester_json = {}
            semester_json['semester_id'] = each_semester.semester_id
            semester_json['semester_name'] = each_semester.sem_name
            semester_data.append(semester_json)

    context = {}
    context['token']                    = token.key
    context['states']                   = TblStates.objects.all().values('id', 'country_id', 'country_name', 'state')
    context['branch']                   = branch_data
    context['semester']                 = semester_data
    context['support_staff']            = support_data
    context['visit_recording_limit']    = 60
    context['user_details']             = user_details
    context['message']                  = 'Login successfully'
    context['firebase_token']           = fireBaseToken
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)



@csrf_exempt
@api_view(['POST'])
@validate_teachers_api
def filterResult(request):
    if request.method == 'POST':
        visit_filter = request.data.get("visit_filter")
        semester_filter = request.data.get("semester_filter")
        branch_filter = request.data.get("branch_filter")
        acad_year = request.data.get("year")
        search_key = ''
        if request.data.get('search_key'):
            search_key = request.data.get('search_key')
            reg_search = str("%"+search_key+"%")

        if visit_filter != "" and semester_filter != "" and branch_filter != "" and acad_year != "":
            filter_result = TblStudents.objects.filter(visit_status = visit_filter).filter(semester_id = semester_filter).filter(branch_id = branch_filter).filter(reg_no__regex = r'%s'%acad_year)

        elif visit_filter != "" and semester_filter != "" and branch_filter != "" and acad_year == "":
            filter_result = TblStudents.objects.filter(visit_status = visit_filter).filter(semester_id = semester_filter).filter(branch_id = branch_filter)

        elif visit_filter != "" and semester_filter != "" and branch_filter == "" and acad_year != "":
            filter_result = TblStudents.objects.filter(visit_status = visit_filter).filter(semester_id = semester_filter).filter(reg_no__regex = r'%s'%acad_year)

        elif visit_filter != "" and semester_filter == "" and branch_filter != "" and acad_year != "":
            filter_result = TblStudents.objects.filter(visit_status = visit_filter).filter(branch_id = branch_filter).filter(reg_no__regex = r'%s'%acad_year)

        elif visit_filter == "" and semester_filter != "" and branch_filter != "" and acad_year != "":
            filter_result = TblStudents.objects.filter(semester_id = semester_filter).filter(branch_id = branch_filter).filter(reg_no__regex = r'%s'%acad_year)


        elif visit_filter == "" and semester_filter == "" and branch_filter != "" and acad_year != "":
            filter_result = TblStudents.objects.filter(branch_id = branch_filter).filter(reg_no__regex = r'%s'%acad_year)
        
        elif visit_filter == "" and semester_filter != "" and branch_filter == "" and acad_year != "":
            filter_result = TblStudents.objects.filter(semester_id = semester_filter).filter(reg_no__regex = r'%s'%acad_year)
        
        elif visit_filter == "" and semester_filter != "" and branch_filter != "" and acad_year == "":
            filter_result = TblStudents.objects.filter(semester_id = semester_filter).filter(branch_id = branch_filter)


        elif visit_filter != "" and semester_filter == "" and branch_filter == "" and acad_year == "":
            filter_result = TblStudents.objects.filter(visit_status = visit_filter)

        elif visit_filter == "" and semester_filter != "" and branch_filter == "" and acad_year == "":
            filter_result = TblStudents.objects.filter(semester_id = semester_filter)

        elif visit_filter == "" and semester_filter == "" and branch_filter != "" and acad_year == "":
            filter_result = TblStudents.objects.filter(branch_id = branch_filter)
        
        elif visit_filter == "" and semester_filter == "" and branch_filter == "" and acad_year != "":
            filter_result = TblStudents.objects.filter(reg_no__regex = r'%s'%acad_year)

        else:
            filter_result = TblStudents.objects.all()

        if search_key != '':
            print("Search Key: ", search_key)
            search_result = filter_result.filter(reg_no__regex = r'%s'%reg_search)
            for each_row in search_result:
                print("Search Result: ", each_row.id, each_row.reg_no, getStudentName(each_row.id))

        content_data = []
        for each_result in filter_result:
            registered_data = {}
            semester = TblSemester.objects.filter(semester_id = each_result.semester_id)
            branch = TblBranch.objects.filter(id = each_result.branch_id)

            if each_result.profile_image:
                registered_data['profile_pic'] = "http://bipe.sortstring.co.in/"+str(each_result.profile_image)
            else:
                registered_data['profile_pic'] = each_result.profile_image

            registered_data['name'] = getStudentName(each_result.id)
            registered_data['branch'] = branch[0].branch
            registered_data['semester'] = semester[0].sem_name
            registered_data['semester_id'] = each_result.semester_id
            registered_data['registration_id'] = each_result.reg_no
            registered_data['mother_name'] = each_result.mother_name
            registered_data['father_name'] = each_result.father_name
            registered_data['phone'] = each_result.primary_contact_no
            registered_data['visit_status'] = each_result.visit_status
            content_data.append(registered_data)

        context = {}
        context['total_result'] = len(filter_result)
        context['result'] = content_data
        context['message'] = "Successful"
        context['response_status'] = HTTP_200_OK
        return Response(context, status=HTTP_200_OK)
    else:
        return Response({"message":"Method Not Allowed"}, status=HTTP_405_METHOD_NOT_ALLOWED)

@csrf_exempt
@validatePOST
@validate_teachers_api
@renderer_classes((JSONRenderer))
def getRegisteredList(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        page_limit  = int(request_data["page_limit"])*15
        offset      = int(page_limit)-15
        page_limit  = 15
        sort_flag = request_data['sort_flag']
        _number_of_rows = 0
        visit_filter = request_data['visit_filter']
        semester_filter = request_data['semester_filter']
        branch_filter = request_data['branch_filter']
        acad_year = request_data['year']
        if acad_year != "":
            acad_year = "%"+acad_year+"%"
            
        try:
            if request_data['search_key']:
                search_key = request_data['search_key']
                reg_search = str("%"+search_key+"%")
                if visit_filter != "" and semester_filter != "" and branch_filter != "" and acad_year != "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s ;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter,   branch_filter, semester_filter, acad_year, page_limit, offset) )

                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter,   branch_filter, semester_filter, acad_year, page_limit, offset) )

                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter,   branch_filter, semester_filter, acad_year, page_limit, offset) )

                    else:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s);", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s);", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter,   branch_filter, semester_filter, acad_year, page_limit, offset) )
           
 
                elif visit_filter != "" and semester_filter != "" and branch_filter != "" and acad_year == "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY first_name ASC LIMIT %s OFFSET %s", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY first_name DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY first_name DESC LIMIT %s OFFSET %s", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY visit_status ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY visit_status DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter, page_limit, offset) )
                    # else:
                    #     filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s);", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter) )
                    #     _number_of_rows = len(filter_result)
                    #     filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND semester_id = %s) LIMIT %s OFFSET %s", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, semester_filter, page_limit, offset) )

                elif visit_filter != "" and semester_filter == "" and branch_filter != "" and acad_year != "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, acad_year, page_limit, offset) )

                elif visit_filter != "" and semester_filter != "" and branch_filter == "" and acad_year != "":
                    # filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter,  semester_filter, acad_year) )

                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter,  semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter,  semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter,  semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter,  semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter,  semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter,  semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter,  semester_filter, acad_year, page_limit, offset) )

                elif visit_filter == "" and semester_filter != "" and branch_filter != "" and acad_year != "":
                    # filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s);", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter, acad_year) )
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter, acad_year, page_limit, offset) )

                elif visit_filter == "" and semester_filter == "" and branch_filter != "" and acad_year != "":
                    # filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, acad_year) )

                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, acad_year, page_limit, offset) )

                elif visit_filter == "" and semester_filter != "" and branch_filter == "" and acad_year != "":
                    # filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter, acad_year) )

                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter, acad_year, page_limit, offset) )

                elif visit_filter == "" and semester_filter != "" and branch_filter != "" and acad_year == "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s) ORDER BY visit_status ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s) ORDER BY visit_status DESC ;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s AND semester_id = %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, semester_filter, page_limit, offset) )
                    

                elif visit_filter != "" and semester_filter != "" and branch_filter == "" and acad_year == "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, semester_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s) ORDER BY first_name DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, semester_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s) ORDER BY visit_status ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, semester_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s) ORDER BY visit_status DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, semester_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND semester_id = %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, semester_filter, page_limit, offset) )

                elif visit_filter != "" and semester_filter == "" and branch_filter != "" and acad_year == "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s) ORDER BY first_name DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s) ORDER BY visit_status ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s) ORDER BY visit_status DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND branch_id = %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, branch_filter, page_limit, offset) )
                    
                elif visit_filter != "" and semester_filter == "" and branch_filter == "" and acad_year != "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, acad_year, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND reg_no LIKE %s) ORDER BY first_name DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, acad_year, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND reg_no LIKE %s) ORDER BY visit_status ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, acad_year, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND reg_no LIKE %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND reg_no LIKE %s) ORDER BY visit_status DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, acad_year, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s AND reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, acad_year, page_limit, offset) )

                elif visit_filter != "" and semester_filter == "" and branch_filter == "" and acad_year == "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s) ORDER BY visit_status ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s) ORDER BY visit_status DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (visit_status = %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, visit_filter, page_limit, offset) )

                elif visit_filter == "" and semester_filter != "" and branch_filter == "" and acad_year == "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter,) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s) ORDER BY first_name DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter,) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s) ORDER BY visit_status ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter,) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s) ORDER BY visit_status DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter,) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (semester_id = %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, semester_filter, page_limit, offset) )

                elif visit_filter == "" and semester_filter == "" and branch_filter != "" and acad_year == "":
                    # filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter) )
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (branch_id = %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, branch_filter, page_limit, offset) )
                
                elif visit_filter == "" and semester_filter == "" and branch_filter == "" and acad_year != "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (reg_no LIKE %s) ORDER BY first_name DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, acad_year, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, acad_year, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (reg_no LIKE %s) ORDER BY visit_status ASC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (reg_no LIKE %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, acad_year, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (reg_no LIKE %s) ORDER BY visit_status DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ) AND (reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, acad_year, page_limit, offset) )

                else:
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s AND reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ORDER BY first_name ASC; ", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s AND reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ORDER BY first_name ASC LIMIT %s OFFSET %s ; ", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, page_limit, offset, ) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s AND reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ORDER BY first_name DESC;", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s AND reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ORDER BY first_name DESC LIMIT %s OFFSET %s; ", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, page_limit, offset, ) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s AND reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ORDER BY visit_status ASC; ", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s AND reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ORDER BY visit_status ASC LIMIT %s OFFSET %s; ", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, page_limit, offset, ) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s AND reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ORDER BY visit_status DESC; ", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s AND reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s ORDER BY visit_status DESC LIMIT %s OFFSET %s; ", (request_data['organization_id'], reg_search, search_key, search_key, search_key, search_key, page_limit, offset, ) )

         
            elif request_data['search_key'] == "":
                if visit_filter != "" and semester_filter != "" and branch_filter != "" and acad_year != "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], visit_filter, branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, branch_filter, semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC;", (request_data['organization_id'], visit_filter, branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s ;", (request_data['organization_id'], visit_filter,   branch_filter, semester_filter, acad_year, page_limit, offset) )

                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC;", (request_data['organization_id'], visit_filter, branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter,   branch_filter, semester_filter, acad_year, page_limit, offset) )

                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC;", (request_data['organization_id'], visit_filter, branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter,   branch_filter, semester_filter, acad_year, page_limit, offset) )

                    else:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s);", (request_data['organization_id'], visit_filter, branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s AND reg_no LIKE %s);", (request_data['organization_id'], visit_filter,   branch_filter, semester_filter, acad_year, page_limit, offset) )
           
 
                elif visit_filter != "" and semester_filter != "" and branch_filter != "" and acad_year == "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], visit_filter, branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY first_name ASC LIMIT %s OFFSET %s", (request_data['organization_id'], visit_filter, branch_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY first_name DESC;", (request_data['organization_id'], visit_filter, branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY first_name DESC LIMIT %s OFFSET %s", (request_data['organization_id'], visit_filter, branch_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY visit_status ASC;", (request_data['organization_id'], visit_filter, branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s", (request_data['organization_id'], visit_filter, branch_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY visit_status DESC;", (request_data['organization_id'], visit_filter, branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s", (request_data['organization_id'], visit_filter, branch_filter, semester_filter, page_limit, offset) )
                    else:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s);", (request_data['organization_id'], visit_filter, branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND semester_id = %s) LIMIT %s OFFSET %s", (request_data['organization_id'], visit_filter, branch_filter, semester_filter, page_limit, offset) )

                elif visit_filter != "" and semester_filter == "" and branch_filter != "" and acad_year != "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC", (request_data['organization_id'], visit_filter, branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s", (request_data['organization_id'], visit_filter, branch_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC", (request_data['organization_id'], visit_filter, branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s", (request_data['organization_id'], visit_filter, branch_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC", (request_data['organization_id'], visit_filter, branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s", (request_data['organization_id'], visit_filter, branch_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC", (request_data['organization_id'], visit_filter, branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s", (request_data['organization_id'], visit_filter, branch_filter, acad_year, page_limit, offset) )

                elif visit_filter != "" and semester_filter != "" and branch_filter == "" and acad_year != "":
                    # filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], visit_filter,  semester_filter, acad_year) )

                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], visit_filter,  semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter,  semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC;", (request_data['organization_id'], visit_filter,  semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter,  semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC;", (request_data['organization_id'], visit_filter,  semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC;", (request_data['organization_id'], visit_filter,  semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter,  semester_filter, acad_year, page_limit, offset) )

                elif visit_filter == "" and semester_filter != "" and branch_filter != "" and acad_year != "":
                    # filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s);", (request_data['organization_id'], branch_filter, semester_filter, acad_year) )
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC;", (request_data['organization_id'], branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC;", (request_data['organization_id'], branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC;", (request_data['organization_id'], branch_filter, semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, semester_filter, acad_year, page_limit, offset) )

                elif visit_filter == "" and semester_filter == "" and branch_filter != "" and acad_year != "":
                    # filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], branch_filter, acad_year) )

                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC;", (request_data['organization_id'], branch_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, acad_year, page_limit, offset) )

                elif visit_filter == "" and semester_filter != "" and branch_filter == "" and acad_year != "":
                    # filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], semester_filter, acad_year) )

                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC;", (request_data['organization_id'], semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s AND reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC;", (request_data['organization_id'], semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], semester_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC;", (request_data['organization_id'], semester_filter, acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s AND reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], semester_filter, acad_year, page_limit, offset) )

                elif visit_filter == "" and semester_filter != "" and branch_filter != "" and acad_year == "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s) ORDER BY visit_status ASC;", (request_data['organization_id'], branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s) ORDER BY visit_status DESC ;", (request_data['organization_id'], branch_filter, semester_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s AND semester_id = %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, semester_filter, page_limit, offset) )

                elif visit_filter != "" and semester_filter != "" and branch_filter == "" and acad_year == "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], visit_filter, semester_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s) ORDER BY first_name DESC;", (request_data['organization_id'], visit_filter, semester_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s) ORDER BY visit_status ASC;", (request_data['organization_id'], visit_filter, semester_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, semester_filter, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s) ORDER BY visit_status DESC;", (request_data['organization_id'], visit_filter, semester_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND semester_id = %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, semester_filter, page_limit, offset) )

                elif visit_filter != "" and semester_filter == "" and branch_filter != "" and acad_year == "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], visit_filter, branch_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, branch_filter, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s) ORDER BY first_name DESC;", (request_data['organization_id'], visit_filter, branch_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, branch_filter, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s) ORDER BY visit_status ASC;", (request_data['organization_id'], visit_filter, branch_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, branch_filter, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s) ORDER BY visit_status DESC;", (request_data['organization_id'], visit_filter, branch_filter, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND branch_id = %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, branch_filter, page_limit, offset) )
                    
                elif visit_filter != "" and semester_filter == "" and branch_filter == "" and acad_year != "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], visit_filter, acad_year, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND reg_no LIKE %s) ORDER BY first_name DESC;", (request_data['organization_id'], visit_filter, acad_year, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND reg_no LIKE %s) ORDER BY visit_status ASC;", (request_data['organization_id'], visit_filter, acad_year, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND reg_no LIKE %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, acad_year, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND reg_no LIKE %s) ORDER BY visit_status DESC;", (request_data['organization_id'], visit_filter, acad_year, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s AND reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, acad_year, page_limit, offset) )

                elif visit_filter != "" and semester_filter == "" and branch_filter == "" and acad_year == "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s) ORDER BY first_name ASC;", (request_data['organization_id'], visit_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s) ORDER BY first_name ASC;", (request_data['organization_id'], visit_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s) ORDER BY visit_status ASC;", (request_data['organization_id'], visit_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s) ORDER BY visit_status DESC;", (request_data['organization_id'], visit_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (visit_status = %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], visit_filter, page_limit, offset) )

                elif visit_filter == "" and semester_filter != "" and branch_filter == "" and acad_year == "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], semester_filter,) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], semester_filter, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s) ORDER BY first_name DESC;", (request_data['organization_id'], semester_filter,) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], semester_filter, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s) ORDER BY visit_status ASC;", (request_data['organization_id'], semester_filter,) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], semester_filter, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s) ORDER BY visit_status DESC;", (request_data['organization_id'], semester_filter,) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (semester_id = %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], semester_filter, page_limit, offset) )

                elif visit_filter == "" and semester_filter == "" and branch_filter != "" and acad_year == "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], branch_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s) ORDER BY first_name ASC;", (request_data['organization_id'], branch_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s) ORDER BY visit_status ASC;", (request_data['organization_id'], branch_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s) ORDER BY visit_status DESC;", (request_data['organization_id'], branch_filter) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (branch_id = %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], branch_filter, page_limit, offset) )
                
                elif visit_filter == "" and semester_filter == "" and branch_filter == "" and acad_year != "":
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s) ORDER BY first_name ASC;", (request_data['organization_id'], acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s) ORDER BY first_name ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], acad_year, page_limit, offset) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s) ORDER BY first_name DESC;", (request_data['organization_id'], acad_year, ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s) ORDER BY first_name DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], acad_year, page_limit, offset) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s) ORDER BY visit_status ASC;", (request_data['organization_id'], acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s) ORDER BY visit_status ASC LIMIT %s OFFSET %s;", (request_data['organization_id'], acad_year, page_limit, offset) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s) ORDER BY visit_status DESC;", (request_data['organization_id'], acad_year) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s AND (reg_no LIKE %s) ORDER BY visit_status DESC LIMIT %s OFFSET %s;", (request_data['organization_id'], acad_year, page_limit, offset) )

                else:
                    if sort_flag == 0:
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s ORDER BY first_name ASC; ", (request_data['organization_id'], ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s ORDER BY first_name ASC LIMIT %s OFFSET %s ; ", (request_data['organization_id'], page_limit, offset, ) )
                    elif sort_flag == 1:
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s ORDER BY first_name DESC;", (request_data['organization_id'], ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s ORDER BY first_name DESC LIMIT %s OFFSET %s; ", (request_data['organization_id'],page_limit, offset, ) )
                    elif sort_flag == 2:
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s ORDER BY visit_status ASC; ", (request_data['organization_id'], ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s ORDER BY visit_status ASC LIMIT %s OFFSET %s; ", (request_data['organization_id'], page_limit, offset, ) )
                    elif sort_flag == 3:
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s ORDER BY visit_status DESC; ", (request_data['organization_id'], ) )
                        _number_of_rows = len(filter_result)
                        filter_result = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE college_id = %s ORDER BY visit_status DESC LIMIT %s OFFSET %s; ", (request_data['organization_id'],  page_limit, offset, ) )
        except:
            TblStudents.DoesNotExist
            all_registered_students = None

        content_data = []

        if _number_of_rows is not None:
            _count = math.ceil(round(_number_of_rows/15, 2))
        else:
            _count = 0

        for each_student in filter_result:
            registered_data = {}
            semester = TblSemester.objects.filter(semester_id = each_student.semester_id)
            branch = TblBranch.objects.filter(id = each_student.branch_id)

            if each_student.profile_image:
                registered_data['profile_pic'] = "http://bipe.sortstring.co.in/"+str(each_student.profile_image)
            else:
                registered_data['profile_pic'] = each_student.profile_image

            registered_data['id']               = each_student.id
            registered_data['name']             = getStudentName(each_student.id)
            registered_data['branch']           = branch[0].branch
            registered_data['semester']         = semester[0].sem_name
            registered_data['semester_id']      = each_student.semester_id
            registered_data['registration_id']  = each_student.reg_no
            registered_data['mother_name']      = each_student.mother_name
            registered_data['father_name']      = each_student.father_name
            registered_data['phone']            = each_student.primary_contact_no
            registered_data['visit_status']     = each_student.visit_status
            content_data.append(registered_data)


        context = {}
        context['result_count']     = _number_of_rows
        context['page_count']       = _count
        context['content']          = content_data
        context['message']          = "Success"
        context['response_code']    = HTTP_200_OK

    return JsonResponse(context, status=HTTP_200_OK)


@csrf_exempt
@validate_teachers_api
@validatePOST
def getQuestionnaire(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        semester = request_data['semester']
        if semester in ["sem_1","sem_2"]:
            academic_year = 1
        elif semester in ["sem_3","sem_4"]:
            academic_year = 2
        elif semester in ["sem_5", "sem_6"]:
            academic_year = 3
        else:
            return Response({"message" : "Invalid Semester"})
        all_questions = TblQuestionnaire.objects.filter(academic_year = academic_year).filter(college_id = request_data['college_id'])
        question_data = []
        for each_question in all_questions:
            question = {}
            question['id'] = each_question.id
            question['question'] = each_question.question
            question['input_flag'] = each_question.input_flag
            question['input_type'] = each_question.input_type
            if each_question.input_flag:
                if each_question.input_type:
                    question['max_value'] = each_question.max_value
                question['max_length'] = each_question.max_length
                question['label'] = each_question.label
            question_data.append(question)
        
        context = {}
        context['content']          = question_data
        context['message']          = "Success"
        context['response_status']  =  HTTP_200_OK
    return JsonResponse(context, status = 200)

@csrf_exempt
@validate_teachers_api
@validatePOST
def VisitOTP(request):
    request_data = json.loads(request.body)
    otp = generateVisitOTP()
    try:
        visit_otp = TblVisitOtp.objects.filter(mobile_no = request_data['mob_no'])
    except TblVisitOtp.DoesNotExist:
        visit_otp = None
        return JsonResponse({'message':'Could not generate OTP for mentioned mobile number'}, status=HTTP_404_NOT_FOUND)
    
    if visit_otp:
        visit_otp = TblVisitOtp.objects.filter(mobile_no = request_data['mob_no']).delete()
    
    visiting_otp = TblVisitOtp()
    visiting_otp.mobile_no = request_data['mob_no']
    visiting_otp.student_id = request_data['student_id']
    visiting_otp.otp = otp
    visiting_otp.save()
    support = getUserName(request_data['faculty_id'])
    if request_data['support_staff'] is not None or request_data['support_staff'] != {} or request_data['support_staff'] != "":
        for support_id in request_data['support_staff']:
            support += ", "+getUserName(support_id)
    clg_num = getModelColumnById(SpOrganizations, request_data['college_id'], 'mobile_country_code')+"-"+getModelColumnById(SpOrganizations, request_data['college_id'], 'mobile_number')

    message = "BIPE गजोखर वाराणसी से ‘गृह सम्पर्क’ कार्यक्रम के अंतर्गत, हमारे प्रतिनिधि श्री {support} जी ने आपसे भेंट की है। संस्था को गुणवत्ता के लिए आपने {rate}/5 की रेटिंग दी है। {feedback} इस सूचना से यदि आप सहमत हैं तो, कृपया OTP {otp} हमारे प्रतिनिधि से साझा करें। किसी भी अन्य सुझाव अथवा समस्या को साझा करने के लिए कृपया {phone} पर संपर्क करें। BGIVNS,".format(support = support, rate=request_data['rate'], feedback = request_data['opinion'], otp=otp, phone=clg_num)
    sendSMS("BGIVNS", request_data['mob_no'], message)
    return JsonResponse({'message': 'OTP Saved in DB'}, status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
@validate_teachers_api
def postQuestionnaire(request):
    if request.method == 'POST':
        phone = request.data.get("phone")
        otp = TblVisitOtp.objects.filter(mobile_no = phone).values()
        visit_report = []
        visit_selfie = []
        visit_audio = []
        if request.data.get('otp') == otp[0]['otp']:
            home_visit = TblHomeVisit()
            home_visit.faculty_id                   = request.data.get('faculty_id')
            home_visit.student_id                   = request.data.get('id')
            home_visit.registration_no              = request.data.get('student_id')
            home_visit.college_id                   = request.data.get('college_id')
            home_visit.guardian_relation            = request.data.get('contact_person')
            home_visit.mob_no                       = request.data.get('phone')
            home_visit.address_hno                  = request.data.get('hno')
            home_visit.address_locality             = request.data.get('locality')
            home_visit.state_id                     = request.data.get('state_id')
            home_visit.district_id                  = request.data.get('district_id')
            home_visit.tehsil_id                    = request.data.get('tehsil_id')
            home_visit.village_id                   = request.data.get('village_id')
            home_visit.pincode                      = request.data.get('pincode')
            home_visit.semester                     = request.data.get('semester')
            home_visit.opinion                      = request.data.get('opinion')
            home_visit.rating                       = request.data.get('rate')
            home_visit.longitude                    = request.data.get('long')
            home_visit.latitude                     = request.data.get('lat')
            home_visit.answers                      = request.data.get('answer')
            home_visit.field_report                 = request.data.get('report')
            home_visit.selfie_with_parents          = request.data.get('selfie')
            home_visit.support_staff                = request.data.get('support_staff')
            storage = FileSystemStorage()
            if bool(request.FILES.get('report', False)) == True:
                for visit_report_record in request.FILES.getlist('report'):
                    timestamp = int(time.time())
                    session_record_filename = visit_report_record.name
                    temp = session_record_filename.split('.')
                    session_record_filename = 'visit_session_report'+str(timestamp)+"."+temp[(len(temp) - 1)]

                    visit_report_file = storage.save(session_record_filename, visit_report_record)
                    visit_report.append(storage.url(visit_report_file))
            else:
                visit_report = None
            if bool(request.FILES.get('selfie', False)) == True:
                for visit_selfie_record in request.FILES.getlist('selfie'):
                    timestamp = int(time.time())
                    session_record_filename = visit_selfie_record.name
                    temp = session_record_filename.split('.')
                    session_record_filename = 'visit_session_selfie'+str(timestamp)+"."+temp[(len(temp) - 1)]
                    
                    visit_selfie_file = storage.save(session_record_filename, visit_selfie_record)
                    visit_selfie.append(storage.url(visit_selfie_file))
            else:
                visit_selfie = None
            if bool(request.FILES.get('visit_recording', False)) == True:
                for visit_audio_record in request.FILES.getlist('visit_recording'):
                    timestamp = int(time.time())
                    session_record_filename = visit_audio_record.name
                    temp = session_record_filename.split('.')
                    session_record_filename = 'visit_session_record'+str(timestamp)+"."+temp[(len(temp) - 1)]
                    
                    visit_audio_file = storage.save(session_record_filename, visit_audio_record)
                    visit_audio.append(storage.url(visit_audio_file))
            else:
                visit_audio = None
            
            home_visit.field_report = visit_report
            home_visit.selfie_with_parents = visit_selfie
            home_visit.visit_audio = visit_audio
            student_id = TblStudents.objects.filter(reg_no = request.data.get('student_id')).values('id')
            student_name = getStudentName(student_id[0]['id'])
            clg_num = getModelColumnById(SpOrganizations, request.data.get('college_id'), 'mobile_country_code')+"-"+getModelColumnById(SpOrganizations, request.data.get('college_id'), 'mobile_number')
            
            attendance = ""
            scholarship = ""
            if request.data.get('answer') is not None or request.data.get('answer') != {} or request.data.get('answer') != "":
                answer_raw = request.data.get('answer')

                all_answers = json.loads(answer_raw)
                for each_answer in all_answers:
                    if each_answer['question_id'] == 5 or  each_answer['question_id'] == 12:
                        attendance = each_answer['value']+"%"
                    elif each_answer['question_id'] == 6 or  each_answer['question_id'] == 13:
                        scholarship = "₹"+each_answer['value']

            if request.data.get('semester') == "sem_1" or request.data.get('semester') == "sem_2":
                message = "प्रिय अभिभावक, BIPE गजोखर, वाराणसी के ‘गृह सम्पर्क कार्यक्रम’ के अंतर्गत, हमारे प्रतिनिधि द्वारा आपको {student_name} के सम्बंध में निम्न सूचनाओं से अवगत करवाया गया है: \n1. इस वर्ष, संस्था द्वारा उपस्थिति (80% से अधिक) के आधार पर मिलने वाली स्कॉलरशिप ₹3000-₹4000 है। \n2. उपस्थिति स्कालरशिप के लिए उपस्थिति की गणना 1/12/2021 से की जाएगी। \n3. संस्था की ओर से इस वर्ष, छात्र को निःशुल्क यूनिफार्म उपलब्ध कराया जा रहा है। \n4. संस्था द्वारा संचालित बस फैसिलिटी और रूट \n5. मात्र ₹600 में छात्र को दी जाने वाली बुक बैंक फैसिलिटी \nयदि आप उपरोक्त जानकारी से संतुष्ट नहीं है तो आप {phone} पर संपर्क करके अवगत करवाएँ। BGIVNS,".format(student_name = student_name, phone = clg_num)
            elif request.data.get('semester') == "sem_3" or request.data.get('semester') == "sem_4":
                message = "प्रिय अभिभावक, BIPE गजोखर, वाराणसी के ‘गृह सम्पर्क कार्यक्रम’ के अंतर्गत, हमारे प्रतिनिधि द्वारा आपको {student_name} के सम्बंध में निम्न सूचनाओं से अवगत करवाया गया है: \n1. विगत सेमेस्टर/सत्र में छात्र की उपस्थिति {attendance} रही है। जिसके आधार पर उसे {scholarship} की स्कालरशिप संस्था द्वारा प्रदान की गयी है। \n2. इस वर्ष, संस्था द्वारा उपस्थिति (80% से अधिक) के आधार पर मिलने वाली स्कॉलरशिप ₹3000-₹4000 है। \n3. उपस्थिति स्कालरशिप के लिए उपस्थिति की गणना 1/12/2021 से की जाएगी। \n4. संस्था की ओर से इस वर्ष, छात्र को निःशुल्क यूनिफार्म उपलब्ध कराया जा रहा है। साथ ही अंतिम सेमेस्टर में छात्र को संस्था द्वारा औपचारिक यूनिफार्म (कोट, टाई, शर्ट) भी निःशुल्क उपलब्ध कराया जाएगा। \n5. संस्था द्वारा संचालित बस फैसिलिटी और रूट \n6. मात्र ₹600 में छात्र को दी जाने वाली बुक बैंक फैसिलिटी \nयदि आप उपरोक्त जानकारी से संतुष्ट नहीं है तो आप {phone} पर संपर्क करके अवगत करवाएँ। \nBGIVNS,".format(student_name = student_name, attendance = attendance , scholarship = scholarship, phone=clg_num)
            elif request.data.get('semester') == "sem_5" or request.data.get('semester') == "sem_6":
                message = "प्रिय अभिभावक, BIPE गजोखर, वाराणसी के ‘गृह सम्पर्क कार्यक्रम’ के अंतर्गत, हमारे प्रतिनिधि द्वारा आपको {student_name} के सम्बंध में निम्न सूचनाओं से अवगत करवाया गया है:\n1. विगत सेमेस्टर/सत्र में छात्र की उपस्थिति {attendance} रही है। जिसके आधार पर उसे {scholarship} की स्कालरशिप संस्था द्वारा प्रदान की गयी है। \n2. इस वर्ष, संस्था द्वारा उपस्थिति (80% से अधिक) के आधार पर मिलने वाली स्कॉलरशिप ₹3000-₹4000 है। \n3. उपस्थिति स्कालरशिप के लिए उपस्थिति की गणना 1/12/2021 से की जाएगी। \n4. संस्था की ओर से इस वर्ष, छात्र को निःशुल्क यूनिफार्म उपलब्ध कराया जा रहा है। साथ ही अंतिम सेमेस्टर में छात्र को संस्था द्वारा औपचारिक यूनिफार्म (कोट, टाई, शर्ट) भी निःशुल्क उपलब्ध कराया जाएगा। \n5. संस्था द्वारा संचालित बस फैसिलिटी और रूट \n6. मात्र ₹600 में छात्र को दी जाने वाली बुक बैंक फैसिलिटी \nयदि आप उपरोक्त जानकारी से संतुष्ट नहीं है तो आप {phone} पर संपर्क करके अवगत करवाएँ। \nBGIVNS,".format(student_name = student_name, attendance = attendance , scholarship = scholarship, phone=clg_num)
            sendSMS('BGIVNS', request.data.get('phone'),message)
            home_visit.save()
            TblStudents.objects.filter(reg_no = request.data.get('student_id')).update(secondary_phone_no = request.data.get('phone'), secondary_phone_relative = request.data.get('contact_person'), address_hno = request.data.get('hno'), address_locality = request.data.get('locality'), state_id = request.data.get('state_id'), district_id=request.data.get('district_id'), tehsil_id = request.data.get('tehsil_id'), village_id = request.data.get('village_id'), visit_status = 1, last_visit_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            return JsonResponse( {"message":"Successfully saved the visited data"}, status = HTTP_200_OK )
        else:
            return JsonResponse({"message":"OTP invalid"})

@csrf_exempt
@validate_teachers_api
@validatePOST
def getDistrictUsingStateID(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        state_code = request_data['state_code']
        districts = TblNewDistrict.objects.filter(state_id = state_code)
        district_data = []
        for district in districts:
            district_json = {}
            district_json['id'] = district.id
            district_json['district_name'] = district.district_name
            district_data.append(district_json)
        
        context = {}
        context['all_districts'] = district_data
        context['message']       = "Success"
        context['response_status'] = HTTP_200_OK
        return JsonResponse(context, status=HTTP_200_OK)

@csrf_exempt
@validatePOST
@validate_teachers_api
def getTehsilUsingDistrictID(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        district_code = request_data['district_code']
        all_tehsil = TblNewTehsil.objects.filter(district_id = district_code)
        tehsil_data = []
        for each_tehsil in all_tehsil:
            tehsil_json = {}
            tehsil_json['id'] = each_tehsil.id
            tehsil_json['tehsil_name'] = each_tehsil.tehsil_name
            tehsil_data.append(tehsil_json)
        context = {}
        context['all_tehsil']   = tehsil_data
        context['message']      = "Success"
        context['response_status'] = HTTP_200_OK
        return JsonResponse(context, status=HTTP_200_OK)


@csrf_exempt
@validatePOST
@validate_teachers_api
def getVillageUsingTehsilID(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        block_code = request_data['tehsil_code']
        all_villages = TblNewVillage.objects.filter(tehsil_id = block_code)
        village_data = []
        for each_village in all_villages:
            village_json = {}
            village_json['id'] = each_village.id
            village_json['village_name'] = each_village.village_name
            village_data.append(village_json)
        
        context = {}
        context['all_villages'] = village_data
        context['message'] = "Success"
        context['response_status'] = HTTP_200_OK
        return JsonResponse(context, status= HTTP_200_OK)
        
from datetime import datetime
@csrf_exempt
@api_view(['POST'])
@validate_teachers_api
def HomePageAPI(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        college_id = request_data["organization_id"]
        faculty_id = request_data['faculty_id']
        today_visit = TblHomeVisit.objects.filter(college_id = college_id).filter(faculty_id = faculty_id).filter(created_at__icontains = datetime.now().today().date() )
        total_visit = TblHomeVisit.objects.filter(college_id = college_id).filter(faculty_id = faculty_id)

        current_date = datetime.now().date()
        each_faculty_visit = TblHomeVisit.objects.all().values('faculty_id').distinct()
        faculty_content = []

        for each_visit in each_faculty_visit:
            visit_dashboard = {}
            faculty_visit = TblHomeVisit.objects.filter(faculty_id = each_visit['faculty_id'])
            faculty_today = TblHomeVisit.objects.filter(faculty_id = each_visit['faculty_id']).filter(created_at__icontains = current_date)
            visit_dashboard['faculty_name'] = getUserName(each_visit['faculty_id'])
            visit_dashboard['total_visit'] = len(faculty_visit)
            visit_dashboard['today_visit'] = len(faculty_today)
            faculty_content.append(visit_dashboard)
        
        _week = {}
        dates_between = days_between_dates(current_date, (current_date-timedelta(6)))

        for each_day in dates_between:
            visit_week = TblHomeVisit.objects.filter(created_at__icontains = each_day).count()
            _day = calendar.day_name[datetime.strptime(each_day, "%Y-%m-%d").weekday()]
            _week[_day] = visit_week

        today_school_visit = TblSchoolVisit.objects.filter(visited_by = faculty_id, visited_datetime__icontains = datetime.now().today().date() ).count()
        total_school_visit = TblSchoolVisit.objects.filter(visited_by = faculty_id).count()
        
        today_individual_visit = TblIndividualVisit.objects.filter(visited_by = faculty_id, visited_datetime__icontains = datetime.now().today().date() ).count()
        total_individual_visit = TblIndividualVisit.objects.filter(visited_by = faculty_id).count()

        context = {}
        context['today_visit'] = len(today_visit)
        context['total_visit'] = len(total_visit)
        context['today_school_visit'] = today_school_visit
        context['total_school_visit'] = total_school_visit
        context['today_individual_visit'] = today_individual_visit
        context['total_individual_visit'] = total_individual_visit
        context['faculty_visit'] = faculty_content
        context['weekly'] = _week
        context['message'] = "Success"
        context['response_status'] = HTTP_200_OK

        return Response(context, status=HTTP_200_OK)

@csrf_exempt
@validatePOST
@validate_teachers_api
@renderer_classes((JSONRenderer))
def getVisitedStudents(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        page_limit  = int(request_data["page_limit"])*15
        offset      = int(page_limit)-15
        page_limit  = 15
        college_id = request_data['organization_id']
        faculty_id = request_data['faculty_id']
        try:
            if request_data['type'] == "all":
                total_visit = TblHomeVisit.objects.filter(college_id = college_id).filter(faculty_id = faculty_id).order_by('-created_at')
            elif request_data['type'] == "today":
                total_visit = TblHomeVisit.objects.filter(college_id = college_id).filter(faculty_id = faculty_id).filter(created_at__icontains = datetime.now().today().date() )  
        except:
            TblHomeVisit.DoesNotExist
            total_visit = None
        content_data = []
        for each_visit in total_visit:
            visited_data = {}
            try:
                student_info = TblStudents.objects.filter(id = each_visit.student_id)
            except TblStudents.DoesNotExist:
                student_info = None
            if student_info:
                branch = TblBranch.objects.filter(id = student_info[0].branch_id)
                semester = TblSemester.objects.filter(semester_id = student_info[0].semester_id)

                visited_data['name'] = getStudentName(student_info[0].id)
                visited_data['student_id'] = student_info[0].id
                visited_data['branch'] = branch[0].branch
                visited_data['semester'] = semester[0].sem_name
                visited_data['semester_id'] = student_info[0].semester_id
                visited_data['registration_id'] = student_info[0].reg_no
                visited_data['mother_name'] = student_info[0].mother_name
                visited_data['father_name'] = student_info[0].father_name
                visited_data['phone'] = student_info[0].primary_contact_no
                visited_data['visit_status'] = student_info[0].visit_status
                visited_data['visited_datetime'] = each_visit.created_at
                
                if student_info[0].profile_image:
                    visited_data['profile_pic'] = "http://bipe.sortstring.co.in/"+str(student_info[0].profile_image)
                else:
                    visited_data['profile_pic'] = ''
                content_data.append(visited_data)

        context = {}
        context['content']          = content_data
        context['message']          = "Success"
        context['response_code']    = HTTP_200_OK

    return JsonResponse(context, status=HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def visitedStudentDetail(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        student_id = request_data['student_id']
        try:
            visited_form = TblHomeVisit.objects.filter(student_id = student_id)

            if visited_form is None or visited_form.values() == "" or visited_form.values() == []:
                return Response({"message": "No content available"}, status=HTTP_404_NOT_FOUND)
            form_data = {}
            for info in visited_form:
                student_info = TblStudents.objects.filter(id = info.student_id)
                if student_info[0].profile_image:
                    form_data['profile_pic'] = "http://bipe.sortstring.co.in/"+str(student_info[0].profile_image)
                else:
                    form_data['profile_pic'] = student_info[0].profile_image
                
                branch = TblBranch.objects.filter(id = student_info[0].branch_id)
                semester = TblSemester.objects.filter(semester_id = student_info[0].semester_id)
                address = student_info[0].address_hno +", "+ student_info[0].address_locality +", "+ TblNewVillage.objects.filter(id = info.village_id).values('village_name')[0]['village_name']+", "+TblNewTehsil.objects.filter(id = info.tehsil_id).values('tehsil_name')[0]['tehsil_name']+", "+TblNewDistrict.objects.filter(id = info.district_id).values('district_name')[0]['district_name'] +", "+ TblStates.objects.filter(id = info.state_id).values('state_name')[0]['state_name']

                form_data['student_name']       = getStudentName(student_info[0].id)
                form_data['student_id']         = info.registration_no
                form_data['latitude']           = info.latitude
                form_data['longitude']          = info.longitude
                form_data['student_mob']        = student_info[0].primary_contact_no
                form_data['branch']             = branch[0].branch
                form_data['semester']           = semester[0].sem_name
                form_data['relative_mob']       = info.mob_no
                form_data['relative']           = info.guardian_relation
                form_data['father']             = student_info[0].father_name
                form_data['mother']             = student_info[0].mother_name
                form_data['address']            = address
                form_data['visit_status']       = student_info[0].visit_status
                form_data['visit_datetime']     = student_info[0].last_visit_datetime
                form_data['rating']             = info.rating
                all_answers = json.loads(info.answers)
                questionnaire_data = []
                for each_answer in all_answers:
                    answer_dict = {}
                    question_id = each_answer['question_id']
                    each_question = TblQuestionnaire.objects.filter(id = question_id).values('question', 'label')
                    answer_dict['question'] = each_question[0]['question']
                    answer_dict['answered'] = each_answer['is_answered']
                    if each_answer['value'] != "" and (question_id == 6 or question_id == 12):
                        answer_dict['value'] = each_question[0]['label'] + each_answer['value']
                    elif each_answer['value'] != "" and (question_id == 5 or question_id == 13):
                        answer_dict['value'] = each_answer['value']+each_question[0]['label']
                    questionnaire_data.append(answer_dict)
                form_data['answers'] = questionnaire_data
                all_staff = json.loads(info.support_staff)
                staff_data = []
                for each_staff in all_staff:
                    staff_dict = {}
                    staff_dict['id'] = each_staff['id']
                    staff_dict['name'] = each_staff['name']
                    staff_data.append(staff_dict)
                
                form_data['support_staff'] = staff_data
                
            if info.visit_audio == "" or info.visit_audio is None:
                form_data['audio_recording'] = info.visit_audio
            else:
                form_data['audio_recording'] = ast.literal_eval(info.visit_audio)
            if ast.literal_eval(info.field_report) == "" or ast.literal_eval(info.field_report) is None:
                form_data['report'] = info.field_report
            else:
                form_data['report'] = ast.literal_eval(info.field_report)
            if ast.literal_eval(info.selfie_with_parents) == "" or ast.literal_eval(info.selfie_with_parents) is None:
                form_data['selfie_with_parents'] = info.selfie_with_parents
            else:
                form_data['selfie_with_parents'] = ast.literal_eval(info.selfie_with_parents)
            form_data['message'] = "Success"
            form_data['response_status'] = HTTP_200_OK

            return Response(form_data, status=HTTP_200_OK)
        except Exception as exp:
            return Response({"message": "Error: "+str(exp)},status=HTTP_404_NOT_FOUND)
    else:
        return Response({"meassge": "Method Not Allowed"}, status=HTTP_405_METHOD_NOT_ALLOWED)

# @csrf_exempt
# @api_view(["POST"])
# @validate_teachers_api
# def schoolVisit(request):
#     if request.method == 'POST':
#         visit_selfie                     = []
#         school_visit                     = TblSchoolVisit()
#         school_visit.school_name         = request.data.get('school_name')
#         school_visit.high_school_students = request.data.get('high_school_students')
#         school_visit.school_contact      = request.data.get('phone')
#         school_visit.address_hno         = request.data.get('hno')
#         school_visit.address_locality    = request.data.get('locality')
#         school_visit.state_id            = request.data.get('state_id')
#         school_visit.state_name          = getModelColumnById(TblStates, request.data.get('state_id'), "state_name")
#         school_visit.district_id         = request.data.get('district_id')
#         school_visit.district_name       = getModelColumnById(TblNewDistrict, request.data.get('district_id'), "district_name")
#         school_visit.tehsil_id           = request.data.get('tehsil_id')
#         school_visit.tehsil_name         = getModelColumnById(TblNewTehsil, request.data.get('tehsil_id'), "tehsil_name")
#         school_visit.village_id          = request.data.get('village_id')
#         school_visit.village_name        = getModelColumnById(TblNewVillage, request.data.get('village_id'), "village_name")
#         school_visit.pincode             = request.data.get('pincode')
#         school_visit.longitude           = request.data.get('long')
#         school_visit.latitude            = request.data.get('lat')
#         school_visit.support_staff       = request.data.get('support_staff')
#         school_visit.remark              = request.data.get('remark')


#         if bool(request.FILES.get('school_image', False)) == True:
#             school_image                = request.FILES['school_image']
#             folder                      = 'media/school_images/'
#             storage                     = FileSystemStorage(location=folder)
#             timestamp                   = int(time.time())
#             session_record_filename     = school_image.name
#             temp                        = session_record_filename.split('.')
#             session_record_filename     = 'school_image'+str(timestamp)+"."+temp[(len(temp) - 1)]
#             school_img_file             = storage.save(session_record_filename, school_image)
#             school_img                  = storage.url(school_img_file)
#             school_img = school_img.split('media/')[1]
#             school_img = "/"+folder+school_img
#             school_visit.school_image   = school_img


#         # if bool(request.FILES.get('selfie', False)) == True:
#         #     for visit_selfie_record in request.FILES.getlist('selfie'):
#         #         folder      ='media/school_visit_selfie/'
#         #         storage     = FileSystemStorage(location=folder)
#         #         timestamp   = int(time.time())
#         #         session_record_filename = visit_selfie_record.name
#         #         temp = session_record_filename.split('.')
#         #         session_record_filename = 'school_visit_selfie'+str(timestamp)+"."+temp[(len(temp) - 1)]
#         #         visit_selfie_file = storage.save(session_record_filename, visit_selfie_record)
#         #         visit_selfie_file = storage.url(visit_selfie_file)

#         #         visit_selfie_file = visit_selfie_file.split('media/')[1]
#         #         visit_selfie_file = "/"+folder+visit_selfie_file
#         #         visit_selfie.append(visit_selfie_file)
#         # else:
#         #     visit_selfie = None

#         # school_visit.selfie = visit_selfie
        
#         school_visit.visit_datetime = datetime.now()
#         school_visit.created_by = request.user.id
#         school_visit.created_at = datetime.now()
#         school_visit.updated_at = datetime.now()

#         school_visit.save()

#         # contacts = eval(request.data.get("contacts"))
#         # contacts = ast.literal_eval(contacts)
#         contacts = ast.literal_eval(request.data.get("contacts"))

#         for each_contact in contacts:
#             school_contact                  = TblSchoolContact()
#             school_contact.school_id        = school_visit.id
#             school_contact.contact_name     = each_contact["contact_name"]
#             school_contact.contact_number   = each_contact["contact_number"]
#             school_contact.contact_type     = each_contact["contact_type"]
#             if each_contact["is_referred"] == '1':
#                 school_contact.is_referred  = each_contact["is_referred"]
#                 school_contact.referred_by  = each_contact["referred_by"]

#             school_contact.save()

#         return JsonResponse( {"message":"Successfully saved the visited data"}, status = HTTP_200_OK )




# @csrf_exempt
# @api_view(["POST"])
# @validate_teachers_api
# def individualVisit(request):
#     if request.method == 'POST':
#         visit_selfie                     = []
#         individual_visit                     = TblIndividualVisit()
#         individual_visit.student_name        = request.data.get('student_name')
#         individual_visit.guardian_name       = request.data.get('guardian_name')
#         individual_visit.student_contact     = request.data.get('student_contact')
#         individual_visit.referred_by_teacher = request.data.get('referred_by_teacher')
#         individual_visit.referred_by_student = request.data.get('referred_by_student')

#         individual_visit.branch_id           = request.data.get('branch_id')
#         individual_visit.branch_name         = getModelColumnById(TblBranch, request.data.get('branch_id'), "abbr")
#         individual_visit.year                = request.data.get('year')
#         individual_visit.highschool_in_year  = request.data.get('highschool_in_year')

#         individual_visit.address_hno         = request.data.get('hno')
#         individual_visit.address_locality    = request.data.get('locality')
#         individual_visit.village_id          = request.data.get('village_id')
#         individual_visit.address_village     = getModelColumnById(TblNewVillage, request.data.get('village_id'), "village_name")
#         individual_visit.tehsil_id           = request.data.get('tehsil_id')
#         individual_visit.address_tehsil      = getModelColumnById(TblNewTehsil, request.data.get('tehsil_id'), "tehsil_name")
#         individual_visit.district_id         = request.data.get('district_id')
#         individual_visit.address_district    = getModelColumnById(TblNewDistrict, request.data.get('district_id'), "district_name")
#         individual_visit.state_id            = request.data.get('state_id')
#         individual_visit.address_state       = getModelColumnById(TblStates, request.data.get('state_id'), "state_name")
#         individual_visit.pincode             = request.data.get("pincode")


#         individual_visit.school_name         = request.data.get('school_name')
#         individual_visit.school_address      = request.data.get('school_address')
#         individual_visit.coaching_name       = request.data.get('coaching_name')
#         individual_visit.coaching_teacher    = request.data.get('coaching_teacher')
#         individual_visit.coaching_address    = request.data.get('coaching_address')

#         individual_visit.longitude           = request.data.get('long')
#         individual_visit.latitude            = request.data.get('lat')
#         individual_visit.remark              = request.data.get('remark')

#         if bool(request.FILES.get('student_image', False)) == True:
#             school_image                = request.FILES['student_image']
#             folder                      = 'media/individual_student_images/'
#             storage                     = FileSystemStorage(location=folder)
#             timestamp                   = int(time.time())
#             session_record_filename     = school_image.name
#             temp                        = session_record_filename.split('.')
#             session_record_filename     = 'student_image'+str(timestamp)+"."+temp[(len(temp) - 1)]
#             school_img_file             = storage.save(session_record_filename, school_image)
#             school_img                  = storage.url(school_img_file)

#             school_img = school_img.split('media/')[1]
#             school_img = "/"+folder+school_img
#             individual_visit.student_image   = school_img

#         # if bool(request.FILES.get('selfie', False)) == True:
#         #     for visit_selfie_record in request.FILES.getlist('selfie'):
#         #         folder      ='media/individual_visit_selfie/'
#         #         storage     = FileSystemStorage(location=folder)
#         #         timestamp   = int(time.time())
#         #         session_record_filename = visit_selfie_record.name
#         #         temp = session_record_filename.split('.')
#         #         session_record_filename = 'individual_visit_selfie'+str(timestamp)+"."+temp[(len(temp) - 1)]
#         #         visit_selfie_file = storage.save(session_record_filename, visit_selfie_record)
#         #         visit_selfie_file = storage.url(visit_selfie_file)

#         #         visit_selfie_file = visit_selfie_file.split('media/')[1]
#         #         visit_selfie_file = "/"+folder+visit_selfie_file
#         #         visit_selfie.append(visit_selfie_file)
#         # else:
#         #     visit_selfie = None

#         individual_visit.selfie = visit_selfie
        
#         individual_visit.visited_datetime = datetime.now()
#         individual_visit.visited_by = request.user.id
#         individual_visit.created_at = datetime.now()
#         individual_visit.updated_at = datetime.now()

#         individual_visit.save()

#         return JsonResponse( {"message":"Successfully saved the visited data"}, status = HTTP_200_OK )


# @csrf_exempt
# @api_view(["POST"])
# @validate_teachers_api
# def schoolVisit(request):
#     if request.method == 'POST':
#         visit_selfie                     = []
#         if request.data.get('id') and TblSchoolVisit.objects.filter(id = request.data.get('id')).exists():
#             school_visit                = TblSchoolVisit.objects.get(id=request.data.get('id'))
#         else:
#             school_visit                = TblSchoolVisit()
#             school_visit.longitude              = request.data.get('long')
#             school_visit.latitude               = request.data.get('lat')
#         school_visit.school_name            = request.data.get('school_name')
#         school_visit.high_school_students   = request.data.get('high_school_students')
#         school_visit.school_contact         = request.data.get('phone')
#         school_visit.address_hno            = request.data.get('hno')
#         school_visit.address_locality       = request.data.get('locality')
#         school_visit.state_id               = request.data.get('state_id')
#         school_visit.state_name             = getModelColumnById(TblStates, request.data.get('state_id'), "state_name")
#         school_visit.district_id            = request.data.get('district_id')
#         school_visit.district_name          = getModelColumnById(TblNewDistrict, request.data.get('district_id'), "district_name")
#         school_visit.tehsil_id              = request.data.get('tehsil_id')
#         school_visit.tehsil_name            = getModelColumnById(TblNewTehsil, request.data.get('tehsil_id'), "tehsil_name")
#         school_visit.village_id             = request.data.get('village_id')
#         school_visit.village_name           = getModelColumnById(TblNewVillage, request.data.get('village_id'), "village_name")
#         school_visit.pincode                = request.data.get('pincode')

#         school_visit.support_staff          = request.data.get('support_staff')
#         school_visit.remark                 = request.data.get('remark')

#         if bool(request.FILES.get('school_image', False)) == True:
#             school_image                = request.FILES['school_image']
#             folder                      = 'media/school_images/'
#             storage                     = FileSystemStorage(location=folder)
#             timestamp                   = int(time.time())
#             session_record_filename     = school_image.name
#             temp                        = session_record_filename.split('.')
#             session_record_filename     = 'school_image'+str(timestamp)+"."+temp[(len(temp) - 1)]
#             school_img_file             = storage.save(session_record_filename, school_image)
#             school_img                  = storage.url(school_img_file)

#             school_img = school_img.split('media/')[1]
#             school_img = "/"+folder+school_img
#             school_visit.school_image   = school_img

#         # if bool(request.FILES.get('selfie', False)) == True:
#         #     for visit_selfie_record in request.FILES.getlist('selfie'):
#         #         folder      ='media/school_visit_selfie/'
#         #         storage     = FileSystemStorage(location=folder)
#         #         timestamp   = int(time.time())
#         #         session_record_filename = visit_selfie_record.name
#         #         temp = session_record_filename.split('.')
#         #         session_record_filename = 'school_visit_selfie'+str(timestamp)+"."+temp[(len(temp) - 1)]
#         #         visit_selfie_file = storage.save(session_record_filename, visit_selfie_record)
#         #         visit_selfie_file = storage.url(visit_selfie_file)

#         #         visit_selfie_file = visit_selfie_file.split('media/')[1]
#         #         visit_selfie_file = "/"+folder+visit_selfie_file
#         #         visit_selfie.append(visit_selfie_file)
#         # else:
#         #     visit_selfie = None

#         # school_visit.selfie = visit_selfie
        
#         school_visit.visited_datetime = datetime.now()
#         school_visit.visited_by = request.user.id
#         school_visit.created_at = datetime.now()
#         school_visit.updated_at = datetime.now()

#         school_visit.save()

#         # contacts = eval(request.data.get("contacts"))
#         # contacts = ast.literal_eval(contacts)
#         contacts = ast.literal_eval(request.data.get("contacts"))

#         TblSchoolContact.objects.filter(school_id = school_visit.id).delete()
#         for each_contact in contacts:
#             # if each_contact["contact_id"] and TblSchoolContact.objects.filter(id = each_contact["contact_id"], school_id = school_visit.id).exists():
#             #     school_contact                  = TblSchoolContact.objects.get(id = each_contact["contact_id"], school_id = school_visit.id)
#             # else:
#             school_contact                  = TblSchoolContact()

#             school_contact.school_id        = school_visit.id
#             school_contact.contact_name     = each_contact["contact_name"]
#             school_contact.contact_number   = each_contact["contact_number"]
#             school_contact.contact_type     = each_contact["contact_type"]
#             if each_contact["is_referred"] == '1':
#                 school_contact.is_referred  = each_contact["is_referred"]
#                 school_contact.referred_by  = each_contact["referred_by"]

#             school_contact.save()

#         return JsonResponse( {"message":"Successfully saved the visited data"}, status = HTTP_200_OK )



# @csrf_exempt
# @api_view(["POST"])
# @validate_teachers_api
# def individualVisit(request):
#     if request.method == 'POST':
#         visit_selfie                         = []
#         if request.data.get('id') and TblSchoolVisit.objects.filter(id = request.data.get('id')).exists():
#             individual_visit        = TblIndividualVisit.objects.get(id=request.data.get('id'))
#         else:
#             individual_visit        = TblIndividualVisit()
#             individual_visit.latitude       = request.data.get('lat')
#             individual_visit.longitude      = request.data.get('long')

#         individual_visit.student_name        = request.data.get('student_name')
#         individual_visit.guardian_name       = request.data.get('guardian_name')
#         individual_visit.student_contact     = request.data.get('student_contact')
#         individual_visit.referred_by_teacher = request.data.get('referred_by_teacher')
#         individual_visit.referred_by_student = request.data.get('referred_by_student')

#         individual_visit.branch_id           = request.data.get('branch_id')
#         individual_visit.branch_name         = getModelColumnById(TblBranch, request.data.get('branch_id'), "abbr")
#         individual_visit.year                = request.data.get('year')
#         individual_visit.highschool_in_year  = request.data.get('highschool_in_year')

#         individual_visit.address_hno         = request.data.get('hno')
#         individual_visit.address_locality    = request.data.get('locality')
#         individual_visit.village_id          = request.data.get('village_id')
#         individual_visit.address_village     = getModelColumnById(TblNewVillage, request.data.get('village_id'), "village_name")
#         individual_visit.tehsil_id           = request.data.get('tehsil_id')
#         individual_visit.address_tehsil      = getModelColumnById(TblNewTehsil, request.data.get('tehsil_id'), "tehsil_name")
#         individual_visit.district_id         = request.data.get('district_id')
#         individual_visit.address_district    = getModelColumnById(TblNewDistrict, request.data.get('district_id'), "district_name")
#         individual_visit.state_id            = request.data.get('state_id')
#         individual_visit.address_state       = getModelColumnById(TblStates, request.data.get('state_id'), "state_name")
#         individual_visit.pincode             = request.data.get("pincode")

#         individual_visit.school_name         = request.data.get('school_name')
#         individual_visit.school_address      = request.data.get('school_address')
#         individual_visit.coaching_name       = request.data.get('coaching_name')
#         individual_visit.coaching_teacher    = request.data.get('coaching_teacher')
#         individual_visit.coaching_address    = request.data.get('coaching_address')

#         individual_visit.remark              = request.data.get('remark')


#         if bool(request.FILES.get('student_image', False)) == True:
#             school_image                = request.FILES['student_image']
#             folder                      = 'media/student_images/'
#             storage                     = FileSystemStorage(location=folder)
#             timestamp                   = int(time.time())
#             session_record_filename     = school_image.name
#             temp                        = session_record_filename.split('.')
#             session_record_filename     = 'student_image'+str(timestamp)+"."+temp[(len(temp) - 1)]
#             school_img_file             = storage.save(session_record_filename, school_image)
#             school_img                  = storage.url(school_img_file)

#             school_img = school_img.split('media/')[1]
#             school_img = "/"+folder+school_img
#             individual_visit.student_image   = school_img

#         # if bool(request.FILES.get('selfie', False)) == True:
#         #     for visit_selfie_record in request.FILES.getlist('selfie'):
#         #         folder      ='media/individual_visit_selfie/'
#         #         storage     = FileSystemStorage(location=folder)
#         #         timestamp   = int(time.time())
#         #         session_record_filename = visit_selfie_record.name
#         #         temp = session_record_filename.split('.')
#         #         session_record_filename = 'individual_visit_selfie'+str(timestamp)+"."+temp[(len(temp) - 1)]
#         #         visit_selfie_file = storage.save(session_record_filename, visit_selfie_record)
#         #         visit_selfie_file = storage.url(visit_selfie_file)

#         #         visit_selfie_file = visit_selfie_file.split('media/')[1]
#         #         visit_selfie_file = "/"+folder+visit_selfie_file
#         #         visit_selfie.append(visit_selfie_file)
#         # else:
#         #     visit_selfie = None

#         # individual_visit.selfie = visit_selfie
        
#         individual_visit.visited_datetime = datetime.now()
#         individual_visit.visited_by = request.user.id
#         individual_visit.created_at = datetime.now()
#         individual_visit.updated_at = datetime.now()

#         individual_visit.save()

#         return JsonResponse( {"message":"Successfully saved the visited data"}, status = HTTP_200_OK )



@csrf_exempt
@api_view(["POST"])
@validate_teachers_api
def schoolVisit(request):
    if request.method == 'POST':
        visit_selfie                     = []
        if request.data.get('id') and TblSchoolVisit.objects.filter(id = request.data.get('id')).exists():
            school_visit                = TblSchoolVisit.objects.get(id=request.data.get('id'))
        else:
            school_visit                = TblSchoolVisit()
            school_visit.longitude              = request.data.get('long')
            school_visit.latitude               = request.data.get('lat')

        school_visit.school_name            = request.data.get('school_name')
        school_visit.high_school_students   = request.data.get('high_school_students')
        school_visit.school_contact         = request.data.get('phone')
        school_visit.address_hno            = request.data.get('hno')
        school_visit.address_locality       = request.data.get('locality')
        school_visit.state_id               = request.data.get('state_id')
        school_visit.state_name             = getModelColumnById(TblStates, request.data.get('state_id'), "state_name")
        school_visit.district_id            = request.data.get('district_id')
        school_visit.district_name          = getModelColumnById(TblNewDistrict, request.data.get('district_id'), "district_name")
        school_visit.tehsil_id              = request.data.get('tehsil_id')
        school_visit.tehsil_name            = getModelColumnById(TblNewTehsil, request.data.get('tehsil_id'), "tehsil_name")
        school_visit.village_id             = request.data.get('village_id')
        school_visit.village_name           = getModelColumnById(TblNewVillage, request.data.get('village_id'), "village_name")
        school_visit.pincode                = request.data.get('pincode')

        school_visit.support_staff          = request.data.get('support_staff')
        school_visit.remark                 = request.data.get('remark')

        if bool(request.FILES.get('school_image', False)) == True:
            school_image                = request.FILES['school_image']
            folder                      = 'media/school_images/'
            storage                     = FileSystemStorage(location=folder)
            timestamp                   = int(time.time())
            session_record_filename     = school_image.name
            temp                        = session_record_filename.split('.')
            session_record_filename     = 'school_image'+str(timestamp)+"."+temp[(len(temp) - 1)]
            school_img_file             = storage.save(session_record_filename, school_image)
            school_img                  = storage.url(school_img_file)

            school_img = school_img.split('media/')[1]
            school_img = "/"+folder+school_img
            school_visit.school_image   = school_img

        # if bool(request.FILES.get('selfie', False)) == True:
        #     for visit_selfie_record in request.FILES.getlist('selfie'):
        #         folder      ='media/school_visit_selfie/'
        #         storage     = FileSystemStorage(location=folder)
        #         timestamp   = int(time.time())
        #         session_record_filename = visit_selfie_record.name
        #         temp = session_record_filename.split('.')
        #         session_record_filename = 'school_visit_selfie'+str(timestamp)+"."+temp[(len(temp) - 1)]
        #         visit_selfie_file = storage.save(session_record_filename, visit_selfie_record)
        #         visit_selfie_file = storage.url(visit_selfie_file)

        #         visit_selfie_file = visit_selfie_file.split('media/')[1]
        #         visit_selfie_file = "/"+folder+visit_selfie_file
        #         visit_selfie.append(visit_selfie_file)
        # else:
        #     visit_selfie = None

        # school_visit.selfie = visit_selfie
        
        school_visit.visited_datetime = datetime.now()
        school_visit.visited_by = request.user.id
        school_visit.created_at = datetime.now()
        school_visit.updated_at = datetime.now()

        school_visit.save()

        school_visit_history = TblSchoolVisitHistory()
        school_visit_history.school_id              = school_visit.id
        school_visit_history.school_name            = request.data.get('school_name')
        school_visit_history.high_school_students   = request.data.get('high_school_students')
        school_visit_history.school_contact         = request.data.get('phone')
        school_visit_history.address_hno            = request.data.get('hno')
        school_visit_history.address_locality       = request.data.get('locality')
        school_visit_history.state_id               = request.data.get('state_id')
        school_visit_history.state_name             = getModelColumnById(TblStates, request.data.get('state_id'), "state_name")
        school_visit_history.district_id            = request.data.get('district_id')
        school_visit_history.district_name          = getModelColumnById(TblNewDistrict, request.data.get('district_id'), "district_name")
        school_visit_history.tehsil_id              = request.data.get('tehsil_id')
        school_visit_history.tehsil_name            = getModelColumnById(TblNewTehsil, request.data.get('tehsil_id'), "tehsil_name")
        school_visit_history.village_id             = request.data.get('village_id')
        school_visit_history.village_name           = getModelColumnById(TblNewVillage, request.data.get('village_id'), "village_name")
        school_visit_history.pincode                = request.data.get('pincode')

        school_visit_history.visited_by             = school_visit.visited_by
        school_visit_history.edited_by              = request.user.id
        school_visit_history.edited_datetime        = datetime.now()
        school_visit_history.remark                 = request.data.get('remark')

        if bool(request.FILES.get('school_image', False)) == True:
            school_image                = request.FILES['school_image']
            folder                      = 'media/school_images/'
            storage                     = FileSystemStorage(location=folder)
            timestamp                   = int(time.time())
            session_record_filename     = school_image.name
            temp                        = session_record_filename.split('.')
            session_record_filename     = 'school_image'+str(timestamp)+"."+temp[(len(temp) - 1)]
            school_img_file             = storage.save(session_record_filename, school_image)
            school_img                  = storage.url(school_img_file)

            school_img = school_img.split('media/')[1]
            school_img = "/"+folder+school_img
            school_visit_history.school_image   = school_img

        school_visit_history.save()

        contacts = ast.literal_eval(request.data.get("contacts"))
        TblSchoolContact.objects.filter(school_id = school_visit.id).delete()

        for each_contact in contacts:
            school_contact                  = TblSchoolContact()
            school_contact.school_id        = school_visit.id
            school_contact.contact_name     = each_contact["contact_name"]
            school_contact.contact_number   = each_contact["contact_number"]
            school_contact.contact_type     = each_contact["contact_type"]
            if each_contact["is_referred"] == '1':
                school_contact.is_referred  = each_contact["is_referred"]
                school_contact.referred_by  = each_contact["referred_by"]

            school_contact.save()

            school_contact_history                      = TblSchoolContactHistory()
            school_contact_history.school_contact_id    = school_contact.id
            school_contact_history.school_id            = school_visit.id
            school_contact_history.contact_name         = each_contact["contact_name"]
            school_contact_history.contact_number       = each_contact["contact_number"]
            school_contact_history.contact_type         = each_contact["contact_type"]
            school_contact_history.edited_by            = request.user.id
            school_contact_history.edited_datetime      = datetime.now()
            if each_contact["is_referred"] == '1':
                school_contact_history.is_referred      = each_contact["is_referred"]
                school_contact_history.referred_by      = each_contact["referred_by"]

            school_contact_history.save()



        return JsonResponse( {"message":"Successfully saved the visited data"}, status = HTTP_200_OK )


@csrf_exempt
@api_view(["POST"])
@validate_teachers_api
def individualVisit(request):
    if request.method == 'POST':
        visit_selfie                         = []
        if request.data.get('id') and TblSchoolVisit.objects.filter(id = request.data.get('id')).exists():
            individual_visit        = TblIndividualVisit.objects.get(id=request.data.get('id'))
        else:
            individual_visit        = TblIndividualVisit()
            individual_visit.longitude      = request.data.get('long')
            individual_visit.latitude       = request.data.get('lat')

        individual_visit.student_name        = request.data.get('student_name')
        individual_visit.guardian_name       = request.data.get('guardian_name')
        individual_visit.student_contact     = request.data.get('student_contact')
        individual_visit.referred_by_teacher = request.data.get('referred_by_teacher')
        individual_visit.referred_by_student = request.data.get('referred_by_student')

        individual_visit.branch_id           = request.data.get('branch_id')
        individual_visit.branch_name         = getModelColumnById(TblBranch, request.data.get('branch_id'), "abbr")
        individual_visit.year                = request.data.get('year')
        individual_visit.highschool_in_year  = request.data.get('highschool_in_year')

        individual_visit.address_hno         = request.data.get('hno')
        individual_visit.address_locality    = request.data.get('locality')
        individual_visit.village_id          = request.data.get('village_id')
        individual_visit.address_village     = getModelColumnById(TblNewVillage, request.data.get('village_id'), "village_name")
        individual_visit.tehsil_id           = request.data.get('tehsil_id')
        individual_visit.address_tehsil      = getModelColumnById(TblNewTehsil, request.data.get('tehsil_id'), "tehsil_name")
        individual_visit.district_id         = request.data.get('district_id')
        individual_visit.address_district    = getModelColumnById(TblNewDistrict, request.data.get('district_id'), "district_name")
        individual_visit.state_id            = request.data.get('state_id')
        individual_visit.address_state       = getModelColumnById(TblStates, request.data.get('state_id'), "state_name")
        individual_visit.pincode             = request.data.get("pincode")

        individual_visit.school_name         = request.data.get('school_name')
        individual_visit.school_address      = request.data.get('school_address')
        individual_visit.coaching_name       = request.data.get('coaching_name')
        individual_visit.coaching_teacher    = request.data.get('coaching_teacher')
        individual_visit.coaching_address    = request.data.get('coaching_address')

        individual_visit.remark              = request.data.get('remark')


        if bool(request.FILES.get('student_image', False)) == True:
            school_image                = request.FILES['student_image']
            folder                      = 'media/student_images/'
            storage                     = FileSystemStorage(location=folder)
            timestamp                   = int(time.time())
            session_record_filename     = school_image.name
            temp                        = session_record_filename.split('.')
            session_record_filename     = 'student_image'+str(timestamp)+"."+temp[(len(temp) - 1)]
            school_img_file             = storage.save(session_record_filename, school_image)
            school_img                  = storage.url(school_img_file)

            school_img = school_img.split('media/')[1]
            school_img = "/"+folder+school_img
            individual_visit.student_image   = school_img

        # if bool(request.FILES.get('selfie', False)) == True:
        #     for visit_selfie_record in request.FILES.getlist('selfie'):
        #         folder      ='media/individual_visit_selfie/'
        #         storage     = FileSystemStorage(location=folder)
        #         timestamp   = int(time.time())
        #         session_record_filename = visit_selfie_record.name
        #         temp = session_record_filename.split('.')
        #         session_record_filename = 'individual_visit_selfie'+str(timestamp)+"."+temp[(len(temp) - 1)]
        #         visit_selfie_file = storage.save(session_record_filename, visit_selfie_record)
        #         visit_selfie_file = storage.url(visit_selfie_file)

        #         visit_selfie_file = visit_selfie_file.split('media/')[1]
        #         visit_selfie_file = "/"+folder+visit_selfie_file
        #         visit_selfie.append(visit_selfie_file)
        # else:
        #     visit_selfie = None

        # individual_visit.selfie = visit_selfie
        
        individual_visit.visited_datetime = datetime.now()
        individual_visit.visited_by = request.user.id
        individual_visit.created_at = datetime.now()
        individual_visit.updated_at = datetime.now()

        individual_visit.save()


        individual_visit_history                            = TblIndividualVisitHistory()

        individual_visit_history.individual_student_id      = individual_visit.id
        individual_visit_history.student_name               = request.data.get('student_name')
        individual_visit_history.guardian_name              = request.data.get('guardian_name')
        individual_visit_history.student_contact            = request.data.get('student_contact')
        individual_visit_history.referred_by_teacher        = request.data.get('referred_by_teacher')
        individual_visit_history.referred_by_student        = request.data.get('referred_by_student')

        individual_visit_history.branch_id                  = request.data.get('branch_id')
        individual_visit_history.branch_name                = getModelColumnById(TblBranch, request.data.get('branch_id'), "abbr")
        individual_visit_history.year                       = request.data.get('year')
        individual_visit_history.highschool_in_year         = request.data.get('highschool_in_year')

        individual_visit_history.address_hno                = request.data.get('hno')
        individual_visit_history.address_locality           = request.data.get('locality')
        individual_visit_history.village_id                 = request.data.get('village_id')
        individual_visit_history.address_village            = getModelColumnById(TblNewVillage, request.data.get('village_id'), "village_name")
        individual_visit_history.tehsil_id                  = request.data.get('tehsil_id')
        individual_visit_history.address_tehsil             = getModelColumnById(TblNewTehsil, request.data.get('tehsil_id'), "tehsil_name")
        individual_visit_history.district_id                = request.data.get('district_id')
        individual_visit_history.address_district           = getModelColumnById(TblNewDistrict, request.data.get('district_id'), "district_name")
        individual_visit_history.state_id                   = request.data.get('state_id')
        individual_visit_history.address_state              = getModelColumnById(TblStates, request.data.get('state_id'), "state_name")
        individual_visit_history.pincode                    = request.data.get("pincode")

        individual_visit_history.school_name                = request.data.get('school_name')
        individual_visit_history.school_address             = request.data.get('school_address')
        individual_visit_history.coaching_name              = request.data.get('coaching_name')
        individual_visit_history.coaching_teacher           = request.data.get('coaching_teacher')
        individual_visit_history.coaching_address           = request.data.get('coaching_address')

        individual_visit_history.visited_by                 = individual_visit.visited_by
        individual_visit_history.edited_by                  = request.user.id
        individual_visit_history.edited_datetime            = datetime.now()

        individual_visit_history.remark                     = request.data.get('remark')

        if bool(request.FILES.get('student_image', False)) == True:
            school_image                = request.FILES['student_image']
            folder                      = 'media/student_images/'
            storage                     = FileSystemStorage(location=folder)
            timestamp                   = int(time.time())
            session_record_filename     = school_image.name
            temp                        = session_record_filename.split('.')
            session_record_filename     = 'student_image'+str(timestamp)+"."+temp[(len(temp) - 1)]
            school_img_file             = storage.save(session_record_filename, school_image)
            school_img                  = storage.url(school_img_file)

            school_img = school_img.split('media/')[1]
            school_img = "/"+folder+school_img
            individual_visit_history.student_image   = school_img

        individual_visit_history.save()


        return JsonResponse( {"message":"Successfully saved the visited data"}, status = HTTP_200_OK )


# Written By: Jalaj Tripathi on 21/02/2022
@csrf_exempt
@api_view(["POST"])
@validate_teachers_api
def visitList(request):
    if request.method == 'POST':

        page_limit  = int(request.data.get("page_limit"))*15
        offset      = int(page_limit)-15
        page_limit  = 15

        faculty_id = request.data.get('faculty_id')
        visit_count = 0


        # Visit --> 1(School), 2(Individual) and Type --> 1(Total), 2(Today)
        try:
            if request.data.get('visit') == "1":
                if request.data.get('type') == "1":
                    total_visit = TblSchoolVisit.objects.filter(visited_by = faculty_id)

                elif request.data.get('type') == "2":
                    total_visit = TblSchoolVisit.objects.filter(visited_by = faculty_id, visited_datetime__icontains = datetime.now().today().date() )
                    
                if request.data.get("search"):
                    total_visit = total_visit.filter(school_name__icontains = request.data.get("search"))
                
                visit_count = total_visit.count()
                total_visit = total_visit.order_by('-visited_datetime').values("id", "address_hno", "address_locality", "village_name", "tehsil_name", "district_name", "state_name", "pincode", "visited_datetime", name = F("school_name"), phone = F("school_contact"), pic = F("school_image"))[offset:offset+page_limit]

            elif request.data.get('visit') == "2":
                if request.data.get('type') == "1":
                    total_visit = TblIndividualVisit.objects.filter(visited_by = faculty_id)
                elif request.data.get('type') == "2":
                    total_visit = TblIndividualVisit.objects.filter(visited_by = faculty_id, visited_datetime__icontains = datetime.now().today().date())
                
                if request.data.get("search") != "" :
                    total_visit = total_visit.filter(student_name__icontains = request.data.get("search"))
                
                visit_count = total_visit.count()
                total_visit = total_visit.order_by('-visited_datetime').values("id", "pincode", "visited_datetime", "address_hno", "address_locality", village_name = F("address_village"), tehsil_name = F("address_tehsil"), district_name = F("address_district"), state_name = F("address_state"), name = F("student_name"), phone = F("student_contact"), pic = F("student_image"))[offset:offset+page_limit]

        except:
            total_visit = ""
        
        page_count = math.ceil(round(visit_count/10, 2))

        context = {}
        context['page_count']       = page_count
        context['count']            = visit_count
        context['content']          = list(total_visit)
        context['message']          = "Success"
        context['response_code']    = HTTP_200_OK

    return JsonResponse(context, status=HTTP_200_OK)
    

@csrf_exempt
@api_view(["POST"])
@validate_teachers_api
def visitDetails(request):
    if request.method == 'POST':
        visit_id    = request.data.get("visit_id")
        visit       = request.data.get('visit')

        if visit == "1":
            visit_info = TblSchoolVisit.objects.filter(id = visit_id).values("id", "school_name", "school_image", "school_contact","address_hno", "address_locality", "state_id", "state_name", "district_id", "district_name", "tehsil_id", "tehsil_name","village_id","village_name","pincode","high_school_students","latitude","longitude","remark","visited_by","visited_datetime")
            visit_contact = TblSchoolContact.objects.filter(school_id = visit_id).values("id", "school_id", "contact_name", "contact_number", "contact_type", "is_referred", "referred_by")
            for visit in visit_info:
                visit['contact'] = list(visit_contact)
        elif visit == "2":
            visit_info = TblIndividualVisit.objects.filter(id = visit_id).values("id", "student_name", "student_image", "guardian_name", "student_contact", "referred_by_teacher", "referred_by_student", "branch_id", "branch_name", "year", "highschool_in_year", "address_hno", "address_locality", "village_id", "address_village", "tehsil_id", "address_tehsil", "district_id", "address_district", "state_id", "address_state", "pincode", "school_name", "school_address", "coaching_name", "coaching_teacher", "coaching_address", "latitude", "longitude", "visited_by", "visited_datetime", "remark")

        context = {}
        context['visit_info']       = list(visit_info)
        context['message']          = "Success"
        context['response_code']    = HTTP_200_OK
    return JsonResponse(context, status=HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
def employeeDocumentList(request):
    baseurl = settings.BASE_URL
    if request.method == 'POST':
        document_list   = TblClEmployeeDocuments.objects.filter(is_uploaded=0).values('id', 'employee_id', 'document_name', 'ducument_number', 'document_path').order_by('-id')
        for document in document_list:
            if document['document_path']:
                document['document_path']   = baseurl+'/'+str(document['document_path'])
            else:
                document['document_path']   = ''    
            document['employee_name']        = getUserName(document['employee_id'])
            document['employee_contact_no']  = getModelColumnById(SpUsers, document['employee_id'], 'primary_contact_number')
            document['document_desc']       = getModelColumnByColumnId(TblClDocumentTypes, 'document_name', document['document_name'], 'description')
        context = {}
        context['document_list']    = document_list
        context['message']          = "Success"
        context['response_code']  = HTTP_200_OK
        return Response(context, status=HTTP_200_OK)
    else:
        return Response({"message":"Method Not Allowed"}, status=HTTP_405_METHOD_NOT_ALLOWED)

@csrf_exempt
@api_view(['POST'])
def uploadEmployeeDocument(request):
    if request.method == 'POST':
        if request.data.get("employee_id")is None or request.data.get("employee_id") == '':
            return Response({'message': 'Employee id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
        if request.data.get("document_id")is None or request.data.get("document_id") == '':
            return Response({'message': 'Document id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
        if bool(request.FILES.get('document_file', False)) == True:
            document_file = request.FILES['document_file']
            employee_name = getModelColumnById(SpUsers, request.data.get("employee_id"), 'first_name')
            employee_name = employee_name.lower()
            employee_name = str(employee_name)+'_'+str(request.data.get("employee_id"))
            folder='media/document_files/'+str(employee_name) 
            try:
                os.mkdir(folder)
            except OSError:
                pass
            else:
                pass
            folder=str(folder)+'/'        
            storage = FileSystemStorage(location=folder)
            timestamp = int(time.time())
            document_file_name = document_file.name
            temp = document_file_name.split('.')
            document_file_name = str(getModelColumnById(TblClEmployeeDocuments, request.data.get("document_id"), 'document_name')) + "_"+str(timestamp)+"."+temp[(len(temp) - 1)]
            
            uploaded_document_file = storage.save(document_file_name, document_file)
            
            document_url = folder+document_file_name

            document                  = TblClEmployeeDocuments.objects.get(id=request.data.get("document_id"),employee_id=request.data.get("employee_id"))
            document.is_uploaded      = 1
            document.document_path    = document_url
            document.save()
            
            context = {}
            context['message']          = "Success"
            context['response_code']  = HTTP_200_OK
            return Response(context, status=HTTP_200_OK)
        else:
            return Response({'message': 'Please select document file', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)    
            
    else:
        return Response({"message":"Method Not Allowed"}, status=HTTP_405_METHOD_NOT_ALLOWED)