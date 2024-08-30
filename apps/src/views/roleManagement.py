import sys
import os
import json,time
from django.core.files.storage import FileSystemStorage
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import make_password
from django.core import serializers
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.apps import apps
from ..models import *
from django.db.models import Q
from utils import getConfigurationResult,getModelColumnById
from datetime import datetime
from datetime import timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from django.utils.text import slugify

from io import BytesIO
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.conf import settings
from ..decorators import *
from django.core.files.storage import FileSystemStorage

# Create your views here.

# roleManagement View
@login_required
# @has_par(sub_module_id=2,permission='list')
def index(request):
    context = {}
    
    page = request.GET.get('page')
    roles = SpRoles.objects.all().order_by('-id')
    paginator = Paginator(roles, getConfigurationResult('page_limit'))

    try:
        roles = paginator.page(page)
    except PageNotAnInteger:
        roles = paginator.page(1)
    except EmptyPage:
        roles = paginator.page(paginator.num_pages)  
    if page is not None:
           page = page
    else:
           page = 1
    
    total_pages = int(paginator.count/getConfigurationResult('page_limit')) 
    if(paginator.count == 0):
        paginator.count = 1
        
    temp = int(total_pages) % paginator.count
    if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
        total_pages = total_pages+1
    else:
        total_pages = total_pages
        
        
    role_details = SpRoles.objects.order_by('-id').first()
    if role_details:

        context['role_leave_policy_mapping'] = role_leave_policy_mapping = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_leave_policies.leave_policy FROM sp_role_entity_mapping
                    LEFT JOIN sp_leave_policies on sp_leave_policies.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="leave_policy" ''', [role_details.id])

        context['role_attendance_group_mapping'] = role_attendance_group_mapping = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_attendance_groups.attendance_group FROM sp_role_entity_mapping
                    LEFT JOIN sp_attendance_groups on sp_attendance_groups.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="attendance_group" ''', [role_details.id])
        context['role_pay_band_mapping'] = role_pay_band_mapping = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_pay_bands.pay_band FROM sp_role_entity_mapping
                    LEFT JOIN sp_pay_bands on sp_pay_bands.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="pay_band" ''', [role_details.id])

        context['role_holiday_mappings'] = role_holiday_mappings = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_holidays.holiday FROM sp_role_entity_mapping
                    LEFT JOIN sp_holidays on sp_holidays.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="holiday" ''', [role_details.id])

        context['role_salary_addition_mappings'] = role_salary_addition_mappings = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_salary_addition_types.addition FROM sp_role_entity_mapping
                    LEFT JOIN sp_salary_addition_types on sp_salary_addition_types.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="salary_addition" ''', [role_details.id])

        context['role_salary_deduction_mappings'] = role_salary_deduction_mappings = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_salary_deduction_types.deduction FROM sp_role_entity_mapping
                    LEFT JOIN sp_salary_deduction_types on sp_salary_deduction_types.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="salary_deduction" ''', [role_details.id])        


    context['roles'] = roles
    context['total_pages'] = total_pages
    context['page_limit'] = getConfigurationResult('page_limit')
    context['role_details'] = role_details
    
    context['page_title'] = "Manage Roles"
    template = 'role-permission/role-management/roles.html'

    return render(request, template, context)




@login_required
def roleDetails(request,role_id):
    context = {}
    role_details = SpRoles.objects.get(id=role_id)

    context['role_details'] = role_details
    context['role_leave_policy_mapping'] = role_leave_policy_mapping = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_leave_policies.leave_policy FROM sp_role_entity_mapping
                    LEFT JOIN sp_leave_policies on sp_leave_policies.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="leave_policy" ''', [role_details.id])

    context['role_attendance_group_mapping'] = role_attendance_group_mapping = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_attendance_groups.attendance_group FROM sp_role_entity_mapping
                    LEFT JOIN sp_attendance_groups on sp_attendance_groups.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="attendance_group" ''', [role_details.id])
    context['role_pay_band_mapping'] = role_pay_band_mapping = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_pay_bands.pay_band FROM sp_role_entity_mapping
                    LEFT JOIN sp_pay_bands on sp_pay_bands.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="pay_band" ''', [role_details.id])

    context['role_holiday_mappings'] = role_holiday_mappings = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_holidays.holiday FROM sp_role_entity_mapping
                    LEFT JOIN sp_holidays on sp_holidays.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="holiday" ''', [role_details.id])

    context['role_salary_addition_mappings'] = role_salary_addition_mappings = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_salary_addition_types.addition FROM sp_role_entity_mapping
                    LEFT JOIN sp_salary_addition_types on sp_salary_addition_types.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="salary_addition" ''', [role_details.id])

    context['role_salary_deduction_mappings'] = role_salary_deduction_mappings = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_salary_deduction_types.deduction FROM sp_role_entity_mapping
                    LEFT JOIN sp_salary_deduction_types on sp_salary_deduction_types.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="salary_deduction" ''', [role_details.id])
    
    template = 'role-permission/role-management/role-details.html'

    return render(request, template, context)


@login_required
def ajaxRoleList(request):
    page = request.GET.get('page')
    roles = SpRoles.objects.all().order_by('-id')
    paginator = Paginator(roles, getConfigurationResult('page_limit'))

    try:
        roles = paginator.page(page)
    except PageNotAnInteger:
        roles = paginator.page(1)
    except EmptyPage:
        roles = paginator.page(paginator.num_pages)  
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

    organization_details = SpRoles.objects.order_by('-id').first()

    return render(request, 'role-permission/role-management/ajax-roles.html', {'roles': roles, 'total_pages':total_pages, 'organization_details': organization_details})


@login_required
def ajaxRoleLists(request):
    page = request.GET.get('page')

    roles = SpRoles.objects.all().order_by('-id')
    paginator = Paginator(roles, getConfigurationResult('page_limit'))

    try:
        roles = paginator.page(page)
    except PageNotAnInteger:
        roles = paginator.page(1)
    except EmptyPage:
        roles = paginator.page(paginator.num_pages)  
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

    return render(request, 'role-permission/role-management/ajax-organization-lists.html', {'roles': roles, 'total_pages':total_pages})





