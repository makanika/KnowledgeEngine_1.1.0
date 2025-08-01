# assets/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import AssetType, Manufacturer, Asset, AssetSpecification, AssetLog, MaintenanceRecord

@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    """
    Admin configuration for AssetType model.
    """
    list_display = ('name', 'description', 'asset_count')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    def asset_count(self, obj):
        """Display the number of assets of this type"""
        count = obj.asset_set.count()
        if count > 0:
            url = reverse('admin:assets_asset_changelist') + f'?asset_type__id__exact={obj.id}'
            return format_html('<a href="{}">{} assets</a>', url, count)
        return '0 assets'
    asset_count.short_description = 'Assets'

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    """
    Admin configuration for Manufacturer model.
    """
    list_display = ('name', 'website', 'support_contact', 'asset_count')
    search_fields = ('name', 'support_contact')
    list_filter = ('name',)
    ordering = ('name',)
    
    def asset_count(self, obj):
        """Display the number of assets from this manufacturer"""
        count = obj.asset_set.count()
        if count > 0:
            url = reverse('admin:assets_asset_changelist') + f'?manufacturer__id__exact={obj.id}'
            return format_html('<a href="{}">{} assets</a>', url, count)
        return '0 assets'
    asset_count.short_description = 'Assets'

class AssetSpecificationInline(admin.TabularInline):
    """
    Inline admin for asset specifications.
    This allows editing specifications directly on the asset page.
    """
    model = AssetSpecification
    extra = 1
    fields = ('specification_name', 'specification_value', 'unit')

