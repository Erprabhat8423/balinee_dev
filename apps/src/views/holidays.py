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
from datetime import datetime
from calendar import monthrange
from datetime import date
import calendar

# Create your views here.

# @login_required
# def index(request):
#     context = {}
#     year = datetime.now().year
#     currentMonth = datetime.now().month
#     month = ['January','February','March','April','May','June','July','August','September','October','November','December']
#     num_days = monthrange(year, currentMonth)[1]
#     page = request.GET.get('page')
#     holidays = SpHolidays.objects.all().order_by('-id')
#     paginator = Paginator(holidays, getConfigurationResult('page_limit'))

#     try:
#         holidays = paginator.page(page)
#     except PageNotAnInteger:
#         holidays = paginator.page(1)
#     except EmptyPage:
#         holidays = paginator.page(paginator.num_pages)  
#     if page is not None:
#            page = page
#     else:
#            page = 1
    
#     total_pages = int(paginator.count/getConfigurationResult('page_limit')) 

#     if(paginator.count == 0):
#         paginator.count = 1

#     temp = total_pages%paginator.count
#     if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
#         total_pages = total_pages+1
#     else:
#         total_pages = total_pages
#     firstWeek = []
#     secondWeek = []
#     thirdWeek = []
#     fourthWeek = []
#     fifthWeek = []
  
#     weekday = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
#     day = calendar.weekday(year,currentMonth,1)

#     for i in range(1,num_days+1):
#         if day != '0':
#             if len(firstWeek)<7-int(day):
#                 firstWeek.append(i)
#             elif len(secondWeek)<7:
#                 secondWeek.append(i)
#             elif len(thirdWeek)<7:
#                 thirdWeek.append(i)
#             elif len(fourthWeek)<7:
#                 fourthWeek.append(i)
#             else:
#                 fifthWeek.append(i)
#         else:
#             if len(firstWeek)<7:
#                 firstWeek.append(i)
#             elif len(secondWeek)<7:
#                 secondWeek.append(i)
#             elif len(thirdWeek)<7:
#                 thirdWeek.append(i)
#             elif len(fourthWeek)<7:
#                 fourthWeek.append(i)
#             else:
#                 fifthWeek.append(i)
#     if day != 0:
#         manageDays = []
#         for i in range(day):
#             manageDays.append(i)
#         context['manageDays'] = manageDays
#     context['last_holiday'] = last_holiday = SpHolidays.objects.all().order_by('-id').first()
#     context['total_pages'] = total_pages
#     context['holidays'] = holidays
#     context['currentMonth'] = month[currentMonth-1]
#     context['currentYear'] = year

    
#     context['firstWeek'] = firstWeek
#     context['secondWeek'] = secondWeek
#     context['thirdWeek'] = thirdWeek
#     context['fourthWeek'] = fourthWeek
#     context['fifthWeek'] = fifthWeek

#     context['page_title'] = "Manage Holidays"
#     template = 'profile/manage-holidays.html'
#     # template = 'holidays/index.html'
#     return render(request, template, context)

@login_required
def index(request):
    page = request.GET.get('page')
    
    holidays = list(SpHolidays.objects.raw(''' SELECT * FROM sp_holidays order by id desc'''))
    paginator = Paginator(holidays, getConfigurationResult('page_limit'))
    try:
        holidays = paginator.page(page)
    except PageNotAnInteger:
        holidays = paginator.page(1)
    except EmptyPage:
        holidays = paginator.page(paginator.num_pages)  
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

    if len(holidays):
        holidays_id = holidays[0].id
        last_holiday = SpHolidays.objects.raw(''' SELECT * FROM sp_holidays WHERE id = %s ''',[holidays_id])[0]
        holiday_dates = []

        start_date = last_holiday.start_date
        delta = last_holiday.end_date - last_holiday.start_date
        for i in range(delta.days + 1):
            holiday_date = start_date + timedelta(days=i)
            holiday_date = holiday_date.strftime('%Y-%m-%d')
            holiday_dates.append(holiday_date)

        calendarObj = calendar.Calendar()
        calendar_dates = []
        for week in calendarObj.monthdatescalendar(current_year, current_month):
            dates = []
            for week_date in week:
                calendar_datass = []
                tmp = {}
                tmp['full_date'] = week_date
                tmp['day'] = week_date.strftime('%A')
                tmp['short_date'] = week_date.strftime('%d')
                tmp['month'] = week_date.strftime('%m')
                                  

                if str(week_date) in holiday_dates:
                     tmp['is_holiday'] = 1
                     tmp['holiday'] = last_holiday.holiday
                else:
                    tmp['is_holiday'] = 0
                
                dates.append(tmp)               
            calendar_dates.append(dates)
    if str(request.user.role_id) == '0':
        context['institutions'] = SpOrganizations.objects.all()
    else:
        institutes_ids = SpUsers.objects.filter(role_id=request.user.role_id).values('id')
        for institute_id in institutes_ids:
            context['institutions'] = SpOrganizations.objects.filter(id=institute_id['id'])
    context['roles'] = SpRoles.objects.all()
    context['calendar_dates'] = calendar_dates
    context['holiday'] = last_holiday
    context['holidays'] = holidays
    context['holiday_types'] = SpHolidayTypes.objects.all()
    context['total_pages'] = total_pages
    context['page_limit'] = getConfigurationResult('page_limit')
    context['page_title'] = "Manage Holidays"
    template = 'holidays/index.html'
    return render(request, template, context)


