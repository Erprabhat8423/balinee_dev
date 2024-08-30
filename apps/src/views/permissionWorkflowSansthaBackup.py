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
from utils import getConfigurationResult,getModelColumnById
from io import BytesIO
from django.template.loader import get_template
from django.views import View
from django.conf import settings
from ..decorators import *

# Create your views here.

@login_required
def index(request):
    context = {}
    roles = SpRoles.objects.filter(status=1) 
    permissions = SpPermissions.objects.filter(status=1) 
    modules = SpModules.objects.filter(status=1)
    for module in modules : 
        module.sub_modules = SpSubModules.objects.filter(status=1,module_id=module.id)

    departments = SpDepartments.objects.filter(status=1)
    for department in departments : 
        department.roles = SpRoles.objects.filter(status=1,department_id=department.id)
    
    for module in modules:
        for sub_module in module.sub_modules:
            permission_data = []
            for permission in permissions:
                temp = {}
                temp['id'] = permission.id
                temp['permission'] = permission.permission
                temp['slug'] = permission.slug
                if SpModulePermissions.objects.filter(module_id=module.id,sub_module_id=sub_module.id,permission_id=permission.id).exists():
                    module_permission = SpModulePermissions.objects.get(module_id=module.id,sub_module_id=sub_module.id,permission_id=permission.id)
                    temp['module_permission'] = module_permission
                    workflow = json.loads(module_permission.workflow)
                    temp['workflow_length'] = len(workflow)
                else:
                    temp['module_permission'] = None
                    temp['workflow_length'] = 0

                permission_data.append(temp)

            sub_module.permissions = permission_data
                

    context['modules'] = modules
    context['permissions'] = permissions
    context['departments'] = departments
    context['page_title'] = "Manage Permission Workflows"
    context['first_workflow_level'] =  SpWorkflowLevels.objects.get(priority='first')
    context['last_workflow_level'] =  SpWorkflowLevels.objects.get(priority='last')
    context['middle_workflow_level'] =  SpWorkflowLevels.objects.get(priority='middle')

    

    template = 'permission-workflows/index.html'

    return render(request, template, context)



@login_required
def updatePermissionWorkflows(request):
    if request.method == "POST":
        permissions = SpPermissions.objects.filter(status=1)
        sub_modules = SpSubModules.objects.filter(status=1)
        for sub_module in sub_modules :
            for permission in permissions :
                var_name = 'permission_'+ str(sub_module.id) + '_' + str(permission.id)
                # delete old data
                SpModulePermissions.objects.filter(sub_module_id=sub_module.id,permission_id=permission.id).delete()
                SpRolePermissions.objects.filter(sub_module_id=sub_module.id,permission_id=permission.id).delete()
                SpRoleWorkflowPermissions.objects.filter(sub_module_id=sub_module.id,permission_id=permission.id).delete()
                
                if var_name in request.POST:
                    module_permission = SpModulePermissions()
                    module_permission.module_id = getModelColumnById(SpSubModules,sub_module.id,'module_id')
                    module_permission.sub_module_id = sub_module.id
                    module_permission.permission_id = permission.id
                    module_permission.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                    module_permission.save()
                    total_work_flows_var = 'workflow_'+str(sub_module.id)+'_'+str(permission.id)
                    if request.POST[total_work_flows_var] :

                        module_permission.workflow = request.POST[total_work_flows_var]
                        module_permission.save()

                        total_work_flows = json.loads(request.POST[total_work_flows_var])

                        # delete old data
                        SpPermissionWorkflows.objects.filter(sub_module_id=sub_module.id,permission_id=permission.id).delete()
                        
                        for total_work_flow in total_work_flows :
                            permission_workflow = SpPermissionWorkflows()
                            permission_workflow.sub_module_id = sub_module.id
                            permission_workflow.permission_id = permission.id
                            permission_workflow.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                            permission_workflow.level_id = total_work_flow['level_id']
                            permission_workflow.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                            permission_workflow.description = total_work_flow['description']
                            permission_workflow.status = 1
                            permission_workflow.save()

                            level_roles = total_work_flow['role_id'].split(',')
                            # delete old data
                            SpPermissionWorkflowRoles.objects.filter(level_id=total_work_flow['level_id'],sub_module_id=sub_module.id,permission_id=permission.id).delete()
                            
                            
                            for level_role in level_roles:
                                permission_workflow_role = SpPermissionWorkflowRoles()
                                permission_workflow_role.sub_module_id = sub_module.id
                                permission_workflow_role.permission_id = permission.id
                                permission_workflow_role.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                                permission_workflow_role.level_id = total_work_flow['level_id']

                                if int(level_role) > 0 :
                                    permission_workflow_role.workflow_level_dept_id = getModelColumnById(SpRoles,level_role,'department_id')
                                    permission_workflow_role.workflow_level_dept_name = getModelColumnById(SpDepartments,permission_workflow_role.workflow_level_dept_id,'department_name')
                                    permission_workflow_role.workflow_level_role_id = level_role
                                    permission_workflow_role.workflow_level_role_name = getModelColumnById(SpRoles,level_role,'role_name')
                                else:
                                    permission_workflow_role.workflow_level_dept_id = None
                                    permission_workflow_role.workflow_level_dept_name = None
                                    permission_workflow_role.workflow_level_role_id = level_role
                                    permission_workflow_role.workflow_level_role_name = "Super Admin"

                                permission_workflow_role.save()

                                # add role permission & workflow
                                if int(level_role) > 0 :
                                    if not SpRolePermissions.objects.filter(role_id=level_role,sub_module_id=sub_module.id,permission_id=permission.id).exists():
                                        role_permission = SpRolePermissions()
                                        role_permission.role_id = level_role
                                        role_permission.module_id = getModelColumnById(SpSubModules,sub_module.id,'module_id')
                                        role_permission.sub_module_id = sub_module.id
                                        role_permission.permission_id = permission.id
                                        role_permission.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                                        role_permission.save()

                                        role_permission_workflow = SpRoleWorkflowPermissions()
                                        role_permission_workflow.role_id = level_role
                                        role_permission_workflow.sub_module_id = sub_module.id
                                        role_permission_workflow.permission_id = permission.id
                                        role_permission_workflow.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                                        role_permission_workflow.level_id = total_work_flow['level_id']
                                        role_permission_workflow.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                                        role_permission_workflow.description = total_work_flow['description']
                                        role_permission_workflow.workflow_level_dept_id = getModelColumnById(SpRoles,level_role,'department_id')
                                        role_permission_workflow.workflow_level_role_id = level_role
                                        role_permission_workflow.status = 1
                                        role_permission_workflow.save()


        response = {}
        response['flag'] = True
        response['message'] = "Record has been updated successfully."

        #Save Activity
        user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
        heading     = 'Workflow Permission Updated'
        activity    = 'Workflow Permission Updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
        saveActivity('Workflow Permission Updated', 'Workflow Permission Updated', heading, activity, request.user.id, user_name, 'add.png', '1', 'web.png')
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

