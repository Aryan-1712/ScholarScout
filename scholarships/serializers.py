from rest_framework import serializers
from .models import Scholarship, SavedScholarship


class ScholarshipSerializer(serializers.ModelSerializer):
    """Full representation used in list AND detail responses."""

    class Meta:
        model = Scholarship
        fields = [
            "id",
            "name",
            "organization",
            "description",
            "amount",
            "deadline",
            "field_of_study",
            "scholarship_type",
            "student_status",
            "min_gpa",
            "eligibility",
            "benefits",
            "application_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("created_at", "updated_at")


class SavedScholarshipSerializer(serializers.ModelSerializer):
    """Nested scholarship inside the saved-list response."""

    scholarship = ScholarshipSerializer(read_only=True)

    class Meta:
        model = SavedScholarship
        fields = ("id", "scholarship", "saved_at")
        read_only_fields = fields
