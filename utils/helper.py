import os
import calendar
from apps.src.models.helper_model import Configuration
from apps.src.models.models import *
from django.template.loader import get_template
from django.conf import settings
from sanstha.settings import EMAIL_HOST_USER
from django.core.mail import EmailMessage
from datetime import datetime,timedelta
import requests
import urllib
import math, random 
from django.db.models import Sum
import re
from random import randint
# from pyfcm import FCMNotification
import numpy as np
import cv2
import base64

import datetime as dt



Path = settings.MEDIA_ROOT




def getUserRole(id):
    result =  SpUsers.objects.get(id=id)
    if result.user_type == 2:
        if result.is_distributor == 1:
            return 'Distributor'
        else:
            return 'SuperStockist'
    elif result.user_type == 1: 
        return 'Employee'       
    else:
        if result.is_distributor == 1:
            return 'Distributor'
        else:
            return 'Retailer'
          
def clean_data(data):
    data = data.strip()
    return data

def getConfigurationResult(column):
    result =  Configuration.objects.values(column).filter()[0][column]
    return result

def getModelColumnById(Model, id,column):
    result =  Model.objects.values(column).filter(pk=id)[0][column]
    return result

def getUserName(id):
    if SpUsers.objects.filter(id=id):
        user = SpUsers.objects.filter(id=id).values('first_name','middle_name','last_name')
        user_name = user[0]['first_name']
        if user[0]['middle_name'] is not None:
            user_name += " "+user[0]['middle_name']
        if user[0]['last_name'] is not None:
            user_name += " "+user[0]['last_name']
        return user_name
    else:
        return "User not found"

def getStudentName(id):
    if TblStudents.objects.filter(id=id):
        user = TblStudents.objects.filter(id=id).values('first_name','middle_name','last_name').first()
        user_name = user['first_name'].strip()
        if user['middle_name']:
            if user['middle_name'].strip():
                user_name += " "+user['middle_name'].strip()
        if user['last_name']:
            user_name += " "+user['last_name'].strip()
        return user_name
    else:
        return "User not found"
        
def getModelColumnByColumnId(Model,column_name,column_value,column):
    filters = {
        column_name: column_value
    }
    result =  Model.objects.values(column).filter(**filters)[0][column]
    return result

def deleteMediaFile(path):
    path = path.replace('/media', '') 
    path = Path + path
    if os.path.isfile(path):
       os.remove(path)

def sendEmail(request, template, context, subject, recipient):
    subject = subject
    message = get_template(template).render(context)
    msg = EmailMessage(
        subject,
        message,
        EMAIL_HOST_USER,
        [recipient],
    )
    msg.content_subtype = "html"  
    msg.send()
    print("Mail successfully sent")

def weeks_in_month(year, month):
    return len(calendar.monthcalendar(year, month))

def get_week_day(current_year, current_month):
    year, week, dow = datetime.today().isocalendar()
    result = [datetime.strptime(str(year) + "-" + str(week-1) + "-" + str(x), "%Y-%W-%w").day for x in range(0,7)]
    
    week_days = []
    for id, val in enumerate(result):
        if id != 0:
            if current_month > 9:
                if val > 9:
                    week_date = str(current_year)+'-'+str(current_month)+'-'+str(val)
                else:
                    week_date = str(current_year)+'-'+str(current_month)+'-0'+str(val)    
            else:
                week_date = str(current_year)+'-0'+str(current_month)+'-'+str(val)  
            day = datetime.strptime(str(week_date), '%Y-%m-%d').strftime('%a') 
                  
            week_days.append(day)
        else:
            val = result[1]-1
            if current_month > 9:
                if val > 9:
                    week_date = str(current_year)+'-'+str(current_month)+'-'+str(val)
                else:
                    week_date = str(current_year)+'-'+str(current_month)+'-0'+str(val) 
            else:
                week_date = str(current_year)+'-0'+str(current_month)+'-'+str(val) 
            day = datetime.strptime(str(week_date), '%Y-%m-%d').strftime('%a')  
                  
            week_days.append(day)
    return week_days

def get_week_date(current_year, current_month):
    year, week, dow = datetime.today().isocalendar()
    result = [datetime.strptime(str(year) + "-" + str(week-1) + "-" + str(x), "%Y-%W-%w").day for x in range(0,7)]
    
    week_dates = []
    for id, val in enumerate(result):
        if id != 0:
            if current_month > 9:
                if val > 9:
                    week_date = str(current_year)+'-'+str(current_month)+'-'+str(val)
                else:
                    week_date = str(current_year)+'-'+str(current_month)+'-0'+str(val)    
            else:
                week_date = str(current_year)+'-0'+str(current_month)+'-'+str(val)
                  
            week_dates.append(week_date)
        else:
            val = result[1]-1
            if current_month > 9:
                if val > 9:
                    week_date = str(current_year)+'-'+str(current_month)+'-'+str(val)
                else:
                    week_date = str(current_year)+'-'+str(current_month)+'-0'+str(val) 
            else:
                week_date = str(current_year)+'-0'+str(current_month)+'-'+str(val) 
                  
            week_dates.append(week_date)
    return week_dates

