import sys
import os
import json
from django.core import serializers
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
from utils import getConfigurationResult,getModelColumnById,clean_data
from io import BytesIO
from django.template.loader import get_template
from django.views import View
from django.conf import settings
from ..decorators import *


# Create your views here.

@login_required
def index(request):
    context = {}
    page = request.GET.get('page')
    if request.user.role_id == 0:
        leave_policies = SpLeavePolicies.objects.all().order_by('-id')
    else:            
        leave_policies = SpLeavePolicies.objects.filter(organization_id=request.user.organization_id).all().order_by('-id')
    for leave_policy in leave_policies:
        total_leave_count = SpLeavePolicyDetails.objects.raw(''' SELECT id, SUM(year_leave_count) as total_leave_count from sp_leave_policy_details where leave_policy_id=%s''',[leave_policy.id])
        leave_policy.total_leave_count = total_leave_count[0].total_leave_count

    paginator = Paginator(leave_policies, getConfigurationResult('page_limit'))

    try:
        leave_policies = paginator.page(page)
    except PageNotAnInteger:
        leave_policies = paginator.page(1)
    except EmptyPage:
        leave_policies = paginator.page(paginator.num_pages)  
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
    
    context['last_leave_policy'] = last_leave_policy = SpLeavePolicies.objects.all().order_by('-id').first()
    if last_leave_policy:
        last_leave_policy_details = SpLeavePolicyDetails.objects.raw(''' SELECT slpd.*,slt.leave_type FROM sp_leave_policy_details as slpd LEFT JOIN sp_leave_types as slt on slt.id = slpd.leave_type_id WHERE slpd.leave_policy_id=%s ''',[last_leave_policy.id])
        if len(last_leave_policy_details)>0:
            if last_leave_policy_details[0]:
                for last_leave_policy_detail in last_leave_policy_details :
                    swipeable_leave_types = ''
                    if int(last_leave_policy_detail.can_swipe) > 0:
                        swipeable_leave_type_list = last_leave_policy_detail.swipeable_leave_types.split(',')
                        i = 1
                        for swipeable_leave_type in swipeable_leave_type_list:
                            if i == len(swipeable_leave_type_list):
                                swipeable_leave_types += str(getModelColumnById(SpLeaveTypes,swipeable_leave_type,'leave_type'))
                            else:
                                swipeable_leave_types += str(getModelColumnById(SpLeaveTypes,swipeable_leave_type,'leave_type'))+" ,"

                            i = int(i) + 1
                            
                    last_leave_policy_detail.swipeable_leave_types = swipeable_leave_types
                
        context['last_leave_policy_details'] = last_leave_policy_details
        role_ids  = SpRoleEntityMapping.objects.filter(entity_type='leave_policy',entity_id=last_leave_policy.id).values_list('role_id',flat=True)
        context['mapped_roles'] = SpRoles.objects.filter(id__in=role_ids)

    context['total_pages'] = total_pages
    context['leave_policies'] = leave_policies
    context['page_title'] = "Manage Leave Policies"
    template = 'leaves/index.html'
    return render(request, template, context)

@login_required
def ajaxLeaveFilter(request,filter_value):
    if request.method == 'POST':
        context = {}
        page = request.GET.get('page')
        
        if filter_value and filter_value != '1':            
            leave_policies = SpLeavePolicies.objects.filter(leave_policy__icontains=filter_value)
            for leave_policy in leave_policies:
                total_leave_count = SpLeavePolicyDetails.objects.raw(''' SELECT id, SUM(year_leave_count) as total_leave_count from sp_leave_policy_details where leave_policy_id=%s''',[leave_policy.id])
                leave_policy.total_leave_count = total_leave_count[0].total_leave_count
            context['leave_policies'] = leave_policies
        else:
            leave_policies = SpLeavePolicies.objects.all().order_by('-id')
            for leave_policy in leave_policies:
                total_leave_count = SpLeavePolicyDetails.objects.raw(''' SELECT id, SUM(year_leave_count) as total_leave_count from sp_leave_policy_details where leave_policy_id=%s''',[leave_policy.id])
                leave_policy.total_leave_count = total_leave_count[0].total_leave_count
            context['leave_policies'] = leave_policies
        template = 'leaves/ajax-policy-filter.html'
        return render(request, template, context)

