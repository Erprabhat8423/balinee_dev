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

# State option View
@login_required
def stateOption(request,country_id):
    response = {}
    options = '<option value="" selected>Select State</option>'
    states = SpStates.objects.filter(country_id=country_id)
    for state in states :
        options += "<option value="+str(state.id)+">"+state.state+"</option>"

    response['options'] = options
    return JsonResponse(response)

# State option View
@login_required
def cityOption(request,state_id):
    response = {}
    options = '<option value="" selected>Select City</option>'
    cities = SpCities.objects.filter(state_id=state_id)
    for city in cities :
        options += "<option value="+str(city.id)+">"+city.city+"</option>"

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
                    print(favorite.favorite)
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

def globalMenuSearch(request):
    context = {}
    template = 'global-menu-search.html'
    return render(request,template,context)