def saveActivity(module,sub_module,heading,activity_msg,user_id,user_name,icon,platform,platform_icon):
    activity = SpActivityLogs()
    activity.module = module
    activity.sub_module = sub_module
    activity.heading = heading
    activity.activity = activity_msg
    activity.user_id = user_id
    activity.user_name = user_name
    if icon:
        activity.icon = icon
    else:
       activity.icon = 'add.png'     
    activity.platform = platform
    if platform_icon:
        activity.platform_icon = platform_icon
    else:
        activity.platform_icon = 'web.png'    
    activity.save()

def sendNotificationToUsers(row_id, row_code, permission_slug, sub_module_id, user_id, user_name, model_name, role_id):
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

                #save notification
                if user_wf_level == 3 and wf_permission.level_id == 2:
                    notification                        = SpUserNotifications()
                    notification.row_id                 = row_id
                    notification.user_id                = user_detail.id
                    notification.model_name             = model_name
                    notification.notification           = 'Leave policy '+wf_permission.level+' Request has been sent.'
                    notification.is_read                = 0
                    notification.created_by_user_id     = user_id
                    notification.created_by_user_name   = user_name
                    notification.save()
                    if model_name == 'SpLeavePolicies':
                        model                               = SpLeavePolicies.objects.get(id=row_id)   
                        model.policy_status                  = wf_permission.level_id-1
                    else:
                        model                               = SpHolidays.objects.get(id=row_id)   
                        model.holiday_status                  = wf_permission.level_id-1
                    model.save()
                elif user_wf_level == 2 and wf_permission.level_id == 3:
                    notification                        = SpUserNotifications()
                    notification.row_id                 = row_id
                    notification.user_id                = user_detail.id
                    notification.model_name             = model_name
                    notification.notification           = 'Leave policy '+wf_permission.level+' Request has been sent.'
                    notification.is_read                = 0
                    notification.created_by_user_id     = user_id
                    notification.created_by_user_name   = user_name
                    notification.save()
                    if model_name == 'SpLeavePolicies':                                   
                        model                               = SpLeavePolicies.objects.get(id=row_id)   
                        model.policy_status                  = wf_permission.level_id-1
                    else:
                        model                               = SpHolidays.objects.get(id=row_id)   
                        model.holiday_status                  = wf_permission.level_id-1
                    model.save()  

    if user_wf_level == 1:
        if model_name == 'SpLeavePolicies':
            model                               = SpLeavePolicyDetails.objects.get(id=row_id)   
            model.policy_status                  = 3
        else:
            model                               = SpHolidays.objects.get(id=row_id)   
            model.holiday_status                  = 3
        model.save()  

def numberOfDays(y, m):
      leap = 0
      if y% 400 == 0:
         leap = 1
      elif y % 100 == 0:
         leap = 0
      elif y% 4 == 0:
         leap = 1
      if m==2:
         return 28 + leap
      list = [1,3,5,7,8,10,12]
      if m in list:
         return 31
      return 30

def sendSMS(sender_id,mobile,message):
    url = 'http://sms.bulksmsserviceproviders.com/api/send_http.php'
    postdata = {
        "authkey": "1c61258322ecbac5b5d1d3c950ef8d06",
        "sender": sender_id,
        "mobiles": mobile,
        "unicode": 1,
        "message": message,
        "route": 'B'
        }
        
    response = requests.post(url, data=postdata)
    return response.status_code

def generateOTPs() : 
    # Declare a digits variable   
    # which stores all digits  
    digits = "0123456789"
    OTP = "" 
  
    # length of password can be chaged 
    # by changing value in range 
    for i in range(4) : 
        OTP += digits[math.floor(random.random() * 10)] 
  
    return OTP


def isValidEmail(email):
    regex = '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+.[A-Za-z]{2,4}$'
    if(re.search(regex,email)):
        return True  
    else:  
        return False  

def generateOTP(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def getTinyUrl(long_url):
    url = "http://tinyurl.com/api-create.php"
    try:
        url = url + "?" \
            + urllib.parse.urlencode({"url": long_url})
        res = requests.get(url)
        return res.text
    except Exception as e:
        raise

def sendWebPushNotification(message_title,message_body,registration_ids):
    api_key = 'AAAAQXQhNB8:APA91bHi3uR-nCBxMZByM1Uxz5goUYjJcnLSVEuK2LGOd0_Q8fpPpE5BSo2I8GhIb_qybtcbPiPrtL4kAWaTV8LB7nzc-4X4qexDvKf83emPz7xJwErPlJHfThGcdiRvV4S7H3p3iDOG'
    push_service = FCMNotification(api_key=api_key)
    result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title, message_body=message_body)
    return result

def days_in_months(year, month):

    c = calendar.Calendar()
    month_array = []
    for date in c.itermonthdates(year, month):
        if int(month) > 9:
            months = month
        else:
            months = '0'+str(month)

        date_format = str(date).split('-')
        if date_format[0] == str(year) and date_format[1] == str(months):
            rt = datetime.strptime(str(date), '%Y-%m-%d').strftime('%d/%m/%Y')
            month_array.append(datetime.strptime(str(date), '%Y-%m-%d').strftime('%d/%m/%Y'))
    return month_array

        