@login_required
def updatePolicyStatus(request):
    response = {}
    if request.method == 'POST':        
        page = request.GET.get('page')
        policyID = request.POST.getlist('policyId[]')
        if request.POST['description']:
            for policy_id in policyID:
                updatePolicyStatus = SpLeavePolicies.objects.get(id=policy_id)
                updatePolicyStatus.policy_status = request.POST['statusId']
                updatePolicyStatus.policy_description = request.POST['description']
                updatePolicyStatus.save()
            response['error'] = False
            response['message'] = "Record has been updated successfully."
            return JsonResponse(response)
        if policyID:
            for policy_id in policyID:
                updatePolicyStatus = SpLeavePolicies.objects.get(id=policy_id)
                updatePolicyStatus.policy_status = request.POST['statusId']
                # updatePolicyStatus.policy_description = request.POST['description']
                updatePolicyStatus.save()
            response['error'] = False
            response['message'] = "Record has been updated successfully."
            return JsonResponse(response)
        else:
            response['error'] = True
            response['message'] = "Record has Not been updated successfully."
            return JsonResponse(response)
        return redirect('/leave-policies')

@login_required
def ajaxLeaveFilterStatus(request,filter_value,filter_status):
    if request.method == 'POST':
        context = {}
        page = request.GET.get('page')
        
        if filter_value != 'rep1' and filter_status =='rep2':
            leave_policies = SpLeavePolicies.objects.filter(leave_policy__icontains=filter_value)
            for leave_policy in leave_policies:
                total_leave_count = SpLeavePolicyDetails.objects.raw(''' SELECT id, SUM(year_leave_count) as total_leave_count from sp_leave_policy_details where leave_policy_id=%s''',[leave_policy.id])
                leave_policy.total_leave_count = total_leave_count[0].total_leave_count
            context['leave_policies'] = leave_policies

        if filter_value =='rep1' and filter_status != 'rep2': 
            if "all_status" in filter_status:                  
                leave_policies = SpLeavePolicies.objects.all()
                for leave_policy in leave_policies:
                    total_leave_count = SpLeavePolicyDetails.objects.raw(''' SELECT id, SUM(year_leave_count) as total_leave_count from sp_leave_policy_details where leave_policy_id=%s''',[leave_policy.id])
                    leave_policy.total_leave_count = total_leave_count[0].total_leave_count
                context['leave_policies'] = leave_policies
            else:
                leave_policies = SpLeavePolicies.objects.filter(policy_status=filter_status)
                for leave_policy in leave_policies:
                    total_leave_count = SpLeavePolicyDetails.objects.raw(''' SELECT id, SUM(year_leave_count) as total_leave_count from sp_leave_policy_details where leave_policy_id=%s''',[leave_policy.id])
                    leave_policy.total_leave_count = total_leave_count[0].total_leave_count
                context['leave_policies'] = leave_policies

        if filter_value !='rep1' and filter_status != 'rep2':   
            if "all_status" in filter_status:            
                leave_policies = SpLeavePolicies.objects.filter(leave_policy__icontains=filter_value)
                for leave_policy in leave_policies:
                    total_leave_count = SpLeavePolicyDetails.objects.raw(''' SELECT id, SUM(year_leave_count) as total_leave_count from sp_leave_policy_details where leave_policy_id=%s''',[leave_policy.id])
                    leave_policy.total_leave_count = total_leave_count[0].total_leave_count
                context['leave_policies'] = leave_policies
            else:
                leave_policies = SpLeavePolicies.objects.filter(policy_status=filter_status,leave_policy__icontains=filter_value)
                for leave_policy in leave_policies:
                    total_leave_count = SpLeavePolicyDetails.objects.raw(''' SELECT id, SUM(year_leave_count) as total_leave_count from sp_leave_policy_details where leave_policy_id=%s''',[leave_policy.id])
                    leave_policy.total_leave_count = total_leave_count[0].total_leave_count
                context['leave_policies'] = leave_policies

        if filter_value =='rep1' and filter_status == 'rep2':
            leave_policies = SpLeavePolicies.objects.all().order_by('-id')
            for leave_policy in leave_policies:
                total_leave_count = SpLeavePolicyDetails.objects.raw(''' SELECT id, SUM(year_leave_count) as total_leave_count from sp_leave_policy_details where leave_policy_id=%s''',[leave_policy.id])
                leave_policy.total_leave_count = total_leave_count[0].total_leave_count
            context['leave_policies'] = leave_policies
        template = 'leaves/ajax-policy-filter.html'
        return render(request, template, context)



