import sys
import os
import time,json
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.apps import apps
from ..models import *
from django.db.models import Q,F
from utils import *
from datetime import datetime, date,timedelta
from django.core import serializers

from django.views import View
from django.conf import settings
import calendar 


# Create your views here.

#ajax customer list
@login_required
def index(request):
    page = request.GET.get('page')

    customers = list(SpUsers.objects.raw(''' SELECT id,first_name,middle_name, last_name,emp_sap_id,official_email,primary_contact_number FROM sp_users 
    WHERE id IN (SELECT DISTINCT customer_id FROM sp_customer_vacations) '''))
    paginator = Paginator(customers, getConfigurationResult('page_limit'))

    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)  
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

    context = {}

    current_date = date.today() 
    context['current_year'] = current_year = current_date.year
    context['current_month'] = current_month = current_date.month
    
    if int(current_month) == 12:
        context['next_month'] = 1
    else:
        context['next_month'] = int(current_month) + 1
    if int(current_month) == 1:
        context['previous_month'] = 12
    else:
        context['previous_month'] = int(current_month) - 1
    
    context['current_month_name'] = calendar.month_name[current_month]

    if len(customers):

        customer_id = customers[0].id
        last_customer = SpUsers.objects.raw(''' SELECT id,first_name,middle_name,last_name,emp_sap_id FROM sp_users 
                        WHERE id = %s ''',[customer_id])[0]

        calendarObj = calendar.Calendar()
        calendar_dates = []
        for week in calendarObj.monthdatescalendar(current_year, current_month):
            dates = []
            for week_date in week:
                tmp = {}
                tmp['full_date'] = week_date
                tmp['day'] = week_date.strftime('%A')
                tmp['short_date'] = week_date.strftime('%d')
                tmp['month'] = week_date.strftime('%m')
                if SpCustomerVacations.objects.filter(customer_id=customer_id,vacation_date=week_date).exists():
                    tmp['is_vacation'] = 1
                else:
                    tmp['is_vacation'] = 0
                
                if SpCustomerOrders.objects.filter(user_id=customer_id,is_subscribed=1, expected_delivery_date=week_date).exclude(order_status=5).exists():
                    tmp['is_disabled'] = 0
                else:
                    tmp['is_disabled'] = 1
                
                if current_date > week_date:
                    tmp['is_disabled'] = 1
                    
                dates.append(tmp)

            calendar_dates.append(dates)

        context['calendar_dates'] = calendar_dates
        context['customer'] = last_customer

    context['customers'] = customers
    context['localities'] = SpTowns.objects.all()
    context['total_pages'] = total_pages
    context['page_limit'] = getConfigurationResult('page_limit')
    context['page_title'] = "Manage Vacations"
    template = 'vacation/index.html'
    return render(request, template, context)

