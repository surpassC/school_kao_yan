from django.urls import path
from . import views

app_name = 'recommend'

urlpatterns = [
    path('input/', views.recommend_input, name='input'),
    path('results/', views.recommend_results, name='results'),
] 