@login_required
# @has_par(sub_module_id=2,permission=2)
def addRole(request):
    if request.method == "POST":
        response = {}
        if SpRoles.objects.filter(department_id=request.POST['department_id'], role_name=request.POST['role_name']).exists():
            response['message'] = "Role already exist"
            response['flag'] = False
        else:
            role = SpRoles()
            role.organization_id = request.POST['organization_id']
            role.organization_name = getModelColumnById(SpOrganizations,request.POST['organization_id'],'organization_name')
            role.department_id = request.POST['department_id']
            role.department_name = getModelColumnById(SpDepartments,request.POST['department_id'],'department_name')
            role.role_name = request.POST['role_name']
            role.responsibilities = request.POST['responsibilities']

            if request.POST['reporting_role_id'] != "" :
                if int(request.POST['reporting_role_id']) > 0 :
                    reporting_department_id = getModelColumnById(SpRoles,request.POST['reporting_role_id'],'department_id')
                    role.reporting_department_id = reporting_department_id
                    role.reporting_department_name = getModelColumnById(SpDepartments,reporting_department_id,'department_name')
                else:
                    role.reporting_department_id = None
                    role.reporting_department_name = None

                role.reporting_role_id = request.POST['reporting_role_id']
                
                if int(request.POST['reporting_role_id']) > 0 :
                    role.reporting_role_name = getModelColumnById(SpRoles,request.POST['reporting_role_id'],'role_name')
                else :
                    role.reporting_role_name = "Super User"

            else :
                role.reporting_department_id = None
                role.reporting_department_name = None
                role.reporting_role_id = None
                role.reporting_role_name = None

            # role.is_outsider = request.POST['is_outsider']
            role.status = 1
            role.save()
            if role.id != "" :
                response['role_id'] = role.id
                response['message'] = "Record has been saved successfully."
                response['flag'] = True
                #SAVE ACTIVITY
                user_name   = getUserName(request.user.id)
                heading     = 'New Role Added'
                activity    = str(request.POST['role_name'])+' Role Added by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                saveActivity('Role Add', 'New Role Added', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')
            else:
                response['message'] = "Failed to saved"
                response['flag'] = False

        return JsonResponse(response)

    else:

        context = {}
        permissions = SpPermissions.objects.filter(status=1)

        if request.user.role_id == 0:
            organizations = SpOrganizations.objects.filter(status=1)
            departments = SpDepartments.objects.filter(status=1)
            roles = SpRoles.objects.filter(status=1)
        else:
            organizations = SpOrganizations.objects.filter(id=request.user.organization_id)
            departments = SpDepartments.objects.filter(status=1,organization_id=request.user.organization_id)
            roles = SpRoles.objects.filter(status=1,department_id=request.user.department_id)

        modules = SpModules.objects.filter(status=1)
        for module in modules : 
            module.sub_modules = SpSubModules.objects.filter(status=1,module_id=module.id)
        
        context['permissions'] = permissions
        context['organizations'] = organizations
        context['departments'] = departments
        context['roles'] = roles
        context['modules'] = modules
        

        template = 'role-permission/role-management/add-role.html'
        return render(request,template , context)

@login_required
def getAddRolePermission(request,role_id):
    try:
        context = {}
        role = SpRoles.objects.get(id=role_id)

        other_departments = SpDepartments.objects.filter(status=1,organization_id=role.organization_id)
        for department in other_departments : 
            department.other_roles = SpRoles.objects.filter(status=1,department_id=department.id).exclude(id=role.id)
        
        permissions = SpPermissions.objects.filter(status=1)
        modules = SpModules.objects.filter(status=1)
        for module in modules : 
            module.sub_modules = SpSubModules.objects.filter(status=1,module_id=module.id)
        
        context['permissions'] = permissions
        context['modules'] = modules
        context['role'] = role
        context['other_departments'] = other_departments
        context['first_workflow_level'] =  SpWorkflowLevels.objects.get(priority='first')
        context['last_workflow_level'] =  SpWorkflowLevels.objects.get(priority='last')
        context['middle_workflow_level'] =  SpWorkflowLevels.objects.get(priority='middle')
        template = 'role-permission/role-management/add-role-permission.html'
        return render(request,template ,context)
    except SpRoles.DoesNotExist:
        return HttpResponse('role not found')

@login_required
def addRolePermission(request):
    if request.method == "POST":
        role = SpRoles.objects.get(id=request.POST['role_id'])
        permissions = SpPermissions.objects.filter(status=1)
        sub_modules = SpSubModules.objects.filter(status=1)
        for sub_module in sub_modules :
            for permission in permissions :
                var_name = 'permission_'+ str(sub_module.id) + '_' + str(permission.id)
                if var_name in request.POST:
                    role_permission = SpRolePermissions()
                    role_permission.role_id = role.id
                    role_permission.module_id = getModelColumnById(SpSubModules,sub_module.id,'module_id')
                    role_permission.sub_module_id = sub_module.id
                    role_permission.permission_id = permission.id
                    role_permission.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                    role_permission.save()
                    total_work_flows_var = 'workflow_'+str(sub_module.id)+'_'+str(permission.id)
                    if request.POST[total_work_flows_var] :

                        role_permission.workflow = request.POST[total_work_flows_var]
                        role_permission.save()

                        total_work_flows = json.loads(request.POST[total_work_flows_var])
                        
                        SpRoleWorkflowPermissions.objects.filter(role_id=role.id,sub_module_id=sub_module.id,permission_id=permission.id).delete()
                        
                        for total_work_flow in total_work_flows :
                            role_permission_level = SpRoleWorkflowPermissions()
                            role_permission_level.role_id = role.id
                            role_permission_level.sub_module_id = sub_module.id
                            role_permission_level.permission_id = permission.id
                            role_permission_level.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                            role_permission_level.level_id = total_work_flow['level_id']
                            role_permission_level.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                            role_permission_level.description = total_work_flow['description']
                            if int(total_work_flow['role_id']) > 0 :
                                role_permission_level.workflow_level_dept_id = getModelColumnById(SpRoles,total_work_flow['role_id'],'department_id')
                            else:
                                role_permission_level.workflow_level_dept_id = None

                            role_permission_level.workflow_level_role_id = total_work_flow['role_id']
                            role_permission_level.status = 1
                            role_permission_level.save()

        response = {}
        response['flag'] = True
        response['message'] = "Record has been updated successfully."
        return JsonResponse(response)
    else:
        return HttpResponse('Method not allowed')
    


def orgDepartmentOption(request,organization_id):
    response = {}
    options = '<option value="" selected>Select</option>'
    departments = SpDepartments.objects.filter(status=1,organization_id=organization_id)
    for department in departments : 
        options += "<option value="+str(department.id)+">"+department.department_name+"</option>"

    response['options'] = options
    return JsonResponse(response)

def orgRoleOption(request,organization_id):
    response = {}
    options = '<option value="">Select</option>'
    options += '<option value="0">Super Admin</option>'
    departments = SpDepartments.objects.filter(status=1,organization_id=organization_id)
    for department in departments : 
        roles = SpRoles.objects.filter(status=1,department_id=department.id)
        if roles:
            options += '<optgroup label="' + department.department_name + '">'
            for role in roles : 
                options += "<option value="+str(role.id)+">"+role.role_name+"</option>"
            options += '</optgroup>'
    

    response['options'] = options
    return JsonResponse(response)

