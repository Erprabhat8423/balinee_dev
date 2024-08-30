import sys
import os
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
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

# products View
@login_required
def index(request):

    context = {}
    page = request.GET.get('page')
    schemes = SpSchemes.objects.all().order_by('-id')
    paginator = Paginator(schemes, getConfigurationResult('page_limit'))

    try:
        schemes = paginator.page(page)
    except PageNotAnInteger:
        schemes = paginator.page(1)
    except EmptyPage:
        schemes = paginator.page(paginator.num_pages)  
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

    
    last_scheme = SpSchemes.objects.order_by('-id').first()
    if last_scheme:
        scheme_users = SpUserSchemes.objects.filter(scheme_id=last_scheme.id).order_by('-id')
        page = request.GET.get('page')
        variant_paginator = Paginator(scheme_users, getConfigurationResult('page_limit'))
        try:
            scheme_users = variant_paginator.page(page)
        except PageNotAnInteger:
            scheme_users = variant_paginator.page(1)
        except EmptyPage:
            scheme_users = variant_paginator.page(variant_paginator.num_pages)  
        if page is not None:
            page = page
        else:
            page = 1
        total_scheme_users_pages = int(variant_paginator.count/getConfigurationResult('page_limit')) 
        
        if(variant_paginator.count == 0):
            variant_paginator.count = 1

        temp = total_scheme_users_pages%variant_paginator.count
        if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
            total_scheme_users_pages = total_scheme_users_pages+1
        else:
            total_scheme_users_pages = total_scheme_users_pages
        context['total_scheme_users_pages']            = total_scheme_users_pages
    else:
        scheme_users = {}
        context['total_scheme_users_pages']            = 0


   
    context['schemes']          = schemes
    context['total_pages']            = total_pages
    context['page_limit']             = getConfigurationResult('page_limit')
    context['scheme_users']   = scheme_users
    context['page_title'] = "Scheme Management"
    template = 'schemes/schemes.html'
    return render(request, template, context)


@login_required
def getSchemeUsers(request,scheme_id):
    if SpProducts.objects.filter(id=product_id).exists() :
        product_variants = SpProductVariants.objects.filter(product_id=product_id).order_by('-id')
        page = request.GET.get('page')
        variant_paginator = Paginator(product_variants, getConfigurationResult('page_limit'))
        try:
            product_variants = variant_paginator.page(page)
        except PageNotAnInteger:
            product_variants = variant_paginator.page(1)
        except EmptyPage:
            product_variants = variant_paginator.page(variant_paginator.num_pages)  
        if page is not None:
            page = page
        else:
            page = 1
        total_variant_pages = int(variant_paginator.count/getConfigurationResult('page_limit')) 
        
        if(variant_paginator.count == 0):
            variant_paginator.count = 1

        temp = total_variant_pages%variant_paginator.count
        if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
            total_variant_pages = total_variant_pages+1
        else:
            total_variant_pages = total_variant_pages
        
        context = {}
        context['page_limit']             = getConfigurationResult('page_limit')
        context['total_variant_pages']     = total_variant_pages
        context['product_variants']   = product_variants
        template = 'schemes/product-variants.html'
        return render(request, template, context)
        
    else:
        return HttpResponse('Not found')




@login_required
def ajaxSchemeList(request):
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

    template = 'role-permission/ajax-schemes.html'
    return render(request, template, context)


@login_required
def ajaxSchemeUserLists(request,product_id):
    if SpProducts.objects.filter(id=product_id).exists() :

        product_variants = SpProductVariants.objects.filter(product_id=product_id).order_by('-id')
        page = request.GET.get('page')
        variant_paginator = Paginator(product_variants, getConfigurationResult('page_limit'))
        try:
            product_variants = variant_paginator.page(page)
        except PageNotAnInteger:
            product_variants = variant_paginator.page(1)
        except EmptyPage:
            product_variants = variant_paginator.page(variant_paginator.num_pages)  
        if page is not None:
            page = page
        else:
            page = 1
        total_variant_pages = int(variant_paginator.count/getConfigurationResult('page_limit')) 
        
        if(variant_paginator.count == 0):
            variant_paginator.count = 1

        temp = total_variant_pages%variant_paginator.count
        if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
            total_variant_pages = total_variant_pages+1
        else:
            total_variant_pages = total_variant_pages
        
        context = {}
        context['page_limit']             = getConfigurationResult('page_limit')
        context['total_variant_pages']     = total_variant_pages
        context['product_variants']   = product_variants
        template = 'schemes/ajax-product-variant-lists.html'
        return render(request, template, context)

    else:
        return HttpResponse('Not found')

    





