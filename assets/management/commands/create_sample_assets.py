from django.core.management.base import BaseCommand
from assets.models import Asset, AssetType, Manufacturer, AssetSpecification, AssetLog
from users.models import Location, CustomUser
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Create sample assets for testing'

    def handle(self, *args, **options):
        # Get required objects
        asset_types = list(AssetType.objects.all())
        manufacturers = list(Manufacturer.objects.all())
        locations = list(Location.objects.all())
        users = list(CustomUser.objects.all())
        
        if not all([asset_types, manufacturers, locations, users]):
            self.stdout.write(self.style.ERROR('Missing required data. Please ensure you have asset types, manufacturers, locations, and users.'))
            return
        
        # Sample assets data
        sample_assets = [
            {
                'asset_tag': 'UPS-001',
                'name': 'Main UPS System',
                'description': 'Primary uninterruptible power supply for datacenter critical systems',
                'model_number': 'APC-5000',
                'serial_number': 'APC123456789',
                'status': 'active',
                'priority': 'high',
                'specs': [
                    {'name': 'Power Rating', 'value': '5000', 'unit': 'VA'},
                    {'name': 'Battery Runtime', 'value': '15', 'unit': 'minutes'},
                    {'name': 'Input Voltage', 'value': '230', 'unit': 'V'},
                ]
            },
            {
                'asset_tag': 'AC-001',
                'name': 'Primary Air Conditioning Unit',
                'description': 'Main cooling system for server room temperature control',
                'model_number': 'CARRIER-7500',
                'serial_number': 'CAR987654321',
                'status': 'active',
                'priority': 'high',
                'specs': [
                    {'name': 'Cooling Capacity', 'value': '7.5', 'unit': 'tons'},
                    {'name': 'Power Consumption', 'value': '8.5', 'unit': 'kW'},
                    {'name': 'Refrigerant Type', 'value': 'R410A', 'unit': ''},
                ]
            },
            {
                'asset_tag': 'SRV-001',
                'name': 'Database Server Primary',
                'description': 'Main database server hosting critical business applications',
                'model_number': 'DELL-R750',
                'serial_number': 'DELL123ABC789',
                'status': 'active',
                'priority': 'critical',
                'specs': [
                    {'name': 'CPU', 'value': 'Intel Xeon Gold 6338', 'unit': ''},
                    {'name': 'RAM', 'value': '128', 'unit': 'GB'},
                    {'name': 'Storage', 'value': '2', 'unit': 'TB SSD'},
                ]
            },
            {
                'asset_tag': 'NET-001',
                'name': 'Core Network Switch',
                'description': 'Primary network switch for datacenter connectivity',
                'model_number': 'CISCO-9300',
                'serial_number': 'CIS456DEF123',
                'status': 'active',
                'priority': 'high',
                'specs': [
                    {'name': 'Port Count', 'value': '48', 'unit': 'ports'},
                    {'name': 'Speed', 'value': '1', 'unit': 'Gbps'},
                    {'name': 'PoE Budget', 'value': '740', 'unit': 'W'},
                ]
            },
            {
                'asset_tag': 'FW-001',
                'name': 'Perimeter Firewall',
                'description': 'Main security firewall protecting datacenter perimeter',
                'model_number': 'PALO-PA-3220',
                'serial_number': 'PA789GHI456',
                'status': 'maintenance',
                'priority': 'critical',
                'specs': [
                    {'name': 'Throughput', 'value': '2', 'unit': 'Gbps'},
                    {'name': 'Concurrent Sessions', 'value': '500000', 'unit': ''},
                    {'name': 'VPN Tunnels', 'value': '2500', 'unit': ''},
                ]
            }
        ]
        
        created_count = 0
        
        for asset_data in sample_assets:
            # Check if asset already exists
            if Asset.objects.filter(asset_tag=asset_data['asset_tag']).exists():
                self.stdout.write(f"Asset {asset_data['asset_tag']} already exists, skipping...")
                continue
            
            # Create asset
            asset = Asset.objects.create(
                asset_tag=asset_data['asset_tag'],
                name=asset_data['name'],
                description=asset_data['description'],
                asset_type=random.choice(asset_types),
                manufacturer=random.choice(manufacturers),
                location=random.choice(locations),
                assigned_to=random.choice(users),
                status=asset_data['status'],
                priority=asset_data['priority'],
                model_number=asset_data['model_number'],
                serial_number=asset_data['serial_number'],
                purchase_date=date.today() - timedelta(days=random.randint(30, 365)),
                installation_date=date.today() - timedelta(days=random.randint(1, 30)),
                warranty_expiry=date.today() + timedelta(days=random.randint(365, 1095)),
                next_maintenance=date.today() + timedelta(days=random.randint(30, 90))
            )
            
            # Create specifications
            for spec_data in asset_data['specs']:
                AssetSpecification.objects.create(
                    asset=asset,
                    specification_name=spec_data['name'],
                    specification_value=spec_data['value'],
                    unit=spec_data['unit']
                )
            
            # Create initial log entry
            AssetLog.objects.create(
                asset=asset,
                event_type='created',
                description=f'Asset {asset.asset_tag} created and added to inventory',
                user=random.choice(users)
            )
            
            created_count += 1
            self.stdout.write(f"Created asset: {asset.asset_tag} - {asset.name}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample assets')
        )