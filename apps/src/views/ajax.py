import sys
import os
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
from utils import *
from django.forms.models import model_to_dict
from datetime import datetime, date,timedelta
import numpy as np
import pickle
import cv2
# import face_recognition
import base64
from PIL import Image
from io import BytesIO
import requests


# order user option View
@login_required
def travelUserOption(request):
    today                   = request.GET['travel_date']
    today                   = datetime.strptime(str(today), '%d/%m/%Y').strftime('%Y-%m-%d')

    response = {}
    options = '<option value="">Select Employee</option>'
    condition = " and created_at LIKE '%%"+str(today)+"%%'" 
    users = SpUsers.objects.raw(''' SELECT id,emp_sap_id, CONCAT(first_name," ",middle_name," ", last_name) as name 
                        FROM sp_users WHERE id in (SELECT user_id FROM sp_user_tracking WHERE 1 group by user_id order by id asc) 
    
                        ''')

    if SpUserTracking.objects.filter().exists() :
        first_order = SpUserTracking.objects.filter().order_by('-id').first()
        user_id = first_order.user_id
    else:
        user_id = 0

    user_details = SpUsers.objects.raw(''' SELECT sp_users.id, CONCAT(sp_users.first_name," ",sp_users.middle_name," ", sp_users.last_name) as name
                    FROM sp_users WHERE sp_users.id = %s ''',[user_id])

    if users:                    
        for user in users :
            if user_details:
                if user.id == user_details[0].id:
                    condition = "selected"
                else:
                    condition = ""
            else:
                condition = ""        
            options += "<option value="+str(user.id)+" "+condition+">"+user.name+"</option>"
    else:
        options = '<option value="">Select Employee</option>'
    response['options'] = options
    return JsonResponse(response)
    
 

# State option View
@login_required
def stateOption(request,country_id):
    # print(country_id)
    response = {}
    options = '<option value="" selected>Select State</option>'
    states = TblStates.objects.filter(country_id=country_id)
    for state in states :
        options += "<option value="+str(state.id)+">"+state.state+"</option>"

    response['options'] = options
    return JsonResponse(response)

# District option View
@login_required
def districtOptions(request,state_id):
    response = {}
    options = '<option value="" selected>Select District</option>'
    districts = TblNewDistrict.objects.filter(state_id=state_id)
    for district in districts :
        options += "<option value="+str(district.id)+">"+district.district_name+"</option>"

    response['options'] = options
    return JsonResponse(response)

# Tehsil option View
@login_required
def tehsilOption(request,district_id):
    response = {}
    options = '<option value="" selected>Select Tehsil</option>'
    tehsils = TblNewTehsil.objects.filter(district_id=district_id)
    for tehsil in tehsils :
        options += "<option value="+str(tehsil.id)+">"+tehsil.tehsil_name+"</option>"

    response['options'] = options
    return JsonResponse(response)



@login_required
def leaveTypeDocumentOption(request,leave_type_id):
    response = {}
    options = '<option value="">Select</option>'
    documents = SpLeaveTypeDocuments.objects.filter(leave_type_id=leave_type_id)
    for document in documents :
        options += "<option value="+str(document.id)+">"+document.document+"</option>"

    response['options'] = options
    return JsonResponse(response)


@login_required
def cityOption(request,state_id):
    response = {}
    options = '<option value="" selected>Select City</option>'
    cities = TblNewDistrict.objects.filter(state_id=state_id)
    for city in cities :
        options += "<option value="+str(city.id)+">"+city.district_name+"</option>"

    response['options'] = options
    return JsonResponse(response)

# option View
@login_required
def getOptionsList(request):
    response = {}
    if request.POST['id'] == 'department_id':
        options = '<option value="" selected>Select Department</option>'
        selects = SpDepartments.objects.filter(organization_id=request.POST['val'])
        for select in selects :
            options += "<option value="+str(select.id)+">"+select.department_name+"</option>"
            response['options'] = options
    elif request.POST['id'] == 'role_id':
        options = '<option value="" selected>Select Role</option>'
        if request.POST['flag'] is not None and request.POST['flag'] =='0':
            selects = SpRoles.objects.filter(department_id=request.POST['val']).filter(id__in=[8,9])
        else:
            selects = SpRoles.objects.filter(department_id=request.POST['val'])
        for select in selects :
            options += "<option value="+str(select.id)+">"+select.role_name+"</option>"
            response['options'] = options
    elif request.POST['id'] == 'town_id':
        options = '<option value="" selected>Select Town</option>'
        selects = SpTowns.objects.filter(zone_id=request.POST['val'])
        for select in selects :
            options += "<option value="+str(select.id)+">"+select.town+"</option>"
            response['options'] = options
            
    return JsonResponse(response)