@login_required
def addLeavePolicy(request):
    if request.method == "POST":
        context = {}
        leave_policy_name       = clean_data(request.POST['leave_policy'])
        if SpLeavePolicies.objects.filter(leave_policy=leave_policy_name).exists():
            context['flag'] = False
            context['message'] = "Leave Policy already exists."
        elif SpRoleEntityMapping.objects.filter(role_id__in = request.POST.getlist('filter_role[]') , entity_type = "leave_policy").exists():
            context['flag'] = False
            context['message'] = "Leave Policy already exists this roles."
        else:
            if request.POST.getlist('filter_org_name[]'):
                for organization_id in request.POST.getlist('filter_org_name[]'):
                    org_name = getModelColumnById(SpOrganizations,organization_id,'organization_name')
                    leave_policy = SpLeavePolicies()
                    leave_policy.leave_policy = clean_data(request.POST['leave_policy'])
                    leave_policy.organization_id = organization_id
                    leave_policy.organization_name = org_name
                    leave_policy.status = 1
                    leave_policy.policy_status = 1
                    leave_policy.save()
                    if request.user.role_id == 0:
                            SpLeavePolicies.objects.filter(id=leave_policy.id).update(policy_status=3)
                    else:
                        sendNotificationToUsers(leave_policy.id, '', "add" , 32, request.user.id, request.user.first_name+" "+request.user.middle_name+" "+request.user.last_name, "SpLeavePolicies", request.user.role_id)
                    if leave_policy.id:
                        leave_type       = request.POST.getlist('leave_type[]')
                        year_leave_count       = request.POST.getlist('year_leave_count[]')
                        month_leave_count       = request.POST.getlist('month_leave_count[]')
                        consecutive_leave       = request.POST.getlist('consecutive_leave[]')
                        is_carry_forward       = request.POST.getlist('is_carry_forward[]')
                        is_salary_affecting       = request.POST.getlist('is_salary_affecting[]')
                        is_halfday_included       = request.POST.getlist('is_halfday_included[]')
                        can_swipe       = request.POST.getlist('can_swipe[]')
                       
                        apply_leave_before          = request.POST.getlist('apply_leave_before[]')
                        is_fraction_leave           = request.POST.getlist('is_fraction_leave[]')
                        is_avial_advance_leaved     = request.POST.getlist('is_avial_advance_leaved[]')
                        is_document_required        = request.POST.getlist('is_document_required[]')
                

                        for id, val in enumerate(leave_type):
                            if id != "":
                                leave_policy_details = SpLeavePolicyDetails()
                                leave_policy_details.leave_policy_id = leave_policy.id
                                leave_policy_details.leave_type_id = leave_type[id]
                                leave_policy_details.year_leave_count = clean_data(year_leave_count[id])
                                leave_policy_details.month_leave_count = clean_data(month_leave_count[id])
                                leave_policy_details.consecutive_leave = clean_data(consecutive_leave[id])
                                leave_policy_details.is_salary_affecting = is_salary_affecting[id]
                                leave_policy_details.is_carry_forward = is_carry_forward[id]
                                leave_policy_details.is_halfday_included = is_halfday_included[id]
                                leave_policy_details.can_swipe = can_swipe[id]
                                if apply_leave_before[id]:
                                    leave_policy_details.apply_leave_before         = apply_leave_before[id]
                                    
                                leave_policy_details.is_fraction_leave          = is_fraction_leave[id]
                                leave_policy_details.is_avial_advance_leave     = is_avial_advance_leaved[id]
                                leave_policy_details.is_document_required       = is_document_required[id]
                                
                                if int(can_swipe[id]) == 1:
                                    swipeable_leave_types_var = 'swipeable_leave_types_'+str(id)+'[]'
                                    leave_policy_details.swipeable_leave_types = ','.join(request.POST.getlist(swipeable_leave_types_var))
                                
                                leave_policy_details.save()
                                context['flag'] = True
                                context['message'] = "Record has been save successfully."
                    else:
                        context['flag'] = False
                        context['message'] = "Failed to save record."

            if request.POST.getlist('filter_role[]'):                
                role_id_to_mapped = request.POST.getlist('filter_role[]')
                leave_policy_id = SpLeavePolicies.objects.filter(leave_policy=leave_policy_name).values('id')
                if 'all' in role_id_to_mapped:
                    for org_id in request.POST.getlist('filter_org_name[]'):
                        for roleId in SpRoles.objects.filter(organization_id=org_id):
                            mapping =  SpRoleEntityMapping()
                            mapping.entity_type = "leave_policy"
                            mapping.role_id = roleId.id
                            mapping.entity_id = leave_policy.id
                            mapping.save()
                else:
                    for id in leave_policy_id:
                        leave_policy_id= id['id']
                        for roleId in role_id_to_mapped:                            
                            mapping =  SpRoleEntityMapping()
                            mapping.entity_type = "leave_policy"
                            mapping.role_id = roleId
                            mapping.entity_id = id['id']
                            mapping.save()
        return JsonResponse(context)
    else:
        context = {}
        context['leave_types'] = SpLeaveTypes.objects.filter(status=1)
        context['range'] = range(1,101)
        if request.user.role_id == 0:
            context['institution_names'] = SpOrganizations.objects.all()            
        else:
            context['institution_names'] = SpOrganizations.objects.filter(id=request.user.organization_id)
        template = 'leaves/add-leave-policy.html'
        return render(request, template, context)