@login_required
def leaveFilterStatus(request,filter_status):
    if request.method == 'POST':
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
        page = request.GET.get('page')
        if filter_status !='rep1':
            context['holidays'] = SpHolidays.objects.filter(holiday_status=filter_status)
        else:
            context['holidays'] = SpHolidays.objects.all()       
        template = 'holidays/ajax-holiday-filter.html'
        return render(request, template, context)


@login_required
def HolidayCalendar(request,holiday_id):
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
    
    if holiday_id != "rep1":
        last_holiday = SpHolidays.objects.raw(''' SELECT * FROM sp_holidays WHERE id = %s ''',[holiday_id])[0]
    else:
        last_holiday = SpHolidays.objects.raw(''' SELECT * FROM sp_holidays ''')[0]
    holiday_dates = []

    start_date = last_holiday.start_date
    delta = last_holiday.end_date - last_holiday.start_date
    for i in range(delta.days + 1):
        holiday_date = start_date + timedelta(days=i)
        holiday_date = holiday_date.strftime('%Y-%m-%d')
        holiday_dates.append(holiday_date)

    calendarObj = calendar.Calendar()
    calendar_dates = []
    for week in calendarObj.monthdatescalendar(current_year, current_month):
        dates = []
        for week_date in week:
            calendar_datass = []
            tmp = {}
            tmp['full_date'] = week_date
            tmp['day'] = week_date.strftime('%A')
            tmp['short_date'] = week_date.strftime('%d')
            tmp['month'] = week_date.strftime('%m')
                                

            if str(week_date) in holiday_dates:
                    tmp['is_holiday'] = 1
                    tmp['holiday'] = last_holiday.holiday
            else:
                tmp['is_holiday'] = 0
            
            dates.append(tmp)               
        calendar_dates.append(dates)

    context['calendar_dates'] = calendar_dates
    context['holiday'] = last_holiday
    context['page_limit'] = getConfigurationResult('page_limit')
    context['page_title'] = "Manage Holidays"

    template = 'holidays/customer-vacation-calendar.html'
    return render(request, template, context)

@login_required
def addHoliday(request):
    if request.method == "POST":
        context = {}
        holiday_dates = []

        if clean_data(request.POST['filter_org_name[]']):
            for org_id in clean_data(request.POST['filter_org_name[]']):
                org_name = getModelColumnById(SpOrganizations,org_id,'organization_name')  
                holiday = SpHolidays()
                holiday.holiday = clean_data(request.POST['holidayName'])
                holiday.holiday_type_id = request.POST['holiday_type_id'] #From Where
                holiday.holiday_type = getModelColumnById(SpHolidayTypes,request.POST['holiday_type_id'],'holiday_type')
                
                holiday.organization_name = org_name
                holiday.organization_id = org_id
                holiday.start_time = "00:00:00" #clean_data(request.POST['from_time'])
                holiday.start_date = datetime.strptime(clean_data(request.POST['from_date']), '%d/%m/%Y').strftime('%Y-%m-%d')
                holiday.end_date = datetime.strptime(clean_data(request.POST['to_date']), '%d/%m/%Y').strftime('%Y-%m-%d')
                holiday.end_time = "00:00:00"
                holiday.description = clean_data(request.POST['holiday_description'])
                holiday.status = 1 
                holiday.holiday_status = 1               
                holiday.save()
                sendNotificationToUsers(holiday.id, clean_data(request.POST['holidayName']), "add" , 33, request.user.id, request.user.first_name+" "+request.user.middle_name+" "+request.user.last_name, "SpHolidays", request.user.role_id)
                if holiday.id:
                    context['flag'] = True
                    context['message'] = "Record has been save successfully."
                else:
                    context['flag'] = False
                    context['message'] = "Failed to save record."
            return JsonResponse(context)
        
    else:
        context = {}
        # context['holiday_types'] = SpHolidayTypes.objects.filter(status=1)
        # template = 'holidays'
        # return render(request, template, context)
        context['flag'] = False
        context['message'] = "Method Not Allowed"
        return JsonResponse(context)
    


