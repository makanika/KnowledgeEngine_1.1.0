# assets/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from .models import Asset, AssetType, Manufacturer, MaintenanceRecord, AssetLog
from .forms import AssetForm, MaintenanceRecordForm
from users.models import CustomUser

@login_required
def asset_dashboard(request):
    """
    Main dashboard showing asset overview and statistics.
    """
    # Get summary statistics
    total_assets = Asset.objects.count()
    active_assets = Asset.objects.filter(status='active').count()
    maintenance_assets = Asset.objects.filter(status='maintenance').count()
    faulty_assets = Asset.objects.filter(status='faulty').count()
    
    # Assets by type
    assets_by_type = AssetType.objects.annotate(
        asset_count=Count('asset')
    ).order_by('-asset_count')
    
    # Recent maintenance
    recent_maintenance = MaintenanceRecord.objects.select_related(
        'asset', 'performed_by'
    ).order_by('-performed_date')[:5]
    
    # Assets needing maintenance
    maintenance_due = Asset.objects.filter(
        next_maintenance__lte=timezone.now().date()
    ).exclude(status='decommissioned')[:5]
    
    # Recent asset changes
    recent_logs = AssetLog.objects.select_related(
        'asset', 'user'
    ).order_by('-timestamp')[:10]
    
    context = {
        'total_assets': total_assets,
        'active_assets': active_assets,
        'maintenance_assets': maintenance_assets,
        'faulty_assets': faulty_assets,
        'assets_by_type': assets_by_type,
        'recent_maintenance': recent_maintenance,
        'maintenance_due': maintenance_due,
        'recent_logs': recent_logs,
    }
    
    return render(request, 'assets/dashboard.html', context)

