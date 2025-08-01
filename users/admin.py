# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Location, Certification

class CustomUserAdmin(UserAdmin):
    """
    This class customizes the Django admin interface for our CustomUser model.
    It extends the default UserAdmin to include our custom fields.
    """
    # This defines the fields to be displayed in the list view of users.
    list_display = (
        'username', 
        'full_name', 
        'designation', 
        'location', 
        'on_duty', 
        'is_staff'
    )
    
    # This adds filter options to the right sidebar of the user list page.
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'on_duty', 'location', 'department')
    
    # This adds a search bar to the top of the user list page.
    search_fields = ('username', 'full_name', 'email', 'id_number')
    
    # This organizes the fields on the user's detail/edit page into logical sections.
    # We are adding our custom fields to the default UserAdmin fieldsets.
    fieldsets = UserAdmin.fieldsets + (
        ('Employee Details', {
            'fields': (
                'full_name',
                'id_number',
                'department',
                'designation',
                'location',
                'photo',
            ),
        }),
        ('Operational Status', {
            'fields': (
                'shift',
                'on_duty',
                'certifications',
            ),
        }),
        ('System Timestamps', {
            'fields': (
                'login_time',
                'logout_time',
            ),
        }),
    )

# Register the CustomUser model with our customized admin class.
admin.site.register(CustomUser, CustomUserAdmin)

# Register the Location and Certification models so they can be managed in the admin.
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name', 'country')

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    search_fields = ('name',)