def updateFavorite(request):
    response = {}
    if request.method == "POST":
        current_user                = request.user
        if 'favorite' not in request.POST or request.POST['favorite'] == "" :
            response['flag']        = False
            response['message']     = "favorite is missing"
        elif 'link' not in request.POST or request.POST['link'] == "" :
            response['flag']        = False
            response['message']     = "link is missing"
        else:
            if SpFavorites.objects.filter(favorite=request.POST['favorite'],link=request.POST['link']).exists() :
                SpFavorites.objects.get(favorite=request.POST['favorite'],link=request.POST['link']).delete()

                current_user = request.user
                user_favorites = []
                favorites = SpFavorites.objects.filter(user_id = current_user.id)
                for favorite in favorites :
                    # print(favorite.favorite)
                    temp = {}
                    temp['favorite'] = favorite.favorite
                    temp['link'] = favorite.link
                    user_favorites.append(temp)

                    request.session['favorites'] = user_favorites

                    template = 'ajax/favorite.html'
                    return render(request,template)
            else:
                favorite                = SpFavorites()
                favorite.user_id        = current_user.id
                favorite.favorite       = request.POST['favorite']
                favorite.link           = request.POST['link']
                favorite.save()
                if favorite.id :

                    current_user = request.user
                    user_favorites = []
                    favorites = SpFavorites.objects.filter(user_id = current_user.id)
                    for favorite in favorites :
                        temp = {}
                        temp['favorite'] = favorite.favorite
                        temp['link'] = favorite.link
                        user_favorites.append(temp)
                    
                    request.session['favorites'] = user_favorites
                    template = 'ajax/favorite.html'
                    return render(request,template)
                else:
                    response['flag']    = False
                    response['message'] = "Failed to save"
    else:
        response['flag']            = False
        response['message']         = "Method not allowed"

    return JsonResponse(response)


def saveWebFirebaseToken(request):
    response = {}
    if request.method == "POST":
        current_user                = request.user
        if 'token' not in request.POST or request.POST['token'] == "" :
            response['flag']        = False
            response['message']     = "token is missing"
        else:
            if not TblUserWebTokens.objects.filter(user_id=current_user.id,token=request.POST['token']).exists() :
                current_user = request.user
                token                = TblUserWebTokens()
                token.user_id        = current_user.id
                token.token          = request.POST['token']
                token.save()

                response['flag']            = True
                response['message']         = "Token has been saved successfully"
            else:
                response['flag']            = True
                response['message']         = "Token already updated"
    else:
        response['flag']            = False
        response['message']         = "Method not allowed"

    return JsonResponse(response)

def globalMenuSearch(request):
    context = {}
    template = 'global-menu-search.html'
    return render(request,template,context)

def stateRouteOptions(request,state_id):
    response = {}
    options = '<option value="all">All</option>'
    routes = SpRoutes.objects.filter(state_id=state_id)
    for route in routes : 
         options += "<option value="+str(route.id)+">"+route.route+"</option>"
    
    response['options'] = options
    return JsonResponse(response)

def routeTownOptions(request):
    options = '<option value="all">All</option>'
    route_ids = request.POST['route_ids'].split(',')
    routes = SpZones.objects.raw(''' select * from sp_routes where id in %s ''',[route_ids])
    for route in routes:
        towns = SpRoutesTown.objects.filter(route_id=route.id).order_by('order_index')
        if towns:
            options += '<optgroup label="' + route.route + '">'
            for town in towns : 
                options += "<option value="+str(town.town_id)+">"+town.town_name+"</option>"
            options += '</optgroup>'

    return HttpResponse(options)

