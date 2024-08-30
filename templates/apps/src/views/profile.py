import sys
import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponse
from django.apps import apps
from utils import getConfigurationResult



# Create your views here.
#Home View
@login_required
def index(request):
        return render(request, 'profile/home.html')
