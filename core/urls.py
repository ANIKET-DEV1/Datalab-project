# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('', views.register, name='register'),
    path('upload/', views.upload_csv, name='upload'),
    path('preview/', views.preview_csv, name='preview'),
    path('stats/', views.data_stats, name='analyze'),
    path('visualizer/', views.data_visualizer, name='visualizer'),
    path('clean/', views.clean_data, name='clean'),
    path('export/', views.export_data, name='export'),
]
