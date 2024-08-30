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
from ...models import *
from django.db.models import Q
from utils import *
from datetime import datetime,date
from datetime import timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from django.forms.models import model_to_dict
import time
import os, shutil, errno
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
    context['page_title'] = "Master management"
    context['leave_types'] = SpLeaveTypes.objects.all()
    template = 'master/masters.html'
    return render(request, template, context)


@login_required
def ajaxPayBandList(request):
    context = {}
    context['pay_bands'] = SpPayBands.objects.all()
    template = 'master/paybands/ajax-pay-band-list.html'
    return render(request, template, context)

@login_required
def addPayBand(request):
    if request.method == "POST":
        response = {}
        if SpPayBands.objects.filter(pay_band=clean_data(request.POST['pay_band'])).exists() :
            response['flag'] = False
            response['message'] = "Pay band already exists."
        else:
            pay_band = SpPayBands()
            pay_band.pay_band = clean_data(request.POST['pay_band'])
            pay_band.pay_band_code = clean_data(request.POST['pay_band_code'])
            pay_band.status = 1
            pay_band.save()
            if pay_band.id :
                response['flag'] = True
                response['message'] = "Record has been saved successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        template = 'master/paybands/add-pay-band.html'
        return render(request, template, context)

@login_required
def editPayBand(request,pay_band_id):
    if request.method == "POST":
        response = {}
        pay_band_id = request.POST['pay_band_id']
        if SpPayBands.objects.filter(pay_band=clean_data(request.POST['pay_band'])).exclude(id=pay_band_id).exists() :
            response['flag'] = False
            response['message'] = "Pay band already exists."
        else:
            pay_band = SpPayBands.objects.get(id=pay_band_id)
            pay_band.pay_band = clean_data(request.POST['pay_band'])
            pay_band.pay_band_code = clean_data(request.POST['pay_band_code'])
            pay_band.save()
            if pay_band.id :
                response['flag'] = True
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        context['pay_band'] = SpPayBands.objects.get(pk=pay_band_id)
        template = 'master/paybands/edit-pay-band.html'
        return render(request, template, context)

@login_required
def updatePayBandStatus(request,pay_band_id):
    context = {}
    if SpPayBands.objects.filter(id=pay_band_id).exists():
        pay_band = SpPayBands.objects.get(id=pay_band_id)
        if int(pay_band.status) == 1:
            pay_band.status = 0
            pay_band.save()
        else:
            pay_band.status = 1
            pay_band.save()

        context['flag'] = True
        context['message'] = "Record updated successfully."
    else:
        context['flag'] = False
        context['message'] = "Record not found."
    return JsonResponse(context)


@login_required
def ajaxAttendanceGroupList(request):
    context = {}
    context['attendance_groups'] = TblClWorkingShifts.objects.all()
    template = 'master/attendance-group/ajax-attendance-group-list.html'
    return render(request, template, context)

@login_required
def addAttendanceGroup(request):
    if request.method == "POST":
        response = {}
        # if SpAttendanceGroups.objects.filter(attendance_group=clean_data(request.POST['attendance_group_data'])).exists() :
        #     response['flag'] = False
        #     response['message'] = "Attendance group already exists."
        # else:
        #     attendance_group = SpAttendanceGroups()
        #     attendance_group.attendance_group = clean_data(request.POST['attendance_group_data'])
        #     attendance_group.start_time = clean_data(request.POST['start_time_data'])
        #     attendance_group.end_time = clean_data(request.POST['end_time_data'])
        #     attendance_group.status = 1
        #     attendance_group.save()
        #     if attendance_group.id :
        #         response['flag'] = True
        #         response['message'] = "Record has been saved successfully."
        #     else:
        #         response['flag'] = False
        #         response['message'] = "Failed to save record."
        
        attendance_group = TblClWorkingShifts()
        attendance_group.working_shift = clean_data(request.POST['attendance_group_data'])
        attendance_group.start_timing = clean_data(request.POST['start_time_data'])
        attendance_group.end_timing = clean_data(request.POST['end_time_data'])
        attendance_group.status = 1
        attendance_group.save()
        if attendance_group.id :
            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        else:
            response['flag'] = False
            response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        template = 'master/attendance-group/add-attendance-group.html'
        return render(request, template, context)

@login_required
def editAttendanceGroup(request,attendance_group_id):
    if request.method == "POST":
        response = {}
        attendance_group_id = request.POST['attendance_group_id']
        # if SpAttendanceGroups.objects.filter(attendance_group=clean_data(request.POST['attendance_group_data'])).exclude(id=attendance_group_id).exists() :
        #     response['flag'] = False
        #     response['message'] = "Attendance group already exists."
        # else:
        #     attendance_group = SpAttendanceGroups.objects.get(id=attendance_group_id)
        #     attendance_group.attendance_group = clean_data(request.POST['attendance_group_data'])
        #     attendance_group.start_time = clean_data(request.POST['start_time_data'])
        #     attendance_group.end_time = clean_data(request.POST['end_time_data'])
        #     attendance_group.save()
        #     if attendance_group.id :
        #         response['flag'] = True
        #         response['message'] = "Record has been updated successfully."
        #     else:
        #         response['flag'] = False
        #         response['message'] = "Failed to save record."
                
        attendance_group = TblClWorkingShifts.objects.get(id=attendance_group_id)
        attendance_group.working_shift = clean_data(request.POST['attendance_group_data'])
        attendance_group.start_timing = clean_data(request.POST['start_time_data'])
        attendance_group.end_timing = clean_data(request.POST['end_time_data'])
        attendance_group.save()
        if attendance_group.id :
            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        else:
            response['flag'] = False
            response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        context['attendance_group'] = TblClWorkingShifts.objects.get(pk=attendance_group_id)
        template = 'master/attendance-group/edit-attendance-group.html'
        return render(request, template, context)