def departmentRoleOption(request,department_id):
    response = {}
    options = '<option value="" selected>Select</option>'
    roles = SpRoles.objects.filter(status=1,department_id=department_id)
    for role in roles : 
        options += "<option value="+str(role.id)+">"+role.role_name+"</option>"

    response['options'] = options
    return JsonResponse(response)



@login_required
# @has_par(sub_module_id=2,permission=3)
def editRole(request,role_id):
    if request.method == "POST":
        response = {}
        if SpRoles.objects.filter(role_name=request.POST['role_name'],department_id=request.POST['department_id']).exclude(id=role_id).exists() :
            response['flag'] = False
            response['message'] = "Role name already exist"
        else:
            role = SpRoles.objects.get(id=role_id)
            role.organization_id = request.POST['organization_id']
            role.organization_name = getModelColumnById(SpOrganizations,request.POST['organization_id'],'organization_name')
            role.department_id = request.POST['department_id']
            role.department_name = getModelColumnById(SpDepartments,request.POST['department_id'],'department_name')
            role.role_name = request.POST['role_name']
            role.responsibilities = request.POST['responsibilities']

            if request.POST['reporting_role_id'] != "" :
                if int(request.POST['reporting_role_id']) > 0 :
                    reporting_department_id = getModelColumnById(SpRoles,request.POST['reporting_role_id'],'department_id')
                    role.reporting_department_id = reporting_department_id
                    role.reporting_department_name = getModelColumnById(SpDepartments,reporting_department_id,'department_name')
                else:
                    role.reporting_department_id = None
                    role.reporting_department_name = None

                role.reporting_role_id = request.POST['reporting_role_id']
                
                if int(request.POST['reporting_role_id']) > 0 :
                    role.reporting_role_name = getModelColumnById(SpRoles,request.POST['reporting_role_id'],'role_name')
                else :
                    role.reporting_role_name = "Super User"

            else :
                role.reporting_department_id = None
                role.reporting_department_name = None
                role.reporting_role_id = None
                role.reporting_role_name = None

            # role.is_outsider = request.POST['is_outsider']    
            role.save()
            

            permissions = SpPermissions.objects.filter(status=1)
            sub_modules = SpSubModules.objects.filter(status=1)
             
            SpRolePermissions.objects.filter(role_id=role.id).delete()
            SpRoleWorkflowPermissions.objects.filter(role_id=role.id).delete()

            for sub_module in sub_modules :
                for permission in permissions :                    
                    other_roles = SpRolePermissions.objects.filter(sub_module_id=sub_module.id,permission_id=permission.id).values('role_id').distinct().exclude(role_id=role.id)
                    if len(other_roles) :
                        for other_role in other_roles :
                            SpRolePermissions.objects.filter(role_id=other_role['role_id']).delete()
                            SpRoleWorkflowPermissions.objects.filter(role_id=other_role['role_id']).delete()

                            var_name = 'permission_'+ str(sub_module.id) + '_' + str(permission.id)
                            if var_name in request.POST:
                                role_permission = SpRolePermissions()
                                role_permission.role_id = other_role['role_id']
                                role_permission.module_id = getModelColumnById(SpSubModules,sub_module.id,'module_id')
                                role_permission.sub_module_id = sub_module.id
                                role_permission.permission_id = permission.id
                                role_permission.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                                role_permission.save()
                                total_work_flows_var = 'workflow_'+str(sub_module.id)+'_'+str(permission.id)
                                if request.POST[total_work_flows_var] :

                                    role_permission.workflow = request.POST[total_work_flows_var]
                                    role_permission.save()

                                    total_work_flows = json.loads(request.POST[total_work_flows_var])
                                    
                                    SpRoleWorkflowPermissions.objects.filter(role_id=other_role['role_id'],sub_module_id=sub_module.id,permission_id=permission.id).delete()
                                    
                                    for total_work_flow in total_work_flows :
                                        role_permission_level = SpRoleWorkflowPermissions()
                                        role_permission_level.role_id = other_role['role_id']
                                        role_permission_level.sub_module_id = sub_module.id
                                        role_permission_level.permission_id = permission.id
                                        role_permission_level.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                                        role_permission_level.level_id = total_work_flow['level_id']
                                        role_permission_level.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                                        role_permission_level.description = total_work_flow['description']
                                        if int(total_work_flow['role_id']) > 0 :
                                            role_permission_level.workflow_level_dept_id = getModelColumnById(SpRoles,total_work_flow['role_id'],'department_id')
                                        else:
                                            role_permission_level.workflow_level_dept_id = None
                                        role_permission_level.workflow_level_role_id = total_work_flow['role_id']
                                        if 'status' in total_work_flow :
                                            role_permission_level.status = total_work_flow['status']
                                        else:
                                            role_permission_level.status = 1
                                        role_permission_level.save()

                    var_name = 'permission_'+ str(sub_module.id) + '_' + str(permission.id)
                    if var_name in request.POST:
                        role_permission = SpRolePermissions()
                        role_permission.role_id = role.id
                        role_permission.module_id = getModelColumnById(SpSubModules,sub_module.id,'module_id')
                        role_permission.sub_module_id = sub_module.id
                        role_permission.permission_id = permission.id
                        role_permission.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                        role_permission.save()
                        total_work_flows_var = 'workflow_'+str(sub_module.id)+'_'+str(permission.id)
                        if request.POST[total_work_flows_var] :

                            role_permission.workflow = request.POST[total_work_flows_var]
                            role_permission.save()

                            total_work_flows = json.loads(request.POST[total_work_flows_var])
                            
                            SpRoleWorkflowPermissions.objects.filter(role_id=role.id,sub_module_id=sub_module.id,permission_id=permission.id).delete()
                            
                            for total_work_flow in total_work_flows :
                                role_permission_level = SpRoleWorkflowPermissions()
                                role_permission_level.role_id = role.id
                                role_permission_level.sub_module_id = sub_module.id
                                role_permission_level.permission_id = permission.id
                                role_permission_level.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                                role_permission_level.level_id = total_work_flow['level_id']
                                role_permission_level.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                                role_permission_level.description = total_work_flow['description']
                                if int(total_work_flow['role_id']) > 0 :
                                    role_permission_level.workflow_level_dept_id = getModelColumnById(SpRoles,total_work_flow['role_id'],'department_id')
                                else:
                                    role_permission_level.workflow_level_dept_id = None
                                role_permission_level.workflow_level_role_id = total_work_flow['role_id']
                                if 'status' in total_work_flow :
                                    role_permission_level.status = total_work_flow['status']
                                else:
                                    role_permission_level.status = 1
                                role_permission_level.save()
                                
                                
            # update users role & permission
            updateUsersRole(role.id)
            response['flag']    = True
            response['message'] = "Record has been updated successfully."
            #SAVE ACTIVITY
            user_name   = getUserName(request.user.id)
            heading     = 'Role Updated'
            activity    = 'Role Updated '+str(request.POST['role_name'])+' by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            saveActivity('Edit Roles Details', 'Role Updated To'+str(request.POST['role_name']), heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')

        return JsonResponse(response)
    else:
        context = {}
        role = SpRoles.objects.get(id=role_id)
        other_departments = SpDepartments.objects.filter(status=1,organization_id=role.organization_id)
        for department in other_departments : 
            # department.other_roles = SpRoles.objects.filter(status=1,department_id=department.id).exclude(id=role.id)
            department.other_roles = SpRoles.objects.filter(status=1,department_id=department.id)

        permissions = SpPermissions.objects.filter(status=1)
        organizations = SpOrganizations.objects.filter(status=1)
        departments = SpDepartments.objects.filter(status=1,organization_id=role.organization_id)
        
        reporting_departments = SpDepartments.objects.filter(status=1,organization_id=role.organization_id)
        for reporting_department in reporting_departments:
            reporting_department.roles = SpRoles.objects.filter(status=1,department_id=reporting_department.id).exclude(id=role_id)
            
        modules = SpModules.objects.filter(status=1)
        for module in modules : 
            module.sub_modules = SpSubModules.objects.filter(status=1,module_id=module.id)
        

        context['role'] = role
        context['other_departments'] = other_departments
        context['permissions'] = permissions
        context['organizations'] = organizations
        context['departments'] = departments
        context['reporting_departments'] = reporting_departments
        context['modules'] = modules
        context['first_workflow_level'] =  SpWorkflowLevels.objects.get(priority='first')
        context['last_workflow_level'] =  SpWorkflowLevels.objects.get(priority='last')
        context['middle_workflow_level'] =  SpWorkflowLevels.objects.get(priority='middle')
        template = 'role-permission/role-management/edit-role.html'
    return render(request,template , context)



