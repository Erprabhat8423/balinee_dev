import sys
import os
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db import connection
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.apps import apps
from ..models import *
from django.db.models import Q
from utils import *
from datetime import datetime
from datetime import timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from django.forms.models import model_to_dict
import time



from io import BytesIO
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Create your views here.

@login_required
def index(request):
    context = {}
    page = request.GET.get('page')
    vehicles = SpVehicles.objects.all().order_by('-id')
    paginator = Paginator(vehicles, getConfigurationResult('page_limit'))

    try:
        drivers = paginator.page(page)
    except PageNotAnInteger:
        drivers = paginator.page(1)
    except EmptyPage:
        drivers = paginator.page(paginator.num_pages)  
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

    
    context['vehicles']          = vehicles
    context['page_limit']             = getConfigurationResult('page_limit')
    context['page_title'] = "Vehicle Management"

    first_vehicle = SpVehicles.objects.raw('''SELECT * FROM sp_vehicles order by id desc LIMIT 1 ''')

    if first_vehicle :
        context['first_vehicle'] = first_vehicle[0]
    
    template = 'logistics/vehicle/vehicles.html'
    return render(request, template, context)



@login_required
def vehicleShortDetails(request,vehicle_id):
    context = {}
    first_vehicle = SpVehicles.objects.raw('''SELECT * FROM sp_vehicles WHERE id=%s  ''',[vehicle_id])

    if first_vehicle :
        context['first_vehicle'] = first_vehicle[0]
    else : 
        context['first_vehicle'] = []

    template = 'logistics/vehicle/vehicle-short-details.html'
    return render(request, template, context)



@login_required
def ajaxVehicleList(request):
    page = request.GET.get('page')
    organizations = SpOrganizations.objects.all().order_by('-id')
    paginator = Paginator(organizations, getConfigurationResult('page_limit'))

    try:
        organizations = paginator.page(page)
    except PageNotAnInteger:
        organizations = paginator.page(1)
    except EmptyPage:
        organizations = paginator.page(paginator.num_pages)  
    if page is not None:
           page = page
    else:
           page = 1

    total_pages = int(paginator.count/getConfigurationResult('page_limit'))   
    
    temp = total_pages%paginator.count
    if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
        total_pages = total_pages+1
    else:
        total_pages = total_pages

    organization_details = SpOrganizations.objects.order_by('-id').first()
    
    context = {}
    context['organizations']          = organizations
    context['total_pages']            = total_pages
    context['organization_details']   = organization_details

    template = 'role-permission/ajax-vehicles.html'
    return render(request, template, context)



