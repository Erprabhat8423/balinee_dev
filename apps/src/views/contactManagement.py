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

@login_required
def index(request):
    context = {}
    
    page = request.GET.get('page')  
    users = SpUsers.objects.raw('''SELECT sp_users.*,sp_user_contacts.contact_number,sp_user_contacts.contact_type FROM sp_users LEFT JOIN sp_user_contacts on sp_user_contacts.user_id = sp_users.id WHERE sp_user_contacts.is_primary=1 and sp_users.role_id > 0 order by id desc ''' )
    
    paginator = Paginator(users, getConfigurationResult('page_limit'))

    

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)  
    if page is not None:
           page = page
    else:
           page = 1
    
    for user in users:
        user_name = user.first_name+' '
        if user.middle_name is not None:
            user_name += user.middle_name+' '
        if user.last_name is not None:
            user_name += user.last_name

        user.user_name = user_name
        user_tags = SpUserTags.objects.raw('''SELECT ut.id,t.id as tag_id, t.tag, t.color, t.description FROM sp_user_tags as ut LEFT JOIN sp_tags as t on t.id = ut.tag_id WHERE ut.user_id = %s ''', [user.id])
        user.tags = user_tags
        user.total_tags =  len(user_tags)

        user.organization_name = getModelColumnById(SpOrganizations,user.organization_id,'alias')        
        if SpUserAcademicDetails.objects.filter(user_id=user.id).exists():
            academic_detail = SpUserAcademicDetails.objects.get(user_id=user.id)
            user.course = getModelColumnById(TblBranch,academic_detail.branch_id,'abbr')
            if academic_detail.year_id is not None:
                user.year_sem = academic_detail.year_id + ' year'
            else:
                user.year_sem = academic_detail.semester_id + ' semester'


    total_pages = int(paginator.count/getConfigurationResult('page_limit')) 
    if(paginator.count == 0):
        paginator.count = 1
        
    temp = int(total_pages) % paginator.count
    if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
        total_pages = total_pages+1
    else:
        total_pages = total_pages
        
        
    user_details = SpUsers.objects.exclude(role_id=0).order_by('-id').first()
    if user_details:
        role_attributes = SpRoleAttributes.objects.raw('''SELECT sp_role_attributes.attribute_id, sp_attributes.* FROM sp_role_attributes LEFT JOIN sp_attributes on sp_attributes.id = sp_role_attributes.attribute_id WHERE sp_role_attributes.role_id = %s ''', [user_details.role_id])
        personalInfo = SpUserPersonalDetails.objects.filter(user_id=user_details.id).first()
        if personalInfo:
            context['personalInfo']    = personalInfo

        user_tags = SpUserTags.objects.raw('''SELECT ut.id,t.id as tag_id, t.tag, t.color, t.description FROM sp_user_tags as ut LEFT JOIN sp_tags as t on t.id = ut.tag_id WHERE ut.user_id = %s ''', [user_details.id])
        user_details.user_tags = user_tags
        user_details.total_tags =  len(user_tags)

        

        contactInfo = SpUserContacts.objects.filter(user_id=user_details.id).first()
        context['contactInfo']     = contactInfo
        context['role_attributes'] = role_attributes


    organizations = SpOrganizations.objects.all()
    tags = SpTags.objects.all()
    context['organizations'] = organizations
    context['tags'] = tags
    context['users'] = users
    context['total_pages'] = total_pages
    context['page_limit'] = getConfigurationResult('page_limit')
    context['user_details'] = user_details
    context['page_title'] = "Manage Contact Card"
    template = 'contact-management/index.html'

    return render(request, template, context)

@login_required
def ajaxContactCardList(request):
    page = request.POST['page']
    condition = ''
    if 'search' in request.POST and request.POST['search'] != "":
        condition = "and ( sp_users.first_name like '%%"+request.POST['search']+"%%' or sp_users.middle_name like '%%"+request.POST['search']+"%%' or sp_users.last_name like '%%"+request.POST['search']+"%%' )"

    if 'org_id' in request.POST and request.POST['org_id'] != "":
        condition = condition + " and sp_users.organization_id ='"+request.POST['org_id']+"'"

    if 'status' in request.POST and request.POST['status'] != "":
        condition = condition + " and sp_users.status ='"+request.POST['status']+"'"
    if 'tag[]' in request.POST and request.POST.getlist('tag[]') != "":
        cond = ','.join(request.POST.getlist('tag[]'))
        condition += " and sp_users.id IN (select distinct user_id from sp_user_tags where tag_id in ("+cond+"))"
        
    users = SpUsers.objects.raw("""SELECT sp_users.*,sp_user_contacts.contact_number,sp_user_contacts.contact_type FROM sp_users LEFT JOIN sp_user_contacts on sp_user_contacts.user_id = sp_users.id WHERE 1 {condition} order by id desc """.format(condition=condition))
     
     
    

    paginator = Paginator(users, getConfigurationResult('page_limit'))

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)  
    if page is not None:
           page = page
    else:
           page = 1

    for user in users:
        user_name = user.first_name+' '
        if user.middle_name is not None:
            user_name += user.middle_name+' '
        if user.last_name is not None:
            user_name += user.last_name

        user.user_name = user_name

        user_tags = SpUserTags.objects.raw('''SELECT ut.id,t.id as tag_id, t.tag, t.color, t.description FROM sp_user_tags as ut LEFT JOIN sp_tags as t on t.id = ut.tag_id WHERE ut.user_id = %s ''', [user.id])
        user.tags = user_tags
        user.total_tags =  len(user_tags)
        user.organization_name = getModelColumnById(SpOrganizations,user.organization_id,'alias')
        if SpUserAcademicDetails.objects.filter(user_id=user.id).exists():
            academic_detail = SpUserAcademicDetails.objects.get(user_id=user.id)
            user.course = getModelColumnById(TblBranch,academic_detail.branch_id,'abbr')
            if academic_detail.year_id is not None:
                user.year_sem = academic_detail.year_id + ' year'
            else:
                user.year_sem = academic_detail.semester_id + ' semester'


    total_pages = int(paginator.count/getConfigurationResult('page_limit'))   
    
    if(paginator.count == 0):
        paginator.count=1
    temp = total_pages%paginator.count
    if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
        total_pages = total_pages+1
    else:
        total_pages = total_pages

    user_details = SpUsers.objects.order_by('-id').first()     
    role_attributes = SpRoleAttributes.objects.raw('''SELECT sp_role_attributes.attribute_id, sp_attributes.* FROM sp_role_attributes LEFT JOIN sp_attributes on sp_attributes.id = sp_role_attributes.attribute_id WHERE sp_role_attributes.role_id = %s ''', [user_details.role_id])
    context = {}

    context['role_attributes'] = role_attributes
    context['users']          = users
    context['user_details'] = user_details
    context['total_pages']            = total_pages
    context['page_limit']             = getConfigurationResult('page_limit')
    template = 'contact-management/ajax-contact-card-lists.html'
    return render(request, template, context)


@login_required
def ajaxContactList(request):
    page = request.GET.get('page')
    users = SpUsers.objects.raw('''SELECT sp_users.*,sp_user_contacts.contact_number,sp_user_contacts.contact_type FROM sp_users LEFT JOIN sp_user_contacts on sp_user_contacts.user_id = sp_users.id WHERE 1 order by id desc ''' )
    
                
    paginator = Paginator(users, getConfigurationResult('page_limit'))

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)  
    if page is not None:
           page = page
    else:
           page = 1


    for user in users:
        user_name = user.first_name+' '
        if user.middle_name is not None:
            user_name += user.middle_name+' '
        if user.last_name is not None:
            user_name += user.last_name

        user.user_name = user_name
        
        user_tags = SpUserTags.objects.raw('''SELECT ut.id,t.id as tag_id, t.tag, t.color, t.description FROM sp_user_tags as ut LEFT JOIN sp_tags as t on t.id = ut.tag_id WHERE ut.user_id = %s ''', [user.id])
        user.tags = user_tags
        user.total_tags =  len(user_tags)
        user.organization_name = getModelColumnById(SpOrganizations,user.organization_id,'alias')
        if SpUserAcademicDetails.objects.filter(user_id=user.id).exists():
            academic_detail = SpUserAcademicDetails.objects.get(user_id=user.id)
            user.course = getModelColumnById(TblBranch,academic_detail.branch_id,'abbr')
            if academic_detail.year_id is not None:
                user.year_sem = academic_detail.year_id + ' year'
            else:
                user.year_sem = academic_detail.semester_id + ' semester'

                
    total_pages = int(paginator.count/getConfigurationResult('page_limit'))   
    
    temp = total_pages%paginator.count
    if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
        total_pages = total_pages+1
    else:
        total_pages = total_pages

    user_details = SpUsers.objects.order_by('-id').first()     
    role_attributes = SpRoleAttributes.objects.raw('''SELECT sp_role_attributes.attribute_id, sp_attributes.* FROM sp_role_attributes LEFT JOIN sp_attributes on sp_attributes.id = sp_role_attributes.attribute_id WHERE sp_role_attributes.role_id = %s ''', [user_details.role_id])
    context = {}

    context['role_attributes'] = role_attributes
    context['users']          = users
    context['user_details'] = user_details
    context['total_pages']            = total_pages
    context['page_limit']             = getConfigurationResult('page_limit')
    template = 'contact-management/ajax-contact-lists.html'
    return render(request, template, context)


@login_required
def getUserContactRecord(request):
    context = {}
    id = request.GET.get('id')
    user_details = SpUsers.objects.get(id=id)    

    if user_details:
        role_attributes = SpRoleAttributes.objects.raw('''SELECT sp_role_attributes.attribute_id, sp_attributes.* FROM sp_role_attributes LEFT JOIN sp_attributes on sp_attributes.id = sp_role_attributes.attribute_id WHERE sp_role_attributes.role_id = %s ''', [user_details.role_id])

        contactInfo = SpUserContacts.objects.filter(user_id=id).first()

        user_tags = SpUserTags.objects.raw('''SELECT ut.id,t.id as tag_id, t.tag, t.color, t.description FROM sp_user_tags as ut LEFT JOIN sp_tags as t on t.id = ut.tag_id WHERE ut.user_id = %s ''', [id])
        context['user_tags'] = user_tags
        context['total_tags'] =  len(user_tags)

        context['userContact_details']     = user_details
        context['contactInfo']     = contactInfo
        context['role_attributes']     = role_attributes
        personalInfo = SpUserPersonalDetails.objects.filter(user_id=id).first()
        if personalInfo:
            context['personalInfo'] = personalInfo
    

    template = 'contact-management/get-user-contact-record.html'
    return render(request, template, context)

