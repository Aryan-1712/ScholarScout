"""
Usage:
    python manage.py seed_scholarships          # insert (skip if already seeded)
    python manage.py seed_scholarships --flush  # delete existing rows first
"""

from django.core.management.base import BaseCommand
from scholarships.models import Scholarship

SCHOLARSHIPS = [
    {
        "name": "Gates Millennium Scholars Program",
        "organization": "Bill & Melinda Gates Foundation",
        "description": "A highly selective scholarship for outstanding minority students with significant financial need.",
        "amount": 50000,
        "deadline": "2026-03-15",
        "field_of_study": "All Fields",
        "scholarship_type": "Merit-Based",
        "student_status": "Undergraduate",
        "min_gpa": "3.3",
        "eligibility": [
            "U.S. Citizen or Legal Permanent Resident",
            "Pell Grant eligible",
            "Minimum 3.3 GPA",
            "Planning to enroll full-time",
        ],
        "benefits": [
            "Full tuition coverage",
            "Room and board",
            "Books and supplies",
            "Mentorship program",
        ],
        "application_url": "#",
    },
    {
        "name": "National Merit Scholarship",
        "organization": "National Merit Scholarship Corporation",
        "description": "Awarded to high school students based on PSAT/NMSQT scores and academic achievement.",
        "amount": 25000,
        "deadline": "2026-02-28",
        "field_of_study": "All Fields",
        "scholarship_type": "Merit-Based",
        "student_status": "High School",
        "min_gpa": "3.5",
        "eligibility": [
            "High PSAT scores",
            "U.S. Citizen",
            "Minimum 3.5 GPA",
            "Full-time enrollment",
        ],
        "benefits": [
            "$2,500 one-time award",
            "Renewable options available",
            "Recognition certificate",
        ],
        "application_url": "#",
    },
    {
        "name": "Google Engineering Scholarship",
        "organization": "Google LLC",
        "description": "Supporting students pursuing computer science and engineering degrees with a passion for technology.",
        "amount": 10000,
        "deadline": "2026-04-20",
        "field_of_study": "Computer Science",
        "scholarship_type": "Merit-Based",
        "student_status": "Undergraduate",
        "min_gpa": "3.0",
        "eligibility": [
            "Computer Science or related major",
            "Demonstrated leadership",
            "Minimum 3.0 GPA",
        ],
        "benefits": [
            "$10,000 award",
            "Google internship opportunity",
            "Tech community access",
        ],
        "application_url": "#",
    },
    {
        "name": "Coca-Cola Scholars Program",
        "organization": "The Coca-Cola Company",
        "description": "Recognizing and celebrating high-achieving high school seniors who are making a difference in their communities.",
        "amount": 20000,
        "deadline": "2026-02-10",
        "field_of_study": "All Fields",
        "scholarship_type": "Merit-Based",
        "student_status": "High School",
        "min_gpa": "3.0",
        "eligibility": [
            "High school senior",
            "Minimum 3.0 GPA",
            "U.S. Citizen or permanent resident",
            "Community service",
        ],
        "benefits": [
            "$20,000 scholarship",
            "Leadership development",
            "Scholars summit attendance",
        ],
        "application_url": "#",
    },
    {
        "name": "Dell Scholars Program",
        "organization": "Michael & Susan Dell Foundation",
        "description": "Supporting students who have overcome significant obstacles and demonstrate grit and potential.",
        "amount": 20000,
        "deadline": "2026-03-01",
        "field_of_study": "All Fields",
        "scholarship_type": "Need-Based",
        "student_status": "High School",
        "min_gpa": "2.4",
        "eligibility": [
            "Participate in approved college readiness program",
            "Minimum 2.4 GPA",
            "Pell-eligible",
            "Planned college enrollment",
        ],
        "benefits": [
            "$20,000 scholarship",
            "Dell laptop",
            "Textbook credits",
            "Ongoing support",
        ],
        "application_url": "#",
    },
    {
        "name": "Jack Kent Cooke Foundation Scholarship",
        "organization": "Jack Kent Cooke Foundation",
        "description": "Nation's largest private scholarship for high-achieving students with financial need.",
        "amount": 40000,
        "deadline": "2026-04-15",
        "field_of_study": "All Fields",
        "scholarship_type": "Merit-Based",
        "student_status": "Undergraduate",
        "min_gpa": "3.5",
        "eligibility": [
            "Exceptional academic ability",
            "Financial need",
            "Minimum 3.5 GPA",
            "U.S. Citizen or permanent resident",
        ],
        "benefits": [
            "Up to $40,000 per year",
            "Educational advising",
            "Funded internships",
            "Networking opportunities",
        ],
        "application_url": "#",
    },
    {
        "name": "STEM Excellence Award",
        "organization": "National STEM Foundation",
        "description": "Supporting the next generation of STEM leaders and innovators.",
        "amount": 15000,
        "deadline": "2026-05-30",
        "field_of_study": "Science",
        "scholarship_type": "Merit-Based",
        "student_status": "Undergraduate",
        "min_gpa": "3.2",
        "eligibility": [
            "STEM major",
            "Demonstrated research experience",
            "Minimum 3.2 GPA",
        ],
        "benefits": [
            "$15,000 award",
            "Research mentorship",
            "Conference attendance",
        ],
        "application_url": "#",
    },
    {
        "name": "Hispanic Scholarship Fund",
        "organization": "Hispanic Scholarship Fund",
        "description": "Supporting Hispanic American students in achieving their higher education goals.",
        "amount": 5000,
        "deadline": "2026-03-30",
        "field_of_study": "All Fields",
        "scholarship_type": "Diversity",
        "student_status": "Undergraduate",
        "min_gpa": "3.0",
        "eligibility": [
            "Hispanic heritage",
            "Minimum 3.0 GPA",
            "U.S. Citizen or permanent resident",
            "Enrolled in accredited institution",
        ],
        "benefits": [
            "$500 - $5,000 award",
            "Scholar services",
            "Career development",
        ],
        "application_url": "#",
    },
    {
        "name": "Women in Engineering Scholarship",
        "organization": "Society of Women Engineers",
        "description": "Empowering women to achieve their full potential in engineering careers.",
        "amount": 12000,
        "deadline": "2026-02-15",
        "field_of_study": "Engineering",
        "scholarship_type": "Diversity",
        "student_status": "Undergraduate",
        "min_gpa": "3.0",
        "eligibility": [
            "Female student",
            "Engineering major",
            "Minimum 3.0 GPA",
            "SWE membership (can apply simultaneously)",
        ],
        "benefits": [
            "$12,000 scholarship",
            "Professional development",
            "Networking events",
        ],
        "application_url": "#",
    },
    {
        "name": "Future Business Leaders Scholarship",
        "organization": "American Business Association",
        "description": "Investing in tomorrow's business innovators and entrepreneurs.",
        "amount": 8000,
        "deadline": "2026-06-01",
        "field_of_study": "Business",
        "scholarship_type": "Merit-Based",
        "student_status": "Undergraduate",
        "min_gpa": "3.3",
        "eligibility": [
            "Business major",
            "Leadership experience",
            "Minimum 3.3 GPA",
        ],
        "benefits": [
            "$8,000 award",
            "Mentorship program",
            "Industry connections",
        ],
        "application_url": "#",
    },
]


class Command(BaseCommand):
    help = "Seed the Scholarship table with sample data from the dashboard"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing scholarships before inserting",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            count, _ = Scholarship.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {count} existing scholarship(s)."))

        created = 0
        for data in SCHOLARSHIPS:
            _, was_created = Scholarship.objects.get_or_create(
                name=data["name"],
                organization=data["organization"],
                defaults=data,
            )
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done — {created} scholarship(s) created "
                f"({len(SCHOLARSHIPS) - created} already existed)."
            )
        )