@login_required
def filterVacation(request):

    page = request.GET.get('page')
    condition = ""
    if 'search' in request.POST and request.POST['search'] != "":
        condition += " and (sp_users.first_name LIKE '%%"+request.POST['search']+"%%' OR sp_users.primary_contact_number LIKE '%%"+request.POST['search']+"%%' OR sp_users.emp_sap_id LIKE '%%"+request.POST['search']+"%%') " 
    if 'locality_id' in request.POST and request.POST['locality_id'] != "":
        condition += " and sp_addresses.town_id="+request.POST['locality_id']

    customers = list(SpUsers.objects.raw(''' SELECT sp_users.id,sp_users.first_name,sp_users.middle_name, sp_users.last_name,sp_users.emp_sap_id,sp_users.official_email,sp_users.primary_contact_number FROM sp_users 
    LEFT JOIN sp_addresses on sp_addresses.user_id = sp_users.id 
    WHERE sp_users.id IN (SELECT DISTINCT customer_id FROM sp_customer_vacations) and 1 {condition} GROUP BY sp_addresses.user_id '''.format(condition=condition)))
    paginator = Paginator(customers, getConfigurationResult('page_limit'))

    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)  
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

    context = {}

    current_date = date.today() 
    context['current_year'] = current_year = current_date.year
    context['current_month'] = current_month = current_date.month
    
    if int(current_month) == 12:
        context['next_month'] = 1
    else:
        context['next_month'] = int(current_month) + 1
    if int(current_month) == 1:
        context['previous_month'] = 12
    else:
        context['previous_month'] = int(current_month) - 1
    
    context['current_month_name'] = calendar.month_name[current_month]

    if len(customers):

        customer_id = customers[0].id
        last_customer = SpUsers.objects.raw(''' SELECT id,first_name,middle_name,last_name,emp_sap_id FROM sp_users 
                        WHERE id = %s ''',[customer_id])[0]

        calendarObj = calendar.Calendar()
        calendar_dates = []
        for week in calendarObj.monthdatescalendar(current_year, current_month):
            dates = []
            for week_date in week:
                tmp = {}
                tmp['full_date'] = week_date
                tmp['day'] = week_date.strftime('%A')
                tmp['short_date'] = week_date.strftime('%d')
                tmp['month'] = week_date.strftime('%m')
                if SpCustomerVacations.objects.filter(customer_id=customer_id,vacation_date=week_date).exists():
                    tmp['is_vacation'] = 1
                else:
                    tmp['is_vacation'] = 0
                
                if SpCustomerOrders.objects.filter(user_id=customer_id,is_subscribed=1, expected_delivery_date=week_date).exclude(order_status=5).exists():
                    tmp['is_disabled'] = 0
                else:
                    tmp['is_disabled'] = 1
                
                if current_date > week_date:
                    tmp['is_disabled'] = 1
                    
                dates.append(tmp)

            calendar_dates.append(dates)

        context['calendar_dates'] = calendar_dates
        context['customer'] = last_customer

    context['customers'] = customers
    context['total_pages'] = total_pages
    context['page_limit'] = getConfigurationResult('page_limit')
    template = 'vacation/filter-vacations.html'

    return render(request, template, context)
    

@login_required
def customerVacationCalendar(request,customer_id):
    context = {}
    calendarObj = calendar.Calendar()
    current_date = date.today() 
    if 'year' in request.GET and int(request.GET.get('year')) != "":
        context['current_year'] = current_year = int(request.GET.get('year'))
    else:
        context['current_year'] = current_year = current_date.year
    
    if 'month' in request.GET and int(request.GET.get('month')) != "":
        context['current_month'] = current_month = int(request.GET.get('month'))
    else:
        context['current_month'] = current_month = current_date.month

    if int(current_month) == 12:
        context['next_month'] = 1
    else:
        context['next_month'] = int(current_month) + 1
    if int(current_month) == 1:
        context['previous_month'] = 12
    else:
        context['previous_month'] = int(current_month) - 1

    context['current_month_name'] = calendar.month_name[current_month]

    context['week_days'] =  ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    calendar_dates = []
    for week in calendarObj.monthdatescalendar(current_year, current_month):
        dates = []
        for week_date in week:
            tmp = {}
            tmp['full_date'] = week_date
            tmp['day'] = week_date.strftime('%A')
            tmp['short_date'] = week_date.strftime('%d')
            tmp['month'] = week_date.strftime('%m')
            
            
            if SpCustomerVacations.objects.filter(customer_id=customer_id,vacation_date=week_date).exists():
                tmp['is_vacation'] = 1
            else:
                tmp['is_vacation'] = 0
                
            if SpCustomerOrders.objects.filter(user_id=customer_id,is_subscribed=1, expected_delivery_date=week_date).exclude(order_status=5).exists():
                tmp['is_disabled'] = 0
            else:
                tmp['is_disabled'] = 1
            
            if current_date > week_date:
                tmp['is_disabled'] = 1
                
            dates.append(tmp)

        calendar_dates.append(dates)

    context['calendar_dates'] = calendar_dates
    
    context['customer'] = SpUsers.objects.raw(''' SELECT id,first_name,middle_name,last_name,emp_sap_id FROM sp_users 
    WHERE id = %s ''',[customer_id])[0]

    template = 'vacation/customer-vacation-calendar.html'
    return render(request, template, context)