@login_required
def getUserAttributeDetail(request,user_id,attribute_name):
    # print(user_id)
    context = {}
    if attribute_name=='PersonalInfo':
        personalInfo = SpUserPersonalDetails.objects.filter(user_id=user_id).first()
        context['personalInfo']     = personalInfo
        template = 'contact-management/personal_info.html'
    if attribute_name=='academicInfo':
        template = 'contact-management/academic_info.html'
    if attribute_name=='FinancialInfo':
        if SpUserBankDetails.objects.filter(user_id=user_id).exists():
            bankInfo = SpUserBankDetails.objects.filter(user_id=user_id)
            financialInfo = SpUserFinancialDetails.objects.filter(user_id=user_id).first() 
            context['bankDetails']     = bankInfo
            context['financialInfo']     = financialInfo
        template = 'contact-management/financial_info.html'
    if attribute_name=='OfficalInfo':
        user_details = SpUsers.objects.get(id=user_id) 
        officalInfo = SpUserOfficialDetails.objects.filter(user_id=user_id).first() 
        context['user_details']     = user_details
        context['officalInfo']     = officalInfo
        template = 'contact-management/official_info.html'
    if attribute_name=='vehicleInfo':
        user_details = SpVehicles.objects.filter(user_id=user_id).first() 
        context['vehicleInfo']     = user_details
        template = 'contact-management/vehicle_info.html'
    if attribute_name=='biometricInfo':
        biometricInfo = SpUserBiometricDetails.objects.filter(user_id=user_id).first() 
        context['biometricInfo']     = biometricInfo
        template = 'contact-management/biometric_info.html'
    if attribute_name=='documentInfo':
        documentInfo = SpUserDocuments.objects.filter(user_id=user_id)
        context['documentInfo']     = documentInfo
        template = 'contact-management/document_info.html'
    return render(request, template, context)

@login_required
def getRoleOrganizationOption(request,role_id):
    response = {}
    response['role'] = model_to_dict(SpRoles.objects.get(id=role_id))
    options = ''
    organizations = SpOrganizations.objects.filter(id=getModelColumnById(SpRoles,role_id,'organization_id'))
    for organization in organizations :
        options += "<option value="+str(organization.id)+" selected>"+organization.organization_name+"</option>"

    response['options'] = options
    return JsonResponse(response)

@login_required
def addContactCard(request):
    try:
        context = {}
        # role = SpRoles.objects.get(id=role_id)
        roles = SpRoles.objects.all().order_by('-id')
        contact_types = SpContactTypes.objects.all().order_by('-id')
        business_types = SpBusinessTypes.objects.all().order_by('-id')
        attributes = SpAttributes.objects.all().exclude(id=1)
        context['organizations'] = SpOrganizations.objects.all()
        context['roles'] = roles
        context['contact_types'] = contact_types
        context['business_types'] = business_types
        context['attributes'] = attributes
        context['required_documents'] = SpRequiredDocuments.objects.all()
        template = 'contact-management/add-contact-card.html'
        return render(request,template ,context)
    except SpRoles.DoesNotExist:
        return HttpResponse('role not found')

@login_required
def editContactCard(request):
    try:
        context = {}
        user_id = request.GET['user_id']
        roles = SpRoles.objects.all().order_by('-id')
        contact_types = SpContactTypes.objects.all().order_by('-id')
        business_types = SpBusinessTypes.objects.all().order_by('-id')
        attributes = SpAttributes.objects.all().exclude(id=1)

        business_details = SpUserBusinessDetails.objects.filter(user_id=user_id).first()
        if business_details:
            business_details.contact_persons  = json.loads(business_details.contact_persons)
        
        context['user_detail'] = user_detail = SpUsers.objects.filter(id=user_id).first()
        context['organizations'] = SpOrganizations.objects.filter(id=user_detail.organization_id)
        context['business_details'] = business_details
        context['business_details_count'] = SpUserBusinessDetails.objects.filter(user_id=user_id).count()
        
        context['contact_details'] = SpUserContacts.objects.filter(user_id=user_id)
        context['roles'] = roles
        context['contact_types'] = contact_types
        context['business_types'] = business_types
        context['attributes'] = attributes
        context['required_documents'] = SpRequiredDocuments.objects.all()
        template = 'contact-management/edit-contact-card.html'
        return render(request,template ,context)
    except SpRoles.DoesNotExist:
        return HttpResponse('role not found')

@login_required
def getRoleTypeAttributesEditForm(request,user_id,role_id):
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
            
            if (role_attribute.attribute_id==2):
                

                    context['income_categories'] = SpIncomeCategories.objects.all()
                    context['previlege_categories'] = SpPrevilegeCategories.objects.all()
                    context['tags'] = SpTags.objects.all()
                    context['personal_detail'] = SpUserPersonalDetails.objects.filter(user_id=user_id).first()
                    context['tag_detail_id'] = list(SpUserTags.objects.filter(user_id=user_id).values_list("tag_id" , flat=True))
                    # print(list(tag_detail))
            elif (role_attribute.attribute_id==3):
                    context['sessions'] = SpSessions.objects.all()
                    sessions = SpSessions.objects.filter(is_active=1)
                    for session in sessions:
                        session.admission_procedures = SpAdmissionProcedures.objects.filter(session_id=session.id,is_active=1)



                    context['sessions'] = sessions
                    organizations = SpOrganizations.objects.filter(id=getModelColumnById(SpRoles,role_id,'organization_id'))
                    context['organizations'] = organizations
                    context['branches'] = TblBranch.objects.all()
                    context['years'] = SpYears.objects.all()
                    context['semesters'] = TblSemester.objects.all()
                    context['teachers'] = SpUsers.objects.filter(role_id=30)
                    context['academic_detail'] = SpUserAcademicDetails.objects.filter(user_id=user_id).first()
            elif (role_attribute.attribute_id==4):
                    organizations = SpOrganizations.objects.filter(id=getModelColumnById(SpRoles,role_id,'organization_id'))
                    context['organizations'] = organizations
                    context['pay_grades'] = SpPayGrades.objects.all()
                    context['additional_responsibilities'] = SpAdditionalResponsibilities.objects.all()
                    context['working_hours'] = SpWorkingHours.objects.all()
                    context['user_details'] = SpUsers.objects.get(id=user_id)
                    context['official_detail'] = SpUserOfficialDetails.objects.filter(user_id=user_id).first()

            elif (role_attribute.attribute_id==5):
                    context['banks'] = SpBanks.objects.all()
                    context['salary_additions'] = SpSalaryAdditionTypes.objects.all()
                    context['salary_deductions'] = SpSalaryDeductionTypes.objects.all()
                    context['financial_detail'] = SpUserFinancialDetails.objects.filter(user_id=user_id).first()
                    context['bank_details'] = SpUserBankDetails.objects.filter(user_id=user_id).all()
                    context['bank_detail_count'] = SpUserBankDetails.objects.filter(user_id=user_id).count()
            elif (role_attribute.attribute_id==6):
                    context['vehicle_types'] = SpVehicleTypes.objects.all()
                    context['vehicle_detail'] = SpVehicles.objects.filter(user_id=user_id).first()
            elif (role_attribute.attribute_id==7):
                    context['biometric_detail'] = SpUserBiometricDetails.objects.filter(user_id=user_id).first()
            elif (role_attribute.attribute_id==8):
                    context['document_details'] = SpUserDocuments.objects.filter(user_id=user_id).all()


        context['attributes'] = attributes
        context['role_attributes'] = role_attributes
        context['role_attribute_ids'] = role_attribute_ids
        context['required_documents'] = SpRequiredDocuments.objects.all()
        context['role_id'] = role_id
        context['is_outsider'] = role.is_outsider
        template = 'contact-management/role_type_attributes.html'
        return render(request,template ,context)
    except SpRoles.DoesNotExist:
        return HttpResponse('role not found')

@login_required
def getRoleTypeAttributesForm(request,role_id):
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
            
            if (role_attribute.attribute_id==2):
                context['income_categories'] = SpIncomeCategories.objects.all()
                context['previlege_categories'] = SpPrevilegeCategories.objects.all()
                context['tags'] = SpTags.objects.all()
            elif (role_attribute.attribute_id==3):
                context['sessions'] = SpSessions.objects.all()
                sessions = SpSessions.objects.filter(is_active=1)
                for session in sessions:
                    session.admission_procedures = SpAdmissionProcedures.objects.filter(session_id=session.id,is_active=1)

                context['sessions'] = sessions
                organizations = SpOrganizations.objects.filter(id=getModelColumnById(SpRoles,role_id,'organization_id'))
                context['organizations'] = organizations
                context['branches'] = TblBranch.objects.all()
                context['years'] = SpYears.objects.all()
                context['semesters'] = TblSemester.objects.all()
                context['teachers'] = SpUsers.objects.filter(role_id=30)
            elif (role_attribute.attribute_id==4):
                organizations = SpOrganizations.objects.filter(id=getModelColumnById(SpRoles,role_id,'organization_id'))
                context['organizations'] = organizations
                context['pay_grades'] = SpPayGrades.objects.all()
                context['additional_responsibilities'] = SpAdditionalResponsibilities.objects.all()
                context['working_hours'] = SpWorkingHours.objects.all()
            elif (role_attribute.attribute_id==5):
                context['banks'] = SpBanks.objects.all()
                context['salary_additions'] = SpSalaryAdditionTypes.objects.all()
                context['salary_deductions'] = SpSalaryDeductionTypes.objects.all()
            elif (role_attribute.attribute_id==6):
                context['vehicle_types'] = SpVehicleTypes.objects.all()

        context['attributes'] = attributes
        context['role_attributes'] = role_attributes
        context['role_attribute_ids'] = role_attribute_ids
        context['required_documents'] = SpRequiredDocuments.objects.all()
        context['role_id'] = role_id
        context['is_outsider'] = role.is_outsider
        template = 'contact-management/role_type_attributes.html'
        return render(request,template ,context)
    except SpRoles.DoesNotExist:
        return HttpResponse('role not found')

@login_required
def getRoleTypeAttributes(request,role_id):
    try:
        context = {}
        role = SpRoles.objects.get(id=role_id)
        role_attributes = SpRoleAttributes.objects.raw('''SELECT sp_role_attributes.attribute_id, sp_attributes.* FROM sp_role_attributes LEFT JOIN sp_attributes on sp_attributes.id = sp_role_attributes.attribute_id WHERE sp_role_attributes.role_id = %s ''', [role_id])
        response = {}
        options = '<option value="" >Select Attribute</option>'
        for role_attribute in role_attributes :
            options += "<option value="+str(role_attribute.id)+" selected>"+role_attribute.attribute+"</option>"

        response['options'] = options
        return JsonResponse(response)
    except SpRoles.DoesNotExist:
        return HttpResponse('role not found')