@login_required
def updateAttendanceGroupStatus(request,attendance_group_id):
    context = {}
    if TblClWorkingShifts.objects.filter(id=attendance_group_id).exists():
        attendance_group = TblClWorkingShifts.objects.get(id=attendance_group_id)
        if int(attendance_group.status) == 1:
            attendance_group.status = 0
            attendance_group.save()
        else:
            attendance_group.status = 1
            attendance_group.save()

        context['flag'] = True
        context['message'] = "Record updated successfully."
    else:
        context['flag'] = False
        context['message'] = "Record not found."
    return JsonResponse(context)


@login_required
def ajaxSalaryAdditionTypeList(request):
    context = {}
    context['salary_addition_types'] = SpSalaryAdditionTypes.objects.all()
    template = 'master/salary/ajax-salary-addition-type-list.html'
    return render(request, template, context)

@login_required
def addSalaryAdditionType(request):
    if request.method == "POST":
        response = {}
        if SpSalaryAdditionTypes.objects.filter(addition=clean_data(request.POST['addition'])).exists() :
            response['flag'] = False
            response['message'] = "Addition Type already exists."
        else:
            salary_addition_type = SpSalaryAdditionTypes()
            salary_addition_type.addition = clean_data(request.POST['addition'])
            salary_addition_type.addition_basis = clean_data(request.POST['addition_basis'])
            salary_addition_type.addition_amount = clean_data(request.POST['addition_amount'])
            if 'addition_percent_on' in request.POST and request.POST['addition_basis'] != "":
                salary_addition_type.addition_percent_on = clean_data(request.POST['addition_percent_on'])
            salary_addition_type.addition_limit = clean_data(request.POST['addition_limit'])
            salary_addition_type.addition_upper_limit = clean_data(request.POST['addition_upper_limit'])
            salary_addition_type.status = 1
            salary_addition_type.save()
            if salary_addition_type.id :
                response['flag'] = True
                response['message'] = "Record has been saved successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        template = 'master/salary/add-salary-addition-type.html'
        return render(request, template, context)

@login_required
def editSalaryAdditionType(request,salary_addition_type_id):
    if request.method == "POST":
        response = {}
        salary_addition_type_id = request.POST['salary_addition_type_id']
        if SpSalaryAdditionTypes.objects.filter(addition=clean_data(request.POST['addition'])).exclude(id=salary_addition_type_id).exists() :
            response['flag'] = False
            response['message'] = "Addition Type already exists."
        else:
            salary_addition_type = SpSalaryAdditionTypes.objects.get(id=salary_addition_type_id)
            salary_addition_type.addition = clean_data(request.POST['addition'])
            salary_addition_type.addition_basis = clean_data(request.POST['addition_basis'])
            salary_addition_type.addition_amount = clean_data(request.POST['addition_amount'])
            if 'addition_percent_on' in request.POST and request.POST['addition_basis'] != "":
                salary_addition_type.addition_percent_on = clean_data(request.POST['addition_percent_on'])
            salary_addition_type.addition_limit = clean_data(request.POST['addition_limit'])
            salary_addition_type.addition_upper_limit = clean_data(request.POST['addition_upper_limit'])
            salary_addition_type.save()
            if salary_addition_type.id :
                response['flag'] = True
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        context['salary_addition_type'] = SpSalaryAdditionTypes.objects.get(pk=salary_addition_type_id)
        template = 'master/salary/edit-salary-addition-type.html'
        return render(request, template, context)

@login_required
def updateSalaryAdditionTypeStatus(request,salary_addition_type_id):
    context = {}
    if SpSalaryAdditionTypes.objects.filter(id=salary_addition_type_id).exists():
        salary_addition_type = SpSalaryAdditionTypes.objects.get(id=salary_addition_type_id)
        if int(salary_addition_type.status) == 1:
            salary_addition_type.status = 0
            salary_addition_type.save()
        else:
            salary_addition_type.status = 1
            salary_addition_type.save()

        context['flag'] = True
        context['message'] = "Record updated successfully."
    else:
        context['flag'] = False
        context['message'] = "Record not found."
    return JsonResponse(context)

@login_required
def ajaxSalaryDeductionTypeList(request):
    context = {}
    context['salary_deduction_types'] = SpSalaryDeductionTypes.objects.all()
    template = 'master/salary/ajax-salary-deduction-type-list.html'
    return render(request, template, context)

@login_required
def addSalaryDeductionType(request):
    if request.method == "POST":
        response = {}
        if SpSalaryDeductionTypes.objects.filter(deduction=clean_data(request.POST['deduction'])).exists() :
            response['flag'] = False
            response['message'] = "Deduction Type already exists."
        else:
            salary_deduction_type = SpSalaryDeductionTypes()
            salary_deduction_type.deduction = clean_data(request.POST['deduction'])
            salary_deduction_type.deduction_basis = clean_data(request.POST['deduction_basis'])
            salary_deduction_type.deduction_amount = clean_data(request.POST['deduction_amount'])
            if 'deduction_percent_on' in request.POST and request.POST['deduction_basis'] != "":
                salary_deduction_type.deduction_percent_on = clean_data(request.POST['deduction_percent_on'])
            salary_deduction_type.deduction_limit = clean_data(request.POST['deduction_limit'])
            salary_deduction_type.deduction_upper_limit = clean_data(request.POST['deduction_upper_limit'])
            salary_deduction_type.status = 1
            salary_deduction_type.save()
            if salary_deduction_type.id :
                response['flag'] = True
                response['message'] = "Record has been saved successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        template = 'master/salary/add-salary-deduction-type.html'
        return render(request, template, context)

