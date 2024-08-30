import json
import time
import calendar
import pytz
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
from datetime import datetime, date
from datetime import timedelta
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.db.models import Q





#get product list
@csrf_exempt
@api_view(["POST"])
def productList(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
    product_list            = SpProducts.objects.filter(status=1).values('id', 'product_name', 'product_class_name', 'container_name').order_by('product_name')
    
    
    try:
        user_outstanding_amount = SpBasicDetails.objects.get(status=1, user_id=request.data.get("user_id"))
        outstanding_amount      = user_outstanding_amount.outstanding_amount
    except SpBasicDetails.DoesNotExist:
        outstanding_amount = None

    context = {}
    context['product_list']             = product_list
    context['shift_list']               = SpWorkingShifts.objects.all().values('id', 'working_shift').order_by('-working_shift')
    context['user_outstanding_amount']  = outstanding_amount
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)   

#get product variant list
@csrf_exempt
@api_view(["POST"])
def productVariantList(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("product_id") is None or request.data.get("product_id") == '':
        return Response({'message': 'Product Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
    if getUserRole(request.data.get("user_id")) == 'Distributor':
        product_variant_list    = SpUserProductVariants.objects.filter(product_id=int(request.data.get("product_id"))).extra(select={'rate': 'container_sp_distributor'}).values('id', 'product_id', 'item_sku_code', 'variant_quantity', 'variant_unit_id', 'variant_unit_name', 'variant_name', 'variant_size', 'no_of_pouch', 'sp_distributor', 'container_size', 'rate', 'valid_from', 'valid_to').order_by('variant_name')
    elif getUserRole(request.data.get("user_id")) == 'SuperStockist':
        product_variant_list    = SpUserProductVariants.objects.filter(product_id=int(request.data.get("product_id"))).extra(select={'rate': 'container_sp_superstockist'}).values('id', 'product_id', 'item_sku_code', 'variant_quantity', 'variant_unit_id', 'variant_unit_name', 'variant_name', 'variant_size', 'no_of_pouch', 'sp_superstockist', 'container_size', 'rate', 'valid_from', 'valid_to').order_by('variant_name')
    else:
        product_variant_list    = SpUserProductVariants.objects.filter(status=1, product_id=int(request.data.get("product_id"))).extra(select={'rate': 'container_sp_employee'}).values('id', 'product_id', 'item_sku_code', 'variant_quantity', 'variant_unit_id', 'variant_unit_name', 'variant_name', 'variant_size', 'no_of_pouch', 'sp_employee', 'container_size', 'rate', 'valid_from', 'valid_to').order_by('variant_name')

    context = {}
    context['product_variant_list']     = product_variant_list
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK) 

#save order and order details
@csrf_exempt
@api_view(["POST"])
def saveOrder(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("order_details") is None or request.data.get("order_details") == '':
        return Response({'message': 'Order Details is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("order_item_list") is None or request.data.get("order_item_list") == '':
        return Response({'message': 'Order Item Details is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("mode_of_payment") is None or request.data.get("mode_of_payment") == '':
        return Response({'message': 'Mode of Payment field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("amount_to_be_paid") is None or request.data.get("amount_to_be_paid") == '':
        return Response({'message': 'Amount field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 

    order_details   = request.data.get('order_details')
    order_item_list = request.data.get('order_item_list')

    #update user outstanding Amount
    user                        = SpBasicDetails.objects.get(user_id=request.data.get("user_id"))
    user.outstanding_amount     = order_details['remaining_outstanding_amount']
    user.save()
    
    if SpOrders.objects.count() == 0:
        last_order_id = 1
    else:
        last_order_id = SpOrders.objects.order_by('-id').first()
        last_order_id = last_order_id.id+1 

    user_area_details = SpUserAreaAllocations.objects.get(user_id=request.data.get("user_id"))

    #save order
    order                       = SpOrders()
    order.order_code            =  getConfigurationResult('org_code')+str(last_order_id)
    order.user_id               =  request.data.get("user_id")
    order.user_sap_id           =  getModelColumnById(SpUsers, request.data.get("user_id"), 'emp_sap_id')
    order.user_name             =  getModelColumnById(SpUsers, request.data.get("user_id"), 'first_name')+' '+getModelColumnById(SpUsers, request.data.get("user_id"), 'middle_name')+' '+getModelColumnById(SpUsers, request.data.get("user_id"), 'last_name')
    order.user_type             =  getUserRole(request.data.get("user_id"))
    order.route_id              =  user_area_details.route_id
    order.route_name            =  user_area_details.route_name
    order.town_id               =  user_area_details.town_id
    order.town_name             =  user_area_details.town_name
    order.mode_of_payment       =  request.data.get("mode_of_payment")
    order.amount_to_be_paid     =  request.data.get("amount_to_be_paid")
    order.order_date            =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    order.order_status          =  1
    order.order_shift_id        =  order_details['shift_id']
    order.order_shift_name      =  order_details['shift_name']
    if order_details['scheme_id'] is not None and order_details['scheme_id']!= '':
        order.order_scheme_id   =  order_details['scheme_id']
    order.order_total_amount    =  order_details['total_order_amount']
    order.order_items_count     =  order_details['items_count']
    order.save()

    #save order item details
    for order_item in order_item_list:
        item                            = SpOrderDetails()
        item.user_id                    = request.data.get("user_id")
        item.order_id                   = order.id
        item.product_id                 = order_item['product_id']
        item.product_name               = order_item['product_name']
        item.product_variant_id         = order_item['product_variant_id']
        item.product_variant_name       = order_item['product_variant_name']
        item.product_variant_size       = order_item['product_variant_size']
        item.product_no_of_pouch        = order_item['product_no_of_pouch']
        item.product_container_size     = order_item['product_container_size']
        item.product_container_type     = getModelColumnById(SpProducts, order_item['product_id'], 'container_name')
        item.quantity                   = order_item['qty']
        item.rate                       = order_item['rate']
        item.amount                     = order_item['amount']
        item.order_date                 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item.save()

    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = 'New Order('+order.order_code+') has been initiated'
    activity    = 'New Order('+order.order_code+') has been initiated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('Order Management', 'Order Summary', heading, activity, request.user.id, user_name, 'add.png', '2', 'app.png')
    sendNotificationToUsers(order.id, order.order_code, 'add', 8, request.user.id, user_name, 'SpOrders', request.user.role_id)

    context = {}
    context['message']                  = 'Order has been saved successfully.'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)

#update order and order details
@csrf_exempt
@api_view(["POST"])
def updateOrder(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("order_details") is None or request.data.get("order_details") == '':
        return Response({'message': 'Order Details is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("order_item_list") is None or request.data.get("order_item_list") == '':
        return Response({'message': 'Order Item Details is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("order_id") is None or request.data.get("order_id") == '':
        return Response({'message': 'Order Id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("mode_of_payment") is None or request.data.get("mode_of_payment") == '':
        return Response({'message': 'Mode of Payment field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("amount_to_be_paid") is None or request.data.get("amount_to_be_paid") == '':
        return Response({'message': 'Amount field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 


    order_details   = request.data.get('order_details')
    order_item_list = request.data.get('order_item_list')

    previous_order_list = SpOrderDetails.objects.filter(order_id=request.data.get("order_id")).values_list('id', flat=True)
    
    current_order_item_list = []
    for order_item in order_item_list:
        if "id" in order_item:
            current_order_item_list.append(int(order_item['id']))

    order_item_id = []
    for id, val in enumerate(previous_order_list):
        if val not in current_order_item_list:
            order_item_id.append(val)    

    #update user outstanding Amount
    user                        = SpBasicDetails.objects.get(user_id=request.data.get("user_id"))
    user.outstanding_amount     = order_details['remaining_outstanding_amount']
    user.save()
    
    user_area_details = SpUserAreaAllocations.objects.get(user_id=request.data.get("user_id"))    
    #save order
    order                       =  SpOrders.objects.get(id=request.data.get("order_id"))
    order.user_id               =  request.data.get("user_id")
    order.user_sap_id           =  getModelColumnById(SpUsers, request.data.get("user_id"), 'emp_sap_id')
    order.user_name             =  getModelColumnById(SpUsers, request.data.get("user_id"), 'first_name')+' '+getModelColumnById(SpUsers, request.data.get("user_id"), 'middle_name')+' '+getModelColumnById(SpUsers, request.data.get("user_id"), 'last_name')
    order.user_type             =  getUserRole(request.data.get("user_id"))
    order.route_id              =  user_area_details.route_id
    order.route_name            =  user_area_details.route_name
    order.town_id               =  user_area_details.town_id
    order.town_name             =  user_area_details.town_name
    order.mode_of_payment       =  request.data.get("mode_of_payment")
    order.amount_to_be_paid     =  request.data.get("amount_to_be_paid")
    order.updated_date          =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    order.order_status          =  1
    order.indent_status         =  0
    order.order_shift_id        =  order_details['shift_id']
    order.order_shift_name      =  order_details['shift_name']
    if order_details['scheme_id'] is not None and order_details['scheme_id']!= '':
        order.order_scheme_id   =  order_details['scheme_id']
    order.order_total_amount    =  order_details['total_order_amount']
    order.order_items_count     =  order_details['items_count']
    order.save()

    #save order item details
    for order_item in order_item_list:
        if "id" in order_item and int(order_item['id']) in previous_order_list :
            item                            = SpOrderDetails.objects.get(id=int(order_item['id']))
        else:
            item                            = SpOrderDetails()    
        item.user_id                    = request.data.get("user_id")
        item.order_id                   = request.data.get("order_id")
        item.product_id                 = order_item['product_id']
        item.product_name               = order_item['product_name']
        item.product_variant_id         = order_item['product_variant_id']
        item.product_variant_name       = order_item['product_variant_name']
        item.product_variant_size       = order_item['product_variant_size']
        item.product_no_of_pouch        = order_item['product_no_of_pouch']
        item.product_container_size     = order_item['product_container_size']
        item.product_container_type     = getModelColumnById(SpProducts, order_item['product_id'], 'container_name') 
        item.quantity                   = order_item['qty']
        item.rate                       = order_item['rate']
        item.amount                     = order_item['amount']
        item.order_date                 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')    
        item.save()

    #delete order items
    for order_item in order_item_id:
        SpOrderDetails.objects.filter(id=order_item).delete()

    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = 'Order('+order.order_code+') has been updated'
    activity    = 'Order('+order.order_code+') has been updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('Order Management', 'Order Summary', heading, activity, request.user.id, user_name, 'add.png', '2', 'app.png')
    context = {}
    context['message']                  = 'Order has been updated successfully.'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)    

#get order details
@csrf_exempt
@api_view(["POST"])
def orderDetails(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 

    if request.data.get("order_id") is None or request.data.get("order_id") == '':
        today   = date.today()
        try:
            order_details               = SpOrders.objects.filter(user_id=request.data.get("user_id"), order_date__icontains=today.strftime("%Y-%m-%d")).order_by('-id').first()
        except SpOrders.DoesNotExist:
            order_details = None
        if order_details:
            order_date                  = str(order_details.order_date).replace('+00:00', '')
            order_details.order_date    = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')    
        else:
            order_details               = []
    else:
        order = SpOrders.objects.filter(id=request.data.get("order_id")).exists()
        if not  order:
            return Response({'message': 'Order id not exists', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
        order_details               = SpOrders.objects.filter(id=request.data.get("order_id")).order_by('-id').first()
        order_date                  = str(order_details.order_date).replace('+00:00', '')
        order_details.order_date    = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')

    if order_details:
        order_item_list     = SpOrderDetails.objects.filter(order_id=order_details.id).values('id', 'order_id', 'product_id', 'product_name', 'product_variant_id', 'product_variant_name', 'quantity', 'rate', 'amount', 'order_date')
        for order_item in order_item_list:
            order_date = str(order_item['order_date']).replace('+00:00', '')
            container_name                      = SpProducts.objects.get(id=order_item['product_id'])
            order_item['container_name']        = container_name.container_name
            order_item['product_class_name']    = container_name.product_class_name
            order_item['order_date']            = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')
    else:
        order_item_list = []
    try:
        user_details            = SpBasicDetails.objects.get(user_id=request.data.get("user_id"))
        order_timing            = user_details.order_timing
        outstanding_amount      = user_details.outstanding_amount
        opening_crates          = user_details.opening_crates
    except SpBasicDetails.DoesNotExist:
        order_timing = getConfigurationResult('order_timing')
        outstanding_amount      = 0
        opening_crates          = 0
    
    context = {}
    if order_details:
        context['order_details']        = model_to_dict(order_details)
    else:
        context['order_details']        = order_details   
    context['order_item_list']          = order_item_list
    context['order_time']               = order_timing
    context['user_outstanding_amount']  = outstanding_amount
    context['user_opening_crates']      = opening_crates
    context['mode_of_payments']         = Sp_Mode_Of_Payments.objects.all().values('id', 'mode_of_payment').order_by('-mode_of_payment')
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)

#get order list
@csrf_exempt
@api_view(["POST"])
def orderList(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 

    if request.data.get("type") is None or request.data.get("type") == '':
        return Response({'message': 'Type field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)


    #Call function to get dates range
    current_date = date.today() 
    if request.data.get("year") is None or request.data.get("year") == '':
        year = current_date.year
    else:
        year = request.data.get("year")

    if request.data.get("month") is None or request.data.get("month") == '':
        month = current_date.month
    else:
        month = request.data.get("month")

    if request.data.get("type") == '0':
        order_list = []
        index = 0
        total_weeks = weeks_in_month(year, month)
        for week in range(total_weeks):
            week_details = {}
            index += 1

            d = date(year,month,1)
            dlt = timedelta(days = (index-1)*7)
            start_date = d + dlt
            end_date = d + dlt + timedelta(days=6)
            total_day = numberOfDays(year,month)

            if month > 9:
                last_date = str(year)+'-'+str(month)+'-'+str(total_day)
            else:
                last_date = str(year)+'-0'+str(month)+'-'+str(total_day)
                
            if str(start_date) <= str(last_date) and (int(end_date.month) == int(month) or int(start_date.month) == int(month)):
                if str(last_date) < str(end_date):
                    end_date = last_date
                elif str(start_date) == str(end_date):
                    end_date = last_date     
                else:
                    end_date = end_date
                    
                week_details['week']            = index
                week_details['start_date']      = start_date
                week_details['end_date']        = end_date
                
                order_list.append(week_details)
    elif request.data.get("type") == '2':
        if request.data.get("start_date") is None or request.data.get("start_date") == '':
            return Response({'message': 'Start date field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)

        if request.data.get("end_date") is None or request.data.get("end_date") == '':
            return Response({'message': 'End date field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)

        start_date  = request.data.get("start_date")
        end_date    = datetime.strptime(request.data.get("end_date"), "%Y-%m-%d")
        end_date    = end_date + timedelta(days=1)
        
        order_list = SpOrders.objects.filter(user_id=request.data.get("user_id"), order_date__range=[start_date, end_date]).values('id', 'order_code', 'order_date', 'order_status', 'order_shift_id', 'order_shift_name', 'order_scheme_id', 'order_total_amount', 'order_items_count')
        for order_item in order_list:
            order_date = str(order_item['order_date']).replace('+00:00', '')
            order_item['order_date']  = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')
        if order_list:
            order_list  = order_list
        else:
            order_list  = []            
    else:
        order_list = SpOrders.objects.filter(user_id=request.data.get("user_id"), order_date__year=year, order_date__month=month).values('id', 'order_code', 'order_date', 'order_status', 'order_shift_id', 'order_shift_name', 'order_scheme_id', 'order_total_amount', 'order_items_count')
        for order_item in order_list:
            order_date = str(order_item['order_date']).replace('+00:00', '')
            order_item['order_date']  = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')
        if order_list:
            order_list  = order_list
        else:
            order_list  = []
        
    context = {}
    context['order_list']               = order_list 
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK) 

@csrf_exempt
@api_view(["POST"])
def saveGrievance(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 

    if bool(request.FILES.get('attachment', False)) == True:
        uploaded_attachment = request.FILES['attachment']
        storage = FileSystemStorage()
        timestamp = int(time.time())
        attachment_name = uploaded_attachment.name
        temp = attachment_name.split('.')
        attachment_name = 'attachment_'+str(timestamp)+"."+temp[(len(temp) - 1)]
        
        attachment = storage.save(attachment_name, uploaded_attachment)
        attachment = storage.url(attachment)        
            

    data = SpGrievance()
    data.user_id                = request.data.get("user_id")
    if request.data.get("order_id"):
        order = SpOrders.objects.filter(order_code=request.data.get("order_id")).exists()
        if not  order:
            return Response({'message': 'Order id not exists', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
        data.order_id               = request.data.get('order_id')
    if request.data.get("reason_id"):
        data.reason_id              = request.data.get('reason_id')
    if request.data.get("reason_name"):
        data.reason_name            = request.data.get('reason_name')
    data.description            = request.data.get('description')
    if bool(request.FILES.get('attachment', False)) == True:
        data.attachment             = attachment
    data.save()

    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = 'New Grievance Request has been initiated'
    activity    = 'New Grievance Request has been initiated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('Order Management', 'Order Grievance Request', heading, activity, request.user.id, user_name, 'add.png', '2', 'app.png')

    context = {}
    context['message']       = 'Grievance Request has been successfully sent'
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def orderSchemeList(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
    today   = date.today()
    free_scheme = []
    quantitative_scheme = []  
    scheme_list = SpUserSchemes.objects.filter(user_id=request.data.get("user_id"), status=1)
    for scheme in scheme_list:
        free_scheme             = SpUserSchemes.objects.filter(scheme_type=1, user_id=request.data.get("user_id")).values('id', 'scheme_id', 'scheme_name', 'state_id', 'route_id', 'town_id', 'scheme_start_date', 'scheme_end_date', 'applied_on_variant_id', 'applied_on_variant_name', 'minimum_order_quantity', 'order_container_id', 'order_container_name', 'free_variant_id', 'free_variant_name', 'container_quantity', 'pouch_quantity') 
        for free in free_scheme:
            product_id             = getModelColumnById(SpProductVariants, free['free_variant_id'], 'product_id')
            free['container_type'] = getModelColumnById(SpProducts, product_id, 'container_name')
        quantitative_scheme     = SpUserSchemes.objects.filter(scheme_type=2, user_id=request.data.get("user_id")).values('id', 'scheme_id', 'scheme_name', 'state_id', 'route_id', 'town_id', 'scheme_start_date', 'scheme_end_date', 'applied_on_variant_id', 'applied_on_variant_name', 'minimum_order_quantity', 'order_container_id', 'order_container_name', 'free_variant_id', 'free_variant_name', 'container_quantity', 'pouch_quantity') 
        for quantitative in quantitative_scheme:
            product_id             = getModelColumnById(SpProductVariants, quantitative['free_variant_id'], 'product_id')
            quantitative['container_type'] = getModelColumnById(SpProducts, product_id, 'container_name')

    flat_scheme  = SpUserFlatSchemes.objects.filter(user_id=request.data.get("user_id"), status=1).values('id', 'scheme_id', 'scheme_name', 'state_id', 'route_id', 'town_id', 'scheme_start_date', 'scheme_end_date', 'incentive_amount', 'unit_id', 'unit_name') 

    bulkpack_scheme_list = SpUserBulkpackSchemes.objects.filter(user_id=request.data.get("user_id"), status=1).values('id', 'scheme_id', 'scheme_name', 'state_id', 'route_id', 'town_id', 'scheme_start_date', 'scheme_end_date', 'unit_id', 'unit_name') 
    for bulkpack_scheme in bulkpack_scheme_list:
        bulkpack_scheme['bifurcation'] = SpUserBulkpackSchemeBifurcation.objects.filter(user_id=request.data.get("user_id")).values('id', 'user_id', 'bulkpack_scheme_id', 'above_upto_quantity', 'incentive_amount')
    
    context = {}
    context['message']              = 'Success'
    context['response_code']        = HTTP_200_OK
    context['free_scheme']          = free_scheme
    context['quantitative_scheme']  = quantitative_scheme
    context['flat_scheme']          = flat_scheme
    context['bulkpack_scheme']      = bulkpack_scheme_list
    return Response(context, status=HTTP_200_OK)