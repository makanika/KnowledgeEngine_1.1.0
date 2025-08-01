# assets/models.py

from django.db import models
from django.utils import timezone
from users.models import CustomUser, Location

class AssetType(models.Model):
    """
    Represents different categories or types of assets, e.g., 'UPS', 'Generator', 'IAC'.
    This helps in classifying assets and can be used for filtering and reporting.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Name of the asset type (e.g., UPS, Generator, IAC)")
    description = models.TextField(blank=True, help_text="A brief description of this asset type")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Asset Type"
        verbose_name_plural = "Asset Types"

    def __str__(self):
        return self.name

class Manufacturer(models.Model):
    """
    Stores information about the manufacturers of the assets.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Name of the manufacturer (e.g., APC, Caterpillar, Schneider)")
    website = models.URLField(blank=True, null=True, help_text="Official website of the manufacturer")
    support_contact = models.CharField(max_length=255, blank=True, help_text="Support contact information (email or phone)")
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Asset(models.Model):
    """
    Represents a single asset within the datacenter.
    This model captures detailed information about each piece of equipment.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('decommissioned', 'Decommissioned'),
        ('standby', 'Standby'),
        ('faulty', 'Faulty'),
    ]
    
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    # Basic Identification
    asset_tag = models.CharField(max_length=100, unique=True, help_text="Unique identifier for the asset (e.g., UPS-001)")
    serial_number = models.CharField(max_length=100, unique=True, blank=True, null=True, help_text="Manufacturer's serial number")
    name = models.CharField(max_length=255, help_text="Common name or hostname of the asset")
    
    # Classification
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT, help_text="Type of asset")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, help_text="Asset manufacturer")
    model_number = models.CharField(max_length=100, blank=True, help_text="Manufacturer's model number")
    
    # Location and Assignment
    location = models.ForeignKey(Location, on_delete=models.PROTECT, help_text="Physical location of the asset")
    assigned_to = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_assets',
        help_text="Employee responsible for this asset"
    )
    
    # Status and Operational Information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', help_text="Current operational status")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', help_text="Business priority level")
    
    # Dates and Tracking
    purchase_date = models.DateField(null=True, blank=True, help_text="Date when asset was purchased")
    installation_date = models.DateField(null=True, blank=True, help_text="Date when asset was installed")
    warranty_expiry = models.DateField(null=True, blank=True, help_text="Warranty expiration date")
    last_maintenance = models.DateField(null=True, blank=True, help_text="Date of last maintenance")
    next_maintenance = models.DateField(null=True, blank=True, help_text="Scheduled next maintenance date")
    
    # Additional Information
    description = models.TextField(blank=True, help_text="Detailed description of the asset")
    notes = models.TextField(blank=True, help_text="Additional notes or comments")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['asset_tag']
        verbose_name = "Asset"
        verbose_name_plural = "Assets"

    def __str__(self):
        return f"{self.asset_tag} - {self.name}"
    
    @property
    def is_maintenance_due(self):
        """Check if maintenance is due or overdue"""
        if self.next_maintenance:
            return self.next_maintenance <= timezone.now().date()
        return False
    
    @property
    def warranty_status(self):
        """Check warranty status"""
        if not self.warranty_expiry:
            return "Unknown"
        
        today = timezone.now().date()
        if self.warranty_expiry < today:
            return "Expired"
        elif (self.warranty_expiry - today).days <= 30:
            return "Expiring Soon"
        else:
            return "Active"

class AssetSpecification(models.Model):
    """
    Stores asset-specific technical specifications.
    This allows for flexible storage of different specifications for different asset types.
    """
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='specifications')
    specification_name = models.CharField(max_length=100, help_text="Name of the specification (e.g., 'Power Rating', 'Fuel Capacity')")
    specification_value = models.CharField(max_length=255, help_text="Value of the specification (e.g., '600 kVA', '1000 Liters')")
    unit = models.CharField(max_length=50, blank=True, help_text="Unit of measurement (e.g., 'kVA', 'Liters', 'Celsius')")
    
    class Meta:
        unique_together = ['asset', 'specification_name']
        ordering = ['specification_name']

    def __str__(self):
        unit_str = f" {self.unit}" if self.unit else ""
        return f"{self.specification_name}: {self.specification_value}{unit_str}"

class AssetLog(models.Model):
    """
    Tracks all changes and events related to assets.
    This provides an audit trail for asset management.
    """
    EVENT_TYPES = [
        ('created', 'Asset Created'),
        ('updated', 'Asset Updated'),
        ('status_change', 'Status Changed'),
        ('assignment_change', 'Assignment Changed'),
        ('maintenance_scheduled', 'Maintenance Scheduled'),
        ('maintenance_completed', 'Maintenance Completed'),
        ('incident_reported', 'Incident Reported'),
        ('specification_updated', 'Specification Updated'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='logs')
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    description = models.TextField(help_text="Description of what happened")
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, help_text="User who performed the action")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Optional fields for specific event types
    old_value = models.CharField(max_length=255, blank=True, help_text="Previous value (for updates)")
    new_value = models.CharField(max_length=255, blank=True, help_text="New value (for updates)")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Asset Log"
        verbose_name_plural = "Asset Logs"

    def __str__(self):
        return f"{self.asset.asset_tag} - {self.get_event_type_display()} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"

class MaintenanceRecord(models.Model):
    """
    Records maintenance activities performed on assets.
    """
    MAINTENANCE_TYPES = [
        ('preventive', 'Preventive Maintenance'),
        ('corrective', 'Corrective Maintenance'),
        ('emergency', 'Emergency Maintenance'),
        ('inspection', 'Inspection'),
        ('calibration', 'Calibration'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Scheduling
    scheduled_date = models.DateField(help_text="When maintenance is scheduled")
    scheduled_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='scheduled_maintenance',
        help_text="Who scheduled this maintenance"
    )
    
    # Execution
    performed_date = models.DateField(null=True, blank=True, help_text="When maintenance was actually performed")
    performed_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='performed_maintenance',
        help_text="Who performed the maintenance"
    )
    
    # Details
    description = models.TextField(help_text="Description of maintenance work")
    work_performed = models.TextField(blank=True, help_text="Detailed description of work performed")
    parts_used = models.TextField(blank=True, help_text="Parts or materials used")
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Cost of maintenance")
    
    # Duration
    estimated_duration = models.DurationField(null=True, blank=True, help_text="Estimated time for maintenance")
    actual_duration = models.DurationField(null=True, blank=True, help_text="Actual time taken")
    
    # Follow-up
    next_maintenance_date = models.DateField(null=True, blank=True, help_text="When next maintenance should be scheduled")
    notes = models.TextField(blank=True, help_text="Additional notes or observations")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = "Maintenance Record"
        verbose_name_plural = "Maintenance Records"

    def __str__(self):
        return f"{self.asset.asset_tag} - {self.get_maintenance_type_display()} ({self.scheduled_date})"
    
    @property
    def is_overdue(self):
        """Check if scheduled maintenance is overdue"""
        if self.status in ['completed', 'cancelled']:
            return False
        return self.scheduled_date < timezone.now().date()