@login_required
def updateRoleStatus(request):

    response = {}
    if request.method == "POST":
        try:
            id = request.POST.get('id')
            is_active = request.POST.get('is_active')

            data = SpRoles.objects.get(id=id)
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


def updateUsersRole(role_id):
    users = SpUsers.objects.filter(role_id=role_id).values('id')
    if len(users):
        for user in users :
            role_permissions = SpRolePermissions.objects.filter(role_id=role_id)
            if len(role_permissions):
                SpUserRolePermissions.objects.filter(user_id=user['id'],role_id=role_id).delete()
                for role_permission in role_permissions:
                    user_role_permission = SpUserRolePermissions()
                    user_role_permission.user_id = user['id']
                    user_role_permission.role_id = role_id
                    user_role_permission.module_id = role_permission.module_id
                    user_role_permission.sub_module_id = role_permission.sub_module_id
                    user_role_permission.permission_id = role_permission.permission_id
                    user_role_permission.permission_slug = getModelColumnById(SpPermissions,role_permission.permission_id,'slug')
                    user_role_permission.workflow = role_permission.workflow
                    user_role_permission.save()

                
                role_permission_workflows = SpRoleWorkflowPermissions.objects.filter(role_id=role_id)
                if len(role_permission_workflows):
                    SpUserRoleWorkflowPermissions.objects.filter(user_id=user['id'],role_id=role_id).delete()
                    for role_permission_workflow in role_permission_workflows : 
                        user_role_permission_wf = SpUserRoleWorkflowPermissions()
                        user_role_permission_wf.user_id = user['id']
                        user_role_permission_wf.role_id = role_permission_workflow.role_id
                        user_role_permission_wf.sub_module_id = role_permission_workflow.sub_module_id
                        user_role_permission_wf.permission_id = role_permission_workflow.permission_id
                        user_role_permission_wf.permission_slug = getModelColumnById(SpPermissions,role_permission_workflow.permission_id,'slug')
                        user_role_permission_wf.level_id = role_permission_workflow.level_id
                        user_role_permission_wf.level = role_permission_workflow.level
                        user_role_permission_wf.description = role_permission_workflow.description
                        user_role_permission_wf.workflow_level_dept_id = role_permission_workflow.workflow_level_dept_id
                        user_role_permission_wf.workflow_level_role_id = role_permission_workflow.workflow_level_role_id
                        user_role_permission_wf.status = role_permission_workflow.status
                        user_role_permission_wf.save()





@login_required
def addShortRole(request,parent_role_id):

    if request.method == "POST":
        response = {}
        if SpRoles.objects.filter(department_id=request.POST['department_id'], role_name=request.POST['role_name']).exists():
            response['message'] = "Role already exist"
            response['flag'] = False
        else:
            role = SpRoles()
            role.organization_id = request.POST['organization_id']
            role.organization_name = getModelColumnById(SpOrganizations,request.POST['organization_id'],'organization_name')
            role.department_id = request.POST['department_id']
            role.department_name = getModelColumnById(SpDepartments,request.POST['department_id'],'department_name')
            role.role_name = request.POST['role_name']

            if int(request.POST['reporting_role_id']) > 0 :
                role.reporting_role_id = request.POST['reporting_role_id']
                role.reporting_role_name = getModelColumnById(SpRoles,request.POST['reporting_role_id'],'role_name')
                reporting_department_id = getModelColumnById(SpRoles,request.POST['reporting_role_id'],'department_id')
                role.reporting_department_id = reporting_department_id
                role.reporting_department_name = getModelColumnById(SpDepartments,reporting_department_id,'department_name')
            else :
                role.reporting_department_id = None
                role.reporting_department_name = None
                role.reporting_role_id = 0
                role.reporting_role_name = "Super User"

            role.status = 1
            role.save()
            if role.id != "" :
                response['role_id'] = role.id
                response['message'] = "Record has been saved successfully."
                response['flag'] = True
            else:
                response['message'] = "Failed to saved"
                response['flag'] = False

        return JsonResponse(response)

    else:

        context = {}
        permissions = SpPermissions.objects.filter(status=1)
        organizations = SpOrganizations.objects.filter(status=1)
        departments = SpDepartments.objects.filter(status=1)
        if parent_role_id == '0' :
            parent_role = None
        else:
            parent_role = SpRoles.objects.get(id=parent_role_id)

        context['organizations'] = organizations
        context['departments'] = departments
        context['parent_role'] = parent_role
        context['reporting_role_id'] = parent_role_id
        template = 'role-permission/role-management/add-short-role.html'
        return render(request,template , context)


