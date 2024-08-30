import json
import time
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
from datetime import datetime
from datetime import timedelta
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    user_type = request.data.get("user_type")
    if not user_type:
        return Response({'message': 'User type field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)
    if user_type == '0':
        user_details = SpUsers.objects.filter(status=1, user_type=2, emp_sap_id=request.data.get("username")).first()
        error_msg = 'Invalid SAP Id'
    else:
        user_details = SpUsers.objects.filter(status=1, user_type=1, official_email=request.data.get("username")).first()
        error_msg = 'Invalid Email Id'
    
    if not user_details:
        return Response({'message': error_msg, 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)
    
    username = user_details.official_email
    password = request.data.get("password")
    if username == '':  
        return Response({'message': 'Please provide username', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if password == '':
        return Response({'message': 'Please provide password', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)     
    if username is None or password is None:
        return Response({'message': 'Please provide both username and password', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'message': 'Invalid Credentials', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)

    user_details = SpUsers.objects.filter(status=1, id=user.id).values()
    try:
        user_basic_details = model_to_dict(SpBasicDetails.objects.get(user_id=user.id))
    except SpBasicDetails.DoesNotExist:
        user_basic_details = []

    try:
        user_correspondence_details = model_to_dict(SpAddresses.objects.get(user_id=user.id,type='correspondence'))
    except SpAddresses.DoesNotExist:
        user_correspondence_details = []

    try:
        user_permanent_details = model_to_dict(SpAddresses.objects.get(user_id=user.id,type='permanent'))
    except SpAddresses.DoesNotExist:
        user_permanent_details = []

    context = {}
    context['token']                    = token.key
    context['user_details']             = user_details
    context['basic_details']            = user_basic_details
    context['correspondence_address']   = user_correspondence_details
    context['permanent_address']        = user_permanent_details
    context['app_version']              = model_to_dict(SpAppVersions.objects.get())
    context['state_list']               = SpStates.objects.all().values('id', 'state')
    context['city_list']                = SpCities.objects.all().values('id', 'state_id', 'city')
    context['message']                  = 'Login Succsessfully'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def updateUserPassword(request):
    
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("old_password")is None or request.data.get("old_password") == '':
        return Response({'message': 'Old Password field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("new_password")is None or request.data.get("new_password") == '':
        return Response({'message': 'New Password field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    user_details = SpUsers.objects.get(id=request.data.get("user_id"))    
    if user_details.plain_password != request.data.get("old_password"):
        return Response({'message': 'Old Password incorrect', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 


    user                = SpUsers.objects.get(id=request.data.get("user_id"))
    user.password       = make_password(str(request.data.get("new_password")))
    user.plain_password = str(request.data.get("new_password"))
    user.save()

    context = {}
    context['message'] = 'Password has been successfully updated'
    context['response_code'] = HTTP_200_OK
    
    return Response(context, status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def logout(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    AuthtokenToken.objects.filter(user_id=request.data.get("user_id")).delete()
    context = {}
    context['message'] = 'Logout Succsessfully'
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def updateUserProfile(request):
    user_exists = SpUsers.objects.filter(official_email=request.data.get("official_email")).exclude(id=request.data.get("user_id")).exists()

    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("gender")is None or request.data.get("gender") == '':
        return Response({'message': 'Gender field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("date_of_birth")is None or request.data.get("date_of_birth") == '':
        return Response({'message': 'Date of birth field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("contact_number")is None or request.data.get("contact_number") == '':
        return Response({'message': 'Contact No. field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("official_email")is None or request.data.get("official_email") == '':
        return Response({'message': 'Email id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)    
    if user_exists:
        return Response({'message': 'Email id already exists', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)            
    if request.data.get("store_address_line_1")is None or request.data.get("store_address_line_1") == '':
        return Response({'message': 'Store Address field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("store_state_id")is None or request.data.get("store_state_id") == '':
        return Response({'message': 'Store State field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("store_city_id")is None or request.data.get("store_city_id") == '':
        return Response({'message': 'Store City field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("store_pincode")is None or request.data.get("store_pincode") == '':
        return Response({'message': 'Store Pincode field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("permanent_address_line_1")is None or request.data.get("permanent_address_line_1") == '':
        return Response({'message': 'Permanent Address field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("permanent_state_id")is None or request.data.get("permanent_state_id") == '':
        return Response({'message': 'Permanent State field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("permanent_city_id")is None or request.data.get("permanent_city_id") == '':
        return Response({'message': 'Permanent City field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("permanent_pincode")is None or request.data.get("permanent_pincode") == '':
        return Response({'message': 'Permanent Pincode field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)          


    if bool(request.FILES.get('profile_image', False)) == True:
        uploaded_profile_image = request.FILES['profile_image']
        storage = FileSystemStorage()
        timestamp = int(time.time())
        profile_image_name = uploaded_profile_image.name
        temp = profile_image_name.split('.')
        profile_image_name = 'profile_'+str(timestamp)+"."+temp[(len(temp) - 1)]
        
        profile_image = storage.save(profile_image_name, uploaded_profile_image)
        profile_image = storage.url(profile_image)        
            
    user                        = SpUsers.objects.get(id=request.data.get("user_id"))
    user.official_email         = request.data.get('official_email')
    if bool(request.FILES.get('profile_image', False)) == True:
        if user.profile_image:
            deleteMediaFile(user.profile_image)
        user.profile_image          = profile_image
    user.primary_contact_number = request.data.get('contact_number')
    user.save()

    try:
        user_basic_detail = SpBasicDetails.objects.get(user_id=request.data.get("user_id"))
    except SpBasicDetails.DoesNotExist:
        user_basic_detail = None
    if user_basic_detail:
        user_basic_details = SpBasicDetails.objects.get(user_id=request.data.get("user_id"))
    else:
        user_basic_details = SpBasicDetails()
        
    user_basic_details.user_id          = request.data.get("user_id")
    user_basic_details.date_of_birth    = datetime.strptime(request.data.get('date_of_birth'), '%d/%m/%Y').strftime('%Y-%m-%d')
    user_basic_details.gender           = request.data.get('gender')
    user_basic_details.blood_group      = request.data.get('blood_group')
    user_basic_details.save()

    try:
        user_contact_nos = SpContactNumbers.objects.get(user_id=request.data.get("user_id"), is_primary=1)
    except SpContactNumbers.DoesNotExist:
        user_contact_nos = None
    if user_contact_nos:
        user_contact_no = SpContactNumbers.objects.get(user_id=request.data.get("user_id"), is_primary=1)
    else:
        user_contact_no = SpContactNumbers()

    user_contact_no.user_id         = request.data.get("user_id")    
    user_contact_no.contact_number  = request.data.get('contact_number')
    user_contact_no.save()

    SpAddresses.objects.filter(user_id=request.data.get("user_id")).delete()

    correspondence = SpAddresses()
    correspondence.user_id          = request.data.get("user_id")
    correspondence.type             = 'correspondence'
    correspondence.address_line_1   = request.data.get('store_address_line_1')
    correspondence.address_line_2   = request.data.get('store_address_line_2')
    correspondence.country_id       = 1
    correspondence.country_name     = getModelColumnById(SpCountries, 1,'country')
    correspondence.state_id         = request.data.get('store_state_id')
    correspondence.state_name       = getModelColumnById(SpStates, request.data.get('store_state_id'),'state')
    correspondence.city_id          = request.data.get('store_city_id')
    correspondence.city_name        = getModelColumnById(SpCities, request.data.get('store_city_id'),'city')
    correspondence.pincode          = request.data.get('store_pincode')
    correspondence.save()

    permanent = SpAddresses()
    permanent.user_id               = request.data.get("user_id")
    permanent.type                  = 'permanent'
    permanent.address_line_1        = request.data.get('permanent_address_line_1')
    permanent.address_line_2        = request.data.get('permanent_address_line_2')
    permanent.country_id            = 1
    permanent.country_name          = getModelColumnById(SpCountries, 1,'country')
    permanent.state_id              = request.data.get('permanent_state_id')
    permanent.state_name            = getModelColumnById(SpStates, request.data.get('permanent_state_id'),'state')
    permanent.city_id               = request.data.get('permanent_city_id')
    permanent.city_name             = getModelColumnById(SpCities, request.data.get('permanent_city_id'),'city')
    permanent.pincode               = request.data.get('permanent_pincode')
    permanent.save()

    user                            = SpUsers.objects.get(id=request.data.get("user_id"))

    context = {}
    context['profile_image'] =  user.profile_image
    context['message']       = 'Profile has been updated succsessfully'
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)        
