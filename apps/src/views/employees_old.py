from math import log
import sys
import os
import time
import json
from django.core.files.storage import FileSystemStorage
import openpyxl
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, response
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.apps import apps
from ..models import *
from django.db.models import *
from django.forms.models import model_to_dict
from utils import *
from datetime import datetime, date, timedelta
from io import BytesIO
from django.views import View
from django.conf import settings
from datetime import datetime, date
from datetime import timedelta
import pickle
import face_recognition
# python standard lib
import base64
import secrets
import io
# django and pillow lib
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from django.template.loader import render_to_string
from gtts import gTTS
import numpy as np
import cv2
import qrcode
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password



@login_required
def employeeIdCardEditor(request):
    template = 'employee/employee-id-card-editor.html'
    return render(request, template)


@login_required
def employeeQRGeneration(request):
    response = {}
    reg_no = request.POST.get('reg_no')
    blood_group = request.POST.get('blood_group')
    address = request.POST.get('address')
    if SpUsers.objects.filter(emp_sap_id=reg_no).exists() == False:
        response['message'] = "No employee id found"
        response['response_status'] = 404
        return JsonResponse(response)
    else:
        id_counter = SpUsers.objects.filter(emp_sap_id=reg_no).values(
            'id_card_attempts_left')[0]['id_card_attempts_left']

    if SpUsers.objects.filter(emp_sap_id=reg_no, is_id_card_generated=1).exists() and id_counter == 0:
        response['message'] = "No Attempts left! Please contact Admin."
        response['response_status'] = 403
        return JsonResponse(response)

    elif SpUsers.objects.filter(emp_sap_id=reg_no).exists() and id_counter == 3:
        student_info = SpUsers.objects.filter(emp_sap_id=reg_no)

        first_name = student_info[0].first_name
        last_name = ""
        if student_info[0].middle_name is None and student_info[0].last_name is not None:
            last_name += student_info[0].last_name
        elif student_info[0].middle_name is not None and student_info[0].last_name is not None:
            last_name += student_info[0].middle_name + \
                " " + student_info[0].last_name

        primary_no = student_info[0].primary_contact_number

        input_data = {"emp_id": reg_no, "name": first_name+" "+last_name, "address": address,
                      "primary_no": primary_no, "blood_group": blood_group}

        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(input_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        reg_url = reg_no.replace("/", "-")

        qr_parent_path = "./media/qr-code-image/"
        qr_url = qr_parent_path+reg_url+".png"
        img.save(qr_url)

        college_info = TblColleges.objects.filter(
            id=student_info[0].organization_id)
        for info in college_info:
            college_logo = info.college_logo
            college_website = info.college_website
            college_phone = info.college_contacts

        if address == "":
            address = "-"
        try:
            dob = SpBasicDetails.objects.get(user_id=student_info[0].id)
            dob = dob.date_of_birth.strftime('%d/%m/%Y')
        except SpBasicDetails.DoesNotExist:
            dob = None
        response['QR'] = qr_url
        response['blood_group'] = blood_group
        response['address'] = address
        response['first_name'] = first_name
        response['last_name'] = last_name
        response['reg_no'] = reg_no
        response['contact'] = primary_no
        response['role_name'] = student_info[0].role_name
        response['mail_id'] = student_info[0].official_email
        response['college_logo'] = college_logo
        response['dob'] = dob
        response['college_website'] = college_website.split("www.")[1]
        response['message'] = "Success"
        response['response_status'] = 200
        template = 'employee/id-card-preview.html'
        return render(request, template, response)
    elif SpUsers.objects.filter(emp_sap_id=reg_no).exists() and id_counter != 3 and id_counter > 0:
        response['message'] = "ID Card already generated."
        response['sub_message'] = str(
            id_counter) + " Download attempts left for Employee Id: "+reg_no
        response['response_status'] = 403
        return JsonResponse(response)
    else:
        response['message'] = "No employee id found"
        response['response_status'] = 404
        return JsonResponse(response)


@login_required
def employeeIDCardSave(request):
    reg_no = request.POST['reg_no']
    id_card = request.POST['id_card']
    reg_url = reg_no.replace("/", "-")
    context = {}
    id_counter = SpUsers.objects.filter(emp_sap_id=reg_no).values(
        'id_card_attempts_left')[0]['id_card_attempts_left']

    if id_counter > 0:
        im = Image.open(BytesIO(base64.b64decode(id_card.split(",")[1])))
        im.save("./media/id-cards/" + str(reg_url) + ".png", 'PNG')
        filePath = "./media/id-cards/" + reg_url + ".png"
        # id_counter = TblStudents.objects.filter(reg_no = reg_no).values('id_card_attempts_left')[0]['id_card_attempts_left']
        SpUsers.objects.filter(emp_sap_id=reg_no).update(is_id_card_generated=1, id_card_created_at=datetime.now(
        ), id_card_link=filePath, id_card_attempts_left=id_counter - 1)
        context['message'] = "Success"
        context['response_status'] = 200
    else:
        context['id_counter'] = 0
        context['message'] = "No Attempts left! Please contact Admin."
        context['response_status'] = 403
    return JsonResponse(context)


@login_required
def employeeIDCardDownload(request):
    reg_no = request.POST['reg_no']
    id_counter = SpUsers.objects.filter(emp_sap_id=reg_no).values(
        "id_card_attempts_left")[0]['id_card_attempts_left']
    response = {}
    if id_counter > 0:
        id_url = SpUsers.objects.filter(emp_sap_id=reg_no).values(
            "id_card_link")[0]['id_card_link']
        SpUsers.objects.filter(emp_sap_id=reg_no).update(
            is_id_card_generated=1, id_card_created_at=datetime.now(), id_card_attempts_left=id_counter - 1)
        response['id_url'] = id_url
        response['id_counter'] = id_counter - 1
        response['message'] = "Success"
        response['response_status'] = "200"
    else:
        response['id_counter'] = 0
        response['message'] = "No Attempts left! Please contact Admin."
        response['response_status'] = 403
    return JsonResponse(response)


def sendWebNotification(student_id):
    registration_ids = []
    tokens = TblUserWebTokens.objects.all().values_list('token', flat=True).distinct()
    for token in tokens:
        registration_ids.append(token)
    if len(tokens):

        student_details = TblStudents.objects.raw(''' SELECT tbl_students.id,tbl_students.first_name,tbl_students.middle_name,
        tbl_students.last_name,tbl_students.semester_id,tbl_branch.branch FROM tbl_students
        LEFT JOIN tbl_branch on tbl_branch.id = tbl_students.branch_id
        WHERE tbl_students.id=%s ''', [student_id])

        student_name = student_details[0].first_name+' '
        if student_details[0].middle_name is not None:
            student_name += student_details[0].middle_name+' '
        if student_details[0].last_name is not None:
            student_name += student_details[0].last_name

        tmp = student_details[0].semester_id.split('_')
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
            semester_year = str(tmp[1])+suffix+" Sem"
        else:
            semester_year = str(tmp[1])+suffix+" Year"

        title = "Attendance marked Successfully."
        message = student_name+" "
        message += "(" + student_details[0].branch + " - "+semester_year + ") marked his/her attendance successfully at " + str(datetime.now().strftime('%H:%M'))+"."

        result = sendWebPushNotification(title, message, registration_ids)


@csrf_exempt
@login_required
def markEmployeeAttendance(request):
    if request.method == "GET":
        context = {}
        template = 'employee/attendance/new-mark-employee-attendance.html'
        return render(request, template, context)
    else:
        context = {}
        if 'student_id' in request.POST and request.POST['student_id'] != "":
            current_date = datetime.now().strftime('%Y-%m-%d')
            if TblClEmployeeAttendance.objects.filter(emp_id=request.POST['student_id'], created_at__contains=current_date).exists():
                last_record = TblClEmployeeAttendance.objects.filter(
                    emp_id=request.POST['student_id'], created_at__contains=current_date).last()
                if last_record.end_datetime is None:
                    TblClEmployeeAttendance.objects.filter(
                        id=last_record.id).update(end_datetime=datetime.now())
                    context['flag'] = True
                    context['message'] = "Attendance marked successfully."
                    context['current_time'] = datetime.now().strftime('%H:%M')

                    # send notification to web
                    # sendWebNotification(request.POST['student_id'])

                else:
                    attendance = TblClEmployeeAttendance()
                    attendance.emp_id = request.POST['student_id']
                    attendance.start_datetime = datetime.now()
                    attendance.end_datetime = None
                    if 'latitude' in request.POST and request.POST['latitude'] != "":
                        attendance.latitude = request.POST['latitude']
                    if 'longitude' in request.POST and request.POST['longitude'] != "":
                        attendance.longitude = request.POST['longitude']
                    attendance.save()

                    context['flag'] = True
                    context['message'] = "Attendance marked successfully."
                    context['current_time'] = datetime.now().strftime('%H:%M')

                    # send notification to web
                    # sendWebNotification(request.POST['student_id'])
            else:
                attendance = TblClEmployeeAttendance()
                attendance.emp_id = request.POST['student_id']
                attendance.start_datetime = datetime.now()
                attendance.end_datetime = None
                if 'latitude' in request.POST and request.POST['latitude'] != "":
                    attendance.latitude = request.POST['latitude']
                if 'longitude' in request.POST and request.POST['longitude'] != "":
                    attendance.longitude = request.POST['longitude']
                attendance.save()

                context['flag'] = True
                context['message'] = "Attendance marked successfully."
                context['current_time'] = datetime.now().strftime('%H:%M')

                # send notification to web
                # sendWebNotification(request.POST['student_id'])
        else:
            context['flag'] = False
            context['message'] = "Parameter missing. please try again."

        return JsonResponse(context)


@csrf_exempt
@login_required
def getByEmployeeId(request):
    context = {}
    if request.method == "POST":
        reg_number = request.POST['reg_number']
        student_details = SpUsers.objects.raw(''' SELECT sp_users.*,sp_basic_details.father_name,sp_basic_details.mother_name , sp_basic_details.aadhaar_nubmer FROM sp_users
        LEFT JOIN tbl_colleges on tbl_colleges.id = sp_users.organization_id LEFT JOIN sp_basic_details on sp_basic_details.user_id = sp_users.id WHERE sp_users.emp_sap_id=%s ''', [reg_number])
        if student_details:
            context['student_details'] = student_details[0]
            if student_details[0].organization_id == 1:
                context['college_base_url'] = "http://bipe.sortstring.co.in/"
            elif student_details[0].organization_id == 2:
                context['college_base_url'] = "http://bite.sortstring.co.in/"
            elif student_details[0].organization_id == 3:
                context['college_base_url'] = "http://bip.sortstring.co.in/"
            student_id = student_details[0].id
            current_date = datetime.now().strftime('%Y-%m-%d')
            if TblAttendance.objects.filter(student_id=student_id, created_at__contains=current_date).exists():
                last_record = TblAttendance.objects.filter(
                    student_id=student_id, created_at__contains=current_date).last()
                if last_record.end_datetime is None:
                    context['punch_in_status'] = 1
                    context['last_punch_in'] = last_record.start_datetime
                else:
                    context['punch_in_status'] = 0
                    context['last_punch_in'] = last_record.end_datetime
            else:
                context['punch_in_status'] = 0
                context['last_punch_in'] = None

            student_html = render_to_string('employee/attendance/employee-details.html', context)

            student_name = student_details[0].first_name+' '
            if student_details[0].middle_name is not None:
                student_name += student_details[0].middle_name+' '
            if student_details[0].last_name is not None:
                student_name += student_details[0].last_name+' '

            # generate audio
            student_file_name = "student_id_"+str(student_id)+".mp3"
            if os.path.isdir(str(settings.MEDIA_ROOT)+'/attendance_audio/qr_scan/'+student_file_name):
                audio = '/media/attendance_audio/qr_scan/'+student_file_name
            else:
                Text = "Welcome "+student_name+". Please scan your thumb."
                speech = gTTS(text=Text)
                file_name = str(settings.MEDIA_ROOT) + '/attendance_audio/qr_scan/'+student_file_name
                speech.save(file_name)
                audio = '/media/attendance_audio/qr_scan/'+student_file_name

            response = {}
            response['flag'] = True
            response['student_id'] = student_id
            response['student_html'] = student_html
            response['audio'] = audio

            return JsonResponse(response)
        else:
            context['flag'] = False
            context['message'] = "Record not found"

    else:
        context['flag'] = False
        context['message'] = "Method not allowed"

    return JsonResponse(context)


@login_required
def getEmployeeThumbs(request, emp_id):
    context = {}
    if request.method == "POST":
        context['flag'] = False
        context['message'] = "Method not allowed"
    else:
        student_details = SpUsers.objects.raw(''' SELECT sp_users.id,sp_users.finger_iso_1,sp_users.finger_iso_2 FROM sp_users WHERE sp_users.id=%s''', [emp_id])
        if student_details:
            context['flag'] = True
            context['student_details'] = model_to_dict(student_details[0])
        else:
            context['flag'] = False
            context['message'] = "Record not found"
    return JsonResponse(context)


@login_required
def employeeAttendanceReport(request):

    page = request.GET.get('page')

    students = SpUsers.objects.raw(''' SELECT sp_users.* FROM sp_users
    LEFT JOIN tbl_colleges on tbl_colleges.id = sp_users.organization_id 
    LEFT JOIN tbl_cl_employee_attendance on tbl_cl_employee_attendance.emp_id = sp_users.id
    WHERE sp_users.user_type = 1 AND  date(tbl_cl_employee_attendance.created_at)=CURDATE() GROUP BY tbl_cl_employee_attendance.emp_id ORDER BY  sp_users.id DESC ''')

    totat_record = len(students)

    paginator = Paginator(list(students), getConfigurationResult('page_limit'))

    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)
    if page is not None:
        page = page
    else:
        page = 1

    total_pages = int(paginator.count/getConfigurationResult('page_limit'))

    if(paginator.count == 0):
        paginator.count = 1

    temp = total_pages % paginator.count
    if(temp > 0 and getConfigurationResult('page_limit') != paginator.count):
        total_pages = total_pages+1
    else:
        total_pages = total_pages

    context = {}

    for student in students:
        college = TblColleges.objects.get(id=student.organization_id)
        student.college_name = college.college_name
        current_date = datetime.now().strftime('%Y-%m-%d')
        if TblClEmployeeAttendance.objects.filter(emp_id=student.id, created_at__contains=current_date).exists():
            last_record = TblClEmployeeAttendance.objects.filter(
                emp_id=student.id, created_at__contains=current_date).last()
            if last_record.end_datetime is None:
                student.punch_in_time = last_record.start_datetime
                student.punch_out_time = None
            else:
                student.punch_in_time = last_record.start_datetime
                student.punch_out_time = last_record.end_datetime
        else:
            student.punch_in_time = None
            student.punch_out_time = None

    student_details = SpUsers.objects.raw(''' SELECT sp_users.*,tbl_colleges.college_name ,sp_basic_details.father_name,sp_basic_details.mother_name,sp_basic_details.aadhaar_nubmer 
    FROM sp_users LEFT JOIN tbl_colleges on tbl_colleges.id = sp_users.organization_id 
    LEFT JOIN sp_basic_details on sp_basic_details.user_id = sp_users.id
    LEFT JOIN tbl_cl_employee_attendance on tbl_cl_employee_attendance.emp_id = sp_users.id WHERE date(tbl_cl_employee_attendance.created_at)=CURDATE()
    ORDER BY  sp_users.id DESC LIMIT 1
    ''')
    if student_details:
        context['student_details'] = student_details[0]
        if student_details[0].organization_id == 1:
            context['college_base_url'] = "http://bipe.sortstring.co.in/"
        elif student_details[0].organization_id == 2:
            context['college_base_url'] = "http://bite.sortstring.co.in/"
        elif student_details[0].organization_id == 3:
            context['college_base_url'] = "http://bip.sortstring.co.in/"

        current_date = datetime.now().strftime('%Y-%m-%d')
        if TblClEmployeeAttendance.objects.filter(emp_id=student_details[0].id, created_at__contains=current_date).exists():
            last_record = TblClEmployeeAttendance.objects.filter(
                emp_id=student_details[0].id, created_at__contains=current_date).last()
            if last_record.end_datetime is None:
                context['punch_in_status'] = 1
                context['last_punch_in'] = last_record.start_datetime
            else:
                context['punch_in_status'] = 0
                context['last_punch_in'] = last_record.end_datetime
        else:
            context['punch_in_status'] = 0
            context['last_punch_in'] = None

    context['colleges'] = TblColleges.objects.all().values('id','college_name')
    

    context['students'] = students
    context['totat_record'] = totat_record
    context['total_pages'] = total_pages
    context['page_limit'] = getConfigurationResult('page_limit')
    context['page_title'] = "Employee Attendance Report"
    context['current_date'] = datetime.now().strftime('%Y-%m-%d')
    template = 'employee/attendance/employee-attendance-report.html'
    return render(request, template, context)


