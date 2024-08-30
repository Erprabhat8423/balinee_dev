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
def ajaxLeaveTypeList(request):
    context = {}
    context['leave_types'] = SpLeaveTypes.objects.all()
    template = 'master/leave-holidays/ajax-leave-type-list.html'
    return render(request, template, context)


@login_required
def getLeaveTypeDocuments(request,leave_type_id):
    response = {}
    if SpLeaveTypes.objects.filter(id=leave_type_id).exists():
        response['flag'] = True
        documents = list(SpLeaveTypeDocuments.objects.filter(leave_type_id=leave_type_id).values())
        response['documents'] = documents
    else:
        response['flag'] = False
        response['message'] = "Leave type not found"

    return JsonResponse(response)

@login_required
def ajaxHolidayTypeList(request):
    context = {}
    context['holiday_types'] = SpHolidayTypes.objects.all()
    template = 'master/leave-holidays/ajax-holiday-type-list.html'
    return render(request, template, context)


@login_required
def addLeaveType(request):
    if request.method == "POST":
        response = {}
        print(request.POST)
        if SpLeaveTypes.objects.filter(leave_type=clean_data(request.POST['leave_type_name'])).exists() :
            response['flag'] = False
            response['message'] = "Leave type name already exists."
        else:
            leave_type = SpLeaveTypes()
            leave_type.leave_type = clean_data(request.POST['leave_type_name'])
            leave_type.alias = clean_data(request.POST['leave_type_alias'])
            leave_type.status = 1
            leave_type.save()
            if leave_type.id :
                documents = request.POST.getlist('document[]')
                for id, val in enumerate(documents):
                    document = SpLeaveTypeDocuments()
                    document.leave_type_id = leave_type.id
                    document.document = clean_data(documents[id])
                    document.save()

            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        return JsonResponse(response)

    else:
        context = {}
        template = 'master/leave-holidays/add-leave-type.html'
        return render(request, template, context)

@login_required
def editLeaveType(request,leave_type_id):
    if request.method == "POST":
        response = {}
        leave_type_id = request.POST['leave_type_id']
        if SpLeaveTypes.objects.filter(leave_type=clean_data(request.POST['leave_type_name'])).exclude(id=leave_type_id).exists() :
            response['flag'] = False
            response['message'] = "Leave type name already exists."
        else:
            leave_type = SpLeaveTypes.objects.get(id=leave_type_id)
            leave_type.leave_type = clean_data(request.POST['leave_type_name'])
            leave_type.alias = clean_data(request.POST['leave_type_alias'])
            leave_type.status = 1
            leave_type.save()

            # delete old documents
            SpLeaveTypeDocuments.objects.filter(leave_type_id=leave_type_id).delete()

            if leave_type.id :
                documents = request.POST.getlist('document[]')
                for id, val in enumerate(documents):
                    document = SpLeaveTypeDocuments()
                    document.leave_type_id = leave_type.id
                    document.document = clean_data(documents[id])
                    document.save()

            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['leave_type'] = SpLeaveTypes.objects.get(pk=leave_type_id)
        context['leave_type_documents'] = SpLeaveTypeDocuments.objects.filter(leave_type_id=leave_type_id)

        template = 'master/leave-holidays/edit-leave-type.html'
        return render(request, template, context)


@login_required
def updateLeaveTypeStatus(request,leave_type_id):
    context = {}
    if SpLeaveTypes.objects.filter(id=leave_type_id).exists():
        leave_type = SpLeaveTypes.objects.get(id=leave_type_id)
        if int(leave_type.status) == 1:
            leave_type.status = 0
            leave_type.save()
        else:
            leave_type.status = 1
            leave_type.save()

        context['flag'] = True
        context['message'] = "Record updated successfully."
    else:
        context['flag'] = False
        context['message'] = "Record not found."
    return JsonResponse(context)


@login_required
def addHolidayType(request):
    if request.method == "POST":
        response = {}
        if SpHolidayTypes.objects.filter(holiday_type=clean_data(request.POST['holiday_type_name'])).exists() :
            response['flag'] = False
            response['message'] = "Holiday type already exists."
        else:
            holiday_type = SpHolidayTypes()
            holiday_type.holiday_type = clean_data(request.POST['holiday_type_name'])
            holiday_type.status = 1
            holiday_type.save()
            if holiday_type.id :
                response['flag'] = True
                response['message'] = "Record has been saved successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        template = 'master/leave-holidays/add-holiday-type.html'
        return render(request, template, context)

@login_required
def editHolidayType(request,holiday_type_id):
    if request.method == "POST":
        response = {}
        holiday_type_id = request.POST['holiday_type_id']
        if SpHolidayTypes.objects.filter(holiday_type=clean_data(request.POST['holiday_type_name'])).exclude(id=holiday_type_id).exists() :
            response['flag'] = False
            response['message'] = "Holiday type already exists."
        else:
            holiday_type = SpHolidayTypes.objects.get(id=holiday_type_id)
            holiday_type.holiday_type = clean_data(request.POST['holiday_type_name'])
            holiday_type.status = 1
            holiday_type.save()
            if holiday_type.id :
                response['flag'] = True
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save record."

        return JsonResponse(response)
    else:
        context = {}
        context['holiday_type'] = SpHolidayTypes.objects.get(pk=holiday_type_id)
        template = 'master/leave-holidays/edit-holiday-type.html'
        return render(request, template, context)

@login_required
def updateHolidayTypeStatus(request,holiday_type_id):
    context = {}
    if SpHolidayTypes.objects.filter(id=holiday_type_id).exists():
        holiday_type = SpHolidayTypes.objects.get(id=holiday_type_id)
        if int(holiday_type.status) == 1:
            holiday_type.status = 0
            holiday_type.save()
        else:
            holiday_type.status = 1
            holiday_type.save()

        context['flag'] = True
        context['message'] = "Record updated successfully."
    else:
        context['flag'] = False
        context['message'] = "Record not found."
    return JsonResponse(context)