@login_required
def editSalaryDeductionType(request,salary_deduction_type_id):
    if request.method == "POST":
        response = {}
        salary_deduction_type_id = request.POST['salary_deduction_type_id']
        if SpSalaryDeductionTypes.objects.filter(deduction=clean_data(request.POST['deduction'])).exclude(id=salary_deduction_type_id).exists() :
            response['flag'] = False
            response['message'] = "Deduction Type already exists."
        else:
            salary_deduction_type = SpSalaryDeductionTypes.objects.get(id=salary_deduction_type_id)
            salary_deduction_type.deduction = clean_data(request.POST['deduction'])
            salary_deduction_type.deduction_basis = clean_data(request.POST['deduction_basis'])
            salary_deduction_type.deduction_amount = clean_data(request.POST['deduction_amount'])
            if 'deduction_percent_on' in request.POST and request.POST['deduction_basis'] != "":
                salary_deduction_type.deduction_percent_on = clean_data(request.POST['deduction_percent_on'])
            salary_deduction_type.deduction_limit = clean_data(request.POST['deduction_limit'])
            salary_deduction_type.deduction_upper_limit = clean_data(request.POST['deduction_upper_limit'])
            salary_deduction_type.save()
            if salary_deduction_type.id :
                response['flag'] = True
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        context['salary_deduction_type'] = SpSalaryDeductionTypes.objects.get(pk=salary_deduction_type_id)
        template = 'master/salary/edit-salary-deduction-type.html'
        return render(request, template, context)

@login_required
def updateSalaryDeductionTypeStatus(request,salary_deduction_type_id):
    context = {}
    if SpSalaryDeductionTypes.objects.filter(id=salary_deduction_type_id).exists():
        salary_deduction_type = SpSalaryDeductionTypes.objects.get(id=salary_deduction_type_id)
        if int(salary_deduction_type.status) == 1:
            salary_deduction_type.status = 0
            salary_deduction_type.save()
        else:
            salary_deduction_type.status = 1
            salary_deduction_type.save()

        context['flag'] = True
        context['message'] = "Record updated successfully."
    else:
        context['flag'] = False
        context['message'] = "Record not found."
    return JsonResponse(context)

# @login_required
# def masterSearch(request):
#     context = {}
#     context['leave_types'] = SpLeaveTypes.objects.all()
#     template = 'master/masters.html'
#     return render(request, template, context)

# @login_required
# def searchLeaveType(request,leave_type_filter):
#     context = {}
#     # leave_type = leave_type_filter
#     context['leave_types'] = SpLeaveTypes.objects.filter(leave_type__icontains=leave_type_filter)
#     template = 'master/leave-holidays/ajax-leave-type-list.html'
#     return render(request, template, context)

# @login_required
# def searchHolidayType(request,holiday_type_filter):
#     context = {}
#     context['holiday_types'] = SpHolidayTypes.objects.filter(holiday_type__icontains=holiday_type_filter)
#     template = 'master/leave-holidays/ajax-holiday-type-list.html'
#     return render(request, template, context)

# @login_required
# def searchPayBand(request,pay_band_filter):
#     context = {}
#     context['pay_bands'] = SpPayBands.objects.filter(pay_band__icontains=pay_band_filter)
#     template = 'master/paybands/ajax-pay-band-list.html'
#     return render(request, template, context)

# @login_required
# def searchAttendanceGroup(request,search_attendance_group_filter):
#     context = {}
#     context['attendance_groups'] = SpAttendanceGroups.objects.filter(attendance_group__icontains=search_attendance_group_filter)
#     template = 'master/attendance-group/ajax-attendance-group-list.html'
#     return render(request, template, context)

# @login_required
# def searchSalaryAdditionTypeList(request,search_salary_addition_filter):
#     context = {}
#     context['salary_addition_types'] = SpSalaryAdditionTypes.objects.filter(addition__icontains=search_salary_addition_filter)
#     template = 'master/salary/ajax-salary-addition-type-list.html'
#     return render(request, template, context)

# @login_required
# def searchSalaryDeductionTypeList(request,search_salary_deduction_filter):
#     context = {}
#     context['salary_deduction_types'] = SpSalaryDeductionTypes.objects.filter(deduction__icontains=search_salary_deduction_filter)
#     template = 'master/salary/ajax-salary-deduction-type-list.html'
#     return render(request, template, context)

# @login_required
# def searchIncomeCategoryList(request,income_category_id):
#     context = {}
#     context['income_category'] = TblClIncomeCategory.objects.filter(income_category__icontains=income_category_id)
#     template = 'master/income-category/ajax-income-category.html'
#     return render(request, template, context)

@login_required
def ajaxIncomeCategoryList(request):
    context = {}
    context['income_category'] = TblClIncomeCategory.objects.all()
    template = 'master/income-category/ajax-income-category.html'
    return render(request, template, context)


@login_required
def addIncomeCategoryList(request):
    if request.method == "POST":
        response = {}
        if TblClIncomeCategory.objects.filter(income_category=clean_data(request.POST['income_category'])).exists():
            response['flag'] = False
            response['message'] = "Income Category already exists."
        else:
            income = TblClIncomeCategory()
            income.income_category = clean_data(
                request.POST['income_category'])
            income.created_at = date.today()
            income.save()
            if income.id:
                response['flag'] = True
                response['message'] = "Record has been saved successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        template = 'master/income-category/add-income-category.html'
        return render(request, template, context)