@login_required
def employeeAttendanceDetail(request, emp_id):
    context = {}
    if request.method == "GET":
        context['flag'] = False
        context['message'] = "Method not allowed"
    else:
        student_details = SpUsers.objects.raw(''' SELECT sp_users.*,tbl_colleges.college_name ,sp_basic_details.father_name,sp_basic_details.mother_name,sp_basic_details.aadhaar_nubmer FROM sp_users
        LEFT JOIN tbl_colleges on tbl_colleges.id = sp_users.organization_id 
        LEFT JOIN sp_basic_details on sp_basic_details.user_id = sp_users.id
        WHERE sp_users.id=%s ''', [emp_id])

        if student_details:
            context['student_details'] = student_details[0]
            if student_details[0].organization_id == 1:
                context['college_base_url'] = "http://bipe.sortstring.co.in/"
            elif student_details[0].organization_id == 2:
                context['college_base_url'] = "http://bite.sortstring.co.in/"
            elif student_details[0].organization_id == 3:
                context['college_base_url'] = "http://bip.sortstring.co.in/"

            current_filter_date = datetime.now().strftime('%Y-%m-%d')
            if 'date' in request.POST and request.POST['date'] != "":
                current_filter_date = datetime.strptime(
                    request.POST['date'], "%d/%m/%Y").strftime('%Y-%m-%d')

            if TblClEmployeeAttendance.objects.filter(emp_id=emp_id, created_at__contains=current_filter_date).exists():
                last_record = TblClEmployeeAttendance.objects.filter(
                    emp_id=emp_id, created_at__contains=current_filter_date).last()
                if last_record.end_datetime is None:
                    context['punch_in_status'] = 1
                    context['last_punch_in'] = last_record.start_datetime
                else:
                    context['punch_in_status'] = 0
                    context['last_punch_in'] = last_record.end_datetime
            else:
                context['punch_in_status'] = 0
                context['last_punch_in'] = None

            context['current_date'] = datetime.now().strftime('%Y-%m-%d')
            context['current_filter_date'] = current_filter_date
            template = "employee/attendance/employee-attendance-details.html"

            return render(request, template, context)
        else:
            context['flag'] = False
            context['message'] = "Record not found"

    return JsonResponse(context)


