import math
from re import T, search
import time
from django.contrib.auth import authenticate
from datetime import datetime, date
from django.core.files.storage import FileSystemStorage
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
@api_view(['POST'])
@validate_teachers_api
def entranceRegistration(request):
    if request.data.get("student_name") == '':  
        return Response({'message': 'Please provide Student Name', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
    if request.data.get("contact") == '':
        return Response({'message': 'Please provide Contact Number', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)

    if request.data.get("class_standard") == '':
        return Response({'message': 'Please provide Class of this student', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)

    
    # if request.data.get("course_id") == '':
    #     return Response({'message': 'Please provide Course Name', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)

    if not TblEntranceRegistration.objects.filter(contact = request.data.get("contact")).exists():
        registration                    = TblEntranceRegistration()
        registration.class_passed       = int(request.data.get("class_standard"))
        if request.data.get("class_standard") == "10":
            high_school_students = TblEntranceRegistration.objects.filter(class_passed = 10).count()
            registration.registration_id    = "SBAT/" + str(date.today().year) + "/HS/" + str(high_school_students+101)
        elif request.data.get("class_standard") == "12":
            inter_students = TblEntranceRegistration.objects.filter(class_passed = 12).count()
            registration.registration_id    = "SBAT/" + str(date.today().year) + "/IN/" + str(inter_students+101)

        registration.student_name       = request.data.get("student_name")
        registration.contact            = request.data.get("contact")
        registration.email_address      = request.data.get("email")

        registration.address_hno        = request.data.get("address_hno")
        registration.address_locality   = request.data.get("address_locality")
        registration.village_id         = request.data.get("village_id")

        if request.data.get("village_id"):
            registration.address_village     = getModelColumnById(TblNewVillage, request.data.get("village_id"), "village_name")
        
        registration.tehsil_id          = request.data.get("tehsil_id")
        if request.data.get("tehsil_id"):
            registration.address_tehsil     = getModelColumnById(TblNewTehsil, request.data.get("tehsil_id"), "tehsil_name")

        registration.district_id        = request.data.get("district_id")
        if request.data.get("district_id"):
            registration.address_district   = getModelColumnById(TblNewDistrict, request.data.get("district_id"), "district_name")

        registration.state_id           = request.data.get("state_id")
        if request.data.get("state_id"):
            registration.address_state      = getModelColumnById(TblStates, request.data.get("state_id"), "state_name")

        registration.course_id          = request.data.get("course_id")
        if request.data.get("course_id"):
            registration.course_name        = getModelColumnById(TblBranch, request.data.get("course_id"), "branch")
        registration.registered_by      = request.user.id

        if bool(request.FILES.get('student_image', False)) == True:
            student_image                = request.FILES['student_image']
            folder                      = 'media/entrance_student_images/'
            storage                     = FileSystemStorage(location=folder)
            timestamp                   = int(time.time())
            session_record_filename     = student_image.name
            temp                        = session_record_filename.split('.')
            session_record_filename     = 'entrance/student_image'+str(timestamp)+"."+temp[(len(temp) - 1)]
            student_img_file             = storage.save(session_record_filename, student_image)
            student_img                  = storage.url(student_img_file)

            student_img = student_img.split('media/')[1]
            student_img = "/"+folder+student_img
            registration.photo   = student_img

        registration.is_student = request.data.get("is_student")
        registration.referenced_by_name = request.data.get("referenced_by_name")

        if request.data.get("is_student") == "0" and request.data.get("referenced_by_name") != "":

            if request.data.get("referenced_by_branch_id") != "":
                registration.referenced_by_branch_id    = request.data.get("referenced_by_branch_id")
            if request.data.get("referenced_by_branch_id") != "":
                registration.referenced_by_branch_name  = getModelColumnById(TblBranch, request.data.get("referenced_by_branch_id"), 'branch')
            registration.referenced_by_year         = request.data.get("referenced_by_year")

        registration.save()

        return JsonResponse( {"message":"Successfully registered the student"}, status = HTTP_200_OK )
    else:
        return JsonResponse( {"message":"Mobile number already registered"}, status = HTTP_400_BAD_REQUEST )
