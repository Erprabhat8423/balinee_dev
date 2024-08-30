import sys
import os
import openpyxl
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.apps import apps
from ..models import *
from django.db.models import *
from utils import *
from datetime import datetime, date
from datetime import timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

from io import BytesIO
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.conf import settings

# Account List View
@login_required
def index(request):  
    today                   = date.today()
    today_order_status      = SpOrders.objects.filter(indent_status=1, order_date__icontains=today).count()
    order_regenerate_status = SpOrders.objects.filter(indent_status=0, order_date__icontains=today).count()

    users = SpUsers.objects.filter(user_type=2, status=1).values('id', 'first_name', 'middle_name', 'last_name')
    for user in users:
        try:
            address = SpAddresses.objects.get(user_id=user['id'], type='correspondence')
        except SpAddresses.DoesNotExist:
            address = None
        if address:
            user['address'] = address.address_line_1+', '+address.address_line_2+', '+address.city_name+', '+address.state_name+', '+address.country_name+', '+address.pincode
        else:
            user['address'] = ''

        try:
            basic_details = SpBasicDetails.objects.get(user_id=user['id'])
        except SpBasicDetails.DoesNotExist:
            basic_details = None     

        if basic_details:
            user['cin']     = basic_details.cin
            user['gstin']   = basic_details.gstin
            user['fssai']   = basic_details.fssai
        else:
            user['cin']     = ''
            user['gstin']   = ''
            user['fssai']   = ''
        try:
            route_name = SpUserAreaAllocations.objects.get(user_id=user['id'])
        except SpUserAreaAllocations.DoesNotExist:
            route_name = None
        if route_name:
            user['route_name']     = route_name.route_name
        else:
            user['route_name']     = ''

    user_list = []
    for user in users:
        orders  = SpOrders.objects.all().order_by('-id').filter(order_date__icontains=today.strftime("%Y-%m-%d"), user_id=user['id']).values_list('id', flat=True)
        users_list = {}
        if orders:
            order_details           = SpOrderDetails.objects.filter(order_id__in=orders)
            for order_detail in order_details:
                order_detail.hsn_code       = getModelColumnById(SpProducts, order_detail.product_id, 'product_hsn_code')
                order_detail.no_of_pouches  = int(order_detail.product_no_of_pouch)*int(order_detail.quantity)
            users_list['id']        = user['id']
            users_list['user_name'] = user['first_name']+' '+user['middle_name']+' '+user['last_name']
            users_list['address']   = user['address']
            users_list['cin']       = user['cin']
            users_list['gstin']     = user['gstin']
            users_list['fssai']     = user['fssai']
            users_list['route_name']= user['route_name']
            users_list['orders']    = order_details
            user_list.append(users_list)

    context = {}
    context['user_list']                    = user_list  
    context['today_date']                   = today.strftime("%d/%m/%Y")
    context['today_order_status']           = today_order_status
    context['order_regenerate_status']      = order_regenerate_status
    context['page_title']                   = "Accounts"

    template = 'accounts/index.html'
    return render(request, template, context)

# Account List View
@login_required
def invoiceList(request):
    today                   = date.today()
    today_order_status      = SpOrders.objects.filter(indent_status=1, order_date__icontains=today).count()
    order_regenerate_status = SpOrders.objects.filter(indent_status=0, order_date__icontains=today).count()

    users = SpUsers.objects.filter(user_type=2, status=1).values('id', 'first_name', 'middle_name', 'last_name')
    for user in users:
        try:
            address = SpAddresses.objects.get(user_id=user['id'], type='correspondence')
        except SpAddresses.DoesNotExist:
            address = None
        if address:
            user['address'] = address.address_line_1+', '+address.address_line_2+', '+address.city_name+', '+address.state_name+', '+address.country_name+', '+address.pincode
        else:
            user['address'] = ''

        try:
            basic_details = SpBasicDetails.objects.get(user_id=user['id'])
        except SpBasicDetails.DoesNotExist:
            basic_details = None     

        if basic_details:
            user['cin']     = basic_details.cin
            user['gstin']   = basic_details.gstin
            user['fssai']   = basic_details.fssai
        else:
            user['cin']     = ''
            user['gstin']   = ''
            user['fssai']   = ''
        try:
            route_name = SpUserAreaAllocations.objects.get(user_id=user['id'])
        except SpUserAreaAllocations.DoesNotExist:
            route_name = None
        if route_name:
            user['route_name']     = route_name.route_name
        else:
            user['route_name']     = ''

    user_list = []
    for user in users:
        orders  = SpOrders.objects.all().order_by('-id').filter(order_date__icontains=today.strftime("%Y-%m-%d"), user_id=user['id']).values_list('id', flat=True)
        users_list = {}
        if orders:
            users_list['id']        = user['id']
            users_list['user_name'] = user['first_name']+' '+user['middle_name']+' '+user['last_name']
            users_list['address']   = user['address']
            users_list['cin']       = user['cin']
            users_list['gstin']     = user['gstin']
            users_list['fssai']     = user['fssai']
            users_list['route_name']= user['route_name']
            user_list.append(users_list)

    context = {}
    context['user_list']                    = user_list  
    context['today_date']                   = today.strftime("%d/%m/%Y")
    context['today_order_status']           = today_order_status
    context['order_regenerate_status']      = order_regenerate_status
    context['page_title']                   = "Invoice List"

    template = 'accounts/invoice-list.html'
    return render(request, template, context) 

