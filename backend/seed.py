"""
Seed script — run once after DB creation to populate dummy HCPs and materials.
Usage: python seed.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import engine, SessionLocal, Base
from models import HCP, Material

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── Seed HCPs ────────────────────────────────────────────────────────────────
hcps = [
    HCP(name="Dr. Smith",     specialty="Cardiologist",   hospital="City Heart Institute",     city="New York",    email="smith@cityheartinstitute.com"),
    HCP(name="Dr. John",      specialty="Oncologist",     hospital="Metro Cancer Center",       city="Los Angeles", email="john@metrocancer.com"),
    HCP(name="Dr. Patel",     specialty="Endocrinologist",hospital="Diabetes & Wellness Clinic",city="Chicago",     email="patel@dwclinic.com"),
    HCP(name="Dr. Liu",       specialty="Neurologist",    hospital="Brain & Spine Hospital",    city="Houston",     email="liu@brainspine.com"),
    HCP(name="Dr. Fernandez", specialty="Pulmonologist",  hospital="Respiratory Health Center", city="Miami",       email="fernandez@rhcmiami.com"),
    HCP(name="Dr. Williams",  specialty="General Practitioner", hospital="Community Health Clinic", city="Seattle", email="williams@commhealth.com"),
    HCP(name="Dr. Singh",     specialty="Rheumatologist", hospital="Joint & Bone Clinic",       city="Boston",      email="singh@jointbone.com"),
    HCP(name="Dr. Chen",      specialty="Gastroenterologist", hospital="Digestive Health Center", city="San Francisco", email="chen@dhcsf.com"),
]

# ── Seed Materials ────────────────────────────────────────────────────────────
materials = [
    Material(name="ProduX Efficacy Brochure",      type="Brochure", product="ProduX"),
    Material(name="ProduX Patient Starter Kit",    type="Sample",   product="ProduX"),
    Material(name="CardioFlow Brochure",           type="Brochure", product="CardioFlow"),
    Material(name="CardioFlow Clinical Trial PDF", type="Leaflet",  product="CardioFlow"),
    Material(name="NeuroMax Product Leaflet",      type="Leaflet",  product="NeuroMax"),
    Material(name="NeuroMax Sample Pack",          type="Sample",   product="NeuroMax"),
    Material(name="OncoClear Data Sheet",          type="Brochure", product="OncoClear"),
    Material(name="PulmoRelief Inhaler Sample",    type="Sample",   product="PulmoRelief"),
]

# Avoid duplicates on re-run
existing_hcps = db.query(HCP).count()
existing_materials = db.query(Material).count()

if existing_hcps == 0:
    db.add_all(hcps)
    print(f"✅ Seeded {len(hcps)} HCPs")
else:
    print(f"ℹ️  HCPs already seeded ({existing_hcps} records)")

if existing_materials == 0:
    db.add_all(materials)
    print(f"✅ Seeded {len(materials)} Materials")
else:
    print(f"ℹ️  Materials already seeded ({existing_materials} records)")

db.commit()
db.close()
print("✅ Database seeding complete!")
