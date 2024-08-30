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
baseurl = settings.BASE_URL

@csrf_exempt
@api_view(['POST'])
def studentDocumentList(request):
    if request.method == 'POST':
        document_list   = TblClDocuments.objects.filter(is_uploaded=0).values('id', 'student_id', 'document_name', 'ducument_number', 'document_path').order_by('-id')
        for document in document_list:
            if document['document_path']:
                document['document_path']   = baseurl+'/'+str(document['document_path'])
            else:
                document['document_path']   = ''    
            document['student_name']        = getStudentName(document['student_id'])
            document['student_contact_no']  = getModelColumnById(TblStudents, document['student_id'], 'primary_contact_no')
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
def uploadDocument(request):
    if request.method == 'POST':
        if request.data.get("student_id")is None or request.data.get("student_id") == '':
            return Response({'message': 'Student id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
        if request.data.get("document_id")is None or request.data.get("document_id") == '':
            return Response({'message': 'Document id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
        if bool(request.FILES.get('document_file', False)) == True:
            document_file = request.FILES['document_file']
            reg_no = getModelColumnById(TblStudents, request.data.get("student_id"), 'reg_no')
            reg_no = reg_no.replace("/", "_")
            folder='media/document_files/'+str(reg_no) 
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
            document_file_name = str(getModelColumnById(TblClDocuments, request.data.get("document_id"), 'document_name')) + "_"+str(timestamp)+"."+temp[(len(temp) - 1)]
            
            uploaded_document_file = storage.save(document_file_name, document_file)
            
            document_url = folder+document_file_name

            document                  = TblClDocuments.objects.get(id=request.data.get("document_id"),student_id=request.data.get("student_id"))
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