# Users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class Location(models.Model):
    """
    This model stores the physical locations of the datacenters.
    Using a separate model ensures data consistency and makes it easy to
    manage the list of sites.
    """
    name = models.CharField(max_length=100, unique=True, help_text="The name of the datacenter location, e.g., Kampala, Nairobi")
    country = models.CharField(max_length=100, help_text="The country where the datacenter is located")

    def __str__(self):
        return f"{self.name}, {self.country}"

class Certification(models.Model):
    """
    This model stores the different types of certifications an employee can have.
    This allows for a many-to-many relationship with the CustomUser model,
    enabling each user to have multiple certifications.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    """
    This model extends Django's built-in AbstractUser to include fields
    specific to the employees of the datacenter. It serves as the central
    repository for user information, including their roles, contact details,
    and operational status.
    """
    # Extending the standard Django User model with additional fields
    # as per the documentation.

    # Personal and Employment Details
    id_number = models.CharField(max_length=100, unique=True, help_text="Staff or national identifier")
    full_name = models.CharField(max_length=255, help_text="Employee's full name")
    department = models.CharField(max_length=100, help_text="e.g., Facilities, IT, Security")
    designation = models.CharField(max_length=100, help_text="e.g., Lead Engineer, Technician")
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The primary datacenter location for the user"
    )


    # Operational Status
    shift = models.CharField(max_length=50, help_text="Work shift schedule, e.g., 08:00-20:00")
    on_duty = models.BooleanField(default=False, help_text="Indicates if the user is currently on active duty")

    # Professional Qualifications
    certifications = models.ManyToManyField(Certification, blank=True, help_text="Data center certification types")

    # System Interaction Tracking
    login_time = models.DateTimeField(null=True, blank=True, help_text="Recorded system login timestamp")
    logout_time = models.DateTimeField(null=True, blank=True, help_text="Recorded system logout timestamp")

    # Profile Media
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True, help_text="Profile photo")

    def __str__(self):
        return self.username