@login_required
def editLeavePolicy(request,leave_policy_id):
    leavePolicyId = leave_policy_id
    if request.method == "POST":
        context = {}
        leave_policy_name       = clean_data(request.POST['leave_policy'])
        leave_policy_id         = request.POST['leave_policy_id']
        filter_org_id           = request.POST['filter_org_name']

        if SpLeavePolicies.objects.filter(leave_policy=leave_policy_name,organization_id=filter_org_id).exclude(id=leave_policy_id).exists():
            context['flag'] = False
            context['message'] = "Leave Policy already exists."
        elif SpRoleEntityMapping.objects.filter(role_id__in = request.POST.getlist('filter_role[]') , entity_type = "leave_policy").exclude(entity_id=leave_policy_id).exists():
            context['flag'] = False
            context['message'] = "Leave Policy already exists this roles."
        else:
            leave_policy = SpLeavePolicies.objects.get(id=leave_policy_id)
            leave_policy.organization_id = filter_org_id
            leave_policy.organization_name = getModelColumnById(SpOrganizations,filter_org_id,'organization_name')
            leave_policy = SpLeavePolicies.objects.get(id=leave_policy_id)
            leave_policy.leave_policy = clean_data(request.POST['leave_policy'])
            leave_policy.status = 1
            leave_policy.save()

            SpRoleEntityMapping.objects.filter(entity_type="leave_policy",entity_id=leave_policy_id).delete()

            role_id_to_mapped = request.POST.getlist('filter_role[]')                
            

            if 'all' in role_id_to_mapped:
                for roleId in SpRoles.objects.filter(organization_id=filter_org_id):
                    mapping =  SpRoleEntityMapping()
                    mapping.entity_type = "leave_policy"
                    mapping.role_id = roleId.id
                    mapping.entity_id = leave_policy_id 
                    mapping.save()
            else:            
                for roleId in role_id_to_mapped:
                    mapping =  SpRoleEntityMapping()
                    mapping.entity_type = 'leave_policy'
                    mapping.role_id = roleId
                    mapping.entity_id = leave_policy_id
                    mapping.save()
        
            if leave_policy.id:

                leave_type                  = request.POST.getlist('leave_type[]')
                year_leave_count            = request.POST.getlist('year_leave_count[]')
                month_leave_count           = request.POST.getlist('month_leave_count[]')
                consecutive_leave           = request.POST.getlist('consecutive_leave[]')
                is_carry_forward            = request.POST.getlist('is_carry_forward[]')
                is_salary_affecting         = request.POST.getlist('is_salary_affecting[]')
                is_halfday_included         = request.POST.getlist('is_halfday_included[]')
                
                apply_leave_before          = request.POST.getlist('apply_leave_before[]')
                is_fraction_leave           = request.POST.getlist('is_fraction_leave[]')
                is_avial_advance_leaved     = request.POST.getlist('is_avial_advance_leaved[]')
                is_document_required        = request.POST.getlist('is_document_required[]')
                
                can_swipe       = request.POST.getlist('can_swipe[]')

                #delete old record
                SpLeavePolicyDetails.objects.filter(leave_policy_id=leave_policy_id).delete()

                for id, val in enumerate(leave_type):
                    if id != "":
                        leave_policy_details = SpLeavePolicyDetails()
                        leave_policy_details.leave_policy_id = leave_policy_id
                        leave_policy_details.leave_type_id = leave_type[id]
                        leave_policy_details.year_leave_count = clean_data(year_leave_count[id])
                        leave_policy_details.month_leave_count = clean_data(month_leave_count[id])
                        leave_policy_details.consecutive_leave = clean_data(consecutive_leave[id])
                        leave_policy_details.is_salary_affecting = is_salary_affecting[id]
                        leave_policy_details.is_carry_forward = is_carry_forward[id]
                        leave_policy_details.is_halfday_included = is_halfday_included[id]
                        leave_policy_details.can_swipe = can_swipe[id]
                        
                        if apply_leave_before[id]:
                            leave_policy_details.apply_leave_before         = apply_leave_before[id]
                        leave_policy_details.is_fraction_leave          = is_fraction_leave[id]
                        leave_policy_details.is_avial_advance_leave     = is_avial_advance_leaved[id]
                        leave_policy_details.is_document_required       = is_document_required[id]
                        
                        if int(can_swipe[id]) == 1:
                            swipeable_leave_types_var = 'swipeable_leave_types_'+str(id)+'[]'
                            leave_policy_details.swipeable_leave_types = ','.join(request.POST.getlist(swipeable_leave_types_var))
                        leave_policy_details.save()

                context['flag'] = True
                context['message'] = "Record has been updated successfully."
            else:
                context['flag'] = False
                context['message'] = "Failed to update record."

        return JsonResponse(context)
    else:
        context = {}
        if request.user.role_id == 0:
            context['institution_names'] = SpOrganizations.objects.all()
        else:
            context['institution_names'] = SpOrganizations.objects.filter(id=request.user.organization_id)
        
        context['role_mappings'] = SpRoleEntityMapping.objects.filter(entity_type='leave_policy',entity_id=leave_policy_id).values_list('role_id',flat=True)
        context['leave_policy'] = leave_policy = SpLeavePolicies.objects.get(id=leave_policy_id)
        context['role_names'] = SpRoles.objects.filter(organization_id=leave_policy.organization_id)
        context['leave_policy_details'] = SpLeavePolicyDetails.objects.filter(leave_policy_id=leave_policy.id)
        context['leave_types'] = SpLeaveTypes.objects.filter(status=1)
        context['range'] = range(1,101)
        template = 'leaves/edit-leave-policy.html'
        return render(request, template, context)




