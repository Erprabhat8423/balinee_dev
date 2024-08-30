import json
import time
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.db.models import Max
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from ...models import *
from utils import *

from datetime import datetime, date
from datetime import timedelta
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import time
from django.shortcuts import get_object_or_404


@csrf_exempt
@api_view(["POST"])
def saveTAVisit(request):
    data = request.data
    # Validation
    required_fields = ["user_id", "visit_date", "latitude", "longitude", "type","bmc_id","ser_check"]
    for field in required_fields:
        if data.get(field) is None or data.get(field) == '':
            return Response({'message': f'{field} field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if data.get("type") != '1':
        if SpTaVisit.objects.filter(user_id=data.get("user_id"), visit_date__icontains=data.get("visit_date"), end_time__isnull=False, ser_check=data.get("ser_check"),bmc_id=data.get("bmc_id")).exists():
            return Response({'message': 'Visit already marked.', 'response_code': HTTP_200_OK}, status=HTTP_200_OK)
    # Handle images
    try:
        start_image = None
        end_image = None
        if bool(request.FILES.get('start_reading_img', False)):
            start_reading_img = request.FILES['start_reading_img']
            storage = FileSystemStorage()
            timestamp = int(time.time())
            start_reading_img_name = f'attendance{timestamp}.{start_reading_img.name.split(".")[-1]}'
            start_image = storage.save(start_reading_img_name, start_reading_img)
            start_image = storage.url(start_image)

        if bool(request.FILES.get('end_reading_img', False)):
            end_reading_img = request.FILES['end_reading_img']
            storage = FileSystemStorage()
            timestamp = int(time.time())
            end_reading_img_name = f'attendance{timestamp}.{end_reading_img.name.split(".")[-1]}'
            end_image = storage.save(end_reading_img_name, end_reading_img)
            end_image = storage.url(end_image)
        # Prepare payload
        user_name = getUserName(data.get("user_id"))
        travel_charge = 1
        payload = {
            "user_id": data.get("user_id"),
            "user_name": user_name if data.get("type") == '1' else None,
            "visit_date": data.get("visit_date"),
            "bmc_id": data.get("bmc_id"),
            "travel_charge": travel_charge if data.get("type") == '1' else 0,
            "start_time": data.get("start_time") if data.get("type") == '1' else None,
            "start_reading": data.get("start_reading") if data.get("type") == '1' else None,
            "end_time": data.get("end_time") if data.get("end_time") else None,
            "end_reading": data.get("end_reading") if data.get("end_reading") else None,
            "purpose": data.get("purpose") if data.get("purpose") else None,
            "remark": data.get("remark") if data.get("remark") else None,
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "start_reading_img": start_image,
            "end_reading_img": end_image,
            "ser_check":data.get("ser_check")
        }

        if not SpTaVisit.objects.filter(**payload).exists():
            new_entry = SpTaVisit.objects.create(**payload)
            # if data.get("type") == '1':
            #     new_entry.ser_check = new_entry.id
            #     new_entry.save()
            # else:
            #     get_visit_ser_check_id = SpTaVisit.objects.filter(user_id=data.get("user_id"), visit_date__icontains=data.get("visit_date"), start_time__isnull=False,ser_check = data.get("ser_check")).first()
            #     if get_visit_ser_check_id:
            #         new_entry.ser_check = get_visit_ser_check_id.ser_check
            #         new_entry.save()
            #     else:
            #         new_entry.ser_check = data.get("ser_check")
            #         new_entry.save()
        user_name = f"{request.user.first_name} {request.user.middle_name} {request.user.last_name}"
        heading = 'Visit request'
        activity = "Your visit has started." if data.get("type") == '1' else "Your visit has ended."
        saveActivity('Visit request', 'Visit request', heading, activity, request.user.id, user_name, 'markedAtten.png', '2', 'app.png')

        context = {
            'message': activity,
            'response_code': HTTP_200_OK
        }
        return Response(context, status=HTTP_200_OK)
    except Exception as e:
        context = {
            'message': str(e),
            'response_code': HTTP_400_BAD_REQUEST
        }
        return Response(context, status=HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(["POST"])
def getVisitData(request):
    user_id = request.data.get("user_id")
    request_date = request.data.get("request_date")
    
    if not user_id:
        return Response({'message': 'user_id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    
    if not request_date:
        return Response({'message': 'request_date field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    
    # Fetch all records at once
    visit_records = SpTaVisit.objects.filter(user_id=user_id, visit_date__icontains=request_date).order_by('-start_time')

    visit_list = []
    for visit in visit_records:
        if visit.start_time is not None:
            visit_dict = {
                'user_id': visit.user_id,
                'user_name': visit.user_name,
                'visit_date': visit.visit_date,
                'start_time': visit.start_time,
                'start_reading': visit.start_reading,
                'start_reading_img': visit.start_reading_img,
                'start_latitude': visit.latitude,
                'start_longitude': visit.longitude,
                'bmc_id': visit.bmc_id,
                'bmc_name': visit.bmc.name if visit.bmc else None,  # BMC name
                'bmc_code': visit.bmc.bmc_code if visit.bmc else None,  # BMC code
                'end_time': None,
                'end_reading': None,
                'end_reading_img': None,
                'purpose': visit.purpose,
                'remark': None,
                'total_km': 0.0,
                "ser_check": visit.ser_check,
                # "start_ser_check": visit.ser_check,
                "travel_charge":getConfigurationResult('travel_charge'),
                # 'end_ser_check': None
            }

            # Find corresponding end visit record
            end_visit = visit_records.filter(
                start_time__isnull=True,
                visit_date=visit.visit_date,
                ser_check=visit.ser_check
            ).first()

            if end_visit:
                visit_dict.update({
                    'end_time': end_visit.end_time,
                    'end_reading': end_visit.end_reading,
                    'end_reading_img': end_visit.end_reading_img,
                    'remark': end_visit.remark,
                    'start_latitude': end_visit.latitude,
                    'start_longitude': end_visit.longitude,
                    'total_km': end_visit.end_reading - visit.start_reading if visit.start_reading is not None and end_visit.end_reading is not None else 0.0,
                    # 'end_ser_check': end_visit.ser_check
                })

            visit_list.append(visit_dict)

    visit_list.sort(key=lambda x: x['visit_date'], reverse=True)
    
    context = {
        'visit_list': visit_list,
        'count': len(visit_list),
        'message': 'Success',
        'response_code': HTTP_200_OK    
    }

    return JsonResponse(context, status=HTTP_200_OK)



@csrf_exempt
@api_view(["POST"])
def createVisitCheckin(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required'}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("bmc_id") is None or request.data.get("bmc_id") == '':
        return Response({'message': 'bmc id field is required'}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("mpp_id") is None or request.data.get("mpp_id") == '':
        return Response({'message': 'mpp id field is required'}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("checkin_datetime") is None or request.data.get("checkin_datetime") == '':
        return Response({'message': 'checkin datetime field is required'}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("visit_date") is None or request.data.get("visit_date") == '':
        return Response({'message': 'visit date field is required'}, status=HTTP_400_BAD_REQUEST) 
    if SpVisits.objects.filter(user_id = request.data.get("user_id"),bmc_id=request.data.get("bmc_id"),mpp_id=request.data.get("mpp_id"),visit_date = request.data.get("visit_date")).exists():
        return Response({"message":"Check In successfully"},status=HTTP_200_OK) 
    visit_obj                   =   SpVisits()
    visit_obj.user_id           =   request.data.get("user_id") 
    visit_obj.bmc_id            =   request.data.get("bmc_id")
    visit_obj.mpp_id            =   request.data.get("mpp_id")
    visit_obj.visit_date        =   request.data.get("visit_date")
    visit_obj.checkin_datetime  =   request.data.get("checkin_datetime")
    visit_obj.visit_status      =   1
    visit_obj.created_at        =   datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    visit_obj.updated_at        =   datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    visit_obj.save()
    user_name                   = getUserName(request.data.get("user_id"))
    heading                     = 'Check-In'
    activity                    = 'Check-In done for '+str(getModelColumnById(SpMPP,request.data.get("mpp_id"),'name')).upper() 
    saveActivity('Check-In', 'Check-In done', heading, activity, request.data.get("user_id"), user_name, 'noti.png', '2', 'mobile.png')
    return Response({"message":"Check In successfully"},status=HTTP_200_OK) 
    


@csrf_exempt
@api_view(["POST"])
def createVisitCheckout(request):                         
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required'}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("bmc_id") is None or request.data.get("bmc_id") == '':
        return Response({'message': 'Beat id field is required'}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("mpp_id") is None or request.data.get("mpp_id") == '':
        return Response({'message': 'mpp id field is required'}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("checkout_datetime") is None or request.data.get("checkout_datetime") == '':
        return Response({'message': 'checkout datetime field is required'}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("visit_date") is None or request.data.get("visit_date") == '':
        return Response({'message': 'visit date field is required'}, status=HTTP_400_BAD_REQUEST) 

    visit_obj =  SpVisits.objects.filter(user_id = request.data.get("user_id"),bmc_id=request.data.get("bmc_id"),mpp_id=request.data.get("mpp_id"),visit_date = request.data.get("visit_date")).first()
    start_datetime              = visit_obj.checkin_datetime
    end_datetime                = datetime.strptime(str(request.data.get("checkout_datetime")), '%Y-%m-%d %H:%M:%S')
    consume_hours               = str(end_datetime - start_datetime)
    visit_obj.checkout_datetime = request.data.get("checkout_datetime")
    visit_obj.visit_status      = 2
    visit_obj.total_retail_time = consume_hours      
    visit_obj.updated_at        = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    visit_obj.save()
    user_name                   = getUserName(request.data.get("user_id"))
    heading                     = 'Check-Out'
    activity                    = 'Check-Out done for '+str(getModelColumnById(SpMPP,request.data.get("mpp_id"),'name')).upper()
    saveActivity('Check-Out', 'Check-Out done', heading, activity, request.data.get("user_id"), user_name, 'noti.png', '2', 'mobile.png')
    return Response({"message":"Check Out successfully"},status=HTTP_200_OK) 

@csrf_exempt
@api_view(["POST"])
def visitList(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("page_limit") is None or request.data.get("page_limit") == '':
        return Response({'message': 'Page limit is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    current_date    = date.today()
    page_limit      = int(request.data.get("page_limit")) * 20
    offset          = int(page_limit) - 20
    page_limit      = 20
    total_no_pages  = 0
    list_count      = 0

    # Query to get MPPs with the latest check-in datetime
    mpp_list = SpMPP.objects.filter(employee_id=request.data.get("user_id"))
    
    if request.data.get("mpp_id"):
        mpp_list = mpp_list.filter(id=request.data.get("mpp_id"))
    
    if request.data.get("bmc_id"):
        mpp_list = mpp_list.filter(bmc_id=request.data.get("bmc_id"))
    
    # Annotate MPPs with the latest check-in datetime
    mpp_list = mpp_list.prefetch_related('mpp_visits').select_related('bmc').annotate(
        latest_checkin = Max('mpp_visits__checkin_datetime')
    )
    list_count          = mpp_list.count()
    bmc_count           = len(list(set(mpp_list.values_list('bmc_id', flat=True) )))
    mpp_list            = mpp_list.values('id', 'name', 'mpp_code', 'bmc__name', 'bmc__bmc_code','employee__id','employee__first_name','employee__middle_name','employee__last_name','employee__emp_sap_id','employee__role_name','latest_checkin').order_by('-id')[offset:offset+page_limit]
    for mpp in mpp_list:
        is_visit        = SpVisits.objects.filter(mpp_id = mpp['id'],visit_date__icontains = current_date.strftime("%Y-%m-%d")).first()
        mpp['is_visit'] = is_visit.visit_status if is_visit else 0
        mpp['visit_id'] = is_visit.id if is_visit else 0
    total_no_pages      = math.ceil(round(list_count / 20, 2))  
    
    context = {
        'list_count': list_count,
        'mpp_count':list_count,
        'bmc_count':bmc_count,
        'total_no_pages': total_no_pages,
        'mpp_list': list(mpp_list),  # Ensure it's a list for JSON serialization
        'message': 'Success',
        'response_code': HTTP_200_OK
    }
    
    return Response(context, status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def visitHistoryList(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("page_limit") is None or request.data.get("page_limit") == '':
        return Response({'message': 'Page limit is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("start_date") is None or request.data.get("start_date") == '':
        return Response({'message': 'start data field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   
    if request.data.get("end_date") is None or request.data.get("end_date") == '':
        return Response({'message': 'end data field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    start_date      = request.data.get("start_date")
    end_date        = datetime.strptime(request.data.get("end_date"), "%Y-%m-%d")
    end_date        = end_date + timedelta(days=1)
    page_limit          = int(request.data.get("page_limit")) * 20
    offset              = int(page_limit) - 20
    page_limit          = 20
    total_no_pages      = 0
    list_count          = 0
    # Query to get MPPs with the latest check-in datetime
    mpp_list            = SpVisits.objects.filter(user_id=request.data.get("user_id"))
    if request.data.get("start_date") and request.data.get("end_date"):
        mpp_list        = mpp_list.filter(user_id=request.data.get("user_id"),visit_date__range = [start_date,end_date])
    if request.data.get("mpp_id"):
        mpp_list        = mpp_list.filter(id=request.data.get("mpp_id"))
    if request.data.get("bmc_id"):
        mpp_list        = mpp_list.filter(bmc_id=request.data.get("bmc_id"))
    list_count          = mpp_list.count()
    bmc_count           = len(list(set(mpp_list.values_list('bmc_id', flat=True) )))
    mpp_list            = mpp_list.values('id','mpp__id','mpp__name', 'mpp__mpp_code','bmc__id' ,'bmc__name', 'bmc__bmc_code','user__id','user__first_name','user__middle_name','user__last_name' ,'checkin_datetime').order_by('-id')[offset:offset+page_limit]
    total_no_pages      = math.ceil(round(list_count / 20, 2))  
    
    context = {
        'list_count': list_count,
        'mpp_count':list_count,
        'bmc_count':bmc_count,
        'total_no_pages': total_no_pages,
        'mpp_list': list(mpp_list),  # Ensure it's a list for JSON serialization
        'message': 'Success',
        'response_code': HTTP_200_OK
    }

    return Response(context, status=HTTP_200_OK) 



def handle_file_upload(file, prefix):
    storage = FileSystemStorage()
    timestamp = int(time.time())
    file_name = f'{prefix}{timestamp}.{file.name.split(".")[-1]}'
    saved_file = storage.save(file_name, file)
    return storage.url(saved_file)


from django.db import transaction

@csrf_exempt
@api_view(["POST"])
def saveMppVisitHistory(request):
    data = request.data
    required_fields = ["user_id","visit_id","mpp_id", "visit_date", "visit_date_time", "shift", "bmc_id", "arrival_time", "departure_time", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12", "q13", "q14", "q15", "q16", "q17", "q18", "q19", "q20", "q21", "q22", "q23"]
    for field in required_fields:
        if not data.get(field):
            return Response({'message': f'{field} field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if SpMppVisitHistory.objects.filter(visit_id = data.get("visit_id"), user_id = data.get("user_id"),mpp_id = data.get("mpp_id"),visit_date = data.get("visit_date"),bmc_id = data.get("bmc_id"),shift = data.get("shift")).exists():
        return Response({"message":"Data saved successfully"},status=HTTP_200_OK)
    mpp_image, mpp_signature = None, None

    if request.FILES.get('q25'):
        mpp_image = handle_file_upload(request.FILES['q25'], 'mpp')
    if request.FILES.get('q26'):
        mpp_signature = handle_file_upload(request.FILES['q26'], 'mpp')

    try:
        with transaction.atomic():
            mppvist, created = SpMppVisitHistory.objects.get_or_create(
                user_id=data.get("user_id"),
                mpp_id=data.get("mpp_id"),
                visit_id=data.get("visit_id"),
                visit_date=data.get("visit_date"),
                bmc_id=data.get("bmc_id"),
                shift=data.get("shift"),
                defaults={
                    'visit_date_time': data.get("visit_date_time"),
                    'arrival_time': data.get("arrival_time"),
                    'departure_time': data.get("departure_time")
                }
            )

            if created:
                SpMppVisitHistoryDetails.objects.create(
                    sp_mpp_visit_history_id=mppvist.id,
                    q1=data.get('q1'),
                    q2=data.get('q2'),
                    q3=data.get('q3'),
                    q4=data.get('q4'),
                    q5=data.get('q5'),
                    q6=data.get('q6'),
                    q7=data.get('q7'),
                    q8=data.get('q8'),
                    q9=data.get('q9'),
                    q10=data.get('q10'),
                    q11=data.get('q11'),
                    q12=data.get('q12'),
                    q13=data.get('q13'),
                    q14=data.get('q14'),
                    q15=data.get('q15'),
                    q16=data.get('q16'),
                    q17=data.get('q17'),
                    q18=data.get('q18'),
                    q19=data.get('q19'),
                    q20=data.get('q20'),
                    q21=data.get('q21'),
                    q22=data.get('q22'),
                    q23=data.get('q23'),
                    q24=data.get('q24', None),
                    q25=mpp_image,
                    q26=mpp_signature
                )
        context = {
            'message': "Data saved successfully",
            'response_code': HTTP_200_OK
        }
        return Response(context, status=HTTP_200_OK)

    except Exception as e:
        return Response({'message': str(e), 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    

@csrf_exempt
@api_view(["POST"])
def visitHistoryDetails(request):
    visit_id = request.data.get("visit_id")

    if not visit_id:
        return Response({'message': 'visit_id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)

    # Get the visit history object using the visit_id field
    try:
        visit_history = SpMppVisitHistory.objects.select_related('user', 'mpp', 'bmc').prefetch_related('history_details').get(visit_id=visit_id)
    except SpMppVisitHistory.DoesNotExist:
        return Response({'message': 'Visit history not found', 'response_code': HTTP_404_NOT_FOUND}, status=HTTP_404_NOT_FOUND)


    # Get the related visit details
    visit_details = visit_history.history_details.all()

    # Prepare the response data
    data = {
        'visit': {
            'id': visit_history.id,
            'visit_date_time': visit_history.visit_date_time,
            'visit_date': visit_history.visit_date,
            'shift': visit_history.shift,
            'arrival_time': visit_history.arrival_time,
            'departure_time': visit_history.departure_time,
            'created_at': visit_history.created_at,
            'updated_at': visit_history.updated_at,
            'user_id': visit_history.user.id,
            'first_name': visit_history.user.first_name, 
            'middle_name': visit_history.user.middle_name,  
            'last_name': visit_history.user.last_name,  
            'emp_sap_id': visit_history.user.emp_sap_id,  
            'role_name': visit_history.user.role_name,  
            'mpp_id': visit_history.mpp.id,
            'mpp_name': visit_history.mpp.name,  
            'mpp_code': visit_history.mpp.mpp_code, 
            'bmc_id': visit_history.bmc.id,
            'bmc_name': visit_history.bmc.name,  
            'bmc_code': visit_history.bmc.bmc_code, 
        },
        'visit_details': [{
            'id': detail.id,
            'q1': detail.q1,
            'q2': detail.q2,
            'q3': detail.q3,
            'q4': detail.q4,
            'q5': detail.q5,
            'q6': detail.q6,
            'q7': detail.q7,
            'q8': detail.q8,
            'q9': detail.q9,
            'q10': detail.q10,
            'q11': detail.q11,
            'q12': detail.q12,
            'q13': detail.q13,
            'q14': detail.q14,
            'q15': detail.q15,
            'q16': detail.q16,
            'q17': detail.q17,
            'q18': detail.q18,
            'q19': detail.q19,
            'q20': detail.q20,
            'q21': detail.q21,
            'q22': detail.q22,
            'q23': detail.q23,
            'q24': detail.q24,
            'q25': detail.q25,
            'q26': detail.q26,
        } for detail in visit_details]
    }

    return Response(data, status=HTTP_200_OK)