@login_required
def editHoliday(request,holiday_id):
    if request.method == "POST":
        context = {}
        holiday_name       = clean_data(request.POST['holiday'])
        holiday_id       = request.POST['holiday_id']
        if SpHolidays.objects.filter(holiday=holiday_name).exclude(id=holiday_id).exists():
            context['flag'] = False
            context['message'] = "Holiday already exists."
        else:
            holiday = SpHolidays.objects.get(id=holiday_id)
            holiday.holiday = clean_data(request.POST['holiday'])
            holiday.holiday_type_id = request.POST['holiday_type_id']
            holiday.holiday_type = getModelColumnById(SpHolidayTypes,request.POST['holiday_type_id'],'holiday_type')
            holiday.start_date = datetime.strptime(clean_data(request.POST['from_date']), '%d/%m/%Y').strftime('%Y-%m-%d')
            holiday.start_time = clean_data(request.POST['from_time'])
            holiday.end_date = datetime.strptime(clean_data(request.POST['to_date']), '%d/%m/%Y').strftime('%Y-%m-%d')
            holiday.end_time = clean_data(request.POST['to_time'])
            holiday.description = clean_data(request.POST['description'])
            holiday.status = 1
            holiday.save()

            if holiday.id:
                context['flag'] = True
                context['message'] = "Record has been updated successfully."

            else:
                context['flag'] = False
                context['message'] = "Failed to update record."

        return JsonResponse(context)
    else:
        context = {}
        context['holiday'] = holiday = SpHolidays.objects.get(id=holiday_id)
        context['holiday_types'] = SpHolidayTypes.objects.filter(status=1)
        template = 'holidays/edit-holiday.html'
        return render(request, template, context)

@login_required
def holidaysPolicyShortDetails(request,holiday_id):
    context = {}
    last_holiday = SpHolidays.objects.get(id=holiday_id)
    context['last_holiday'] = last_holiday
    template = 'holidays/holiday-short-details.html'
    return render(request, template, context)

@login_required
def ajaxHolidayRows(request):

    page = request.GET.get('page')
    holidays = SpHolidays.objects.all().order_by('-id')
    paginator = Paginator(holidays, getConfigurationResult('page_limit'))

    try:
        holidays = paginator.page(page)
    except PageNotAnInteger:
        holidays = paginator.page(1)
    except EmptyPage:
        holidays = paginator.page(paginator.num_pages)  
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
    context['holidays']     = holidays
    context['total_pages']       = total_pages

    template = 'holidays/ajax-holiday-rows.html'
    return render(request, template, context)

@login_required
def updateHolidayStatus(request):

    response = {}
    if request.method == "POST":
        try:
            id = request.POST.get('id')
            is_active = request.POST.get('is_active')

            data = SpHolidays.objects.get(id=id)
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

@login_required
def leaveReport(request):
    today = date.today()
    
    if request.user.role_id == 0:
        leaveReport = SpUserLeaves.objects.all().order_by('-id')

    else:
        leaveReport = SpUserLeaves.objects.raw('''SELECT sp_user_leaves.*, sp_approval_status.level_id, sp_approval_status.level, sp_approval_status.status, sp_approval_status.final_status_user_id, sp_approval_status.final_status_user_name, sp_users.store_name
    FROM sp_user_leaves left join sp_approval_status on sp_approval_status.row_id = sp_user_leaves.id
    left join sp_users on sp_users.id = sp_user_leaves.user_id 
    where  sp_approval_status.user_id = %s and sp_approval_status.model_name = 'SpUserLeaves' order by id desc ''',[request.user.id])
    

    user_type = SpPermissionWorkflowRoles.objects.filter(sub_module_id=38,  workflow_level_role_id=request.user.role_id).exclude(level_id=1).values('level_id').order_by('-id').first()  
    if user_type:
        level_id = user_type['level_id']
    else:
        level_id = '0'
    context = {}

    user_ids = SpUserLeaves.objects.all().distinct().values_list('user_id',flat=True)
    users = SpUsers.objects.filter(id__in=user_ids).values('id','first_name','middle_name','last_name','emp_sap_id')

    context['leaveReport'] = leaveReport
    context['role_id'] = request.user.role_id
    context['level_id'] = level_id
    context['today_date'] = today.strftime("%d/%m/%Y")
    context['page_title'] = "Manage Leaves"
    context['users'] = users

    template = 'holidays/attendance-report/leave-report.html'
    return render(request, template, context)