@login_required
def addScheme(request):
    template = 'schemes/add-product.html'
    context = {}
    context['product_classes']          = SpProductClass.objects.filter(status=1)
    context['product_containers']          = SpContainers.objects.all()
    return render(request, template,context)


@login_required
def saveScheme(request):
    if request.method == "POST":
        response = {}
        try:
            product_class_id = request.POST.get('product_class_id')
            product_name = request.POST.get('product_name')
            product_container_id = request.POST.get('product_container_id')

            
            if product_class_id == '':
                response['flag'] = False
                response['message'] = "Please select product class"
            if product_name == '':
                response['flag'] = False
                response['message'] = "Please enter product name"
            if SpProducts.objects.filter(product_name=product_name).exists():
                response['flag'] = False
                response['message'] = "Product name already exists"
            
            if product_container_id == '':
                response['flag'] = False
                response['message'] = "Please select container"   
            
            else:
                product = SpProducts()
                product.product_class_id = request.POST['product_class_id']
                product.product_class_name = getModelColumnById(SpProductClass,request.POST['product_class_id'],'product_class')
                product.product_name = request.POST['product_name']
                product.container_id  = request.POST['product_container_id']
                product.container_name  = getModelColumnById(SpContainers,request.POST['product_container_id'],'container')
                product.status  = 1
                product.save()

                if product.id :
                    response['flag'] = True
                    response['message'] = "Record has been successfully saved"
                else:
                    response['flag'] = False
                    response['message'] = "Failed to save"

            return JsonResponse(response)
        
        except Exception as e:
            response['flag'] = False
            response['message'] = str(e)
            return JsonResponse(response)
    else:
        response = {}
        response['error'] = False
        response['message'] = "Method not allowed"
        return JsonResponse(response)


@login_required
def editScheme(request,product_id):
    if request.method == "POST":
        response = {}
        try:
            if SpProducts.objects.filter(product_name=request.POST['product_name']).exclude(id=request.POST['product_id']).exists():
                response['flag'] = False
                response['message'] = "Product name already exist"
            else:
                product = SpProducts.objects.get(id=request.POST['product_id'])
                product.product_class_id = request.POST['product_class_id']
                product.product_class_name = getModelColumnById(SpProductClass,request.POST['product_class_id'],'product_class')
                product.product_name = request.POST['product_name']
                product.container_id  = request.POST['product_container_id']
                product.container_name  = getModelColumnById(SpContainers,request.POST['product_container_id'],'container')
                product.status  = 1
                product.save()

                if product.id :
                    response['flag'] = True
                    response['message'] = "Record has been successfully saved"
                else:
                    response['flag'] = False
                    response['message'] = "Failed to save"
        except Exception as e:
            response['error'] = False
            response['message'] = str(e)
        return JsonResponse(response)
    else:
        context = {}
        context['product']     = SpProducts.objects.get(id=product_id)
        context['product_classes']        = SpProductClass.objects.filter(status=1)
        context['product_containers']     = SpContainers.objects.all()
        context['product_units']          = SpProductUnits.objects.filter(status=1)
        
        template = 'schemes/edit-product.html'
        return render(request, template, context)




@login_required
def productUnitDetails(request,unit_id):
    response = {}
    if SpProductUnits.objects.filter(id=unit_id).exists():
        response['flag'] = True
        response['product_unit'] = model_to_dict(SpProductUnits.objects.get(id=unit_id))
    else:
        response['flag'] = False
        response['flag'] = "Unit not found"

    return JsonResponse(response)




@login_required
def updateSchemetatus(request):

    response = {}
    if request.method == "POST":
        try:
            id = request.POST.get('id')
            is_active = request.POST.get('is_active')
            data = SpProducts.objects.get(id=id)
            data.status = is_active
            data.save()
            response['error'] = False
            response['message'] = "Record has been successfully updated"
        except ObjectDoesNotExist:
            response['error'] = True
            response['message'] = "Method not allowed"
        except Exception as e:
            response['error'] = True
            response['message'] = e
        return JsonResponse(response)
    return redirect('/products')
