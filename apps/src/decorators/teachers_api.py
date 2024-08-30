from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,redirect
from ..models import *
from utils import *

def validatePOST(view_func):
    def wrapper_func(request, *args, **kwargs):
        response = {}
        if  request.method == "POST" :
            return view_func(request, *args, **kwargs)
        else:
            response['message'] = "Method Not Allowed"
            return Response(response,status=405)

    return wrapper_func
  
def validateGET(view_func):
    def wrapper_func(request, *args, **kwargs):
        response = {}
        if  request.method == "GET" :
            return view_func(request, *args, **kwargs)
        else:
            response['message'] = "Method Not Allowed"
            return Response(response,status=405)

    return wrapper_func

def validate_teachers_api(view_func):
    def wrapper_func(request, *args, **kwargs):
        response = {}
        if 'Authorization' in request.headers and request.headers['Authorization'] != "" :
            api_token = request.headers['Authorization']
            if SpUsers.objects.filter(api_token=api_token.split(" ")[1]).exists() :
                return view_func(request, *args, **kwargs)
            else:
                response['message'] = "Invalid Authorization token"
                
                return Response(response,status=401)
        else:
            response['message'] = "Authorization token is missing"
            return Response(response,status=404)

    return wrapper_func