# ajax order list
@login_required
def ajaxLeaveReportLists(request):
    context = {}
    today = date.today()
    user_id = request.GET['user_id']
    leaveReport = SpUserLeaves.objects.all().order_by('-id')
    if request.user.role_id == 0:
        if 'leave_status' in request.GET and request.GET['leave_status'] != "":
            leave_status = request.GET['leave_status']
            context['leave_status'] = leave_status
            leaveReport = leaveReport.filter(leave_status=leave_status).order_by('-id')

        # if 'leave_from_date' in request.GET and request.GET['leave_from_date'] and request.GET['leave_to_date']:
        #     leave_from_date = datetime.strptime(request.GET['leave_from_date'], '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S')
        #     leave_to_date = datetime.strptime(request.GET['leave_to_date'], '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S')
            
        #     leaveReport = leaveReport.filter(leave_from_date__range=(leave_from_date, leave_to_date))
        # if request.GET['leave_from_date']:
        #     if request.GET['leave_to_date'] in today.strftime("%d/%m/%Y"):
        #         leave_from_date = datetime.strptime(request.GET['leave_from_date'], '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S')
                
        #         leaveReport = leaveReport.filter(leave_from_date__range=(leave_from_date, leave_to_date))
        if user_id:
                leaveReport = leaveReport.filter(user_id=user_id).order_by('-id')
    else:
        condition = ''
        
        if 'leave_status' in request.GET and request.GET['leave_status'] != "":
            leave_status = request.GET['leave_status']
            condition += ' and sp_user_leaves.leave_status = "%s"' % leave_status
        if user_id:
            condition += ' and sp_user_leaves.user_id = "%s"' % user_id
            

        query = """SELECT sp_user_leaves.*, sp_approval_status.level_id, sp_approval_status.level, sp_approval_status.status, sp_approval_status.final_status_user_id, sp_approval_status.final_status_user_name, sp_users.store_name
        FROM sp_user_leaves left join sp_approval_status on sp_approval_status.row_id = sp_user_leaves.id
        left join sp_users on sp_users.id = sp_user_leaves.user_id 
        where  sp_approval_status.user_id = %s and sp_approval_status.model_name = 'SpUserLeaves' %s order by id desc """ % (request.user.id,condition)

        leaveReport = SpUserLeaves.objects.raw(query)

        
    

    user_type = SpRoleWorkflowPermissions.objects.filter(sub_module_id=8, permission_slug='add',
                                                             workflow_level_role_id=request.user.role_id).exclude(
            role_id=request.user.role_id).values('level_id').order_by('-id').first()
    if user_type:
        level_id = user_type['level_id']
    else:
        level_id = '0'
    context['leaveReport'] = leaveReport
    context['level_id'] = level_id

    context['role_id'] = request.user.role_id
    template = 'holidays/attendance-report/ajax-leave-report-lists.html'
    return render(request, template, context)

@login_required
def leaveStatusDetails(request):
    leave_id = request.GET.get('leave_id')
    initiate_leave_details = SpUserLeaves.objects.get(id=leave_id)
    leave_details = SpApprovalStatus.objects.filter(row_id=leave_id, model_name='SpUserLeaves', status=1).values(
        'final_status_user_id').distinct().values('final_status_user_name', 'final_update_date_time', 'level_id')

    context = {}
    context['initiate_leave_details'] = initiate_leave_details
    context['leave_details'] = leave_details
    template = 'holidays/attendance-report/leave-status-details.html'

    return render(request, template, context)


