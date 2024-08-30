import sys
import os
import json
from django.core import serializers
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password
from django.apps import apps
from ..models import *
from django.db.models import Q
from utils import getConfigurationResult,getModelColumnById
from datetime import datetime
from datetime import timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from django.core.files.storage import FileSystemStorage
from io import BytesIO
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.conf import settings
from ..decorators import *

import base64
from PIL import Image


# Create your views here.


def firebase_messaging_sw_js(request):
    filename = '/static/js/firebase-messaging-sw.js'
    jsfile = open(str(settings.BASE_DIR) + filename, 'rb')
    response = HttpResponse(content=jsfile)
    response['Content-Type'] = 'text/javascript'
    response['Content-Disposition'] = 'attachment; filename="%s"' % (str(settings.BASE_DIR) + filename)
    return response

def opencv_js(request):
    filename = '/static/js/opencv.js'
    jsfile = open(str(settings.BASE_DIR) + filename, 'rb')
    response = HttpResponse(content=jsfile)
    response['Content-Type'] = 'text/javascript'
    response['Content-Disposition'] = 'attachment; filename="%s"' % (str(settings.BASE_DIR) + filename)
    return response

def haarcascade_frontalface_default_xml(request):
    filename = '/static/js/haarcascade_frontalface_default.xml'
    jsfile = open(str(settings.BASE_DIR) + filename, 'rb')
    response = HttpResponse(content=jsfile)
    response['Content-Type'] = 'text/javascript'
    response['Content-Disposition'] = 'attachment; filename="%s"' % (str(settings.BASE_DIR) + filename)
    return response

#Home View
#@login_required
def idCardDesign(request):
    context = {}
    context['page_title']               = "ID Card Design" 
    template = 'profile/id-card.html'
    
    return render(request, template, context)
#Home View
@login_required
def index(request):
    context = {}
    condition = ''    
    page = request.GET.get('page')
    current_date = datetime.now().strftime('%Y-%m-%d')    
    activity_list = SpActivityLogs.objects.order_by('-created_at') 
    paginator = Paginator(activity_list, getConfigurationResult('page_limit'))
    if request.user.role_id == 0:
        context['first_college'] = first_college = SpOrganizations.objects.all().first()
        branches = TblBranch.objects.filter(college_id=first_college.id).values('id','branch','abbr')
        for branch in branches:
            condition += " AND date(created_at)='"+current_date+"' and student_id IN (SELECT id from tbl_students where branch_id='"+str(branch['id'])+"')"
            total_students = TblStudents.objects.raw("""SELECT id,COUNT(id) as total_students FROM tbl_students WHERE is_registered = 1 AND status=1 AND branch_id=%s""",[branch['id']])[0]
            branch['total_students'] = total_students.total_students
            total_attendance = TblAttendance.objects.raw("""SELECT id, COUNT(tbl_attendance.id) as total_attendance FROM tbl_attendance WHERE 1 {condition}""".format(condition=condition))[0]
            branch['total_attendance'] = total_attendance.total_attendance
        context['branches'] = branches    
        context["college_names"] = SpOrganizations.objects.raw("""SELECT id,organization_name  FROM sp_organizations WHERE status=1 """)
    else:
        context['first_college'] = first_college = SpOrganizations.objects.filter(id=request.user.organization_id).first()
        branches = TblBranch.objects.filter(college_id=first_college.id).values('id','branch','abbr')
        for branch in branches:
            condition += " AND date(created_at)='"+current_date+"' and student_id IN (SELECT id from tbl_students where branch_id='"+str(branch['id'])+"')"
            total_students = TblStudents.objects.raw("""SELECT id,COUNT(id) as total_students FROM tbl_students WHERE is_registered = 1 AND status=1 AND branch_id=%s""",[branch['id']])[0]
            branch['total_students'] = total_students.total_students
            total_attendance = TblAttendance.objects.raw("""SELECT id, COUNT(tbl_attendance.id) as total_attendance FROM tbl_attendance WHERE 1 {condition}""".format(condition=condition))[0]   
            branch['total_attendance'] = total_attendance.total_attendance
        context['branches'] = branches    
        context["college_names"] = SpOrganizations.objects.raw("""SELECT id,organization_name  FROM sp_organizations WHERE id=%s """,[request.user.organization_id])

    try:
        activity_list = paginator.page(page)
    except PageNotAnInteger:
        activity_list = paginator.page(1)
    except EmptyPage:
        activity_list = paginator.page(paginator.num_pages)
    if page is not None:
           page = page
    else:
           page = 1

    context['page_title']               = "Dashboard"
    context['activity_list']            = activity_list    
    template = 'profile/home.html'
    
    return render(request, template, context)