@login_required
def updateCustomerVacation(request):
    if request.method == "POST":
        response = {}

        vacation_dates       = request.POST.getlist('vacation_date[]')

        customer_name = ''
        if getModelColumnById(SpUsers, request.POST['customer_id'], 'first_name'):
            customer_name += str(getModelColumnById(SpUsers, request.POST['customer_id'], 'first_name'))
        if getModelColumnById(SpUsers, request.POST['customer_id'], 'middle_name'):
            customer_name += ' '+str(getModelColumnById(SpUsers, request.POST['customer_id'], 'middle_name'))    
        if getModelColumnById(SpUsers, request.POST['customer_id'], 'last_name'):
            customer_name += ' '+str(getModelColumnById(SpUsers, request.POST['customer_id'], 'last_name'))

        for id, val in enumerate(vacation_dates):
            
            if not SpCustomerVacations.objects.filter(customer_id=request.POST['customer_id'],vacation_date=vacation_dates[id]).exists():
                vacation = SpCustomerVacations()
                vacation.customer_id = request.POST['customer_id']
                vacation.customer_name = customer_name
                vacation.vacation_date = vacation_dates[id]
                vacation.marked_by = request.user.id
                vacation.status = 1 
                vacation.save()

                if SpCustomerOrders.objects.filter(user_id=request.POST['customer_id'],is_subscribed=1,expected_delivery_date=vacation_dates[id]).exists():
                    orders = SpCustomerOrders.objects.filter(user_id=request.POST['customer_id'],is_subscribed=1,expected_delivery_date=vacation_dates[id])
                    for order in orders:
                        subscription = SpSubscriptions.objects.get(id=order.subscription_id)
                        last_order = SpCustomerOrders.objects.filter(user_id=request.POST['customer_id']).order_by('-id').first()
                        if subscription.plan_type == "daily":
                            
                            date = (last_order.expected_delivery_date + timedelta(days=1)).strftime('%Y-%m-%d')
                            saveSubscriptionOrder(subscription.id,date)
                            
                            #cancel old order 
                            SpCustomerOrders.objects.filter(user_id=request.POST['customer_id'],expected_delivery_date=vacation_dates[id]).update(order_status=5)
                        elif subscription.plan_type == "alternate_day":
                            date = (last_order.expected_delivery_date + timedelta(days=2)).strftime('%Y-%m-%d')
                            saveSubscriptionOrder(subscription.id,date)
                            
                            #cancel old order 
                            SpCustomerOrders.objects.filter(user_id=request.POST['customer_id'],expected_delivery_date=vacation_dates[id]).update(order_status=5)
                        else:
                            selected_days = subscription.plan_days.split(',')
                            order_date = last_order.expected_delivery_date
                            new_date = returnDateSelectedDays(selected_days,order_date)
                            print(new_date)
                            saveSubscriptionOrder(subscription.id,new_date)
                            
                            #cancel old order 
                            SpCustomerOrders.objects.filter(user_id=request.POST['customer_id'],expected_delivery_date=vacation_dates[id]).update(order_status=5)



                        




        response['flag'] = True
        response['message'] = "Record updated successfully."
        response['customer_id'] = request.POST['customer_id']
        return JsonResponse(response)
    else:
        response = {}
        response['flag'] = False
        response['message'] = "Method not allowed"
        return JsonResponse(response)


@login_required
def searchCustomer(request):
    keyword = request.GET['term']
    response = {}
    customers = []
    if 'term' in request.GET and keyword != "":
        if SpUsers.objects.filter(Q(first_name__icontains=keyword) | Q(primary_contact_number__contains=keyword) | Q(emp_sap_id__icontains=keyword),user_type=4).exists():
            users = SpUsers.objects.filter(Q(first_name__icontains=keyword) | Q(primary_contact_number__contains=keyword),user_type=4)
            for user in users:
                tmp = {}
                tmp['id'] = user.id
                user_name = user.first_name+' '
                if user.middle_name is not None:
                   user_name += user.middle_name+' '
                user_name += user.last_name 
                tmp['label'] = user_name + '('+ user.emp_sap_id +')'
                tmp['value'] = user.id
                customers.append(tmp)

    response['results'] = customers
    return JsonResponse(response)