@login_required
def leaveExportToXlsx(request, columns, userId,leave_status):
    column_list = columns.split(",")

    leaveReport = SpUserLeaves.objects.all().order_by('-id')
    if request.user.role_id == 0:
        condition = ''
        if leave_status != "" and leave_status != "0":
            condition += ' and leave_status = "%s"' % leave_status

        if userId != "" and userId != "0":
            condition += ' and user_id = "%s"' % userId
        
        leaveReport = SpUserLeaves.objects.raw("""SELECT * FROM sp_user_leaves WHERE 1 {condition}  order by id desc """.format(condition=condition))
    else:
        condition = ''
        if leave_status != "" and leave_status != "0":
            condition += ' and sp_user_leaves.leave_status = "%s"' % leave_status

        if userId != "" and userId != "0":
            condition += ' and sp_user_leaves.user_id = "%s"' % userId

            

        query = """SELECT sp_user_leaves.*, sp_approval_status.level_id, sp_approval_status.level, sp_approval_status.status, sp_approval_status.final_status_user_id, sp_approval_status.final_status_user_name, sp_users.store_name
        FROM sp_user_leaves left join sp_approval_status on sp_approval_status.row_id = sp_user_leaves.id
        left join sp_users on sp_users.id = sp_user_leaves.user_id 
        where  sp_approval_status.user_id = %s and sp_approval_status.model_name = 'SpUserLeaves' %s order by id desc """ % (request.user.id,condition)

        leaveReport = SpUserLeaves.objects.raw(query)

        
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=leave-report.xlsx'.format(
        date=datetime.now().strftime('%Y-%m-%d'),
    )
    workbook = Workbook()

    # Define some styles and formatting that will be later used for cells
    header_font = Font(name='Calibri', bold=True)
    centered_alignment = Alignment(horizontal='left')
    thin = Side(border_style="thin", color="303030")
    black_border = Border(top=thin, left=thin, right=thin, bottom=thin)
    wrapped_alignment = Alignment(
        vertical='top',
        wrap_text=True
    )
    # Get active worksheet/tab
    worksheet = workbook.active
    worksheet.title = 'Leave-reports'

    # Define the titles for columns
    columns = []

    if 'user_name' in column_list:
        columns += ['Name']

    if 'leave_from_date' in column_list:
        columns += ['Leave Apply From Date']

    if 'leave_to_date' in column_list:
        columns += ['Leave Apply To Date']

    if 'status' in column_list:
        columns += ['Status']

    row_num = 1
    # Assign the titles for each cell of the header
    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title
        cell.font = header_font
        cell.alignment = centered_alignment
        cell.font = Font(size=12, color='FFFFFFFF', bold=True)
        cell.fill = PatternFill(start_color="4d86bf", end_color="4d86bf", fill_type="solid")

        column_letter = get_column_letter(col_num)
        column_dimensions = worksheet.column_dimensions[column_letter]
        column_dimensions.width = 23

    for results in leaveReport:
        row_num += 1
        # Define the data for each cell in the row
        row = []
        if 'user_name' in column_list:
            row += [results.user_name]

        if 'leave_from_date' in column_list:
            if None in [results.leave_from_date]:
                leave_from_date = ['']
            else:
                leave_from_date = [results.leave_from_date]
            row += leave_from_date

        if 'leave_to_date' in column_list:
            if None in [results.leave_to_date]:
                leave_to_date = ['']
            else:
                leave_to_date = [results.leave_to_date]
            row += leave_to_date

        if 'status' in column_list:
            if results.leave_status == 1:
                status = 'Pending'
                row += [status]
            elif results.leave_status == 2:
                status = 'Forwarded'
                row += [status]
            elif results.leave_status == 3:
                status = 'Approved'
                row += [status]
            elif results.leave_status == 4:
                status = 'Declined'
                row += [status]
        # Assign the data for each cell of the row
        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value
            cell.alignment = wrapped_alignment
            cell.border = black_border
    workbook.save(response)

    return response

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


# Automaticly downloads to PDF file
@login_required
def leaveExportToPDF(request, columns, userId,leave_status):
    column_list = columns.split(",")

    leaveReport = SpUserLeaves.objects.all().order_by('-id')
    if request.user.role_id == 0:
        condition = ''
        if leave_status != "" and leave_status != "0":
            condition += ' and leave_status = "%s"' % leave_status

        if userId != "" and userId != "0":
            condition += ' and user_id = "%s"' % userId
        
        leaveReport = SpUserLeaves.objects.raw("""SELECT * FROM sp_user_leaves WHERE 1 {condition}  order by id desc """.format(condition=condition))
    else:
        condition = ''
        if leave_status != "" and leave_status != "0":
            condition += ' and sp_user_leaves.leave_status = "%s"' % leave_status

        if userId != "" and userId != "0":
            condition += ' and sp_user_leaves.user_id = "%s"' % userId

            

        query = """SELECT sp_user_leaves.*, sp_approval_status.level_id, sp_approval_status.level, sp_approval_status.status, sp_approval_status.final_status_user_id, sp_approval_status.final_status_user_name, sp_users.store_name
        FROM sp_user_leaves left join sp_approval_status on sp_approval_status.row_id = sp_user_leaves.id
        left join sp_users on sp_users.id = sp_user_leaves.user_id 
        where  sp_approval_status.user_id = %s and sp_approval_status.model_name = 'SpUserLeaves' %s order by id desc """ % (request.user.id,condition)

        leaveReport = SpUserLeaves.objects.raw(query)
    
    baseurl = settings.BASE_URL
    pdf = render_to_pdf('holidays/attendance-report/leave_pdf_template.html',
                        {'leaveReport': leaveReport, 'url': baseurl, 'columns': column_list,
                         'columns_length': len(column_list)})
    
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = 'leave-report.pdf'
    content = "attachment; filename=%s" % filename
    response['Content-Disposition'] = content
    return response


@login_required
def editLeaveStatus(request):
    id = request.GET.get('id')
    context = {}
    context['leaveData'] = SpUserLeaves.objects.get(id=id)
    template = 'holidays/attendance-report/edit-leave-status.html'
    return render(request, template, context)

@login_required
def updateLeaveRemark(request): 
    context = {}
    context['level_id']     = request.GET.get('level_id')
    context['leave_status'] = request.GET.get('leave_status')
    template = 'holidays/attendance-report/update-leave-remark.html'
    return render(request, template, context)

