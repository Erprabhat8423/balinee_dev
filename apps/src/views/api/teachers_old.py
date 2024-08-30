import math
import time
from django.contrib.auth import authenticate
from datetime import datetime
from django.http.response import HttpResponse
from django.views.decorators import csrf
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from apps.src.decorators.teachers_api import validate_teachers_api, validatePOST
from utils.helper import *
from ...models import *
import json
from rest_framework.renderers import JSONRenderer
from django.http import JsonResponse
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.core.files.storage import FileSystemStorage

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    if request.data.get("username") == '':  
        return Response({'message': 'Please provide username', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("password") == '':
        return Response({'message': 'Please provide password', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("user_role") == '':
        return Response({'message': 'Please provide user role', 'response_code': HTTP_400_BAD_REQUEST}, status = HTTP_400_BAD_REQUEST)
    if request.data.get("username") is None or request.data.get("password") is None:
        return Response({'message': 'Please provide both username and password', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    
    try:
        user_role = request.data.get('user_role')
        if user_role in [0,1,3,5,8]:
            user_details = SpUsers.objects.filter(status=1, user_type=1, official_email=request.data.get("username")).first()
        else:
            return Response({'message': 'Please provide valid user role', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
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

    # if request.data.get("device_id") != '' and user.device_id is not None :
    #     if request.data.get("device_id") != getModelColumnById(SpUsers, user.id, 'device_id'):
    #        return Response({'message': 'You have already login in another device', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND) 

    token, _ = Token.objects.get_or_create(user=user)
    fireBaseToken = request.data.get('firebase_token')
    # if not fireBaseToken:
    #     return Response({'message': 'FireBase-Token Missing', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)
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
    
    all_support_staff = SpUsers.objects.raw(""" SELECT * FROM sp_users WHERE role_name NOT LIKE %s AND organization_id = %s AND id <> %s """, ('%Student', user_details[0]['organization_id'], user_details[0]['id'], ) )
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
    context['states']                   = TblStates.objects.all().values('id', 'state_name')
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
@validatePOST
@validate_teachers_api
@renderer_classes((JSONRenderer))
def getRegisteredList(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        page_limit  = int(request_data["page_limit"])*15
        offset      = int(page_limit)-15
        page_limit  = 15
        _number_of_rows = 0

        try:
            if request_data['search_key']:
                search_key = request_data['search_key']
                # all_registered_students = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE reg_no = %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s; ", (search_key, search_key, search_key, search_key, search_key, ) )
                # _number_of_rows = len(all_registered_students)
                # all_registered_students = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE reg_no = %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s LIMIT %s OFFSET %s; ", (search_key, search_key, search_key, search_key, search_key, page_limit, offset, ) )
                reg_search = str("%"+search_key+"%")
                all_registered_students = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s; ", (reg_search, search_key, search_key, search_key, search_key, ) )
                _number_of_rows = len(all_registered_students)
                all_registered_students = TblStudents.objects.raw(" SELECT * FROM `tbl_students` WHERE reg_no LIKE %s or first_name LIKE %s or CONCAT(first_name, ' ', last_name) LIKE %s or CONCAT(first_name, ' ', middle_name) LIKE %s or CONCAT(first_name, ' ', middle_name, ' ', last_name) LIKE %s LIMIT %s OFFSET %s; ", (reg_search, search_key, search_key, search_key, search_key, page_limit, offset, ) )

            elif request_data['visit_flag'] != "" and (request_data['semester_id'] != '' or request_data['branch_id'] != ''):
                _college_id = request_data['organization_id']
                visit_flag = request_data['visit_flag']
                if request_data['semester_id'] != '' and request_data['branch_id'] != '':
                    all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s and visit_status = %s and  semester_id = %s and branch_id = %s;", (_college_id, visit_flag, request_data['semester_id'], request_data['branch_id'], ) )
                    _number_of_rows = len(all_registered_students)
                    all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s and visit_status = %s and  semester_id = %s and branch_id =%s LIMIT %s OFFSET %s;", (_college_id, visit_flag, request_data['semester_id'], request_data['branch_id'], page_limit, offset, ) )

                elif request_data['semester_id'] != '' and request_data['branch_id'] == '':
                    all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s and visit_status = %s and  semester_id = %s;", (_college_id, visit_flag, request_data['semester_id'], ) )
                    _number_of_rows = len(all_registered_students)
                    all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s and visit_status = %s and  semester_id = %s LIMIT %s OFFSET %s;", (_college_id, visit_flag, request_data['semester_id'], page_limit, offset, ))
                elif request_data['semester_id'] == '' and request_data['branch_id'] != '':
                    all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s and visit_status = %s and branch_id = %s;", (_college_id, visit_flag, request_data['branch_id'], ) )
                    _number_of_rows = len(all_registered_students)
                    all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s and visit_status = %s and  branch_id =%s LIMIT %s OFFSET %s;", (_college_id, visit_flag, request_data['branch_id'], page_limit, offset, ) )

            elif request_data['visit_flag'] != "" and (request_data['semester_id'] == '' and request_data['branch_id'] == ''):
                _college_id = request_data['organization_id']
                visit_flag = request_data['visit_flag']
                all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s and visit_status = %s;",  (_college_id, visit_flag, ) )
                _number_of_rows = len(all_registered_students)
                all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s and visit_status = %s LIMIT  %s OFFSET %s;", (_college_id, visit_flag, page_limit, offset, ) )

            elif  request_data['visit_flag'] == "" and (request_data['semester_id'] != '' or request_data['branch_id'] != ''):
                _college_id = request_data['organization_id']

                if request_data['semester_id'] != '' and request_data['branch_id'] != '':

                    all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s and  semester_id = %s and branch_id = %s;", (_college_id, request_data['semester_id'], request_data['branch_id'], ) )
                    _number_of_rows = len(all_registered_students)
                    all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s and  semester_id = %s and branch_id =%s LIMIT %s OFFSET %s;", (_college_id, request_data['semester_id'], request_data['branch_id'], page_limit, offset, ) )

                elif request_data['semester_id'] != '' and request_data['branch_id'] == '':
                    all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s and  semester_id = %s;", (_college_id, request_data['semester_id'], ) )
                    _number_of_rows = len(all_registered_students)
                    all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s and  semester_id = %s LIMIT %s OFFSET %s;", (_college_id, request_data['semester_id'], page_limit, offset, ))

                elif request_data['semester_id'] == '' and request_data['branch_id'] != '':
                    all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s and  branch_id = %s;", (_college_id, request_data['branch_id'], ) )
                    _number_of_rows = len(all_registered_students)
                    all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s  branch_id =%s LIMIT %s OFFSET %s;", (_college_id, request_data['branch_id'], page_limit, offset, ) )
            else:
                _college_id = request_data['organization_id']
                all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s",  (_college_id, ) )
                _number_of_rows = len(all_registered_students)
                all_registered_students = TblStudents.objects.raw("SELECT * FROM tbl_students WHERE college_id = %s LIMIT %s OFFSET %s;", (_college_id, page_limit, offset, ) )

        except:
            TblStudents.DoesNotExist
            all_registered_students = None
        all_semester = TblSemester.objects.filter(type = "semester")
        all_branch = TblBranch.objects.filter(college_id = request_data['organization_id'])
        content_data = []
        semester_data = []
        branch_data = []
        if _number_of_rows is not None:
            _count = math.ceil(round(_number_of_rows/15, 2))
        else:
            _count = 0

        for each_student in all_registered_students:
            registered_data = {}
            semester = TblSemester.objects.filter(semester_id = each_student.semester_id)
            branch = TblBranch.objects.filter(id = each_student.branch_id)

            if each_student.profile_image:
                registered_data['profile_pic'] = "http://bipe.sortstring.co.in/"+str(each_student.profile_image)
            else:
                registered_data['profile_pic'] = each_student.profile_image

            registered_data['name'] = getStudentName(each_student.id)
            registered_data['branch'] = branch[0].branch
            registered_data['semester'] = semester[0].sem_name
            registered_data['semester_id'] = each_student.semester_id
            registered_data['registration_id'] = each_student.reg_no
            registered_data['mother_name'] = each_student.mother_name
            registered_data['father_name'] = each_student.father_name
            registered_data['phone'] = each_student.primary_contact_no
            registered_data['visit_status'] = each_student.visit_status
            content_data.append(registered_data)
        
        # for each_semester in all_semester:
        #     semester_json = {}
        #     semester_json['semester_id'] = each_semester.semester_id
        #     semester_json['semester_name'] = each_semester.sem_name
        #     semester_data.append(semester_json)
        
        # for each_branch in all_branch:
        #     branch_json = {}
        #     branch_json['branch_id'] = each_branch.id
        #     branch_json['official_branch_name'] = each_branch.branch
        #     branch_json['common_branch_name'] = each_branch.abbr
        #     branch_data.append(branch_json)

        context = {}
        context['result_count']     = _number_of_rows
        context['page_count']       = _count
        # context['semester']         = semester_data
        # context['branch']           = branch_data
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
    # support = getUserName(request_data['faculty_id'])
    # if request_data['support_staff'] is not None or request_data['support_staff'] != {} or request_data['support_staff'] != "":
    #     for support_id in request_data['support_staff']:
    #         support += ", "+getUserName(support_id)
    # clg_num = getModelColumnById(SpOrganizations, request_data['college_id'], 'mobile_country_code')+"-"+getModelColumnById(SpOrganizations, request_data['college_id'], 'mobile_number')
    # message = "BIPE गजोखर वाराणसी से ‘गृह सम्पर्क’ कार्यक्रम के अंतर्गत, हमारे प्रतिनिधि श्री {support} जी ने आपसे भेंट की है। संस्था को गुणवत्ता के लिए आपने {rate}/5 की रेटिंग दी है। {feedback} इस सूचना से यदि आप सहमत हैं तो, कृपया OTP {otp} हमारे प्रतिनिधि से साझा करें। किसी भी अन्य सुझाव अथवा समस्या को साझा करने के लिए कृपया {phone} पर संपर्क करें। BGIVNS,".format(support = support, rate=request_data['rate'], feedback = request_data['opinion'], otp=otp, phone=clg_num)
    # sendSMS("BGIVNS", request_data['mob_no'], message)
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
            home_visit.faculty_id = int(request.data.get('faculty_id'))
            home_visit.student_id = request.data.get('student_id')
            home_visit.college_id = int(request.data.get('college_id'))
            home_visit.guardian_relation = request.data.get('contact_person')
            home_visit.mob_no = request.data.get('phone')
            home_visit.address_hno = request.data.get('hno')
            home_visit.address_locality = request.data.get('locality')
            home_visit.state_id = int(request.data.get('state_id'))
            home_visit.district_id = int(request.data.get('district_id'))
            home_visit.tehsil_id = int(request.data.get('tehsil_id'))
            home_visit.village_id = int(request.data.get('village_id'))
            home_visit.pincode = request.data.get('pincode')
            home_visit.semester = request.data.get('semester')
            home_visit.opinion = request.data.get('opinion')
            home_visit.rating = float(request.data.get('rate'))
            home_visit.longitude = request.data.get('long')
            home_visit.latitude = request.data.get('lat')
            home_visit.answers = request.data.get('answer')
            home_visit.field_report = request.data.get('report')
            home_visit.selfie_with_parents = request.data.get('selfie')
            home_visit.support_staff = request.data.get('support_staff')
            
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
            # support = getUserName(request.data.get('faculty_id'))
            # if request.data.get('support_staff') is not None or request.data.get('support_staff') != {} or request.data.get('support_staff') != "":
            #     staff_raw = request.data.get('support_staff')
            #     all_staff = json.loads(staff_raw)
            #     for support_id in all_staff:
            #         support += ", "+getUserName(int(support_id['id']))

            # message = 'BIPE गजोखर वाराणसी से ‘गृह सम्पर्क’ कार्यक्रम के अंतर्गत, हमारे प्रतिनिधि श्री {visitors} जी ने आपसे भेंट की है। संस्था को गुणवत्ता के लिए आपने {rate}/5 की रेटिंग दी है। {feedback} इस सूचना से यदि आप सहमत हैं तो, कृपया OTP {otp} हमारे प्रतिनिधि से साझा करें। किसी भी अन्य सुझाव अथवा समस्या को साझा करने के लिए कृपया {phone} पर संपर्क करें। BGIVNS,'.format(visitors = support, rate=request.data.get('rate'), feedback = request.data.get('opinion'), phone=getModelColumnById(SpOrganizations, request.data.get('college_id'), 'mobile_number') )

            # sendSMS('BGIVNS', request.data.get('phone'),message)
            home_visit.save()
            TblStudents.objects.filter(reg_no = request.data.get('student_id')).update(secondary_phone_no = request.data.get('phone'), secondary_phone_relative = request.data.get('contact_person'), address_hno = request.data.get('hno'), address_locality = request.data.get('locality'), state_id = request.data.get('state_id'), district_id=request.data.get('district_id'), tehsil_id = request.data.get('tehsil_id'), village_id = request.data.get('village_id'), visit_status = 1)
            return JsonResponse( {"message":"Successfully saved the visited data"}, status = HTTP_200_OK )
        else:
            return JsonResponse({"message":"OTP invalid"}, status=HTTP_400_BAD_REQUEST)
# @csrf_exempt
# @api_view(["POST"])
# @validate_teachers_api
# def postQuestionnaire(request):
#     if request.method == 'POST':
#         phone = request.data.get("phone")
#         otp = TblVisitOtp.objects.filter(mobile_no = phone).values()
#         visit_report = []
#         visit_selfie = []
#         visit_audio = []
#         if request.data.get('otp') == otp[0]['otp']:
#             home_visit = TblHomeVisit()
#             home_visit.faculty_id = request.data.get('faculty_id')
#             home_visit.student_id = request.data.get('student_id')
#             home_visit.college_id = request.data.get('college_id')
#             home_visit.guardian_relation = request.data.get('contact_person')
#             home_visit.mob_no = request.data.get('phone')
#             home_visit.address_hno = request.data.get('hno')
#             home_visit.address_locality = request.data.get('locality')
#             home_visit.state_id = request.data.get('state_id')
#             home_visit.district_id = request.data.get('district_id')
#             home_visit.tehsil_id = request.data.get('tehsil_id')
#             home_visit.village_id = request.data.get('village_id')
#             home_visit.pincode = request.data.get('pincode')
#             home_visit.semester = request.data.get('semester')
#             home_visit.rating = request.data.get('rate')
#             home_visit.longitude = request.data.get('long')
#             home_visit.latitude = request.data.get('lat')
#             home_visit.answers = request.data.get('answer')
#             home_visit.field_report = request.data.get('report')
#             home_visit.selfie_with_parents = request.data.get('selfie')
#             home_visit.support_staff = request.data.get('support_staff')

#             if bool(request.FILES.get('report', False)) == True:
#                 visit_report_record = request.FILES['report']
#                 storage = FileSystemStorage()
#                 timestamp = int(time.time())
#                 session_record_filename = visit_report_record.name
#                 temp = session_record_filename.split('.')
#                 session_record_filename = 'visit_session_report'+str(timestamp)+"."+temp[(len(temp) - 1)]
                
#                 visit_report_file = storage.save(session_record_filename, visit_report_record)
#                 visit_report.append(storage.url(visit_report_file))
#             else:
#                 visit_report = None
#             if bool(request.FILES.get('selfie', False)) == True:
#                 visit_selfie_record = request.FILES['selfie']
#                 storage = FileSystemStorage()
#                 timestamp = int(time.time())
#                 session_record_filename = visit_selfie_record.name
#                 temp = session_record_filename.split('.')
#                 session_record_filename = 'visit_session_selfie'+str(timestamp)+"."+temp[(len(temp) - 1)]
                
#                 visit_selfie_file = storage.save(session_record_filename, visit_selfie_record)
#                 visit_selfie.append(storage.url(visit_selfie_file))
#             else:
#                 visit_selfie = None
#             if bool(request.FILES.get('visit_recording', False)) == True:
#                 visit_audio_record = request.FILES['visit_recording']
#                 storage = FileSystemStorage()
#                 timestamp = int(time.time())
#                 session_record_filename = visit_audio_record.name
#                 temp = session_record_filename.split('.')
#                 session_record_filename = 'visit_session_record'+str(timestamp)+"."+temp[(len(temp) - 1)]
                
#                 visit_audio_file = storage.save(session_record_filename, visit_audio_record)
#                 visit_audio.append(storage.url(visit_audio_file))
#             else:
#                 visit_audio = None
            
#             home_visit.field_report = visit_report
#             home_visit.selfie_with_parents = visit_selfie
#             home_visit.visit_audio = visit_audio
#             message = 'BIPE गजोखर वाराणसी से "गृह सम्पर्क" कार्यक्रम के अंतर्गत {visitors} जी ने आपसे भेंट की है। संस्था को गुणवत्ता के लिए आपने {rate}/5 की रेटिंग दी है। {feedback}  आपके सुझाव संस्था और छात्र के उन्नयन के लिए बहुत महत्वपूर्ण हैं। किसी भी सुझाव अथवा समस्या को साझा करने के लिए कृपया {phone} पर संपर्क करें।, BGIVNS'.format(visitors = "Abdul, Anand and Rahul", rate=request.data.get('rate'), feedback = request.data.get('opinion'), phone=getModelColumnById(SpOrganizations, request.data.get('college_id'), 'mobile_number') )
#             sendSMS('BGIVNS', request.POST.get['phone'],message)
#             home_visit.save()
#             return JsonResponse( {"message":"Successfully saved the visited data"}, status = HTTP_200_OK )
#         else:
#             return JsonResponse({"message":"OTP invalid"})


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
