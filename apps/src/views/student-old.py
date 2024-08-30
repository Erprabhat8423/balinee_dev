from math import log
import sys
import os
import time,json
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
from datetime import datetime, date,timedelta
from io import BytesIO
from django.views import View
from django.conf import settings
from datetime import datetime, date
from datetime import timedelta
import pickle
import face_recognition
# python standard lib
import base64, secrets, io

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

def get_image_from_data_url( data_url, resize=True, base_width=600 ):

    # getting the file format and the necessary dataURl for the file
    _format, _dataurl       = data_url.split(';base64,')
    # file name and extension
    _filename, _extension   = secrets.token_hex(20), _format.split('/')[-1]

    # generating the contents of the file
    file = ContentFile( base64.b64decode(_dataurl), name=f"{_filename}.{_extension}")

    # resizing the image, reducing quality and size
    if resize:

        # opening the file with the pillow
        image = Image.open(file)
        # using BytesIO to rewrite the new content without using the filesystem
        image_io = io.BytesIO()

        # resize
        w_percent    = (base_width/float(image.size[0]))
        h_size       = int((float(image.size[1])*float(w_percent)))
        image        = image.resize((base_width,h_size), Image.ANTIALIAS)

        # save resized image
        image.save(image_io, format=_extension)

        # generating the content of the new image
        file = ContentFile( image_io.getvalue(), name=f"{_filename}.{_extension}" )

    # file and filename
    return file, ( _filename, _extension )

@login_required
def index(request):

    page = request.GET.get('page')
    students = TblStudents.objects.filter(is_registered=1).values('id','reg_no','status','college_id','branch_id','semester_id','first_name','middle_name','last_name','father_name','primary_contact_no','is_mobile_verified','is_registered','id_card_pin', 'latitude', 'longitude').order_by('-id')

    paginator = Paginator(students, getConfigurationResult('page_limit'))

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

    temp = total_pages%paginator.count
    if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
        total_pages = total_pages+1
    else:
        total_pages = total_pages

    context = {}

    for student in students:
        college = TblColleges.objects.get(id=student['college_id'])
        course = TblBranch.objects.get(id=student['branch_id'])
        student['college_name'] = college.college_name
        student['college_alias'] = college.alias
        student['branch'] = course.branch

        tmp = student['semester_id'].split('_')
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
            student['semester_year'] = str(tmp[1])+suffix+" Sem"
        else:
            student['semester_year'] = str(tmp[1])+suffix+" Year"

    student_details = TblStudents.objects.raw(''' SELECT tbl_students.*,tbl_colleges.college_name,tbl_branch.branch FROM tbl_students
    LEFT JOIN tbl_colleges on tbl_colleges.id = tbl_students.college_id 
    LEFT JOIN tbl_branch on tbl_branch.id = tbl_students.branch_id
    WHERE tbl_students.is_registered = 1
    ORDER BY  tbl_students.id DESC LIMIT 1
    ''')
    if student_details:
        context['student_details']        = student_details[0]
        if student_details[0].college_id == 1:
            context['college_base_url'] = "http://bipe.sortstring.co.in/"
        elif student_details[0].college_id == 2:
            context['college_base_url'] = "http://bite.sortstring.co.in/"
        elif student_details[0].college_id == 3:
            context['college_base_url'] = "http://bip.sortstring.co.in/"

    context['students']                 = students
    context['total_pages']              = total_pages
    context['page_limit']               = getConfigurationResult('page_limit')
    context['page_title']               = "Manage Students"
    context['google_app_key']           = getConfigurationResult('google_app_key')
    template = 'student/index.html'
    return render(request, template, context)

@login_required
def showMapsView(request):
    context = {}
    try:
        user_coordinates = TblStudents.objects.get(id=request.GET['student_id'])
    except TblStudents.DoesNotExist:
        user_coordinates = None

    context['user_coordinates'] = user_coordinates
    context['google_app_key']   = getConfigurationResult('google_app_key')
    template = 'student/user-geo-tagged.html'

    return render(request, template,context)

@login_required
def addCoordinates(request):
    latitude = request.POST['latitude']
    longitude = request.POST['longitude']
    student_id = request.POST['student_id']
    print("POST: ", latitude, longitude, student_id)
    TblStudents.objects.filter(id = student_id).update(latitude=latitude, longitude=longitude)
    return JsonResponse({'message':'Success', 'status': 200}, status=200)

@login_required
def ajaxStudentList(request):
    page = request.GET.get('page')
    students = TblStudents.objects.filter(is_registered=1).values('id','reg_no','college_id','branch_id','semester_id','first_name','middle_name','last_name','father_name','primary_contact_no','is_mobile_verified','is_registered','id_card_pin', 'latitude', 'longitude').order_by('-id')
    for student in students:
        college = TblColleges.objects.get(id=student['college_id'])
        course = TblBranch.objects.get(id=student['branch_id'])
        student['college_name'] = college.college_name
        student['college_alias'] = college.alias
        student['branch'] = course.branch

        tmp = student['semester_id'].split('_')
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
            student['semester_year'] = str(tmp[1])+suffix+" Sem"
        else:
            student['semester_year'] = str(tmp[1])+suffix+" Year"

    paginator = Paginator(students, getConfigurationResult('page_limit'))

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
        
    temp = total_pages%paginator.count
    if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
        total_pages = total_pages+1
    else:
        total_pages = total_pages

    context = {}

    student_details = TblStudents.objects.raw(''' SELECT tbl_students.*,tbl_colleges.college_name,tbl_branch.branch FROM tbl_students
    LEFT JOIN tbl_colleges on tbl_colleges.id = tbl_students.college_id 
    LEFT JOIN tbl_branch on tbl_branch.id = tbl_students.branch_id
    ORDER BY  tbl_students.id DESC LIMIT 1
    ''')
    if student_details:
        context['student_details']        = student_details[0]
        if student_details[0].college_id == 1:
            context['college_base_url'] = "http://bipe.sortstring.co.in/"
        elif student_details[0].college_id == 2:
            context['college_base_url'] = "http://bite.sortstring.co.in/"
        elif student_details[0].college_id == 3:
            context['college_base_url'] = "http://bip.sortstring.co.in/"
    

    
    context['students']          = students
    context['total_pages']            = total_pages
    context['page_limit']             = getConfigurationResult('page_limit')

    template = 'student/ajax-students.html'
    return render(request, template, context)


@login_required
def ajaxStudentLists(request):
    page = request.GET.get('page')

    students = TblStudents.objects.filter(is_registered=1).values('id','reg_no','status','college_id','branch_id','semester_id','first_name','middle_name','last_name','father_name','primary_contact_no','is_mobile_verified','is_registered','id_card_pin', 'latitude', 'longitude').order_by('-id')
    for student in students:
        college = TblColleges.objects.get(id=student['college_id'])
        course = TblBranch.objects.get(id=student['branch_id'])
        student['college_name'] = college.college_name
        student['college_alias'] = college.alias
        student['branch'] = course.branch

        tmp = student['semester_id'].split('_')
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
            student['semester_year'] = str(tmp[1])+suffix+" Sem"
        else:
            student['semester_year'] = str(tmp[1])+suffix+" Year"

    paginator = Paginator(students, getConfigurationResult('page_limit'))

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

    temp = total_pages%paginator.count
    if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
        total_pages = total_pages+1
    else:
        total_pages = total_pages
    
    context = {}
    context['students']     = students
    context['total_pages']       = total_pages

    template = 'student/ajax-student-lists.html'
    return render(request, template, context)