@login_required
def shortRoleDetails(request,role_id):
    context = {}
    role_details = SpRoles.objects.get(id=role_id)
    context['role_details'] = role_details
    if SpRoleActivities.objects.filter(role_id=role_id).exists():
        context['role_activities'] = SpRoleActivities.objects.filter(role_id=role_id)
    else:
        context['role_activities'] = None

    context['role_user_counts'] = SpUsers.objects.filter(role_id=role_id).count()
    template = 'role-permission/role-short-details.html'

    return render(request, template, context)




@login_required
def saveRoleActivity(request):
    if request.method == "POST":
        response = {}
        role_id = request.POST['role_id']
        if 'role_activity_id' in request.POST and request.POST['role_activity_id'] != "" :
            role_activity = SpRoleActivities.objects.get(id=request.POST['role_activity_id'])
        else:
            role_activity = SpRoleActivities()
            role_activity.role_id = role_id

        role_activity.activity = request.POST['role_activity']
        role_activity.status = 1
        role_activity.save()
        if role_activity.id != "" :
            context = {}
            role_activity_list = SpRoleActivities.objects.filter(role_id=role_id)
            context['activity_list'] = role_activity_list
            template = 'role-permission/role-activity-list.html'
            return render(request, template, context)

        else:
            response['message'] = "Failed to saved"
            response['flag'] = False
        return JsonResponse(response)

    else:
        context = {}
        context['flag'] = False
        context['message'] = "Method Not allowed"
        return JsonResponse(context)


@login_required
def deleteRoleActivity(request,role_activity_id):
    if request.method == "POST":
        context = {}
        context['flag'] = False
        context['message'] = "Method Not allowed"
        return JsonResponse(context)
    else:
        if SpRoleActivities.objects.filter(id=role_activity_id).exists():

            SpRoleActivities.objects.filter(id=role_activity_id).delete()
            context = {}
            context['flag'] = True
            context['message'] = "Record has been deleted successfully."
            return JsonResponse(context)
        else:
            context = {}
            context['flag'] = False
            context['message'] = "Method Not allowed"
            return JsonResponse(context)


@login_required
def roleEntityMapping(request,role_id,entity_type):
    context = {}
    if request.method == "POST":
        context['flag'] = False
        context['message'] = "Method Not allowed"
        return JsonResponse(context)
    else:
        if SpRoles.objects.filter(id=role_id).exists():
            context['role'] = SpRoles.objects.get(id=role_id)
            if entity_type == "leave_policy":
                if SpRoleEntityMapping.objects.filter(role_id=role_id,entity_type='leave_policy').exists():
                    context['mapping'] = mapping = SpRoleEntityMapping.objects.get(role_id=role_id,entity_type='leave_policy')
                    context['mapping_leave_policy'] = mapping_leave_policy = SpLeavePolicies.objects.get(id=mapping.entity_id)
                    context['leave_policies'] = SpLeavePolicies.objects.filter(status=1).exclude(id=mapping.entity_id)
                else:
                    context['leave_policies'] = SpLeavePolicies.objects.filter(status=1)
                template = 'role-permission/role-management/role-leave-policy-mapping.html'
                return render(request,template,context)

            elif entity_type == "attendance_group":
                if SpRoleEntityMapping.objects.filter(role_id=role_id,entity_type='attendance_group').exists():
                    context['mapping'] = mapping = SpRoleEntityMapping.objects.raw('''SELECT sp_role_entity_mapping.*,sp_attendance_groups.attendance_group FROM sp_role_entity_mapping
                    LEFT JOIN sp_attendance_groups on sp_attendance_groups.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="attendance_group"''', [role_id])
                    
                    map_list = []
                    for role_mapping in mapping:
                        map_list.append(role_mapping.entity_id)
                    context['attendance_groups'] = SpAttendanceGroups.objects.filter(status=1).exclude(id__in=map_list)
                else:
                    context['attendance_groups'] = SpAttendanceGroups.objects.filter(status=1)             
                template = 'role-permission/role-management/role-attendance-group-mapping.html'
                return render(request,template,context)
            
            elif entity_type == "pay_band":
                if SpRoleEntityMapping.objects.filter(role_id=role_id,entity_type='pay_band').exists():
                    context['mapping'] = mapping = SpRoleEntityMapping.objects.get(role_id=role_id,entity_type='pay_band')
                    context['mapping_pay_band'] = mapping_pay_band = SpPayBands.objects.get(id=mapping.entity_id)
                    context['pay_bands'] = SpPayBands.objects.filter(status=1).exclude(id=mapping.entity_id)
                else:
                    context['pay_bands'] = SpPayBands.objects.filter(status=1)
                template = 'role-permission/role-management/role-pay-band-mapping.html'
                return render(request,template,context)

            elif entity_type == "holiday":
                if SpRoleEntityMapping.objects.filter(role_id=role_id,entity_type='holiday').exists():
                    context['mapping'] = mapping = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_holidays.holiday FROM sp_role_entity_mapping
                    LEFT JOIN sp_holidays on sp_holidays.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="holiday" ''', [role_id])
                    map_list = []
                    for role_mapping in mapping:
                        map_list.append(role_mapping.entity_id)
                    
                    context['holidays'] = SpHolidays.objects.filter(status=1).exclude(id__in=map_list)
                else:
                    context['holidays'] = SpHolidays.objects.filter(status=1)
                template = 'role-permission/role-management/role-holiday-mapping.html'
                return render(request,template,context)
            
            elif entity_type == "salary_addition":
                if SpRoleEntityMapping.objects.filter(role_id=role_id,entity_type='salary_addition').exists():
                    context['mapping'] = mapping = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_salary_addition_types.addition FROM sp_role_entity_mapping
                    LEFT JOIN sp_salary_addition_types on sp_salary_addition_types.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="salary_addition" ''', [role_id])
                    map_list = []
                    for role_mapping in mapping:
                        map_list.append(role_mapping.entity_id)
                    
                    context['salary_additions'] = SpSalaryAdditionTypes.objects.filter(status=1).exclude(id__in=map_list)
                else:
                    context['salary_additions'] = SpSalaryAdditionTypes.objects.filter(status=1)
                template = 'role-permission/role-management/role-salary-addition-mapping.html'
                return render(request,template,context)
            
            elif entity_type == "salary_deduction":
                if SpRoleEntityMapping.objects.filter(role_id=role_id,entity_type='salary_deduction').exists():
                    context['mapping'] = mapping = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_salary_deduction_types.deduction FROM sp_role_entity_mapping
                    LEFT JOIN sp_salary_deduction_types on sp_salary_deduction_types.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="salary_deduction" ''', [role_id])
                    map_list = []
                    for role_mapping in mapping:
                        map_list.append(role_mapping.entity_id)
                    
                    context['salary_deductions'] = SpSalaryDeductionTypes.objects.filter(status=1).exclude(id__in=map_list)
                else:
                    context['salary_deductions'] = SpSalaryDeductionTypes.objects.filter(status=1)
                template = 'role-permission/role-management/role-salary-deduction-mapping.html'
                return render(request,template,context)

           

        else:
            context['flag'] = False
            context['message'] = "Method Not allowed"
            return JsonResponse(context)


@csrf_exempt
@login_required
def saveRoleMapping(request):
    if request.method == "POST":
        role_id = request.POST['role_id']
        entity_type = request.POST['entity_type']
        entity_id = request.POST['entity_id']
        
        if SpRoleEntityMapping.objects.filter(entity_type=entity_type,role_id=role_id,entity_id=entity_id).exists():
            context = {}
            context['flag'] = False
            context['message'] = "Mapping already exists."
            return JsonResponse(context)
        else:
            mapping = SpRoleEntityMapping()
            mapping.role_id = role_id
            mapping.entity_type = entity_type
            mapping.entity_id = entity_id
            mapping.save()

            if entity_type == "leave_policy":
                #SAVE ACTIVITY
                user_name   = getUserName(request.user.id)
                heading     = 'Role Leave Policy Mapping'
                activity    = 'Role Leave Policy Mapping Updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                saveActivity('Manage Roles & Permission', 'Role Leave Policy Mapping', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')
                
                context = {}
                if SpRoleEntityMapping.objects.filter(role_id=role_id,entity_type='leave_policy').exists():
                    context['mapping'] = mapping = SpRoleEntityMapping.objects.get(role_id=role_id,entity_type='leave_policy')
                    context['mapping_leave_policy'] = mapping_leave_policy = SpLeavePolicies.objects.get(id=mapping.entity_id)
                    context['leave_policies'] = SpLeavePolicies.objects.filter(status=1).exclude(id=mapping.entity_id)
                else:
                    context['leave_policies'] = SpLeavePolicies.objects.filter(status=1)
                template = 'role-permission/role-management/ajax-leave-policy-mapping.html'
                return render(request,template,context)

            elif entity_type == "holiday":
                #SAVE ACTIVITY
                user_name   = getUserName(request.user.id)
                heading     = 'Role Holiday Mapping'
                activity    = 'Role Holiday Mapping Updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                saveActivity('Manage Roles & Permission', 'Holiday Mapping', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')
                
                context = {}
                if SpRoleEntityMapping.objects.filter(role_id=role_id,entity_type='holiday').exists():
                    context['mapping'] = mapping = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_holidays.holiday FROM sp_role_entity_mapping
                    LEFT JOIN sp_holidays on sp_holidays.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="holiday" ''', [role_id])
                    map_list = []
                    for role_mapping in mapping:
                        map_list.append(role_mapping.entity_id)
                    
                    context['holidays'] = SpHolidays.objects.filter(status=1).exclude(id__in=map_list)
                else:
                    context['holidays'] = SpHolidays.objects.filter(status=1)

                template = 'role-permission/role-management/ajax-holiday-mapping.html'
                return render(request,template,context)

            elif entity_type == "attendance_group":
                #SAVE ACTIVITY
                user_name   = getUserName(request.user.id)
                heading     = 'Role Attendance Group Mapping'
                activity    = 'Role Attendance Group Mapping Updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                saveActivity('Manage Roles & Permission', 'Role Attendance Group Mapping', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')  
                
                context = {}
                if SpRoleEntityMapping.objects.filter(role_id=role_id,entity_type='attendance_group').exists():
                    context['mapping'] = mapping = SpRoleEntityMapping.objects.raw('''SELECT sp_role_entity_mapping.*,sp_attendance_groups.attendance_group FROM sp_role_entity_mapping
                    LEFT JOIN sp_attendance_groups on sp_attendance_groups.id = sp_role_entity_mapping.entity_id 
                    WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="attendance_group"''', [role_id])
                    
                    map_list = []
                    for role_mapping in mapping:
                        map_list.append(role_mapping.entity_id)
                    context['attendance_groups'] = SpAttendanceGroups.objects.filter(status=1).exclude(id__in=map_list)
                else:
                    context['attendance_groups'] = SpAttendanceGroups.objects.filter(status=1)

                template = 'role-permission/role-management/ajax-attendance-group-mapping.html'
                return render(request,template,context)

    else:
        context = {}
        context['flag'] = False
        context['message'] = "Method Not allowed"
        return JsonResponse(context)