class AssetLogInline(admin.TabularInline):
    """
    Inline admin for asset logs (read-only).
    This shows the asset history on the asset page.
    """
    model = AssetLog
    extra = 0
    readonly_fields = ('event_type', 'description', 'user', 'timestamp', 'old_value', 'new_value')
    fields = ('timestamp', 'event_type', 'description', 'user')
    ordering = ('-timestamp',)
    
    def has_add_permission(self, request, obj=None):
        return False  # Don't allow adding logs manually

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    """
    Admin configuration for Asset model.
    """
    list_display = (
        'asset_tag', 
        'name', 
        'asset_type', 
        'status_badge', 
        'location', 
        'assigned_to', 
        'warranty_status_badge',
        'maintenance_status'
    )
    list_filter = (
        'status', 
        'priority', 
        'asset_type', 
        'manufacturer', 
        'location',
        'assigned_to'
    )
    search_fields = (
        'asset_tag', 
        'name', 
        'serial_number', 
        'model_number',
        'description'
    )
    readonly_fields = ('created_at', 'updated_at', 'warranty_status_display', 'maintenance_due_display')
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'asset_tag',
                'name',
                'description',
                'asset_type',
                'manufacturer',
                'model_number',
                'serial_number'
            )
        }),
        ('Location & Assignment', {
            'fields': (
                'location',
                'assigned_to',
                'status',
                'priority'
            )
        }),
        ('Dates & Warranty', {
            'fields': (
                'purchase_date',
                'installation_date',
                'warranty_expiry',
                'warranty_status_display'
            )
        }),
        ('Maintenance', {
            'fields': (
                'last_maintenance',
                'next_maintenance',
                'maintenance_due_display'
            )
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [AssetSpecificationInline, AssetLogInline]
    
    actions = ['mark_as_active', 'mark_as_maintenance', 'mark_as_faulty']
    
    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'active': 'green',
            'maintenance': 'orange',
            'faulty': 'red',
            'standby': 'blue',
            'decommissioned': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def warranty_status_badge(self, obj):
        """Display warranty status with color coding"""
        status = obj.warranty_status
        colors = {
            'Active': 'green',
            'Expiring Soon': 'orange',
            'Expired': 'red',
            'Unknown': 'gray'
        }
        color = colors.get(status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            status
        )
    warranty_status_badge.short_description = 'Warranty'
    
    def maintenance_status(self, obj):
        """Display maintenance status"""
        if obj.is_maintenance_due:
            return format_html('<span style="color: red; font-weight: bold;">Due</span>')
        elif obj.next_maintenance:
            return format_html('<span style="color: green;">Scheduled</span>')
        return format_html('<span style="color: gray;">Not Scheduled</span>')
    maintenance_status.short_description = 'Maintenance'
    
    def warranty_status_display(self, obj):
        """Read-only field showing warranty status"""
        return obj.warranty_status
    warranty_status_display.short_description = 'Warranty Status'
    
    def maintenance_due_display(self, obj):
        """Read-only field showing if maintenance is due"""
        return 'Yes' if obj.is_maintenance_due else 'No'
    maintenance_due_display.short_description = 'Maintenance Due'
    
    # Admin actions
    def mark_as_active(self, request, queryset):
        """Mark selected assets as active"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} assets marked as active.')
    mark_as_active.short_description = "Mark selected assets as active"
    
    def mark_as_maintenance(self, request, queryset):
        """Mark selected assets as under maintenance"""
        updated = queryset.update(status='maintenance')
        self.message_user(request, f'{updated} assets marked as under maintenance.')
    mark_as_maintenance.short_description = "Mark selected assets as under maintenance"
    
    def mark_as_faulty(self, request, queryset):
        """Mark selected assets as faulty"""
        updated = queryset.update(status='faulty')
        self.message_user(request, f'{updated} assets marked as faulty.')
    mark_as_faulty.short_description = "Mark selected assets as faulty"

@admin.register(AssetSpecification)
class AssetSpecificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for AssetSpecification model.
    """
    list_display = ('asset', 'specification_name', 'specification_value', 'unit')
    list_filter = ('specification_name', 'unit')
    search_fields = ('asset__asset_tag', 'asset__name', 'specification_name', 'specification_value')
    ordering = ('asset__asset_tag', 'specification_name')

@admin.register(AssetLog)
class AssetLogAdmin(admin.ModelAdmin):
    """
    Admin configuration for AssetLog model.
    """
    list_display = ('asset', 'event_type', 'description_short', 'user', 'timestamp')
    list_filter = ('event_type', 'timestamp', 'user')
    search_fields = ('asset__asset_tag', 'asset__name', 'description')
    readonly_fields = ('asset', 'event_type', 'description', 'user', 'timestamp', 'old_value', 'new_value')
    ordering = ('-timestamp',)
    
    def description_short(self, obj):
        """Show shortened description"""
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'
    
    def has_add_permission(self, request):
        return False  # Logs should be created automatically, not manually

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    """
    Admin configuration for MaintenanceRecord model.
    """
    list_display = (
        'asset', 
        'maintenance_type', 
        'status_badge', 
        'scheduled_date', 
        'performed_date',
        'scheduled_by',
        'performed_by',
        'overdue_badge'
    )
    list_filter = (
        'maintenance_type', 
        'status', 
        'scheduled_date',
        'performed_date',
        'scheduled_by',
        'performed_by'
    )
    search_fields = (
        'asset__asset_tag', 
        'asset__name', 
        'description',
        'work_performed'
    )
    readonly_fields = ('created_at', 'updated_at', 'is_overdue_display')
    
    fieldsets = (
        ('Asset & Type', {
            'fields': ('asset', 'maintenance_type', 'status')
        }),
        ('Scheduling', {
            'fields': (
                'scheduled_date',
                'scheduled_by',
                'estimated_duration'
            )
        }),
        ('Execution', {
            'fields': (
                'performed_date',
                'performed_by',
                'actual_duration'
            )
        }),
        ('Work Details', {
            'fields': (
                'description',
                'work_performed',
                'parts_used',
                'cost'
            )
        }),
        ('Follow-up', {
            'fields': (
                'next_maintenance_date',
                'notes'
            )
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'is_overdue_display'),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'scheduled': 'blue',
            'in_progress': 'orange',
            'completed': 'green',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def overdue_badge(self, obj):
        """Display if maintenance is overdue"""
        if obj.is_overdue:
            return format_html('<span style="color: red; font-weight: bold;">OVERDUE</span>')
        return ''
    overdue_badge.short_description = 'Overdue'
    
    def is_overdue_display(self, obj):
        """Read-only field showing if maintenance is overdue"""
        return 'Yes' if obj.is_overdue else 'No'
    is_overdue_display.short_description = 'Is Overdue'

# Customize the admin site header
admin.site.site_header = "Knowledge Engine - Asset Management"
admin.site.site_title = "Knowledge Engine Admin"
admin.site.index_title = "Asset Management System"