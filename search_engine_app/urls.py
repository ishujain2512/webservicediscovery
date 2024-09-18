from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('results/', views.results, name='results'),
    path('result_detail/', views.result_detail, name='result_detail'),]
handler500 = views.error_page