#update order status
@login_required
def updateLeaveStatus(request):
    response = {}
    leave_id        = request.POST.getlist('leave_id[]')
    level_id        = request.POST['level_id']
    leave_status    = request.POST['leave_status']
    if request.user.role_id == 0:
        for leave in leave_id:
            approvals_request = SpApprovalStatus.objects.filter(row_id=leave, model_name='SpUserLeaves', level_id=level_id)
            if approvals_request:
                for approval in approvals_request:
                    approval_data                           = SpApprovalStatus.objects.get(id=approval.id)
                    approval_data.level_id                  = leave_status
                    if leave_status == '2':
                        approval_data.level                    = 'Forward'
                    elif leave_status == '3':
                        approval_data.level                    = 'Approve'
                    elif leave_status == '4':
                        approval_data.level                    = 'Declined'         
                    approval_data.status                    = 1
                    approval_data.final_status_user_id      = request.user.id
                    approval_data.final_status_user_name    = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
                    approval_data.final_update_date_time    = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    approval_data.save()

                user_level_approval_count = SpApprovalStatus.objects.filter(row_id=leave, model_name='SpUserLeaves', level_id=level_id, status=0).count()
                if user_level_approval_count == 0:
                    leave                   = SpUserLeaves.objects.get(id=leave)   
                    leave.leave_status      = leave_status
                    if request.POST['remark']:
                        leave.remark      = request.POST['remark']
                    leave.save()
            else:
                leave                   = SpUserLeaves.objects.get(id=leave)   
                leave.leave_status      = leave_status
                if request.POST['remark']:
                    leave.remark      = request.POST['remark']
                leave.updated_at        = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                leave.save()
                today   = date.today()
                 
    
    else:    
        for leave in leave_id:
            approvals_request = SpApprovalStatus.objects.filter(row_id=leave, model_name='SpUserLeaves', role_id=request.user.role_id, level_id=level_id)
            for approval in approvals_request:
                approval_data                           = SpApprovalStatus.objects.get(id=approval.id)
                approval_data.status                    = 1
                approval_data.final_status_user_id      = request.user.id
                approval_data.final_status_user_name    = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
                approval_data.final_update_date_time    = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                approval_data.save()

            user_level_approval_count = SpApprovalStatus.objects.filter(row_id=leave, model_name='SpUserLeaves', level_id=level_id, status=0).count()
            if user_level_approval_count == 0:
                leave                   = SpUserLeaves.objects.get(id=leave)   
                leave.leave_status      = leave_status
                if request.POST['remark']:
                    leave.remark      = request.POST['remark']
                leave.save()   

    
    if leave_status == '2':
        for leave in leave_id:
            approvals_requests = SpApprovalStatus.objects.filter(row_id=leave, model_name='SpUserLeaves', status=0)
            if approvals_requests:
                for approval in approvals_requests:
                    notification                        = SpUserNotifications()
                    notification.row_id                 = approval.row_id
                    notification.user_id                = approval.user_id
                    notification.model_name             = 'SpUserLeaves'
                    notification.notification           = 'leave '+approval.level+' Request has been sent.'
                    notification.is_read                = 0
                    notification.created_by_user_id     = request.user.id
                    notification.created_by_user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
                    notification.save()

    if leave_status == '2':
        for leave in leave_id:
            user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
            heading     = 'Leave Request has been forwarded'
            activity    = 'Leave Request has been forwarded by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            if request.POST['remark']:
                activity += '. '+request.POST['remark']
            saveActivity('User Management', 'Leave', heading, activity, request.user.id, user_name, 'forwaord.png', '1', 'web.png')

            #-----------------------------notify android block-------------------------------#
            user_id = getModelColumnById(SpUserLeaves,leave,'user_id')
            user_role = getModelColumnById(SpUsers,user_id,'role_name')
            userFirebaseToken = getModelColumnById(SpUsers,user_id,'firebase_token')
            employee_name = getUserName(user_id)
            
            message_title = "Leave request forwarded"
            message_body = "A Leave request("+employee_name+" - "+user_role+") has been forwarded  by "+user_name
            if request.POST['remark']:
                message_body += '. '+request.POST['remark']
            notification_image = ""

            if userFirebaseToken is not None and userFirebaseToken != "" :
                registration_ids = []
                registration_ids.append(userFirebaseToken)
                data_message = {}
                data_message['id'] = 1
                data_message['status'] = 'notification'
                data_message['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
                data_message['image'] = notification_image
                send_android_notification(message_title,message_body,data_message,registration_ids)
                #-----------------------------notify android block-------------------------------#

            #-----------------------------save notification block----------------------------#
            saveNotification(leave,'SpUserLeaves','User Management','Leave request forwarded',message_title,message_body,notification_image,request.user.id,user_name,user_id,employee_name,'profile.png',2,'app.png',1,1)
            #-----------------------------save notification block----------------------------#
            employee_role = getModelColumnById(SpUsers, user_id, 'role_id')
            if employee_role == 5:
                user_area_allocation = SpUserAreaAllocations.objects.filter(user_id=user_id).values('town_id')
                user_list = []   
                for area_allocation in user_area_allocation:
                    operational_user_list  = SpUserAreaAllocations.objects.raw(''' SELECT sp_user_area_allocations.id, sp_user_area_allocations.town_name, sp_users.id as user_id, sp_users.first_name, sp_users.middle_name, sp_users.role_id, sp_users.user_type, sp_users.reporting_to_id, sp_users.reporting_to_name, sp_users.primary_contact_number, sp_users.store_name, sp_users.last_name, sp_users.is_tagged FROM sp_user_area_allocations left join sp_users on sp_users.id = sp_user_area_allocations.user_id WHERE sp_user_area_allocations.town_id=%s and sp_users.role_id=%s and sp_users.status=%s order by sp_users.first_name asc ''', [area_allocation['town_id'], 4, 1])
                    if operational_user_list: 
                        for operational_user in operational_user_list:
                            user_list.append(operational_user.user_id)
                            
                if len(user_list) > 0:
                    for tse in user_list:
                        userFirebaseToken = getModelColumnById(SpUsers,tse,'firebase_token')
                        employee_name = getUserName(tse)
                        if userFirebaseToken is not None and userFirebaseToken != "" :
                            registration_ids = []
                            registration_ids.append(userFirebaseToken)
                            data_message = {}
                            data_message['id'] = 1
                            data_message['status'] = 'notification'
                            data_message['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
                            data_message['image'] = notification_image
                            send_android_notification(message_title,message_body,data_message,registration_ids)
                        #-----------------------------save notification block----------------------------#
                        saveNotification(leave,'SpUserLeaves','User Management','Leave request approved',message_title,message_body,notification_image,request.user.id,user_name,tse,employee_name,'profile.png',2,'app.png',1,1)
                        #-----------------------------save notification block----------------------------# 
    elif leave_status == '3':
        for leave in leave_id:
            user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
            heading     = 'Leave Request has been approved'
            activity    = 'Leave Request has been approved by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            if request.POST['remark']:
                activity += '. '+request.POST['remark']
            saveActivity('User Management', 'Leave', heading, activity, request.user.id, user_name, 'approved.svg', '1', 'web.png')

            #-----------------------------notify android block-------------------------------#
            user_id = getModelColumnById(SpUserLeaves,leave,'user_id')
            user_role = getModelColumnById(SpUsers,user_id,'role_name')
            userFirebaseToken = getModelColumnById(SpUsers,user_id,'firebase_token')
            employee_name = getUserName(user_id)

            #update user leave count
            user_basic_details              = SpBasicDetails.objects.get(user_id=user_id)
            leave_count                     = int(user_basic_details.leave_count)-1   
            user_basic_details.leave_count  = leave_count
            user_basic_details.save()

            message_title = "Leave request approved"
            message_body = "A Leave request("+employee_name+" - "+user_role+") has been approved  by "+user_name
            if request.POST['remark']:
                message_body += '. '+request.POST['remark']
            notification_image = ""

            if userFirebaseToken is not None and userFirebaseToken != "" :
                registration_ids = []
                registration_ids.append(userFirebaseToken)
                data_message = {}
                data_message['id'] = 1
                data_message['status'] = 'notification'
                data_message['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
                data_message['image'] = notification_image
                send_android_notification(message_title,message_body,data_message,registration_ids)
                #-----------------------------notify android block-------------------------------#

            #-----------------------------save notification block----------------------------#
            saveNotification(leave,'SpUserLeaves','User Management','Leave request approved',message_title,message_body,notification_image,request.user.id,user_name,user_id,employee_name,'profile.png',2,'app.png',1,1)
            #-----------------------------save notification block----------------------------#
            employee_role = getModelColumnById(SpUsers, user_id, 'role_id')
            if employee_role == 5:
                user_area_allocation = SpUserAreaAllocations.objects.filter(user_id=user_id).values('town_id')
                user_list = []   
                for area_allocation in user_area_allocation:
                    operational_user_list  = SpUserAreaAllocations.objects.raw(''' SELECT sp_user_area_allocations.id, sp_user_area_allocations.town_name, sp_users.id as user_id, sp_users.first_name, sp_users.middle_name, sp_users.role_id, sp_users.user_type, sp_users.reporting_to_id, sp_users.reporting_to_name, sp_users.primary_contact_number, sp_users.store_name, sp_users.last_name, sp_users.is_tagged FROM sp_user_area_allocations left join sp_users on sp_users.id = sp_user_area_allocations.user_id WHERE sp_user_area_allocations.town_id=%s and sp_users.role_id=%s and sp_users.status=%s order by sp_users.first_name asc ''', [area_allocation['town_id'], 4, 1])
                    if operational_user_list: 
                        for operational_user in operational_user_list:
                            user_list.append(operational_user.user_id)
                            
                if len(user_list) > 0:
                    for tse in user_list:
                        userFirebaseToken = getModelColumnById(SpUsers,tse,'firebase_token')
                        employee_name = getUserName(tse)
                        if userFirebaseToken is not None and userFirebaseToken != "" :
                            registration_ids = []
                            registration_ids.append(userFirebaseToken)
                            data_message = {}
                            data_message['id'] = 1
                            data_message['status'] = 'notification'
                            data_message['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
                            data_message['image'] = notification_image
                            send_android_notification(message_title,message_body,data_message,registration_ids)
                        #-----------------------------save notification block----------------------------#
                        saveNotification(leave,'SpUserLeaves','User Management','Leave request approved',message_title,message_body,notification_image,request.user.id,user_name,tse,employee_name,'profile.png',2,'app.png',1,1)
                        #-----------------------------save notification block----------------------------#    

    elif leave_status == '4':
        for leave in leave_id:
            user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
            heading     = 'Leave Request has been declined'
            activity    = 'Leave Request has been declined by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            if request.POST['remark']:
                activity += '. '+request.POST['remark']
            saveActivity('User Management', 'Leave', heading, activity, request.user.id, user_name, 'declined.svg', '1', 'web.png')

            #-----------------------------notify android block-------------------------------#
            user_id = getModelColumnById(SpUserLeaves,leave,'user_id')
            user_role = getModelColumnById(SpUsers,user_id,'role_name')
            userFirebaseToken = getModelColumnById(SpUsers,user_id,'firebase_token')
            employee_name = getUserName(user_id)

            message_title = "Leave request declined"
            message_body = "A Leave request("+employee_name+" - "+user_role+") has been declined  by "+user_name
            if request.POST['remark']:
                message_body += '. '+request.POST['remark']
            notification_image = ""

            if userFirebaseToken is not None and userFirebaseToken != "" :
                registration_ids = []
                registration_ids.append(userFirebaseToken)
                data_message = {}
                data_message['id'] = 1
                data_message['status'] = 'notification'
                data_message['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
                data_message['image'] = notification_image
                send_android_notification(message_title,message_body,data_message,registration_ids)
                #-----------------------------notify android block-------------------------------#

            #-----------------------------save notification block----------------------------#
            saveNotification(leave,'SpUserLeaves','User Management','Leave request declined',message_title,message_body,notification_image,request.user.id,user_name,user_id,employee_name,'profile.png',2,'app.png',1,1)
            #-----------------------------save notification block----------------------------#
            employee_role = getModelColumnById(SpUsers, user_id, 'role_id')
            if employee_role == 5:
                user_area_allocation = SpUserAreaAllocations.objects.filter(user_id=user_id).values('town_id')
                user_list = []   
                for area_allocation in user_area_allocation:
                    operational_user_list  = SpUserAreaAllocations.objects.raw(''' SELECT sp_user_area_allocations.id, sp_user_area_allocations.town_name, sp_users.id as user_id, sp_users.first_name, sp_users.middle_name, sp_users.role_id, sp_users.user_type, sp_users.reporting_to_id, sp_users.reporting_to_name, sp_users.primary_contact_number, sp_users.store_name, sp_users.last_name, sp_users.is_tagged FROM sp_user_area_allocations left join sp_users on sp_users.id = sp_user_area_allocations.user_id WHERE sp_user_area_allocations.town_id=%s and sp_users.role_id=%s and sp_users.status=%s order by sp_users.first_name asc ''', [area_allocation['town_id'], 4, 1])
                    if operational_user_list: 
                        for operational_user in operational_user_list:
                            user_list.append(operational_user.user_id)
                            
                if len(user_list) > 0:
                    for tse in user_list:
                        userFirebaseToken = getModelColumnById(SpUsers,tse,'firebase_token')
                        employee_name = getUserName(tse)
                        if userFirebaseToken is not None and userFirebaseToken != "" :
                            registration_ids = []
                            registration_ids.append(userFirebaseToken)
                            data_message = {}
                            data_message['id'] = 1
                            data_message['status'] = 'notification'
                            data_message['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
                            data_message['image'] = notification_image
                            send_android_notification(message_title,message_body,data_message,registration_ids)
                        #-----------------------------save notification block----------------------------#
                        saveNotification(leave,'SpUserLeaves','User Management','Leave request approved',message_title,message_body,notification_image,request.user.id,user_name,tse,employee_name,'profile.png',2,'app.png',1,1)
                        #-----------------------------save notification block----------------------------#

    response['error'] = False
    response['message'] = "Leave status has been updated successfully."
    return JsonResponse(response)