@login_required
def editIncomeCategory(request, income_category_id):
    if request.method == "POST":
        response = {}
        income_category_id = request.POST['income_category_id']
        if TblClIncomeCategory.objects.filter(income_category=clean_data(request.POST['income_category'])).exclude(id=income_category_id).exists():
            response['flag'] = False
            response['message'] = "Pay band already exists."
        else:
            income_category = TblClIncomeCategory.objects.get(id=income_category_id)
            income_category.income_category = clean_data(request.POST['income_category'])
            income_category.save()
            if income_category.id:
                response['flag'] = True
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        context['income_category'] = TblClIncomeCategory.objects.get(pk=income_category_id)
        template = 'master/income-category/edit-income-category.html'
        return render(request, template, context)



@login_required
def ajaxCollegeSessionList(request):
    context = {}
    context['college_session'] = TblClCollegeSession.objects.all()
    template = 'master/college/ajax-college-session.html'
    return render(request, template, context)

@login_required
def addCollegeSession(request):
    if request.method == "POST":
        response = {}
        if TblClCollegeSession.objects.filter(session=clean_data(request.POST['session'])).exists():
            response['flag'] = False
            response['message'] = "College session already exists."
        else:
            session = TblClCollegeSession()
            session.session = clean_data(request.POST['session'])
            session.created_at = datetime.today()
            session.updated_at = datetime.today()
            session.save()
            if session.id:
                response['flag'] = True
                response['message'] = "Record has been saved successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."
        return JsonResponse(response)
    else:
        context = {}
        template = 'master/college/add-college-session.html'
        return render(request, template, context)

@login_required
def editCollegeSession(request, session_id):
    if request.method == "POST":
        response = {}  
        if TblClCollegeSession.objects.filter(session=clean_data(request.POST['session'])).exists():
            response['flag'] = False
            response['message'] = "College session already exists."
        else:
            session = TblClCollegeSession.objects.get(id=session_id)
            session.session = clean_data(request.POST['session'])
            session.created_at = datetime.today()
            session.updated_at = datetime.today()
            session.save()
            if session.id:
                response['flag'] = True
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."
        return JsonResponse(response)
    else:
        context = {}
        context['session'] = TblClCollegeSession.objects.get(pk=session_id)
        template = 'master/college/edit-college-session.html'
        return render(request, template, context)



@login_required
def ajaxPrviliageCategoryList(request):
    context = {}
    context['Prviliage_category'] = TblClPrviliageCategory.objects.all()
    template = 'master/prviliage-category/ajax-prviliage-category-list.html'
    return render(request, template, context)

@login_required
def addPrviliageCategory(request):
    if request.method == "POST":
        response = {}
        if TblClPrviliageCategory.objects.filter(prviliage_category=clean_data(request.POST['prviliage_category'])).exists():
            response['flag'] = False
            response['message'] = "Prviliage Category already exists."
        else:
            prviliageCategory = TblClPrviliageCategory()
            prviliageCategory.prviliage_category = request.POST.get('prviliage_category')
            prviliageCategory.created_at = datetime.today()
            prviliageCategory.updated_at = datetime.today()
            prviliageCategory.status = 0
            prviliageCategory.save()
            if prviliageCategory.id:
                response['flag'] = True
                response['message'] = "Record has been saved successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        template = 'master/prviliage-category/add-prviliage-category.html'
        return render(request, template, context)

@login_required
def editPrviliageCategory(request, prviliage_category_id):
    if request.method == "POST":
        response = {}
        if TblClPrviliageCategory.objects.filter(prviliage_category=clean_data(request.POST['prviliage_category'])).exists():
            response['flag'] = False
            response['message'] = "Prviliage Category already exists."
        else:
            prviliage = TblClPrviliageCategory.objects.get(id=prviliage_category_id)
            prviliage.prviliage_category = request.POST['prviliage_category']
            prviliage.created_at = datetime.today()
            prviliage.updated_at = datetime.today()
            prviliage. status = 0
            prviliage.save()
            if prviliage.id:
                response['flag'] = True
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        context['prviliage_category'] = TblClPrviliageCategory.objects.get(pk=prviliage_category_id)
        template = 'master/prviliage-category/edit-prviliage-category.html'
        return render(request, template, context)



@login_required
def ajaxCasteCategoryList(request):
    context = {}
    context['caste_category'] = TblClCasteCategory.objects.all()
    template = 'master/caste-category/ajax-caste-category.html'
    return render(request, template, context)

@login_required
def addCasteCategoryList(request):
    if request.method == "POST":
        response = {}
        if TblClCasteCategory.objects.filter(caste_category=clean_data(request.POST['caste_category'])).exists():
            response['flag'] = False
            response['message'] = "Caste Category already exists."
        else:
            caste = TblClCasteCategory()
            caste.caste_category = clean_data(request.POST['caste_category'])
            caste.created_at = date.today()

            caste.save()
            if caste.id:
                response['flag'] = True
                response['message'] = "Record has been saved successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        template = 'master/caste-category/add-caste-category.html'
        return render(request, template, context)

@login_required
def editCasteCategory(request, caste_category_id):
    if request.method == "POST":
        response = {}
        caste_category_id = request.POST['caste_category_id']
        if TblClCasteCategory.objects.filter(caste_category=clean_data(request.POST['caste_category'])).exists():
            response['flag'] = False
            response['message'] = "Caste already exists."
        else:
            caste_category = TblClCasteCategory.objects.get(
                id=caste_category_id)
            caste_category.caste_category = clean_data(
                request.POST['caste_category'])
            caste_category.save()
            if caste_category.id:
                response['flag'] = True
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        context['caste_category'] = TblClCasteCategory.objects.get(
            pk=caste_category_id)
        template = 'master/caste-category/edit-caste-category.html'
        return render(request, template, context)



@login_required
def ajaxDistrictList(request):
    context = {}
    get_all_district_name = TblNewDistrict.objects.all()
    for get_all_district in get_all_district_name:
        get_all_district.state_name = getModelColumnById(TblStates, get_all_district.state_id, 'state')
    context['districts'] = get_all_district_name
    template = 'master/location/ajax-district-list.html'
    return render(request, template, context)


