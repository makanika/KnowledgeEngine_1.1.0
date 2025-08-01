# assets/management/commands/assign_sample_assets.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from assets.models import Asset, AssetLog
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Assign sample assets to users for testing integration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting asset assignment...'))
        
        # Get all active users
        users = CustomUser.objects.filter(is_active=True)
        if not users.exists():
            self.stdout.write(self.style.ERROR('No active users found. Please create users first.'))
            return
        
        # Get all unassigned assets
        unassigned_assets = Asset.objects.filter(assigned_to__isnull=True)
        if not unassigned_assets.exists():
            self.stdout.write(self.style.WARNING('No unassigned assets found.'))
            return
        
        # Create admin user if it doesn't exist
        admin_user, created = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@knowledgeengine.com',
                'full_name': 'System Administrator',
                'id_number': 'ADMIN-001',
                'department': 'IT',
                'designation': 'System Administrator',
                'shift': '24/7',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'Created admin user: {admin_user.username}')
        
        # Assignment logic based on asset type and user department
        assignment_rules = {
            'UPS': ['IT', 'Facilities'],
            'Generator': ['Facilities', 'Engineering'],
            'IAC': ['IT', 'Facilities'],
            'Camera System': ['Security', 'IT'],
            'Pump': ['Facilities', 'Engineering'],
            'Fire System': ['Safety', 'Facilities'],
        }
        
        assignments_made = 0
        
        for asset in unassigned_assets:
            # Find suitable users based on asset type
            suitable_departments = assignment_rules.get(asset.asset_type.name, ['IT'])
            suitable_users = users.filter(department__in=suitable_departments)
            
            if not suitable_users.exists():
                # Fallback to any user
                suitable_users = users
            
            # Assign to user with least assets
            user_asset_counts = {}
            for user in suitable_users:
                user_asset_counts[user] = user.assigned_assets.count()
            
            # Get user with minimum assets
            assigned_user = min(user_asset_counts.keys(), key=lambda u: user_asset_counts[u])
            
            # Make the assignment
            asset.assigned_to = assigned_user
            asset.save()
            
            # Create log entry
            AssetLog.objects.create(
                asset=asset,
                event_type='assignment_change',
                description=f'Asset assigned to {assigned_user.full_name} during system setup',
                user=admin_user,
                old_value='Unassigned',
                new_value=assigned_user.full_name
            )
            
            assignments_made += 1
            self.stdout.write(f'Assigned {asset.asset_tag} to {assigned_user.full_name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully assigned {assignments_made} assets!')
        )