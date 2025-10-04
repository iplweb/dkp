from django.urls import path
from . import views

app_name = 'hospital'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),

    # Hospital URLs
    path('hospital/edit/', views.hospital_edit, name='hospital_edit'),

    # Ward URLs
    path('wards/', views.ward_list, name='ward_list'),
    path('wards/create/', views.ward_create, name='ward_create'),
    path('wards/<int:pk>/edit/', views.ward_edit, name='ward_edit'),
    path('wards/<int:pk>/delete/', views.ward_delete, name='ward_delete'),

    # Operating Room URLs
    path('operating-rooms/', views.operating_room_list, name='operating_room_list'),
    path('operating-rooms/create/', views.operating_room_create, name='operating_room_create'),
    path('operating-rooms/<int:pk>/edit/', views.operating_room_edit, name='operating_room_edit'),
    path('operating-rooms/<int:pk>/delete/', views.operating_room_delete, name='operating_room_delete'),
]