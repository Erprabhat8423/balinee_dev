from ...models import *
from ...decorators import validate_logistic_api,validatePOST,validateGET
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.core import serializers
from utils import *
from datetime import datetime, date
from datetime import timedelta
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from  django.contrib.auth.hashers import check_password,make_password
import json

@csrf_exempt
@validatePOST
def login(request):
    response = {}
    status_code = 200
    received_data=json.loads(request.body)
    if 'registration_number' not in received_data or received_data['registration_number'] == "" :
        response['message'] = "Registration Number is missing"
        status_code = 404
    if 'password' not in received_data or received_data['password'] == "" :
        response['message'] = "Password is missing"
        status_code = 404
    
    if status_code == 200 :
        registration_number = received_data['registration_number']
        password = received_data['password']
        if SpVehicles.objects.filter(registration_number=registration_number).exists() :
            vehicle = SpVehicles.objects.get(registration_number=registration_number)
            if check_password(received_data['password'], vehicle.password):
                if vehicle.route_id is not None :
                    vehicle.api_token = make_password(str(vehicle.id) + str(vehicle.registration_number))
                    vehicle.save()
                    response['message'] = "Logged in successfully"
                    response['registration_number'] = vehicle.registration_number
                    response['route_name'] = vehicle.route_name
                    response['user_id'] = vehicle.id
                    response['api_key'] = vehicle.api_token
                    if vehicle.vehicle_pic is None:
                        response['vehicle_pic'] = '/static/img/png/default_app_icon.png'
                    else:
                        response['vehicle_pic'] = vehicle.vehicle_pic
                    response['tracking_time'] = getModelColumnById(Configuration, 1, 'user_tracking_time')    
                    status_code = 200
                else:
                    response['message'] = "Route is not assigned. please contact the administrator."
                    status_code = 401
            else:
                response['message'] = "Invalid Credentials"
                status_code = 401
        else:
            response['message'] = "Invalid Credentials"
            status_code = 401
    return JsonResponse(response,status = status_code)

@validateGET
@validate_logistic_api
def todayOrders(request):
    
    response = {}
    status_code = 200
    api_token = request.headers['Authorization']
    vehicle = SpVehicles.objects.get(api_token=api_token)
    if vehicle.route_id is None:
        response['message'] = "Route is not assigned. please contact the administrator."
        status_code = 401
    else:
        route_id = vehicle.route_id
        today   = date.today()
        orders = []
        order_list = SpOrders.objects.filter(order_date__icontains=today.strftime("%Y-%m-%d"),route_id=route_id,order_status=3,indent_status=1).values('id','user_id', 'order_code','town_name','route_name','user_name', 'order_date', 'order_status', 'order_total_amount', 'order_items_count')
        for order in order_list:
            current_order = {}
            order_date = str(order['order_date']).replace('+00:00', '')
            current_order['order_id'] = order['id']
            current_order['order_date']  = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')
            current_order['order_code'] = order['order_code']
            current_order['user_number'] =getModelColumnById(SpUsers,order['user_id'],'primary_contact_number')
            current_order['town_name'] = order['town_name']
            current_order['user_name'] = order['user_name']
            current_order['route_name'] = order['route_name']
            current_order['order_status'] = order['order_status']
            current_order['order_items_count'] = order['order_items_count']

            order_item_list     = SpOrderDetails.objects.filter(order_id=order['id']).values('id','product_variant_size', 'order_id', 'product_id', 'product_name', 'product_variant_id', 'product_variant_name', 'quantity', 'rate', 'amount', 'order_date')
            order_items = []
            for order_item in order_item_list:
                current_item = {}
                container_name                      = SpProducts.objects.get(id=order_item['product_id'])
                current_item['container_name']        = container_name.container_name
                current_item['product_class_name']    = container_name.product_class_name
                current_item['product_name']        = order_item['product_name']
                current_item['product_variant_name']        = order_item['product_variant_name']
                current_item['quantity']        = order_item['quantity']
                order_items.append(current_item)

            current_order['order_item_list'] = order_items
            orders.append(current_order)
        
        if order_list:
            order_list  = orders
        else:
            order_list  = []

        status_code = 200
        response['order_list'] = order_list
    

    return JsonResponse(response,status = status_code)