@login_required
def leavePolicyShortDetails(request,leave_policy_id):
    context = {}
    context['leave_policy'] = SpLeavePolicies.objects.get(id=leave_policy_id)
    last_leave_policy_details = SpLeavePolicyDetails.objects.raw(''' SELECT slpd.*,slt.leave_type FROM sp_leave_policy_details 
    as slpd
    LEFT JOIN sp_leave_types as slt on slt.id = slpd.leave_type_id WHERE slpd.leave_policy_id=%s ''',[leave_policy_id])
    if last_leave_policy_details[0]:
        for last_leave_policy_detail in last_leave_policy_details :
            swipeable_leave_types = ''
            if int(last_leave_policy_detail.can_swipe) > 0:
                swipeable_leave_type_list = last_leave_policy_detail.swipeable_leave_types.split(',')
                i = 1
                for swipeable_leave_type in swipeable_leave_type_list:
                    if i == len(swipeable_leave_type_list):
                        swipeable_leave_types += str(getModelColumnById(SpLeaveTypes,swipeable_leave_type,'leave_type'))
                    else:
                        swipeable_leave_types += str(getModelColumnById(SpLeaveTypes,swipeable_leave_type,'leave_type'))+" ,"

                    i = int(i) + 1
            last_leave_policy_detail.swipeable_leave_types = swipeable_leave_types

    context['role_mappings'] = SpRoleEntityMapping.objects.filter(entity_type='leave_policy',entity_id=leave_policy_id).values_list('role_id',flat=True)
    context['last_leave_policy_details'] = last_leave_policy_details
    
    role_ids  = SpRoleEntityMapping.objects.filter(entity_type='leave_policy',entity_id=leave_policy_id).values_list('role_id',flat=True)
    context['mapped_roles'] = SpRoles.objects.filter(id__in=role_ids)
    
    template = 'leaves/leave-policy-short-details.html'
    return render(request, template, context)






@login_required
def ajaxLeavePolicyRows(request):

    page = request.GET.get('page')
    leave_policies = SpLeavePolicies.objects.all().order_by('-id')
    paginator = Paginator(leave_policies, getConfigurationResult('page_limit'))

    try:
        leave_policies = paginator.page(page)
    except PageNotAnInteger:
        leave_policies = paginator.page(1)
    except EmptyPage:
        leave_policies = paginator.page(paginator.num_pages)  
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
    context['leave_policies']     = leave_policies
    context['total_pages']       = total_pages

    template = 'leaves/ajax-leave-policy-rows.html'
    return render(request, template, context)

@login_required
def updateLeavePolicyStatus(request):

    response = {}
    if request.method == "POST":
        try:
            id = request.POST.get('id')
            is_active = request.POST.get('is_active')

            data = SpLeavePolicies.objects.get(id=id)
            data.status = is_active
            data.save()
            response['error'] = False
            response['message'] = "Record has been updated successfully."
        except ObjectDoesNotExist:
            response['error'] = True
            response['message'] = "Method not allowed"
        except Exception as e:
            response['error'] = True
            response['message'] = e
        return JsonResponse(response)
    return redirect('/roles')