@login_required
def searchDepartments(request,location_id):
    try:
        departments = SpDepartments.objects.filter(organization_id=location_id)
        response = {}
        options = '<option value="" >Select Departments</option>'
        for department in departments:
            options += "<option value="+str(department.id)+" selected>"+department.department_name+"</option>"

        response['options'] = options
        return JsonResponse(response)
    except SpRoles.DoesNotExist:
        return HttpResponse('role not found')

@login_required
def searchRoles(request):
    try:
        department_id = request.GET['department']
        if department_id:
            roles = list(SpRoles.objects.filter(department_id=department_id).extra(select={'text':'role_name'}).values('id','text'))
        else:
            roles = list(SpRoles.objects.extra(select={'text':'role_name'}).values('id','text'))

        response = {}
        pagination = {}
        pagination['more'] = True
        response['results'] = roles
        response['pagination'] = pagination
        return JsonResponse(response)
    except SpRoles.DoesNotExist:
        return HttpResponse('role not found')

@login_required
def admissionProcedureDetails(request,admission_procedures_id):
    try:
        context = {}
        admission_procedure = SpAdmissionProcedures.objects.filter(id=admission_procedures_id).first()
        branches = SpAdmissionProcedureBranches.objects.filter(admission_procedure_id=admission_procedures_id)
        
        response = {}
        options = '<option value="" >Select Branch</option>'
        if branches:
            for branch in branches :
                options += "<option value="+str(branch.branch_id)+" selected>"+branch.branch+"</option>"

        response['options'] = options
        return JsonResponse(response)
    except SpRoles.DoesNotExist:
        return HttpResponse('role not found')


