from django.db import models
from django.conf import settings


class Scholarship(models.Model):
    """
    Central scholarship record.
    Mirrors every field rendered on the dashboard cards / modal.
    """

    # ── identity ─────────────────────────────────────────────────────
    name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # ── amounts & dates ──────────────────────────────────────────────
    amount = models.PositiveIntegerField(help_text="Award amount in USD")
    deadline = models.DateField()

    # ── filters / tags ───────────────────────────────────────────────
    FIELD_CHOICES = [
        ("All Fields", "All Fields"),
        ("Engineering", "Engineering"),
        ("Computer Science", "Computer Science"),
        ("Business", "Business"),
        ("Medicine", "Medicine"),
        ("Arts", "Arts & Humanities"),
        ("Science", "Science"),
        ("Law", "Law"),
        ("Education", "Education"),
    ]

    TYPE_CHOICES = [
        ("Merit-Based", "Merit-Based"),
        ("Need-Based", "Need-Based"),
        ("Athletic", "Athletic"),
        ("Diversity", "Diversity & Inclusion"),
    ]

    STATUS_CHOICES = [
        ("Undergraduate", "Undergraduate"),
        ("Graduate", "Graduate"),
        ("High School", "High School"),
    ]

    field_of_study = models.CharField(max_length=50, choices=FIELD_CHOICES, default="All Fields")
    scholarship_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="Merit-Based")
    student_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Undergraduate")
    min_gpa = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)

    # ── JSON lists (eligibility & benefits) ──────────────────────────
    # Stored as JSON; works on SQLite AND PostgreSQL.
    eligibility = models.JSONField(default=list, blank=True)
    benefits = models.JSONField(default=list, blank=True)

    application_url = models.URLField(max_length=512, blank=True, default="#")

    # ── meta ─────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-amount"]
        verbose_name_plural = "scholarships"

    def __str__(self):
        return self.name


class SavedScholarship(models.Model):
    """Per-user bookmarks — the 'save for later' button on the dashboard."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_scholarships",
    )
    scholarship = models.ForeignKey(
        Scholarship,
        on_delete=models.CASCADE,
        related_name="saved_by",
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "scholarship")
        ordering = ["-saved_at"]

    def __str__(self):
        return f"{self.user.email} → {self.scholarship.name}"
