from django import template
from ...src.models import *

register = template.Library()

@register.simple_tag
def checkedFavorite(favorite,link):
    if SpFavorites.objects.filter(favorite=favorite,link=link).exists() :
        return "checked"
    else: 
        return ""

@register.simple_tag
def get_workflow(role_id,sub_module_id,permission_id):
    role_permission = SpRolePermissions.objects.get(role_id=role_id,sub_module_id=sub_module_id,permission_id=permission_id)
    return role_permission.workflow

@register.simple_tag
def get_workflow_count(role_id,sub_module_id,permission_id):
    role_permission_workflow = SpRoleWorkflowPermissions.objects.filter(role_id=role_id,sub_module_id=sub_module_id,permission_id=permission_id).count()
    return role_permission_workflow

@register.simple_tag
def sum(num1, num2):
    return num1 + num2

@register.simple_tag
def subtract(value, arg):
    return value - arg