@login_required
def saveContact(request):
    context = {}
    errors = []
    if request.method == "POST":
        role_id = request.POST['role_id']
        #Sever-side Validation
        field_name = 'role_id'
        if field_name in request.POST and request.POST[field_name] == "":
            tmp = {}
            tmp['name'] = field_name
            tmp['message'] = "Role is Required"
            errors.append(tmp)
        #Sever-side Validation
        field_name = 'locations_list'
        if field_name in request.POST and request.POST[field_name] == "":
            tmp = {}
            tmp['name'] = field_name
            tmp['message'] = "Institutions is Required"
            errors.append(tmp)
        #Sever-side Validation
        if 'is_role_outsider' in request.POST and request.POST['is_role_outsider'] != '': 
            if request.POST['is_role_outsider'] == '1': 
                field_name = 'organisation_id'
                if field_name in request.POST and request.POST[field_name] == "":
                    tmp = {}
                    tmp['name'] = field_name
                    tmp['message'] = "Organization is Required"
                    errors.append(tmp)
        #Sever-side Validation              
        field_name = 'first_name'
        if field_name in request.POST and request.POST[field_name] == "":
            tmp = {}
            tmp['name'] = field_name
            tmp['message'] = "First Name is Required"
            errors.append(tmp)
        #Sever-side Validation
        field_name = 'last_name'
        if field_name in request.POST and request.POST[field_name] == "":
            tmp = {}
            tmp['name'] = field_name
            tmp['message'] = "Last Name is Required"
            errors.append(tmp)
        #Sever-side Validation
        field_name = 'alias_name'
        if field_name in request.POST and request.POST[field_name] == "":
            tmp = {}
            tmp['name'] = field_name
            tmp['message'] = "Alias is Required"
            errors.append(tmp)
        if field_name in request.POST and request.POST[field_name] != "":
            if SpUsers.objects.filter(alias=request.POST[field_name]).exists():
                tmp = {}
                tmp['name'] = field_name
                tmp['message'] = "Alias already exists"
                errors.append(tmp)

        #Sever-side Validation
        field_name = 'email'
        if field_name in request.POST and request.POST[field_name] == "":
            tmp = {}
            tmp['name'] = field_name
            tmp['message'] = "Email is Required"
            errors.append(tmp)
        
        if bool(request.FILES.get('profile_image', False)) == True:
           
            uploaded_profile_image = request.FILES['profile_image']
            storage = FileSystemStorage('media/profileImage/')
            timestamp = int(time.time())
            profile_image_name = uploaded_profile_image.name
            temp = profile_image_name.split('.')
            profile_image_name = 'profile_'+str(timestamp)+"."+temp[(len(temp) - 1)]
            
            profile_image = storage.save(profile_image_name, uploaded_profile_image)            
            profile_image = storage.url(profile_image)
            profile_image = profile_image.split('media/')[1]
            profile_image = "media/profileImage/"+profile_image
        
        else:
            profile_image = None

        
        #Sever-side Validation
        if '2' in request.POST.getlist('attribute_id[]'):
            attrChecker = checkAttributeValue(request,role_id,2,'father_first_name',"Father's first name is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'father_last_name',"Father's last name is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'mother_first_name', "Mother's first name is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'mother_last_name', "Mother's last name is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'spouse_name', "Spouce name is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'spouse_employer', "Spouse employer name is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'spouse_work_phone', "Spouse work phone number is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'no_of_child', "Number of child is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'gender', "gender is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'date_of_birth', "Date of birth is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'birth_place', "Birth Place is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'marital_status', "Marital status is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'blood_group', "Blood group is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'disability', "Disability is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'identification_mark', "Identification mark is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'caste_category', "Caste category is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'income_category', "Income category is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'previlege_category', "Previlege category is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'c_country', "Country is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'c_state', "State is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'c_city', "City is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'c_address_line_1', "Address line 1 is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'c_address_line_2', "Address line 2 is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'c_pincode', "Pincode is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'p_country', "Permanent country is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'p_state', "Permanent state is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'p_city', "Permanent City is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'p_address_line_1', "Permanent Address line 1 is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'p_address_line_2', "Permanent Address line 2 is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'p_pincode', "Permanent pincode is required")
            if attrChecker:
                errors.append(attrChecker)
            
            attrChecker = checkAttributeValue(request,role_id,2,'tags[]', "Tags is required")
            if attrChecker:
                errors.append(attrChecker)

        #Sever-side Validation
        if '3' in request.POST.getlist('attribute_id[]'):
            attrChecker = checkAttributeValue(request,role_id,3,'student_location', "College Name is Required")
            if attrChecker:
                errors.append(attrChecker)
            
            attrChecker = checkAttributeValue(request,role_id,3,'branch', "Branch is Required")
            if attrChecker:
                errors.append(attrChecker)
            
            attrChecker = checkAttributeValue(request,role_id,3,'registration', "Registration Number is Required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,3,'year', "Year/Semester is Required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,3,'date_of_admission', "Admission Date is Required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,3,'teacher_gaurdian_name', "Teacher's Gaurdian Name is Required")
            if attrChecker:
                errors.append(attrChecker)
            
        #Sever-side Validation
        if '4' in request.POST.getlist('attribute_id[]'):
            attrChecker = checkAttributeValue(request,role_id,4,'location',"Institution is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'department',"Department is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'designation', "Designation is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'paygrade', "Pay grade is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'employment_term', "Employment term is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'additional_responsibility[]', "Additional responsibility is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'working_hour', "Working hour is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'date_of_joining', "Date of joining is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'previous_employer', "Previous employer is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'experience', "Experience is required")
            if attrChecker:
                errors.append(attrChecker)
            
            attrChecker = checkAttributeValue(request,role_id,4,'login_id', "Login Id is required")
            if attrChecker:
                errors.append(attrChecker)
            
            attrChecker = checkAttributeValue(request,role_id,4,'password', "Password is required")
            if attrChecker:
                errors.append(attrChecker)
            
            
        #Sever-side Validation
        if '5' in request.POST.getlist('attribute_id[]'):
            # attrChecker = checkAttributeValue(request,role_id,5,'is_health_insurance',"Health insurance is required")
            # if attrChecker:
            #     errors.append(attrChecker)

            # attrChecker = checkAttributeValue(request,role_id,5,'is_salary_saving_scheme',"Salary saving scheme is required")
            # if attrChecker:
            #     errors.append(attrChecker)

            # attrChecker = checkAttributeValue(request,role_id,5,'is_wage_tax_applicable', "Wage tax applicable is required")
            # if attrChecker:
            #     errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,5,'gstin', "GSTIN is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,5,'salary_addition[]', "Salary addition is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,5,'salary_deduction[]', "Salary deduction is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,5,'bank[]', "Bank name is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,5,'ifsc_code[]', "IFSC code is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,5,'bank_account_no[]', "Bank account number is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,5,'account_holder_name[]', "Account holder name is required")
            if attrChecker:
                errors.append(attrChecker)
        #Sever-side Validation
        if '6' in request.POST.getlist('attribute_id[]'):
            attrChecker = checkAttributeValue(request,role_id,6,'vehicle_type',"Vehicle type is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,6,'fuel_type',"Fuel type is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,6,'vehicle_no', "Vehicle Number is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,6,'chessis_no', "Chessis Number is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,6,'engine_no', "Engine Number is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,6,'dl_no', "Driving License Number is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,6,'dl_expiry', "Driving License Expiry is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,6,'seating_capacity_no', "Seating Capacity Number is required")
            if attrChecker:
                errors.append(attrChecker)
        #Sever-side Validation
        if '7' in request.POST.getlist('attribute_id[]'):
            attrChecker = checkAttributeValue(request,role_id,7,'finger_1',"Finger Print is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,7,'finger_2',"Finger Print is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,7,'finger_3', "Finger Print is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,7,'finger_4', "Finger Print is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,7,'finger_5', "Finger Print is required")
            if attrChecker:
                errors.append(attrChecker)

                        
        
        if len(errors)>0:
            context['flag'] = False
            context['errors'] = errors
            return JsonResponse(context)

        user_data = SpUsers()
        user_data.role_id = role_id 
        user_data.role_name = getModelColumnByColumnId(SpRoles,'id',role_id,'role_name')
        user_data.organization_id = request.POST['locations_list']
        user_data.organization_name = getModelColumnByColumnId(SpOrganizations,'id',request.POST['locations_list'],'organization_name')
        user_data.salutation = request.POST['salutation_id']
        user_data.first_name = request.POST['first_name']
        user_data.profile_image = profile_image
        # if (request.POST['middle_name']):
        user_data.middle_name = checkPostNone(request,'middle_name')
        user_data.last_name = request.POST['last_name']
        if (request.POST['email']):
            user_data.official_email = request.POST['email']
        if (request.POST['alias_name']):
            user_data.alias = request.POST['alias_name']
        

        user_data.created_by = request.user.id
        user_data.save()
        
        contact_numbers  = request.POST.getlist('contact_number[]') 
        contact_types  = request.POST.getlist('contact_type[]') 
        primary_contacts  = request.POST.getlist('primary_contact[]') 
        i=0
        for id, val in enumerate(contact_numbers):
            contact_data = SpUserContacts()
            contact_data.user_id = user_data.id 
            contact_data.contact_type_id = contact_types[id]
            contact_data.contact_type = getModelColumnByColumnId(SpContactTypes,'id',contact_types[id],'contact_type')
            contact_data.contact_number = contact_numbers[id]
            contact_data.is_primary = primary_contacts[id]
            contact_data.save()
            
           
        if request.POST['business_type']:
            contact_first_names  = request.POST.getlist('contact_person_first_name[]') 
            contact_middle_names  = request.POST.getlist('contact_person_middle_name[]') 
            contact_last_names  = request.POST.getlist('contact_person_last_name[]') 
            contact_person_numbers  = request.POST.getlist('contact_person_mobile[]') 
            contact_emails  = request.POST.getlist('contact_person_email[]') 
            contact_designations  = request.POST.getlist('contact_person_designation[]') 
            contactList = []
            for id, val in enumerate(contact_first_names):
                tmp = {}
                tmp['contact_first_name'] = contact_first_names[id]
                tmp['contact_middle_name'] = contact_middle_names[id]
                tmp['contact_last_name'] = contact_last_names[id]
                tmp['contact_person_number'] = contact_person_numbers[id]
                tmp['contact_email'] = contact_emails[id]
                tmp['contact_designation'] = contact_designations[id]
                contactList.append(tmp)

            business_data = SpUserBusinessDetails()
            business_data.user_id = user_data.id   
            business_data.business_type_id = request.POST['business_type']
            business_data.business_type = getModelColumnByColumnId(SpBusinessTypes,'id',request.POST['business_type'],'business_type')
            business_data.contact_persons = json.dumps(contactList)
            business_data.save()


            # Create Contact person as Contacts
            if contact_first_names:
                for id, val in enumerate(contact_first_names):
                    contactDetails = SpContacts()
                    contactDetails.type = 1  
                    contactDetails.first_name = contact_first_names[id]
                    contactDetails.middle_name = contact_middle_names[id]
                    contactDetails.last_name = contact_last_names[id]
                    contactDetails.email = contact_emails[id]
                    contactDetails.designation = contact_designations[id]
                    contactDetails.phone = contact_person_numbers[id]
                    contactDetails.created_by = request.user.id
                    contactDetails.save()

                    if contact_designations[id]:
                        tag = SpTags.objects.filter(tag=contact_designations[id]).first()
                        if not tag:
                            tag = SpTags()
                            tag.tag = contact_designations[id]
                            tag.color = '#2878B5'
                            tag.save()
                        contact_tag = SpContactTags()
                        contact_tag.contact_id = contactDetails.id
                        contact_tag.tag_id = tag.id
                        contact_tag.save()

                    if 'tags[]' in request.POST:
                        tagList = request.POST.getlist('tags[]') 
                        if tagList:
                            for id, val in enumerate(tagList):
                                contact_tag = SpContactTags.objects.filter(contact_id=contactDetails.id,tag_id=tagList[id]).first()
                                if not contact_tag:
                                    contact_tag = SpContactTags()
                                    contact_tag.contact_id = contactDetails.id
                                    contact_tag.tag_id = tagList[id]
                                    contact_tag.save()
        
        # personal details
        if '2' in request.POST.getlist('attribute_id[]'):

            personal_detail = SpUserPersonalDetails()
            personal_detail.user_id = user_data.id
            personal_detail.father_first_name = request.POST['father_first_name']                    
            personal_detail.father_last_name = request.POST['father_last_name']
            personal_detail.mother_first_name = request.POST['mother_first_name']
            personal_detail.mother_last_name = request.POST['mother_last_name']
            personal_detail.spouse_name = request.POST['spouse_name']
            personal_detail.spouse_employer = request.POST['spouse_employer']
            personal_detail.spouse_work_phone = request.POST['spouse_work_phone']
            if request.POST['no_of_child']:
                personal_detail.no_of_children = request.POST['no_of_child']
            personal_detail.gender = request.POST['gender']
            personal_detail.date_of_birth = datetime.strptime(request.POST['date_of_birth'], "%d/%m/%Y").strftime('%Y-%m-%d') 
            personal_detail.place_of_birth = request.POST['birth_place']
            personal_detail.martial_status = request.POST['marital_status']
            personal_detail.blood_group = request.POST['blood_group']
            personal_detail.disability = request.POST['disability']
            personal_detail.identification_mark = request.POST['identification_mark']
            personal_detail.caste_category = request.POST['caste_category']
            if request.POST['income_category']:
                personal_detail.income_category_id = request.POST['income_category']
                personal_detail.income_category = getModelColumnByColumnId(SpIncomeCategories,'id',request.POST['income_category'],'income_category') 
            if request.POST['previlege_category']:
                personal_detail.previlege_category_id = request.POST['previlege_category']
                personal_detail.previlege_category = getModelColumnByColumnId(SpPrevilegeCategories,'id',request.POST['previlege_category'],'previlege_category') 

            personal_detail.c_country = checkPostNone(request,'c_country')
            personal_detail.c_state = checkPostNone(request,'c_state')
            personal_detail.c_city = checkPostNone(request,'c_city')
            personal_detail.c_address_line_1 = checkPostNone(request,'c_address_line_1')
            personal_detail.c_address_line_2 = checkPostNone(request,'c_address_line_2')
            personal_detail.c_pincode = checkPostNone(request,'c_pincode')

            if 'both_address_same' in request.POST:
                if request.POST['both_address_same']:
                    personal_detail.p_country = checkPostNone(request,'c_country')
                    personal_detail.p_state = checkPostNone(request,'c_state')
                    personal_detail.p_city = checkPostNone(request,'c_city')
                    personal_detail.p_address_line_1 = checkPostNone(request,'c_address_line_1')
                    personal_detail.p_address_line_2 = checkPostNone(request,'c_address_line_2')
                    personal_detail.p_pincode = checkPostNone(request,'c_pincode')
            else:
                personal_detail.p_country = checkPostNone(request,'p_country')
                personal_detail.p_state = checkPostNone(request,'p_state')
                personal_detail.p_city = checkPostNone(request,'p_city')
                personal_detail.p_address_line_1 = checkPostNone(request,'p_address_line_1')
                personal_detail.p_address_line_2 = checkPostNone(request,'p_address_line_2')
                personal_detail.p_pincode = checkPostNone(request,'p_pincode')
            personal_detail.save()

            if 'tags[]' in request.POST:
                tagList = request.POST.getlist('tags[]') 
                if tagList:
                    for id, val in enumerate(tagList):
                        user_tag = SpUserTags.objects.filter(user_id=user_data.id,tag_id=tagList[id]).first()
                        if not user_tag:
                            user_tag = SpUserTags()
                            user_tag.user_id = user_data.id
                            user_tag.tag_id = tagList[id]
                            user_tag.save()
        # personal details

        # Academic details
        if '3' in request.POST.getlist('attribute_id[]'):
            academic_detail = SpUserAcademicDetails()
            academic_detail.user_id = user_data.id
            if checkPostNone(request,'student_location'):
                academic_detail.location_id = request.POST['student_location']

            if checkPostNone(request,'branch'):
                academic_detail.branch_id = request.POST['branch']

            if checkPostNone(request,'year'):
                yearList = request.POST['year'].split("_")
                if 'year' in yearList:
                    academic_detail.year_id = request.POST['year']
                elif 'sem' in yearList:
                    academic_detail.semester_id = request.POST['year']

            if checkPostNone(request,'date_of_admission'):
                academic_detail.date_of_admission = datetime.strptime(request.POST['date_of_admission'], "%d/%m/%Y").strftime('%Y-%m-%d')

            if checkPostNone(request,'registration'):
                academic_detail.registration_no = request.POST['registration']

            if checkPostNone(request,'teacher_gaurdian_name'):
                academic_detail.teacher_guardian_id = request.POST['teacher_gaurdian_name']
            academic_detail.save() 

            tag = SpTags.objects.filter(tag='Student').first()
            if not tag:
                tag = SpTags()
                tag.tag = 'Student'
                tag.color = '#2878B5'
                tag.save()
            users_tag = SpUserTags()
            users_tag.user_id = user_data.id
            users_tag.tag_id = tag.id
            users_tag.save()
        # Academic details

       

        # Official details
        if '4' in request.POST.getlist('attribute_id[]'):
            official_detail = SpUserOfficialDetails()
            official_detail.user_id = user_data.id
            if request.POST['location']:
                official_detail.location_id = request.POST['location']
                official_detail.location = getModelColumnByColumnId(SpOrganizations,'id',request.POST['location'],'organization_name')

            if checkPostNone(request,'department'):
                official_detail.department_id = request.POST['department']
                official_detail.department = getModelColumnByColumnId(SpDepartments,'id',request.POST['department'],'department_name')

            if checkPostNone(request,'designation'):
                official_detail.designation_id = request.POST['designation']
                official_detail.designation = getModelColumnByColumnId(SpRoles,'id',request.POST['designation'],'role_name')

            if checkPostNone(request,'paygrade'):
                official_detail.pay_grade = request.POST['paygrade']

            if checkPostNone(request,'employment_term'):
                official_detail.employment_term = request.POST['employment_term']

            if request.POST.getlist('additional_responsibility[]'):
                separator = ','
                additional_responsibilities = separator.join(request.POST.getlist('additional_responsibility[]'))
                official_detail.additional_responsibilities = additional_responsibilities
            
            if checkPostNone(request,'working_hour'):
                official_detail.working_hour = request.POST['working_hour']

            if checkPostNone(request,'date_of_joining'):
                official_detail.date_of_joining = datetime.strptime(request.POST['date_of_joining'], "%d/%m/%Y").strftime('%Y-%m-%d')

            if checkPostNone(request,'previous_employer'):
                official_detail.previous_employer = request.POST['previous_employer']

            if checkPostNone(request,'experience'):
                official_detail.years_of_experience = request.POST['experience']
            official_detail.save()
            

            user_data.emp_sap_id = request.POST['login_id']
            user_data.plain_password = request.POST['password']
            user_data.password = make_password(str(request.POST['password']))
            user_data.save()    


            if request.POST['location']:
                tag_name = getModelColumnById(SpRoles,request.POST['designation'],'role_name')
                tag = SpTags.objects.filter(tag=tag_name).first()
                if not tag:
                    tag = SpTags()
                    tag.tag = tag_name
                    tag.color = '#2878B5'
                    tag.save()
                user_tag = SpUserTags()
                user_tag.user_id = user_data.id
                user_tag.tag_id = tag.id
                user_tag.save()

            if 'tags[]' in request.POST:
                tagList = request.POST.getlist('tags[]') 
                if tagList:
                    for id, val in enumerate(tagList):
                        role_tag = SpUserTags.objects.filter(user_id = user_data.id,tag_id=tagList[id]).first()
                        if not role_tag:
                            role_tag = SpUserTags()
                            role_tag.user_id = user_data.id
                            role_tag.tag_id = tagList[id]
                            role_tag.save()
        # Official details

        # Financial details
        if '5' in request.POST.getlist('attribute_id[]'):
            financial_detail = SpUserFinancialDetails()
            financial_detail.user_id = user_data.id      

            if request.POST['is_health_insurance']:
                financial_detail.is_health_insurance = request.POST['is_health_insurance']    
                financial_detail.health_insurance = request.POST['health_insurence']  
            if request.POST['is_salary_saving_scheme']:
                financial_detail.salary_saving_scheme = request.POST['salary_saving_scheme'] 
            if request.POST['is_wage_tax_applicable']:
                financial_detail.wage_tax = request.POST['wage_tax'] 
            if request.POST['gstin']:
                financial_detail.gstin = request.POST['gstin']    
            if request.POST.getlist('salary_addition[]'):
                separator = ','
                financial_detail.salary_addition = separator.join(request.POST.getlist('salary_addition[]'))
            if request.POST.getlist('salary_deduction[]'):
                separator = ','
                financial_detail.salary_deduction = separator.join(request.POST.getlist('salary_deduction[]')) 
            financial_detail.save()

            if request.POST.getlist('bank[]'):
                bankList = request.POST.getlist('bank[]')
                ifsc_code  = request.POST.getlist('ifsc_code[]') 
                bank_account_no  = request.POST.getlist('bank_account_no[]') 
                account_holder_name  = request.POST.getlist('account_holder_name[]') 
                for id, val in enumerate(bankList):
                    bank_detail = SpUserBankDetails()
                    bank_detail.user_id = user_data.id
                    if bankList[id]:
                        bank_detail.bank_id = bankList[id]
                        bank_detail.bank_name = getModelColumnByColumnId(SpBanks,'id',bankList[id],'bank_name')
                    bank_detail.ifsc_code = ifsc_code[id]
                    bank_detail.bank_account_no = bank_account_no[id]
                    bank_detail.account_holder_name = account_holder_name[id]
                    bank_detail.save()
        # Financial details


        # Vehicle details
        if '6' in request.POST.getlist('attribute_id[]'):
            vehicle_detail = SpVehicles()
            vehicle_detail.user_id = user_data.id     
            if request.POST['vehicle_type']:
                vehicle_detail.vehicle_type = request.POST['vehicle_type']
            vehicle_detail.fuel_type = request.POST['fuel_type']
            vehicle_detail.registration_number = request.POST['vehicle_no']
            vehicle_detail.chassis_no = request.POST['chessis_no']
            vehicle_detail.engine_no = request.POST['engine_no']
            vehicle_detail.driver_id = request.POST['dl_no']
            if request.POST['dl_expiry']:
                vehicle_detail.dl_expiry = datetime.strptime(request.POST['dl_expiry'], "%d/%m/%Y").strftime('%Y-%m-%d')
            if request.POST['seating_capacity_no']:
                vehicle_detail.seating_capacity_standard = request.POST['seating_capacity_no']
            vehicle_detail.save()
        # Vehicle details

        # Biometrics details
        if '7' in request.POST.getlist('attribute_id[]'):
            biometric_detail = SpUserBiometricDetails()
            biometric_detail.user_id = user_data.id 
            biometric_detail.finger_1 = checkPostNone(request,'finger_1')
            biometric_detail.finger_2 = checkPostNone(request,'finger_2')
            biometric_detail.finger_3 = checkPostNone(request,'finger_3')
            biometric_detail.finger_4 = checkPostNone(request,'finger_4')
            biometric_detail.finger_5 = checkPostNone(request,'finger_5')
            biometric_detail.save()
        # Biometrics details

        # Documents details
        required_docs = SpRequiredDocuments.objects.all()
        for required_doc in required_docs:
            var_name  = slugify(required_doc.document)
            if var_name in request.POST and request.POST[var_name] != "":
                document = SpUserDocuments()
                document.user_id = user_data.id
                document.document_id  = required_doc.id
                document.document_name  = required_doc.document
                document.ducument_number  = request.POST[var_name]
                document.save()
        # Documents details

        contactDetailsInfo = SpContacts()
        contactDetailsInfo.type = 1  
        contactDetailsInfo.first_name = request.POST['first_name']
        contactDetailsInfo.middle_name = request.POST['middle_name']
        contactDetailsInfo.last_name = request.POST['last_name']
        contactDetailsInfo.email = request.POST['email']
        if request.POST.getlist('contact_number[]'):
            contact_number = request.POST.getlist('contact_number[]')
            primary_contact = request.POST.getlist('primary_contact[]')
            for id, val in enumerate(contact_number):
                if primary_contact[id]==1:
                    contactDetailsInfo.phone = contact_number[id]

        contactDetailsInfo.state = checkPostNone(request,'c_state')
        contactDetailsInfo.city = checkPostNone(request,'c_city')
        contactDetailsInfo.address = checkPostNone(request,'c_address_line_1')
        if checkPostNone(request,'designation'):
            contactDetailsInfo.address = getModelColumnByColumnId(SpRoles,'id',request.POST['designation'],'role_name')
        contactDetailsInfo.address = checkPostNone(request,'gstin')
        contactDetailsInfo.save()

        if checkPostNone(request,'designation'):
            tag = SpTags.objects.filter(tag=official_detail.designation).first()
            if not tag:
                tag = SpTags()
                tag.tag = official_detail.designation
                tag.color = '#2878B5'
                tag.save()  
            contact_tag = SpContactTags()
            contact_tag.contact_id = contactDetailsInfo.id
            contact_tag.tag_id = tag.id
            contact_tag.save()
        elif '3' in request.POST.getlist('attribute_id[]'):
            tag = SpTags.objects.filter(tag='Student').first()
            if not tag:
                tag = SpTags()
                tag.tag = 'Student'
                tag.color = '#2878B5'
                tag.save()
            contact_tag = SpContactTags()
            contact_tag.contact_id = contactDetailsInfo.id
            contact_tag.tag_id = tag.id
            contact_tag.save()
        if 'tags[]' in request.POST:
                tagList = request.POST.getlist('tags[]') 
                if (tagList):
                    for id, val in enumerate(tagList):
                        role_tag = SpContactTags.objects.filter(contact_id=contactDetailsInfo.id,tag_id=tagList[id]).first()
                        if not role_tag:
                            contact_tag = SpContactTags()
                            contact_tag.contact_id = contactDetailsInfo.id
                            contact_tag.tag_id = tagList[id]
                            contact_tag.save()

        context['flag'] = True
        context['message'] = "Contact has been created successfully."
            
        return JsonResponse(context)
    else:
        context['flag'] = False
        context['message'] = "Method Not allowed"
        return JsonResponse(context)

def checkPostNone(request, value):
    if value in request.POST and request.POST[value] != "":
        return request.POST[value]
    else:
        return None


def checkAttributeValue(request,role_id,attribute_id,field_name,message):
    
    
    if not SpRoleAttrOptionalFields.objects.filter(role_id=role_id,attribute_id=attribute_id,field_name=field_name).exists():
      
        if "[]" in field_name:
            if field_name in request.POST and len(request.POST.getlist(field_name)) < 1:
                tmp = {}
                if "[]" in field_name:
                    field_name = field_name.split('[]')[0]
                    tmp['name'] = field_name
                else:
                    tmp['name'] = field_name
                tmp['message'] = message
                return tmp

            else:
                return False
        else:
            if field_name in request.POST and request.POST[field_name] == "":
                tmp = {}
                if "[]" in field_name:
                    field_name = field_name.split('[]')[0]
                    tmp['name'] = field_name
                else:
                    tmp['name'] = field_name
                tmp['message'] = message
                return tmp
            else:
                return False
    else:
        return False



@login_required
def updateContact(request):
    context = {}
    errors = []
    # print(request.POST.getlist('attribute_id[]'))
    if request.method == "POST":
        role_id = request.POST['role_id']
        #Sever-side Validation
        field_name = 'role_id'
        if field_name in request.POST and request.POST[field_name] == "":
            tmp = {}
            tmp['name'] = field_name
            tmp['message'] = "Role is Required"
            errors.append(tmp)
        #Sever-side Validation
        field_name = 'locations_list'
        if field_name in request.POST and request.POST[field_name] == "":
            tmp = {}
            tmp['name'] = field_name
            tmp['message'] = "Institutions is Required"
            errors.append(tmp)
        #Sever-side Validation
        if 'is_role_outsider' in request.POST and request.POST['is_role_outsider'] != '': 
            if request.POST['is_role_outsider'] == '1': 
                field_name = 'organisation_id'
                if field_name in request.POST and request.POST[field_name] == "":
                    tmp = {}
                    tmp['name'] = field_name
                    tmp['message'] = "Organization is Required"
                    errors.append(tmp)
        #Sever-side Validation              
        field_name = 'first_name'
        if field_name in request.POST and request.POST[field_name] == "":
            tmp = {}
            tmp['name'] = field_name
            tmp['message'] = "First Name is Required"
            errors.append(tmp)
        #Sever-side Validation
        field_name = 'last_name'
        if field_name in request.POST and request.POST[field_name] == "":
            tmp = {}
            tmp['name'] = field_name
            tmp['message'] = "Last Name is Required"
            errors.append(tmp)
        #Sever-side Validation
        field_name = 'alias_name'
        if field_name in request.POST and request.POST[field_name] == "":
            tmp = {}
            tmp['name'] = field_name
            tmp['message'] = "Alias is Required"
            errors.append(tmp)

        if field_name in request.POST and request.POST[field_name] != "":
            if SpUsers.objects.filter(alias=request.POST[field_name]).exclude(id=request.POST['user_id']).exists():
                tmp = {}
                tmp['name'] = field_name
                tmp['message'] = "Alias already exists"
                errors.append(tmp)
        #Sever-side Validation
        field_name = 'email'
        if field_name in request.POST and request.POST[field_name] == "":
            tmp = {}
            tmp['name'] = field_name
            tmp['message'] = "Email is Required"
            errors.append(tmp)
        #Sever-side Validation
        # field_name = 'contact_number[]'
        # if field_name in request.POST and len(request.POST.getlist(field_name)) > 0:
            # tmp = {}
            # field_name = field_name.split('[]')[0]
            # tmp['name'] = field_name
            # tmp['message'] = "Contact number is Required"
            # errors.append(tmp)
        #Sever-side Validation
        # field_name = 'primary_contact[]'
        # if field_name in request.POST and len(request.POST.getlist(field_name)) > 0:
            # tmp = {}
            # field_name = field_name.split('[]')[0]
            # tmp['name'] = field_name
            # tmp['message'] = "Atleast one primary contact is Required"
            # errors.append(tmp)
        
        #Sever-side Validation
        
        if bool(request.FILES.get('profile_image', False)) == True:
            
            uploaded_profile_image = request.FILES['profile_image']
            storage = FileSystemStorage('media/profileImage/')
            timestamp = int(time.time())
            profile_image_name = uploaded_profile_image.name
            temp = profile_image_name.split('.')
            profile_image_name = 'profile_'+str(timestamp)+"."+temp[(len(temp) - 1)]
            
            profile_image = storage.save(profile_image_name, uploaded_profile_image)            
            profile_image = storage.url(profile_image)
            profile_image = profile_image.split('media/')[1]
            profile_image = "media/profileImage/"+profile_image
        else:
            if request.POST['old_profile_image'] != '':
                profile_image = request.POST['old_profile_image']
            else:
                profile_image = ''

        # if 'business_type' in request.POST:
        #     field_name = 'contact_person_first_name[]'
        #     if field_name in request.POST and len(request.POST.getlist(field_name)) > 0:
        #         tmp = {}
        #         tmp['name'] = field_name
        #         tmp['message'] = "First Name is Required"
        #         errors.append(tmp)
        #     field_name = 'contact_person_last_name[]'
        #     if field_name in request.POST and len(request.POST.getlist(field_name)) > 0:
        #         tmp = {}
        #         tmp['name'] = field_name
        #         tmp['message'] = "Last Name is Required"
        #         errors.append(tmp)
        #     field_name = 'contact_person_email[]'
        #     if field_name in request.POST and len(request.POST.getlist(field_name)) > 0:
        #         tmp = {}
        #         tmp['name'] = field_name
        #         tmp['message'] = "Email is Required"
        #         errors.append(tmp)            
        #     field_name = 'contact_person_mobile[]'
        #     if field_name in request.POST and len(request.POST.getlist(field_name)) > 0:
        #         tmp = {}
        #         field_name = field_name.split('[]')[0]
        #         tmp['name'] = field_name
        #         tmp['message'] = "Contact number is Required"
        #         errors.append(tmp)            
        #     field_name = 'contact_person_designation[]'
        #     if field_name in request.POST and len(request.POST.getlist(field_name)) > 0:
        #         tmp = {}
        #         field_name = field_name.split('[]')[0]
        #         tmp['name'] = field_name
        #         tmp['message'] = "Contact person designation is Required"
        #         errors.append(tmp)
        
        #Sever-side Validation
        if '2' in request.POST.getlist('attribute_id[]'):
            attrChecker = checkAttributeValue(request,role_id,2,'father_first_name',"Father's first name is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'father_last_name',"Father's last name is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'mother_first_name', "Mother's first name is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'mother_last_name', "Mother's last name is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'spouse_name', "Spouce name is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'spouse_employer', "Spouse employer name is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'spouse_work_phone', "Spouse work phone number is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'no_of_child', "Number of child is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'gender', "gender is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'date_of_birth', "Date of birth is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'birth_place', "Birth Place is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'marital_status', "Marital status is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'blood_group', "Blood group is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'disability', "Disability is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'identification_mark', "Identification mark is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'caste_category', "Caste category is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'income_category', "Income category is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'previlege_category', "Previlege category is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'c_country', "Country is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'c_state', "State is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'c_city', "City is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'c_address_line_1', "Address line 1 is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'c_address_line_2', "Address line 2 is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'c_pincode', "Pincode is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'p_country', "Permanent country is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'p_state', "Permanent state is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'p_city', "Permanent City is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'p_address_line_1', "Permanent Address line 1 is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'p_address_line_2', "Permanent Address line 2 is required")
            if attrChecker:
                errors.append(attrChecker)
            attrChecker = checkAttributeValue(request,role_id,2,'p_pincode', "Permanent pincode is required")
            if attrChecker:
                errors.append(attrChecker)
            
            attrChecker = checkAttributeValue(request,role_id,2,'tags[]', "Tags is required")
            if attrChecker:
                errors.append(attrChecker)

        #Sever-side Validation
        if '3' in request.POST.getlist('attribute_id[]'):
            attrChecker = checkAttributeValue(request,role_id,3,'student_location', "College Name is Required")
            if attrChecker:
                errors.append(attrChecker)
            
            attrChecker = checkAttributeValue(request,role_id,3,'branch', "Branch is Required")
            if attrChecker:
                errors.append(attrChecker)
            
            attrChecker = checkAttributeValue(request,role_id,3,'registration', "Registration Number is Required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,3,'year', "Year/Semester is Required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,3,'date_of_admission', "Admission Date is Required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,3,'teacher_gaurdian_name', "Teacher's Gaurdian Name is Required")
            if attrChecker:
                errors.append(attrChecker)
            
        #Sever-side Validation
        if '4' in request.POST.getlist('attribute_id[]'):
            attrChecker = checkAttributeValue(request,role_id,4,'location',"Institution is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'department',"Department is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'designation', "Designation is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'paygrade', "Pay grade is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'employment_term', "Employment term is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'additional_responsibility[]', "Additional responsibility is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'working_hour', "Working hour is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'date_of_joining', "Date of joining is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'previous_employer', "Previous employer is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,4,'experience', "Experience is required")
            if attrChecker:
                errors.append(attrChecker)
            
            attrChecker = checkAttributeValue(request,role_id,4,'login_id', "Login Id is required")
            if attrChecker:
                errors.append(attrChecker)
            
            attrChecker = checkAttributeValue(request,role_id,4,'password', "Password is required")
            if attrChecker:
                errors.append(attrChecker)
            
            
        #Sever-side Validation
        if '5' in request.POST.getlist('attribute_id[]'):
            # attrChecker = checkAttributeValue(request,role_id,5,'is_health_insurance',"Health insurance is required")
            # if attrChecker:
            #     errors.append(attrChecker)

            # attrChecker = checkAttributeValue(request,role_id,5,'is_salary_saving_scheme',"Salary saving scheme is required")
            # if attrChecker:
            #     errors.append(attrChecker)

            # attrChecker = checkAttributeValue(request,role_id,5,'is_wage_tax_applicable', "Wage tax applicable is required")
            # if attrChecker:
            #     errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,5,'gstin', "GSTIN is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,5,'salary_addition[]', "Salary addition is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,5,'salary_deduction[]', "Salary deduction is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,5,'bank[]', "Bank name is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,5,'ifsc_code[]', "IFSC code is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,5,'bank_account_no[]', "Bank account number is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,5,'account_holder_name[]', "Account holder name is required")
            if attrChecker:
                errors.append(attrChecker)
        #Sever-side Validation
        if '6' in request.POST.getlist('attribute_id[]'):
            attrChecker = checkAttributeValue(request,role_id,6,'vehicle_type',"Vehicle type is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,6,'fuel_type',"Fuel type is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,6,'vehicle_no', "Vehicle Number is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,6,'chessis_no', "Chessis Number is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,6,'engine_no', "Engine Number is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,6,'dl_no', "Driving License Number is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,6,'dl_expiry', "Driving License Expiry is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,6,'seating_capacity_no', "Seating Capacity Number is required")
            if attrChecker:
                errors.append(attrChecker)
        #Sever-side Validation
        if '7' in request.POST.getlist('attribute_id[]'):
            attrChecker = checkAttributeValue(request,role_id,7,'finger_1',"Finger Print is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,7,'finger_2',"Finger Print is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,7,'finger_3', "Finger Print is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,7,'finger_4', "Finger Print is required")
            if attrChecker:
                errors.append(attrChecker)

            attrChecker = checkAttributeValue(request,role_id,7,'finger_5', "Finger Print is required")
            if attrChecker:
                errors.append(attrChecker)

                        
        
        if len(errors)>0:
            context['flag'] = False
            context['errors'] = errors
            return JsonResponse(context)
        user_data = SpUsers.objects.get(id=request.POST['user_id'])

        user_data.role_id = role_id 
        user_data.role_name = getModelColumnByColumnId(SpRoles,'id',role_id,'role_name')
        user_data.organization_id = request.POST['locations_list']
        user_data.organization_name = getModelColumnByColumnId(SpOrganizations,'id',request.POST['locations_list'],'organization_name')
        user_data.salutation = request.POST['salutation_id']
        user_data.first_name = request.POST['first_name']
        user_data.profile_image = profile_image
        # if (request.POST['middle_name']):
        user_data.middle_name = checkPostNone(request,'middle_name')
        user_data.last_name = request.POST['last_name']
        if (request.POST['email']):
            user_data.official_email = request.POST['email']
        if (request.POST['alias_name']):
            user_data.alias = request.POST['alias_name']
        

        user_data.created_by = request.user.id
        user_data.save()
        
        SpUserContacts.objects.filter(user_id=request.POST['user_id']).delete()

        contact_numbers  = request.POST.getlist('contact_number[]') 
        contact_types  = request.POST.getlist('contact_type[]') 
        primary_contacts  = request.POST.getlist('primary_contact[]') 
        i=0
        for id, val in enumerate(contact_numbers):
            contact_data = SpUserContacts()
            contact_data.user_id = user_data.id 
            contact_data.contact_type_id = contact_types[id]
            contact_data.contact_type = getModelColumnByColumnId(SpContactTypes,'id',contact_types[id],'contact_type')
            contact_data.contact_number = contact_numbers[id]
            contact_data.is_primary = primary_contacts[id]
            contact_data.save()
            
           
        if request.POST['business_type']:
            contact_first_names  = request.POST.getlist('contact_person_first_name[]') 
            contact_middle_names  = request.POST.getlist('contact_person_middle_name[]') 
            contact_last_names  = request.POST.getlist('contact_person_last_name[]') 
            contact_person_numbers  = request.POST.getlist('contact_person_mobile[]') 
            contact_emails  = request.POST.getlist('contact_person_email[]') 
            contact_designations  = request.POST.getlist('contact_person_designation[]') 
            contactList = []
            for id, val in enumerate(contact_first_names):
                tmp = {}
                tmp['contact_first_name'] = contact_first_names[id]
                tmp['contact_middle_name'] = contact_middle_names[id]
                tmp['contact_last_name'] = contact_last_names[id]
                tmp['contact_person_number'] = contact_person_numbers[id]
                tmp['contact_email'] = contact_emails[id]
                tmp['contact_designation'] = contact_designations[id]
                contactList.append(tmp)

            

            business_data = SpUserBusinessDetails.objects.get(user_id=request.POST['user_id'])
            if business_data:
                SpUserBusinessDetails.objects.filter(user_id=request.POST['user_id']).delete()

            business_data.user_id = request.POST['user_id'] 
            business_data.business_type_id = request.POST['business_type']
            business_data.business_type = getModelColumnByColumnId(SpBusinessTypes,'id',request.POST['business_type'],'business_type')
            business_data.contact_persons = json.dumps(contactList)
            business_data.save()


            # Create Contact person as Contacts
            if contact_first_names:
                for id, val in enumerate(contact_first_names):
                    contactDetails = SpContacts()
                    contactDetails.type = 1  
                    contactDetails.first_name = contact_first_names[id]
                    contactDetails.middle_name = contact_middle_names[id]
                    contactDetails.last_name = contact_last_names[id]
                    contactDetails.email = contact_emails[id]
                    contactDetails.designation = contact_designations[id]
                    contactDetails.phone = contact_person_numbers[id]
                    contactDetails.created_by = request.user.id
                    contactDetails.save()

                    if contact_designations[id]:
                        tag = SpTags.objects.filter(tag=contact_designations[id]).first()
                        if not tag:
                            tag = SpTags()
                            tag.tag = contact_designations[id]
                            tag.color = '#2878B5'
                            tag.save()
                        contact_tag = SpContactTags()
                        contact_tag.contact_id = contactDetails.id
                        contact_tag.tag_id = tag.id
                        contact_tag.save()

                    if 'tags[]' in request.POST:
                        tagList = request.POST.getlist('tags[]') 
                        if tagList:
                            for id, val in enumerate(tagList):
                                contact_tag = SpContactTags.objects.filter(contact_id=contactDetails.id,tag_id=tagList[id]).first()
                                if not contact_tag:
                                    contact_tag = SpContactTags()
                                    contact_tag.contact_id = contactDetails.id
                                    contact_tag.tag_id = tagList[id]
                                    contact_tag.save()
        
        # personal details
        if '2' in request.POST.getlist('attribute_id[]'):

            personal_detail = SpUserPersonalDetails.objects.get(user_id=request.POST['user_id'])
            personal_detail.user_id = request.POST['user_id']
            personal_detail.father_first_name = request.POST['father_first_name']                    
            personal_detail.father_last_name = request.POST['father_last_name']
            personal_detail.mother_first_name = request.POST['mother_first_name']
            personal_detail.mother_last_name = request.POST['mother_last_name']
            personal_detail.spouse_name = request.POST['spouse_name']
            personal_detail.spouse_employer = request.POST['spouse_employer']
            personal_detail.spouse_work_phone = request.POST['spouse_work_phone']
            if request.POST['no_of_child']:
                personal_detail.no_of_children = request.POST['no_of_child']
            personal_detail.gender = request.POST['gender']
            personal_detail.date_of_birth = datetime.strptime(request.POST['date_of_birth'], "%d/%m/%Y").strftime('%Y-%m-%d') 
            personal_detail.place_of_birth = request.POST['birth_place']
            personal_detail.martial_status = request.POST['marital_status']
            personal_detail.blood_group = request.POST['blood_group']
            personal_detail.disability = request.POST['disability']
            personal_detail.identification_mark = request.POST['identification_mark']
            personal_detail.caste_category = request.POST['caste_category']
            if request.POST['income_category']:
                personal_detail.income_category_id = request.POST['income_category']
                personal_detail.income_category = getModelColumnByColumnId(SpIncomeCategories,'id',request.POST['income_category'],'income_category') 
            if request.POST['previlege_category']:
                personal_detail.previlege_category_id = request.POST['previlege_category']
                personal_detail.previlege_category = getModelColumnByColumnId(SpPrevilegeCategories,'id',request.POST['previlege_category'],'previlege_category') 

            personal_detail.c_country = checkPostNone(request,'c_country')
            personal_detail.c_state = checkPostNone(request,'c_state')
            personal_detail.c_city = checkPostNone(request,'c_city')
            personal_detail.c_address_line_1 = checkPostNone(request,'c_address_line_1')
            personal_detail.c_address_line_2 = checkPostNone(request,'c_address_line_2')
            personal_detail.c_pincode = checkPostNone(request,'c_pincode')

            if 'both_address_same' in request.POST:
                if request.POST['both_address_same']:
                    personal_detail.p_country = checkPostNone(request,'c_country')
                    personal_detail.p_state = checkPostNone(request,'c_state')
                    personal_detail.p_city = checkPostNone(request,'c_city')
                    personal_detail.p_address_line_1 = checkPostNone(request,'c_address_line_1')
                    personal_detail.p_address_line_2 = checkPostNone(request,'c_address_line_2')
                    personal_detail.p_pincode = checkPostNone(request,'c_pincode')
            else:
                personal_detail.p_country = checkPostNone(request,'p_country')
                personal_detail.p_state = checkPostNone(request,'p_state')
                personal_detail.p_city = checkPostNone(request,'p_city')
                personal_detail.p_address_line_1 = checkPostNone(request,'p_address_line_1')
                personal_detail.p_address_line_2 = checkPostNone(request,'p_address_line_2')
                personal_detail.p_pincode = checkPostNone(request,'p_pincode')
            personal_detail.save()

            SpUserTags.objects.filter(user_id=request.POST['user_id']).delete()
            if 'tags[]' in request.POST:
                tagList = request.POST.getlist('tags[]') 
                if tagList:
                    for id, val in enumerate(tagList):
                        user_tag = SpUserTags()
                        user_tag.user_id = user_data.id
                        user_tag.tag_id = tagList[id]
                        user_tag.save()
        # personal details

        # Academic details
        if '3' in request.POST.getlist('attribute_id[]'):
            academic_detail = SpUserAcademicDetails.objects.get(user_id=request.POST['user_id'])
            academic_detail.user_id = request.POST['user_id']
            if checkPostNone(request,'student_location'):
                academic_detail.location_id = request.POST['student_location']

            if checkPostNone(request,'branch'):
                academic_detail.branch_id = request.POST['branch']

            if checkPostNone(request,'year'):
                yearList = request.POST['year'].split("_")
                if 'year' in yearList:
                    academic_detail.year_id = request.POST['year']
                elif 'sem' in yearList:
                    academic_detail.semester_id = request.POST['year']

            if checkPostNone(request,'date_of_admission'):
                academic_detail.date_of_admission = datetime.strptime(request.POST['date_of_admission'], "%d/%m/%Y").strftime('%Y-%m-%d')

            if checkPostNone(request,'registration'):
                academic_detail.registration_no = request.POST['registration']

            if checkPostNone(request,'teacher_gaurdian_name'):
                academic_detail.teacher_guardian_id = request.POST['teacher_gaurdian_name']
            academic_detail.save() 

            tag = SpTags.objects.filter(tag='Student').first()
            if not tag:
                tag = SpTags()
                tag.tag = 'Student'
                tag.color = '#2878B5'
                tag.save()
            users_tag = SpUserTags()
            users_tag.user_id = user_data.id
            users_tag.tag_id = tag.id
            users_tag.save()
        # Academic details

       

        # Official details
        if '4' in request.POST.getlist('attribute_id[]'):
            official_detail = SpUserOfficialDetails.objects.filter(user_id=request.POST['user_id']).first()
            if not official_detail:
                official_detail = SpUserOfficialDetails()
            official_detail.user_id = user_data.id
            if request.POST['location']:
                official_detail.location_id = request.POST['location']
                official_detail.location = getModelColumnByColumnId(SpOrganizations,'id',request.POST['location'],'organization_name')

            if checkPostNone(request,'department'):
                official_detail.department_id = request.POST['department']
                official_detail.department = getModelColumnByColumnId(SpDepartments,'id',request.POST['department'],'department_name')

            if checkPostNone(request,'designation'):
                official_detail.designation_id = request.POST['designation']
                official_detail.designation = getModelColumnByColumnId(SpRoles,'id',request.POST['designation'],'role_name')

            if checkPostNone(request,'paygrade'):
                official_detail.pay_grade = request.POST['paygrade']

            if checkPostNone(request,'employment_term'):
                official_detail.employment_term = request.POST['employment_term']

            if request.POST.getlist('additional_responsibility[]'):
                separator = ','
                additional_responsibilities = separator.join(request.POST.getlist('additional_responsibility[]'))
                official_detail.additional_responsibilities = additional_responsibilities
            
            if checkPostNone(request,'working_hour'):
                official_detail.working_hour = request.POST['working_hour']

            if checkPostNone(request,'date_of_joining'):
                official_detail.date_of_joining = datetime.strptime(request.POST['date_of_joining'], "%d/%m/%Y").strftime('%Y-%m-%d')

            if checkPostNone(request,'previous_employer'):
                official_detail.previous_employer = request.POST['previous_employer']

            if checkPostNone(request,'experience'):
                official_detail.years_of_experience = request.POST['experience']
            official_detail.save()
            

            user_data.emp_sap_id = request.POST['login_id']
            user_data.plain_password = request.POST['password']
            user_data.password = make_password(str(request.POST['password']))
            user_data.save()    


            if request.POST['location']:
                tag_name = getModelColumnById(SpRoles,request.POST['designation'],'role_name')
                if not SpTags.objects.filter(tag=tag_name).exists():
                    tag = SpTags()
                    tag.tag = tag_name
                    tag.color = '#2878B5'
                    tag.save()

                    user_tag = SpUserTags()
                    user_tag.user_id = user_data.id
                    user_tag.tag_id = tag.id
                    user_tag.save()

            
        # Official details

        # Financial details
        if '5' in request.POST.getlist('attribute_id[]'):
            financial_detail = SpUserFinancialDetails.objects.filter(user_id=request.POST['user_id']).first()
            if not financial_detail:
                financial_detail = SpUserFinancialDetails()
            financial_detail.user_id = user_data.id      

            if request.POST['is_health_insurance']:
                financial_detail.is_health_insurance = request.POST['is_health_insurance']    
                financial_detail.health_insurance = request.POST['health_insurence']  
            if request.POST['is_salary_saving_scheme']:
                financial_detail.salary_saving_scheme = request.POST['salary_saving_scheme'] 
            if request.POST['is_wage_tax_applicable']:
                financial_detail.wage_tax = request.POST['wage_tax'] 
            if request.POST['gstin']:
                financial_detail.gstin = request.POST['gstin']    
            if request.POST.getlist('salary_addition[]'):
                separator = ','
                financial_detail.salary_addition = separator.join(request.POST.getlist('salary_addition[]'))
            if request.POST.getlist('salary_deduction[]'):
                separator = ','
                financial_detail.salary_deduction = separator.join(request.POST.getlist('salary_deduction[]')) 
            financial_detail.save()
            SpUserBankDetails.objects.filter(user_id=request.POST['user_id']).delete()
            if request.POST.getlist('bank[]'):
                bankList = request.POST.getlist('bank[]')
                ifsc_code  = request.POST.getlist('ifsc_code[]') 
                bank_account_no  = request.POST.getlist('bank_account_no[]') 
                account_holder_name  = request.POST.getlist('account_holder_name[]') 
                for id, val in enumerate(bankList):
                    bank_detail = SpUserBankDetails()
                    bank_detail.user_id = user_data.id
                    if bankList[id]:
                        bank_detail.bank_id = bankList[id]
                        bank_detail.bank_name = getModelColumnByColumnId(SpBanks,'id',bankList[id],'bank_name')
                    bank_detail.ifsc_code = ifsc_code[id]
                    bank_detail.bank_account_no = bank_account_no[id]
                    bank_detail.account_holder_name = account_holder_name[id]
                    bank_detail.save()
        # Financial details


        # Vehicle details
        if '6' in request.POST.getlist('attribute_id[]'):
            vehicle_detail = SpVehicles.objects.filter(user_id=request.POST['user_id']).first()
            if not vehicle_detail:
                vehicle_detail = SpVehicles()
            vehicle_detail.user_id = user_data.id     
            if request.POST['vehicle_type']:
                vehicle_detail.vehicle_type = request.POST['vehicle_type']
            vehicle_detail.fuel_type = request.POST['fuel_type']
            vehicle_detail.registration_number = request.POST['vehicle_no']
            vehicle_detail.chassis_no = request.POST['chessis_no']
            vehicle_detail.engine_no = request.POST['engine_no']
            vehicle_detail.driver_id = request.POST['dl_no']
            if request.POST['dl_expiry']:
                vehicle_detail.dl_expiry = datetime.strptime(request.POST['dl_expiry'], "%d/%m/%Y").strftime('%Y-%m-%d')
            if request.POST['seating_capacity_no']:
                vehicle_detail.seating_capacity_standard = request.POST['seating_capacity_no']
            vehicle_detail.save()
        # Vehicle details

        # Biometrics details
        if '7' in request.POST.getlist('attribute_id[]'):

            biometric_detail = SpUserBiometricDetails.objects.get(user_id=request.POST['user_id'])
            if not biometric_detail:
                biometric_detail = SpUserBiometricDetails()
            biometric_detail.user_id = request.POST['user_id']
            biometric_detail.finger_1 = checkPostNone(request,'finger_1')
            biometric_detail.finger_2 = checkPostNone(request,'finger_2')
            biometric_detail.finger_3 = checkPostNone(request,'finger_3')
            biometric_detail.finger_4 = checkPostNone(request,'finger_4')
            biometric_detail.finger_5 = checkPostNone(request,'finger_5')
            biometric_detail.save()
        # Biometrics details

        # Documents details
        required_docs = SpRequiredDocuments.objects.all()
        SpUserDocuments.objects.filter(user_id=request.POST['user_id']).delete()
        for required_doc in required_docs:
            var_name  = slugify(required_doc.document)
            if var_name in request.POST and request.POST[var_name] != "":
                document = SpUserDocuments()
                document.user_id = request.POST['user_id']
                document.document_id  = required_doc.id
                document.document_name  = required_doc.document
                document.ducument_number  = request.POST[var_name]
                document.save()
        # Documents details

        contactDetailsInfo = SpContacts()
        contactDetailsInfo.type = 1  
        contactDetailsInfo.first_name = request.POST['first_name']
        contactDetailsInfo.middle_name = request.POST['middle_name']
        contactDetailsInfo.last_name = request.POST['last_name']
        contactDetailsInfo.email = request.POST['email']
        if request.POST.getlist('contact_number[]'):
            contact_number = request.POST.getlist('contact_number[]')
            primary_contact = request.POST.getlist('primary_contact[]')
            for id, val in enumerate(contact_number):
                if primary_contact[id]==1:
                    contactDetailsInfo.phone = contact_number[id]

        contactDetailsInfo.state = checkPostNone(request,'c_state')
        contactDetailsInfo.city = checkPostNone(request,'c_city')
        contactDetailsInfo.address = checkPostNone(request,'c_address_line_1')
        if checkPostNone(request,'designation'):
            contactDetailsInfo.address = getModelColumnByColumnId(SpRoles,'id',request.POST['designation'],'role_name')
        contactDetailsInfo.address = checkPostNone(request,'gstin')
        contactDetailsInfo.save()

        if checkPostNone(request,'designation'):
            tag = SpTags.objects.filter(tag=official_detail.designation).first()
            if not tag:
                tag = SpTags()
                tag.tag = official_detail.designation
                tag.color = '#2878B5'
                tag.save()  
            contact_tag = SpContactTags()
            contact_tag.contact_id = contactDetailsInfo.id
            contact_tag.tag_id = tag.id
            contact_tag.save()
        elif '3' in request.POST.getlist('attribute_id[]'):
            tag = SpTags.objects.filter(tag='Student').first()
            if not tag:
                tag = SpTags()
                tag.tag = 'Student'
                tag.color = '#2878B5'
                tag.save()
            contact_tag = SpContactTags()
            contact_tag.contact_id = contactDetailsInfo.id
            contact_tag.tag_id = tag.id
            contact_tag.save()
        if 'tags[]' in request.POST:
                tagList = request.POST.getlist('tags[]') 
                if (tagList):
                    for id, val in enumerate(tagList):
                        role_tag = SpContactTags.objects.filter(contact_id=contactDetailsInfo.id,tag_id=tagList[id]).first()
                        if not role_tag:
                            contact_tag = SpContactTags()
                            contact_tag.contact_id = contactDetailsInfo.id
                            contact_tag.tag_id = tagList[id]
                            contact_tag.save()

        context['flag'] = True
        context['message'] = "Contact has been created successfully."
            
        return JsonResponse(context)
    else:
        context['flag'] = False
        context['message'] = "Method Not allowed"
        return JsonResponse(context)

def createStudentCard(request):
    students = TblStudents.objects.all()
    for student in students:
        user_data = SpUsers()
        if student.college_id == 1:
            role_id = 2 
        if student.college_id == 2:
            role_id = 4 
        if student.college_id == 3:
            role_id = 6 

        user_data.role_id = 6

        user_data.role_name = getModelColumnByColumnId(SpRoles,'id',role_id,'role_name')
        user_data.organization_id = student.college_id
        user_data.organization_name = getModelColumnByColumnId(SpOrganizations,'id',student.college_id,'organization_name')
        user_data.salutation = 'Mr.'
        user_data.first_name = student.first_name
        if student.middle_name is not None:
            user_data.middle_name =  student.middle_name
        else:
            user_data.middle_name = ''

        if student.last_name is not None:
            user_data.last_name = student.last_name
        user_data.profile_image = student.profile_image
        user_data.official_email = slugify(str(student.first_name)+'-'+str(student.last_name))+str(student.id)+'@gmail.com'
        user_data.created_by = request.user.id

        if student.primary_contact_no is not None:
            user_data.primary_contact_no = student.primary_contact_no

        user_data.save()
        
        if student.primary_contact_no is not None:
            contact_data = SpUserContacts()
            contact_data.user_id = user_data.id 
            contact_data.contact_type_id = 1
            contact_data.contact_type = getModelColumnByColumnId(SpContactTypes,'id',1,'contact_type')
            contact_data.contact_number = student.primary_contact_no
            contact_data.is_primary = 1
            contact_data.save()
                    

        personal_detail = SpUserPersonalDetails()
        personal_detail.user_id = user_data.id
        if student.father_name is not None:
            personal_detail.father_first_name =  student.father_name                  
        
        if student.father_name is not None:
            personal_detail.mother_first_name =  student.mother_name                   


        personal_detail.save()
        # personal details

        # Academic details
        academic_detail = SpUserAcademicDetails()
        academic_detail.user_id = user_data.id
        academic_detail.location_id = student.college_id
        academic_detail.branch_id = student.branch_id

        yearList = student.semester_id.split("_")
        if 'year' in yearList:
            academic_detail.year_id = student.semester_id.split("_")[1]
        elif 'sem' in yearList:
            academic_detail.semester_id = student.semester_id.split("_")[1]

        academic_detail.registration_no = student.reg_no
        academic_detail.save() 

        tag = SpTags.objects.filter(tag='Student').first()
        if not tag:
            tag = SpTags()
            tag.tag = 'Student'
            tag.color = '#2878B5'
            tag.save()
        users_tag = SpUserTags()
        users_tag.user_id = user_data.id
        users_tag.tag_id = tag.id
        users_tag.save()
        # Academic details

       

        # Biometrics details
        if int(student.is_registered) == 1:
            biometric_detail = SpUserBiometricDetails()
            biometric_detail.user_id = user_data.id 
            biometric_detail.finger_1 = student.finger_iso_1
            biometric_detail.finger_2 = student.finger_iso_2
            biometric_detail.finger_3 = None
            biometric_detail.finger_4 = None
            biometric_detail.finger_5 = None
            biometric_detail.save()
        # Biometrics details

        # Documents details
        document = SpUserDocuments()
        document.user_id = user_data.id
        document.document_id  = 1
        document.document_name  = getModelColumnById(SpRequiredDocuments,1,'document')
        document.ducument_number  = student.aadhaar_no
        document.save()
        # Documents details

        contactDetailsInfo = SpContacts()
        contactDetailsInfo.type = 1  
        contactDetailsInfo.first_name = student.first_name
        if student.middle_name is not None:
            contactDetailsInfo.middle_name = student.middle_name
        if student.last_name is not None:
            contactDetailsInfo.last_name = student.last_name

        contactDetailsInfo.email = slugify(str(student.first_name)+'-'+str(student.last_name))+str(student.id)+'@gmail.com'
        contactDetailsInfo.phone = student.primary_contact_no

        
        contactDetailsInfo.save()
        tag = SpTags.objects.filter(tag='Student').first()
        if not tag:
            tag = SpTags()
            tag.tag = 'Student'
            tag.color = '#2878B5'
            tag.save()
        contact_tag = SpContactTags()
        contact_tag.contact_id = contactDetailsInfo.id
        contact_tag.tag_id = tag.id
        contact_tag.save()
        
    
    return HttpResponse('created')

