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
def candidateList(request):
    if request.method == 'POST':
        if request.data.get("page_limit") is None or request.data.get("page_limit") == '':
            return Response({'message': 'Page Limit field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 

        if request.data.get("status") is None or request.data.get("status") == '':
            return Response({'message': 'Status field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 

        page_limit  = int(request.data.get("page_limit"))*10
        offset      = int(page_limit)-10
        page_limit  = 10
        status = request.data.get("status")
        candidates   = TblSsCandidates.objects.filter(status=status)
        if request.data.get("search_key"):
            candidates = candidates.filter(candidate_name__icontains = request.data.get("search_key"))

        candidates = candidates.values().order_by('-id')[offset:offset+page_limit]

        for candidate in candidates:
            if candidate['candidate_image'] is None:
                candidate['candidate_image'] = baseurl + '/static/img/svg/user_NEW.svg'
            if candidate['resume'] is None:
                candidate['resume'] = baseurl + '/media/candidate-resume/sample_resume.pdf'
        context = {}
        context['candidates']    = candidates
        context['message']          = "Success"
        context['response_code']  = HTTP_200_OK
        return Response(context, status=HTTP_200_OK)
    else:
        return Response({"message":"Method Not Allowed"}, status=HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(['POST'])
def updateCandidateStatus(request):
    if request.method == 'POST':
        if request.data.get("candidate_id") is None or request.data.get("candidate_id") == '':
            return Response({'message': 'Candidate ID field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 

        if request.data.get("status") is None or request.data.get("status") == '':
            return Response({'message': 'Status field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 

        candidate_id = request.data.get("candidate_id")
        status = request.data.get("status")
        if not TblSsCandidates.objects.filter(id = candidate_id).exists():
            return Response({"message":"Candidate ID does not exists"}, status=HTTP_404_NOT_FOUND)
        else:
            TblSsCandidates.objects.filter(id = candidate_id).update(status=status)

        context = {}
        context['message']        = "Success"
        context['response_code']  = HTTP_200_OK
        return Response(context, status=HTTP_200_OK)

    else:
        return Response({"message":"Method Not Allowed"}, status=HTTP_405_METHOD_NOT_ALLOWED)

