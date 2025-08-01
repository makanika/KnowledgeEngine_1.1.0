# assets/urls.py

from django.urls import path
from . import views

# URL patterns for the Assets application
# These will be prefixed with 'assets/' when included in the main project URLs

urlpatterns = [
    # Asset list and dashboard views
    path('', views.asset_dashboard, name='asset_dashboard'),
    path('list/', views.asset_list, name='asset_list'),
    path('list/<str:asset_type>/', views.asset_list_by_type, name='asset_list_by_type'),
    
    # Asset management views (specific paths first)
    path('add/', views.asset_add, name='asset_add'),
    path('maintenance/schedule/', views.maintenance_schedule, name='maintenance_schedule'),
    
    # User-asset integration
    path('user/<int:user_id>/', views.user_assets, name='user_assets'),
    
    # API endpoints
    path('api/status-summary/', views.asset_status_summary, name='asset_status_summary'),
    
    # Asset detail views (dynamic paths last)
    path('<str:asset_tag>/', views.asset_detail, name='asset_detail'),
    path('<str:asset_tag>/edit/', views.asset_edit, name='asset_edit'),
    path('<str:asset_tag>/assign/', views.asset_assign, name='asset_assign'),
    path('<str:asset_tag>/maintenance/', views.asset_maintenance, name='asset_maintenance'),
]