@login_required
def printInvoice(request, invoice_id):
    today                   = date.today()
    today_order_status      = SpOrders.objects.filter(indent_status=1, order_date__icontains=today).count()
    order_regenerate_status = SpOrders.objects.filter(indent_status=0, order_date__icontains=today).count()

    users = SpUsers.objects.filter(user_type=2, status=1, id=invoice_id).values('id', 'first_name', 'middle_name', 'last_name')
    for user in users:
        try:
            address = SpAddresses.objects.get(user_id=user['id'], type='correspondence')
        except SpAddresses.DoesNotExist:
            address = None
        if address:
            user['address'] = address.address_line_1+', '+address.address_line_2+', '+address.city_name+', '+address.state_name+', '+address.country_name+', '+address.pincode
        else:
            user['address'] = ''

        try:
            basic_details = SpBasicDetails.objects.get(user_id=user['id'])
        except SpBasicDetails.DoesNotExist:
            basic_details = None     

        if basic_details:
            user['cin']     = basic_details.cin
            user['gstin']   = basic_details.gstin
            user['fssai']   = basic_details.fssai
        else:
            user['cin']     = ''
            user['gstin']   = ''
            user['fssai']   = ''
        try:
            route_name = SpUserAreaAllocations.objects.get(user_id=user['id'])
        except SpUserAreaAllocations.DoesNotExist:
            route_name = None
        if route_name:
            user['route_name']     = route_name.route_name
        else:
            user['route_name']     = ''

    user_list = []
    for user in users:
        orders  = SpOrders.objects.all().order_by('-id').filter(order_date__icontains=today.strftime("%Y-%m-%d"), user_id=user['id']).values_list('id', flat=True)
        users_list = {}
        if orders:
            order_details           = SpOrderDetails.objects.filter(order_id__in=orders)
            for order_detail in order_details:
                order_detail.hsn_code       = getModelColumnById(SpProducts, order_detail.product_id, 'product_hsn_code')
                order_detail.no_of_pouches  = int(order_detail.product_no_of_pouch)*int(order_detail.quantity)
            users_list['id']        = user['id']
            users_list['user_name'] = user['first_name']+' '+user['middle_name']+' '+user['last_name']
            users_list['address']   = user['address']
            users_list['cin']       = user['cin']
            users_list['gstin']     = user['gstin']
            users_list['fssai']     = user['fssai']
            users_list['route_name']= user['route_name']
            users_list['orders']    = order_details
            user_list.append(users_list)

    context = {}
    context['user_list']                    = user_list  
    context['today_date']                   = today.strftime("%d/%m/%Y")
    context['today_order_status']           = today_order_status
    context['order_regenerate_status']      = order_regenerate_status
    context['invoice_id']                   = invoice_id
    context['page_title']                   = "Print Invoice"

    template = 'accounts/print-invoice.html'
    return render(request, template, context)

def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None


#Automaticly downloads to PDF file
@login_required
def printInvoiceTemplate(request, invoice_id):
    today                   = date.today()
    today_order_status      = SpOrders.objects.filter(indent_status=1, order_date__icontains=today).count()
    order_regenerate_status = SpOrders.objects.filter(indent_status=0, order_date__icontains=today).count()

    users = SpUsers.objects.filter(user_type=2, status=1, id=invoice_id).values('id', 'first_name', 'middle_name', 'last_name')
    for user in users:
        try:
            address = SpAddresses.objects.get(user_id=user['id'], type='correspondence')
        except SpAddresses.DoesNotExist:
            address = None
        if address:
            user['address'] = address.address_line_1+', '+address.address_line_2+', '+address.city_name+', '+address.state_name+', '+address.country_name+', '+address.pincode
        else:
            user['address'] = ''

        try:
            basic_details = SpBasicDetails.objects.get(user_id=user['id'])
        except SpBasicDetails.DoesNotExist:
            basic_details = None     

        if basic_details:
            user['cin']     = basic_details.cin
            user['gstin']   = basic_details.gstin
            user['fssai']   = basic_details.fssai
        else:
            user['cin']     = ''
            user['gstin']   = ''
            user['fssai']   = ''
        try:
            route_name = SpUserAreaAllocations.objects.get(user_id=user['id'])
        except SpUserAreaAllocations.DoesNotExist:
            route_name = None
        if route_name:
            user['route_name']     = route_name.route_name
        else:
            user['route_name']     = ''

    user_list = []
    for user in users:
        orders  = SpOrders.objects.all().order_by('-id').filter(order_date__icontains=today.strftime("%Y-%m-%d"), user_id=user['id']).values_list('id', flat=True)
        users_list = {}
        if orders:
            order_details           = SpOrderDetails.objects.filter(order_id__in=orders)
            for order_detail in order_details:
                order_detail.hsn_code       = getModelColumnById(SpProducts, order_detail.product_id, 'product_hsn_code')
                order_detail.no_of_pouches  = int(order_detail.product_no_of_pouch)*int(order_detail.quantity)
            users_list['id']        = user['id']
            users_list['user_name'] = user['first_name']+' '+user['middle_name']+' '+user['last_name']
            users_list['address']   = user['address']
            users_list['cin']       = user['cin']
            users_list['gstin']     = user['gstin']
            users_list['fssai']     = user['fssai']
            users_list['route_name']= user['route_name']
            users_list['orders']    = order_details
            user_list.append(users_list)
    today_date                      = today.strftime("%d/%m/%Y")
    baseurl = settings.BASE_URL
    pdf = render_to_pdf('accounts/print-invoice-template.html', {'user_list': user_list, 'url': baseurl, 'today_date':today_date})
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = 'Invoice.pdf'
    content = "attachment; filename=%s" %(filename)
    response['Content-Disposition'] = content
    return response
