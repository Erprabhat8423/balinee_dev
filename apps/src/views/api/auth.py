import json
import time,timeago
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from ...models import *
from django.forms.models import model_to_dict
from django.core import serializers
from utils import *

from datetime import datetime, date

from datetime import timedelta
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password, check_password
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from math import sin, cos, sqrt, atan2, radians

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))

def verifyIdPin(request):
    id_card_pin = request.data.get("id_card_pin")
    if not id_card_pin:
        return Response({'message': 'ID Card pin is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)

    if TblStudents.objects.filter(id_card_pin=id_card_pin).exists():
        student = TblStudents.objects.raw(''' SELECT tbl_students.*,tbl_colleges.college_name,tbl_colleges.alias,tbl_branch.branch FROM tbl_students
        LEFT JOIN tbl_colleges on tbl_colleges.id = tbl_students.college_id 
        LEFT JOIN tbl_branch on tbl_branch.id = tbl_students.branch_id
        WHERE tbl_students.id_card_pin=%s ''',[id_card_pin])

        # update 
        TblStudents.objects.filter(id_card_pin=id_card_pin).update(is_id_card_pin_verified=1)

        student_name   = student[0].first_name+' '
        if student[0].middle_name is not None:
            student_name   += student[0].middle_name+' '
        if student[0].last_name is not None:
            student_name   += student[0].last_name

        heading     = 'ID Card Pin Verification.'
        activity    = student_name+' ('+ student[0].reg_no +')  has verified his/her id card at '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
        saveActivity('Student', 'ID Card Pin Verification', heading, activity, student[0].id, student_name, 'add.png', '2', 'app.png')

        student_details = {}
        student_details['id'] = student[0].id
        student_details['name'] = student_name
        student_details['registration_number'] = student[0].reg_no
        student_details['college'] = student[0].alias
        student_details['course'] = student[0].branch
        student_details['contact_number'] = student[0].primary_contact_no
        student_details['father_name'] = student[0].father_name

        if student[0].college_id == 1:
            if student[0].profile_image is not None:
                student_details['profile_image'] = "http://bipe.sortstring.co.in/"+student[0].profile_image
            else:
                student_details['profile_image'] = "https://sansthaa.sortstring.co.in/static/img/png/default_icon.png"

            student_details['college_logo'] = "http://bipe.sortstring.co.in/public/assets/images/bipe-logo.png"
        elif student[0].college_id == 2:
            if student[0].profile_image is not None:
                student_details['profile_image'] = "http://bite.sortstring.co.in/"+student[0].profile_image
            else:
                student_details['profile_image'] = "https://sansthaa.sortstring.co.in/static/img/png/default_icon.png"

            student_details['college_logo'] = "http://bipe.sortstring.co.in/public/assets/images/bipe-logo.png"
        
        elif student[0].college_id == 3:
            if student[0].profile_image is not None:
                student_details['profile_image'] = "http://bip.sortstring.co.in/"+student[0].profile_image
            else:
                student_details['profile_image'] = "https://sansthaa.sortstring.co.in/static/img/png/default_icon.png"

            student_details['college_logo'] = "http://bipe.sortstring.co.in/public/assets/images/bip-logo.png"

        
        tmp = student[0].semester_id.split('_')
        suffix = ""
        if tmp[1] == "1":
            suffix = "st"
        elif tmp[1] == "2":
            suffix = "nd"
        elif tmp[1] == "3":
            suffix = "rd"
        elif tmp[1] == "4" or tmp[1] == "5" or tmp[1] == "6":
            suffix = "th"

        if tmp[0] == "sem":
            student_details['semester_year'] = str(tmp[1])+suffix+" Sem"
        else:
            student_details['semester_year'] = str(tmp[1])+suffix+" Year"


        context = {}
        
        context['message']                  = 'ID Card pin verified successfully'
        context['response_code']            = HTTP_200_OK
        context['student']                  = student_details

        return Response(context, status=HTTP_200_OK)
    else:
        return Response({'message': 'Invalid ID Card pin', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)
    

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    user_type = request.data.get("user_type")
    if request.data.get("username") == '':  
        return Response({'message': 'Please provide username', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("password") == '':
        return Response({'message': 'Please provide password', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)     
    if request.data.get("username") is None or request.data.get("password") is None:
        return Response({'message': 'Please provide both username and password', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)

    branches  = []
    semesters = []
    context = {}
    states = TblStates.objects.all().values('id','state')
    cities = TblNewDistrict.objects.all().values('id','state_id','district_name')
    
    if not user_type:
        return Response({'message': 'User type field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)
    if user_type == '0':
        try:
            user_details = SpUsers.objects.filter(status=1, user_type=1, emp_sap_id=request.data.get("username")).first()
        except SpUsers.DoesNotExist:
            user_details = None
        if user_details:
            username = user_details.emp_sap_id
        else:        
            username = None
        error_msg = 'Invalid Id'

        if not user_details:
            return Response({'message': error_msg, 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)
        
        context["state_list"] = list(states)
        context["city_list"]  = list(cities)
    else:
        try:
            user_details = SpUsers.objects.filter(status=1, user_type=1, emp_sap_id=request.data.get("username")).first()
        except SpUsers.DoesNotExist:
            user_details = None
        if user_details:
            username = request.data.get("username")
        else:        
            username = None
        error_msg = 'Invalid Email Id'

        if not user_details:
            return Response({'message': error_msg, 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)
        
        branches  = TblBranch.objects.filter(status=1).values('id','branch')  
        
        semesters = TblSemester.objects.all().values('id','sem_name','semester_id')
        courses   = TblCourseTypes.objects.filter(status=1).values('id','college_id','course_type')

        context['branch']                  = branches
        context['semester']                = semesters
        context['course']                  = courses

    username = username
    password = request.data.get("password")
    
    if user_type == '0':
        if check_password(password, user_details.password):
            user = user_details
        else:    
            user = None
    else:
        user = authenticate(username=username, password=password)
    if not user:
        return Response({'message': 'Invalid Credentials', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)
    
    if user.role_id!=0:
        context["latitude"] = user.latitude
        context["longitude"] = user.longitude
        context["contact_number"] = "9876543210"
        if request.data.get("device_id") != '' and user.device_id is not None :
            if user.id != 30:
                if request.data.get("device_id") != getModelColumnById(SpUsers, user.id, 'device_id'):
                   return Response({'message': 'You have already login in another device', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND) 

    token, _ = Token.objects.get_or_create(user=user)

    user_details = SpUsers.objects.filter(status=1, id=user.id).values()
    try:
        user_basic_details = model_to_dict(SpBasicDetails.objects.get(user_id=user.id))
    except SpBasicDetails.DoesNotExist:
        user_basic_details = {}

    try:
        user_correspondence_details = model_to_dict(SpAddresses.objects.get(user_id=user.id,type='correspondence'))
    except SpAddresses.DoesNotExist:
        user_correspondence_details = {}

    try:
        user_permanent_details = model_to_dict(SpAddresses.objects.get(user_id=user.id,type='permanent'))
    except SpAddresses.DoesNotExist:
        user_permanent_details = {}

    user_name   = user.first_name+' '+user.middle_name+' '+user.last_name
    heading     = user_name+' has been logged In'
    activity    = user_name+' has been logged In on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('Login', 'Login', heading, activity, user.id, user_name, 'login.png', '2', 'app.png')
    
    if request.data.get("device_id") != '' :
        current_user = SpUsers.objects.get(id=user.id)
        current_user.device_id = request.data.get("device_id")
        current_user.firebase_token = request.data.get("firebase_token")
        current_user.save()
        
    # context = {}
    context['token']                    = token.key
    context['user_details']             = user_details
    context['basic_details']            = user_basic_details
    context['correspondence_address']   = user_correspondence_details
    context['permanent_address']        = user_permanent_details

    context['message']                  = 'Login successfully'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)


#for approvalRequests
@csrf_exempt
@api_view(["POST"])
def approvalRequests(request):    
    data = {}
    if request.user.role_id == 0:
        #all leave policies only excluding approved one with policy status 3
        leave_policy_data = []
        leave_policies = SpLeavePolicies.objects.exclude(policy_status=3).order_by('-id')
        for leave_policy in leave_policies:
            leave_policy_data.append(model_to_dict(leave_policy))

        #all holiday only excluding approved one with holiday status 3
        holiday_data = []
        holidays = SpHolidays.objects.exclude(holiday_status=3).order_by('-id')
        for holiday in holidays:
            holiday_data.append(model_to_dict(holiday))
        
        data['leave_policies'] = leave_policy_data
        data['holidays'] = holiday_data

        return Response({'message':"approval request","approval_requests":data, 'response_code': HTTP_200_OK}, status=HTTP_200_OK)
    
    else:
        #will show leaves on behalf of user logged in and excluding leave with status 3
        leave_policy_data = []
        leave_policies = SpLeavePolicies.objects.raw('''SELECT sp_leave_policies.*, sp_approval_status.level_id, sp_approval_status.level, sp_approval_status.status, sp_approval_status.final_status_user_id, sp_approval_status.final_status_user_name
        FROM sp_leave_policies left join sp_approval_status on sp_approval_status.row_id = sp_leave_policies.id 
        where sp_leave_policies.policy_status != 3 and  sp_approval_status.user_id = %s and sp_approval_status.model_name = 'SpLeavePolicyDetails' order by id desc ''',[19])#[request.user.id]
        for leave_policy in leave_policies:
            leave_policy_data.append(model_to_dict(leave_policy))

        #will show holidays on behalf of user logged in and excluding holiday with status 3
        holiday_data = []
        holidays = SpHolidays.objects.raw('''SELECT sp_holidays.*, sp_approval_status.level_id, sp_approval_status.level, sp_approval_status.status, sp_approval_status.final_status_user_id, sp_approval_status.final_status_user_name
        FROM sp_holidays left join sp_approval_status on sp_approval_status.row_id = sp_holidays.id 
        where sp_holidays.holiday_status != 3 and  sp_approval_status.user_id = %s and sp_approval_status.model_name = 'SpHolidays' order by id desc ''',[19])#[request.user.id]

        for holiday in holidays:
            holiday_data.append(model_to_dict(holiday))

        
        data['leave_policies'] = leave_policy_data
        data['holidays'] = holiday_data
            
        return Response({'message':"approval request","approval_requests":data, 'response_code': HTTP_200_OK}, status=HTTP_200_OK)
    

#for updatePolicyStatus
@csrf_exempt
@api_view(["POST"])
def updatePolicyStatus(request):
    response = {}
    uploaded_file_url = ''
    policyID = request.POST.getlist('policyId')
    if bool(request.FILES.get('document', False)) == True:
        document = request.FILES['document']
        fs = FileSystemStorage(location="media/approval_documents")
        filename = fs.save(document.name, document)
        uploaded_file_url = fs.url(filename)
        uploaded_file_url = uploaded_file_url.split("media/")[1]
        uploaded_file_url = "media/approval_documents/"+uploaded_file_url
        
    policyID = str(policyID).replace("'","")
    policyID = str(policyID).replace("[","")
    policyID = str(policyID).replace("]","")
    policyID = policyID.split(",")
    if policyID:
        for policy_id in policyID:
            updatePolicyStatus = SpLeavePolicies.objects.get(id=policy_id)
            updatePolicyStatus.policy_status = request.POST['statusId']
            updatePolicyStatus.approval_description = request.POST['description']
            updatePolicyStatus.document = uploaded_file_url
            updatePolicyStatus.save()
        response['error'] = False
        response['message'] = "Record has been updated successfully."
        return Response(response)
    else:
        response['error'] = True
        response['message'] = "Record has Not been updated successfully."
        return Response(response)


#for updatePolicyStatus
@csrf_exempt
@api_view(["POST"])
def updateHolidayStatus(request):
    response = {}
    uploaded_file_url = ''
    if bool(request.FILES.get('document', False)) == True:
        document = request.FILES['document']
        fs = FileSystemStorage(location="media/approval_documents")
        filename = fs.save(document.name, document)
        uploaded_file_url = fs.url(filename)
        uploaded_file_url = uploaded_file_url.split("media/")[1]
        uploaded_file_url = "media/approval_documents/"+uploaded_file_url

    holidayID = request.POST.getlist('holidayID')
    holidayID = str(holidayID).replace("'","")
    holidayID = str(holidayID).replace("[","")
    holidayID = str(holidayID).replace("]","")
    holidayID = holidayID.split(",")
    if holidayID:
        for holiday_id in holidayID:
            updateHolidayStatus = SpHolidays.objects.get(id=holiday_id)
            updateHolidayStatus.holiday_status = request.POST['statusId']
            updateHolidayStatus.approval_description = request.POST['description']
            updateHolidayStatus.document = uploaded_file_url
            updateHolidayStatus.save()
        response['error'] = False
        response['message'] = "Record has been updated successfully."
        return Response(response)
    else:
        response['error'] = True
        response['message'] = "Record has Not been updated successfully."
        return Response(response)


# New Code

# @csrf_exempt
# @api_view(["POST"])
# def userAttendance(request):
#     if request.data.get("emp_id")is None or request.data.get("emp_id") == '':
#         return Response({'message': 'Emp Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
#     if request.data.get("type")is None or request.data.get("type") == '':
#         return Response({'message': 'Attendance type is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
#     if request.data.get("start_datetime")is None or request.data.get("start_datetime") == '':
#         return Response({'message': 'Start DateTime field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
#     # if int(request.data.get("type")) == 1:
        
#     #     if request.data.get("dis_ss_id") is None or request.data.get("dis_ss_id") == '':
#     #         return Response({'message': 'Dis/SS id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)      
    
#     data = TblClEmployeeAttendance()
#     data.emp_id = request.data.get("emp_id")
#     data.start_datetime = request.data.get("start_datetime")
#     now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     if request.data.get("type") == '1':
#         data.start_datetime = now
#         data.end_datetime = None
#     else:
#         data.start_datetime = None
#         data.end_datetime = now
    
#     if request.data.get("latitude") is None or request.data.get("latitude") == '':
#         data.latitude = None
#     else:
#         data.latitude = request.data.get("latitude")
    
#     if request.data.get("longitude") is None or request.data.get("longitude") == '':
#         data.longitude = None
#     else:
#         data.longitude = request.data.get("longitude")
    
#     data.attendence_type=1 
#     data.status = 1
#     data.save()
    
#     # save tracking

#     if (request.data.get("latitude") is not None and request.data.get("latitude") != '') and (request.data.get("longitude") is not None and request.data.get("longitude") != ''):

#         if TblClUserTracking.objects.filter(user_id=request.data.get("emp_id")).exists():
            
#             user_last_data = TblClUserTracking.objects.filter(user_id=request.data.get("emp_id")).order_by('-id').first()
            
#             R = 6373.0
#             lat1 = radians(float(user_last_data.latitude))
#             lon1 = radians(float(user_last_data.longitude))
#             lat2 = radians(float(request.data.get("latitude")))
#             lon2 = radians(float(request.data.get("longitude")))
#             dlon = lon2 - lon1
#             dlat = lat2 - lat1
#             a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
#             c = 2 * atan2(sqrt(a), sqrt(1 - a))
#             distance = R * c
#             meter_distance = float(distance * 1000)
#             if meter_distance > 15 :
#                 user_data                       = TblClUserTracking()
#                 user_data.user_id               = request.data.get("emp_id")
#                 user_data.latitude              = request.data.get("latitude")
#                 user_data.longitude             = request.data.get("longitude")
#                 user_data.save()
#         else:
#             user_data                       = TblClUserTracking()
#             user_data.user_id               = request.data.get("emp_id")
#             user_data.latitude              = request.data.get("latitude")
#             user_data.longitude             = request.data.get("longitude")
#             user_data.save()
            
#     user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    
#     heading     = 'Attendance'
#     if request.data.get("type") == '1':
#         activity    = "Day started"
#     else:
#         activity    = "Day end" 
        
#     saveActivity('User Attendance', 'User Attendance', heading, activity, request.user.id, user_name, 'markedAtten.png', '2', 'app.png')


#     context = {}
#     context['message'] = 'Attendance marked successfully'
#     context['response_code'] = HTTP_200_OK
#     return Response(context, status=HTTP_200_OK)


# @csrf_exempt
# @api_view(["POST"])
# def checkAttendance(request):
#     today   = date.today()
#     if request.data.get("emp_id")is None or request.data.get("emp_id") == '':
#         return Response({'message': 'User Id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
#     context = {}
#     if TblClEmployeeAttendance.objects.filter(start_datetime=today.strftime("%Y-%m-%d"), emp_id=request.data.get("emp_id")).exists():
#         start_data      = TblClEmployeeAttendance.objects.filter(start_time__isnull=False,start_datetime=today.strftime("%Y-%m-%d"),emp_id=request.data.get("emp_id")).order_by('id').first()
#         end_data        = TblClEmployeeAttendance.objects.filter(end_time__isnull=False,start_datetime=today.strftime("%Y-%m-%d"),emp_id=request.data.get("emp_id")).order_by('-id').first()
#         user_attendance = TblClEmployeeAttendance.objects.filter(start_datetime=today.strftime("%Y-%m-%d"), emp_id=request.data.get("emp_id")).order_by('-id').first()
#         if user_attendance.start_datetime is not None and user_attendance.end_datetime is None:
#             context['status'] = 1
#         elif user_attendance.start_datetime is None and user_attendance.end_datetime is not None:
#             context['status'] = 0
#         else:
#             context['status'] = 0
#         now = datetime.now().strftime('%Y-%m-%d')
#         start_datetime = now + ' '+start_data.start_datetime
#         if context['status'] == 0:
#             end_datetime = now + ' '+end_data.end_datetime
#         else:
#             end_datetime = now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         start_datetime = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
#         end_datetime = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
#         time_delta = (end_datetime - start_datetime)
#         # total_seconds = time_delta.total_seconds()
#         # hours = (total_seconds/60)/60
#         time_delta = str(time_delta).split(':')
#         time_delta = time_delta[0]+':'+time_delta[1]
#         context['working_hours'] = str(time_delta) + ' hours'
#     else:
#         context['status'] = 0
#         context['working_hours'] = ''
        
#     if getModelColumnById(SpUsers, request.data.get("emp_id"), 'periphery')is None or getModelColumnById(SpUsers, request.data.get("emp_id"), 'periphery') == '':
#         periphery = '500'
#     else:
#         periphery = getModelColumnById(SpUsers, request.data.get("emp_id"), 'periphery')

#     working_shift_timing = TblClWorkingShifts.objects.filter(id=getModelColumnByColumnId(SpBasicDetails, 'user_id', request.data.get("emp_id"), 'working_shift_id')).values('id','start_timing','end_timing').first()

#     context['periphery']     = periphery
#     context['timing']        = working_shift_timing  
#     context['response_code'] = HTTP_200_OK
#     return Response(context, status=HTTP_200_OK)



# @csrf_exempt
# @api_view(["POST"])
# def appliedLeaves(request):
#     if request.data.get("page_limit")is None or request.data.get("page_limit") == '':
#         return Response({'message': 'Page limit is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
#     if request.data.get("user_id")is None or request.data.get("user_id") == '':
#         return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   
#     page_limit  = int(request.data.get("page_limit"))*10
#     offset      = int(page_limit)-10
#     page_limit  = 10
#     leave_list_count = TblClUserLeaves.objects.filter(user_id=request.data.get("user_id")).values('id').count()
        
#     if leave_list_count:
#         leave_list_count = math.ceil(round(leave_list_count/10, 2))
#         leave_status     = TblClUserLeaves.objects.filter(user_id=request.data.get("user_id")).order_by('-id').first()
#         leave_status     = leave_status.leave_status 
#     else:
#         leave_list_count = 0 
#         leave_status     = 0
#     leave_list = TblClUserLeaves.objects.filter(user_id=request.data.get("user_id")).values('id','user_id','user_name','leave_type_id','leave_type','leave_from_date','leave_to_date','leave_detail','leave_status','is_first_half_day','is_last_half_day').order_by('-id')[offset:offset+page_limit]
#     for leave in leave_list:
#         alias = getModelColumnById(SpLeaveTypes,leave['leave_type_id'],'alias')
#         leave['leave_type'] = leave['leave_type']+" ("+ alias +")"
    
#     basic_details_obj=SpBasicDetails.objects.filter(user_id=request.data.get("user_id")).first()
#     if basic_details_obj:
#         if basic_details_obj.week_of_day:
#             week_off_day=basic_details_obj.week_of_day
#         else:
#             week_off_day=""
#     else:
#         week_off_day=""
        
#     context = {}
#     context['message']              = 'Success'
#     context['leave_list']           = list(leave_list)
#     context['leave_list_count']     = leave_list_count
#     context['leave_count']          = getModelColumnByColumnId(SpBasicDetails, 'user_id', request.data.get("user_id"), 'leave_count')
#     context['leave_status']         = leave_status
#     context['week_off_day']    = week_off_day
    
#     context['response_code']        = HTTP_200_OK
#     return Response(context, status=HTTP_200_OK)

# @csrf_exempt
# @api_view(["POST"])
# def applyLeave(request):
#     today   = date.today()
#     if request.data.get("user_id")is None or request.data.get("user_id") == '':
#         return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    
#     if request.data.get("leave_type_id")is None or request.data.get("leave_type_id") == '':
#         return Response({'message': 'Leave type id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
#     if request.data.get("leave_from_date")is None or request.data.get("leave_from_date") == '':
#         return Response({'message': 'From date field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
#     if request.data.get("leave_to_date")is None or request.data.get("leave_to_date") == '':
#         return Response({'message': 'To date field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
#     if request.data.get("description")is None or request.data.get("description") == '':
#         return Response({'message': 'Description field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
#     attachment = None
    
#     isLeaveAppliedOrNot  = checkLeaveAppliedOrNot(request.data.get("user_id"), request.data.get("leave_from_date"), request.data.get("leave_to_date"))
#     if checkAttendanceMarkedOrNot(request.data.get("user_id"), request.data.get("leave_from_date"), request.data.get("leave_to_date"), today.strftime('%Y-%m-%d')):
#         return Response({'message': 'Attendance already marked', 'response_code':0}, status=HTTP_200_OK)
#     elif isLeaveAppliedOrNot['status'] == True:
#         return Response({'message': 'You have already marked leave on selected dates, kindly select another date', 'response_code':0}, status=HTTP_200_OK)
#     else:
#         if bool(request.FILES.get('attachment', False)) == True:
#             uploaded_attachment = request.FILES['attachment']
#             storage = FileSystemStorage()
#             timestamp = int(time.time())
#             attachment_name = uploaded_attachment.name
#             temp = attachment_name.split('.')
#             attachment_name = 'leave_attachment_'+str(timestamp)+"."+temp[(len(temp) - 1)]
            
#             attachment = storage.save(attachment_name, uploaded_attachment)
#             attachment = storage.url(attachment)        
                
#         user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
#         data = TblClUserLeaves()
#         data.user_id                = request.data.get("user_id")
#         data.user_name              = user_name
#         data.leave_type_id          = request.data.get("leave_type_id")
#         data.leave_type             = getModelColumnById(SpLeaveTypes,request.data.get("leave_type_id"),'leave_type')
#         data.leave_from_date        = request.data.get("leave_from_date")
#         data.leave_to_date          = request.data.get("leave_to_date")
#         if request.data.get("is_first_half_day") == "1":
#             data.is_first_half_day = 1
#         else:
#             data.is_first_half_day = 0
#         if request.data.get("is_last_half_day") == "1":
#             data.is_last_half_day = 1
#         else:
#             data.is_last_half_day = 0
#         data.leave_detail           = request.data.get('description')
#         data.leave_status           = 1
#         data.attachment             = attachment
#         data.save()
#         sendFocNotificationToUsers(data.id, '', 'add', 38, request.user.id, user_name, 'TblClUserLeaves',request.user.role_id)
        
#         heading     = 'New Leave Request has been initiated'
#         activity    = 'New Leave Request has been initiated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
        
#         saveActivity('Leave Management', 'Leave Request', heading, activity, request.user.id, user_name, 'add.png', '2', 'app.png')
#         context = {}
#         context['message']       = 'Leave Request has been successfully sent.'
#         context['response_code'] = 1
#         return Response(context, status=HTTP_200_OK)   
        
        

def checkApplyLeaveBefore(date,leave_policy_id,user_id ,leave_type_id):
    try:
        leave_policy_details = SpLeavePolicyDetails.objects.get(leave_policy_id = leave_policy_id,leave_type_id=leave_type_id)
    except SpLeavePolicyDetails.DoesNotExist:
        leave_policy_details = None
    if leave_policy_details:
        if leave_policy_details.apply_leave_before:
            apply_leave_before = int(leave_policy_details.apply_leave_before)
            today               = datetime.today()
            total_no_of_leave_before_days      = date - today
            total_no_of_leave_before_days      = total_no_of_leave_before_days.days 
            if apply_leave_before > total_no_of_leave_before_days:
                return True
            else:
                return False
        else:
                return False
    else:
        return False
           
def checkAvailAdvance(user_id):
    date_of_joining = getModelColumnByColumnId(SpBasicDetails,'user_id',user_id,'date_of_joining')
    date_of_joining = datetime.strptime(date_of_joining.strftime('%Y-%m-%d'), '%Y-%m-%d')
    today           = datetime.today()
    total_days      = today - date_of_joining
    total_days      = total_days.days 
    if total_days > 365 or total_days > 366:
      return True
    else:
        return False 
        
@csrf_exempt
@api_view(["POST"])
def handOverLeaveRequestList(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("page_limit")is None or request.data.get("page_limit") == '':
        return Response({'message': 'Page limit is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)

    page_limit  = int(request.data.get("page_limit"))*10
    offset      = int(page_limit)-10
    page_limit  = 10
    
    leave_list_count = SpNotifications.objects.filter(sub_module = 'Leave request forwarded',to_user_id = request.data.get("user_id"),model_name = 'SpUserLeaves').values('id').count()
        
    if leave_list_count:
        leave_list_count = math.ceil(round(leave_list_count/10, 2))
    else:
        leave_list_count = 0 

        
    leave_request = SpNotifications.objects.filter(sub_module = 'Leave request forwarded',to_user_id = request.data.get("user_id"),model_name = 'SpUserLeaves').order_by('-id')[offset:offset+page_limit]
    request_list = []
    for req in leave_request:
        if SpUserLeaves.objects.filter(id =req.row_id).exists():
            request_dict = {}
            request_dict['leave_id']                = req.row_id
            request_dict['heading']                 = req.heading
            
            request_dict['leave_status']        = getModelColumnById(SpUserLeaves,req.row_id,'leave_status')
            
            request_dict['applied_emp_name']        = req.from_user_name
            request_dict['applied_emp_code']        = getModelColumnById(SpUsers,req.from_user_id,'emp_sap_id')
            request_dict['leave_from_date']         = getModelColumnById(SpUserLeaves,req.row_id,'leave_from_date')
            request_dict['leave_to_date']           = getModelColumnById(SpUserLeaves,req.row_id,'leave_to_date')
            request_dict['is_first_half_day']       = getModelColumnById(SpUserLeaves,req.row_id,'is_first_half_day')
            request_dict['is_last_half_day']        = getModelColumnById(SpUserLeaves,req.row_id,'is_last_half_day')
            request_list.append(request_dict)
        
    context = {}
    context['message']                  = 'Success'
    context['leave_request_list']       = request_list
    context['leave_list_count']         = leave_list_count
    return Response(context, status=HTTP_200_OK)   

@csrf_exempt
@api_view(["POST"])
def applyLeave(request):
    today   = date.today()
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    
    if request.data.get("leave_type_id")is None or request.data.get("leave_type_id") == '':
        return Response({'message': 'Leave type id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
    if request.data.get("leave_from_date")is None or request.data.get("leave_from_date") == '':
        return Response({'message': 'From date field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
    if request.data.get("leave_to_date")is None or request.data.get("leave_to_date") == '':
        return Response({'message': 'To date field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("description")is None or request.data.get("description") == '':
        return Response({'message': 'Description field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    attachment = None
    
    year_leave_count = SpUserLeavePolicyLedger.objects.filter(user_id = request.data.get("user_id"),leave_type_id = request.data.get("leave_type_id")).last()
    if year_leave_count.year_leave_count == 0:
        return Response({'message': 'No '+getModelColumnById(SpLeaveTypes,year_leave_count.leave_type_id ,'leave_type')+' available Kindly contact HR', 'response_code':0}, status=HTTP_200_OK)
        
    leave_from_date             = datetime.strptime(request.data.get("leave_from_date"), '%Y-%m-%d')
    leave_to_date               = datetime.strptime(request.data.get("leave_to_date"), '%Y-%m-%d')
    total_no_of_leave_days      = leave_to_date - leave_from_date
    total_no_of_leave_days      = total_no_of_leave_days.days 
    if request.data.get("leave_type_id") == '1' and int(float(total_no_of_leave_days)) > 3 :
        return Response({'message': 'You can not apply  more then 3 leave.', 'response_code':0}, status=HTTP_200_OK)
    if request.data.get("leave_type_id") == '4' and int(float(total_no_of_leave_days)) > 3 and bool(request.FILES.get('attachment', False)) == False:
        return Response({'message': 'attachment is required for this leave', 'response_code':0}, status=HTTP_200_OK)
    
    consecutive_leave_counts     = SpUserLeavePolicyLedger.objects.filter(leave_type_id = request.data.get("leave_type_id"),user_id = request.data.get("user_id")).last() 
    if consecutive_leave_counts.year_leave_count == 00.00:
        return Response({'message': 'This holiday has been fully utilized', 'response_code':0}, status=HTTP_200_OK)
        
    
    if consecutive_leave_counts.year_leave_count:
        year_leave_count     = int(consecutive_leave_counts.year_leave_count)
    else:
        year_leave_count = 0
    # consecutive_leave_counts     = SpUserLeavePolicyLedger.objects.filter(leave_type_id = request.data.get("leave_type_id"),user_id = request.data.get("user_id")).last() 
    # if consecutive_leave_counts.consecutive_leave:
    #     consecutive_leave_count     = int(consecutive_leave_counts.consecutive_leave)
    # else:
    #     consecutive_leave_count = 0
   
    isLeaveAppliedOrNot  = checkLeaveAppliedOrNot(request.data.get("user_id"), request.data.get("leave_from_date"), request.data.get("leave_to_date"))
    if checkAttendanceMarkedOrNot(request.data.get("user_id"), request.data.get("leave_from_date"), request.data.get("leave_to_date"), today.strftime('%Y-%m-%d')):
        return Response({'message': 'Attendance already marked', 'response_code':0}, status=HTTP_200_OK)
    elif isLeaveAppliedOrNot['status'] == True:
        return Response({'message': 'You have already marked leave on selected dates, kindly select another date', 'response_code':0}, status=HTTP_200_OK)
    elif year_leave_count < total_no_of_leave_days:
        return Response({'message': f'You can not apply more than your remaining leave', 'response_code':0}, status=HTTP_200_OK)
    
    # elif consecutive_leave_count < total_no_of_leave_days:
    #     return Response({'message': f'You can apply leave only {consecutive_leave_count} days , kindly select another date', 'response_code':0}, status=HTTP_200_OK)
    elif checkApplyLeaveBefore(leave_from_date,consecutive_leave_counts.leave_policy_id,request.data.get("user_id"),consecutive_leave_counts.leave_type_id) == True:
        try:
            leave_policy_details = SpLeavePolicyDetails.objects.get(leave_policy_id = consecutive_leave_counts.leave_policy_id,leave_type_id=consecutive_leave_counts.leave_type_id)
        except SpLeavePolicyDetails.DoesNotExist:
            leave_policy_details = None
        apply_leave_before = int(leave_policy_details.apply_leave_before)
        return Response({'message': f'You can only apply leaves before {apply_leave_before} days, kindly select another date', 'response_code':0}, status=HTTP_200_OK)
    else: 
        try:
            leave_policy_details = SpLeavePolicyDetails.objects.get(leave_policy_id = consecutive_leave_counts.leave_policy_id,leave_type_id=consecutive_leave_counts.leave_type_id)
        except SpLeavePolicyDetails.DoesNotExist:
            leave_policy_details = None
        if bool(request.FILES.get('attachment', False)) == True:    
            uploaded_attachment = request.FILES['attachment']
            storage = FileSystemStorage()
            timestamp = int(time.time())
            attachment_name = uploaded_attachment.name
            temp = attachment_name.split('.')
            attachment_name = 'leave-document/leave_attachment_'+str(timestamp)+"."+temp[(len(temp) - 1)]
            attachment = storage.save(attachment_name, uploaded_attachment)
            attachment = storage.url(attachment)  
                
        
        # attachment = storage.save(attachment_name, document)
        # attachment = storage.url(attachment)  
        user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
        data = SpUserLeaves()
        data.user_id                = request.data.get("user_id")
        data.user_name              = user_name
        data.leave_type_id          = request.data.get("leave_type_id")
        data.leave_type             = getModelColumnById(SpLeaveTypes,request.data.get("leave_type_id"),'leave_type')
        data.leave_from_date        = request.data.get("leave_from_date")
        data.leave_to_date          = request.data.get("leave_to_date")
        if request.data.get("is_first_half_day") == "1":
            data.is_first_half_day = 1
        else:
            data.is_first_half_day = 0
        if request.data.get("is_last_half_day") == "1":
            data.is_last_half_day = 1
        else:
            data.is_last_half_day = 0
        data.leave_detail           = request.data.get('description')
        data.leave_status           = 1
        data.is_document_required   = leave_policy_details.is_document_required
        if bool(request.FILES.get('attachment', False)) == True:
            data.is_document_upload = 1
        data.attachment             = attachment
        data.is_document_required_count             = len(request.FILES.getlist('document'))
        data.save()
        user_leave_id  = data.id
        
        if request.data.get("handover_user_id"):
            userFirebaseToken = getModelColumnById(SpUsers,request.data.get("handover_user_id"),'firebase_token')
            employee_name = getUserName(request.data.get("handover_user_id"))

            message_title = "Leave Request Forwarded"
            message_body = "Leave Handover request has been sent by "+user_name
            notification_image = ""

            if userFirebaseToken is not None and userFirebaseToken != "" :
                registration_ids = []
                registration_ids.append(userFirebaseToken)
                data_message = {}
                data_message['id'] = 1
                data_message['status'] = 'notification'
                data_message['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
                data_message['image'] = notification_image
                send_android_notification(message_title,message_body,data_message,registration_ids)
                #-----------------------------notify android block-------------------------------#
                
                #-----------------------------save notification block----------------------------#
            saveNotification(user_leave_id,'SpUserLeaves','Users Management','Leave request forwarded',message_title,message_body,notification_image,request.data.get("user_id"),user_name,request.data.get("handover_user_id"),employee_name,'profile.png',2,'app.png',1,1)
            SpUserLeaves.objects.filter(id = user_leave_id).update(handover_user_id = request.data.get("handover_user_id"))
        #-----------------------------save notification block----------------------------#
                
       
        # sp_leave_type_documents
        document_id  = request.data.get('document_id')
        document_id = document_id.split(',')
        
        if bool(request.FILES.get('document', False)) == True:
            for i,document in enumerate(request.FILES.getlist('document')):
                # uploaded_attachment = request.FILES['attachment']
                
                storage = FileSystemStorage()
                timestamp = int(time.time())
                attachment_name = document.name
                temp = attachment_name.split('.')
                attachment_name = 'leave-document/leave_attachment_'+str(timestamp)+"."+temp[(len(temp) - 1)]
                
                attachment = storage.save(attachment_name, document)
                attachment = storage.url(attachment)  
                
                doc = SpUserLeaveDocument()  
                doc.user_id = request.data.get("user_id")
                doc.user_leave_id = user_leave_id
                doc.leave_type_document_id = document_id[i]
                doc.document = attachment
                doc.save()
        
            
                
        sendFocNotificationToUsers(data.id, '', 'add', 38, request.user.id, user_name, 'SpUserLeaves',request.user.role_id)
        
        heading     = 'New Leave Request has been initiated'
        activity    = 'New Leave Request has been initiated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
        
        saveActivity('Leave Management', 'Leave Request', heading, activity, request.user.id, user_name, 'add.png', '2', 'app.png')
        context = {}
        context['message']       = 'Leave Request has been successfully sent.'
        context['response_code'] = 1
        return Response(context, status=HTTP_200_OK)   
 
@csrf_exempt
@api_view(["POST"])
def appliedLeaves(request):
    if request.data.get("page_limit")is None or request.data.get("page_limit") == '':
        return Response({'message': 'Page limit is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   
    page_limit  = int(request.data.get("page_limit"))*10
    offset      = int(page_limit)-10
    page_limit  = 10
    leave_list_count = SpUserLeaves.objects.filter(user_id=request.data.get("user_id")).values('id').count()
        
    if leave_list_count:
        leave_list_count = math.ceil(round(leave_list_count/10, 2))
        leave_status     = SpUserLeaves.objects.filter(user_id=request.data.get("user_id")).order_by('-id').first()
        leave_status     = leave_status.leave_status 
    else:
        leave_list_count = 0 
        leave_status     = 0
    leave_list = SpUserLeaves.objects.filter(user_id=request.data.get("user_id")).values('id','user_id','user_name','leave_type_id','leave_type','leave_from_date','leave_to_date','leave_detail','leave_status','is_first_half_day','is_last_half_day','is_document_required','is_document_required_count').order_by('-id')[offset:offset+page_limit]
    for leave in leave_list:
        alias = getModelColumnById(SpLeaveTypes,leave['leave_type_id'],'alias')
        leave['leave_type'] = leave['leave_type']+" ("+ alias +")"
        uploaded_document_id = SpUserLeaveDocument.objects.filter(user_leave_id = leave['id']).values_list('leave_type_document_id',flat=True)
        pending_documents_list = SpLeaveTypeDocuments.objects.filter(leave_type_id  = leave['leave_type_id']).exclude(id__in  = uploaded_document_id).values('id','document')
        leave['pending_documents_list'] = list(pending_documents_list)
    
    basic_details_obj=SpBasicDetails.objects.filter(user_id=request.data.get("user_id")).first()
    if basic_details_obj:
        if basic_details_obj.week_of_day:
            week_off_day=basic_details_obj.week_of_day
        else:
            week_off_day=""
    else:
        week_off_day=""
        
        
    leave_type                      = SpUserLeavePolicyLedger.objects.filter(user_id = request.data.get("user_id")).values('leave_type_id').distinct()
    for leave in leave_type:
        try:
            leave_policy_id = SpUserLeavePolicyLedger.objects.filter(user_id = request.data.get("user_id"),leave_type_id = leave['leave_type_id']).first()
            is_half_day = SpLeavePolicyDetails.objects.get(leave_policy_id = leave_policy_id.leave_policy_id,leave_type_id =leave['leave_type_id'] )
            is_half_day = is_half_day.is_halfday_included
        except SpLeavePolicyDetails.DoesNotExist:
            is_half_day  = None
        year_leave_count = SpUserLeavePolicyLedger.objects.filter(user_id = request.data.get("user_id"),leave_type_id = leave['leave_type_id']).last()
        leave['leave_type']                 = getModelColumnById(SpLeaveTypes,leave_policy_id.leave_type_id ,'leave_type') + ' (' +  str(year_leave_count.year_leave_count) + ')'
        leave['is_halfday_included']        = is_half_day
        leave['year_leave_count']           = year_leave_count.year_leave_count
        leave['leave_policy_id']            = leave_policy_id.leave_policy_id
        leave['required_document_list']     =  list(SpLeaveTypeDocuments.objects.filter(leave_type_id = leave['leave_type_id']).values('id','document'))
        
        
    year_leave_count = SpUserLeavePolicyLedger.objects.filter(user_id = request.data.get("user_id")).last()
    if year_leave_count:
       year_leave_count =  year_leave_count.balance
    else:
        year_leave_count = 0
    context = {}
    context['message']              = 'Success'
    context['leave_list']           = list(leave_list)
    context['leave_list_count']     = leave_list_count
    context['leave_type_list']      = list(leave_type)
    context['leave_count']          = year_leave_count
    context['leave_status']         = leave_status
    context['week_off_day']    = week_off_day
    
    context['response_code']        = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)

        
       
        
@csrf_exempt
@api_view(["POST"])
def saveUserTracking(request):
    today  = datetime.now()
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
   
    if request.data.get("latitude")is None or request.data.get("latitude") == '' or request.data.get("longitude")is None or request.data.get("longitude") == '':
        return Response({'message': 'Coordinates is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  
    if SpUserTracking.objects.filter(user_id=request.data.get("user_id"), created_at__icontains=today.strftime("%Y-%m-%d")).exists():
        user_last_data = SpUserTracking.objects.filter(user_id=request.data.get("user_id"), created_at__icontains=today.strftime("%Y-%m-%d")).order_by('-id').first()
        # if user_last_data:
        #     diff = today - user_last_data.created_at  
        #     diff_minutes = (diff.days * 24 * 60) + (diff.seconds/60)
        # else:
        #     diff_minutes = 3
        # if diff_minutes > 2:
        R = 6373.0
        lat1 = radians(float(user_last_data.latitude))
        lon1 = radians(float(user_last_data.longitude))
        lat2 = radians(float(request.data.get("latitude")))
        lon2 = radians(float(request.data.get("longitude")))
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        meter_distance = float(distance * 1000)
        if meter_distance > 15 :
            user_data                       = SpUserTracking()
            user_data.user_id               = request.data.get("user_id")
            user_data.latitude              = request.data.get("latitude")
            user_data.longitude             = request.data.get("longitude")
            user_data.distance_travelled    = meter_distance
            user_data.accuracy              = request.data.get("accuracy")
            user_data.travel_charges        = getModelColumnById(Configuration, 1, 'travel_amount')
            user_data.save()
    else:
        user_data                       = SpUserTracking()
        user_data.user_id               = request.data.get("user_id")
        user_data.latitude              = request.data.get("latitude")
        user_data.longitude             = request.data.get("longitude")
        user_data.accuracy             = request.data.get("accuracy")
        user_data.distance_travelled    = 0
        user_data.travel_charges = getModelColumnById(Configuration, 1, 'travel_amount')
    
    start_data  = SpUserAttendance.objects.filter(start_time__isnull=False, attendance_date_time__icontains=today.strftime("%Y-%m-%d"), user_id=request.data.get("user_id")).count()
    end_data    = SpUserAttendance.objects.filter(end_time__isnull=False, attendance_date_time__icontains=today.strftime("%Y-%m-%d"), user_id=request.data.get("user_id")).count()
    if start_data == 0:
        attendance_status = 0
    elif int(start_data)!=int(end_data):
        attendance_status = 1
    else:
        attendance_status = 0
        
    context = {}
    context['attendance_status']        = attendance_status
    context['message']                  = 'Tracking data saved successfully successfully'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)
        


def send_email(subject, html_content, text_content=None, from_email=None, recipients=[], attachments=[], bcc=[], cc=[]):
    # send email to user with attachment
    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL
    if not text_content:
        text_content = ''
    email = EmailMultiAlternatives(
        subject, text_content, from_email, recipients, bcc=bcc, cc=cc
    )
    email.attach_alternative(html_content, "text/html")
    for attachment in attachments:
        # Example: email.attach('design.png', img_data, 'image/png')
        email.attach(*attachment)
    email.send()

def get_rendered_html(template_name, context={}):
    html_content = render_to_string(template_name, context)
    return html_content

def send_mass_mail(data_list):
    for data in data_list:
        template = data.pop('template')
        context = data.pop('context')
        html_content = get_rendered_html(template, context)
        data.update({'html_content': html_content})
        send_email(**data)  



@csrf_exempt
@api_view(["POST"])
def updateUserLocation(request):
    
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("latitude")is None or request.data.get("latitude") == '':
        return Response({'message': 'Latitude field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("longitude")is None or request.data.get("longitude") == '':
        return Response({'message': 'Longitude field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  


    user                = SpUsers.objects.get(id=request.data.get("user_id"))
    user.latitude       = request.data.get("latitude")
    user.longitude      = request.data.get("longitude")
    user.periphery      = '500'
    user.timing         = '6:00 AM'
    user.save()

    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = 'Location has been updated'
    activity    = 'Location has been updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('Location', 'Location updated', heading, activity, request.user.id, user_name, 'UserCredentialChange.png', '2', 'app.png')

    context = {}
    context['latitude']     = request.data.get("latitude")
    context['longitude']    = request.data.get("longitude")
    context['periphery']    = '500'
    context['timing']       = '6:00 AM'
    context['message']      = 'Location has been successfully updated'
    context['response_code'] = HTTP_200_OK
    
    return Response(context, status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def logout(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    AuthtokenToken.objects.filter(user_id=request.user.id).delete()

    # clear firebase token
    SpUsers.objects.filter(id=request.user.id).update(firebase_token=None)
    user = SpUsers.objects.get( id= request.data.get("user_id"))
    user.device_id = None
    user.save()
    
    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = user_name+' has been logout'
    activity    = user_name+' has been logout on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('Logout', 'Logout', heading, activity, request.user.id, user_name, 'add.png', '2', 'app.png')
    context = {}
    context['message'] = 'Logout successfully'
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)



#get master data
@csrf_exempt
@api_view(["POST"])
def getMasterData(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
    leave_type                      = SpUserLeavePolicyLedger.objects.filter(user_id = request.data.get("user_id")).values('leave_type_id').distinct()
    for leave in leave_type:
        try:
            leave_policy_id = SpUserLeavePolicyLedger.objects.filter(user_id = request.data.get("user_id"),leave_type_id = leave['leave_type_id']).first()
            is_half_day = SpLeavePolicyDetails.objects.get(leave_policy_id = leave_policy_id.leave_policy_id,leave_type_id =leave['leave_type_id'] )
            is_half_day = is_half_day.is_halfday_included
        except SpLeavePolicyDetails.DoesNotExist:
            is_half_day  = None
        year_leave_count = SpUserLeavePolicyLedger.objects.filter(user_id = request.data.get("user_id"),leave_type_id = leave['leave_type_id']).last()
        leave['leave_type']                 = getModelColumnById(SpLeaveTypes,leave_policy_id.leave_type_id ,'leave_type') 
        leave['is_halfday_included']        = is_half_day
        leave['year_leave_count']           = year_leave_count.year_leave_count
        leave['leave_policy_id']            = leave_policy_id.leave_policy_id
        leave['required_document_list']     =  list(SpLeaveTypeDocuments.objects.filter(leave_type_id = leave['leave_type_id']).values('id','document'))

    department_id                   = getModelColumnById(SpUsers,request.data.get("user_id"),'department_id')
    handover_emp_list               = SpUsers.objects.filter(department_id = department_id).exclude(id__in=[request.data.get("user_id"),0]).values('id','first_name','middle_name','last_name')
    
    context = {}
    context['state_list']               = SpStates.objects.all().values('id', 'state')
    context['city_list']                = SpCities.objects.all().values('id', 'state_id', 'city')
    context['leave_type_list']          = list(leave_type)
    context['handover_emp_list']        = list(handover_emp_list)
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)




# New Api Added By Sushil


@csrf_exempt
@api_view(["POST"])
def userAttendance(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("type")is None or request.data.get("type") == '':
        return Response({'message': 'Attendance type is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("attendance_date_time")is None or request.data.get("attendance_date_time") == '':
        return Response({'message': 'Attendance DateTime field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    
    # if datetime.now().strftime('%H:%M:%S') > '09:45:00' and request.data.get("type") == '1':
    if datetime.strptime(str(request.data.get("attendance_date_time")), '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S') > '09:45:00' and request.data.get("type") == '1':
        return Response({'message': "You Can't mark attendance at this time, kindly contact admin..", 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)      
    
    data = SpUserAttendance()
    data.user_id = request.data.get("user_id")
    data.attendance_date_time = request.data.get("attendance_date_time")
    now = datetime.strptime(str(request.data.get("attendance_date_time")), '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
    # now = datetime.now().strftime('%H:%M:%S')
    if request.data.get("type") == '1':
        data.start_time = now
        data.end_time = None
    else:
        data.start_time = None
        data.end_time = now
    
    if int(request.data.get("type")) == 1:
        data.dis_ss_id = request.data.get("user_id")

    if request.data.get("latitude") is None or request.data.get("latitude") == '':
        data.latitude = None
    else:
        data.latitude = request.data.get("latitude")
    
    if request.data.get("longitude") is None or request.data.get("longitude") == '':
        data.longitude = None
    else:
        data.longitude = request.data.get("longitude")
    
    data.attendance_type = 1
 
    if bool(request.FILES.get('attendance_image', False)) == True:
        uploaded_attendance_image = request.FILES['attendance_image']
        storage = FileSystemStorage()
        timestamp = int(time.time())
        attendance_image_name = uploaded_attendance_image.name
        temp = attendance_image_name.split('.')
        attendance_image_name = 'attendance'+str(timestamp)+"."+temp[(len(temp) - 1)]
        
        attendance_image = storage.save(attendance_image_name, uploaded_attendance_image)
        attendance_image = storage.url(attendance_image)
    
        data.attendance_img = attendance_image 
    data.status = 1
    data.save()
    
    # save tracking

    if (request.data.get("latitude") is not None and request.data.get("latitude") != '') and (request.data.get("longitude") is not None and request.data.get("longitude") != ''):

        if TblClUserTracking.objects.filter(user_id=request.data.get("user_id")).exists():
            
            user_last_data = TblClUserTracking.objects.filter(user_id=request.data.get("user_id")).order_by('-id').first()
            
            R = 6373.0
            lat1 = radians(float(user_last_data.latitude))
            lon1 = radians(float(user_last_data.longitude))
            lat2 = radians(float(request.data.get("latitude")))
            lon2 = radians(float(request.data.get("longitude")))
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = R * c
            meter_distance = float(distance * 1000)
            if meter_distance > 15 :
                user_data                       = SpUserTracking()
                user_data.user_id               = request.data.get("user_id")
                user_data.latitude              = request.data.get("latitude")
                user_data.longitude             = request.data.get("longitude")
                user_data.distance_travelled    = 0
                user_data.travel_charges        = getModelColumnById(Configuration, 1, 'travel_amount')
                user_data.save()
        else:
            user_data                       = SpUserTracking()
            user_data.user_id               = request.data.get("user_id")
            user_data.latitude              = request.data.get("latitude")
            user_data.longitude             = request.data.get("longitude")
            user_data.distance_travelled    = 0
            user_data.travel_charges        = getModelColumnById(Configuration, 1, 'travel_amount')
            user_data.save()
            
    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    
    heading     = 'Attendance'
    if request.data.get("type") == '1':
        activity    = "Day started"
    else:
        activity    = "Day end" 
        
    saveActivity('User Attendance', 'User Attendance', heading, activity, request.user.id, user_name, 'markedAtten.png', '2', 'app.png')


    context = {}
    context['message'] = 'Attendance marked successfully'
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)
       


@csrf_exempt
@api_view(["POST"])
def checkAttendance(request):
    today   = date.today()
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    context = {}
    if SpUserAttendance.objects.filter(attendance_date_time__icontains=today.strftime("%Y-%m-%d"), user_id=request.data.get("user_id")).exists():
        start_data      = SpUserAttendance.objects.filter(start_time__isnull=False,attendance_date_time__icontains=today.strftime("%Y-%m-%d"),user_id=request.data.get("user_id")).order_by('id').first()
        end_data        = SpUserAttendance.objects.filter(end_time__isnull=False,attendance_date_time__icontains=today.strftime("%Y-%m-%d"),user_id=request.data.get("user_id")).order_by('-id').first()
        user_attendance = SpUserAttendance.objects.filter(attendance_date_time__icontains=today.strftime("%Y-%m-%d"), user_id=request.data.get("user_id")).order_by('-id').first()
        if user_attendance.start_time is not None and user_attendance.end_time is None:
            context['status'] = 1
        elif user_attendance.start_time is None and user_attendance.end_time is not None:
            context['status'] = 0
        else:
            context['status'] = 0
        now = datetime.now().strftime('%Y-%m-%d')
        start_datetime = now + ' '+start_data.start_time
        if context['status'] == 0:
            end_datetime = now + ' '+end_data.end_time
        else:
            end_datetime = now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        start_datetime = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
        time_delta = (end_datetime - start_datetime)
        # total_seconds = time_delta.total_seconds()
        # hours = (total_seconds/60)/60
        time_delta = str(time_delta).split(':')
        time_delta = time_delta[0]+':'+time_delta[1]
        context['working_hours'] = str(time_delta) + ' hours'
    else:
        context['status'] = 0
        context['working_hours'] = ''
        
    if getModelColumnById(SpUsers, request.data.get("user_id"), 'periphery')is None or getModelColumnById(SpUsers, request.data.get("user_id"), 'periphery') == '':
        periphery = '500'
    else:
        periphery = getModelColumnById(SpUsers, request.data.get("user_id"), 'periphery')

    # if getModelColumnById(SpUsers, request.data.get("user_id"), 'timing')is None or getModelColumnById(SpUsers, request.data.get("user_id"), 'timing') == '':
    #     timing = ''
    # else:
    #     timing = getModelColumnById(SpUsers, request.data.get("user_id"), 'timing')


    current_time = datetime.now().strftime("%H:%M:%S")
    working_shifts = TblClAllocatedShifts.objects.filter(user_id = request.data.get("user_id"))
    for each_shift in working_shifts:
        if TblClWorkingShifts.objects.filter(id = each_shift.working_shift_id, start_timing__lte = current_time, end_timing__gte = current_time).exists():
            shift_timings = TblClWorkingShifts.objects.filter(id = each_shift.working_shift_id, start_timing__lte = current_time, end_timing__gte = current_time).values('id','start_timing','end_timing').first()
            context['timing']        = shift_timings

    working_shift_timing = TblClWorkingShifts.objects.filter(id=getModelColumnByColumnId(SpBasicDetails, 'user_id', request.data.get("user_id"), 'working_shift_id')).values('id','start_timing','end_timing').first()
    
    holidays = SpHolidays.objects.filter(start_date__month = date.today().strftime('%m'),start_date__year = date.today().strftime('%Y'))
    holiday_lists= []
    
    for holiday in holidays:
        holiday_list = getHoilydayDates(holiday.start_date,holiday.end_date)
        holiday_dict = {}
        current_date = date.today().strftime('%Y-%m-%d')
        if str(current_date) in holiday_list:
            holiday_dict['holiday_name'] = holiday.holiday
            holiday_lists.append(holiday_dict)
            
    week_of_day_list = getModelColumnByColumnId(SpBasicDetails,'user_id',request.data.get("user_id"),'week_of_day')
    week_of_day_list  = week_of_day_list.split(',')
    
    context['periphery']     = periphery
    context['week_of_day_list']     = week_of_day_list
    context['holiday_lists'] = holiday_lists
    context['geofence']      = getModelColumnByColumnId(SpBasicDetails, "user_id", request.data.get("user_id"), "geofencing")
    # context['timing']        = working_shift_timing  
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)



@api_view(['POST'])
def getDashboardData(request):
    if request.method == 'POST':
        if request.data.get("user_id") is None or request.data.get("user_id") == '':
            return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 

        _user_id = request.data.get('user_id')
        _current_date = date.today()

        total_present       = 0
        total_leaves        = 0
        total_absent        = 0
        # activity_type_name  = ''
        # distributor_name    = ''
        # beat_name           = ''
        start_time          = ''
        end_time            = ''
        hours_worked        = ''
        total_retail_time   = datetime.strptime('00:00:00', '%H:%M:%S')
        monthly_retail_time = datetime.strptime('00:00:00', '%H:%M:%S')

        # try:
        total_present       = SpUserAttendance.objects.filter(start_time__isnull=False, user_id = _user_id).filter(attendance_date_time__month = _current_date.month).filter(attendance_date_time__year = _current_date.year).count()
        
        # productivity_call   = SpSalesQuotation.objects.filter(user_id = _user_id, quotation_datetime__contains = _current_date)
        # monthly_productivity= SpSalesQuotation.objects.filter(user_id = _user_id, quotation_datetime__month = _current_date.month, quotation_datetime__year = _current_date.year)
        new_outlets         = SpUsers.objects.filter(created_by = _user_id,created_at__contains = _current_date)
        
        monthly_outlets     = SpUsers.objects.filter(created_by = _user_id, created_at__month = _current_date.month, created_at__year = _current_date.year)
        # new_visits          = SpVisits.objects.filter(user_id = _user_id,checkin_datetime__contains = _current_date)
        
        # monthly_visits      = SpVisits.objects.filter(user_id = _user_id, checkin_datetime__month = _current_date.month, checkin_datetime__year = _current_date.year)
        # beat_plan           = SpBeatPlan.objects.filter(employee_id = _user_id, scheduled_beat_date__contains = _current_date)
        # todays_todo         = SpSalesTodo.objects.filter(user_id = _user_id, todo_schedule_datetime__contains = _current_date)
        
        on_leave            = 0

        all_month_date = days_cur_month(_current_date.day, _current_date.month, _current_date.year)

        now_leaves_list             = []
        total_leaves_list           = []
        total_no_of_weekoff_list    = []
        total_days = []
        for i in range(len(all_month_date)):
            total_leaves  = get_user_month_leave_count(_user_id, all_month_date[i])
            if i<int(_current_date.strftime("%d")):
                total_days.append(1)
                total_no_of_weekoff = get_total_no_of_weekoff(_user_id, all_month_date[i])
                total_no_of_weekoff_list.append(total_no_of_weekoff)
                now_leaves_list.append(total_leaves)
                
            total_leaves_list.append(total_leaves)

        total_no_of_weekoff = sum(total_no_of_weekoff_list)     
        total_leaves        = sum(total_leaves_list)
        now_total_leaves    = sum(now_leaves_list)
        
        leave_date_day      = datetime.strptime(str(_current_date.strftime("%Y-%m-%d")), '%Y-%m-%d').strftime('%A')
        user_week_off_day   = SpBasicDetails.objects.filter(user_id=_user_id).values('week_of_day').first()

        if get_user_leave(_user_id,_current_date.strftime("%Y-%m-%d")):
            on_leave = 2
        elif str(user_week_off_day['week_of_day']) == str(leave_date_day): 
            on_leave = 1
        else:
            on_leave = 0    

        today_attendance   = SpUserAttendance.objects.filter(start_time__isnull=False,user_id = _user_id).filter(attendance_date_time__icontains=_current_date.strftime("%Y-%m-%d")).count()
        total_absent = (int(sum(total_days))-int(total_no_of_weekoff))-float(now_total_leaves)
        
        if int(today_attendance) == 0:
            total_absent = (float(total_absent)-int(total_present))-1
        else:
            total_absent = float(total_absent)-int(total_present)
        working_hours = SpUserAttendance.objects.filter(user_id = _user_id).filter(attendance_date_time__contains = _current_date)

        for each_time in working_hours:
            if each_time.start_time is None or each_time.start_time == '':
                pass
            else:
                start_time  = each_time.start_time
            if each_time.end_time == '' or each_time.end_time is None:
                pass
            else:
                end_time    = each_time.end_time
            
        if end_time == '' or end_time is None or start_time == '' or start_time is None:
            hours_worked = ''
        else:
            hours_worked = str(datetime.strptime(end_time, '%H:%M:%S') - datetime.strptime(start_time, '%H:%M:%S'))

        last_seven_date_from_current = _current_date - timedelta(days=6)
        graph_data=[]

        if getModelColumnById(SpUsers, request.data.get("user_id"), 'periphery')is None or getModelColumnById(SpUsers, request.data.get("user_id"), 'periphery') == '':
            periphery = '500'
        else:
            periphery = getModelColumnById(SpUsers, request.data.get("user_id"), 'periphery')       
        holidays = SpHolidays.objects.filter(start_date__month = date.today().strftime('%m'),start_date__year = date.today().strftime('%Y'))
        holiday_lists= []
        
        for holiday in holidays:
            holiday_list = getHoilydayDates(holiday.start_date,holiday.end_date)
            holiday_dict = {}
            current_date = date.today().strftime('%Y-%m-%d')
            applicable_to = holiday.applicable_to.split(',')
            role_id = getModelColumnById(SpUsers, request.data.get("user_id"), 'role_id')
            if str(current_date) in holiday_list and str(role_id) in applicable_to:
                holiday_dict['holiday_name'] = holiday.holiday
                holiday_lists.append(holiday_dict)
                
                
        week_of_day_list = getModelColumnByColumnId(SpBasicDetails,'user_id',request.data.get("user_id"),'week_of_day')
        week_of_day_list  = week_of_day_list.split(',')
        
        
        if holiday_lists:
            is_holiday = 1
            
        else:
            is_holiday = 0
            
            
        if date.today().strftime('%A') in week_of_day_list:
            is_week_of = 1
            
        else:
            is_week_of = 0
        
        
        
        
        
        
        
        total_presentss   = 0
        total_leave     = 0
        total_absent    = 0
        
        total_week_of    = 0
        total_holiday    = 0
        
        user_id = request.data.get('user_id')
        current_date  = datetime.today()
        all_month_date  = days_cur_month(current_date.day, current_date.month, current_date.year)

        user_week_off_day   = SpBasicDetails.objects.filter(user_id=user_id).first()
        user_week_off_day = user_week_off_day.week_of_day.split(',')

        role_id = getModelColumnById(SpUsers,user_id,'role_id')
        
        for i in range(len(all_month_date)):
            attendance_dict = {}
            leave_date_day      = datetime.strptime(str(all_month_date[i]), '%Y-%m-%d').strftime('%A')
            total_presents   = SpUserAttendance.objects.filter(start_time__isnull=False, user_id=user_id).filter(attendance_date_time__icontains=all_month_date[i]).count()
            if total_presents > 0:
                attendance_dict['attendance'] = 1  
                total_presentss+=1
            elif checkHoliday(all_month_date[i],role_id):
                total_holiday+=1
            elif str(leave_date_day) in user_week_off_day: 
                total_week_of+=1
            elif get_user_leave(user_id,all_month_date[i]) :
                total_leave+=1
            else:
                total_presents   = SpUserAttendance.objects.filter(start_time__isnull=False, user_id=user_id).filter(attendance_date_time__icontains=all_month_date[i]).count()
                if total_presents > 0 and isHalfDay(user_id, all_month_date[i]) == True:
                    pass
                elif total_presents > 0:
                    pass
                else:
                    if checkDateIsFutureDate(all_month_date[i]):
                        if isHalfDay(user_id, all_month_date[i]):
                            pass
                        else:
                            pass 
                    else:
                        if isHalfDay(user_id, all_month_date[i]):    
                            pass
                        else:
                            total_absent+=1
 
        context = {}
        context['is_holiday']       = is_holiday
        context['is_week_of']       = is_week_of  
        context['periphery']        = periphery
        context['graph_data']       = graph_data
        context['total_present']    = total_presentss
        context['total_leave']      = total_leave
        context['total_absent']     = total_absent
        context['start_time']       = start_time
        context['end_time']         = end_time
        context['working_hours']    = hours_worked
        context['on_leave']         = on_leave
        context['new_calls']        = len(new_outlets)
        context['monthly_new_calls']= len(monthly_outlets)
        context['avg_new_calls']    = round(len(monthly_outlets)/len(all_month_date), 2)
        context['total_retail_time']  = total_retail_time
        context['montly_retail_time'] = monthly_retail_time
        context['travel_charge']      = getConfigurationResult('travel_charge')
        context['bmc_list']           = SpBMC.objects.filter().values('id','name','bmc_code').order_by('bmc_code')
        context['mpp_list']           = SpMPP.objects.filter().values('id','name','mpp_code').order_by('mpp_code')
        
        context['purpose_list']       = SpVisitPurpose.objects.filter().values().order_by('purpose_name')
        context['attendance_type']    = SpUsers.objects.filter(id=request.data.get("user_id")).values_list('attendence_mode',flat=True).first()
        context['regularization_list']= SpRegularization.objects.filter().values('id','regularization_type').order_by('regularization_type')
        context['message']            = "Dashboard Data attained successfully"
        context['status']             = HTTP_200_OK

        return Response(context)
        




def checkHoliday(date,role_id):
    if SpHolidays.objects.filter(start_date__month = datetime.strptime(str(date), '%Y-%m-%d').strftime('%m'),start_date__year = datetime.strptime(str(date), '%Y-%m-%d').strftime('%Y'),holiday_status=3,status = 1).exists():
        holiday_id = SpHolidays.objects.filter(start_date__month = datetime.strptime(str(date), '%Y-%m-%d').strftime('%m'),start_date__year = datetime.strptime(str(date), '%Y-%m-%d').strftime('%Y'),holiday_status=3,status = 1).values_list('id',flat=True)
        holiday_ids = SpRoleEntityMapping.objects.filter(role_id = role_id,entity_type = 'holiday',entity_id__in = holiday_id).values_list('entity_id',flat=True)
        count = 0
        holiday_name_list = []
        for holiday_id in holiday_ids:
            last_date = getModelColumnById(SpHolidays,holiday_id,'end_date')
            last_date = last_date.strftime('%Y-%m-%d')
            last_date = datetime.strptime(str(last_date), '%Y-%m-%d')
            from_date = datetime.strptime(str(date), '%Y-%m-%d')#.strftime('%Y-%m-%d')
            delta = last_date - from_date
            start_date = getModelColumnById(SpHolidays,holiday_id,'start_date')
            start_date = start_date.strftime('%Y-%m-%d')
            start_date = datetime.strptime(str(start_date), '%Y-%m-%d')
            current_date = datetime.strptime(str(date), '%Y-%m-%d')
            if current_date>=start_date:
                if delta.days >= 0:
                    count+=1
                    holiday_name_list.append(getModelColumnById(SpHolidays,holiday_id,'holiday'))
        if count > 0:
            holi_list = []
            for x in holiday_name_list:
                if x not in holi_list:
                    holi_list.append(x)
            return holi_list
        else:
            return False 
    else:
        return False 
        
        
        

@csrf_exempt
@api_view(['POST'])
def getAttendanceData(request):
    if request.method == 'POST':
        if request.data.get("user_id")is None or request.data.get("user_id") == '':
            return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
        if request.data.get("current_date")is None or request.data.get("current_date") == '':
            return Response({'message': 'Date field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
        
        LEAVE_FLAG      = 0
        PRESENT_FLAG    = 1
        FUTURE_FLAG     = 2
        WEEK_OFF_FLAG   = 3
        ABSENT_FLAG     = 4
        
        today           = date.today()
        attendance_list = []
        
        total_presentss   = 0
        total_leave     = 0
        total_absent    = 0
        
        total_week_of    = 0
        total_holiday    = 0
        
        total_travelled = 0
        today_travelled = 0
        user_id         = request.data.get('user_id')
        current_date    = datetime.strptime(request.data.get('current_date'), "%Y-%m-%d")
        total_present   = SpUserAttendance.objects.filter(start_time__isnull=False, user_id=user_id).filter(attendance_date_time__month=current_date.month).filter(attendance_date_time__year=current_date.year).count()
        
        all_month_date  = days_cur_month(current_date.day, current_date.month, current_date.year)

        
        user_week_off_day   = SpBasicDetails.objects.filter(user_id=user_id).first()
        user_week_off_day = user_week_off_day.week_of_day.split(',')

        now_leaves_list             = []
        total_leaves_list           = []
        total_no_of_weekoff_list    = []
        total_days                  = []
        total_distance_travel       = []
        
        role_id = getModelColumnById(SpUsers,user_id,'role_id')
        
        for i in range(len(all_month_date)):
            attendance_dict = {}
            leave_date_day      = datetime.strptime(str(all_month_date[i]), '%Y-%m-%d').strftime('%A')
            total_presents   = SpUserAttendance.objects.filter(start_time__isnull=False, user_id=user_id).filter(attendance_date_time__icontains=all_month_date[i]).count()
            if total_presents > 0:
                attendance_dict['attendance'] = 1  
                total_presentss+=1
            elif checkHoliday(all_month_date[i],role_id):
                attendance_dict['attendance'] = 7
                attendance_dict['holiday_list'] = checkHoliday(all_month_date[i],role_id)
                total_holiday+=1
            elif str(leave_date_day) in user_week_off_day: 
                attendance_dict['attendance'] = 3
                
                total_week_of+=1
            elif get_user_leave(user_id,all_month_date[i]) :
                attendance_dict['attendance'] = 0
                total_leave+=1
            else:
                total_presents   = SpUserAttendance.objects.filter(start_time__isnull=False, user_id=user_id).filter(attendance_date_time__icontains=all_month_date[i]).count()
                if total_presents > 0 and isHalfDay(user_id, all_month_date[i]) == True:
                    attendance_dict['attendance'] = 6
                elif total_presents > 0:
                    # attendance_dict['attendance'] = 1  
                    # total_presentss+=1
                    pass
                else:
                    if checkDateIsFutureDate(all_month_date[i]):
                        if isHalfDay(user_id, all_month_date[i]):
                            attendance_dict['attendance'] = 5
                        else:
                            attendance_dict['attendance'] = 2   
                    else:
                        if isHalfDay(user_id, all_month_date[i]):    
                            attendance_dict['attendance'] = 5
                        else:
                            attendance_dict['attendance'] = 4  
                            total_absent+=1
            
            
            attendance_dict['date']                 = all_month_date[i]
            attendance_data = getAttendanceStartEndTime(user_id, all_month_date[i])
            if attendance_data['starting_time']:
                # attendance_dict['distance_travelled']   = getUserTravelData(user_id, all_month_date[i])
                attendance_dict['starting_time']        = attendance_data['starting_time']
                attendance_dict['ending_time']          = attendance_data['ending_time']
                attendance_dict['working_hours']        = attendance_data['working_hours']
            # else:
            #     attendance_dict['distance_travelled']   = 0
            # total_distance_travel.append(attendance_dict['distance_travelled'])        
            attendance_list.append(attendance_dict)

            total_leaves  = get_user_month_leave_count(user_id, all_month_date[i])
            
            if (str(current_date.strftime("%m")) == str(today.strftime("%m"))) and (str(current_date.strftime("%Y")) == str(today.strftime("%Y"))):
                if i<int(today.strftime("%d")):
                    total_days.append(1)
                    now_leaves_list.append(total_leaves)
            else:
                total_days.append(1)
                now_leaves_list.append(total_leaves)

            if i<=int(today.strftime("%d")):                          
                total_no_of_weekoff = get_total_no_of_weekoff(user_id, all_month_date[i])    
                total_no_of_weekoff_list.append(total_no_of_weekoff)
            total_leaves_list.append(total_leaves)
        
        total_no_of_weekoff = sum(total_no_of_weekoff_list)     
        total_leave         = sum(total_leaves_list)
        now_total_leaves    = sum(now_leaves_list)
        
        today_attendance   = SpUserAttendance.objects.filter(start_time__isnull=False, user_id = user_id).filter(attendance_date_time__icontains=today.strftime("%Y-%m-%d")).count()
        # total_absent = (int(sum(total_days))-int(total_no_of_weekoff))-float(now_total_leaves)
        
        # if int(today_attendance) == 0:
        #     if (str(current_date.strftime("%m")) == str(today.strftime("%m"))) and (str(current_date.strftime("%Y")) == str(today.strftime("%Y"))):
        #         total_absent = (float(total_absent)-int(total_present))-1
        #     else:
        #         total_absent = (float(total_absent)-int(total_present))  
        # else:
        #     if int(current_date.strftime("%Y")) > int(today.strftime("%Y")):
        #         total_absent = 0
        #     else:
        #         total_absent = float(total_absent)-int(total_present)    
        
        context = {}
        
        
        context['total_present']    = total_presentss
        context['total_leave']      = total_leave
        context['total_absent']     = total_absent
        context['total_week_of']     = total_week_of
        context['total_holiday']     = total_holiday
        
        # context['today_travelled']  = getUserTravelData(user_id, today.strftime("%Y-%m-%d"))
        # context['total_travelled']  = round(sum(total_distance_travel),2)
        context['attendance']       = attendance_list
        context['message']          = "Attendance Data has been received successfully"
        context['status']           = HTTP_200_OK
        return Response(context)




def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

def getAttendanceStartEndTime(user_id, month_date):
    start_data      = SpUserAttendance.objects.filter(start_time__isnull=False,attendance_date_time__icontains=month_date,user_id=user_id).order_by('id').first()
    end_data        = SpUserAttendance.objects.filter(end_time__isnull=False,attendance_date_time__icontains=month_date,user_id=user_id).order_by('-id').first()
    
    try:
        user_attendance = SpUserAttendance.objects.filter(attendance_date_time__icontains=month_date, user_id=user_id).order_by('-id').first()
    except SpUserAttendance.DoesNotExist:
        user_attendance = None

    start_datetime  = ''
    end_datetime    = ''
    working_hours   = ''
    if user_attendance:
        if user_attendance.start_time is not None and user_attendance.end_time is None:
            status = 1
        elif user_attendance.start_time is None and user_attendance.end_time is not None:
            status = 0
        else:
            status = 0
        now = datetime.now().strftime('%Y-%m-%d')
        start_datetime = now + ' '+start_data.start_time
        if status == 0:
            end_datetime = now + ' '+end_data.end_time

            start_datetime = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
            end_datetime = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
            time_delta = (end_datetime - start_datetime)
            total_seconds = time_delta.total_seconds()
            hours = convert(total_seconds)
            working_hours = str(hours)

            start_datetime = datetime.strptime(str(start_datetime), '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
            end_datetime   = datetime.strptime(str(end_datetime), '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
        else:
            end_datetime = ''
            start_datetime = datetime.strptime(str(start_datetime), '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')

    attendance_timing = {}
    attendance_timing['starting_time']  = start_datetime
    attendance_timing['ending_time']    = end_datetime
    attendance_timing['working_hours']  = working_hours

    return attendance_timing  

@csrf_exempt
@api_view(["POST"])
def userLocationLog(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("status") is None or request.data.get("status") == '':
        return Response({'message': 'Status field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("date_time") is None or request.data.get("status") == '':
        return Response({'message': 'Date Time field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    user_id = request.data.get("user_id")
    status = request.data.get("status")
    today = datetime.now()
    try:
        email = SpUsers.objects.get(id=user_id)
    except SpUsers.DoesNotExist:
        email = None
    try:
        user_tracking = SpUserTracking.objects.filter(
            user_id=user_id).order_by('-id').count()
        if user_tracking > 1:
            user_tracking = SpUserTracking.objects.filter(
                user_id=user_id).order_by('-id')[1]
        else:
            user_tracking = SpUserTracking.objects.filter(
                user_id=user_id).order_by('-id')[0]
    except SpUserTracking.DoesNotExist:
        user_tracking = None
    if status == '1':
        pre_date_time = datetime.strptime(
            request.data.get("date_time"), '%Y-%m-%d %H:%M:%S')
        if email.official_email:
            user_email = email.official_email
            user_name = email.first_name
            location_log = SpUserLocationLogs.objects.filter(
                user_id=user_id, created_at__icontains=today.strftime("%Y-%m-%d"), status=1).last()
            if location_log:
                diff = today - location_log.created_at
                diff_minutes = (diff.days * 24 * 60) + (diff.seconds/60)
            else:
                diff_minutes = 3
            if user_tracking:
                latitude = user_tracking.latitude
                longitude = user_tracking.longitude
                last_loc_date = user_tracking.created_at
            date_time = datetime.now()
            message = {
                'subject': f'Employee App Notification - App not reachable ({user_name})',
                'text_content': 'Here is the message',
                'from_email'    : 'balineemilk@outlook.com',
                'recipients'    : ['mohdsubhani33143@gmail.com'
 
                              ],
                'template': "email-templates/user-notification.html",
                'context': {
                    "user_name":   user_name,
                    "date_time":   date_time,
                    "pre_date_time":   pre_date_time,
                    "latitude":   latitude,
                    "longitude":   longitude,
                    "last_loc_date":   last_loc_date,
                    "status":   1,
                }
            }

            user_message = {
                'subject': 'Employee App Notification - App not reachable',
                'text_content': 'Here is the message',
                'from_email': 'balineemilk@outlook.com',
                'recipients': [user_email],
                'template': "email-templates/users-notification.html",
                'context': {
                    "user_name":   user_name,
                    "date_time":   date_time,
                    "pre_date_time":   pre_date_time,
                    "status":   1,
                }
            }
        else:
            return Response({'message': 'E-mail Id Not Exist', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
        if diff_minutes > 2:
            send_mass_mail([message])
            send_mass_mail([user_message])
            user_location_log = SpUserLocationLogs()
            user_location_log.user_id = user_id
            user_location_log.particular = 'Internet data is off'
            user_location_log.status = 1
            user_location_log.save()
    else:
        if email.official_email:
            location_log = SpUserLocationLogs.objects.filter(
                user_id=user_id, created_at__icontains=today.strftime("%Y-%m-%d"), status=0).last()
            if location_log:
                diff = today - location_log.created_at
                diff_minutes = (diff.days * 24 * 60) + (diff.seconds/60)
            else:
                diff_minutes = 3
            user_email = email.official_email
            user_name = email.first_name
            if user_tracking:
                latitude = user_tracking.latitude
                longitude = user_tracking.longitude
            date_time = datetime.now()
            message = {
                'subject': f'Employee App Notification - GPS Off ({user_name})',
                'text_content': '',
                'from_email'    : 'balineemilk@outlook.com',
                'recipients'    : ['mohdsubhani33143@gmail.com'
                              ],
                'template': "email-templates/user-notification.html",
                'context': {
                    "user_name":   user_name,
                    "date_time":   date_time,
                    "latitude":   latitude,
                    "longitude":   longitude,
                    "status":   0,
                }
            }

            user_message = {
                'subject': 'Employee App Notification - GPS Off',
                'text_content': '',
                'from_email': 'balineemilk@outlook.com',
                'recipients': [user_email],
                'template': "email-templates/users-notification.html",
                'context': {"user_name":   user_name,
                            "date_time":   date_time,
                            "status":   0,
                            }
            }

        else:
            return Response({'message': 'E-mail Id Not Exist', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
        # location_log = SpUserLocationLogs.objects.filter(user_id=user_id, created_at__icontains=today.strftime("%Y-%m-%d")).last()
        # today = datetime.strptime(today.strftime("%d/%m/%Y %H:%M"), '%d/%m/%Y %H:%M')
        # created_at = datetime.strptime(location_log.created_at.strftime("%d/%m/%Y %H:%M"), '%d/%m/%Y %H:%M')
        if diff_minutes > 2:
            # send_mass_mail([user_message])
            send_mass_mail([message])
            user_location_log = SpUserLocationLogs()
            user_location_log.user_id = user_id
            user_location_log.particular = 'GPS Location is off'
            user_location_log.status = 0
            user_location_log.save()
    context = {}
    context['response_code'] = HTTP_200_OK
    context['message'] = 'Success'
    return Response(context, status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def notificationList(request):

    if request.data.get("page_limit")is None or request.data.get("page_limit") == '':
        return Response({'message': 'Page limit is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)

    page_limit  = int(request.data.get("page_limit"))*30
    offset      = int(page_limit)-30
    page_limit  = 30

    try:
        notification_list = SpNotifications.objects.filter(to_user_id=request.user.id,to_user_type=1).values('id','row_id','model_name', 'heading', 'activity', 'activity_image', 'from_user_id', 'from_user_name', 'icon', 'platform_icon', 'read_status', 'created_at').order_by('-id')[offset:offset+page_limit]
    except SpAddresses.DoesNotExist:
        notification_list = None
    if notification_list:
        for notification in notification_list:
            if notification['activity_image']:
                notification['activity_image'] = baseurl+'/'+notification['activity_image']
            else:
                notification['activity_image'] = ''
            now = datetime.now()    
            notification['created_at'] = timeago.format(str(notification['created_at']), now)        
    else:    
        notification_list = []  

    notification_count = SpNotifications.objects.filter(to_user_id=request.user.id,to_user_type=1).values('id').count()
    if notification_count is not None:
        notification_count = math.ceil(round(notification_count/10, 2))
    else:
        notification_count = 0

    context = {}
    context['message']              = 'Success'
    context['notification_list']    = notification_list
    context['notification_count']   = notification_count
    context['response_code']        = HTTP_200_OK

    return Response(context, status=HTTP_200_OK)



@csrf_exempt
@api_view(["POST"])
def saveUserRegularizationData(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("to_date"):
        is_exists = checkRegularizationAppliedOrNot(request.data.get("user_id"), request.data.get("from_date"), request.data.get("to_date"))
    else:
        is_exists = checkRegularizationAppliedOrNot(request.data.get("user_id"), request.data.get("from_date"), request.data.get("from_date"))    
    if is_exists['status'] == True:
        return Response({'message': 'You have already request on selected dates, kindly select another date', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    else:    
        user                                = SpUserRegularization()
        user.user_id                        = request.data.get("user_id") 
        user.user_name                      = getUserName(request.data.get("user_id"))  
        user.regularization_type_id         = request.data.get("regularization_type_id")
        user.regularization_type_name       = getModelColumnById(SpRegularization, request.data.get("regularization_type_id"), 'regularization_type')
        user.from_date                      = request.data.get("from_date")
        user.from_time                      = request.data.get("from_time")
        user.to_date                        = request.data.get("to_date")
        user.to_time                        = request.data.get("to_time")
        user.mobile_no                      = request.data.get("mobile_no")
        user.place                          = request.data.get("place")
        user.reason_for_leave               = request.data.get("reason_for_leave")
        user.manager                        = request.data.get("manager")
        user.hod                            = request.data.get("hod")
        user.save()

        user_name   = getUserName(request.user.id)
        heading     = 'Regularization request has been generated'
        activity    = 'Regularization request has been generated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
        
        saveActivity('Regularization', 'Regularization request', heading, activity, request.user.id, user_name, 'UserCredentialChange.png', '2', 'app.png')
        sendRegularizationNotificationToUsers(user.id,'', 'add', 0, request.user.id, user_name, 'SpUserRegularization',request.user.role_id)
        
        context = {}
        context['message']      = 'Data has been successfully saved'
        context['response_code'] = HTTP_200_OK
        
        return Response(context, status=HTTP_200_OK)
        

@csrf_exempt
@api_view(["POST"])
def leaveForword(request):    
    if request.data.get("leave_id")is None or request.data.get("leave_id") == '':
        return Response({'message': 'Leave id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("leave_status")is None or request.data.get("leave_status") == '':
        return Response({'message': 'Leave id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
    try:
        leave  = SpUserLeaves.objects.get(id = request.data.get("leave_id"))
        leave.leave_status = request.data.get("leave_status")
        leave.save()
        user_id  = leave.user_id
        user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
        userFirebaseToken = getModelColumnById(SpUsers,user_id,'firebase_token')
        employee_name = getUserName(user_id)

        
        if request.data.get("leave_status") == '2':
            message_title = "Leave Request has been accepted"
            message_body = 'Leave Request has been accepted by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
        else:
            message_title = "Leave Request has been declined"
            message_body = 'Leave Request has been declined by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p')
        notification_image = ""
        if request.data.get("leave_status") == '2':
                msg = 'Handover request has been accepted'
        else:
            msg = 'Handover request has been declined'
        if userFirebaseToken is not None and userFirebaseToken != "" :
            registration_ids = []
            
            registration_ids.append(userFirebaseToken)
            data_message = {}
            data_message['id'] = 1
            data_message['status'] = 'notification'
            data_message['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
            data_message['image'] = notification_image
            send_android_notification(message_title,message_body,data_message,registration_ids)
            #-----------------------------notify android block-------------------------------#
            #-----------------------------save notification block----------------------------#
        saveNotification(leave.id,'SpUserLeaves','Users Management',msg,message_title,message_body,notification_image,request.user.id,user_name,user_id,employee_name,'profile.png',2,'app.png',1,1)
        #-----------------------------save notification block----------------------------#
    except SpUserLeaves.DoesNotExist:
        leave  = None
    context = {}
    if leave:
        if request.data.get("leave_status") == '2':
            context['message']                  = 'Handover request has been accepted'
        else:
            context['message']                  = 'Handover request has been declined'
    else:
         context['message']                  = 'Leave Request has been failed'
    return Response(context, status=HTTP_200_OK) 



@csrf_exempt
@api_view(["POST"])       
def uploadPendingUserLeaveDocument(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("user_leave_id")is None or request.data.get("user_leave_id") == '':
        return Response({'message': 'User Leave Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("document")is None or request.data.get("document") == '':
        return Response({'message': 'Document field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("document_id")is None or request.data.get("document") == '':
        return Response({'message': 'document id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    
    document_id  = request.data.get('document_id')
    document_id = document_id.split(',')
    
    if bool(request.FILES.get('document', False)) == True:
        for i,document in enumerate(request.FILES.getlist('document')):
            # uploaded_attachment = request.FILES['attachment']
            
            storage = FileSystemStorage()
            timestamp = int(time.time())
            attachment_name = document.name
            temp = attachment_name.split('.')
            attachment_name = 'leave-document/leave_attachment_'+str(timestamp)+"."+temp[(len(temp) - 1)]
            
            attachment = storage.save(attachment_name, document)
            attachment = storage.url(attachment)  
            
            doc = SpUserLeaveDocument()  
            doc.user_id = request.data.get("user_id")
            doc.user_leave_id = request.data.get("user_leave_id")
            doc.leave_type_document_id = document_id[i]
            doc.document = attachment
            doc.save()
    context = {}
    context['message']              = 'Document has been uploaded successfully'
    context['response_code']        = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)
        


def sendRegularizationNotificationToUsers(row_id, row_code, permission_slug, sub_module_id, user_id, user_name, model_name, role_id):
    user_wf_level = SpRoleWorkflowPermissions.objects.filter(permission_slug=permission_slug, sub_module_id=sub_module_id, role_id=role_id).values('level_id').distinct().count()
    user_role_wf_permission = SpUserRoleWorkflowPermissions.objects.filter(permission_slug=permission_slug, sub_module_id=sub_module_id, user_id=user_id, status=1).exclude(level_id=1).order_by('level_id')
    
    for wf_permission in user_role_wf_permission:
        user_details = SpUsers.objects.filter(status=1, role_id=wf_permission.workflow_level_role_id)
        if user_wf_level != 1:
            for user_detail in user_details:
                data                    = SpApprovalStatus()
                data.row_id             = row_id
                data.model_name         = model_name
                data.initiated_by_id    = user_id
                data.initiated_by_name  = user_name
                data.user_id            = user_detail.id
                if user_detail.middle_name:
                    data.user_name          = user_detail.first_name+' '+user_detail.middle_name+' '+user_detail.last_name
                else:
                    data.user_name          = user_detail.first_name+' '+user_detail.last_name
                data.role_id            = wf_permission.workflow_level_role_id
                data.sub_module_id      = wf_permission.sub_module_id
                data.permission_id      = wf_permission.permission_id
                data.permission_slug    = wf_permission.permission_slug
                data.level_id           = wf_permission.level_id
                data.level              = wf_permission.level
                data.status             = 0
                data.save()
  
    if user_wf_level == 1:
        model                 = SpUserRegularization.objects.get(id=row_id)   
        model.regularization_status   = 1
        model.save()
    else:
        model                 = SpUserRegularization.objects.get(id=row_id)   
        model.regularization_status   = 1
        model.save()





def saveAttendanceData(id):
    regularizations = SpUserRegularization.objects.get(id=id)
    if regularizations.from_date and regularizations.to_date:
        no_of_days = days_between(str(regularizations.from_date), str(regularizations.to_date))
    else:
        no_of_days = days_between(str(regularizations.from_date), str(regularizations.from_date))  

    for i in range(0, int(no_of_days)):
        start_date      = (datetime.strptime(str(regularizations.from_date), '%Y-%m-%d')+timedelta(days=i)).strftime('%Y-%m-%d')
        end_date        = (datetime.strptime(str(regularizations.from_date), '%Y-%m-%d')+timedelta(days=i)).strftime('%Y-%m-%d')
        start_date_day  = datetime.strptime(str(start_date), '%Y-%m-%d').strftime('%A')
        if start_date_day != 'Sunday':
            if regularizations.regularization_type_id == 1:
                start_date_time = str(start_date)+' '+str(getConfigurationResult('office_start_time'))
                end_date_time   = str(end_date)+' '+str(getConfigurationResult('office_end_time'))
                #start time
                data                        = SpUserAttendance()
                data.user_id                = regularizations.user_id
                data.attendance_date_time   = start_date_time
                data.start_time             = getConfigurationResult('office_start_time')
                data.end_time               = None
                data.dis_ss_id              = regularizations.user_id
                data.latitude               = None
                data.longitude              = None
                
                data.attendance_type        = 1
                data.status                 = 1
                data.save()

                #end time
                data                        = SpUserAttendance()
                data.user_id                = regularizations.user_id
                data.attendance_date_time   = end_date_time
                data.end_time               = getConfigurationResult('office_end_time')
                data.start_time               = None
                data.dis_ss_id              = regularizations.user_id
                data.latitude               = None
                data.longitude              = None
                
                data.attendance_type    = 1
                data.status             = 1
                data.save()
            else:
                start_time = str(regularizations.from_time)+':00'
                start_date_time = str(start_date)+' '+str(start_time)
                #start time
                data                        = SpUserAttendance()
                data.user_id                = regularizations.user_id
                data.attendance_date_time   = start_date_time
                data.start_time             = start_time
                data.end_time               = None
                data.dis_ss_id              = regularizations.user_id
                data.latitude               = None
                data.longitude              = None
                
                data.attendance_type    = 1
                data.status             = 1
                data.save()
         
    return True  



def date_diff_in_seconds(dt2, dt1):
  timedelta = dt2 - dt1
  return timedelta.days * 24 * 3600 + timedelta.seconds

def dhms_from_seconds(seconds):
	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)
    #return (hours, minutes, seconds)
	return (hours)

#user day out
@api_view(["GET"])
@permission_classes((AllowAny,))
def userDayOut(request):
    today   = date.today()
    context = {}
    
    user_attendance = SpUserAttendance.objects.filter(attendance_date_time__icontains=today.strftime("%Y-%m-%d")).order_by('user_id').values('user_id').distinct()
    for attendance in user_attendance:
        user_attendance = SpUserAttendance.objects.filter(attendance_date_time__icontains=today.strftime("%Y-%m-%d"), user_id=attendance['user_id']).order_by('-id').first()
        if user_attendance.start_time is not None and user_attendance.end_time is None:
            start_time      = user_attendance.created_at
            start_time      = datetime.strptime(str(start_time), '%Y-%m-%d %H:%M:%S')
            end_time        = datetime.now()
            
            second = date_diff_in_seconds(end_time,start_time)
            diff   = dhms_from_seconds(second)
            if diff >= 8.5:
                now  = datetime.now().strftime('%H:%M:%S')
                data                        = SpUserAttendance()
                data.user_id                = attendance['user_id']
                data.attendance_date_time   = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data.start_time             = None
                data.end_time               = now
                data.dis_ss_id              = None
                data.attendance_type        = 3
                data.latitude               = None
                data.longitude              = None
                data.status                 = 1
                data.save()

                AuthtokenToken.objects.filter(user_id=attendance['user_id']).delete()

    context['response_code']    = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)


        