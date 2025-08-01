# assets/utils.py

from django.utils import timezone
from django.db.models import Q
from .models import Asset, AssetLog, MaintenanceRecord

def get_asset_health_summary():
    """
    Get a comprehensive health summary of all assets.
    This will be useful for incident management integration.
    """
    total_assets = Asset.objects.count()
    
    # Status breakdown
    status_summary = {
        'active': Asset.objects.filter(status='active').count(),
        'maintenance': Asset.objects.filter(status='maintenance').count(),
        'faulty': Asset.objects.filter(status='faulty').count(),
        'standby': Asset.objects.filter(status='standby').count(),
        'decommissioned': Asset.objects.filter(status='decommissioned').count(),
    }
    
    # Critical assets (high priority + faulty or maintenance due)
    critical_issues = Asset.objects.filter(
        Q(priority='critical') & 
        (Q(status='faulty') | Q(next_maintenance__lte=timezone.now().date()))
    ).exclude(status='decommissioned')
    
    # Maintenance statistics
    overdue_maintenance = Asset.objects.filter(
        next_maintenance__lt=timezone.now().date(),
        status__in=['active', 'standby']
    ).count()
    
    due_this_week = Asset.objects.filter(
        next_maintenance__range=[
            timezone.now().date(),
            timezone.now().date() + timezone.timedelta(days=7)
        ]
    ).count()
    
    return {
        'total_assets': total_assets,
        'status_summary': status_summary,
        'critical_issues': critical_issues,
        'overdue_maintenance': overdue_maintenance,
        'due_this_week': due_this_week,
        'health_percentage': round((status_summary['active'] / total_assets * 100) if total_assets > 0 else 0, 1)
    }

def get_user_asset_summary(user):
    """
    Get asset summary for a specific user.
    Useful for user dashboards and incident assignment.
    """
    user_assets = Asset.objects.filter(assigned_to=user)
    
    return {
        'total_assigned': user_assets.count(),
        'by_status': {
            'active': user_assets.filter(status='active').count(),
            'maintenance': user_assets.filter(status='maintenance').count(),
            'faulty': user_assets.filter(status='faulty').count(),
        },
        'maintenance_due': user_assets.filter(
            next_maintenance__lte=timezone.now().date()
        ).exclude(status='decommissioned').count(),
        'critical_assets': user_assets.filter(priority='critical').count(),
    }

def log_asset_event(asset, event_type, description, user, old_value=None, new_value=None):
    """
    Centralized function for logging asset events.
    This ensures consistent logging across the application.
    """
    return AssetLog.objects.create(
        asset=asset,
        event_type=event_type,
        description=description,
        user=user,
        old_value=old_value or '',
        new_value=new_value or ''
    )

def get_asset_incident_context(asset):
    """
    Prepare asset context for incident management.
    This will be used when the incident management system is implemented.
    """
    # Get recent maintenance
    recent_maintenance = MaintenanceRecord.objects.filter(
        asset=asset
    ).order_by('-performed_date')[:3]
    
    # Get recent logs
    recent_logs = AssetLog.objects.filter(
        asset=asset
    ).order_by('-timestamp')[:5]
    
    # Get specifications that might be relevant for incidents
    critical_specs = asset.specifications.filter(
        specification_name__in=[
            'Power Rating', 'Voltage', 'Current', 'Temperature',
            'Pressure', 'Flow Rate', 'Capacity'
        ]
    )
    
    return {
        'asset': asset,
        'recent_maintenance': recent_maintenance,
        'recent_logs': recent_logs,
        'critical_specs': critical_specs,
        'assigned_user': asset.assigned_to,
        'location': asset.location,
        'is_critical': asset.priority == 'critical',
        'maintenance_due': asset.is_maintenance_due,
        'warranty_status': asset.warranty_status,
    }

def find_related_assets(asset, radius_km=None):
    """
    Find assets related to the given asset.
    This can be used for impact analysis in incident management.
    """
    related_assets = Asset.objects.filter(
        location=asset.location,
        asset_type=asset.asset_type
    ).exclude(id=asset.id)
    
    # Also include assets assigned to the same user
    if asset.assigned_to:
        user_assets = Asset.objects.filter(
            assigned_to=asset.assigned_to
        ).exclude(id=asset.id)
        
        # Combine querysets
        related_assets = related_assets.union(user_assets)
    
    return related_assets

def get_maintenance_recommendations(asset):
    """
    Generate maintenance recommendations based on asset history and status.
    """
    recommendations = []
    
    # Check if maintenance is overdue
    if asset.is_maintenance_due:
        recommendations.append({
            'type': 'urgent',
            'message': f'Maintenance is overdue for {asset.asset_tag}',
            'action': 'Schedule immediate maintenance'
        })
    
    # Check warranty status
    if asset.warranty_status == 'Expired':
        recommendations.append({
            'type': 'warning',
            'message': 'Warranty has expired',
            'action': 'Consider extended warranty or replacement planning'
        })
    elif asset.warranty_status == 'Expiring Soon':
        recommendations.append({
            'type': 'info',
            'message': 'Warranty expiring soon',
            'action': 'Review warranty renewal options'
        })
    
    # Check for frequent issues
    recent_issues = AssetLog.objects.filter(
        asset=asset,
        event_type__in=['incident_reported', 'status_change'],
        timestamp__gte=timezone.now() - timezone.timedelta(days=90)
    ).count()
    
    if recent_issues >= 3:
        recommendations.append({
            'type': 'warning',
            'message': f'{recent_issues} issues reported in the last 90 days',
            'action': 'Consider root cause analysis or replacement'
        })
    
    return recommendations