@login_required
def productVariantDetails(request,product_variant_id):
    response = {}
    if SpProductVariants.objects.filter(id=product_variant_id).exists():
        product_variant = SpProductVariants.objects.get(id=product_variant_id)
        response['flag'] = True
        response['product'] = model_to_dict(SpProducts.objects.get(id=product_variant.product_id))
    else:
        response['flag'] = False
        response['flag'] = "Product Variant not found"

    return JsonResponse(response)

@login_required
def getOrderTime(request):    
    shift_id = request.GET['shift_id']
    order_timing = SpWorkingShifts.objects.get(id=shift_id)
    response = {}
    response['flag']          = True
    response['order_timing'] = order_timing.order_timing

    return JsonResponse(response)

@login_required
def getStateTowns(request,state_id):
    response = {}
    if SpStates.objects.filter(id=state_id).exists():
        response['flag'] = True
        towns = list(SpTowns.objects.filter(state_id=state_id).values())
        response['towns'] = towns
    else:
        response['flag'] = False
        response['message'] = "State not found"

    return JsonResponse(response)


@login_required
def getZoneTowns(request,zone_id):
    response = {}
    if SpZones.objects.filter(id=zone_id).exists():
        response['flag'] = True
        towns = list(SpTowns.objects.filter(zone_id=zone_id).values())
        response['towns'] = towns
    else:
        response['flag'] = False
        response['message'] = "Zone not found"

    return JsonResponse(response)

@login_required
def getRouteTowns(request,route_id):
    response = {}
    if SpRoutes.objects.filter(id=route_id).exists():
        response['flag'] = True
        towns = list(SpRoutesTown.objects.filter(route_id=route_id).values())
        response['towns'] = towns
    else:
        response['flag'] = False
        response['message'] = "Route not found"

    return JsonResponse(response)

@login_required
def getCollegeCourseOptions(request,college_id):
    response = {}
    options = '<option value="">Select</option>'
    branches = TblBranch.objects.filter(college_id=college_id)
    for branch in branches :
        options += "<option value="+str(branch.id)+">"+branch.branch+"</option>"

    response['options'] = options
    return JsonResponse(response)

@login_required
def notifyWeb(request):
    response = {}
    title = request.GET.get('title')
    message = request.GET.get('message')
    if 'title' not in request.GET or request.GET['title'] == "":
        response['response'] = "Title missing"
    elif 'message' not in request.GET or request.GET['message'] == "":
        response['response'] = "Message missing" 
    else:
        registration_ids = []
        tokens = TblUserWebTokens.objects.all().values_list('token',flat=True).distinct()
        for token in tokens:
            registration_ids.append(token)
        response['response'] = sendWebPushNotification(title,message,registration_ids)
    
    return JsonResponse(response)


@csrf_exempt
def matchFace(request):
    if request.method == 'POST':
        response = {}
        image = request.POST['image']
        time = datetime.now().strftime("%H-%M-%S")
        im = Image.open(BytesIO(base64.b64decode(image.split('base64,')[1])))
        im.save("media/faceImage/" + str(time) + ".png", 'PNG')

        with open('media/faceEncodes/students.dat', 'rb') as f:
            all_face_encodings = pickle.load(f)
        face_names = list(all_face_encodings.keys())
        face_encodings = np.array(list(all_face_encodings.values()))
        try:
            unknown_image = face_recognition.load_image_file("media/faceImage/" + str(time) + ".png")
            image = cv2.cvtColor(unknown_image, cv2.COLOR_RGB2BGR)
            locations = face_recognition.face_locations(image, model='hog')
            unknown_face = face_recognition.face_encodings(image, locations)
            result = face_recognition.compare_faces(face_encodings, unknown_face, tolerance=0.44)
            names_with_result = list(zip(face_names, result))
            nam = []
            stat = []
            for i in names_with_result:
                if re.search("True", str(i)):
                    name = i[0].split('_')
                    status = i[1]
                    nam.append(name)
                    stat.append(status)
            try:
                response['flag'] = True
                response['name'] = nam[0][0]
                os.remove("media/faceImage/" + str(time) + ".png")
            except:
                response['flag'] = False
                response['name'] = 'Face Not Registered'
                os.remove("media/faceImage/" + str(time) + ".png")

        except ValueError:
            return "There is an  issue in capturing..."

        return JsonResponse(response)
    else:
        return HttpResponse('Method not allowed')


