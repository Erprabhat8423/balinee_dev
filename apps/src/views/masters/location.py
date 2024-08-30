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
from django.forms.models import model_to_dict

@login_required
def ajaxZoneList(request):
    context = {}
    context['zones'] = SpZones.objects.all()
    template = 'master/location/ajax-zone-list.html'
    return render(request, template, context)

@login_required
def ajaxTownList(request):
    context = {}
    context['towns'] = SpTowns.objects.all()
    template = 'master/location/ajax-town-list.html'
    return render(request, template, context)


@login_required
def ajaxRouteList(request):
    context = {}
    context['routes'] = SpRoutes.objects.all()
    template = 'master/location/ajax-route-list.html'
    return render(request, template, context)


@login_required
def addZone(request):
    if request.method == "POST":
        response = {}
        if SpZones.objects.filter(zone=request.POST['zone_name']).exists() :
            response['flag'] = False
            response['message'] = "Zone already exists."
        else:
            zone = SpZones()
            zone.state_id = request.POST['state_id']
            zone.state_name = getModelColumnById(SpStates,request.POST['state_id'],'state')
            zone.zone = request.POST['zone_name']
            zone.save()
            if zone.id :
                towns = request.POST.getlist('town[]')
                for id, val in enumerate(towns):
                    town = SpTowns.objects.get(id=towns[id])
                    town.zone_id = zone.id
                    town.zone_name = zone.zone
                    town.save()

            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['states'] = SpStates.objects.all()
        context['towns'] = SpTowns.objects.filter(zone_id=None)
        template = 'master/location/add-zone.html'
        return render(request, template, context)


@login_required
def addTown(request):
    if request.method == "POST":
        response = {}
        if SpTowns.objects.filter(town=request.POST['town_name']).exists() :
            response['flag'] = False
            response['message'] = "Town name already exists."
        else:
            town = SpTowns()
            if request.POST['zone_id'] != "" :
                town.zone_id = request.POST['zone_id']
                town.zone_name = getModelColumnById(SpZones,request.POST['zone_id'],'zone')
            else:
                town.zone_id = None
                town.zone_name = None
                
            town.state_id = request.POST['state_id']
            town.state_name = getModelColumnById(SpStates,request.POST['state_id'],'state')
            town.town = request.POST['town_name']
            town.save()

            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['states'] = SpStates.objects.all()
        context['zones'] = SpZones.objects.all()
        template = 'master/location/add-town.html'
        return render(request, template, context)




@login_required
def addRoute(request):
    if request.method == "POST":
        response = {}
        if SpRoutes.objects.filter(route=request.POST['route_name']).exists() :
            response['flag'] = False
            response['message'] = "Route name already exists."
        else:
            route = SpRoutes()
            route.state_id = request.POST['state_id']
            route.state_name = getModelColumnById(SpStates,request.POST['state_id'],'state')
            route.route = request.POST['route_name']
            route.save()
            if route.id :
                towns = request.POST.getlist('town[]') 
                orders = request.POST.getlist('order[]') 

                for id, val in enumerate(towns):
                    route_town = SpRoutesTown()
                    route_town.route_id = route.id
                    route_town.route_name = request.POST['route_name']
                    route_town.town_id = towns[id]
                    route_town.town_name = getModelColumnById(SpTowns,towns[id],'town')
                    route_town.order_index = orders[id]
                    route_town.save()

            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['states'] = SpStates.objects.all()
        context['towns'] = SpTowns.objects.all()
        template = 'master/location/add-route.html'
        return render(request, template, context)



