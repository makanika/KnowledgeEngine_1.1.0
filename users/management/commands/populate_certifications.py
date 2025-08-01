# users/management/commands/populate_certifications.py

from django.core.management.base import BaseCommand
from users.models import Certification, CustomUser
import random

class Command(BaseCommand):
    help = 'Populate the database with sample certifications and assign them to users'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate certifications...'))
        
        # Create sample certifications
        certifications_data = [
            'Uptime Institute Certified Tier Designer',
            'TIA-942 Data Center Infrastructure',
            'NFPA Fire Protection Certified',
            'BMS Operations Specialist',
            'Generator Maintenance Certified',
            'HVAC Systems Professional',
            'Electrical Safety Certified',
            'CompTIA Server+ Certified',
            'Cisco Data Center Unified Computing',
            'VMware Certified Professional',
            'Microsoft Azure Fundamentals',
            'AWS Cloud Practitioner',
            'ITIL Foundation Certified',
            'PMP Project Management',
            'Six Sigma Green Belt',
            'Schneider Electric Certified',
            'APC UPS Specialist',
            'Caterpillar Generator Technician',
            'Liebert Cooling Systems',
            'Data Center Energy Efficiency'
        ]
        
        # Create certifications
        created_certs = []
        for cert_name in certifications_data:
            cert, created = Certification.objects.get_or_create(name=cert_name)
            if created:
                created_certs.append(cert)
                self.stdout.write(f'Created certification: {cert_name}')
        
        # Assign random certifications to users
        users = CustomUser.objects.filter(is_active=True)
        for user in users:
            # Assign 2-5 random certifications to each user
            num_certs = random.randint(2, 5)
            random_certs = random.sample(created_certs, min(num_certs, len(created_certs)))
            
            for cert in random_certs:
                user.certifications.add(cert)
            
            self.stdout.write(f'Assigned {len(random_certs)} certifications to {user.full_name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(created_certs)} certifications and assigned them to users!')
        )