@login_required
def addDistrict(request):
    if request.method == "POST":
        response = {}
        if TblNewDistrict.objects.filter(district_name=request.POST['district_name']).exists():
            response['flag'] = False
            response['message'] = "District already exists."
        else:
            district = TblNewDistrict()
            district.state_id = request.POST['state_id']
            # district.state_name = getModelColumnById(TblStates, request.POST['state_id'], 'state')
            district.district_name = request.POST['district_name']
            district.status = 1
            district.save()

            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['states'] = TblStates.objects.all()
        template = 'master/location/add-district.html'
        return render(request, template, context)


@login_required
def editDistrict(request, district_id):
    if request.method == "POST":
        response = {}
        district_id = request.POST['district_id']
        if TblNewDistrict.objects.filter(district_name=request.POST['district_name']).exclude(id=district_id).exists():
            response['flag'] = False
            response['message'] = "District already exists."
        else:
            district = TblNewDistrict.objects.get(id=district_id)
            district.state_id = request.POST['state_id']
            # district.state_name = getModelColumnById(TblStates, request.POST['state_id'], 'state')
            district.district_name = request.POST['district_name']
            district.save()

            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['district'] = TblNewDistrict.objects.get(id=district_id)
        context['states'] = TblStates.objects.all()
        template = 'master/location/edit-district.html'
        return render(request, template, context)


@login_required
def ajaxTehsilList(request):
    context = {}
    all_tehsil = TblNewTehsil.objects.all()
    for tehsil in all_tehsil:
        tehsil.district_name = getModelColumnById(
            TblNewDistrict, tehsil.district_id, 'district_name')

    context['tehsils'] = all_tehsil
    template = 'master/location/ajax-tehsil-list.html'
    return render(request, template, context)


@login_required
def addTehsil(request):
    if request.method == "POST":
        response = {}
        if TblNewTehsil.objects.filter(tehsil_name=request.POST['tehsil_name']).exists():
            response['flag'] = False
            response['message'] = "Tehsil already exists."
        else:
            tehsil = TblNewTehsil()
            tehsil.district_id = request.POST['district_id']
            tehsil.tehsil_name = request.POST['tehsil_name']
            tehsil.status = 1
            tehsil.save()

            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['districs'] = TblNewDistrict.objects.all()
        template = 'master/location/add-tehsil.html'
        return render(request, template, context)


@login_required
def editTehsil(request, tehsil_id):
    if request.method == "POST":
        response = {}
        tehsil_id = request.POST['tehsil_id']
        if TblNewTehsil.objects.filter(tehsil_name=request.POST['tehsil_name']).exclude(id=tehsil_id).exists():
            response['flag'] = False
            response['message'] = "Tehsil already exists."
        else:
            tehsil = TblNewTehsil.objects.get(id=tehsil_id)
            tehsil.district_id = request.POST['district_id']
            tehsil.tehsil_name = request.POST['tehsil_name']
            tehsil.save()
            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['tehsil'] = tehsil = TblNewTehsil.objects.get(id=tehsil_id)
        context['states'] = TblStates.objects.all()
        context['districts'] = TblNewDistrict.objects.all()
        template = 'master/location/edit-tehsil.html'
        return render(request, template, context)



@login_required
def ajaxSectionList(request):
    context = {}
    context['section'] = TblClSection.objects.all()
    template = 'master/section/ajax-section-list.html'
    return render(request, template, context)

@login_required
def addSection(request):
    if request.method == "POST":
        response = {}
        if TblClSection.objects.filter(section_name=request.POST['section_name']).exists():
            response['flag'] = False
            response['message'] = "Section already exists."
        else:
            section = TblClSection()
            section.section_name = request.POST['section_name']
            section.created_at = date.today()
            section.save()

            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['section'] = TblClSection.objects.all()
        template = 'master/section/add-section.html'
        return render(request, template, context)

@login_required
def editSection(request, section_id):
    if request.method == "POST":
        response = {}
        if TblClSection.objects.filter(section_name=request.POST['section_name']).exists():
            response['flag'] = False
            response['message'] = "Section already exists."
        else:
            section_id = request.POST['section_id']
            section = TblClSection.objects.get(id=section_id)
            section.section_name = request.POST['section_name']
            section.created_at = date.today()
            section.save()

            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['section'] = TblClSection.objects.get(id=section_id)
        template = 'master/section/edit-section.html'
        return render(request, template, context)



@login_required
def ajaxDocumentTypeList(request):
    context = {}
    context['document_type'] = TblClDocumentTypes.objects.all()
    template = 'master/document-type/ajax-document-type.html'
    return render(request, template, context)

@login_required
def ajaxRackList(request):
    context = {}
    context['rack'] = TblClRack.objects.all()
    template = 'master/rack/ajax-rack-list.html'
    return render(request, template, context)


@login_required
def ajaxAlmirahList(request):
    context = {}
    context['almirah'] = TblClAlmirah.objects.all()
    template = 'master/almirah/ajax-almirah-list.html'
    return render(request, template, context)


@login_required
def addDocumentTypeList(request):
    if request.method == "POST":
        response = {}
        if TblClDocumentTypes.objects.filter(document_name=clean_data(request.POST['document_name'])).exists():
            response['flag'] = False
            response['message'] = "Document already exists."
        else:
            document = TblClDocumentTypes()
            document.document_name = clean_data(
                request.POST['document_name'])
            document.description = clean_data(
                request.POST['description'])
            document.status = 1
            document.created_at = date.today()
            document.save()
            if document.id:
                response['flag'] = True
                response['message'] = "Record has been saved successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        template = 'master/document-type/add-document-type.html'
        return render(request, template, context)