@login_required
def addVehicleBasic(request):
    if request.method == "POST":
        response = {}
        try:
            vehicle = SpVehicles()
            vehicle.registration_number = request.POST['registration_number']
            if 'registered_address' in request.POST and request.POST['registered_address']:
                vehicle.registered_address = request.POST['registered_address']
            if 'ownership_type' in request.POST and request.POST['ownership_type']:
                vehicle.ownership_type = request.POST['ownership_type']
            if 'dealer_name' in request.POST and request.POST['dealer_name']:
                vehicle.dealer_name = request.POST['dealer_name']
            if 'dealer_address' in request.POST and request.POST['dealer_address']:
                vehicle.dealer_address = request.POST['dealer_address']
            if 'dealer_contact_no' in request.POST and request.POST['dealer_contact_no']:
                vehicle.dealer_contact_no = request.POST['dealer_contact_no']
            if 'owner_name' in request.POST and request.POST['owner_name']:
                vehicle.owner_name = request.POST['owner_name']
            if 'owner_address' in request.POST and request.POST['owner_address']:
                vehicle.owner_address = request.POST['owner_address']
            if 'owner_contact_no' in request.POST and request.POST['owner_contact_no']:
                vehicle.owner_contact_no = request.POST['owner_contact_no']
            if 'vehicle_type' in request.POST and request.POST['vehicle_type']:
                vehicle.vehicle_type = request.POST['vehicle_type']
            if 'class_of_vehicle' in request.POST and request.POST['class_of_vehicle']:
                vehicle.class_of_vehicle = request.POST['class_of_vehicle']
            if 'maker_name' in request.POST and request.POST['maker_name']:
                vehicle.maker_name = request.POST['maker_name']
            if 'year_of_manufacture' in request.POST and request.POST['year_of_manufacture']:
                vehicle.year_of_manufacture = request.POST['year_of_manufacture']
            if 'chassis_no' in request.POST and request.POST['chassis_no']:
                vehicle.chassis_no = request.POST['chassis_no']
            if 'engine_no' in request.POST and request.POST['engine_no']:
                vehicle.engine_no = request.POST['engine_no']
            if 'horsepower' in request.POST and request.POST['horsepower']:
                vehicle.horsepower = request.POST['horsepower']
            if request.POST['cubic_capacity'] == "":
                vehicle.cubic_capacity = None
            if 'maker_classification' in request.POST and request.POST['maker_classification']:
                vehicle.maker_classification = request.POST['maker_classification']
            if 'seating_capacity_standard' in request.POST and request.POST['seating_capacity_standard']:
                vehicle.seating_capacity_standard = request.POST['seating_capacity_standard']

            if 'color' in request.POST and request.POST['color']:
                vehicle.color = request.POST['color']
            if 'finance' in request.POST and request.POST['finance']:
                vehicle.finance = request.POST['finance']
            if 'financer_name' in request.POST and request.POST['financer_name']:
                vehicle.financer_name = request.POST['financer_name']
            if 'purchase_date' in request.POST and request.POST['purchase_date']:
                vehicle.purchase_date = datetime.strptime(request.POST['purchase_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
            
            if request.POST['fuel_type'] == "":
                vehicle.fuel_type = None
            else:
                vehicle.fuel_type = request.POST['fuel_type']
            
            if request.POST['mileage'] == "":
                vehicle.mileage = None
            else:
                vehicle.mileage = request.POST['mileage']

            vehicle.ac_fitted = request.POST['ac_fitted']
            vehicle.status  = 1
            vehicle.save()

            if vehicle.id :

                #Save Activity
                user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
                heading     = 'Vehicle created'
                activity    = 'Vehicle created by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                saveActivity('Logistics Management', 'Vehicle Management', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')

                response['flag'] = True
                response['vehicle_id'] = vehicle.id
                response['message'] = "Record has been saved successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save"

            return JsonResponse(response)
        
        except Exception as e:
            response['flag'] = False
            response['message'] = str(e)
            return JsonResponse(response)
    else:
        template = 'logistics/vehicle/add-vehicle-basic.html'
        context = {}
        context['fuel_types']          = SpFuelType.objects.filter(status=1)
        context['vehicle_insurers']          = SpVehicleInsurer.objects.filter(status=1)
        context['routes']          = SpRoutes.objects.filter(status=1)
        context['vehicle_classes']          = SpVehicleClass.objects.filter(status=1)
        context['vehicle_makers']          = SpVehicleMaker.objects.filter(status=1)
        context['vehicle_maker_classifications']          = SpVehicleMakerClassification.objects.filter(status=1)
        context['year_loop'] = range(1990, datetime.now().year)

        return render(request, template,context)



@login_required
def editVehicleBasic(request,vehicle_id):
    if request.method == "POST":
        response = {}
        try:
            vehicle = SpVehicles.objects.get(id=request.POST['vehicle_id'])
            vehicle.registration_number = request.POST['registration_number']
            if 'registered_address' in request.POST and request.POST['registered_address']:
                vehicle.registered_address = request.POST['registered_address']
            if 'ownership_type' in request.POST and request.POST['ownership_type']:
                vehicle.ownership_type = request.POST['ownership_type']
            if 'dealer_name' in request.POST and request.POST['dealer_name']:
                vehicle.dealer_name = request.POST['dealer_name']
            if 'dealer_address' in request.POST and request.POST['dealer_address']:
                vehicle.dealer_address = request.POST['dealer_address']
            if 'dealer_contact_no' in request.POST and request.POST['dealer_contact_no']:
                vehicle.dealer_contact_no = request.POST['dealer_contact_no']
            if 'owner_name' in request.POST and request.POST['owner_name']:
                vehicle.owner_name = request.POST['owner_name']
            if 'owner_address' in request.POST and request.POST['owner_address']:
                vehicle.owner_address = request.POST['owner_address']
            if 'owner_contact_no' in request.POST and request.POST['owner_contact_no']:
                vehicle.owner_contact_no = request.POST['owner_contact_no']
            if 'vehicle_type' in request.POST and request.POST['vehicle_type']:
                vehicle.vehicle_type = request.POST['vehicle_type']
            if 'class_of_vehicle' in request.POST and request.POST['class_of_vehicle']:
                vehicle.class_of_vehicle = request.POST['class_of_vehicle']
            if 'maker_name' in request.POST and request.POST['maker_name']:
                vehicle.maker_name = request.POST['maker_name']
            if 'year_of_manufacture' in request.POST and request.POST['year_of_manufacture']:
                vehicle.year_of_manufacture = request.POST['year_of_manufacture']
            if 'chassis_no' in request.POST and request.POST['chassis_no']:
                vehicle.chassis_no = request.POST['chassis_no']
            if 'engine_no' in request.POST and request.POST['engine_no']:
                vehicle.engine_no = request.POST['engine_no']
            if 'horsepower' in request.POST and request.POST['horsepower']:
                vehicle.horsepower = request.POST['horsepower']
            if request.POST['cubic_capacity'] == "":
                vehicle.cubic_capacity = None
            if 'maker_classification' in request.POST and request.POST['maker_classification']:
                vehicle.maker_classification = request.POST['maker_classification']
            if 'seating_capacity_standard' in request.POST and request.POST['seating_capacity_standard']:
                vehicle.seating_capacity_standard = request.POST['seating_capacity_standard']

            if 'color' in request.POST and request.POST['color']:
                vehicle.color = request.POST['color']
            if 'finance' in request.POST and request.POST['finance']:
                vehicle.finance = request.POST['finance']
            if 'financer_name' in request.POST and request.POST['financer_name']:
                vehicle.financer_name = request.POST['financer_name']
            if 'purchase_date' in request.POST and request.POST['purchase_date']:
                vehicle.purchase_date = datetime.strptime(request.POST['purchase_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
            
            if request.POST['fuel_type'] == "":
                vehicle.fuel_type = None
            else:
                vehicle.fuel_type = request.POST['fuel_type']
            
            if request.POST['mileage'] == "":
                vehicle.mileage = None
            else:
                vehicle.mileage = request.POST['mileage']

            if 'ac_fitted' in request.POST and request.POST['ac_fitted']:
                vehicle.ac_fitted = request.POST['ac_fitted']

            vehicle.status  = 1
            vehicle.save()

            if vehicle.id :

                #Save Activity
                user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
                heading     = 'Vehicle Vehicle details updated'
                activity    = 'Vehicle Vehicle details updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                saveActivity('Logistics Management', 'Vehicle Management', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')

                response['flag'] = True
                response['vehicle_id'] = vehicle.id
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save"
        except Exception as e:
            response['error'] = False
            response['message'] = str(e)
        return JsonResponse(response)
    else:
        context = {}
        context['vehicle']     = SpVehicles.objects.get(id=vehicle_id)
        context['fuel_types']          = SpFuelType.objects.filter(status=1)
        context['vehicle_insurers']          = SpVehicleInsurer.objects.filter(status=1)
        context['routes']          = SpRoutes.objects.filter(status=1)
        context['vehicle_classes']          = SpVehicleClass.objects.filter(status=1)
        context['vehicle_makers']          = SpVehicleMaker.objects.filter(status=1)
        context['vehicle_maker_classifications']          = SpVehicleMakerClassification.objects.filter(status=1)
        context['year_loop'] = range(1990, datetime.now().year)
        template = 'logistics/vehicle/edit-vehicle-basic.html'
        return render(request, template, context)

@login_required
def editVehicleRegistration(request,vehicle_id):
    if request.method == "POST":
        response = {}
        try:
            vehicle = SpVehicles.objects.get(id=request.POST['vehicle_id'])
            vehicle.registration_number = request.POST['registration_number']
            vehicle.save()

            vehicle_registration = SpVehicleRegistrationDetails.objects.get(vehicle_id=request.POST['vehicle_id'])
            vehicle_registration.owner_name = request.POST['owner_name']
            vehicle_registration.registration_number = request.POST['registration_number']
            vehicle_registration.registered_address = request.POST['registered_address']
            vehicle_registration.rto = request.POST['rto']

            if request.POST['registration_date'] != "" : 
                vehicle_registration.registration_fees_amount = request.POST['registration_fees_amount']
            
            if request.POST['registration_date'] != "" : 
                vehicle_registration.registration_date = datetime.strptime(request.POST['registration_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
            
            if request.POST['registration_valid_till'] != "" : 
                vehicle_registration.registration_valid_till = datetime.strptime(request.POST['registration_valid_till'], '%d/%m/%Y').strftime('%Y-%m-%d')
                
           
            vehicle_registration.status = 1
            vehicle_registration.save()


            vehicle_insurance = SpVehicleInsuranceDetails.objects.get(vehicle_id=request.POST['vehicle_id'])
            vehicle_insurance.name_of_insurer = request.POST['name_of_insurer']
            if request.POST['date_of_insurance'] != "" :
                vehicle_insurance.date_of_insurance = datetime.strptime(request.POST['date_of_insurance'], '%d/%m/%Y').strftime('%Y-%m-%d')
            if request.POST['valid_till'] != "" :
                vehicle_insurance.valid_till = datetime.strptime(request.POST['valid_till'], '%d/%m/%Y').strftime('%Y-%m-%d')
            if request.POST['premium_amount'] != "" :
                vehicle_insurance.premium_amount = request.POST['premium_amount']
            vehicle_insurance.status = 1
            vehicle_insurance.save()

            if vehicle.id :

                #Save Activity
                user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
                heading     = 'Vehicle registration detailes updated'
                activity    = 'Vehicle registration detailes updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                saveActivity('Logistics Management', 'Vehicle Management', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')
                
                response['flag'] = True
                response['vehicle_id'] = vehicle.id
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save"
        except Exception as e:
            response['error'] = False
            response['message'] = str(e)
        return JsonResponse(response)
    else:
        context = {}
        context['vehicle']     = SpVehicles.objects.get(id=vehicle_id)
        context['vehicle_registration']     = SpVehicleRegistrationDetails.objects.get(vehicle_id=vehicle_id)
        context['vehicle_insurance']     = SpVehicleInsuranceDetails.objects.get(vehicle_id=vehicle_id)
        context['vehicle_insurers']          = SpVehicleInsurer.objects.filter(status=1)
        template = 'logistics/vehicle/edit-vehicle-registration.html'
        return render(request, template, context)



@login_required
def editVehicleOther(request,vehicle_id):
    if request.method == "POST":
        response = {}
        try:
           
            vehicle_pollution = SpVehiclePollutionDetails.objects.get(vehicle_id=request.POST['vehicle_id'])
            vehicle_pollution.certificate_sr_no = request.POST['certificate_sr_no']
            if request.POST['date_of_registration'] != "" : 
                vehicle_pollution.date_of_registration = datetime.strptime(request.POST['date_of_registration'], '%d/%m/%Y').strftime('%Y-%m-%d')
            
            if request.POST['pollution_valid_till'] != "" : 
                vehicle_pollution.pollution_valid_till = datetime.strptime(request.POST['pollution_valid_till'], '%d/%m/%Y').strftime('%Y-%m-%d')
            vehicle_pollution.status = 1
            vehicle_pollution.save()

            vehicle_fit = SpVehicleFitnessDetails.objects.get(vehicle_id=request.POST['vehicle_id'])
            vehicle_fit.application_no = request.POST['application_no']
            if request.POST['inspection_date'] != "" : 
                vehicle_fit.inspection_date = datetime.strptime(request.POST['inspection_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
            
            if request.POST['fitness_valid_till'] != "" : 
                vehicle_fit.fitness_valid_till = datetime.strptime(request.POST['fitness_valid_till'], '%d/%m/%Y').strftime('%Y-%m-%d')
            vehicle_fit.status = 1
            vehicle_fit.save()

            vehicle_roadpermit = SpVehicleRoadpermitDetails.objects.get(vehicle_id=request.POST['vehicle_id'])
            vehicle_roadpermit.permit_no = request.POST['permit_no']
            if request.POST['permit_registration_date'] != "" : 
                vehicle_roadpermit.permit_registration_date = datetime.strptime(request.POST['permit_registration_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
            
            if request.POST['permit_valid_till'] != "" : 
                vehicle_roadpermit.permit_valid_till = datetime.strptime(request.POST['permit_valid_till'], '%d/%m/%Y').strftime('%Y-%m-%d')
            
            vehicle_roadpermit.purpose = request.POST['purpose']

            vehicle_roadpermit.status = 1
            vehicle_roadpermit.save()



            if vehicle_pollution.id :

                #Save Activity
                user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
                heading     = 'Vehicle other details updated'
                activity    = 'Vehicle other details updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                saveActivity('Logistics Management', 'Vehicle Management', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')

                response['flag'] = True
                response['vehicle_id'] = request.POST['vehicle_id']
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save"
        except Exception as e:
            response['error'] = False
            response['message'] = str(e)
        return JsonResponse(response)
    else:
        context = {}
        context['vehicle']     = SpVehicles.objects.get(id=vehicle_id)
        context['vehicle_pollution']     = SpVehiclePollutionDetails.objects.get(vehicle_id=vehicle_id)
        context['vehicle_fitness']     = SpVehicleFitnessDetails.objects.get(vehicle_id=vehicle_id)
        context['vehicle_roadpermit']     = SpVehicleRoadpermitDetails.objects.get(vehicle_id=vehicle_id)
        template = 'logistics/vehicle/edit-vehicle-other.html'
        return render(request, template, context)

@login_required
def editVehicleRoute(request,vehicle_id):
    if request.method == "POST":
        response = {}
        try:
            vehicle = SpVehicles.objects.get(id=request.POST['vehicle_id'])
            if request.POST['route_id'] != "" :
                vehicle.route_id = request.POST['route_id']
                vehicle.route_name = getModelColumnById(SpRoutes,request.POST['route_id'],'route')
            else:
                vehicle.route_id = None
                vehicle.route_name = None
            
            if request.POST['driver_id'] != "" :
                vehicle.driver_id = request.POST['driver_id']
                driver_first_name = getModelColumnById(SpDrivers,request.POST['driver_id'],'first_name')
                driver_middle_name = getModelColumnById(SpDrivers,request.POST['driver_id'],'middle_name')
                driver_last_name = getModelColumnById(SpDrivers,request.POST['driver_id'],'last_name')
                vehicle.driver_name = driver_first_name + " "+ driver_middle_name +" "+driver_last_name
            else:
                vehicle.driver_id = None
                vehicle.driver_name = None

            vehicle.save()
            if vehicle.id :

                #Save Activity
                user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
                heading     = 'Vehicle Route details updated'
                activity    = 'Vehicle Route details updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                saveActivity('Logistics Management', 'Vehicle Management', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')

                response['flag'] = True
                response['vehicle_id'] = request.POST['vehicle_id']
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save"
        except Exception as e:
            response['error'] = False
            response['message'] = str(e)
        return JsonResponse(response)
    else:
        context = {}
        context['vehicle']     = SpVehicles.objects.get(id=vehicle_id)
        context['drivers'] = SpDrivers.objects.raw(''' SELECT id,first_name,middle_name,last_name FROM sp_drivers 
        where id not in (SELECT driver_id FROM sp_vehicles where driver_id IS NOT NULL AND id != %s) ''', [vehicle_id])

        context['routes'] = SpRoutes.objects.raw(''' SELECT sp_routes.id,sp_routes.route,sp_vehicles.route_id as vehicle_route_id FROM sp_routes LEFT JOIN sp_vehicles on
                sp_vehicles.route_id = sp_routes.id  
                where sp_routes.status=1 ''')
        template = 'logistics/vehicle/vehicle-route-details.html'
        return render(request, template, context)

@login_required
def editVehicleCredential(request,vehicle_id):
    if request.method == "POST":
        response = {}
        try:
            vehicle = SpVehicles.objects.get(id=request.POST['vehicle_id'])
            password = make_password(request.POST['password'])
            vehicle.password = password
            vehicle.plain_password = request.POST['password']
            vehicle.save()

            if vehicle.id :

                #Save Activity
                user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
                heading     = 'Vehicle credentials updated'
                activity    = 'Vehicle credentials updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                saveActivity('Logistics Management', 'Vehicle Management', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')

                response['flag'] = True
                response['vehicle_id'] = request.POST['vehicle_id']
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save"
        except Exception as e:
            response['error'] = False
            response['message'] = str(e)
        return JsonResponse(response)
    else:
        context = {}
        context['vehicle']     = SpVehicles.objects.get(id=vehicle_id)
        template = 'logistics/vehicle/vehicle-credentials.html'
        return render(request, template, context)

@login_required
def updateVehicleStatus(request):

    response = {}
    if request.method == "POST":
        try:
            id = request.POST.get('id')
            is_active = request.POST.get('is_active')
            data = SpVehicles.objects.get(id=id)
            data.status = is_active
            data.save()

            #Save Activity
            user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
            heading     = 'Vehicle status updated'
            activity    = 'Vehicle status updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            saveActivity('Logistics Management', 'Vehicle Management', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')

            response['error'] = False
            response['message'] = "Record has been updated successfully."
        except ObjectDoesNotExist:
            response['error'] = True
            response['message'] = "Method not allowed"
        except Exception as e:
            response['error'] = True
            response['message'] = e
        return JsonResponse(response)
    return redirect('/vehicles')

@login_required
def addPollutionDetails(request,vehicle_id):
    if request.method == "POST":
        response={}
        pollution=SpVehiclePollutionDetails()
        pollution.vehicle_id=request.POST['vehicle_id']
        pollution.certificate_sr_no = request.POST['certificate_sr_no']
        pollution.date_of_registration = datetime.strptime(request.POST['date_of_registration'], '%d/%m/%Y').strftime('%Y-%m-%d')
        pollution.pollution_valid_till = datetime.strptime(request.POST['pollution_valid_till'], '%d/%m/%Y').strftime('%Y-%m-%d')
        pollution.status=1
        if bool(request.FILES.get('copy_of_certificate', False)) == True:
            copy_of_certificate = request.FILES['copy_of_certificate']
            fs = FileSystemStorage()
            filename=fs.save(copy_of_certificate.name,copy_of_certificate)
            uploaded_file_url = fs.url(filename) 
            pollution.copy_of_certificate = uploaded_file_url
        pollution.save()
         
        response['flag'] = True
        response['vehicle_id']=request.POST['vehicle_id']
        response['message'] = "Record has been added succesfully"
        return JsonResponse(response)
    else:
        context = {}
        context['vehicle'] = SpVehicles.objects.get(id=vehicle_id)
        template = 'logistics/vehicle/add-Pollution-Details.html'
        return render(request, template, context)  

@login_required
def editPollutionDetails(request,pollution_id):
    if request.method == "POST":
        response={}
        pollution = SpVehiclePollutionDetails.objects.get(id=request.POST['pollution_id'])
        pollution.certificate_sr_no = request.POST['certificate_sr_no']
        pollution.date_of_registration = datetime.strptime(request.POST['date_of_registration'], '%d/%m/%Y').strftime('%Y-%m-%d')
        pollution.pollution_valid_till = datetime.strptime(request.POST['pollution_valid_till'], '%d/%m/%Y').strftime('%Y-%m-%d')
        pollution.status=1
        if bool(request.FILES.get('copy_of_certificate', False)) == True:
            copy_of_certificate = request.FILES['copy_of_certificate']
            fs = FileSystemStorage()
            filename=fs.save(copy_of_certificate.name,copy_of_certificate)
            uploaded_file_url = fs.url(filename) 
            pollution.copy_of_certificate = uploaded_file_url
        pollution.save()
        
        response['flag'] = True 
        response['pollution_id']=pollution.vehicle_id
        response['message'] = "Record has been added succesfully"
        return JsonResponse(response)
        
    else:
        context = {}
        context['pollution'] = SpVehiclePollutionDetails.objects.get(id=pollution_id)
        template = 'logistics/vehicle/edit-PollutionDetails.html'
        return render(request,template,context)
    
    
       
    
@login_required
def addRegistrationDetails(request,vehicle_id):
    if request.method == "POST":
        response={}
        registration=SpVehicleRegistrationDetails()
        registration.vehicle_id=request.POST['vehicle_id']
        registration.owner_name=request.POST['owner_name']
        registration.registration_number = request.POST['registration_number']
        registration.registered_address = request.POST['registered_address']
        registration.rto = request.POST['rto']
        registration.registration_fees_amount = request.POST['registration_fees_amount'] 
        registration.registration_date = datetime.strptime(request.POST['registration_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
        registration.registration_valid_till = datetime.strptime(request.POST['registration_valid_till'], '%d/%m/%Y').strftime('%Y-%m-%d')
        registration.status=1
        if bool(request.FILES.get('registration_copy', False)) == True:
            registration_copy = request.FILES['registration_copy']
            fs = FileSystemStorage()
            filename=fs.save(registration_copy.name,registration_copy)
            uploaded_file_url = fs.url(filename) 
            registration.registration_copy = uploaded_file_url
        registration.save() 
        
        response['flag'] = True
        response['message'] = "Record has been added succesfully"   
        response['vehicle_id']=request.POST['vehicle_id']
        return JsonResponse(response)
    else:
        context = {}
        context['vehicle'] = SpVehicles.objects.get(id=vehicle_id)
        template = 'logistics/vehicle/add-Registration-Details.html'
        return render(request, template, context)
        
@login_required
def editRegistrationDetails(request,registration_id):
    if request.method == "POST":
        response={}
        registration=SpVehicleRegistrationDetails()
        registration = SpVehicleRegistrationDetails.objects.get(id=request.POST['registration_id'])
        registration.owner_name=request.POST['owner_name']
        registration.registration_number = request.POST['registration_number']
        registration.registered_address = request.POST['registered_address']
        registration.rto = request.POST['rto']
        registration.registration_fees_amount = request.POST['registration_fees_amount'] 
        registration.registration_date = datetime.strptime(request.POST['registration_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
        registration.registration_valid_till = datetime.strptime(request.POST['registration_valid_till'], '%d/%m/%Y').strftime('%Y-%m-%d')
        registration.status=1
        if bool(request.FILES.get('registration_copy', False)) == True:
            registration_copy = request.FILES['registration_copy']
            fs = FileSystemStorage()
            filename=fs.save(registration_copy.name,registration_copy)
            uploaded_file_url = fs.url(filename) 
            registration.registration_copy = uploaded_file_url
        registration.save() 

         
        response['flag'] = True
        response['message'] = "Record has been added succesfully"
        response['registration_id']=registration.vehicle_id
        return JsonResponse(response)
        
    else:
        context = {}
        context['registration'] = SpVehicleRegistrationDetails.objects.get(id=registration_id)
        template = 'logistics/vehicle/edit-RegistrationDetails.html'
        return render(request,template,context)
    
        
@login_required
def addFitnessDetails(request,vehicle_id):
    if request.method == "POST":
        response={}
        fitness= SpVehicleFitnessDetails()
        fitness.vehicle_id=request.POST['vehicle_id']
        fitness.application_no=request.POST['application_no']
        fitness.inspection_date = datetime.strptime(request.POST['inspection_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
        fitness.fitness_valid_till = datetime.strptime(request.POST['fitness_valid_till'], '%d/%m/%Y').strftime('%Y-%m-%d')
        fitness.status=0
        if bool(request.FILES.get('copy_of_fitness_certificate', False)) == True:
            copy_of_fitness_certificate = request.FILES['copy_of_fitness_certificate']
            fs = FileSystemStorage()
            filename=fs.save(copy_of_fitness_certificate.name,copy_of_fitness_certificate)
            uploaded_file_url = fs.url(filename) 
            fitness.copy_of_fitness_certificate = uploaded_file_url
        fitness.save() 
        response['flag'] = True
        response['message'] = "Record has been added succesfully"
        response['vehicle_id']=request.POST['vehicle_id']
        return JsonResponse(response)
    else:
        context = {}
        context['vehicle'] = SpVehicles.objects.get(id=vehicle_id)
        template = 'logistics/vehicle/add-Fitness-Details.html'
        return render(request, template, context)
    

        
@login_required
def editFitnesDetails(request,fitness_id):
    if request.method == "POST":
        response={}
        fitness= SpVehicleFitnessDetails()
        fitness = SpVehicleFitnessDetails.objects.get(id=request.POST['fitness_id'])
        fitness.application_no=request.POST['application_no']
        fitness.inspection_date = datetime.strptime(request.POST['inspection_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
        fitness.fitness_valid_till = datetime.strptime(request.POST['fitness_valid_till'], '%d/%m/%Y').strftime('%Y-%m-%d')
        fitness.status=0
        if bool(request.FILES.get('copy_of_fitness_certificate', False)) == True:
            copy_of_fitness_certificate = request.FILES['copy_of_fitness_certificate']
            fs = FileSystemStorage()
            filename=fs.save(copy_of_fitness_certificate.name,copy_of_fitness_certificate)
            uploaded_file_url = fs.url(filename) 
            fitness.copy_of_fitness_certificate = uploaded_file_url
        fitness.save() 
        
        response['flag'] = True
        response['message'] = "Record has been added succesfully"
        response['fitness_id']=fitness.vehicle_id
        return JsonResponse(response)
        
    else:
        context = {}
        context['fitness'] = SpVehicleFitnessDetails.objects.get(id=fitness_id)
        template = 'logistics/vehicle/edit-FitnessDetails.html'
        return render(request,template,context)
    
        
@login_required
def addInsuranceDetails(request,vehicle_id):
    if request.method == "POST":
        response={}
        insurance= SpVehicleInsuranceDetails()
        insurance.vehicle_id=request.POST['vehicle_id']
        insurance.name_of_insurer=request.POST['name_of_insurer']
        insurance.date_of_insurance = datetime.strptime(request.POST['date_of_insurance'], '%d/%m/%Y').strftime('%Y-%m-%d')
        insurance.premium_amount = request.POST['premium_amount']
        insurance.valid_till = datetime.strptime(request.POST['valid_till'], '%d/%m/%Y').strftime('%Y-%m-%d')
        insurance.total_sum_insured = request.POST['total_sum_insured']
        insurance.status=0
        if bool(request.FILES.get('insurance_copy', False)) == True:
            insurance_copy = request.FILES['insurance_copy']
            fs = FileSystemStorage()
            filename=fs.save(insurance_copy.name,insurance_copy)
            uploaded_file_url = fs.url(filename) 
            insurance.insurance_copy = uploaded_file_url
                           
        insurance.save() 
        
        response['flag'] = True
        response['message'] = "Record has been added succesfully"
        response['vehicle_id']=request.POST['vehicle_id']
        return JsonResponse(response)
    else:
        context = {}
        context['vehicle'] = SpVehicles.objects.get(id=vehicle_id)
        template = 'logistics/vehicle/add-Insurance-Details.html'
        return render(request, template, context)
    
        
@login_required
def editInsuranceDetails(request,insurance_id):
    if request.method == "POST":
        response={}
        insurance= SpVehicleInsuranceDetails()
        insurance = SpVehicleInsuranceDetails.objects.get(id=request.POST['insurance_id'])
        insurance.name_of_insurer=request.POST['name_of_insurer']
        insurance.date_of_insurance = datetime.strptime(request.POST['date_of_insurance'], '%d/%m/%Y').strftime('%Y-%m-%d')
        insurance.premium_amount = request.POST['premium_amount']
        insurance.valid_till = datetime.strptime(request.POST['valid_till'], '%d/%m/%Y').strftime('%Y-%m-%d')
        insurance.total_sum_insured = request.POST['total_sum_insured']
        insurance.status=0
        if bool(request.FILES.get('insurance_copy', False)) == True:
            insurance_copy = request.FILES['insurance_copy']
            fs = FileSystemStorage()
            filename=fs.save(insurance_copy.name,insurance_copy)
            uploaded_file_url = fs.url(filename) 
            insurance.insurance_copy = uploaded_file_url
                           
        insurance.save()
              
        
         
        response['flag'] = True
        response['message'] = "Record has been added succesfully"
        response['insurance_id']=insurance.vehicle_id
        return JsonResponse(response)
    else:
        context = {}
        context['insurance'] = SpVehicleInsuranceDetails.objects.get(id=insurance_id)
        template = 'logistics/vehicle/edit-InsuranceDetails.html'
        return render(request,template,context)
    
    
@login_required
def addPermitDetails(request,vehicle_id):
    if request.method == "POST":
        response={}
        permit= SpVehicleRoadpermitDetails()
        permit.vehicle_id=request.POST['vehicle_id']
        permit.permit_no=request.POST['permit_no']
        permit.permit_registration_date = datetime.strptime(request.POST['permit_registration_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
        permit.permitted_route = request.POST['permitted_route']
        permit.permit_valid_till = datetime.strptime(request.POST['permit_valid_till'], '%d/%m/%Y').strftime('%Y-%m-%d')
        permit.purpose = request.POST['purpose']
        permit.status=0
        if bool(request.FILES.get('insurance_copy', False)) == True:
            insurance_copy = request.FILES['insurance_copy']
            fs = FileSystemStorage()
            filename=fs.save(insurance_copy.name,insurance_copy)
            uploaded_file_url = fs.url(filename) 
            permit.insurance_copy = uploaded_file_url
        permit.save() 
        
        response['flag'] = True
        response['message'] = "Record has been added succesfully"
        response['vehicle_id']=request.POST['vehicle_id']
        return JsonResponse(response)
    else:
        context = {}
        context['vehicle'] = SpVehicles.objects.get(id=vehicle_id)
        template = 'logistics/vehicle/add-Permit-Details.html'
        return render(request, template, context)
    
    
@login_required
def editPermitDetails(request,permit_id):
    if request.method == "POST":
        response={}
        permit= SpVehicleRoadpermitDetails()
        permit = SpVehicleRoadpermitDetails.objects.get(id=request.POST['permit_id'])
        permit.permit_no=request.POST['permit_no']
        permit.permit_registration_date = datetime.strptime(request.POST['permit_registration_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
        permit.permitted_route = request.POST['permitted_route']
        permit.permit_valid_till = datetime.strptime(request.POST['permit_valid_till'], '%d/%m/%Y').strftime('%Y-%m-%d')
        permit.purpose = request.POST['purpose']
        permit.status=0
        if bool(request.FILES.get('insurance_copy', False)) == True:
            insurance_copy = request.FILES['insurance_copy']
            fs = FileSystemStorage()
            filename=fs.save(insurance_copy.name,insurance_copy)
            uploaded_file_url = fs.url(filename) 
            permit.insurance_copy = uploaded_file_url
        permit.save() 
        
        permit.save() 
        
        response['flag'] = True
        response['message'] = "Record has been added succesfully"
        response['permit_id']=permit.vehicle_id
        return JsonResponse(response)
    else:
        context = {}
        context['permit'] = SpVehicleRoadpermitDetails.objects.get(id=permit_id)
        template = 'logistics/vehicle/edit-Permit-Details.html'
        return render(request,template,context)
    
  
@login_required
def ajaxRegistrationList(request,vehicle_id):
    context = {}
    context['vehicle'] = SpVehicles.objects.get(id=vehicle_id)
    context['vehicle_pollutions'] =SpVehiclePollutionDetails.objects.filter(vehicle_id=vehicle_id)
    context['vehicle_insurances'] = SpVehicleInsuranceDetails.objects.filter(vehicle_id=vehicle_id)
    context['vehicle_registrations'] = SpVehicleRegistrationDetails.objects.filter(vehicle_id=vehicle_id)
    context['fitness_details'] = SpVehicleFitnessDetails.objects.filter(vehicle_id=vehicle_id)
    context['road_permits'] = SpVehicleRoadpermitDetails.objects.filter(vehicle_id=vehicle_id)
    template = 'logistics/vehicle/ajax-registration-list.html'
    return render(request, template, context)