@login_required
def filterEmployeeAttendanceReport(request):
    context = {}

    page = request.GET.get('page')
    condition = ''

    if 'search' in request.POST and request.POST['search'] != "":
        condition += " and (sp_users.first_name LIKE '%%" + \
            request.POST['search']+"%%' OR sp_users.primary_contact_number LIKE '%%" + \
            request.POST['search']+"%%') "

    if 'college_id' in request.POST and request.POST['college_id'] != "":
        condition += " and sp_users.organization_id=" + request.POST['college_id']

    if 'mentor' in request.POST and request.POST['mentor'] != "":
        condition += " and sp_users.depatment_id='" + request.POST['mentor']+"'"

    if 'date' in request.POST and request.POST['date'] != "":
        date = datetime.strptime(request.POST['date'], "%d/%m/%Y").strftime('%Y-%m-%d')
        condition += " and date(tbl_cl_employee_attendance.created_at)='"+date+"'"

    if condition == "":
        students = SpUsers.objects.raw(''' SELECT sp_users.* FROM sp_users
        LEFT JOIN tbl_colleges on tbl_colleges.id = sp_users.organization_id 
        LEFT JOIN tbl_cl_employee_attendance on tbl_cl_employee_attendance.emp_id = sp_users.id
        WHERE sp_users.user_type = 1 AND  date(tbl_attendance.created_at)=CURDATE()  ORDER BY sp_users.id DESC ''')
    else:
        students = SpUsers.objects.raw(''' SELECT sp_users.* FROM sp_users
        LEFT JOIN tbl_colleges on tbl_colleges.id = sp_users.organization_id 
        LEFT JOIN tbl_cl_employee_attendance on tbl_cl_employee_attendance.emp_id = sp_users.id
        WHERE sp_users.user_type = 1  AND 1 {condition} ORDER BY sp_users.id DESC '''.format(condition=condition))

    total_record = len(students)
    for student in students:
        college = TblColleges.objects.get(id=student.organization_id)
        student.college_name = college.college_name

        current_date = datetime.now().strftime('%Y-%m-%d')
        if 'date' in request.POST and request.POST['date'] != "":
            current_date = datetime.strptime(
                request.POST['date'], "%d/%m/%Y").strftime('%Y-%m-%d')

        context['current_date'] = current_date

        if TblClEmployeeAttendance.objects.filter(emp_id=student.id, created_at__contains=current_date).exists():
            last_record = TblClEmployeeAttendance.objects.filter(
                emp_id=student.id, created_at__contains=current_date).last()
            if last_record.end_datetime is None:
                student.punch_in_time = last_record.start_datetime
                student.punch_out_time = None
            else:
                student.punch_in_time = last_record.start_datetime
                student.punch_out_time = last_record.end_datetime
        else:
            student.punch_in_time = None
            student.punch_out_time = None

    paginator = Paginator(list(students), getConfigurationResult('page_limit'))

    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)
    if page is not None:
        page = page
    else:
        page = 1

    total_pages = int(paginator.count/getConfigurationResult('page_limit'))

    if(paginator.count == 0):
        paginator.count = 1

    temp = total_pages % paginator.count
    if(temp > 0 and getConfigurationResult('page_limit') != paginator.count):
        total_pages = total_pages+1
    else:
        total_pages = total_pages

    context['students'] = students
    context['total_record'] = total_record
    context['total_pages'] = total_pages
    context['page_limit'] = getConfigurationResult('page_limit')
    template = 'employee/attendance/filter-employee-attendance-report.html'
    return render(request, template, context)

