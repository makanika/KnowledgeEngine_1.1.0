from django.core.management.base import BaseCommand
from django.utils import timezone
from assets.models import Asset, AssetType, Manufacturer, AssetSpecification, AssetLog
from users.models import Location, CustomUser
import re
from datetime import datetime, date

class Command(BaseCommand):
    help = 'Import DX-Asset from text file format'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to DX-Asset text file')
        parser.add_argument('--location', type=str, default='Kampala', help='Location name')
        parser.add_argument('--country', type=str, default='Uganda', help='Country name')
        parser.add_argument('--asset-prefix', type=str, default='COOL', help='Asset tag prefix')

    def handle(self, *args, **options):
        try:
            with open(options['file_path'], 'r') as f:
                content = f.read()
            
            # Parse key data
            data = self.parse_dx_asset(content)
            
            # Create/get location
            location, _ = Location.objects.get_or_create(
                name=options['location'],
                defaults={'country': options['country']}
            )
            
            # Create/get asset type
            asset_type, _ = AssetType.objects.get_or_create(
                name="Cooling Unit",
                defaults={'description': "HVAC cooling units for datacenter climate control"}
            )
            
            # Create/get manufacturer
            manufacturer, _ = Manufacturer.objects.get_or_create(
                name=data['manufacturer'],
                defaults={'website': f"https://{data['manufacturer'].lower().replace(' ', '')}.com"}
            )
            
            # Generate unique asset tag
            base_tag = f"{options['asset_prefix']}-{options['country'][:2].upper()}"
            counter = 1
            while Asset.objects.filter(asset_tag=f"{base_tag}-{counter:03d}").exists():
                counter += 1
            asset_tag = f"{base_tag}-{counter:03d}"
            
            # Create asset
            asset = Asset.objects.create(
                asset_tag=asset_tag,
                serial_number=data['serial_number'],
                name=f"{data['model']} Cooling Unit",
                asset_type=asset_type,
                manufacturer=manufacturer,
                model_number=data['model'],
                location=location,
                status='active',
                priority='critical',
                purchase_date=data.get('order_date'),
                description=f"Imported from DX-Asset file. Customer: {data.get('customer', 'Unknown')}",
                notes=f"Article No.: {data.get('article_no', '')}\nCustomer Order: {data.get('order_no', '')}"
            )
            
            # Add specifications
            for spec_name, spec_value, unit in data['specifications']:
                AssetSpecification.objects.create(
                    asset=asset,
                    specification_name=spec_name,
                    specification_value=spec_value,
                    unit=unit
                )
            
            # Create log
            admin_user = CustomUser.objects.filter(is_superuser=True).first()
            AssetLog.objects.create(
                asset=asset,
                event_type='created',
                description=f'Asset imported from DX-Asset file: {options["file_path"]}',
                user=admin_user
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported asset: {asset.asset_tag}')
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))

    def parse_dx_asset(self, content):
        """Parse DX-Asset text format"""
        data = {'specifications': []}
        
        # Extract key fields with regex
        patterns = {
            'manufacturer': r'Manufacturer:\s*(.+)',
            'model': r'Model / Type:\s*(.+)',
            'serial_number': r'Serial No\. \(Unit\):\s*(.+)',
            'article_no': r'Article No\. / Item No\.:\s*(.+)',
            'customer': r'Customer:\s*(.+)',
            'order_no': r'Customer Order No\.:\s*(.+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            data[key] = match.group(1).strip() if match else ''
        
        # Parse order date
        order_match = re.search(r'Order Date:\s*(\d{2}/\d{2}/\d{4})', content)
        if order_match:
            data['order_date'] = datetime.strptime(order_match.group(1), '%d/%m/%Y').date()
        
        # Extract specifications
        spec_patterns = [
            (r'Operating Weight:\s*(.+)', 'Operating Weight'),
            (r'Year of Manufacture:\s*(.+)', 'Year of Manufacture'),
            (r'Compressor Type:\s*(.+)', 'Compressor Type'),
            (r'Refrigerant:\s*(.+)', 'Refrigerant'),
            (r'Voltage:\s*(.+)', 'Voltage'),
            (r'F\.L\.A\. \(Full Load Amps\):\s*(.+)', 'Full Load Amps'),
        ]
        
        for pattern, name in spec_patterns:
            match = re.search(pattern, content)
            if match:
                value = match.group(1).strip()
                # Extract unit if present
                unit_match = re.search(r'(\d+(?:\.\d+)?)\s*(.+)', value)
                if unit_match:
                    data['specifications'].append((name, unit_match.group(1), unit_match.group(2)))
                else:
                    data['specifications'].append((name, value, ''))
        
        return data