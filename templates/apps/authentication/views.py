from django.http import HttpResponse
from utils import getConfigurationResult
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from ..src.models import *
from django.core import serializers

import sys
import os
sys.path.append(os.getcwd()+'/..')
from sales_port.decorators import unauthenticated_user

@unauthenticated_user
def index(request):
    context = {'logo': getConfigurationResult('logo')}
    try:
            if request.POST:
                username = request.POST['username']
                password = request.POST['password']

                error_count = 0
                if username == '' and password == '':
                    messages.error(request, 'Please enter email id & password', extra_tags='invalid')
                    error_count = error_count+1
                    return redirect('login')
                if username == '':
                    messages.error(request, 'Please enter email id', extra_tags='invalid')
                    error_count = error_count+1
                if password == '':
                    messages.error(request, 'Please enter password', extra_tags='invalid')
                    error_count = error_count+1
                if(error_count > 0):
                    return redirect('login')
                else:
                    user = authenticate(username=username, password=password)
                    # return HttpResponse(user)
                    if user is not None:
                        login(request, user)
                        user_name = user.first_name +' '+ user.middle_name +' '+ user.last_name
                        if 'next' in request.POST:
                            menus = []
                            modules = SpModules.objects.filter(status=1)
                            for module in modules : 
                                current_user = request.user
                                user_favorites = []
                                favorites = SpFavorites.objects.filter(user_id = current_user.id)
                                for favorite in favorites :
                                    temp = {}
                                    temp['favorite'] = favorite.favorite
                                    temp['link'] = favorite.link
                                    user_favorites.append(temp)

                                menu = {}
                                menu['menu'] = module.module_name
                                sub_modules = SpSubModules.objects.filter(module_id=module.id).exclude(link='')
                                submenus = []
                                for sub_module in sub_modules :
                                    sub_menu = {}
                                    sub_menu['sub_menu'] = sub_module.sub_module_name
                                    sub_menu['link'] = sub_module.link
                                    submenus.append(sub_menu)

                                
                                menu['submenus'] = submenus
                                menus.append(menu)

                            request.session['modules'] = menus
                            request.session['favorites'] = user_favorites
                            messages.success(request, 'Hello '+user_name+', Welcome to Sales Port!', extra_tags='success')
                            return redirect(request.POST.get('next'))
                        else:
                            current_user = request.user
                            user_favorites = []
                            favorites = SpFavorites.objects.filter(user_id = current_user.id)
                            for favorite in favorites :
                                temp = {}
                                temp['favorite'] = favorite.favorite
                                temp['link'] = favorite.link
                                user_favorites.append(temp)

                            menus = []
                            modules = SpModules.objects.filter(status=1)
                            for module in modules : 
                                menu = {}
                                menu['menu'] = module.module_name
                                sub_modules = SpSubModules.objects.filter(module_id=module.id).exclude(link='')
                                submenus = []
                                for sub_module in sub_modules :
                                    sub_menu = {}
                                    sub_menu['sub_menu'] = sub_module.sub_module_name
                                    sub_menu['link'] = sub_module.link
                                    submenus.append(sub_menu)

                                
                                menu['submenus'] = submenus
                                menus.append(menu)

                            request.session['modules'] = menus
                            request.session['favorites'] = user_favorites
                            messages.success(request, 'Hello '+user_name+', Welcome to Sales Port!', extra_tags='success')
                            return redirect('/dashboard')
                    else:
                        messages.error(request, 'Invalid email id & password', extra_tags='invalid')
                        return redirect('login')
    except Exception as e:
        print(e)
    return render(request, 'authentication/login.html', context)


def logout_view(request):
    try:
        messages.success(request, 'You have successfully logout!', extra_tags='success')
        logout(request)
    except Exception as e:
        print(e)
    return redirect('login')

def handler404(request, exception):
    return render(request, 'authentication/404.html', status=404)     
   
