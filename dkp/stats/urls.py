from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    # Default view - today's statistics
    path('', views.dashboard, name='dashboard'),

    # Export URLs
    path('export/<str:period>/', views.export_xlsx, name='export_period'),
    path('export/<str:period>/<str:date_str>/', views.export_xlsx, name='export_period_date'),

    # Specific period with optional date
    path('<str:period>/', views.dashboard, name='dashboard_period'),
    path('<str:period>/<str:date_str>/', views.dashboard, name='dashboard_period_date'),
]
