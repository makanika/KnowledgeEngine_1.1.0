# assets/management/commands/populate_assets.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from assets.models import AssetType, Manufacturer, Asset, AssetSpecification
from users.models import Location, CustomUser

class Command(BaseCommand):
    help = 'Populate the database with sample asset data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate asset data...'))
        
        # Create Asset Types
        asset_types_data = [
            ('UPS', 'Uninterruptible Power Supply systems'),
            ('Generator', 'Backup power generation equipment'),
            ('IAC', 'In-Row Air Conditioning units'),
            ('Camera System', 'Security camera and NVR systems'),
            ('Water Tank', 'Water storage systems'),
            ('GRP Tank', 'Glass Reinforced Plastic tanks'),
            ('Pump', 'Water circulation and pressure pumps'),
            ('AHU', 'Air Handling Units'),
            ('Fire System', 'Fire detection and suppression systems'),
            ('Kidde Panel', 'Fire control panels'),
        ]
        
        for name, description in asset_types_data:
            asset_type, created = AssetType.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(f'Created asset type: {name}')
        
        # Create Manufacturers
        manufacturers_data = [
            ('APC', 'https://www.apc.com', 'support@apc.com'),
            ('Schneider Electric', 'https://www.se.com', 'support@schneider-electric.com'),
            ('Caterpillar', 'https://www.cat.com', 'support@cat.com'),
            ('Cummins', 'https://www.cummins.com', 'support@cummins.com'),
            ('Liebert', 'https://www.vertiv.com', 'support@vertiv.com'),
            ('Stulz', 'https://www.stulz.com', 'support@stulz.com'),
            ('Hikvision', 'https://www.hikvision.com', 'support@hikvision.com'),
            ('Grundfos', 'https://www.grundfos.com', 'support@grundfos.com'),
            ('Kidde', 'https://www.kidde.com', 'support@kidde.com'),
            ('Honeywell', 'https://www.honeywell.com', 'support@honeywell.com'),
        ]
        
        for name, website, contact in manufacturers_data:
            manufacturer, created = Manufacturer.objects.get_or_create(
                name=name,
                defaults={'website': website, 'support_contact': contact}
            )
            if created:
                self.stdout.write(f'Created manufacturer: {name}')
        
        # Get or create a default location
        location, created = Location.objects.get_or_create(
            name='Kampala DC',
            defaults={'country': 'Uganda'}
        )
        if created:
            self.stdout.write(f'Created location: {location.name}')
        
        # Create sample assets based on your documentation
        sample_assets = [
            # UPS Systems
            {
                'asset_tag': 'UPS-001',
                'name': 'Main UPS 600kVA',
                'asset_type': 'UPS',
                'manufacturer': 'APC',
                'model_number': 'SURT600XLIM',
                'serial_number': 'UPS600-2024-001',
                'status': 'active',
                'priority': 'critical',
                'description': 'Primary UPS system for critical infrastructure',
                'specifications': [
                    ('Power Rating', '600', 'kVA'),
                    ('Input Voltage', '400', 'V'),
                    ('Output Voltage', '400', 'V'),
                    ('Battery Runtime', '15', 'minutes'),
                ]
            },
            {
                'asset_tag': 'UPS-002',
                'name': 'Secondary UPS 10kVA',
                'asset_type': 'UPS',
                'manufacturer': 'Schneider Electric',
                'model_number': 'SRT10KXLI',
                'serial_number': 'UPS010-2024-002',
                'status': 'active',
                'priority': 'high',
                'description': 'Secondary UPS for network equipment',
                'specifications': [
                    ('Power Rating', '10', 'kVA'),
                    ('Input Voltage', '230', 'V'),
                    ('Output Voltage', '230', 'V'),
                    ('Battery Runtime', '30', 'minutes'),
                ]
            },
            # Generators
            {
                'asset_tag': 'GEN-001',
                'name': 'Primary Generator',
                'asset_type': 'Generator',
                'manufacturer': 'Caterpillar',
                'model_number': 'C15-500kW',
                'serial_number': 'CAT500-2024-001',
                'status': 'active',
                'priority': 'critical',
                'description': 'Primary backup generator for facility',
                'specifications': [
                    ('Power Output', '500', 'kW'),
                    ('Fuel Type', 'Diesel', ''),
                    ('Fuel Capacity', '1000', 'Liters'),
                    ('Runtime at Full Load', '8', 'hours'),
                ]
            },
            # IAC Units
            {
                'asset_tag': 'IAC-001',
                'name': 'Server Room IAC Unit 1',
                'asset_type': 'IAC',
                'manufacturer': 'Liebert',
                'model_number': 'CRV-35kW',
                'serial_number': 'IAC035-2024-001',
                'status': 'active',
                'priority': 'critical',
                'description': 'In-row cooling for server rack 1-5',
                'specifications': [
                    ('Cooling Capacity', '35', 'kW'),
                    ('Airflow', '3500', 'CFM'),
                    ('Temperature Range', '18-27', 'Celsius'),
                    ('Humidity Range', '40-60', '%RH'),
                ]
            },
            # Camera System
            {
                'asset_tag': 'CAM-001',
                'name': 'Security Camera System',
                'asset_type': 'Camera System',
                'manufacturer': 'Hikvision',
                'model_number': 'DS-7732NI-K4',
                'serial_number': 'HIK732-2024-001',
                'status': 'active',
                'priority': 'medium',
                'description': 'NVR system with 100 IP cameras',
                'specifications': [
                    ('Camera Count', '100', 'units'),
                    ('Recording Resolution', '4K', ''),
                    ('Storage Capacity', '32', 'TB'),
                    ('Recording Duration', '30', 'days'),
                ]
            },
            # Pumps
            {
                'asset_tag': 'PUMP-001',
                'name': 'Primary Water Pump',
                'asset_type': 'Pump',
                'manufacturer': 'Grundfos',
                'model_number': 'CR15-8',
                'serial_number': 'GRU158-2024-001',
                'status': 'active',
                'priority': 'high',
                'description': 'Main water circulation pump',
                'specifications': [
                    ('Flow Rate', '15', 'm³/h'),
                    ('Head', '80', 'm'),
                    ('Power', '7.5', 'kW'),
                    ('Efficiency', '85', '%'),
                ]
            },
            # Fire System
            {
                'asset_tag': 'FIRE-001',
                'name': 'Main Fire Detection System',
                'asset_type': 'Fire System',
                'manufacturer': 'Honeywell',
                'model_number': 'FS90-Main',
                'serial_number': 'HON90-2024-001',
                'status': 'active',
                'priority': 'critical',
                'description': 'Central fire detection and alarm system',
                'specifications': [
                    ('Zone Coverage', '9', 'zones'),
                    ('Detector Count', '150', 'units'),
                    ('Response Time', '30', 'seconds'),
                    ('Backup Power', '24', 'hours'),
                ]
            },
        ]
        
        # Create the assets
        for asset_data in sample_assets:
            specifications = asset_data.pop('specifications', [])
            
            # Get related objects
            asset_type = AssetType.objects.get(name=asset_data['asset_type'])
            manufacturer = Manufacturer.objects.get(name=asset_data['manufacturer'])
            
            # Create the asset
            asset, created = Asset.objects.get_or_create(
                asset_tag=asset_data['asset_tag'],
                defaults={
                    **asset_data,
                    'asset_type': asset_type,
                    'manufacturer': manufacturer,
                    'location': location,
                    'purchase_date': date.today() - timedelta(days=365),
                    'installation_date': date.today() - timedelta(days=350),
                    'warranty_expiry': date.today() + timedelta(days=730),
                    'next_maintenance': date.today() + timedelta(days=90),
                }
            )
            
            if created:
                self.stdout.write(f'Created asset: {asset.asset_tag}')
                
                # Add specifications
                for spec_name, spec_value, unit in specifications:
                    AssetSpecification.objects.create(
                        asset=asset,
                        specification_name=spec_name,
                        specification_value=spec_value,
                        unit=unit
                    )
                    self.stdout.write(f'  Added specification: {spec_name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated asset data!')
        )