@login_required
def updateStudentStatus(request):
    response = {}
    if request.method == "POST":
        try:
            id = request.POST.get('id')
            is_active = request.POST.get('is_active')

            data = TblStudents.objects.get(id=id)
            data.status = is_active
            data.save()

            if is_active == '1':
                status = 'Unblock'
            else:
                status = 'Block'
            response['error'] = False
            response['message'] = "Record has been updated successfully."
        except ObjectDoesNotExist:
            response['error'] = True
            response['message'] = "Method not allowed"
        except Exception as e:
            response['error'] = True
            response['message'] = e
        return JsonResponse(response)
    return redirect('/students')

@login_required
def filterStudent(request):
    context = {}

    page = request.GET.get('page')
    condition = ''

    if 'search' in request.POST and request.POST['search'] != "":
        students = TblStudents.objects.filter(Q(first_name__icontains=request.POST['search']) | Q(primary_contact_no__contains=request.POST['search'])).filter(is_registered=1).values('id','reg_no','college_id','branch_id','semester_id','first_name','middle_name','last_name','father_name','primary_contact_no','is_mobile_verified','is_registered','id_card_pin', 'latitude', 'longitude').order_by('-id')
    else:
        students = TblStudents.objects.filter(is_registered=1).values('id','reg_no','college_id','branch_id','semester_id','first_name','middle_name','last_name','father_name','primary_contact_no','is_mobile_verified','is_registered','id_card_pin').order_by('-id')

    for student in students:
        college = TblColleges.objects.get(id=student['college_id'])
        course = TblBranch.objects.get(id=student['branch_id'])
        student['college_name'] = college.college_name
        student['college_alias'] = college.alias
        student['branch'] = course.branch

        tmp = student['semester_id'].split('_')
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
            student['semester_year'] = str(tmp[1])+suffix+" Sem"
        else:
            student['semester_year'] = str(tmp[1])+suffix+" Year"

    paginator = Paginator(students, getConfigurationResult('page_limit'))

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
        
    temp = total_pages%paginator.count
    if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
        total_pages = total_pages+1
    else:
        total_pages = total_pages

    context = {}

    student_details = TblStudents.objects.raw(''' SELECT tbl_students.*,tbl_colleges.college_name,tbl_branch.branch FROM tbl_students
    LEFT JOIN tbl_colleges on tbl_colleges.id = tbl_students.college_id 
    LEFT JOIN tbl_branch on tbl_branch.id = tbl_students.branch_id
    ORDER BY  tbl_students.id DESC LIMIT 1
    ''')
    if student_details:
        context['student_details']        = student_details[0]
        if student_details[0].college_id == 1:
            context['college_base_url'] = "http://bipe.sortstring.co.in/"
        elif student_details[0].college_id == 2:
            context['college_base_url'] = "http://bite.sortstring.co.in/"
        elif student_details[0].college_id == 3:
            context['college_base_url'] = "http://bip.sortstring.co.in/"
    

    
    context['students']          = students
    context['total_pages']            = total_pages
    context['page_limit']             = getConfigurationResult('page_limit')

    template = 'student/filter-students.html'
    return render(request, template, context)

@login_required
def studentShortDetail(request,student_id):
    context = {}
    student_details = TblStudents.objects.raw(''' SELECT tbl_students.*,tbl_colleges.college_name,tbl_branch.branch,tbl_cl_documents.ducument_number FROM tbl_students
    LEFT JOIN tbl_colleges on tbl_colleges.id = tbl_students.college_id 
    LEFT JOIN tbl_branch on tbl_branch.id = tbl_students.branch_id
    LEFT JOIN tbl_cl_documents on tbl_cl_documents.student_id = tbl_students.id
    WHERE tbl_students.id=%s
    ''',[student_id])
    if student_details:
        context['student_details']        = student_details[0]
        if student_details[0].college_id == 1:
            context['college_base_url'] = "http://bipe.sortstring.co.in/"
        elif student_details[0].college_id == 2:
            context['college_base_url'] = "http://bite.sortstring.co.in/"
        elif student_details[0].college_id == 3:
            context['college_base_url'] = "http://bip.sortstring.co.in/"

    template = 'student/student-short-details.html'
    return render(request, template,context)

   


@login_required
def generateDigitalIdCard(request,student_id):
    if request.method == "POST":
        pass
    else:

        context = {}
        student_details = TblStudents.objects.raw(''' SELECT tbl_students.*,tbl_colleges.college_name,tbl_branch.branch FROM tbl_students
        LEFT JOIN tbl_colleges on tbl_colleges.id = tbl_students.college_id 
        LEFT JOIN tbl_branch on tbl_branch.id = tbl_students.branch_id
        WHERE tbl_students.id=%s
        ''',[student_id])
        if student_details:
            context['student_details']        = student_details[0]
            if student_details[0].college_id == 1:
                context['college_base_url'] = "http://bipe.sortstring.co.in/"
            elif student_details[0].college_id == 2:
                context['college_base_url'] = "http://bite.sortstring.co.in/"
            elif student_details[0].college_id == 3:
                context['college_base_url'] = "http://bip.sortstring.co.in/"

        template = 'student/generate-digital-id-card.html'
        return render(request, template,context)

@login_required
def getStudentThumbs(request,student_id):
    context = {}
    if request.method == "POST":
        context['flag'] = False
        context['message'] = "Method not allowed"
    else:
        student_details = TblStudents.objects.raw(''' SELECT tbl_students.id,tbl_students.finger_iso_1,tbl_students.finger_iso_2 FROM tbl_students WHERE tbl_students.id=%s
        ''',[student_id])
        if student_details:
            context['flag'] = True
            context['student_details'] = model_to_dict(student_details[0])
        else:
            context['flag'] = False
            context['message'] = "Record not found"

    return JsonResponse(context)   


@login_required
def generateIdOtp(request,student_id):
    context = {}
    if request.method == "POST":
        context['flag'] = False
        context['message'] = "Method not allowed"
    else:
        student_details = TblStudents.objects.raw(''' SELECT tbl_students.id FROM tbl_students WHERE tbl_students.id=%s
        ''',[student_id])
        if student_details:
            otp = getStudentUniqueOtp(student_details[0].id)
            TblStudents.objects.filter(id=student_details[0].id).update(id_card_pin=otp,is_id_card_pin_verified=0)

            if student_details[0].primary_contact_no is not None or student_details[0].primary_contact_no != "":
                #send sms to student
                download_link = "https://play.google.com/store/apps/details?id=com.flutter.id_card_app"
                message = "Click on the link ("+download_link+") to download the college ID card. BGIVNS" 
                sendSMS('BGIVNS',student_details[0].primary_contact_no,message) 

            context['flag'] = True
            context['otp'] = otp

        else:
            context['flag'] = False
            context['message'] = "Record not found"

    return JsonResponse(context)  