@login_required
def asset_list(request):
    """
    Display a list of all assets with filtering options.
    """
    assets = Asset.objects.select_related(
        'asset_type', 'manufacturer', 'location', 'assigned_to'
    ).order_by('asset_tag')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        assets = assets.filter(status=status_filter)
    
    # Filter by asset type
    type_filter = request.GET.get('type')
    if type_filter:
        assets = assets.filter(asset_type__name=type_filter)
    
    # Filter by location
    location_filter = request.GET.get('location')
    if location_filter:
        assets = assets.filter(location__name=location_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        assets = assets.filter(
            Q(asset_tag__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Get filter options for the template
    asset_types = AssetType.objects.all()
    locations = Asset.objects.values_list('location__name', flat=True).distinct()
    
    context = {
        'assets': assets,
        'asset_types': asset_types,
        'locations': locations,
        'current_status': status_filter,
        'current_type': type_filter,
        'current_location': location_filter,
        'search_query': search_query,
    }
    
    return render(request, 'assets/asset_list.html', context)

@login_required
def asset_list_by_type(request, asset_type):
    """
    Display assets filtered by a specific type.
    """
    asset_type_obj = get_object_or_404(AssetType, name=asset_type)
    assets = Asset.objects.filter(asset_type=asset_type_obj).select_related(
        'manufacturer', 'location', 'assigned_to'
    ).order_by('asset_tag')
    
    context = {
        'assets': assets,
        'asset_type': asset_type_obj,
        'page_title': f'{asset_type} Assets',
    }
    
    return render(request, 'assets/asset_list_by_type.html', context)

@login_required
def asset_detail(request, asset_tag):
    """
    Display detailed information about a specific asset.
    """
    asset = get_object_or_404(Asset, asset_tag=asset_tag)
    
    # Get related data
    specifications = asset.specifications.all()
    maintenance_records = asset.maintenance_records.order_by('-scheduled_date')[:10]
    recent_logs = asset.logs.order_by('-timestamp')[:10]
    
    context = {
        'asset': asset,
        'specifications': specifications,
        'maintenance_records': maintenance_records,
        'recent_logs': recent_logs,
    }
    
    return render(request, 'assets/asset_detail.html', context)

@login_required
def asset_edit(request, asset_tag):
    """
    Edit an existing asset.
    """
    asset = get_object_or_404(Asset, asset_tag=asset_tag)
    
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            # Save the asset
            updated_asset = form.save()
            
            # Create a log entry
            AssetLog.objects.create(
                asset=updated_asset,
                event_type='updated',
                description=f'Asset information updated',
                user=request.user
            )
            
            messages.success(request, f'Asset {asset.asset_tag} updated successfully.')
            return redirect('asset_detail', asset_tag=asset.asset_tag)
    else:
        form = AssetForm(instance=asset)
    
    context = {
        'form': form,
        'asset': asset,
        'page_title': f'Edit {asset.asset_tag}',
    }
    
    return render(request, 'assets/asset_form.html', context)

@login_required
def asset_add(request):
    """
    Add a new asset.
    """
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            # Save the asset
            asset = form.save()
            
            # Create a log entry
            AssetLog.objects.create(
                asset=asset,
                event_type='created',
                description=f'Asset created',
                user=request.user
            )
            
            messages.success(request, f'Asset {asset.asset_tag} created successfully.')
            return redirect('asset_detail', asset_tag=asset.asset_tag)
    else:
        form = AssetForm()
    
    context = {
        'form': form,
        'page_title': 'Add New Asset',
    }
    
    return render(request, 'assets/asset_form.html', context)

@login_required
def asset_maintenance(request, asset_tag):
    """
    Display maintenance information for a specific asset.
    """
    asset = get_object_or_404(Asset, asset_tag=asset_tag)
    maintenance_records = asset.maintenance_records.order_by('-scheduled_date')
    
    context = {
        'asset': asset,
        'maintenance_records': maintenance_records,
    }
    
    return render(request, 'assets/asset_maintenance.html', context)

@login_required
def maintenance_schedule(request):
    """
    Schedule new maintenance for an asset.
    """
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.scheduled_by = request.user
            maintenance.save()
            
            # Create a log entry
            AssetLog.objects.create(
                asset=maintenance.asset,
                event_type='maintenance_scheduled',
                description=f'{maintenance.get_maintenance_type_display()} scheduled for {maintenance.scheduled_date}',
                user=request.user
            )
            
            messages.success(request, f'Maintenance scheduled for {maintenance.asset.asset_tag}.')
            return redirect('asset_detail', asset_tag=maintenance.asset.asset_tag)
    else:
        form = MaintenanceRecordForm()
    
    context = {
        'form': form,
        'page_title': 'Schedule Maintenance',
    }
    
    return render(request, 'assets/maintenance_form.html', context)

@login_required
def asset_status_summary(request):
    """
    API endpoint returning asset status summary as JSON.
    This can be used for dashboard widgets or AJAX updates.
    """
    summary = {
        'total': Asset.objects.count(),
        'active': Asset.objects.filter(status='active').count(),
        'maintenance': Asset.objects.filter(status='maintenance').count(),
        'faulty': Asset.objects.filter(status='faulty').count(),
        'standby': Asset.objects.filter(status='standby').count(),
        'decommissioned': Asset.objects.filter(status='decommissioned').count(),
    }
    
    return JsonResponse(summary)

@login_required
def asset_assign(request, asset_tag):
    """
    Assign or reassign an asset to a user.
    """
    asset = get_object_or_404(Asset, asset_tag=asset_tag)
    
    if request.method == 'POST':
        user_id = request.POST.get('assigned_to')
        old_assignee = asset.assigned_to
        
        if user_id:
            new_assignee = get_object_or_404(CustomUser, id=user_id)
            asset.assigned_to = new_assignee
        else:
            asset.assigned_to = None
            new_assignee = None
        
        asset.save()
        
        # Create log entry
        if old_assignee != new_assignee:
            old_name = old_assignee.full_name if old_assignee else "Unassigned"
            new_name = new_assignee.full_name if new_assignee else "Unassigned"
            
            AssetLog.objects.create(
                asset=asset,
                event_type='assignment_change',
                description=f'Asset reassigned from {old_name} to {new_name}',
                user=request.user,
                old_value=old_name,
                new_value=new_name
            )
            
            if new_assignee:
                messages.success(request, f'Asset {asset.asset_tag} assigned to {new_assignee.full_name}.')
            else:
                messages.success(request, f'Asset {asset.asset_tag} unassigned.')
        
        return redirect('asset_detail', asset_tag=asset.asset_tag)
    
    # Get all active users for assignment
    users = CustomUser.objects.filter(is_active=True).order_by('full_name')
    
    context = {
        'asset': asset,
        'users': users,
    }
    
    return render(request, 'assets/asset_assign.html', context)

@login_required
def user_assets(request, user_id):
    """
    Display all assets assigned to a specific user.
    """
    user = get_object_or_404(CustomUser, id=user_id)
    assets = Asset.objects.filter(assigned_to=user).select_related(
        'asset_type', 'manufacturer', 'location'
    ).order_by('asset_tag')
    
    # Get maintenance due for this user's assets
    maintenance_due = assets.filter(
        next_maintenance__lte=timezone.now().date()
    ).exclude(status='decommissioned')
    
    context = {
        'profile_user': user,
        'assets': assets,
        'maintenance_due': maintenance_due,
    }
    
    return render(request, 'assets/user_assets.html', context)