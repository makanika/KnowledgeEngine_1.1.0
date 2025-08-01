# assets/forms.py

from django import forms
from django.utils import timezone
from .models import Asset, AssetType, Manufacturer, MaintenanceRecord, AssetSpecification
from users.models import Location, CustomUser

class AssetForm(forms.ModelForm):
    """
    Form for creating and editing assets.
    """
    class Meta:
        model = Asset
        fields = [
            'asset_tag', 'name', 'description',
            'asset_type', 'manufacturer', 'model_number', 'serial_number',
            'location', 'assigned_to', 'status', 'priority',
            'purchase_date', 'installation_date', 'warranty_expiry',
            'last_maintenance', 'next_maintenance', 'notes'
        ]
        widgets = {
            'asset_tag': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., UPS-001'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Main UPS Unit'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detailed description of the asset...'
            }),
            'asset_type': forms.Select(attrs={'class': 'form-control'}),
            'manufacturer': forms.Select(attrs={'class': 'form-control'}),
            'model_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Manufacturer model number'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Serial number'
            }),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'installation_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'warranty_expiry': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'last_maintenance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'next_maintenance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make assigned_to show only active users
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(
            is_active=True
        ).order_by('full_name')
        
        # Add empty option for optional fields
        self.fields['assigned_to'].empty_label = "Not assigned"
        
        # Set required fields
        self.fields['asset_tag'].required = True
        self.fields['name'].required = True
        self.fields['asset_type'].required = True
        self.fields['manufacturer'].required = True
        self.fields['location'].required = True
    
    def clean_asset_tag(self):
        """
        Validate that asset tag is unique and follows naming convention.
        """
        asset_tag = self.cleaned_data['asset_tag'].upper()
        
        # Check if asset tag already exists (excluding current instance if editing)
        existing = Asset.objects.filter(asset_tag=asset_tag)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise forms.ValidationError("An asset with this tag already exists.")
        
        return asset_tag
    
    def clean(self):
        """
        Perform cross-field validation.
        """
        cleaned_data = super().clean()
        purchase_date = cleaned_data.get('purchase_date')
        installation_date = cleaned_data.get('installation_date')
        warranty_expiry = cleaned_data.get('warranty_expiry')
        last_maintenance = cleaned_data.get('last_maintenance')
        next_maintenance = cleaned_data.get('next_maintenance')
        
        # Validate date relationships
        if purchase_date and installation_date:
            if installation_date < purchase_date:
                raise forms.ValidationError("Installation date cannot be before purchase date.")
        
        if purchase_date and warranty_expiry:
            if warranty_expiry < purchase_date:
                raise forms.ValidationError("Warranty expiry cannot be before purchase date.")
        
        if last_maintenance and next_maintenance:
            if next_maintenance <= last_maintenance:
                raise forms.ValidationError("Next maintenance date must be after last maintenance date.")
        
        return cleaned_data

class MaintenanceRecordForm(forms.ModelForm):
    """
    Form for scheduling and recording maintenance.
    """
    class Meta:
        model = MaintenanceRecord
        fields = [
            'asset', 'maintenance_type', 'scheduled_date',
            'description', 'estimated_duration', 'cost'
        ]
        widgets = {
            'asset': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the maintenance work to be performed...'
            }),
            'estimated_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2:30:00 for 2 hours 30 minutes'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Only show active assets
        self.fields['asset'].queryset = Asset.objects.filter(
            status__in=['active', 'maintenance', 'standby']
        ).order_by('asset_tag')
        
        # Set default scheduled date to tomorrow
        if not self.instance.pk:
            tomorrow = timezone.now().date() + timezone.timedelta(days=1)
            self.fields['scheduled_date'].initial = tomorrow
    
    def clean_scheduled_date(self):
        """
        Validate that scheduled date is not in the past.
        """
        scheduled_date = self.cleaned_data['scheduled_date']
        
        if scheduled_date < timezone.now().date():
            raise forms.ValidationError("Scheduled date cannot be in the past.")
        
        return scheduled_date

class AssetSpecificationForm(forms.ModelForm):
    """
    Form for adding/editing asset specifications.
    """
    class Meta:
        model = AssetSpecification
        fields = ['specification_name', 'specification_value', 'unit']
        widgets = {
            'specification_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Power Rating'
            }),
            'specification_value': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 600'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., kVA'
            }),
        }

# Formset for handling multiple specifications
AssetSpecificationFormSet = forms.inlineformset_factory(
    Asset,
    AssetSpecification,
    form=AssetSpecificationForm,
    extra=3,
    can_delete=True
)