def regEncodes(request):
    if request.method == 'GET':
        students = TblStudents.objects.raw(''' SELECT id,reg_no,college_id,profile_image FROM tbl_students WHERE is_registered = 1 ORDER BY  id DESC
           ''')
        for student in students:
            if student.college_id == 1:
                college_base_url = "http://bipe.sortstring.co.in/"
            elif student.college_id == 2:
                college_base_url = "http://bite.sortstring.co.in/"
            elif student.college_id == 3:
                college_base_url = "http://bip.sortstring.co.in/"
            if student.profile_image:
                student_image = str(college_base_url) + str(student.profile_image)
                imageName = str(str(student.id)+"_"+str(student.reg_no).replace("/", "_"))
                imageName = imageName.replace(".", "_")
                url1 = open("media/faceEncodes/image/" + imageName+".png", 'wb')
                url1.write(requests.get(student_image).content)
                url1.close()

        return HttpResponse("registering")
    else:
        return HttpResponse("Method not allowed")


def trainFile(request):
    if request.method == 'POST':
        filePath = "media/faceEncodes/image/"
        a = os.listdir(filePath)
        all_face_encodings = {}
        for i in a:
            path = (filePath + i)
            imageName = i.split(".")
            nameId = imageName[0].split('_')[0]
            img1 = face_recognition.load_image_file(path)
            all_face_encodings[nameId] = face_recognition.face_encodings(img1)[0]
            with open('media/faceEncodes/sortstring.dat', 'wb') as f:
                pickle.dump(all_face_encodings, f)
                os.remove(path)

        return HttpResponse("registered")

# option View
@login_required
def getBranchList(request):
    response = {}
    options = '<option value="" selected>Branch</option>'
    selects = TblBranch.objects.filter(course_type_id=request.POST['val'], college_id=request.POST['college_id'])
    for select in selects :
        options += "<option value="+str(select.id)+">"+select.branch+"</option>"
        response['options'] = options
            
    return JsonResponse(response)

@login_required
def getAllBranchList(request):
    response = {}
    options = '<option value="" selected>Branch</option>'
    selects = TblBranch.objects.filter(course_type_id=request.POST['val'])
    
    for select in selects :
        if str(select.id) !='':
            options += "<option value="+str(select.id)+">"+select.branch+"</option>"
        else:
            options += "<option value="">Select Branch</option>"
    response['options'] = options
            
    return JsonResponse(response)

# option View
@login_required
def getBranchSemYearList(request):
    response = {}
    options = ''
    selects = TblBranch.objects.get(id=request.POST['val'])
    if selects.total_sem:
        options += '<option value="" selected>Semster</option>'
        for select in range(selects.total_sem) :
            total_sem = int(select)+1
            options += "<option value="+str(total_sem)+">"+str(total_sem)+"</option>"
            response['options'] = options
    elif selects.total_year:
        options += '<option value="" selected>Year</option>'
        for select in range(selects.total_year) :
            total_year = int(select)+1
            options += "<option value="+str(total_year)+">"+str(total_year)+"</option>"
            response['options'] = options        
            
    return JsonResponse(response)

# option View
@login_required
def getStudentRegistrationNo(request):
    response = {}
    last_user_id = request.GET['last_user_id']
    course_id    = request.GET['course_id']
    branch_id    = request.GET['branch_id']
    year_sem_id  = request.GET['year_sem_id']
    section_id   = request.GET['section_id']

    course_code  = getModelColumnById(SpOrganizations, course_id, 'organization_code')
    branch_code  = getModelColumnById(TblBranch, branch_id, 'branch_code')
    reg_no       = str(course_code)+'/'+str(datetime.now().strftime("%Y"))+'/'+str(branch_code)+'/'+str(last_user_id)
    response['reg_no'] = reg_no
            
    return JsonResponse(response)

@login_required
def getOrganizationDepartmentOptions(request,organization_id):
    response = {}
    options = '<option value="">Select</option>'
    departments = SpDepartments.objects.filter(organization_id=organization_id)
    for department in departments :
        options += "<option value="+str(department.id)+">"+department.department_name+"</option>"

    response['options'] = options
    return JsonResponse(response)