@csrf_exempt
@login_required
def saveRoleUnmapping(request):
    if request.method == "POST":
        role_id = request.POST['role_id']
        entity_type = request.POST['entity_type']
        entity_id = request.POST['entity_id']
        
        SpRoleEntityMapping.objects.filter(entity_type=entity_type,entity_id=entity_id,role_id=role_id).delete()

        if entity_type == "leave_policy":
            #SAVE ACTIVITY
            user_name   = getUserName(request.user.id)
            heading     = 'Role Leave Policy Mapping'
            activity    = 'Role Leave Policy Mapping Updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            saveActivity('Manage Roles & Permission', 'Role Leave Policy Mapping', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')
            
            context = {}
            if SpRoleEntityMapping.objects.filter(role_id=role_id,entity_type='leave_policy').exists():
                context['mapping'] = mapping = SpRoleEntityMapping.objects.get(role_id=role_id,entity_type='leave_policy')
                context['mapping_leave_policy'] = mapping_leave_policy = SpLeavePolicies.objects.get(id=mapping.entity_id)
                context['leave_policies'] = SpLeavePolicies.objects.filter(status=1).exclude(id=mapping.entity_id)
            else:
                context['leave_policies'] = SpLeavePolicies.objects.filter(status=1)
                template = 'role-permission/role-management/ajax-leave-policy-mapping.html'
                return render(request,template,context)

        elif entity_type == "holiday":
            #SAVE ACTIVITY
            user_name   = getUserName(request.user.id)
            heading     = 'Role Holiday Mapping'
            activity    = 'Role Holiday Mapping Updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            saveActivity('Manage Roles & Permission', 'Holiday Mapping', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')
            
            context = {}
            if SpRoleEntityMapping.objects.filter(role_id=role_id,entity_type='holiday').exists():
                context['mapping'] = mapping = SpRoleEntityMapping.objects.raw(''' SELECT sp_role_entity_mapping.*,sp_holidays.holiday FROM sp_role_entity_mapping
                LEFT JOIN sp_holidays on sp_holidays.id = sp_role_entity_mapping.entity_id 
                WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="holiday" ''', [role_id])
                map_list = []
                for role_mapping in mapping:
                    map_list.append(role_mapping.entity_id)
                
                context['holidays'] = SpHolidays.objects.filter(status=1).exclude(id__in=map_list)
            else:
                context['holidays'] = SpHolidays.objects.filter(status=1)

            template = 'role-permission/role-management/ajax-holiday-mapping.html'
            return render(request,template,context)

        elif entity_type == "attendance_group":
            #SAVE ACTIVITY
            user_name   = getUserName(request.user.id)
            heading     = 'Role Attendance Group Mapping'
            activity    = 'Role Attendance Group Mapping Updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            saveActivity('Manage Roles & Permission', 'Role Attendance Group Mapping', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')  
            
            context = {}
            if SpRoleEntityMapping.objects.filter(role_id=role_id,entity_type='attendance_group').exists():
                context['mapping'] = mapping = SpRoleEntityMapping.objects.raw('''SELECT sp_role_entity_mapping.*,sp_attendance_groups.attendance_group FROM sp_role_entity_mapping
                LEFT JOIN sp_attendance_groups on sp_attendance_groups.id = sp_role_entity_mapping.entity_id 
                WHERE sp_role_entity_mapping.role_id = %s and sp_role_entity_mapping.entity_type="attendance_group"''', [role_id])
                
                map_list = []
                for role_mapping in mapping:
                    map_list.append(role_mapping.entity_id)
                context['attendance_groups'] = SpAttendanceGroups.objects.filter(status=1).exclude(id__in=map_list)
            else:
                context['attendance_groups'] = SpAttendanceGroups.objects.filter(status=1)

            template = 'role-permission/role-management/ajax-attendance-group-mapping.html'
            return render(request,template,context)

    else:
        context = {}
        context['flag'] = False
        context['message'] = "Method Not allowed"
        return JsonResponse(context)


