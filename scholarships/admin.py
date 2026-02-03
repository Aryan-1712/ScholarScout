from django.contrib import admin
from .models import Scholarship, SavedScholarship


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "amount", "deadline", "field_of_study", "scholarship_type", "student_status")
    list_filter = ("field_of_study", "scholarship_type", "student_status", "deadline")
    search_fields = ("name", "organization", "description")
    ordering = ("-amount",)


@admin.register(SavedScholarship)
class SavedScholarshipAdmin(admin.ModelAdmin):
    list_display = ("user", "scholarship", "saved_at")
    list_filter = ("saved_at",)
    search_fields = ("user__email", "scholarship__name")
