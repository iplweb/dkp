from django.urls import path
from . import views

app_name = 'comms'

urlpatterns = [
    path('', views.role_selection, name='role_selection'),
    path('select_location/<str:role_name>/', views.select_location, name='select_location'),
    path('select_ward_for_anesthetist/<int:or_id>/', views.select_ward_for_anesthetist, name='select_ward_for_anesthetist'),
    path('communication/<str:role_name>/<str:location_type>/<int:location_id>/', views.communication, name='communication'),
    path('communication/<str:role_name>/or/<int:or_id>/ward/<int:ward_id>/', views.communication_anesthetist, name='communication_anesthetist'),
    path('send_message/', views.send_message, name='send_message'),
    path('acknowledge_message/', views.acknowledge_message, name='acknowledge_message'),
    path('acknowledge_all_messages/', views.acknowledge_all_messages, name='acknowledge_all_messages'),
]