def getStudentUniqueOtp(student_id):
    otp = generateOTP(6)
    if TblStudents.objects.filter(id=student_id,id_card_pin=otp).exists():
        getStudentUniqueOtp(student_id)
    else:
        return otp


@csrf_exempt
def registerFace(request):
    context = {}
    if request.method == "POST":
        image = request.POST['image']
        primary_contact_no = request.POST['primary_contact_no']
        student = TblStudents.objects.raw(''' SELECT id,reg_no,college_id,profile_image FROM tbl_students 
        WHERE is_registered = 1 and primary_contact_no = %s ORDER BY  id DESC ''', [primary_contact_no])
        if student:
            if student[0].profile_image:
                imageName = str(student[0].id)
                im = Image.open(BytesIO(base64.b64decode(image)))
                im.save("media/students-images/" + str(imageName) + ".png", 'PNG')
                filePath = "media/students-images/" + imageName + ".png"

                # update student image
                TblStudents.objects.filter(id=student[0].id).update(student_image=filePath)

                datfile = "media/faceEncodes/students.dat"
                try:
                    fr = open(datfile, 'rb')
                    a = pickle.load(fr)
                    dictionary = dict(a)
                    all_face_encodings = {}
                    img1 = face_recognition.load_image_file(filePath)
                    all_face_encodings[imageName] = face_recognition.face_encodings(img1)[0]
                    dictionary.update(all_face_encodings)
                    with open(datfile, 'wb') as f:
                        pickle.dump(dictionary, f)
                    
                        context['flag'] = True
                        context['message'] = "Saved Successfully"

                except:
                    all_face_encodings = {}
                    img1 = face_recognition.load_image_file(filePath)
                    all_face_encodings[imageName] = face_recognition.face_encodings(img1)[0]
                    with open('media/faceEncodes/students.dat', 'wb') as f:
                        pickle.dump(all_face_encodings, f)
                        context['flag'] = True
                        context['message'] = "Saved Successfully"

                
        else:
            context['flag'] = False
            context['message'] = "Record not found."

        return JsonResponse(context)
    else:
        template = 'student/register-face.html'
        return render(request, template, context)



@csrf_exempt
@login_required
def getByMobileNumber(request):
    if request.method == "POST":
        context = {}
        primary_contact_no = request.POST['primary_contact_no']
        student_details = TblStudents.objects.raw(''' SELECT tbl_students.*,tbl_colleges.college_name,tbl_branch.branch FROM tbl_students
        LEFT JOIN tbl_colleges on tbl_colleges.id = tbl_students.college_id 
        LEFT JOIN tbl_branch on tbl_branch.id = tbl_students.branch_id
        WHERE tbl_students.primary_contact_no=%s
        ''',[primary_contact_no])
        if student_details:
            context['student_details']        = student_details[0]
            if student_details[0].college_id == 1:
                context['college_base_url'] = "http://bipe.sortstring.co.in/"
            elif student_details[0].college_id == 2:
                context['college_base_url'] = "http://bite.sortstring.co.in/"
            elif student_details[0].college_id == 3:
                context['college_base_url'] = "http://bip.sortstring.co.in/"
            
            template = 'student/student-short-details.html'
            return render(request, template,context)
        else:
            context['flag'] = False
            context['message'] = "Record not found"

    else:
        context['flag'] = False
        context['message'] = "Method not allowed"
    
    return JsonResponse(context)

@csrf_exempt
@login_required
def getByRegistrationNumber(request):
    context = {}
    if request.method == "POST":
        reg_number = request.POST['reg_number']
        student_details = TblStudents.objects.raw(''' SELECT tbl_students.*,tbl_colleges.college_name,tbl_branch.branch FROM tbl_students
        LEFT JOIN tbl_colleges on tbl_colleges.id = tbl_students.college_id 
        LEFT JOIN tbl_branch on tbl_branch.id = tbl_students.branch_id
        WHERE tbl_students.reg_no=%s
        ''',[reg_number])
        if student_details:
            context['student_details'] = student_details[0]
            if student_details[0].college_id == 1:
                context['college_base_url'] = "http://bipe.sortstring.co.in/"
            elif student_details[0].college_id == 2:
                context['college_base_url'] = "http://bite.sortstring.co.in/"
            elif student_details[0].college_id == 3:
                context['college_base_url'] = "http://bip.sortstring.co.in/"
            student_id = student_details[0].id
            current_date = datetime.now().strftime('%Y-%m-%d')
            if TblAttendance.objects.filter(student_id=student_id,created_at__contains=current_date).exists():
                last_record = TblAttendance.objects.filter(student_id=student_id,created_at__contains=current_date).last()
                if last_record.end_datetime is None:
                    context['punch_in_status'] = 1
                    context['last_punch_in'] = last_record.start_datetime
                else:
                    context['punch_in_status'] = 0
                    context['last_punch_in'] = last_record.end_datetime
            else:
                context['punch_in_status'] = 0
                context['last_punch_in'] = None
            
            student_html = render_to_string('attendance/student-details.html', context)

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
                speech = gTTS(text = Text)
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
    
    
@csrf_exempt
@login_required
def addStudentBasicDetails(request):
    if request.method == "GET":
        context={}
        college = TblColleges.objects.all()
        context['college'] = college
        context['semester']=TblSemester.objects.all().filter(type__startswith="semester")
        return render(request,"student/add-student-basic-detail.html",context)
    elif request.method == "POST":

        try:
            college_name=request.POST.get('college_name')
            first_name=request.POST.get('first_name')
            middle_name=request.POST.get('middle_name')
            last_name=request.POST.get('last_name')
            father_name=request.POST.get('father_name')
            mother_name=request.POST.get('mother_name')
            aadhaar_no=request.POST.get('aadhaar_no')
            primary_contact_no=request.POST.get('primary_contact_no')
            reg_no=request.POST.get('reg_no')
            branch = request.POST.get('branch')
            semester = request.POST.get('sem_name')
            student = TblStudents()
            student.college_id=college_name
            student.first_name=first_name
            student.middle_name=middle_name
            student.last_name=last_name
            student.father_name=father_name
            student.mother_name=mother_name
            student.aadhaar_no=aadhaar_no
            student.primary_contact_no=primary_contact_no
            student.reg_no=reg_no
            student.branch_id = branch
            student.semester_id = semester
            student.is_registered=0
            student.is_mobile_verified=0
            student.status=1
            student.created_on=datetime.now()
            student.updated_at=datetime.now()
            student.is_otp_expired=0
            student.is_id_card_pin_verified=0
            student.is_paid=0
            student.visit_status=0
            student.is_id_card_generated = 0
            student.id_card_attempts_left = 3

            student.save()
            return render(request,"student/index.html")
            # HttpResponseRedirect("/students")
        except Exception as e:
            print(e)
            response = {}
            response['error'] = True
            response['message'] = e
            res = HttpResponse("Registration Number already exists", content_type='application/json')
            res.status_code = 400
            return res

