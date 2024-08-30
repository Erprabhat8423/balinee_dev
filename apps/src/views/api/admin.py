from re import T, search
from django.contrib.auth import authenticate
from datetime import datetime
from django.db.models.query import QuerySet
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_405_METHOD_NOT_ALLOWED
)
from django.http.response import JsonResponse
from rest_framework.response import Response
from utils.helper import *
from ...models import *
import json, math

from datetime import datetime, date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def HomePageAPI(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        user_id = request_data['user_id']
        check_user = SpUsers.objects.filter(role_id = 0).values()[0]['id']
        if user_id == check_user:
            today_visit = TblHomeVisit.objects.filter(created_at__icontains = datetime.now().today().date() )
            total_visit = TblHomeVisit.objects.all()

            current_date = datetime.now().date()
            each_faculty_visit = TblHomeVisit.objects.all().values('faculty_id').distinct()
            faculty_content = []

            for each_visit in each_faculty_visit:
                visit_dashboard = {}
                faculty_visit = TblHomeVisit.objects.filter(faculty_id = each_visit['faculty_id'])
                faculty_today = TblHomeVisit.objects.filter(faculty_id = each_visit['faculty_id']).filter(created_at__icontains = current_date)
                visit_dashboard['faculty_name'] = getUserName(each_visit['faculty_id'])
                visit_dashboard['total_visit'] = len(faculty_visit)
                visit_dashboard['today_visit'] = len(faculty_today)
                faculty_content.append(visit_dashboard)
            
            _week = {}
            dates_between = days_between_dates(current_date, (current_date-timedelta(6)))

            for each_day in dates_between:
                visit_week = TblHomeVisit.objects.filter(created_at__icontains = each_day).count()
                _day = calendar.day_name[datetime.strptime(each_day, "%Y-%m-%d").weekday()]
                _week[_day] = visit_week

            context = {}
            context['today_visit']          = len(today_visit)
            context['total_visit']          = len(total_visit)
            context['faculty_visit']        = faculty_content
            context['weekly']               = _week
            context['graph_from']           = current_date-timedelta(6)
            context['graph_to']             = current_date
            context['message']              = "Success"
            context['response_status'] = HTTP_200_OK

            return Response(context, status=HTTP_200_OK)
        else:
            return Response({'message':'Unauthorized user, Access denied!'}, status=HTTP_401_UNAUTHORIZED)



# Pagination
def pagination(page,data):

    # pagination code start
    if page is None or page == "":
        page = 1
    else:
        page=page    

    paginator = Paginator(data, 10)
    
    
    try:
        current_data = paginator.page(page)
    except PageNotAnInteger:
        current_data = paginator.page(1)
    except EmptyPage:
        current_data = paginator.page(paginator.num_pages)
        
    if current_data.has_next():
        next_page = current_data.next_page_number()
    else :
        next_page = paginator.num_pages
    if current_data.has_previous():
        previous_page = current_data.previous_page_number()
    else :
        previous_page = 1
    
    page_dict={}

    page_dict['current_data']=current_data
    page_dict['total_pages'] = paginator.num_pages
    page_dict['next_page'] = next_page
    page_dict['previous_page'] = previous_page
    # pagination code end
    return page_dict





@csrf_exempt
@api_view(['POST'])
def studentAttendanceList(request):
    if request.data.get("attendance_type") is None or request.data.get("attendance_type") == '':
       return Response({'message': 'Attendance Type field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   

    if request.data.get("college_id") is None or request.data.get("college_id") == '':
       return Response({'message': 'College Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   

    # if request.data.get("page") is None or request.data.get("page") == '':
    #    return Response({'message': 'Page field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   
    
    param  =""
    params = ""
  
    if request.data.get("attendance_type")==1:  # present
        today           = date.today()

        total_student   = TblStudents.objects.filter(is_registered=1,status=1,college_id=request.data.get("college_id")).count()

    
        student_lists = []

        if request.data.get("attendance_date"):
            param += "DATE(tbl_attendance.start_datetime) ='%%"+str(request.data.get('attendance_date'))+"%%'"
            param +=" and tbl_students.college_id = %s group by tbl_students.id" % request.data.get("college_id")
        else:
            param +=" DATE(tbl_attendance.start_datetime) ='%%"+str(today.strftime("%Y-%m-%d"))+"%%'"  
            param +=" and tbl_students.college_id = %s group by tbl_students.id" % int(request.data.get("college_id"))
          
        if request.data.get("course_id"):
            param += " tbl_students.course_type_id={}".format(request.data.get("course_id"))
        if request.data.get("mentor"):
            param += " tbl_students.teacher_gaurdian_name like '%%"+str(request.data.get("mentor"))+"%%'"
        if request.data.get("semester_id"):
            params += " tbl_students.semester_id='%%"+str(request.data.get("semester_id"))+"%%'"

        if request.data.get("sort_by_name")=="asc":
            param += " order by tbl_students.first_name or tbl_students.middle_name or tbl_students.last_name asc"
        elif request.data.get("sort_by_name")=="desc":
            param += " order by tbl_students.first_name or tbl_students.middle_name or tbl_students.last_name desc"    
        
        if request.data.get("sort_by_intime")=="asc": 
            param += " order by tbl_attendance.start_datetime asc"
        elif request.data.get("sort_by_intime")=="desc":
            param += " order by tbl_attendance.start_datetime desc"  
         
        if request.data.get("sort_by_outtime")=="asc":
             param += " order by tbl_attendance.end_datetime asc"
        elif request.data.get("sort_by_outtime")=="desc":    
            param += " order by tbl_attendance.end_datetime desc"  
     
        today_present_student = TblStudents.objects.raw(''' SELECT tbl_students.id FROM tbl_students left join tbl_attendance on tbl_attendance.student_id = tbl_students.id where tbl_students.is_registered=1 and tbl_students.status=1 and {param} '''.format(param=param))
        
        
        # students=pagination(request.data.get("page"),today_present_student)
        
        for student in today_present_student:
            student_data                  = {}
            student_data['id']            = student.id
            student_data['first_name']    = student.first_name
            student_data['middle_name']   = student.middle_name
            student_data['last_name']     = student.last_name
            student_data['profile_image'] = student.profile_image
            student_data['reg_no']        = student.reg_no
            student_data['course']        = student.course_type_name
            student_data['mobile_no']     = student.primary_contact_no
            student_data['father_name']   = student.father_name
            student_data['mother_name']   = student.mother_name
            student_data['mentor']        = student.teacher_gaurdian_name
            student_data['in_time']       = student.start_datetime
            student_data['out_time']      = student.end_datetime
            student_lists.append(student_data)
        
        today_present_student = len(today_present_student)
        
        today_absent_student = int(total_student)-int(today_present_student)

    elif request.data.get("attendance_type")==0:
        today           = date.today()

        total_student   = TblStudents.objects.filter(is_registered=1,status=1,college_id=request.data.get("college_id")).count()

        if request.data.get("attendance_date"):
            params += "DATE(tbl_attendance.start_datetime) LIKE '%%"+str(request.data.get('attendance_date'))+"%%'"
            params +=" and tbl_students.college_id = %s group by tbl_students.id" % request.data.get("college_id")
        else:
            params +=" DATE(tbl_attendance.start_datetime) LIKE '%%"+str(today.strftime("%Y-%m-%d"))+"%%'"  
            params +=" and tbl_students.college_id = %s group by tbl_students.id" % int(request.data.get("college_id"))
          
        if request.data.get("course_id"):
            params += " and tbl_students.course_type_id={}".format(request.data.get("course_id"))
        if request.data.get("mentor"):
            params += " and tbl_students.teacher_gaurdian_name like '%%"+str(request.data.get("mentor"))+"%%'"
        if request.data.get("semester_id"):
            params += " and tbl_students.semester_id='%%"+str(request.data.get("semester_id"))+"%%'"
     
        today_present_student = TblStudents.objects.raw(''' SELECT tbl_students.id FROM tbl_students left join tbl_attendance on tbl_attendance.student_id = tbl_students.id where tbl_students.is_registered=1 and tbl_students.status=1 and {params} '''.format(params=params))

        if request.data.get("attendance_date"):
            attendance_id =TblAttendance.objects.filter(start_datetime__date=request.data.get('attendance_date')).distinct().values_list('student_id',flat=True)
            today_absent_students = TblStudents.objects.filter(is_registered=1,status=1,college_id=request.data.get("college_id")).exclude(id__in=attendance_id)
        else:   
           attendance_id =TblAttendance.objects.filter(start_datetime__date=today.strftime("%Y-%m-%d")).distinct().values_list('student_id',flat=True)
           today_absent_students = TblStudents.objects.filter(is_registered=1,status=1,college_id=request.data.get("college_id")).exclude(id__in=attendance_id)
   
        if request.data.get("course_id"):
            today_absent_students = today_absent_students.filter(course_type_id=request.data.get("course_id"))
        if request.data.get("mentor"):
            today_absent_students = today_absent_students.filter(teacher_gaurdian_name__icontains=request.data.get("mentor"))
        if request.data.get("semester_id"):
            today_absent_students=today_absent_students.filter(semester_id=request.data.get("semester_id"))
    
        if request.data.get("sort_by_name")=="asc":
            today_absent_students=today_absent_students.order_by('first_name')
        elif request.data.get("sort_by_name")=="desc":
            today_absent_students=today_absent_students.order_by('-first_name')
      
        
        student_lists = []
        
        # students=pagination(request.data.get("page"),today_absent_student)
        
        for student in today_absent_students:
            student_data                  = {}
            student_data['id']            = student.id
            student_data['first_name']    = student.first_name
            student_data['middle_name']   = student.middle_name
            student_data['last_name']     = student.last_name
            student_data['profile_image'] = student.profile_image
            student_data['reg_no']        = student.reg_no
            student_data['course']        = student.course_type_name
            student_data['mobile_no']     = student.primary_contact_no
            student_data['father_name']   = student.father_name
            student_data['mother_name']   = student.mother_name
            student_data['mentor']        = student.teacher_gaurdian_name
           
            student_lists.append(student_data)

        today_present_student = len(today_present_student)

        today_absent_student = len(today_absent_students)

    context = {}
    context['student_list']          = student_lists
    context['total_present_student'] = today_present_student
    context['total_absent_student']  = today_absent_student
    # context['total_pages']           = students['total_pages']
    # context['next_page']             = students['next_page']
    # context['previous_page']         = students['previous_page']
    context['message']               = "Success"
    context['response_code']         = HTTP_200_OK

    return JsonResponse(context, status=HTTP_200_OK)




@csrf_exempt
@api_view(['POST'])
def employeeAttendanceList(request):
    if request.data.get("attendance_type") is None or request.data.get("attendance_type") == '':
      return Response({'message': 'Attendance Type field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   

    if request.data.get("college_id") is None or request.data.get("college_id") == '':
      return Response({'message': 'College Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   

    param =""
    params=""
    paramss=""
    context = {}
    
    if request.data.get("attendance_type")==1:  # present
        today           = date.today()

        total_employee   = SpUsers.objects.filter(user_type=1,organization_id=request.data.get("college_id"), status=1).exclude(id=1).count()

    
        employee_lists = []

        if request.data.get("attendance_date"):
            paramss += "DATE(tbl_cl_user_leaves.leave_from_date) <= '%%"+str(request.data.get('attendance_date'))+"%%'"+"<=DATE(tbl_cl_user_leaves.leave_to_date)"
            paramss +=" and sp_users.organization_id = %s group by sp_users.id" % request.data.get("college_id")
        else:   
            paramss += "DATE(tbl_cl_user_leaves.leave_from_date) <= '%%"+str(today.strftime("%Y-%m-%d"))+"%%'"+"<=DATE(tbl_cl_user_leaves.leave_to_date)"   
            paramss +=" and sp_users.organization_id = %s group by sp_users.id" % int(request.data.get("college_id"))

      
        today_leave_employee = SpUsers.objects.raw(''' SELECT sp_users.id FROM sp_users left join tbl_cl_user_leaves on tbl_cl_user_leaves.user_id = sp_users.id where sp_users.user_type=1 and {paramss} '''.format(paramss=paramss))
        

      
        if request.data.get("attendance_date"):
            param += "DATE(sp_user_attendance.attendance_date_time) LIKE '%%"+str(request.data.get('attendance_date'))+"%%'"
            param +=" and sp_users.organization_id = %s group by sp_users.id" % request.data.get("college_id")
        else:
            param +=" DATE(sp_user_attendance.attendance_date_time) LIKE '%%"+str(today.strftime("%Y-%m-%d"))+"%%'"  
            param +=" and sp_users.organization_id = %s group by sp_users.id" % int(request.data.get("college_id"))
        
        if request.data.get("sort_by_name")=="asc":
            param += " order by sp_users.first_name asc"
        elif request.data.get("sort_by_name")=="desc":
            param += " order by sp_users.first_name desc"    
        
        if request.data.get("sort_by_intime")=="asc": 
            param += " order by sp_user_attendance.attendance_date_time asc"
        elif request.data.get("sort_by_intime")=="desc":
            param += " order by sp_user_attendance.attendance_date_time desc"  
         
        if request.data.get("sort_by_outtime")=="asc":
            param += " order by sp_user_attendance.attendance_date_time asc"
        elif request.data.get("sort_by_outtime")=="desc":    
            param += " order by sp_user_attendance.attendance_date_time desc"  
     
        today_present_employee = SpUsers.objects.raw(''' SELECT sp_users.*,sp_user_attendance.* FROM sp_users left join sp_user_attendance on sp_user_attendance.user_id = sp_users.id where sp_users.user_type=1 and {param} '''.format(param=param))
        
   
        # employees=pagination(request.data.get("page"),today_present_employee)
        
        for employee in today_present_employee:
            employee_data                  = {}
            if employee.id!=1:
                employee_data['id']            = employee.id
                employee_data['first_name']    = employee.first_name
                employee_data['middle_name']   = employee.middle_name
                employee_data['last_name']     = employee.last_name
                employee_data['profile_image'] = employee.profile_image
                employee_data['attendance_date_time'] = employee.attendance_date_time
                employee_data['in_time']       =  employee.start_time
                employee_data['out_time']      =  employee.end_time
    
                employee_lists.append(employee_data)

        today_present_employee = len(today_present_employee)

        today_absent_employee = int(total_employee)-int(today_present_employee)
        
        total_leave = len(today_leave_employee)

    elif request.data.get("attendance_type")==0:
        today           = date.today()

        total_employee   = SpUsers.objects.filter(user_type=1,organization_id=request.data.get("college_id"), status=1).exclude(id=1).count()

        if request.data.get("attendance_date"):
            paramss += "DATE(tbl_cl_user_leaves.leave_from_date) <= '%%"+str(request.data.get('attendance_date'))+"%%'"+"<=DATE(tbl_cl_user_leaves.leave_to_date)"
            paramss +=" and sp_users.organization_id = %s group by sp_users.id" % request.data.get("college_id")
        else:   
            paramss += "DATE(tbl_cl_user_leaves.leave_from_date) <= '%%"+str(today.strftime("%Y-%m-%d"))+"%%'"+"<=DATE(tbl_cl_user_leaves.leave_to_date)"   
            paramss +=" and sp_users.organization_id = %s group by sp_users.id" % int(request.data.get("college_id"))

      
        today_leave_employee = SpUsers.objects.raw(''' SELECT sp_users.id FROM sp_users left join tbl_cl_user_leaves on tbl_cl_user_leaves.user_id = sp_users.id where sp_users.user_type=1 and {paramss} '''.format(paramss=paramss))
        

        if request.data.get("attendance_date"):
            params += "DATE(sp_user_attendance.attendance_date_time) LIKE '%%"+str(request.data.get('attendance_date'))+"%%'"
            params +=" and sp_users.organization_id = %s group by sp_users.id" % request.data.get("college_id")
        else:
            params +=" DATE(sp_user_attendance.attendance_date_time) LIKE '%%"+str(today.strftime("%Y-%m-%d"))+"%%'"  
            params +=" and sp_users.organization_id = %s group by sp_users.id" % int(request.data.get("college_id"))
        
        today_present_employee = SpUsers.objects.raw(''' SELECT sp_users.id FROM sp_users left join sp_user_attendance on sp_user_attendance.user_id = sp_users.id where sp_users.user_type=1 and {params} '''.format(params=params))

    
        if request.data.get("attendance_date"):
            attendance_id =SpUserAttendance.objects.filter(attendance_date_time__date=request.data.get('attendance_date')).distinct().values_list('user_id',flat=True)
            today_absent_employees = SpUsers.objects.filter(user_type=1,status=1,organization_id=request.data.get("college_id")).exclude(id__in=attendance_id)
        else:   
          attendance_id =SpUserAttendance.objects.filter(attendance_date_time__date=today.strftime("%Y-%m-%d")).distinct().values_list('user_id',flat=True)
          today_absent_employees = SpUsers.objects.filter(user_type=1,status=1,organization_id=request.data.get("college_id")).exclude(id__in=attendance_id).exclude(id=1)
   
       
        if request.data.get("sort_by_name")=="asc":
            today_absent_employees = today_absent_employees.order_by('first_name')
         
        elif request.data.get("stort_by_name")=="desc":
            today_absent_employees = today_absent_employees.order_by('-first_name')
       
     
        employee_lists = []
        
        # employees=pagination(request.data.get("page"),today_absent_employee)
        
        for employee in today_absent_employees:
            employee_data                  = {}
            if employee.id!=1:
                employee_data['id']            = employee.id
                employee_data['first_name']    = employee.first_name
                employee_data['middle_name']   = employee.middle_name
                employee_data['last_name']     = employee.last_name
                employee_data['profile_image'] = employee.profile_image
            
                employee_lists.append(employee_data)

        today_present_employee = len(today_present_employee)

        today_absent_employee = len(today_absent_employees)

        total_leave = len(today_leave_employee)
    else:
        # Employee Leave
        today           = date.today()

        total_employee   = SpUsers.objects.filter(user_type=1,organization_id=request.data.get("college_id"), status=1).exclude(id=1).count()

        if request.data.get("attendance_date"):
            params += "DATE(sp_user_attendance.attendance_date_time) LIKE '%%"+str(request.data.get('attendance_date'))+"%%'"
            params +=" and sp_users.organization_id = %s group by sp_users.id" % request.data.get("college_id")
        else:
            params +=" DATE(sp_user_attendance.attendance_date_time) LIKE '%%"+str(today.strftime("%Y-%m-%d"))+"%%'"  
            params +=" and sp_users.organization_id = %s group by sp_users.id" % int(request.data.get("college_id"))
        
        today_present_employee = SpUsers.objects.raw(''' SELECT sp_users.id FROM sp_users left join sp_user_attendance on sp_user_attendance.user_id = sp_users.id where sp_users.user_type=1 and {params} '''.format(params=params))


        if request.data.get("attendance_date"):
            attendance_id =SpUserAttendance.objects.filter(attendance_date_time__date=request.data.get('attendance_date')).distinct().values_list('user_id',flat=True)
            today_absent_employees = SpUsers.objects.filter(user_type=1,status=1,organization_id=request.data.get("college_id")).exclude(id__in=attendance_id)
        else:   
          attendance_id =SpUserAttendance.objects.filter(attendance_date_time__date=today.strftime("%Y-%m-%d")).distinct().values_list('user_id',flat=True)
          today_absent_employees = SpUsers.objects.filter(user_type=1,status=1,organization_id=request.data.get("college_id")).exclude(id__in=attendance_id).exclude(id=1)
   
       
        if request.data.get("attendance_date"):
            param += "DATE(tbl_cl_user_leaves.leave_from_date) <= '%%"+str(request.data.get('attendance_date'))+"%%'"+"<=DATE(tbl_cl_user_leaves.leave_to_date)"
            param +=" and sp_users.organization_id = %s group by sp_users.id" % request.data.get("college_id")
        else:   
            param += "DATE(tbl_cl_user_leaves.leave_from_date) <= '%%"+str(today.strftime("%Y-%m-%d"))+"%%'"+"<=DATE(tbl_cl_user_leaves.leave_to_date)"   
            param +=" and sp_users.organization_id = %s group by sp_users.id" % int(request.data.get("college_id"))

        # print("Param==>",param)

        if request.data.get("sort_by_name")=="asc":
            param += " and order by sp_users.first_name asc"
        elif request.data.get("stort_by_name")=="desc":
            param += " and order by sp_users.first_name desc"    
        
        if request.data.get("sort_by_intime")=="asc": 
            param += "and order by tbl_cl_user_leaves.leave_from_date asc"
        elif request.data.get("sort_by_intime")=="desc":
            param += "and order by tbl_cl_user_leaves.leave_from_date desc"  
         
        if request.data.get("stort_by_outtime")=="asc":
             param += "and order by tbl_cl_user_leaves.leave_to_date asc"
        elif request.data.get("stort_by_outtime")=="desc":    
            param += "and order by tbl_cl_user_leaves.leave_to_date desc"  
              
        today_leave_employee = SpUsers.objects.raw(''' SELECT sp_users.*,tbl_cl_user_leaves.* FROM sp_users left join tbl_cl_user_leaves on tbl_cl_user_leaves.user_id = sp_users.id where sp_users.user_type=1 and {param} '''.format(param=param))
        
      
        employee_lists = []
        
        # # students=pagination(request.data.get("page"),today_present_student)
        
        for employee in today_leave_employee:
            employee_data                  = {}
            if employee.id!=1:
                employee_data['id']            = employee.id
                employee_data['first_name']    = employee.first_name
                employee_data['middle_name']   = employee.middle_name
                employee_data['last_name']     = employee.last_name
                employee_data['profile_image'] = employee.profile_image
                employee_data['in_time']       =  employee.leave_from_date
                employee_data['out_time']      =  employee.leave_to_date
    
                employee_lists.append(employee_data)
        
   
        today_present_employee = len(today_present_employee)

        today_absent_employee = len(today_absent_employees)
        
        total_leave = len(today_leave_employee)

    
    context['employee_list']          = employee_lists
    context['total_present_employee'] = today_present_employee
    context['total_absent_employee']  = today_absent_employee
    context['today_leave_count']      = total_leave
    context['message']               = "Success"
    context['response_code']         = HTTP_200_OK

    return JsonResponse(context, status=HTTP_200_OK)     


@csrf_exempt
@api_view(['POST'])
def studentAttendanceMasterData(request):
  
    if request.data.get("college_id") is None or request.data.get("college_id") == '':
       return Response({'message': 'College Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   

    branches  = TblBranch.objects.filter(college_id=request.data.get("college_id")).values('id','branch')
    mentors   = SpUsers.objects.filter(organization_id=request.data.get("college_id")).values('id','first_name','middle_name','last_name')
    semesters = TblSemester.objects.all().values('id','semester_id','sem_name','type')  
   
    context                     = {}
    context['branch']           = branches
    context['semester']         = semesters
    context['mentor']           = mentors
    context['message']          = "Success"
    context['response_code']    = HTTP_200_OK

    return Response(context, status=HTTP_200_OK)     





@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def dashboardData(request):
    today           = date.today()

    dashboard_data_list = []
    colleges = SpOrganizations.objects.filter().order_by('id')
    for college in colleges:
        dashboard_data_dict = {}
        dashboard_data_dict['id']           = college.id
        dashboard_data_dict['college_name'] = college.organization_name
        dashboard_data_dict['alias']        = college.alias
        #student
        total_student   = TblStudents.objects.filter(is_registered=1,status=1,college_id=college.id).count()
        today_present_student = TblStudents.objects.raw('''SELECT tbl_students.id
        FROM tbl_students left join tbl_attendance on tbl_attendance.student_id = tbl_students.id 
            where tbl_students.is_registered=1 and status=1 and DATE(tbl_attendance.start_datetime) = %s and tbl_students.college_id = %s group by tbl_students.id  ''',[today.strftime("%Y-%m-%d"), college.id])
        today_present_student = len(today_present_student)
        today_absent_student = int(total_student)-int(today_present_student)

        #teacher
        total_teacher   = SpUsers.objects.filter(organization_id=college.id,user_type=1,status=1).exclude(id=1).count()
        today_present_teacher = SpUsers.objects.raw('''SELECT sp_users.*,sp_user_attendance.*
        FROM sp_users left join sp_user_attendance on sp_user_attendance.user_id = sp_users.id 
            where DATE(sp_user_attendance.attendance_date_time) = %s and sp_users.organization_id = %s group by sp_users.id  ''',[today.strftime("%Y-%m-%d"), college.id])
        today_present_teacher = len(today_present_teacher)
        today_absent_teacher = int(total_teacher)-int(today_present_teacher)
        
        # leave
        param =""
        param += "DATE(tbl_cl_user_leaves.leave_from_date) <= '%%"+str(today.strftime("%Y-%m-%d"))+"%%'"+"<=DATE(tbl_cl_user_leaves.leave_to_date)"   
        param +=" and sp_users.organization_id = %s group by sp_users.id" % int(college.id)
 
        total_teacher_leave = SpUsers.objects.raw(''' SELECT sp_users.*,tbl_cl_user_leaves.* FROM sp_users left join tbl_cl_user_leaves on tbl_cl_user_leaves.user_id = sp_users.id where sp_users.user_type=1 and {param} '''.format(param=param))

        total_teacher_leave = len(total_teacher_leave)     
   
        dashboard_data_dict['total_student']            = total_student
        dashboard_data_dict['total_teacher']            = total_teacher
        dashboard_data_dict['total_leave_teacher']      = total_teacher_leave
        dashboard_data_dict['today_present_student']    = today_present_student
        dashboard_data_dict['today_absent_student']     = today_absent_student
        dashboard_data_dict['today_present_teacher']    = today_present_teacher
        dashboard_data_dict['today_absent_teacher']     = today_absent_teacher
        dashboard_data_list.append(dashboard_data_dict)
    context = {}
    context['dashboard_data_list']      = dashboard_data_list
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    
    return Response(context, status=HTTP_200_OK)



@csrf_exempt
@api_view(['POST'])
def dashboard(request):
  
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
       return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   
    
    faculty_ids = SpUsers.objects.filter(created_by=request.data.get("user_id")).values_list('id',flat=True)
    
    today_visit = TblHomeVisit.objects.filter(faculty_id__in=faculty_ids).filter(created_at__icontains = datetime.now().today().date()).count()
    total_visits = TblHomeVisit.objects.filter(faculty_id__in= faculty_ids).count()
    total_visit = TblHomeVisit.objects.filter(faculty_id__in= faculty_ids)
    
    faculty_visit = []
    for faculty in total_visit:
        faculty_data = {}
        faculty_data['faculty_name'] = getUserName(faculty.faculty_id)
        faculty_data['today_visit']  = TblHomeVisit.objects.filter(faculty_id=faculty.faculty_id).filter(created_at__icontains = datetime.now().today().date()).count()
        faculty_data['total_visit']  = TblHomeVisit.objects.filter(faculty_id=faculty.faculty_id).count()
        faculty_visit.append(faculty_data) 
    
    date = datetime.now().date()

    current_date = date - timedelta(days=7)
    
  
    graph_from = current_date
    weekly_data = {}
    while current_date<date:
        if current_date.strftime('%A')=="Friday":
            visit_counts = TblHomeVisit.objects.filter(faculty_id__in= faculty_ids,created_at__icontains=current_date).count()
            weekly_data['Friday'] = visit_counts
        elif current_date.strftime('%A')=="Saturday":
            visit_counts = TblHomeVisit.objects.filter(faculty_id__in= faculty_ids,created_at__icontains=current_date).count()
            weekly_data['Saturday'] = visit_counts
        elif current_date.strftime('%A')=="Sunday":
            visit_counts = TblHomeVisit.objects.filter(faculty_id__in= faculty_ids,created_at__icontains=current_date).count()
            weekly_data['Sunday'] = visit_counts
        elif current_date.strftime('%A')=="Monday":
            visit_counts = TblHomeVisit.objects.filter(faculty_id__in= faculty_ids,created_at__icontains=current_date).count()
            weekly_data['Monday'] = visit_counts
        elif current_date.strftime('%A')=="Tuesday":
            visit_counts = TblHomeVisit.objects.filter(faculty_id__in= faculty_ids,created_at__icontains=current_date).count()
            weekly_data['Tuesday'] = visit_counts
        elif current_date.strftime('%A')=="Wednesday":
            visit_counts = TblHomeVisit.objects.filter(faculty_id__in= faculty_ids,created_at__icontains=current_date).count()
            weekly_data['Wednesday'] = visit_counts
        elif current_date.strftime('%A')=="Thursday":
            visit_counts = TblHomeVisit.objects.filter(faculty_id__in= faculty_ids,created_at__icontains=current_date).count()
            weekly_data['Thursday'] = visit_counts
                                                                        
        current_date = current_date + timedelta(days=1) 
  
    graph_to   = current_date - timedelta(days=1)


    context                     = {}

    context['today_visit']      = today_visit
    context['total_visit']      = total_visits
    context['faculty_visit']    = faculty_visit
    context['weekly']           = weekly_data
    context['graph_from']       = graph_from
    context['graph_to']         = graph_to

    context['message']          = "Success"
    context['response_code']    = HTTP_200_OK

    return Response(context, status=HTTP_200_OK)     



@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def getVisitedStudents(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        page  = int(request_data["page"])
    
        try:
            if request_data['type'] == "all":
                total_visit       = TblHomeVisit.objects.order_by('-created_at')
        
            elif request_data['type'] == "today":
                total_visit = TblHomeVisit.objects.filter(created_at__icontains = datetime.now().today().date() ).order_by('-created_at')  
      
        except:
            TblHomeVisit.DoesNotExist
            total_visit = None
        
        total_visit = pagination(page,total_visit)
                
        content_data = []
        for each_visit in total_visit['current_data']:
            visited_data = {}
            
            try:
                student_info = TblStudents.objects.filter(id = each_visit.student_id)
            except TblStudents.DoesNotExist:
                student_info = None
            if student_info:
                if student_info[0].profile_image:
                    visited_data['profile_pic'] = "http://bipe.sortstring.co.in/"+str(student_info[0].profile_image)
                else:
                    visited_data['profile_pic'] = ''
            else:
                visited_data['profile_pic'] = ''       
            
            branch = TblBranch.objects.filter(id = student_info[0].branch_id)
            semester = TblSemester.objects.filter(semester_id = student_info[0].semester_id)
            visited_data['name'] = getStudentName(student_info[0].id)
            visited_data['student_id'] = student_info[0].id
            visited_data['registration_no'] = student_info[0].reg_no
            visited_data['branch'] = branch[0].branch
            visited_data['semester'] = semester[0].sem_name
            visited_data['semester_id'] = student_info[0].semester_id
            visited_data['mother_name'] = student_info[0].mother_name
            visited_data['father_name'] = student_info[0].father_name
            visited_data['phone'] = student_info[0].primary_contact_no
            visited_data['visit_status'] = student_info[0].visit_status
            visited_data['visited_datetime'] = each_visit.created_at
            content_data.append(visited_data)

        context = {}
        context['visited_student']   = content_data
        context['total_pages']       = total_visit['total_pages']
        context['next_page']         = total_visit['next_page']
        context['previous_page']     = total_visit['previous_page']
        context['message']           = "Success"
        context['response_code']     = HTTP_200_OK

    return JsonResponse(context, status=HTTP_200_OK)



import ast
@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def visitedStudentDetail(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        student_id = request_data['student_id']
        try:
            visited_form = TblHomeVisit.objects.filter(student_id = student_id)

            if visited_form is None or visited_form.values() == "" or visited_form.values() == []:
                return Response({"message": "No content available"}, status=HTTP_404_NOT_FOUND)
            form_data = {}
            for info in visited_form:
                student_info = TblStudents.objects.filter(id = info.student_id)
                if student_info[0].profile_image:
                    form_data['profile_pic'] = "http://bipe.sortstring.co.in/"+str(student_info[0].profile_image)
                else:
                    form_data['profile_pic'] = student_info[0].profile_image
                
                branch = TblBranch.objects.filter(id = student_info[0].branch_id)
                semester = TblSemester.objects.filter(semester_id = student_info[0].semester_id)
                address = info.address_hno +", "+ info.address_locality
                # TblNewVillage.objects.filter(id = info.village_id).values('village_name')[0]['village_name']+", "+TblNewTehsil.objects.filter(id = info.tehsil_id).values('tehsil_name')[0]['tehsil_name']+", "+TblNewDistrict.objects.filter(id = info.district_id).values('district_name')[0]['district_name'] +", "+ TblStates.objects.filter(id = info.state_id).values('state_name')[0]['state_name']

                form_data['student_name']       = getStudentName(student_info[0].id)
                form_data['student_id']         = info.registration_no
                form_data['latitude']           = info.latitude
                form_data['longitude']          = info.longitude
                form_data['student_mob']        = student_info[0].primary_contact_no
                form_data['branch']             = branch[0].branch
                form_data['semester']           = semester[0].sem_name
                form_data['relative_mob']       = info.mob_no
                form_data['relative']           = info.guardian_relation
                form_data['father']             = student_info[0].father_name
                form_data['mother']             = student_info[0].mother_name
                form_data['address']            = address
                form_data['visit_status']       = student_info[0].visit_status
                form_data['visit_datetime']     = student_info[0].last_visit_datetime
                form_data['rating']             = info.rating
                all_answers = json.loads(info.answers)
                questionnaire_data = []
                for each_answer in all_answers:
                    answer_dict = {}
                    question_id = each_answer['question_id']
                    each_question = TblQuestionnaire.objects.filter(id = question_id).values('question', 'label')
                    answer_dict['question'] = each_question[0]['question']
                    answer_dict['answered'] = each_answer['is_answered']
                    if each_answer['value'] != "" and (question_id == 6 or question_id == 12):
                        answer_dict['value'] = each_question[0]['label'] + each_answer['value']
                    elif each_answer['value'] != "" and (question_id == 5 or question_id == 13):
                        answer_dict['value'] = each_answer['value']+each_question[0]['label']
                    questionnaire_data.append(answer_dict)
                form_data['answers'] = questionnaire_data
                all_staff = json.loads(info.support_staff)
                staff_data = []
                for each_staff in all_staff:
                    staff_dict = {}
                    staff_dict['id'] = each_staff['id']
                    staff_dict['name'] = each_staff['name']
                    staff_data.append(staff_dict)

                form_data['support_staff'] = staff_data

                if info.visit_audio == "" or info.visit_audio is None:
                    form_data['audio_recording'] = info.visit_audio
                else:
                    form_data['audio_recording'] = ast.literal_eval(info.visit_audio)
                if ast.literal_eval(info.field_report) == "" or ast.literal_eval(info.field_report) is None:
                    form_data['report'] = info.field_report
                else:
                    form_data['report'] = ast.literal_eval(info.field_report)
                if ast.literal_eval(info.selfie_with_parents) == "" or ast.literal_eval(info.selfie_with_parents) is None:
                    form_data['selfie_with_parents'] = info.selfie_with_parents
                else:
                    form_data['selfie_with_parents'] = ast.literal_eval(info.selfie_with_parents)
                form_data['message'] = "Success"
                form_data['response_status'] = HTTP_200_OK

            return Response({"visited_detail":form_data}, status=HTTP_200_OK)
        except Exception as exp:
            return Response({"message": "Error: "+str(exp)},status=HTTP_404_NOT_FOUND)
    else:
        return Response({"meassge": "Method Not Allowed"}, status=HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def visitMapView(request):
    if request.method == 'POST':
        selected_date = request.data.get('selected_date')
        employee_filter = request.data.get('employee_filter')

        try:
            if employee_filter == "":
                all_visits = TblHomeVisit.objects.filter(created_at__icontains = selected_date)
            else:
                all_visits = TblHomeVisit.objects.filter(faculty_id = employee_filter).filter(created_at__icontains = selected_date)
            content = []
            for each_location in all_visits:
                location_data = {}
                branch_name = TblBranch.objects.filter(id = TblStudents.objects.filter(id = each_location.student_id).values('branch_id')[0]['branch_id']).values('abbr')[0]['abbr']
                location_data['student_name'] = getStudentName(each_location.student_id)
                location_data['student_id'] = each_location.student_id
                location_data['registration_no'] = each_location.registration_no
                location_data['visited_by'] = getUserName(each_location.faculty_id)
                location_data['semester'] = TblSemester.objects.filter(semester_id = each_location.semester).values('sem_name')[0]['sem_name']
                location_data['branch'] = branch_name
                location_data['latitude'] = each_location.latitude
                location_data['longitude'] = each_location.longitude
                location_data['visited_on'] = (each_location.created_at).date()
                content.append(location_data)

            all_support_staff = SpUsers.objects.all().order_by('-first_name')
            support_data = []
            for each_support in all_support_staff:
                support_staff_json = {}
                support_staff_json['id'] = each_support.id
                support_staff_json['name'] = getModelColumnById(SpUsers, each_support.id, 'first_name')+" "+getModelColumnById(SpUsers, each_support.id, 'middle_name')+" "+getModelColumnById(SpUsers, each_support.id, 'last_name')
                support_data.append(support_staff_json)

            context = {}
            context['content'] = content
            context['employee'] = support_data
            context['message'] = "Success"
            context['response_status'] = HTTP_200_OK
        except Exception as e:
            return Response({'message': 'Error: '+str(e)})
        return Response(context, status=HTTP_200_OK)
    else:
        return Response({'message': 'Method not allowed'}, status=HTTP_400_BAD_REQUEST)



@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def studentQRData(request):
  
    if request.data.get("reg_no")is None or request.data.get("reg_no") == '':
        return Response({'message': 'student Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    elif not TblStudents.objects.filter(reg_no=request.data.get("reg_no")).exists():
        return Response({'message': 'Registration ID does not exist', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    else:
        reg_no = request.data.get("reg_no")
        student_detail  = TblStudents.objects.filter(reg_no=reg_no).values('id','reg_no', 'first_name','middle_name','last_name','father_name','mother_name','primary_contact_no','profile_image','college_id', 'branch_id', 'semester_id','branch_name', 'is_registered', 'is_mobile_verified').first()
        if student_detail['semester_id']:
            student_detail['semester_name'] = getModelColumnById(TblSemester,student_detail['semester_id'], 'sem_name')
            student_detail['type'] = getModelColumnById(TblSemester,student_detail['semester_id'], 'type')
        else:
            student_detail['semester_name'] = ""
            student_detail['type'] = ""
        current_year = date.today().year

        if datetime.now().month >= 8 :
            acad_start_date = str(current_year)+"-08-01"
            acad_end_date = str(current_year+1)+"-07-31"
        else:
            acad_start_date = str(current_year-1)+"-08-01"
            acad_end_date = str(current_year)+"-07-31"

        total_yearly_days = days_between(acad_end_date, acad_start_date)
        sundays = weekday_count(datetime.strptime(acad_start_date, "%Y-%m-%d"), datetime.strptime(acad_end_date, "%Y-%m-%d"))['Sunday']

        holidays         = SpHolidays.objects.filter(organization_id = student_detail['college_id'], start_date__gte=acad_start_date, end_date__lte=acad_end_date)
        holiday_count = 0
        for each_holiday in holidays:
            if student_detail['branch_id'] in each_holiday.applicable_to['branch'] and student_detail['semester_id'] in each_holiday.applicable_to['semester']:
                holiday_count += days_between(str(each_holiday.end_date), str(each_holiday.start_date))

        total_working_days = total_yearly_days - (sundays + holiday_count)

        attendences = TblAttendance.objects.filter(student_id=student_detail['id'], start_datetime__gte = acad_start_date, end_datetime__lte = acad_end_date).values("student_id", "start_datetime", "end_datetime", "semester_id")
        attendence  = attendences.count()

        all_attendance = TblAttendance.objects.filter(student_id=student_detail['id']).values("student_id","start_datetime", "end_datetime", "semester_id")
   
        if student_detail['branch_id']:
            branch_details = TblBranch.objects.get(id=student_detail['branch_id'])
            if branch_details.total_year is not None:
                tenure = getModelColumnById(TblBranch, student_detail['branch_id'], 'total_year')
            elif branch_details.total_sem is not None:
                tenure = getModelColumnById(TblBranch, student_detail['branch_id'], 'total_sem')
        else:
            tenure = 0

        attendance_summary = []

        semester_obj = []
        for year_sem in range(1, tenure+1):
            year = {}
            semester = {}
            if branch_details.total_year is not None:
                years = year_sem
                each_sem = all_attendance.filter(semester_id = year_sem).count()
    
                if not any([obj.get('year') == str(years)+" Year" for obj in attendance_summary]):
                    year["year"] = "Year " + str(years)
                    year["attendance"] = each_sem
                    # semester['sem_no'] = year_sem
                    # semester['attendance'] = each_sem
                    # semester['total_attendance'] = 150
                    # semester_obj.append(semester)
                # else:
                #     semester['attendance'] = each_sem
                #     semester['total_attendance'] = 150
                #     semester_obj.append(semester)
                year["semester"] = semester_obj
                # if len(semester_obj) == 1:
                #     semester_obj = []
                attendance_summary.append(year)

            elif branch_details.total_sem is not None:
                years = int(math.ceil(year_sem/2))
                each_sem = all_attendance.filter(semester_id = year_sem).count()
    
                if not any([obj.get('year') == str(years)+" Year" for obj in attendance_summary]):
                    year["year"] = "Year " + str(years)
                    semester['sem_no'] = year_sem
                    semester['attendance'] = each_sem
                    semester['total_attendance'] = 150
                    semester_obj.append(semester)
                else:
                    semester['attendance'] = each_sem
                    semester['total_attendance'] = 150
                    semester_obj.append(semester)
                year["semester"] = semester_obj
                if len(semester_obj) == 2:
                    semester_obj = []
                    attendance_summary.append(year)

        context = {}
        context['student_data_list']     = student_detail
        context['attendence']            = attendence
        context['attendance_summary']    = attendance_summary
        context['working_days']          = total_working_days
        context['minimum_attendence']    = 75
        context['message']               = 'Success'
        context['response_code']         = HTTP_200_OK  
        return Response(context, status=HTTP_200_OK)

