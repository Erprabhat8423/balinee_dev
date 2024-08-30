from django.urls import path,re_path
from ..views.api.logistic_api import *

urlpatterns = [
    path('api/logistic/login', login),
    path('api/logistic/today-orders', todayOrders),
    path('api/logistic/save-tracking-data', saveTracking),
    path('api/logistic/send-order-otp', sendOrderOtp),
    path('api/logistic/deliver-order', deliverOrder),

]