@login_required
def saveRoleLeavePolicyMapping(request):
    context = {}
    if request.method == "POST":
        role_id = request.POST['role_id']
        leave_policy_id = request.POST['leave_policy_id']
        if SpRoleEntityMapping.objects.filter(entity_type='leave_policy',role_id=role_id,entity_id=leave_policy_id).exists():
            context['flag'] = False
            context['message'] = "Mapping already exists."
        else:
            # delete old record
            SpRoleEntityMapping.objects.filter(entity_type='leave_policy',role_id=role_id).delete()
            
            mapping = SpRoleEntityMapping()
            mapping.role_id = role_id
            mapping.entity_type = 'leave_policy'
            mapping.entity_id = leave_policy_id
            mapping.save()

            #SAVE ACTIVITY
            user_name   = getUserName(request.user.id)
            heading     = 'Role Leave Policy Mapping'
            activity    = 'Role Leave Policy Mapping Updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            saveActivity('Manage Roles & Permission', 'Role Leave Policy Mapping', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')


            if mapping.id:
                context['flag'] = True
                context['message'] = "Record has been saved successfully."
            else:
                context['flag'] = False
                context['message'] = "Failed to save mapping."
        return JsonResponse(context)
    else:
        context['flag'] = False
        context['message'] = "Method Not allowed"
        return JsonResponse(context)


@login_required
def saveRoleAttendanceGroupMapping(request):
    context = {}
    if request.method == "POST":
        role_id = request.POST['role_id']
        attendance_group_ids = request.POST.getlist('attendance_group_id[]')
        SpRoleEntityMapping.objects.filter(entity_type='attendance_group',role_id=role_id).delete()
        if len(attendance_group_ids)>0:
            for attendance_group_id in attendance_group_ids:            
                if SpRoleEntityMapping.objects.filter(entity_type='attendance_group',role_id=role_id,entity_id=attendance_group_id).exists():
                    SpRoleEntityMapping.objects.filter(entity_type='attendance_group',role_id=role_id).delete()
                    entity_id = getModelColumnById(SpAttendanceGroups,attendance_group_id,'id')
                
                mapping = SpRoleEntityMapping()
                mapping.role_id = role_id
                mapping.entity_type = 'attendance_group'
                mapping.entity_id = attendance_group_id
                mapping.save()

                #SAVE ACTIVITY
                user_name   = getUserName(request.user.id)
                heading     = 'Role Attendance Group Mapping'
                activity    = 'Role Attendance Group Mapping Updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                saveActivity('Manage Roles & Permission', 'Role Attendance Group Mapping', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')    

                if mapping.id:
                    context['flag'] = True
                    context['message'] = "Record has been saved successfully."
                else:
                    context['flag'] = False
                    context['message'] = "Failed to save mapping."
            return JsonResponse(context)
        else:
            context['flag'] = False
            context['message'] = "Atleast Select One Holiday"
            return JsonResponse(context)
    else:
        context['flag'] = False
        context['message'] = "Method Not allowed"
        return JsonResponse(context)
    
@login_required
def saveRolePayBandMapping(request):
    context = {}
    if request.method == "POST":
        role_id = request.POST['role_id']
        pay_band_id = request.POST['pay_band_id']
        if SpRoleEntityMapping.objects.filter(entity_type='pay_band',role_id=role_id,entity_id=pay_band_id).exists():
            context['flag'] = False
            context['message'] = "Mapping already exists."
        else:
            # delete old record
            SpRoleEntityMapping.objects.filter(entity_type='pay_band',role_id=role_id).delete()
            
            mapping = SpRoleEntityMapping()
            mapping.role_id = role_id
            mapping.entity_type = 'pay_band'
            mapping.entity_id = pay_band_id
            mapping.save()

            #SAVE ACTIVITY
            user_name   = getUserName(request.user.id)
            heading     = 'Role Pay Band Mapping'
            activity    = 'Role Pay Band Mapping Updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            saveActivity('Manage Roles & Permission', 'Role Pay Band Mapping', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')


            if mapping.id:
                context['flag'] = True
                context['message'] = "Record has been saved successfully."
            else:
                context['flag'] = False
                context['message'] = "Failed to save mapping."
        return JsonResponse(context)
    else:
        context['flag'] = False
        context['message'] = "Method Not allowed"
        return JsonResponse(context)

@login_required
def saveRoleHolidayMapping(request):
    context = {}
    if request.method == "POST":
        role_id = request.POST['role_id']
        SpRoleEntityMapping.objects.filter(entity_type='holiday',role_id=role_id).delete()
        holiday_id          = request.POST.getlist('holiday_id[]')
        if len(holiday_id) >0:
            for id, val in enumerate(holiday_id):
                mapping = SpRoleEntityMapping()
                mapping.role_id = role_id
                mapping.entity_type = 'holiday'
                mapping.entity_id = holiday_id[id]
                mapping.save()

            #SAVE ACTIVITY
            user_name   = getUserName(request.user.id)
            heading     = 'Role Holiday Mapping'
            activity    = 'Role Holiday Mapping Updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            saveActivity('Manage Roles & Permission', 'Holiday Mapping', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')

            context['flag'] = True
            context['message'] = "Record has been saved successfully."
                
            return JsonResponse(context)
        else:
            context['flag'] = False
            context['message'] = "Atleast Select One Holiday"
            return JsonResponse(context)
    else:
        context['flag'] = False
        context['message'] = "Method Not allowed"
        return JsonResponse(context)