# add new student 
@login_required
def addNewStudentBasicDetails(request):
    all_institution             = SpOrganizations.objects.filter(status=1)
    countries                   = TblCountry.objects.all()
    Castcatogrys                 = TblClCasteCategory.objects.all()
    Collagesessions              = TblClCollegeSession.objects.all()
    previlagecatogrys            = TblClPrviliageCategory.objects.all()
    Incomecatogrys               = TblClIncomeCategory.objects.all()
    contact_types                = TblClContactTypes.objects.filter(status=1)
    context                      = {}
    context['college']           = 'college'
    context['all_institution']   = all_institution
    context['countries']         = countries
    context['Castcatogrys']      = Castcatogrys
    context['Collagesessions']   = Collagesessions
    context['previlagecatogrys'] = previlagecatogrys
    context['Incomecatogrys']    = Incomecatogrys
    context['contact_types']    = contact_types
    template                    = 'student/add-student-basic-details.html'
    response                    = {}
    error_response              = {}
    today      = date.today()
    today_date = today.strftime("%Y-%m-%d")
    if request.method == "POST":
        try:
            
            password = '123456'
            user_context = {}
            user_context['first_name']      = request.POST['first_name']
            user_context['middle_name']     = request.POST['middle_name']
            user_context['last_name']       = request.POST['last_name']
            user_context['official_email']  = request.POST['official_email']
            user_context['password']        = password   
            
             
            if request.POST['last_user_id'] != '':
                user = TblStudents.objects.get(id=request.POST['last_user_id'])
                if request.POST['previous_profile_image']:
                    profile_image = request.POST['previous_profile_image']
                    im = Image.open(BytesIO(base64.b64decode(profile_image.split(",")[1])))
                    im.save("media/document_files/student_photo_"+str(request.POST['last_user_id'])+".png", 'PNG')
                    filePath = "media/document_files/student_photo_"+str(request.POST['last_user_id'])+".png"
                    profile_image = filePath 
                else:
                    profile_image = user.profile_image 
                print(profile_image)    
                user.salutation     = request.POST['salutation']
                user.first_name     = request.POST['first_name']
                if request.POST['middle_name']:
                    user.middle_name    = request.POST['middle_name']
                user.profile_image  = profile_image
                if request.POST['last_name']:
                    user.last_name      = request.POST['last_name']
                if request.POST['official_email']:
                    user.email      = request.POST['official_email']
                user.father_name    = request.POST['father_name']
                user.mother_name    = request.POST['mother_name']
                user.blood_group    = request.POST['blood_group']
                user.password       = make_password(str(password))
                user.college_id     = request.POST['college_name']
                user.college_name   = getModelColumnById(SpOrganizations,request.POST['college_name'],'organization_name')
                user.address_hno       = request.POST['store_address_line_1']
                user.address_locality       = request.POST['store_address_line_2']
                user.country_id     = request.POST['store_country_id']
                user.state_id       = request.POST['store_state_id']
                user.district_id    = request.POST['store_district_id']
                user.tehsil_id      = request.POST['store_tehsil_id']
                user.per_address_hno       = request.POST['permanent_address_line_1']
                user.per_address_locality       = request.POST['permanent_address_line_2']
                user.per_country_id = request.POST['permanent_country_id']
                user.per_state_id   = request.POST['permanent_state_id']
                user.per_tehsil_id  = request.POST['permanent_tehsil_id']
                user.per_district_id = request.POST['permanent_district_id']
                user.cros_pincode   = request.POST['store_pincode']
                user.per_pincode    = request.POST['permanent_pincode']
                user.admission_session       = request.POST['collagesession']
                user.form_no       = request.POST['admission_form']
                user.save()
                last_user_id = request.POST['last_user_id']
                user_inserted = 1
            else:
               

                user = TblStudents()
                user.salutation     = request.POST['salutation']
                user.first_name     = request.POST['first_name']
                if request.POST['middle_name']:
                    user.middle_name    = request.POST['middle_name']
                
                if request.POST['last_name']:
                    user.last_name      = request.POST['last_name']
                if request.POST['official_email']:
                    user.email          = request.POST['official_email']
                user.father_name   = request.POST['father_name']
                user.mother_name   = request.POST['mother_name']
                user.blood_group   = request.POST['blood_group']
                user.college_id    = request.POST['college_name']
                user.college_name    = getModelColumnById(SpOrganizations,request.POST['college_name'],'organization_name')
                user.password       = make_password(str(password))
                user.address_hno       = request.POST['store_address_line_1']
                user.address_locality       = request.POST['store_address_line_2']
                user.country_id       = request.POST['store_country_id']
                user.state_id       = request.POST['store_state_id']
                user.district_id       = request.POST['store_district_id']
                user.tehsil_id       = request.POST['store_tehsil_id']
                user.per_country_id       = request.POST['permanent_country_id']
                user.per_state_id       = request.POST['permanent_state_id']
                user.per_tehsil_id       = request.POST['permanent_tehsil_id']
                user.per_district_id      = request.POST['permanent_district_id']
                user.per_address_hno       = request.POST['permanent_address_line_1']
                user.per_address_locality       = request.POST['permanent_address_line_2']
                user.cros_pincode       = request.POST['store_pincode']
                user.per_pincode       = request.POST['permanent_pincode']
                user.admission_session       = request.POST['collagesession']
                user.form_no       = request.POST['admission_form']
                user.semester_id       = 0
                user.is_registered       = 0
                user.is_mobile_verified  = 0
                user.is_otp_expired  = 0
                user.is_id_card_pin_verified  = 0
                user.is_id_card_generated  = 0
                user.id_card_attempts_left  = 0
                user.is_paid  = 0
                user.visit_status  = 0
                user.status       = 1
                user.created_on = datetime.strptime(str(today_date), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
                user.save()
                last_user_id = user.id

                if request.POST['previous_profile_image']:
                    profile_image = request.POST['previous_profile_image']
                    im = Image.open(BytesIO(base64.b64decode(profile_image.split(",")[1])))
                    im.save("media/document_files/student_photo_"+str(last_user_id)+".png", 'PNG')
                    filePath = "media/document_files/student_photo_"+str(last_user_id)+".png"
                    user.profile_image  = profile_image
                else:
                    user.profile_image = None
                user.save()    
                user_inserted = 0

            try:
                basic = TblClBasicDetails.objects.get(student_id=request.POST['last_user_id'])
            except TblClBasicDetails.DoesNotExist:
                basic = None
                    
            if basic:
                basic = TblClBasicDetails.objects.get(student_id=request.POST['last_user_id'])
                basic.student_id            = last_user_id
                basic.caste_category_id     = request.POST['cast_category']
                basic.caste_category        = getModelColumnById(TblClCasteCategory,request.POST['cast_category'],'caste_category')
                basic.privilage_category_id = request.POST['Privilege_category']
                basic.privilage_category    = getModelColumnById(TblClPrviliageCategory,request.POST['Privilege_category'],'prviliage_category')
                if request.POST['Income_category']:
                    basic.income_category_id = request.POST['Income_category']
                    basic.income_category    = getModelColumnById(TblClIncomeCategory,request.POST['Income_category'],'income_category')
                basic.gender                 = request.POST['user_gender']
                basic.dob                    = datetime.strptime(request.POST['date_of_birth'], '%d/%m/%Y').strftime('%Y-%m-%d')
                basic.blood_group            = request.POST['blood_group']
                basic.save()
            else:
                basic = TblClBasicDetails()
                basic.student_id            = last_user_id
                basic.caste_category_id     = request.POST['cast_category']
                basic.caste_category        = getModelColumnById(TblClCasteCategory,request.POST['cast_category'],'caste_category')
                basic.privilage_category_id = request.POST['Privilege_category']
                basic.privilage_category    = getModelColumnById(TblClPrviliageCategory,request.POST['Privilege_category'],'prviliage_category')
                if request.POST['Income_category']:
                    basic.income_category_id = request.POST['Income_category']
                    basic.income_category    = getModelColumnById(TblClIncomeCategory,request.POST['Income_category'],'income_category')
                basic.gender                = request.POST['user_gender']
                basic.dob                   = datetime.strptime(request.POST['date_of_birth'], '%d/%m/%Y').strftime('%Y-%m-%d')
                basic.blood_group           = request.POST['blood_group']
                basic.created_at            = datetime.strptime(str(today_date), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
                basic.save() 
            
            if request.POST['last_user_id'] != '':
                country_codes       = request.POST.getlist('country_code[]') 
                contact_types       = request.POST.getlist('contact_type[]') 
                contact_nos         = request.POST.getlist('contact_no[]')
                is_primary          = request.POST.getlist('primary_contact[]')
                TblClContactNumbers.objects.filter(student_id=request.POST['last_user_id']).delete()
                for id, val in enumerate(contact_nos):
                    user_contact_no         = TblClContactNumbers()
                    user_contact_no.student_id = last_user_id
                    if country_codes[id]!='':
                        user_contact_no.country_code = country_codes[id]
                    if contact_types[id]!='':    
                        user_contact_no.contact_type = contact_types[id]
                        user_contact_no.contact_type_name = getModelColumnById(TblClContactTypes,contact_types[id],'contact_type')
                    if contact_nos[id]!='':    
                        user_contact_no.contact_number = contact_nos[id]
                    if is_primary[id]!='':    
                        user_contact_no.is_primary = is_primary[id]
                    user_contact_no.status=1
                    user_contact_no.save()
                    if int(is_primary[id]) > 0:
                        user_data1 = TblStudents.objects.get(id=last_user_id)
                        user_data1.primary_contact_no = contact_nos[id]
                        user_data1.save()  
            else:
                country_codes       = request.POST.getlist('country_code[]') 
                contact_types       = request.POST.getlist('contact_type[]')
                contact_nos         = request.POST.getlist('contact_no[]')
                is_primary          = request.POST.getlist('primary_contact[]')

                for id, val in enumerate(contact_nos):
                    user_contact_no         = TblClContactNumbers()
                    user_contact_no.student_id = last_user_id
                    if country_codes[id]!='':
                        user_contact_no.country_code = country_codes[id]
                    if contact_types[id]!='':    
                        user_contact_no.contact_type = contact_types[id]
                        user_contact_no.contact_type_name = getModelColumnById(TblClContactTypes,contact_types[id],'contact_type')
                    if contact_nos[id]!='':    
                        user_contact_no.contact_number = contact_nos[id]
                    if is_primary[id]!='':    
                        user_contact_no.is_primary = is_primary[id]
                    user_contact_no.status=1
                    user_contact_no.save()
                    if int(is_primary[id]) > 0:
                        user_data = TblStudents.objects.get(id=last_user_id)
                        user_data.primary_contact_no = contact_nos[id]
                        user_data.save() 

            
            branches    = TblBranch.objects.filter(course_type_id=user.course_type_id)
            
            year_sem_list = []
            if user.branch_id:
                if getModelColumnById(TblBranch, user.branch_id, 'total_sem'):
                    year_sem    = getModelColumnById(TblBranch, user.branch_id, 'total_sem')
                else:
                    year_sem    = getModelColumnById(TblBranch, user.branch_id, 'total_year')

                for i in range(year_sem) :
                    index = int(i)+1
                    year_sem_list.append(index) 
            user        = TblStudents.objects.get(id=last_user_id)        
            context['courses']           = TblCourseTypes.objects.filter(college_id=user.college_id).order_by('course_type')
            context['branches']          = branches
            context['year_sem_list']     = year_sem_list
            context['sections']          = TblClSection.objects.filter().order_by('section_name')
            context['last_user_id']      = last_user_id   
            context['college_id']        = user.college_id 
            context['user']              = user
            template = 'student/add-student-biometric-details.html'
            return render(request, template, context)
        except Exception as e:
            response['error'] = True
            response['message'] = str(e)
            return HttpResponse(str(e))
    return render(request, template, context)

csrf_exempt
@login_required
def addStudentPhoto(request):
    context = {}
    return render(request,"student/add-student-photo.html",context)

# add student Biometric
@login_required
def addStudentBiometricDetails(request):
    if request.method == "POST":
        last_user_id = request.POST['last_user_id']
        user = TblStudents.objects.get(id=request.POST['last_user_id'])
        user.finger_iso_1        = request.POST['finger_iso_1']
        user.finger_iso_2        = request.POST['finger_iso_2']
        user.course_type_id      = request.POST['course_id']
        user.course_type_name    = getModelColumnById(TblCourseTypes, request.POST['course_id'], 'course_type')
        user.branch_id           = request.POST['branch_id']
        user.branch_name         = getModelColumnById(TblBranch, request.POST['branch_id'], 'branch')
        if getModelColumnById(TblBranch, request.POST['branch_id'], 'total_year'):
            user.year_id             = "year_"+request.POST['year_sem_id']
        else:    
            user.semester_id         = "sem_"+request.POST['year_sem_id']
        user.section_id          = request.POST['section_id']
        user.reg_no              = request.POST['roll_no']
        if request.POST['appeared_option'] ==  '1':
            user.sbat_id             = request.POST['sbat_id']
            user.sbat_percentage     = request.POST['percent']
        else:
            user.sbat_id             = None
            user.sbat_percentage     = None
        user.save()
        user_data = TblStudents.objects.get(id=last_user_id)
        user_data.is_registered = 1
        user_data.save()

        rooms = TblClRoom.objects.filter(college_id=user_data.college_id).values('id', 'room').order_by('id')

        context={}
        context['college']           = 'college'
        context['document_types']    = TblClDocumentTypes.objects.filter().order_by('document_name')
        context['document_lists']    = TblClDocuments.objects.filter(student_id=last_user_id).order_by('-id')
        context['document_list_count']  = TblClDocuments.objects.filter(student_id=last_user_id).count()
        context['last_user_id']      = last_user_id 
        context['college_id']        = user.college_id   
        context['rooms']             = rooms 
        return render(request,"student/add-student-documents.html",context)
    else:
        context={}
        context['college'] = 'college'
        return render(request,"student/add-student-biometric-details.html",context)

# add student Biometric
@login_required
def addStudentDocuments(request):
    template = 'student/add-student-documents.html'
    response = {}
    if request.method == "POST":
        try:
            last_user_id = request.POST['last_user_id']
            if TblClDocuments.objects.filter(student_id=last_user_id, document_name=getModelColumnById(TblClDocumentTypes, request.POST['document_type'], 'document_name')).exists():
                response['error']   = True
                response['message'] = "Document already addedd."
                return JsonResponse(response)
            else:
                document                  = TblClDocuments()
                document.student_id       = last_user_id
                document.document_name    = getModelColumnById(TblClDocumentTypes, request.POST['document_type'], 'document_name')
                document.ducument_number  = request.POST['document_number']
                document.is_uploaded      = 0
                document.created_by       = request.user.id
                document.save()

                #-----------------------------notify android block-------------------------------#
                user_id = 2514
                userFirebaseToken = getModelColumnById(SpUsers,user_id,'firebase_token')
                employee_name = getUserName(request.user.id)

                message_title = document.document_name+" document scan request."
                message_body =  document.document_name+" document scan request has been generated by "+employee_name
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

                context={}
                context['college']           = 'college'
                context['document_lists']    = TblClDocuments.objects.filter(student_id=last_user_id).order_by('-id')
                context['document_list_count']  = TblClDocuments.objects.filter(student_id=last_user_id).count()
                context['last_user_id']      = last_user_id    
                return render(request,"student/student-documents.html",context)
        except Exception as e:
            response['error']            = True
            response['message']          = e
            return HttpResponse(e)
    return render(request, template)

# add student document list
@login_required
def studentDocumentList(request):
    last_user_id        = request.POST['last_user_id']
    previous_list_count = request.POST['document_list_count']
    context={}
    context['college']              = 'college'
    context['last_user_id']         = last_user_id
    context['document_lists']       = TblClDocuments.objects.filter(student_id=last_user_id).order_by('-id') 
    context['document_list_count']  = document_list_count  = TblClDocuments.objects.filter(student_id=last_user_id).count()   
    
    if int(previous_list_count) == int(document_list_count):
        response                     = {}
        response['error']            = True
        return JsonResponse(response)
    else:
        context['is_difference']  = 0   
        return render(request,"student/student-documents.html",context)

@login_required
def addNewFolder(request):
    if request.method == "POST":
        response = {}
        response['student_id']   = request.POST['student_id']
        response['college_id']   = getModelColumnById(TblStudents, response['student_id'], 'college_id')
        response['room_id']      = request.POST['room_id']
        response['almira_id']    = request.POST['almira_id']
        response['rack_id']      = request.POST['rack_id']
        response['rack_name']    = getModelColumnById(TblClRack, request.POST['rack_id'], 'rack')
        
        student_name = getStudentName(request.POST['student_id'])
        reg_no = getModelColumnById(TblStudents, request.POST['student_id'], 'reg_no')
        reg_no = reg_no.replace("/", "_")
        
        if request.POST['is_auto'] == '1':
            if request.POST['auto_file_name'] == '1':
                file_name = student_name
            elif request.POST['auto_file_name'] == '2': 
                file_name = reg_no
            else:
                file_name = str(student_name)+'_'+str(reg_no)
        else:
            file_name = request.POST['file_name']   

        if TblClFileFolder.objects.filter(file_name=file_name, student_id=request.POST['student_id'], college_id=response['college_id'], room_id=request.POST['room_id'], almira_id=request.POST['almira_id'], rack_id=request.POST['rack_id']).exists():
            response['error']   = True
            response['message'] = "File Name already exists."
        else:    
            file_folder              = TblClFileFolder()
            file_folder.student_id   = request.POST['student_id']
            file_folder.college_id   = response['college_id']
            file_folder.room_id      = request.POST['room_id']
            file_folder.almira_id    = request.POST['almira_id']
            file_folder.rack_id      = request.POST['rack_id']
            if request.POST['is_auto'] == '1':   
                file_folder.file_name    = file_name
            else:
                file_folder.file_name    = file_name    
            file_folder.created_by   = request.user.id
            file_folder.save()

            college_name = getModelColumnById(SpOrganizations, file_folder.college_id, 'organization_name')
            room_name    = getModelColumnById(TblClRoom, file_folder.room_id, 'room')
            almira_name  = getModelColumnById(TblClAlmirah, file_folder.almira_id, 'almirah')
            rack_name    = getModelColumnById(TblClRack, file_folder.rack_id, 'rack')
            folder='media/documents/'+str(college_name)+'/'+str(room_name)+'/'+str(almira_name)+'/'+str(rack_name)+'/'+str(file_folder.file_name) 
            try:
                os.mkdir(folder)
            except OSError:
                pass
            else:
                pass
            
        return JsonResponse(response)
    else:    
        context = {}
        context['student_id']   = request.GET['student_id']
        context['room_id']      = request.GET['room_id']
        context['almira_id']    = request.GET['almira_id']
        context['rack_id']      = request.GET['rack_id']
        template = 'student/add-new-folder.html'
        return render(request,template,context)

@login_required
def addNewFile(request):
    context = {}
    template = 'student/create-new-file.html'
    return render(request,template,context)
    
# edit student Biometric
@login_required
def editStudentBiometricDetails(request):
    user        = TblStudents.objects.get(id=request.GET['last_user_id'])
    courses     = TblCourseTypes.objects.filter(college_id=user.college_id).order_by('course_type')
    branches    = TblBranch.objects.filter(course_type_id=user.course_type_id)
    
    year_sem_list = []
    if getModelColumnById(TblBranch, user.branch_id, 'total_sem'):
        year_sem    = getModelColumnById(TblBranch, user.branch_id, 'total_sem')
    else:
        year_sem    = getModelColumnById(TblBranch, user.branch_id, 'total_year')

    for i in range(year_sem) :
        index = int(i)+1
        year_sem_list.append(index)  

    context                      = {}
    context['college']           = 'college'
    context['courses']           = courses
    context['branches']          = branches
    context['year_sem_list']     = year_sem_list
    context['sections']          = TblClSection.objects.filter().order_by('section_name')
    context['last_user_id']      = request.GET['last_user_id']
    context['user']              = user
    context['college_id']        = user.college_id
    template                     = 'student/add-student-biometric-details.html'
    return render(request, template, context) 


@login_required
def editNewStudentBasicDetails(request):
    student_basic                = TblStudents.objects.get(id=request.GET['last_user_id'])
    try:
        basic                    = TblClBasicDetails.objects.get(student_id=request.GET['last_user_id'])
    except TblClBasicDetails.DoesNotExist:
        basic                    = None
    
    all_institution              = SpOrganizations.objects.filter(status=1)
    countries                    = TblCountry.objects.all()
    Castcatogrys                 = TblClCasteCategory.objects.all()
    Collagesessions              = TblClCollegeSession.objects.all()
    previlagecatogrys            = TblClPrviliageCategory.objects.all()
    Incomecatogrys               = TblClIncomeCategory.objects.all()
    try:
        contact_types            = TblClContactTypes.objects.filter(status=1)
    except TblClContactTypes.DoesNotExist:
        contact_types            = None
    
    store_states                = TblStates.objects.filter(country_id=student_basic.country_id)
    store_district               = TblNewDistrict.objects.filter(state_id=student_basic.state_id)
    store_tehsil                = TblNewTehsil.objects.filter(district_id=student_basic.district_id)
    try:
        user_contact_details    = TblClContactNumbers.objects.filter(student_id=request.GET['last_user_id'])
    except TblClContactNumbers.DoesNotExist:
        user_contact_details    = None
    
    permanent_states            = TblStates.objects.filter(country_id=student_basic.per_country_id)
    permanent_district          = TblNewDistrict.objects.filter(state_id=student_basic.per_state_id)
    permanent_tehsil            = TblNewTehsil.objects.filter(district_id=student_basic.per_district_id)
    baseurl = settings.BASE_URL
    context                      = {}
    context['baseurl']           = baseurl
    context['college']           = 'college'
    context['all_institution']   = all_institution
    context['countries']         = countries
    context['Castcatogrys']      = Castcatogrys
    context['Collagesessions']   = Collagesessions
    context['previlagecatogrys'] = previlagecatogrys
    context['Incomecatogrys']    = Incomecatogrys
    context['contact_types']     = contact_types
    context['last_user_id']      = request.GET['last_user_id']
    context['student_basic']              = student_basic
    context['basic']             = basic
    context['store_states']      = store_states
    context['store_district']    = store_district
    context['store_tehsil']      = store_tehsil
    context['permanent_states']  = permanent_states
    context['permanent_district'] = permanent_district
    context['permanent_tehsil']   = permanent_tehsil
    context['user_contact_details']   = user_contact_details
    template                     = 'student/add-student-basic-details.html'
    return render(request, template, context) 
@login_required
def filterByOrganization(request):
    response = {}
    filter_role_option = ''
    branch_option = ''
    if request.method == "POST":
        if request.POST.get('college_name'):
            for org_id in request.POST.get('college_name'):
                for role in SpRoles.objects.filter(organization_id=org_id).filter(role_name__regex = r'%s'%'[s|S]tudent'):
                    filter_role_option += '<option value="'+str(role.id)+'">'+str(role.role_name)+'</option>'
                for role in TblBranch.objects.filter(college_id=org_id):
                    branch_option += '<option value="'+str(role.id)+'">'+str(role.abbr)+'</option>'
            response['branch_option'] = branch_option
            response['filter_role_option'] = filter_role_option
            return JsonResponse(response)
        else:
            for role in SpRoles.objects.filter(organization_id=request.POST['filter_org_id']):
                    filter_role_option += '<option value="'+str(role.id)+'">'+str(role.role_name)+'</option>'
            for role in TblBranch.objects.filter(college_id=request.POST['filter_org_id']):
                    branch_option += '<option value="'+str(role.id)+'">'+str(role.abbr)+'</option>'
            response['branch_option'] = branch_option
            response['filter_role_option'] = filter_role_option
            return JsonResponse(response)

@login_required
def IdCardEditor(request):
    template = 'student/id-card-editor.html'
    return render(request, template)

@login_required
def ImageGrabCut(request):
    #Load the Image
    rec_img = request.POST.get('img_data')
    imgo = readb64(rec_img)
    height, width = imgo.shape[:2]
    mask = np.zeros(imgo.shape[:2],np.uint8)
    bgdModel = np.zeros((1,65),np.float64)
    fgdModel = np.zeros((1,65),np.float64)
    rect = (1,1,width,height)
    cv2.grabCut(imgo,mask,rect,bgdModel,fgdModel,5,cv2.GC_INIT_WITH_RECT)
    mask = np.where((mask==2)|(mask==0),0,1).astype('uint8')
    img1 = imgo*mask[:,:,np.newaxis]
    background = imgo - img1
    background[np.where((background > [0,0,0]).all(axis = 2))] =[255,255,255]
    final = background + img1
    filename = 'final.png'
    cv2.imwrite(filename, final)
    img = Image.open(filename)
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    reg_no = request.POST['reg_no']
    reg_url = reg_no.replace("/", "-")
    reg_url += reg_url+str(datetime.now())
    img.save("./media/img-data/"+reg_url+".png", "PNG")
    grabcut_parent_path = "./media/img-data/"+reg_url+".png"

    response = HttpResponse(content_type="image/png")
    context = {}
    context['grabcut_image'] = grabcut_parent_path
    context['message'] = "Success"
    context['response_status'] = 200
    template = 'student/id-card-preview.html'
    return JsonResponse(context)

@login_required
def QRGeneration(request):
    response = {}
    reg_no = request.POST.get('reg_no')
    blood_group = request.POST.get('blood_group')
    address = request.POST.get('address')
    issue_date = request.POST.get("issue_date")
    expiry_date = request.POST.get("expiry_date")

    if TblStudents.objects.filter(reg_no = reg_no).exists() == False:
        response['message']         = "No Registration Number found"
        response['response_status'] = 404
        return JsonResponse(response)
    else:
        id_counter = TblStudents.objects.filter(reg_no = reg_no).values('id_card_attempts_left')[0]['id_card_attempts_left']

    if TblStudents.objects.filter(reg_no = reg_no, is_id_card_generated = 1).exists() and id_counter == 0:
        response['message']         = "No Attempts left! Please contact Admin."
        response['response_status'] = 403
        return JsonResponse(response)

    elif TblStudents.objects.filter(reg_no = reg_no).exists() and id_counter == 3:
        student_info = TblStudents.objects.filter(reg_no = reg_no)

        first_name = student_info[0].first_name
        last_name = ""
        if student_info[0].middle_name is None and student_info[0].last_name is not None:
            last_name += student_info[0].last_name
        elif student_info[0].middle_name is not None and student_info[0].last_name is not None:
            last_name += student_info[0].middle_name + " " + student_info[0].last_name

        branch_name = TblBranch.objects.filter(id = student_info[0].branch_id).values('abbr')[0]['abbr']
        primary_no = student_info[0].primary_contact_no
        college_info = TblColleges.objects.filter(id = student_info[0].college_id)
        for info in college_info:
            college_logo = info.college_logo
            college_website = info.college_website
            college_phone = info.college_contacts
        input_data = {"reg_no": reg_no, "name": first_name+" "+last_name, "address": address, "primary_no": primary_no, "blood_group": blood_group, "college_contact": college_phone }

        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(input_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        reg_url = reg_no.replace("/", "-")

        qr_parent_path = "./media/qr-code-image/"
        qr_url = qr_parent_path+reg_url+".png"
        img.save(qr_url)

        if address == "":
            address = "-"
        TblStudents.objects.filter(reg_no = reg_no).update(blood_group = blood_group)
        response['QR']              = qr_url
        response['blood_group']     = blood_group
        response['address']         = address
        response['first_name']      = first_name
        response['last_name']       = last_name
        response['branch_name']     = branch_name
        response['reg_no']          = reg_no
        response['contact']         = primary_no
        response['college_logo']    = college_logo
        response['college_website'] = college_website.split("www.")[1]
        response['issue_date']      = issue_date
        response['expiry_date']     = expiry_date
        response['message']         = "Success"
        response['response_status'] = 200
        template = 'student/id-card-preview.html'
        return render(request, template, response)
    elif TblStudents.objects.filter(reg_no = reg_no).exists() and id_counter != 3 and id_counter > 0:
        response['message']         = "ID Card already generated."
        response['sub_message']     = str(id_counter) + " Download attempts left for Registration Number: "+reg_no
        response['response_status'] = 403
        return JsonResponse(response)
    else:
        response['message']         = "No Registration Number found"
        response['response_status'] = 404
        return JsonResponse(response)


@login_required
def IDCardSave(request):
    reg_no = request.POST['reg_no']
    id_card = request.POST['id_card']
    reg_url = reg_no.replace("/", "-")
    context = {}
    id_counter = TblStudents.objects.filter(reg_no = reg_no).values('id_card_attempts_left')[0]['id_card_attempts_left']

    if id_counter > 0:
        im = Image.open(BytesIO(base64.b64decode(id_card.split(",")[1])))
        im.save("media/id-cards/" + str(reg_url) + ".png", 'PNG')
        filePath = "media/id-cards/" + reg_url + ".png"
        # id_counter = TblStudents.objects.filter(reg_no = reg_no).values('id_card_attempts_left')[0]['id_card_attempts_left']
        TblStudents.objects.filter(reg_no = reg_no).update(is_id_card_generated = 1, id_card_created_at = datetime.now(), id_card_link = filePath, id_card_attempts_left = id_counter - 1)
        context['message'] = "Success"
        context['response_status'] = 200
    else:
        context['id_counter'] = 0
        context['message'] = "No Attempts left! Please contact Admin."
        context['response_status'] = 403
    return JsonResponse(context)

@login_required
def IDCardDownload(request):
    reg_no = request.POST['reg_no']
    id_counter = TblStudents.objects.filter(reg_no = reg_no).values("id_card_attempts_left")[0]['id_card_attempts_left']
    response = {}
    if id_counter > 0:
        id_url = TblStudents.objects.filter(reg_no = reg_no).values("id_card_link")[0]['id_card_link']
        TblStudents.objects.filter(reg_no = reg_no).update(is_id_card_generated = 1, id_card_created_at = datetime.now(), id_card_attempts_left = id_counter - 1)
        response['id_url'] = id_url
        response['id_counter'] = id_counter - 1
        response['message'] = "Success"
        response['response_status'] = "200"
    else:
        response['id_counter'] = 0
        response['message'] = "No Attempts left! Please contact Admin."
        response['response_status'] = 403
    return JsonResponse(response)


# @login_required
# def QRReader(request):
#     from pyzbar.pyzbar import decode
#     import ast
#     img = "./static/id_card.jpg"
#     my_QR = decode(Image.open(img))
#     qr_data = (my_QR[0].data).decode("utf-8")
#     qr_data = ast.literal_eval(qr_data)
#     reg_no = qr_data['reg_no']
#     print("QR From Image: ", reg_no)

@login_required
def getMasterDetails(request):
    context     = {}
    id          = request.POST['id']
    type        = request.POST['type']
    college_id  = request.POST['college_id']
    last_user_id  = request.POST['last_user_id']
    master_name = request.POST['master_name']
    if type == 'room_list':
        context['master']       = 'room'
        context['rooms']        = TblClRoom.objects.filter(college_id=college_id)
        context['college_id']   = college_id
        context['master_name']  = master_name
        context['last_user_id']  = last_user_id
    elif type == 'room':
        context['master']       = 'almira'
        context['almiras']      = TblClAlmirah.objects.filter(room_id=id)
        context['college_id']   = college_id
        context['master_name']  = master_name
        context['last_user_id']  = last_user_id
    elif type == 'almira':
        context['master']       = 'rack'
        context['racks']      = TblClRack.objects.filter(almira_id=id)
        context['college_id']   = college_id
        context['room_id']      = getModelColumnById(TblClAlmirah, id, 'room_id')
        context['room_name']    = getModelColumnById(TblClAlmirah, id, 'room_name')
        context['almira_id']    = id
        context['master_name']  = getModelColumnById(TblClRoom, context['room_id'], 'room')  
        context['almira_name']  = getModelColumnById(TblClAlmirah, id, 'almirah')
        context['last_user_id']  = last_user_id
    elif type == 'rack':
        context['master']       = 'file'
        
        context['college_id']   = college_id
        context['last_user_id'] = last_user_id
        context['rack_id']      = id
        context['rack_name']    = getModelColumnById(TblClRack, id, 'rack')
        context['room_id']      = getModelColumnById(TblClRack, id, 'room_id')
        context['room_name']    = getModelColumnById(TblClRack, id, 'room_name')
        context['almira_id']    = getModelColumnById(TblClRack, id, 'almira_id') 
        context['almira_name']  = getModelColumnById(TblClRack, id, 'almira_name') 
        context['files']        = TblClFileFolder.objects.filter(college_id=college_id, student_id=last_user_id, room_id=context['room_id'], almira_id=context['almira_id'], rack_id=context['rack_id'])   

        context['master_name']  = '' 
    elif type == 'file':
        context['master']       = 'folder_files'
        
        context['college_id']   = college_id
        context['last_user_id'] = last_user_id
        context['file_id']      = id
        context['file_name']    = getModelColumnById(TblClFileFolder, id, 'file_name')
        context['room_id']      = getModelColumnById(TblClFileFolder, id, 'room_id')
        context['room_name']    = getModelColumnById(TblClRoom, context['room_id'], 'room')
        context['almira_id']    = getModelColumnById(TblClFileFolder, id, 'almira_id') 
        context['almira_name']  = getModelColumnById(TblClAlmirah, context['almira_id'], 'almirah') 
        context['rack_id']      = getModelColumnById(TblClFileFolder, id, 'rack_id')
        context['rack_name']    = getModelColumnById(TblClRack, context['rack_id'], 'rack')
        context['folder_files'] = TblClFolderFiles.objects.filter(college_id=college_id, student_id=last_user_id, room_id=context['room_id'], almira_id=context['almira_id'], rack_id=context['rack_id'])    

        context['master_name']  = ''     
    baseurl = settings.BASE_URL
    
    context['baseurl']           = baseurl
    template                     = 'student/master-details.html'
    return render(request, template, context)