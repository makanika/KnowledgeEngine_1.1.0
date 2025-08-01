# users/management/commands/populate_db.py

import random
from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import CustomUser, Location, Certification # CORRECTED: 'Users' changed to 'users'

# --- Data for Population ---

LOCATIONS_DATA = [
    ("Kampala", "Uganda"), ("Nairobi", "Kenya"), ("Kigali", "Rwanda"),
    ("Dar es Salaam", "Tanzania"), ("Addis Ababa", "Ethiopia"), ("Lagos", "Nigeria"),
    ("Accra", "Ghana"), ("Johannesburg", "South Africa"), ("Cape Town", "South Africa"),
    ("Cairo", "Egypt"), ("Casablanca", "Morocco"), ("Algiers", "Algeria"),
    ("Dakar", "Senegal"), ("Abidjan", "Côte d'Ivoire"), ("Kinshasa", "DR Congo")
]

CERTIFICATIONS_DATA = [
    "Uptime Institute Certified", "TIA-942 Infrastructure", "NFPA Fire Systems",
    "BMS Operations", "Generator Maintenance", "Fire Suppression Systems", "HVAC Cooling Certified"
]

FIRST_NAMES = [
    "Abebe", "Kwame", "Juma", "Femi", "Emeka", "Sanaa", "Zola", "Amara", "Chidinma", "Ifeyinwa",
    "Musa", "Farai", "Tendai", "Bongani", "Thabo", "Nia", "Zainab", "Fatima", "Ayo", "Simisola",
    "Okello", "Achen", "Mugisha", "Nantale", "Apio", "Bwire", "Kato", "Byaruhanga", "Okumu"
]

LAST_NAMES = [
    "Okafor", "Nkosi", "Adebayo", "Mwangi", "Bekele", "Diallo", "Mensah", "Van Der Merwe", "Abdelaziz",
    "Traoré", "Kone", "Kamau", "Ochieng", "Moyo", "Chukwu", "Ibrahim", "Hassan", "Kante", "Diop",

]

DEPARTMENTS = ["Facilities", "IT", "Security", "NOC", "Operations"]
DESIGNATIONS = ["Technician", "Engineer", "Senior Engineer", "Manager", "Analyst", "Specialist"]
SHIFTS = ["08:00-20:00", "20:00-08:00", "09:00-17:00"]


class Command(BaseCommand):
    help = 'Populates the database with sample data for the Knowledge Engine application.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Starting database population...")

        # --- Clear Existing Data ---
        self.stdout.write("Clearing old data...")
        CustomUser.objects.all().delete()
        Location.objects.all().delete()
        Certification.objects.all().delete()

        # --- Create Locations ---
        locations = []
        for name, country in LOCATIONS_DATA:
            location, _ = Location.objects.get_or_create(name=name, country=country)
            locations.append(location)
        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(locations)} locations."))

        # --- Create Certifications ---
        certifications = []
        for name in CERTIFICATIONS_DATA:
            cert, _ = Certification.objects.get_or_create(name=name)
            certifications.append(cert)
        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(certifications)} certifications."))

        # --- Create Superuser ---
        self.stdout.write("Creating superuser...")
        if not CustomUser.objects.filter(username='admin').exists():
            CustomUser.objects.create_superuser(
                username='admin',
                email='admin@knowledge.engine',
                password='adminpass',
                full_name='Admin User',
                id_number='ADMIN001'
            )
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' with password 'adminpass' created."))

        # --- Create Employees ---
        self.stdout.write("Creating 70 sample employees...")
        created_users = 0
        for i in range(70):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            username = f"{first_name.lower()}.{last_name.lower()}{i}"
            email = f"{username}@knowledge.engine"
            id_number = f"KE{202400 + i}"
            
            # Ensure username and id_number are unique
            if CustomUser.objects.filter(username=username).exists():
                continue

            user = CustomUser.objects.create_user(
                username=username,
                password='password123',
                email=email,
                first_name=first_name,
                last_name=last_name,
                full_name=f"{first_name} {last_name}",
                id_number=id_number,
                department=random.choice(DEPARTMENTS),
                designation=random.choice(DESIGNATIONS),
                shift=random.choice(SHIFTS),
                location=random.choice(locations),
                on_duty=random.choice([True, False])
            )

            # Assign 1 to 3 random certifications to the user
            num_certs = random.randint(1, 3)
            user_certs = random.sample(certifications, num_certs)
            user.certifications.set(user_certs)
            user.save()
            created_users += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_users} employees."))
        self.stdout.write(self.style.SUCCESS("Database population complete."))