def generateVisitOTP() : 
    # Declare a digits variable   
    # which stores all digits  
    digits = "0123456789"
    OTP = "" 
  
    # length of password can be chaged 
    # by changing value in range 
    for i in range(4) : 
        OTP += digits[math.floor(random.random() * 10)] 
  
    return OTP
    
def days_between_dates(from_date, to_date):
    if to_date < from_date:
        delta = from_date - to_date
        return [(to_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]
    else:
        delta = to_date -  from_date
        return [(from_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]

def weekday_count(start, end):
    start_date  = start
    end_date    = end
    week        = {}
    for i in range((end_date - start_date).days):
        day       = calendar.day_name[(start_date + timedelta(days=i+1)).weekday()]
        week[day] = week[day] + 1 if day in week else 1
    return week
    
def readb64(uri):
    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def generateEntranceOTP() : 
    # Declare a digits variable   
    # which stores all digits  
    digits = "0123456789"
    OTP = "" 
  
    # length of password can be chaged 
    # by changing value in range 
    for i in range(4) : 
        OTP += digits[math.floor(random.random() * 10)] 
  
    return OTP

# send android push notifications

def send_android_notification(message_title, message_body, data_message,registration_ids):

    firebase_server_key = getConfigurationResult('firebase_server_key')

    if firebase_server_key is not None and firebase_server_key != "":

        # push_service = FCMNotification(api_key=firebase_server_key)

        # result =  push_service.notify_multiple_devices(registration_ids=registration_ids,message_title=message_title, message_body=message_body, data_message=data_message)

        return True      
        




# New Code for employee

def saveNotification(row_id,model_name,module,sub_module,heading,notification_msg,notification_image,from_user_id,from_user_name,to_user_id,to_user_name,icon,platform,platform_icon,notification_type,to_user_type=None):

    notification = SpNotifications()

    if row_id is not None:

        notification.row_id = row_id

    else:

       notification.row_id = None  



    if model_name is not None:

        notification.model_name = model_name

    else:

       notification.model_name = None

    if to_user_type is not None:
        notification.to_user_type = to_user_type
    else:
        notification.to_user_type = None
    



    notification.module = module

    notification.sub_module = sub_module

    notification.heading = heading

    notification.activity = notification_msg



    if notification_image is not None and notification_image != "" :

        notification.activity_image = notification_image

    else:

       notification.activity_image = None



    notification.from_user_id = from_user_id

    notification.from_user_name = from_user_name

    notification.to_user_id = to_user_id

    notification.to_user_name = to_user_name



    if icon is not None:

        notification.icon = icon

    else:

       notification.icon = 'add.png'  



    notification.platform = platform

    if platform_icon is not None:

        notification.platform_icon = platform_icon

    else:

        notification.platform_icon = 'web.png'

    notification.notification_type = notification_type



        

    notification.save()


def days_cur_month(date = '1', month = '', year = ''):
    _month = int(month)
    _year = int(year)
    
    if _month == 12:
        _last_days = (dt.date(_year+1, int(_month)-11, 1) - dt.date(_year, _month, 1)).days
    else:
        _last_days = (dt.date(_year, int(_month)+1, 1) - dt.date(_year, _month, 1)).days

    month_first_date = dt.datetime(year=_year, month=_month, day=1)
    month_last_date = dt.datetime(year=_year, month=_month, day=_last_days)
    delta = month_last_date - month_first_date
    return [(month_first_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]  

def get_total_no_of_weekoff(user_id, week_date):
    leave_date_day      = datetime.strptime(str(week_date), '%Y-%m-%d').strftime('%A')
    user_week_off_day   = SpBasicDetails.objects.filter(user_id=user_id).values('week_of_day').first()
    user_week_off_day  = user_week_off_day['week_of_day'].split(',')
 
    if str(leave_date_day) in user_week_off_day:
        return 1
    else:
        return 0

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return int(abs((d2 - d1).days))+1

# def get_user_leave(user_id,week_date):
    
#     try:
#         user_leave_obj = TblClUserLeaves.objects.raw('''SELECT * FROM tbl_cl_user_leaves where %s BETWEEN DATE(leave_from_date) AND DATE(leave_to_date) and leave_status=3 and user_id=%s order by id desc LIMIT 1 ''',[week_date, user_id])
#     except TblClUserLeaves.DoesNotExist:
#         user_leave_obj = None
   
#     if user_leave_obj:
#         user_leave_obj = user_leave_obj[0]
#         if TblClUserLeaves.objects.filter(user_id=user_id,leave_status=3, leave_from_date__icontains=week_date, is_first_half_day=1).exists():
#             return False
#         elif TblClUserLeaves.objects.filter(user_id=user_id,leave_status=3, leave_to_date__icontains=week_date, is_last_half_day=1).exists():    
#             return False
#         else:
#             if str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_first_half_day == 1:
#                 return False
#             elif str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_last_half_day == 1:
#                 return False    
#             else:
#                 return user_leave_obj 
#     else:
#         return False

# def get_user_month_leave_count(user_id,week_date):
#     try:
#         user_leave_obj = TblClUserLeaves.objects.raw('''SELECT * FROM tbl_cl_user_leaves where %s BETWEEN DATE(leave_from_date) AND DATE(leave_to_date) and leave_status=3 and user_id=%s order by id desc LIMIT 1 ''',[week_date, user_id])
#     except TblClUserLeaves.DoesNotExist:
#         user_leave_obj = None
   
#     if user_leave_obj:
#         user_leave_obj = user_leave_obj[0]
#         leave_date_day = datetime.strptime(str(week_date), '%Y-%m-%d').strftime('%A')
#         user_week_off_day = SpBasicDetails.objects.filter(user_id=user_leave_obj.user_id).values('week_of_day').first()
#         if str(user_week_off_day['week_of_day']) == str(leave_date_day):
#             return 0
#         elif TblClUserLeaves.objects.filter(user_id=user_id,leave_status=3, leave_from_date__icontains=week_date, is_first_half_day=1).exists():
#             return 0.5
#         elif TblClUserLeaves.objects.filter(user_id=user_id,leave_status=3, leave_to_date__icontains=week_date, is_last_half_day=1).exists():    
#             return 0.5
#         else:
#             if str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_first_half_day == 1:
#                 return 0.5
#             elif str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_last_half_day == 1:
#                 return 0.5  
#             else:
#                 return 1
#     else:
#         return 0

# def checkLeaveAppliedOrNot(user_id, leave_start_date, leave_end_date):
#     leave_data = {}
#     try:
#         if str(leave_start_date) == str(leave_end_date):
#             user_leave_objs = TblClUserLeaves.objects.filter(user_id=user_id,leave_from_date__icontains=leave_start_date).exclude(leave_status=4)
#         else:    
#             user_leave_objs = TblClUserLeaves.objects.raw('''SELECT * FROM sp_user_leaves where (leave_from_date BETWEEN %s AND %s OR leave_to_date BETWEEN %s AND %s) and user_id=%s and leave_status!=%s order by id desc ''',[leave_start_date, leave_end_date, leave_start_date, leave_end_date, user_id, '4'])
#     except TblClUserLeaves.DoesNotExist:
#         user_leave_objs = None
     
#     if user_leave_objs:
#         applied_leave_date_list = []
#         for user_leave_obj in user_leave_objs:    
            
#             if str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date):
#                 leave_date = datetime.strptime(str(user_leave_obj.leave_from_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
#                 applied_leave_date_list.append(leave_date)
#             else:
#                 leave_from_date = datetime.strptime(str(user_leave_obj.leave_from_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
#                 leave_to_date   = datetime.strptime(str(user_leave_obj.leave_to_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')

#                 no_of_days = days_between(leave_from_date, leave_to_date)
#                 for i in range(0, int(no_of_days)):
#                     leave_date = (datetime.strptime(leave_from_date, '%Y-%m-%d')+timedelta(days=i)).strftime('%Y-%m-%d')
#                     applied_leave_date_list.append(leave_date)

#         leave_date_list = []
#         if str(leave_start_date) == str(leave_end_date):
#             leave_date_list.append(leave_start_date)
#         else:
#             no_of_days = days_between(leave_start_date, leave_end_date)
#             for i in range(0, int(no_of_days)):
#                 leave_date = (datetime.strptime(leave_start_date, '%Y-%m-%d')+timedelta(days=i)).strftime('%Y-%m-%d')
#                 leave_date_list.append(leave_date)
        
#         matched_date = [x for x in applied_leave_date_list if x in leave_date_list]
#         if len(matched_date)>0:
#           leave_data['status'] = True     
#         else:
#             leave_data['status'] = False
#     else:
#         leave_data['status'] = False          
#     return leave_data             

# def checkAttendanceMarkedOrNot(user_id, leave_start_date, leave_end_date, today_date):
#     leave_date_list = []
#     if str(leave_start_date) == str(leave_end_date):
#         if str(leave_start_date) == str(today_date) and TblEmployeeAttendance.objects.filter(start_time__isnull=False, user_id=user_id, attendance_date_time__icontains=leave_start_date).exists():
#             leave_date_list.append(leave_start_date)
#     else:
#         no_of_days = days_between(leave_start_date, leave_end_date)
#         for i in range(0, int(no_of_days)):
#             leave_date = (datetime.strptime(leave_start_date, '%Y-%m-%d')+timedelta(days=i)).strftime('%Y-%m-%d')
#             if str(leave_date) == str(today_date) and TblEmployeeAttendance.objects.filter(start_time__isnull=False, user_id=user_id, attendance_date_time__icontains=leave_date).exists():
#                 leave_date_list.append(leave_date)
#     if len(leave_date_list)>0:        
#         return True
#     else:
#         return False
def get_user_leave_count(leave_id):
    try:
        user_leave_obj = SpUserLeaves.objects.get(id=leave_id,leave_status=3)
    except SpUserLeaves.DoesNotExist:
        user_leave_obj = None
    leave_date_list = []
    if str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date):
        leave_date = datetime.strptime(str(user_leave_obj.leave_from_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        leave_date_list.append(leave_date)
    else:
        leave_from_date = datetime.strptime(str(user_leave_obj.leave_from_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        leave_to_date   = datetime.strptime(str(user_leave_obj.leave_to_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        no_of_days = days_between(leave_from_date, leave_to_date)
        for i in range(0, int(no_of_days)):
            leave_date = (datetime.strptime(leave_from_date, '%Y-%m-%d')+timedelta(days=i)).strftime('%Y-%m-%d')
            leave_date_list.append(leave_date)
    
    total_leave_count_list = []
    if leave_date_list:
        for leave_date in leave_date_list:
            leave_date_day = datetime.strptime(str(leave_date), '%Y-%m-%d').strftime('%A')
            user_week_off_day = SpBasicDetails.objects.filter(user_id=user_leave_obj.user_id).values('week_of_day').first()
            if str(user_week_off_day['week_of_day']) == str(leave_date_day):
                total_leave_count_list.append(int(0))
            elif SpUserLeaves.objects.filter(id=leave_id,leave_status=3, leave_from_date__icontains=leave_date, is_first_half_day=1).exists():
                total_leave_count_list.append(float(0.5))
            elif SpUserLeaves.objects.filter(id=leave_id,leave_status=3, leave_to_date__icontains=leave_date, is_last_half_day=1).exists():    
                total_leave_count_list.append(float(0.5))
            else:
                if str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_first_half_day == 1:
                    total_leave_count_list.append(float(0.5))
                elif str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_last_half_day == 1:
                    total_leave_count_list.append(float(0.5))   
                else:
                    total_leave_count_list.append(int(1))
         
    return sum(total_leave_count_list)

def sendFocNotificationToUsers(model_id, code, permission_slug, sub_module_id, user_id, user_name, model_name, role_id):
    user_wf_level           = SpRoleWorkflowPermissions.objects.filter(permission_slug=permission_slug, 
    sub_module_id=sub_module_id).values('level_id').distinct().count()
    
    user_role_wf_permission = SpUserRoleWorkflowPermissions.objects.filter(permission_slug=permission_slug, sub_module_id=sub_module_id, status=1).exclude(level_id=1).order_by('level_id')
    for wf_permission in user_role_wf_permission:
        user_detail = SpUsers.objects.get(id=wf_permission.user_id)
        if user_wf_level != 1:
            data                    = SpApprovalStatus()
            data.row_id             = model_id
            data.model_name         = model_name
            data.initiated_by_id    = user_id
            data.initiated_by_name  = user_name
            data.user_id            = wf_permission.user_id
            data.user_name          = str(user_detail.first_name)+' '+str(user_detail.middle_name)+' '+str(user_detail.last_name)
            data.role_id            = wf_permission.workflow_level_role_id
            data.sub_module_id      = wf_permission.sub_module_id
            data.permission_id      = wf_permission.permission_id
            data.permission_slug    = wf_permission.permission_slug
            data.level_id           = wf_permission.level_id
            data.level              = wf_permission.level
            data.status             = 0
            data.save()
            
            #save notification
            if user_wf_level == 3 and wf_permission.level_id == 2:
                if model_name == 'TblClUserLeaves':
                    data_model                               = TblClUserLeaves.objects.get(id=model_id)    
                    data_model.leave_status                  = wf_permission.level_id-1
                else:
                    data_model                               = SpFocRequests.objects.get(id=model_id)    
                    data_model.foc_status                    = wf_permission.level_id-1
                
                data_model.save()
                

            elif user_wf_level == 2 and wf_permission.level_id == 3:
                if model_name == 'SpUserLeaves':
                    data_model                               = TblClUserLeaves.objects.get(id=model_id)    
                    data_model.leave_status                  = wf_permission.level_id-1
                else:
                    data_model                               = SpFocRequests.objects.get(id=model_id)    
                    data_model.foc_status                    = wf_permission.level_id-1       
                
                data_model.save()
            
            if model_name == 'SpUserLeaves':
                #-----------------------------notify android block-------------------------------#
                userFirebaseToken = getModelColumnById(SpUsers,wf_permission.user_id,'firebase_token')
                employee_name = getUserName(wf_permission.user_id)

                message_title = "Leave initiated"
                message_body = "A leave has been applied by "+user_name
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
                saveNotification(model_id,'SpUserLeaves','Users Management','Leave applied',message_title,message_body,notification_image,user_id,user_name,wf_permission.user_id,employee_name,'profile.png',2,'app.png',1,1)
                #-----------------------------save notification block----------------------------#
                
            else:
                #-----------------------------notify android block-------------------------------#
                userFirebaseToken = getModelColumnById(SpUsers,wf_permission.user_id,'firebase_token')
                employee_name = getUserName(wf_permission.user_id)

                message_title = "Sample Request initiated"
                message_body = "A Sample Request has been initiated by "+user_name
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
                saveNotification(model_id,'SpFocRequests','Order Management','Order initiated',message_title,message_body,notification_image,user_id,user_name,wf_permission.user_id,employee_name,'profile.png',2,'app.png',1,1)
                #-----------------------------save notification block----------------------------#


    if user_wf_level == 1:
        if model_name == 'SpUserLeaves':
            data_model                             = TblClUserLeaves.objects.get(id=model_id)
            data_model.leave_status                = 3 
        else:
            data_model                             = TblClUserLeaves.objects.get(id=model_id) 
            data_model.foc_status                  = 3
        data_model.save()

# def isHalfDay(user_id, week_date):
#     try:
#         user_leave_obj = TblClUserLeaves.objects.raw('''SELECT * FROM tbl_cl_user_leaves where %s BETWEEN DATE(leave_from_date) AND DATE(leave_to_date) and leave_status=3 and user_id=%s order by id desc LIMIT 1 ''',[week_date, user_id])
#     except TblClUserLeaves.DoesNotExist:
#         user_leave_obj = None
   
#     if user_leave_obj:
#         user_leave_obj = user_leave_obj[0]
#         if TblClUserLeaves.objects.filter(user_id=user_id,leave_status=3, leave_from_date__icontains=week_date, is_first_half_day=1).exists():
#             return True
#         elif TblClUserLeaves.objects.filter(user_id=user_id,leave_status=3, leave_to_date__icontains=week_date, is_last_half_day=1).exists():    
#             return True
#         else:
#             if str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_first_half_day == 1:
#                 return True
#             elif str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_last_half_day == 1:
#                 return True
#             else:
#                 return False     
#     else:
#         return False

# def checkDateIsFutureDate(week_date):
#     date_format = "%Y-%m-%d"
#     start = datetime.strptime(week_date, date_format)
#     now = datetime.now()

#     if start > now:
#         return True
#     else:
#         return False


# Code Added By Sushil

def checkAttendanceMarkedOrNot(user_id, leave_start_date, leave_end_date, today_date):
    leave_date_list = []
    if str(leave_start_date) == str(leave_end_date):
        if str(leave_start_date) == str(today_date) and SpUserAttendance.objects.filter(start_time__isnull=False, user_id=user_id, attendance_date_time__icontains=leave_start_date).exists():
            leave_date_list.append(leave_start_date)
    else:
        no_of_days = days_between(leave_start_date, leave_end_date)
        for i in range(0, int(no_of_days)):
            leave_date = (datetime.strptime(leave_start_date, '%Y-%m-%d')+timedelta(days=i)).strftime('%Y-%m-%d')
            if str(leave_date) == str(today_date) and SpUserAttendance.objects.filter(start_time__isnull=False, user_id=user_id, attendance_date_time__icontains=leave_date).exists():
                leave_date_list.append(leave_date)
    if len(leave_date_list)>0:        
        return True
    else:
        return False


def checkLeaveAppliedOrNot(user_id, leave_start_date, leave_end_date):
    leave_data = {}
    try:
        if str(leave_start_date) == str(leave_end_date):
            user_leave_objs = SpUserLeaves.objects.filter(user_id=user_id,leave_from_date__icontains=leave_start_date).exclude(leave_status=4)
        else:    
            user_leave_objs = SpUserLeaves.objects.raw('''SELECT * FROM sp_user_leaves where (leave_from_date BETWEEN %s AND %s OR leave_to_date BETWEEN %s AND %s) and user_id=%s and leave_status!=%s order by id desc ''',[leave_start_date, leave_end_date, leave_start_date, leave_end_date, user_id, '4'])
    except SpUserLeaves.DoesNotExist:
        user_leave_objs = None
     
    if user_leave_objs:
        applied_leave_date_list = []
        for user_leave_obj in user_leave_objs:    
            
            if str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date):
                leave_date = datetime.strptime(str(user_leave_obj.leave_from_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                applied_leave_date_list.append(leave_date)
            else:
                leave_from_date = datetime.strptime(str(user_leave_obj.leave_from_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                leave_to_date   = datetime.strptime(str(user_leave_obj.leave_to_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')

                no_of_days = days_between(leave_from_date, leave_to_date)
                for i in range(0, int(no_of_days)):
                    leave_date = (datetime.strptime(leave_from_date, '%Y-%m-%d')+timedelta(days=i)).strftime('%Y-%m-%d')
                    applied_leave_date_list.append(leave_date)

        leave_date_list = []
        if str(leave_start_date) == str(leave_end_date):
            leave_date_list.append(leave_start_date)
        else:
            no_of_days = days_between(leave_start_date, leave_end_date)
            for i in range(0, int(no_of_days)):
                leave_date = (datetime.strptime(leave_start_date, '%Y-%m-%d')+timedelta(days=i)).strftime('%Y-%m-%d')
                leave_date_list.append(leave_date)
        
        matched_date = [x for x in applied_leave_date_list if x in leave_date_list]
        if len(matched_date)>0:
           leave_data['status'] = True     
        else:
            leave_data['status'] = False
    else:
        leave_data['status'] = False          
    return leave_data             

def checkDateIsFutureDate(week_date):
    date_format = "%Y-%m-%d"
    start = datetime.strptime(week_date, date_format)
    now = datetime.now()

    if start > now:
        return True
    else:
        return False

def isHalfDay(user_id, week_date):
    try:
        user_leave_obj = SpUserLeaves.objects.raw('''SELECT * FROM sp_user_leaves where %s BETWEEN DATE(leave_from_date) AND DATE(leave_to_date) and leave_status=3 and user_id=%s order by id desc LIMIT 1 ''',[week_date, user_id])
    except SpUserLeaves.DoesNotExist:
        user_leave_obj = None
   
    if user_leave_obj:
        user_leave_obj = user_leave_obj[0]
        if SpUserLeaves.objects.filter(user_id=user_id,leave_status=3, leave_from_date__icontains=week_date, is_first_half_day=1).exists():
            return True
        elif SpUserLeaves.objects.filter(user_id=user_id,leave_status=3, leave_to_date__icontains=week_date, is_last_half_day=1).exists():    
            return True
        else:
            if str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_first_half_day == 1:
                return True
            elif str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_last_half_day == 1:
                return True
            else:
                return False     
    else:
        return False

# def get_total_no_of_weekoff(user_id, week_date):
#     leave_date_day      = datetime.strptime(str(week_date), '%Y-%m-%d').strftime('%A')
#     user_week_off_day   = SpBasicDetails.objects.filter(user_id=user_id).values('week_of_day').first()
 
#     if str(user_week_off_day['week_of_day']) == str(leave_date_day):
#         return 1
#     else:
#         return 0

def get_user_month_leave_count(user_id,week_date):
    try:
        user_leave_obj = SpUserLeaves.objects.raw('''SELECT * FROM sp_user_leaves where %s BETWEEN DATE(leave_from_date) AND DATE(leave_to_date) and leave_status=3 and user_id=%s order by id desc LIMIT 1 ''',[week_date, user_id])
    except SpUserLeaves.DoesNotExist:
        user_leave_obj = None
   
    if user_leave_obj:
        user_leave_obj = user_leave_obj[0]
        leave_date_day = datetime.strptime(str(week_date), '%Y-%m-%d').strftime('%A')
        user_week_off_day = SpBasicDetails.objects.filter(user_id=user_leave_obj.user_id).values('week_of_day').first()
        if str(user_week_off_day['week_of_day']) == str(leave_date_day):
            return 0
        elif SpUserLeaves.objects.filter(user_id=user_id,leave_status=3, leave_from_date__icontains=week_date, is_first_half_day=1).exists():
            return 0.5
        elif SpUserLeaves.objects.filter(user_id=user_id,leave_status=3, leave_to_date__icontains=week_date, is_last_half_day=1).exists():    
            return 0.5
        else:
            if str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_first_half_day == 1:
                return 0.5
            elif str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_last_half_day == 1:
                return 0.5  
            else:
                return 1
    else:
        return 0

def get_user_leave(user_id,week_date):
    
    try:
        user_leave_obj = SpUserLeaves.objects.raw('''SELECT * FROM sp_user_leaves where %s BETWEEN DATE(leave_from_date) AND DATE(leave_to_date) and leave_status=3 and user_id=%s order by id desc LIMIT 1 ''',[week_date, user_id])
    except SpUserLeaves.DoesNotExist:
        user_leave_obj = None
   
    if user_leave_obj:
        user_leave_obj = user_leave_obj[0]
        if SpUserLeaves.objects.filter(user_id=user_id,leave_status=3, leave_from_date__icontains=week_date, is_first_half_day=1).exists():
            return False
        elif SpUserLeaves.objects.filter(user_id=user_id,leave_status=3, leave_to_date__icontains=week_date, is_last_half_day=1).exists():    
            return False
        else:
            if str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_first_half_day == 1:
                return False
            elif str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_last_half_day == 1:
                return False    
            else:
                return user_leave_obj 
    else:
        return False

def get_user_leave_count(leave_id):
    try:
        user_leave_obj = SpUserLeaves.objects.get(id=leave_id,leave_status=3)
    except SpUserLeaves.DoesNotExist:
        user_leave_obj = None
    leave_date_list = []
    if str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date):
        leave_date = datetime.strptime(str(user_leave_obj.leave_from_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        leave_date_list.append(leave_date)
    else:
        leave_from_date = datetime.strptime(str(user_leave_obj.leave_from_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        leave_to_date   = datetime.strptime(str(user_leave_obj.leave_to_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        no_of_days = days_between(leave_from_date, leave_to_date)
        for i in range(0, int(no_of_days)):
            leave_date = (datetime.strptime(leave_from_date, '%Y-%m-%d')+timedelta(days=i)).strftime('%Y-%m-%d')
            leave_date_list.append(leave_date)
    
    total_leave_count_list = []
    if leave_date_list:
        for leave_date in leave_date_list:
            leave_date_day = datetime.strptime(str(leave_date), '%Y-%m-%d').strftime('%A')
            user_week_off_day = SpBasicDetails.objects.filter(user_id=user_leave_obj.user_id).values('week_of_day').first()
            if str(user_week_off_day['week_of_day']) == str(leave_date_day):
                total_leave_count_list.append(int(0))
            elif SpUserLeaves.objects.filter(id=leave_id,leave_status=3, leave_from_date__icontains=leave_date, is_first_half_day=1).exists():
                total_leave_count_list.append(float(0.5))
            elif SpUserLeaves.objects.filter(id=leave_id,leave_status=3, leave_to_date__icontains=leave_date, is_last_half_day=1).exists():    
                total_leave_count_list.append(float(0.5))
            else:
                if str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_first_half_day == 1:
                    total_leave_count_list.append(float(0.5))
                elif str(user_leave_obj.leave_from_date) == str(user_leave_obj.leave_to_date) and user_leave_obj.is_last_half_day == 1:
                    total_leave_count_list.append(float(0.5))   
                else:
                    total_leave_count_list.append(int(1))
         
    return sum(total_leave_count_list)




def checkRegularizationAppliedOrNot(user_id, regularization_start_date, regularization_end_date):
    regularization_data = {}
    try:
        if str(regularization_start_date) == str(regularization_end_date):
            user_regularization_objs = SpUserRegularization.objects.filter(user_id=user_id,from_date__icontains=regularization_start_date).exclude(regularization_status=4)
        else:    
            user_regularization_objs = SpUserRegularization.objects.raw('''SELECT * FROM sp_user_regularization where (from_date BETWEEN %s AND %s OR to_date BETWEEN %s AND %s) and user_id=%s and regularization_status!=%s order by id desc ''',[regularization_start_date, regularization_end_date, regularization_start_date, regularization_end_date, user_id, '4'])
    except SpUserRegularization.DoesNotExist:
        user_regularization_objs = None
     
    if user_regularization_objs:
        applied_regularization_date_list = []
        for user_regularization_obj in user_regularization_objs:    
            
            if str(user_regularization_obj.from_date) == str(user_regularization_obj.to_date):
                regularization_date = datetime.strptime(str(user_regularization_obj.from_date), '%Y-%m-%d').strftime('%Y-%m-%d')
                applied_regularization_date_list.append(regularization_date)
            else:
                regularization_from_date = datetime.strptime(str(user_regularization_obj.from_date), '%Y-%m-%d').strftime('%Y-%m-%d')
                if user_regularization_obj.to_date:
                    regularization_to_date   = datetime.strptime(str(user_regularization_obj.to_date), '%Y-%m-%d').strftime('%Y-%m-%d')
                else:
                    regularization_to_date   = datetime.strptime(str(user_regularization_obj.from_date), '%Y-%m-%d').strftime('%Y-%m-%d')
                no_of_days = days_between(regularization_from_date, regularization_to_date)
                for i in range(0, int(no_of_days)):
                    regularization_date = (datetime.strptime(regularization_from_date, '%Y-%m-%d')+timedelta(days=i)).strftime('%Y-%m-%d')
                    applied_regularization_date_list.append(regularization_date)

        regularization_date_list = []
        if str(regularization_start_date) == str(regularization_end_date):
            regularization_date_list.append(regularization_start_date)
        else:
            no_of_days = days_between(regularization_start_date, regularization_end_date)
            for i in range(0, int(no_of_days)):
                regularization_date = (datetime.strptime(regularization_start_date, '%Y-%m-%d')+timedelta(days=i)).strftime('%Y-%m-%d')
                regularization_date_list.append(regularization_date)
        
        matched_date = [x for x in applied_regularization_date_list if x in regularization_date_list]
        if len(matched_date)>0:
           regularization_data['status'] = True     
        else:
            regularization_data['status'] = False
    else:
        regularization_data['status'] = False          
    return regularization_data



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
        if not SpUserAttendance.objects.filter(user_id=regularizations.user_id ,attendance_date_time__contains = start_date).exists():
            if start_date_day != 'Sunday':
                # if regularizations.regularization_type_id == 1:
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
                # else:
                #     start_time = str(regularizations.from_time)+':00'
                #     start_date_time = str(start_date)+' '+str(start_time)
                #     #start time
                #     data                        = SpUserAttendance()
                #     data.user_id                = regularizations.user_id
                #     data.attendance_date_time   = start_date_time
                #     data.start_time             = start_time
                #     data.end_time               = None
                #     data.dis_ss_id              = regularizations.user_id
                #     data.latitude               = None
                #     data.longitude              = None
                    
                #     data.attendance_type    = 1
                #     data.status             = 1
                #     data.save()
            
    return True  
    
    
    
    
    
def getHoilydayDates(start_date,end_date):
    date_list = []
    start_date = start_date
    end_date = end_date   # perhaps date.now()

    delta = end_date - start_date   # returns timedelta

    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        date_list.append(str(day))
        
    return date_list
