from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('schools/', views.school_list, name='school_list'),
    path('school/<int:school_id>/', views.school_detail, name='school_detail'),
]