@login_required
def addRack(request):
    if request.method == "POST":
        response = {}
        room_id = request.POST['room_id']
        college_id = request.POST['college_id']
        almira_id = request.POST['almira_id']
        rack_name=request.POST['rack']
        if TblClRack.objects.filter(college_id=college_id,room_id=room_id,almira_id=almira_id,rack=rack_name).exists():
            response['flag'] = False
            response['message'] = "Rack already exists."
        else:
            rack = TblClRack()
            rack.almira_id = clean_data(request.POST['almira_id'])
            rack.college_id = clean_data(request.POST['college_id'])
            rack.room_id = clean_data(request.POST['room_id'])
            rack.status = 1
            rack.almira_name = getModelColumnById(TblClAlmirah, request.POST['almira_id'], 'almirah')
            rack.room_name = getModelColumnById(TblClRoom, request.POST['room_id'], 'room')
            rack.college_name = getModelColumnById(
                SpOrganizations, request.POST['college_id'], 'organization_name')
            rack.rack = clean_data(request.POST['rack'])
            rack.created_at = date.today()
            collegename_path = getModelColumnById(
                SpOrganizations, request.POST['college_id'], 'organization_name')
            room_path = getModelColumnById(TblClRoom, request.POST['room_id'], 'room')
            almira_path = getModelColumnById(TblClAlmirah, request.POST['almira_id'], 'almirah')
            roots = 'media/documents/'+collegename_path+'/'+room_path+'/'+almira_path+'/'+request.POST['rack']
            rack.path=roots
            rack.save()

            rackno = clean_data(request.POST['rack'])
            almirah_name = getModelColumnById(TblClAlmirah, request.POST['almira_id'], 'almirah')
            college_name = getModelColumnById(
                SpOrganizations, request.POST['college_id'], 'organization_name')
            room_name = getModelColumnById(TblClRoom, request.POST['room_id'], 'room')
            path = 'media/documents/'+college_name+ '/'+room_name+'/'+almirah_name+'/'
            new_dir_path = os.path.join(path, rackno)
            try:
                os.makedirs(new_dir_path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    response['message'] ='Already exists'
                    pass
                else:
                    pass
            if rack.id:
                response['flag'] = True
                response['message'] = "Record has been saved successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        context['college'] = SpOrganizations.objects.all()
        template = 'master/rack/add-rack.html'
    return render(request, template, context)


@login_required
def addAlmirah(request):
    if request.method == "POST":
        response = {}
        room_id = request.POST['room_id']
        college_id = request.POST['college_id']
        almirah_name = request.POST['almirah']
        if TblClAlmirah.objects.filter(room_id=room_id,college_id=college_id,almirah=almirah_name ).exists():
            response['flag'] = False
            response['message'] = "Already exists."
        else:
            almirah = TblClAlmirah()
            almirah.room_id = clean_data(request.POST['room_id'])
            almirah.status= 1
            almirah.college_id = clean_data(request.POST['college_id'])
            almirah.room_name = getModelColumnById(TblClRoom, request.POST['room_id'], 'room')
            almirah.college_name = getModelColumnById(
                SpOrganizations, request.POST['college_id'], 'organization_name')
            almirah.almirah = clean_data(request.POST['almirah'])
            almirah.created_at = date.today()
            collegename_path = getModelColumnById(
                SpOrganizations, request.POST['college_id'], 'organization_name')
            room_path = getModelColumnById(TblClRoom, request.POST['room_id'], 'room')
            roots = 'media/documents/'+collegename_path+'/'+room_path+'/'+request.POST['almirah']
            almirah.path=roots 
            almirah.save()
            almirah_name = clean_data(request.POST['almirah'])
            college_name = getModelColumnById(
                SpOrganizations, request.POST['college_id'], 'organization_name')
            room_name = getModelColumnById(TblClRoom, request.POST['room_id'], 'room')
            path = 'media/documents/'+college_name+ '/'+room_name+'/'
            new_dir_path = os.path.join(path, almirah_name)
            try:
                os.makedirs(new_dir_path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    response['message'] ='Already exists'
                    pass
                else:
                    pass
            if almirah.id:
                response['flag'] = True
                response['message'] = "Record has been saved successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."
        return JsonResponse(response)
    else:
        context = {}
        #context['room'] = TblClRoom.objects.all()
        context['college'] = SpOrganizations.objects.all()
        template = 'master/almirah/add-almirah.html'
        return render(request, template, context)


def getCollegeByRoom(request):
    response = {}
    college_id=request.GET['college_id']
    options = '<option value="" selected>Select Room</option>'
    Room_no = TblClRoom.objects.filter(college_id=college_id,status=1)
    for RoomNo in Room_no :
        options +="<option value="+str(RoomNo.id)+">"+RoomNo.room+"</option>"
    response['output'] = options
    return JsonResponse(response)

def getRoomByAlmirah(request):
    room_id=request.GET['room_id']
    response = {}
    options = '<option value="" selected>Select Almira</option>'
    Room_no = TblClAlmirah.objects.filter(room_id=room_id,status=1)
    for RoomNo in Room_no :
        options += "<option value="+str(RoomNo.id)+">"+RoomNo.almirah+"</option>"
    response['output'] = options
    return JsonResponse(response)

@login_required
def editRackList(request, rack_id):
    if request.method == "POST":
        response = {}
        rack_id = request.POST['rack_id']
        if TblClRack.objects.filter(rack=clean_data(request.POST['rack'])).exclude(id=rack_id).exists():
            response['flag'] = False
            response['message'] = "Rack already exists."
        else:
            rack = TblClRack.objects.get(id=rack_id)
            rack.almira_id = clean_data(request.POST['almira_id'])
            rack.almira_name = getModelColumnById(TblClAlmirah, request.POST['almira_id'], 'almirah')    
            rack.rack = clean_data(request.POST['rack'])
            rack.created_at = date.today()
            rack.save()
            if rack.id:
                response['flag'] = True
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."
        return JsonResponse(response)
    else:
        context = {}
        context['rack'] = TblClRack.objects.get(pk=rack_id)
        context['almirah'] = TblClAlmirah.objects.all()
        template = 'master/rack/edit-rack.html'
        return render(request, template, context)


@login_required
def editAlmirahList(request, almirah_id):
    if request.method == "POST":
        response = {}
        almirah_id = request.POST['almirah_id']
        if TblClAlmirah.objects.filter(almirah=clean_data(request.POST['almirah'])).exclude(id=almirah_id).exists():
            response['flag'] = False
            response['message'] = "Almirah already exists."
        else:
            almirah = TblClAlmirah.objects.get(id=almirah_id)
            almirah.room_id = clean_data(request.POST['room_id'])
            almirah.room_name = getModelColumnById(TblClRoom, request.POST['room_id'], 'room')
            almirah.almirah = clean_data(request.POST['almirah'])
            almirah.created_at = date.today()
            almirah.save()
            if almirah.id:
                response['flag'] = True
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        context['almirah'] = TblClAlmirah.objects.get(pk=almirah_id)
        context['room'] = TblClRoom.objects.all()
        template = 'master/almirah/edit-almirah.html'
        return render(request, template, context)


@login_required
def editDocumentTypeList(request, document_type_id):
    if request.method == "POST":
        response = {}
        document_type_id = request.POST['document_type_id']
        if TblClDocumentTypes.objects.filter(document_name=clean_data(request.POST['document_name'])).exclude(id=document_type_id).exists():
            response['flag'] = False
            response['message'] = "Document already exists."
        else:
            document_type = TblClDocumentTypes.objects.get(
                id=document_type_id)
            document_type.document_name = clean_data(
                request.POST['document_name'])
            document_type.description = clean_data(
                request.POST['description'])
            document_type.save()
            if document_type.id:
                response['flag'] = True
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        context['document_type'] = TblClDocumentTypes.objects.get(
            pk=document_type_id)
        template = 'master/document-type/edit-document-type.html'
        return render(request, template, context)



@login_required
def ajaxRoomList(request):
    context = {}
    context['room'] = TblClRoom.objects.all()
    template = 'master/room/ajax-room-no.html'
    return render(request, template, context)


@login_required
def addRoomList(request):
    if request.method == "POST":
        response = {}
        college_id = request.POST['college_id']
        room=request.POST['room']
        if TblClRoom.objects.filter(room=room,college_id=college_id ).exists():
            response['flag'] = False
            response['message'] = "room no. already exists."
        else:
            room = TblClRoom()
            room.college_id = request.POST['college_id']
            room.college_name = getModelColumnById(
                SpOrganizations, request.POST['college_id'], 'organization_name')
            room.room = request.POST['room']
            room.status = 1
            room.created_at = date.today()
            collegename_path = getModelColumnById(
                SpOrganizations, request.POST['college_id'], 'organization_name')
            roots = 'media/documents/'+collegename_path+'/'+request.POST['room']
            room.path=roots 
            room.save()
           
            college_name = getModelColumnById(
                SpOrganizations, request.POST['college_id'], 'organization_name')
            roomNo = request.POST['room']

            #Creating a folder in static directory
            root = 'media/documents/'
            new_dir_path = os.path.join(root, college_name)
            try:
                os.makedirs(new_dir_path)
               
            except OSError as e:
                if e.errno != errno.EEXIST:
                    response['message'] = "Already exists"
                else:
                    pass
            roompath = 'media/documents/'+college_name+'/'
            new_dir_roomno= os.path.join(roompath, roomNo)
            try:
                os.makedirs(new_dir_roomno)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    response['message'] ='Already exists'
                else:
                    pass
            if room.id:
                    response['flag'] = True
                    response['message'] = "Record has been saved successfully."
            else:
                    response['flag'] = False
                    response['message'] = "Failed to save record."

        return JsonResponse(response)

    else:
        context = {}
        context['college'] = SpOrganizations.objects.all()
        template = 'master/room/add-room-no.html'
        return render(request, template, context)


@login_required
def editRoomList(request, room_id):
    if request.method == "POST":
        response = {}
        if TblClRoom.objects.filter(room=request.POST['room']).exists():
            response['flag'] = False
            response['message'] = "room no already exists."
        else:
            room_id = request.POST['room_id']
            room = TblClRoom.objects.get(id=room_id)
            room.room = request.POST['room']
            room.college_id = request.POST['college_id']
            room.college_name = getModelColumnById(
                SpOrganizations, request.POST['college_id'], 'organization_name')
            room.created_at = date.today()
            room.save()

            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['room'] = TblClRoom.objects.get(id=room_id)
        context['college'] = SpOrganizations.objects.all()
        template = 'master/room/edit-room-no.html'
        return render(request, template, context)


@login_required
def updateRoomStatus(request,room_status):
    context = {}
    if TblClRoom.objects.filter(id=room_status).exists():
        room_status = TblClRoom.objects.get(id=room_status)
        if int(room_status.status) == 1:
            room_status.status = 0
            room_status.save()
        else:
            room_status.status = 1
            room_status.save()
            
        context['flag'] = True
        context['message'] = "Record updated successfully."
    else:
        context['flag'] = False
        context['message'] = "Record not found."
    return JsonResponse(context)

@login_required
def updateAlmiraStatus(request,almira_status):
    context = {}
    if TblClAlmirah.objects.filter(id=almira_status).exists():
        almira_status = TblClAlmirah.objects.get(id=almira_status)
        if int(almira_status.status) == 1:
            almira_status.status = 0
            almira_status.save()
        else:
            almira_status.status = 1
            almira_status.save()

        context['flag'] = True
        context['message'] = "Record updated successfully."
    else:
        context['flag'] = False
        context['message'] = "Record not found."
    return JsonResponse(context)

@login_required
def updateRackStatus(request,rack_status):
    context = {}
    if TblClRack.objects.filter(id=rack_status).exists():
        rack_status = TblClRack.objects.get(id=rack_status)
        if int(rack_status.status) == 1:
            rack_status.status = 0
            rack_status.save()
        else:
            rack_status.status = 1
            rack_status.save()

        context['flag'] = True
        context['message'] = "Record updated successfully."
    else:
        context['flag'] = False
        context['message'] = "Record not found."
    return JsonResponse(context)

@login_required
def ajaxGroupTypeList(request):
    context = {}
    context['group_type'] = TblClDocumentGroup.objects.all()
    template = 'master/group-type/ajax-group-type-list.html'
    return render(request, template, context)


@login_required
def addAGroupType(request):
    if request.method == "POST":
        response = {}
        if TblClDocumentGroup.objects.filter(group_name=clean_data(request.POST['group_name'])).exists():
            response['flag'] = False
            response['message'] = "Group already exists."
        else:
            group = TblClDocumentGroup()
            group.group_name = clean_data(
                request.POST['group_name'])
            group.status = 1
            group.created_at = date.today()
            group.save()
            if group.id:
                response['flag'] = True
                response['message'] = "Record has been saved successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        template = 'master/group-type/add-group.html'
        return render(request, template, context)


@login_required
def editGroupTypeList(request, group_type_id):
    if request.method == "POST":
        response = {}
        group_type_id = request.POST['group_name']
        group_id = request.POST['group_id']
        if TblClDocumentGroup.objects.filter(group_name=clean_data(request.POST['group_name'])).exclude(id=group_id).exists():
            response['flag'] = False
            response['message'] = "Group already exists."
        else:
            group = TblClDocumentGroup.objects.get(id=group_id)
            group.group_name = clean_data(request.POST['group_name'])
            group.save()
            if group.id:
                response['flag'] = True
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        context['group_type'] = TblClDocumentGroup.objects.get(
            id=group_type_id)
        template = 'master/group-type/edit-group-type.html'
        return render(request, template, context)


@login_required
def updateGroupTypeStatus(request, group_type_id):
    context = {}
    if TblClDocumentGroup.objects.filter(id=group_type_id).exists():
        group_type = TblClDocumentGroup.objects.get(id=group_type_id)
        if int(group_type.status) == 1:
            group_type.status = 0
            group_type.save()
        else:
            group_type.status = 1
            group_type.save()

        context['flag'] = True
        context['message'] = "Record updated successfully."
    else:
        context['flag'] = False
        context['message'] = "Record not found."
    return JsonResponse(context)


@login_required
def ajaxJobTypeList(request):
    context = {}
    context['job_types'] = ContractType.objects.all()
    template = 'master/job-type/ajax-job-type-list.html'
    return render(request, template, context)


@login_required
def addJobType(request):
    if request.method == "POST":
        response = {}
        if ContractType.objects.filter(contract_type=clean_data(request.POST['job_name'])).exists():
            response['flag'] = False
            response['message'] = "Job already exists."
        else:
            job = ContractType()
            job.contract_type = clean_data(request.POST['job_name'])
            job.status = 1
            job.created_at = date.today()
            job.save()
            if job.id:
                response['flag'] = True
                response['message'] = "Job Type has been saved successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        template = 'master/job-type/add-job.html'
        return render(request, template, context)


@login_required
def editJobTypeList(request, job_type_id):
    if request.method == "POST":
        response = {}
        job_id = job_type_id
        job_type_id = request.POST['job_name']
        if ContractType.objects.filter(contract_type=clean_data(request.POST['job_name'])).exclude(id=job_id).exists():
            response['flag'] = False
            response['message'] = "Job already exists."
        else:
            group = ContractType.objects.get(id=job_id)
            group.contract_type = clean_data(request.POST['job_name'])
            group.save()
            if group.id:
                response['flag'] = True
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        context['job_type'] = ContractType.objects.get(id=job_type_id)
        template = 'master/job-type/edit-job-type.html'
        return render(request, template, context)

@login_required
def updateJobTypeStatus(request, job_type_id):
    context = {}
    if ContractType.objects.filter(id=job_type_id).exists():
        job_type = ContractType.objects.get(id=job_type_id)
        if int(job_type.status) == 1:
            job_type.status = 0
            job_type.save()
        else:
            job_type.status = 1
            job_type.save()

        context['flag'] = True
        context['message'] = "Record updated successfully."
    else:
        context['flag'] = False
        context['message'] = "Record not found."
    return JsonResponse(context)

def addHalfDaySlot(request):
    if request.method == "POST":
        id = request.POST['id']
        obj = TblClWorkingShifts.objects.get(id=id)
        obj.first_half_start_timing = request.POST['f_start_time_data']
        obj.first_half_end_timing = request.POST['f_end_time_data']
        obj.second_half_start_timing = request.POST['s_start_time_data']
        obj.second_half_end_timing = request.POST['s_end_time_data']
        obj.save()
        context = {}
        context['flag'] = True
        context['message'] = "Record updated successfully."
        return JsonResponse(context)
    else:
        context = {}
        id = request.GET['id']
        context['half_day_slot'] = TblClWorkingShifts.objects.get(id=id)
        template = 'master/attendance-group/add-hlaf-day-slot.html'
        return render(request, template, context)
        
 