#Home View
@login_required
def manageProfile(request):
    if request.method == "GET":
        context = {}
        condition = ''    
        page = request.GET.get('page')
        current_date = datetime.now().strftime('%Y-%m-%d')    
        activity_list = SpActivityLogs.objects.order_by('-created_at') 

        paginator = Paginator(activity_list, getConfigurationResult('page_limit'))
        context['first_college'] = first_college = SpOrganizations.objects.all().first()
        branches = TblBranch.objects.filter(college_id=first_college.id).values('id','branch','abbr')    
        
        
        for branch in branches:
            condition += " AND date(created_at)='"+current_date+"' and student_id IN (SELECT id from tbl_students where branch_id='"+str(branch['id'])+"')"
            total_students = TblStudents.objects.raw("""SELECT id,COUNT(id) as total_students FROM tbl_students WHERE is_registered = 1 AND status=1 AND branch_id=%s""",[branch['id']])[0]
            branch['total_students'] = total_students.total_students
            total_attendance = TblAttendance.objects.raw("""SELECT id, COUNT(tbl_attendance.id) as total_attendance FROM tbl_attendance WHERE 1 {condition}""".format(condition=condition))[0]   
            branch['total_attendance'] = total_attendance.total_attendance
        context['branches'] = branches
        
        context["college_names"] = SpOrganizations.objects.raw("""SELECT id,organization_name  FROM sp_organizations WHERE status=1 """)
            
        try:
            activity_list = paginator.page(page)
        except PageNotAnInteger:
            activity_list = paginator.page(1)
        except EmptyPage:
            activity_list = paginator.page(paginator.num_pages)
        if page is not None:
            page = page
        else:
            page = 1

        context['page_title']               = "Blank"
        context['activity_list']            = activity_list    
        template = 'profile/blank.html'
        
        return render(request, template, context)
    else:
        response = {}
        response['flag'] = False
        response['message'] = "Method Not Allowed"

        return JsonResponse(response)

@login_required
def updateProfile(request):
    if request.method == "POST":   
        if request.POST['firstName'] and request.POST['lastName'] and request.POST['email']:     
            SpUsers.objects.filter(id=request.user.id).update(first_name=request.POST['firstName'],middle_name=request.POST['middleName'] ,last_name=request.POST['lastName'],official_email=request.POST['email'])

        response = {}
        response['flag'] = True
        response['data'] = "Profile Updated Successfully"
        return JsonResponse(response)
    else:
        response['flag'] = False
        response['data'] = "Method Not Allowed"
        return JsonResponse(response)

@login_required
def updateConfiguration(request):
    response = {}
    if request.method == "POST":
        if request.FILES['logo']:    
            storage = FileSystemStorage()           
            store_image_name = request.FILES['logo'].name
            temp = store_image_name.split('.')
            store_image_name = 'logo_'+str(request.FILES['logo'])                    
            store_image = storage.save(store_image_name, request.FILES['logo'])
            store_image = storage.url(store_image)
            store_image = store_image.split('media/')[1]
            store_image = "media/logo/"+store_image
            Configuration.objects.filter(id=request.user.id).update(logo=store_image)

        if request.FILES['profileImage']:
            storage = FileSystemStorage()            
            store_image_name = request.FILES['profileImage'].name
            temp = store_image_name.split('.')
            store_image_name = 'profile_'+str(request.FILES['profileImage'])                    
            store_image = storage.save(store_image_name, request.FILES['profileImage'])
            store_image = storage.url(store_image)
            store_image = store_image.split('media/')[1]
            print(store_image)
            store_image = "media/profileImage/"+store_image
            SpUsers.objects.filter(id=request.user.id).update(profile_image=store_image)
            
        if request.POST['pageLimit']:
            Configuration.objects.filter(id=request.user.id).update(page_limit=request.POST['pageLimit'])
        if request.POST['institutionName']:
            Configuration.objects.filter(id=request.user.id).update(org_name=request.POST['institutionName'])
        if request.POST['institutionCode']:
            Configuration.objects.filter(id=request.user.id).update(org_code=request.POST['institutionCode'])

        
        response['flag'] = True
        response['data'] = "Configuration Updated Successfully"
        return JsonResponse(response)
    else:
        response['flag'] = False
        response['data'] = "Method Not Allowed"
        return JsonResponse(response)


@login_required
def ajaxFilter(request):
    context = {}       
    filterDate = datetime.strptime(request.POST['date'], "%d/%m/%Y").strftime('%Y-%m-%d')
    current_date = datetime.now().strftime('%Y-%m-%d')    
    if 'filter_org' in request.POST and request.POST['filter_org'] != "":
        branches = TblBranch.objects.filter(college_id=request.POST['filter_org']).values('id','branch','abbr')
    else:
        branches = TblBranch.objects.filter().values('id','branch','abbr')

    for branch in branches:
        condition = "" 

        if 'date' in request.POST and request.POST['date'] != "":
            date = datetime.strptime(request.POST['date'], "%d/%m/%Y").strftime('%Y-%m-%d')
            condition += " and date(created_at)='"+date+"'"

        condition += " and student_id in (SELECT id FROM tbl_students WHERE branch_id="+str(branch['id'])+")"        
        branch['total_students'] = TblStudents.objects.raw("""SELECT id,COUNT(id) as total_students FROM tbl_students WHERE is_registered = 1 AND status=1 AND branch_id=%s""",[str(branch['id'])])[0].total_students
        branch['total_attendance'] = TblAttendance.objects.raw(""" SELECT id, COUNT(id) as total_attendance FROM tbl_attendance WHERE 1 {condition}""".format(condition=condition))[0].total_attendance
    
    context['branches'] = branches    
    template = 'profile/filter-graph.html'    
    return render(request, template, context)

@login_required
def changePassword(request):
    if request.method == "POST":
        response = {}
        if 'old_password' not in request.POST :
            response['flag'] = False
            response['message'] = "Please enter old password"
        elif 'new_password' not in request.POST :
            response['flag'] = False
            response['message'] = "Please enter new password"
        else:
            if check_password(request.POST['old_password'],request.user.password):
                SpUsers.objects.filter(id=request.user.id).update(password=make_password(request.POST['new_password']), plain_password=request.POST['new_password'])
                response['flag'] = True
                response['message'] = "Password Changed Successfully"
            else:
                response['flag'] = False
                response['message'] = "Incorrect Old Password"

        return JsonResponse(response)
    else:
        context = {}
        template = 'profile/change-password.html'
        return render(request,template,context)