@login_required
def saveRoleSalaryAdditionMapping(request):
    context = {}
    if request.method == "POST":
        role_id = request.POST['role_id']
        SpRoleEntityMapping.objects.filter(entity_type='salary_addition',role_id=role_id).delete()
        salary_addition_id          = request.POST.getlist('salary_addition_id[]')
        for id, val in enumerate(salary_addition_id):
            mapping = SpRoleEntityMapping()
            mapping.role_id = role_id
            mapping.entity_type = 'salary_addition'
            mapping.entity_id = salary_addition_id[id]
            mapping.save()

            

        context['flag'] = True
        context['message'] = "Record has been saved successfully."
        
        #SAVE ACTIVITY
        user_name   = getUserName(request.user.id)
        heading     = 'Role Salary Addition Mapping'
        activity    = 'Role Salary Addition Mapping Updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
        saveActivity('Manage Roles & Permission', 'Role Salary Addition Mapping', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')
    
        return JsonResponse(context)
    else:
        context['flag'] = False
        context['message'] = "Method Not allowed"
        return JsonResponse(context)

@login_required
def saveRoleSalaryDeductionMapping(request):
    context = {}
    if request.method == "POST":
        role_id = request.POST['role_id']
        SpRoleEntityMapping.objects.filter(entity_type='salary_deduction',role_id=role_id).delete()
        salary_deduction_id          = request.POST.getlist('salary_deduction_id[]')
        for id, val in enumerate(salary_deduction_id):
            mapping = SpRoleEntityMapping()
            mapping.role_id = role_id
            mapping.entity_type = 'salary_deduction'
            mapping.entity_id = salary_deduction_id[id]
            mapping.save()

            #SAVE ACTIVITY
            user_name   = getUserName(request.user.id)
            heading     = 'Role Salary Deduction Mapping'
            activity    = 'Role Salary Deduction Mapping Updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            saveActivity('Manage Roles & Permission', 'Role Salary Deduction Mapping', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')

        context['flag'] = True
        context['message'] = "Record has been saved successfully."
            
        return JsonResponse(context)
    else:
        context['flag'] = False
        context['message'] = "Method Not allowed"
        return JsonResponse(context)


@login_required
def viewMapRoleAttributesModal(request,role_id):
    try:
        context = {}
        role = SpRoles.objects.get(id=role_id)
        attributes = SpAttributes.objects.all().exclude(id=1)
        role_attributes = SpRoleAttributes.objects.raw('''SELECT sp_role_attributes.attribute_id, sp_attributes.* FROM sp_role_attributes LEFT JOIN sp_attributes on sp_attributes.id = sp_role_attributes.attribute_id WHERE sp_role_attributes.role_id = %s ''', [role_id])
        role_attribute_ids = []
        for role_attribute in role_attributes:
            role_attribute_ids.append(role_attribute.id)
            role_attribute.fields = list(SpRoleAttrOptionalFields.objects.filter(role_id=role_id, attribute_id=role_attribute.attribute_id).values_list('field_name',flat=True))
            role_attribute.hidden_fields = list(SpRoleAttrHiddenFields.objects.filter(role_id=role_id, attribute_id=role_attribute.attribute_id).values_list('field_name',flat=True))



        context['attributes'] = attributes
        context['role_attributes'] = role_attributes
        context['role_attribute_ids'] = role_attribute_ids
        context['required_documents'] = SpRequiredDocuments.objects.all()
        context['role_id'] = role_id
        template = 'role-permission/role-management/attribute-controls/role_type_attributes.html'
        return render(request,template ,context)
    except SpRoles.DoesNotExist:
        return HttpResponse('role not found')


@login_required
def getAttributeControls(request, id):
    try:
        context = {}
        attributes = SpAttributes.objects.filter(id=id).first()
        attributes.fields = list()
        attributes.hidden_fields = list()
        
        context['attribute'] = attributes
        if int(id) == 8:
            context['required_documents'] = SpRequiredDocuments.objects.all()
        template = 'role-permission/role-management/attribute-controls/'+str(id)+'.html'
        return render(request,template ,context)
    except SpRoles.DoesNotExist:
        return HttpResponse('role not found')

@login_required
def updateRoleAttributes(request):
    
    if request.method == "POST":
        context = {}
        # attributes = SpAttributes.objects.filter(id=2)
        attributes = SpAttributes.objects.exclude(id=1)
        role_id = request.POST['role_type_id']
        SpRoleAttrOptionalFields.objects.filter(role_id=role_id).delete()
        SpRoleAttrHiddenFields.objects.filter(role_id=role_id).delete()
        SpRoleAttributes.objects.filter(role_id=role_id).delete()
        if request.method == "POST":
            for attribute in attributes : 
                var = 'optional_'+str(attribute.id)
                if var in  request.POST :
                    i = 0
                    attributeList = request.POST[var].split (",")
                    for optionalFieldName in attributeList : 
                        optionalData = SpRoleAttrOptionalFields()
                        optionalData.role_id = role_id
                        optionalData.attribute_id = attribute.id
                        optionalData.field_name = optionalFieldName
                        optionalData.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        optionalData.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        optionalData.save()

                hidden_var = 'hidden_'+str(attribute.id)
                if hidden_var in  request.POST :
                    i = 0
                    attributeList = request.POST[hidden_var].split (",")
                    for hiddenFieldName in attributeList : 
                        hiddenFieldData = SpRoleAttrHiddenFields()
                        hiddenFieldData.role_id = role_id
                        hiddenFieldData.attribute_id = attribute.id
                        hiddenFieldData.field_name = hiddenFieldName
                        hiddenFieldData.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        hiddenFieldData.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        hiddenFieldData.save()

            # attributeArr = request.POST['attribute_id[]']
            attributeArr       = request.POST.getlist('attribute_id[]') 
            for attributeData in attributeArr : 
                insert = SpRoleAttributes()
                insert.role_id = role_id
                insert.attribute_id = attributeData
                insert.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                insert.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                insert.save()
                
        context['flag'] = True
        context['message'] = "Attributes configuration has been saved successfully."
            
        return JsonResponse(context)
    else:
        context['flag'] = False
        context['message'] = "Method Not allowed"
        return JsonResponse(context)