@csrf_exempt
@validatePOST
@validate_logistic_api
def saveTracking(request):
    response = {}
    status_code = 200

    received_data=json.loads(request.body)
    if 'latitude' not in received_data or received_data['latitude'] == "" :
        response['message'] = "Lattitude is missing"
        status_code = 404
    if 'longitude' not in received_data or received_data['longitude'] == "" :
        response['message'] = "Longitude is missing"
        status_code = 404


    if status_code == 200 :
        api_token = request.headers['Authorization']
        vehicle = SpVehicles.objects.get(api_token=api_token)

        if vehicle.route_id is None:
            response['message'] = "Route is not assigned. please contact the administrator."
            status_code = 401
        else:
            route_id = vehicle.route_id
            driver_id = vehicle.driver_id
            vehicle_tracking = SpVehicleTracking()
            vehicle_tracking.vehicle_id = vehicle.id
            vehicle_tracking.route_id = vehicle.route_id
            vehicle_tracking.route_name = vehicle.route_name
            vehicle_tracking.driver_id = vehicle.driver_id
            vehicle_tracking.driver_name = vehicle.driver_name
            vehicle_tracking.latitude = received_data['latitude']
            vehicle_tracking.longitude = received_data['longitude']
            vehicle_tracking.save()

            if vehicle_tracking.id :
                response['message'] = "Data has been saved successfully."
                status_code = 200
            else:
                response['message'] = "Server error occurred."
                status_code = 500

    return JsonResponse(response,status = status_code)

@csrf_exempt
@validatePOST
@validate_logistic_api
def sendOrderOtp(request):
    response = {}
    status_code = 200

    received_data=json.loads(request.body)
    if 'order_id' not in received_data or received_data['order_id'] == "" :
        response['message'] = "Order# is missing"
        status_code = 404
    
    if status_code == 200 :
        api_token = request.headers['Authorization']
        vehicle = SpVehicles.objects.get(api_token=api_token)

        if vehicle.route_id is None:
            response['message'] = "Route is not assigned. please contact the administrator."
            status_code = 401
        else:
            if SpOrders.objects.filter(id=received_data['order_id']).exists():
                order = SpOrders.objects.get(id=received_data['order_id'])
                if order.order_status < 4 :
                    SpOrderOtp.objects.filter(order_id=received_data['order_id'],vehicle_id=vehicle.id).delete()
                    
                    otp = generateOTP()
                    order_otp = SpOrderOtp()
                    order_otp.vehicle_id = vehicle.id
                    order_otp.order_id = received_data['order_id']
                    order_otp.otp = otp
                    order_otp.save()

                    if order_otp.id :
                        #send sms
                        primary_contact_number =  getModelColumnById(SpUsers,order.user_id,'primary_contact_number')
                        message = "Share this OTP ("+ str(otp) +") with delivery boy for order verification."
                        sendSMS('ENQARY',primary_contact_number,message)

                        response['message'] = "OTP sent successfully."
                        status_code = 200
                    else:
                        response['message'] = "Server error occurred."
                        status_code = 500
                else:
                    response['message'] = "Server error occurred."
                    status_code = "Order already delivered. Please contact administrator."

            else:
                response['message'] = "Order not found."
                status_code = 404
    return JsonResponse(response,status = status_code)

@csrf_exempt
@validatePOST
@validate_logistic_api
def deliverOrder(request):
    response = {}
    status_code = 200

    received_data=json.loads(request.body)
    if 'order_id' not in received_data or received_data['order_id'] == "" :
        response['message'] = "Order# is missing"
        status_code = 404
    if 'otp' not in received_data or received_data['otp'] == "" :
        response['message'] = "OTP is missing"
        status_code = 404

    if status_code == 200 :
        api_token = request.headers['Authorization']
        vehicle = SpVehicles.objects.get(api_token=api_token)

        if vehicle.route_id is None:
            response['message'] = "Route is not assigned. please contact the administrator."
            status_code = 401
        else:
            if SpOrders.objects.filter(id=received_data['order_id']).exists():
                order = SpOrders.objects.get(id=received_data['order_id'])
                if order.order_status < 4 :
                    if SpOrderOtp.objects.filter(order_id=received_data['order_id'],otp=received_data['otp'],vehicle_id=vehicle.id).exists():
                        
                        #update order status
                        order.order_status = 4
                        order.save()

                        if order.id :
                            #delete otp
                            SpOrderOtp.objects.filter(order_id=received_data['order_id'],vehicle_id=vehicle.id).delete()

                            response['message'] = "Order delivered successfully."
                            status_code = 200
                        else:
                            response['message'] = "Server error occurred."
                            status_code = 500
                    else:
                        response['message'] = "Invalid OTP."
                        status_code = 400

                else:
                    response['message'] = "Order already delivered. Please contact administrator."
                    status_code = 200

            else:
                response['message'] = "Order not found."
                status_code = 404
            

    return JsonResponse(response,status = status_code)