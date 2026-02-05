from datetime import timedelta

from django.db.models import Sum, Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Scholarship, SavedScholarship
from .serializers import ScholarshipSerializer, SavedScholarshipSerializer


# ── GET /api/scholarships/ ───────────────────────────────────────────────────
# Query params (all optional – mirrors the sidebar filters in dashboard.html):
#   search        – text search across name / organisation / description
#   max_amount    – upper bound on award amount
#   field         – field_of_study value
#   min_gpa       – minimum GPA the scholarship requires  (filter keeps entries ≤ value)
#   status        – student_status value
#   type          – one or more scholarship_type values (comma-separated)
#   deadline_days – keep only scholarships whose deadline is within N days
#   sort          – amount-high | amount-low | deadline | relevant (default)
# ──────────────────────────────────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def scholarship_list(request):
    qs = Scholarship.objects.all()

    # ── search ───────────────────────────────────────────────────────
    search = request.query_params.get("search", "").strip()
    if search:
        qs = qs.filter(
            Q(name__icontains=search)
            | Q(organization__icontains=search)
            | Q(description__icontains=search)
        )

    # ── max_amount ───────────────────────────────────────────────────
    max_amount = request.query_params.get("max_amount")
    if max_amount and max_amount != "50000":          # 50 000 == slider max → "show all"
        try:
            qs = qs.filter(amount__lte=int(max_amount))
        except (ValueError, TypeError):
            pass

    # ── field ────────────────────────────────────────────────────────
    field = request.query_params.get("field", "").strip()
    if field:
        qs = qs.filter(Q(field_of_study=field) | Q(field_of_study="All Fields"))

    # ── min_gpa (sidebar slider: "show scholarships whose GPA req ≤ X") ──
    min_gpa = request.query_params.get("min_gpa")
    if min_gpa and float(min_gpa) > 0:
        try:
            qs = qs.filter(min_gpa__lte=float(min_gpa))
        except (ValueError, TypeError):
            pass

    # ── student_status ───────────────────────────────────────────────
    student_status_val = request.query_params.get("status", "").strip()
    if student_status_val:
        qs = qs.filter(student_status=student_status_val)

    # ── scholarship_type (comma-separated) ───────────────────────────
    types = [t.strip() for t in request.query_params.get("type", "").split(",") if t.strip()]
    if types:
        qs = qs.filter(scholarship_type__in=types)

    # ── deadline_days ────────────────────────────────────────────────
    deadline_days = request.query_params.get("deadline_days")
    if deadline_days:
        try:
            cutoff = timezone.now().date() + timedelta(days=int(deadline_days))
            qs = qs.filter(deadline__lte=cutoff)
        except (ValueError, TypeError):
            pass

    # ── sort ─────────────────────────────────────────────────────────
    sort = request.query_params.get("sort", "relevant")
    sort_map = {
        "amount-high": "-amount",
        "amount-low":  "amount",
        "deadline":    "deadline",
    }
    qs = qs.order_by(sort_map.get(sort, "-amount"))

    serializer = ScholarshipSerializer(qs, many=True)
    return Response(serializer.data)


# ── GET /api/scholarships/<id>/ ──────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def scholarship_detail(request, pk):
    try:
        scholarship = Scholarship.objects.get(pk=pk)
    except Scholarship.DoesNotExist:
        return Response({"detail": "Scholarship not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ScholarshipSerializer(scholarship)
    return Response(serializer.data)


# ── POST / DELETE /api/scholarships/saved/<id>/ ─────────────────────────────
#    POST  → save (bookmark)   |  DELETE → unsave
# ─────────────────────────────────────────────────────────────────────────────
@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def save_scholarship(request, pk):
    try:
        scholarship = Scholarship.objects.get(pk=pk)
    except Scholarship.DoesNotExist:
        return Response({"detail": "Scholarship not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "POST":
        obj, created = SavedScholarship.objects.get_or_create(
            user=request.user, scholarship=scholarship
        )
        if not created:
            return Response(
                {"detail": "Already saved."}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"detail": "Scholarship saved.", "id": obj.pk},
            status=status.HTTP_201_CREATED,
        )

    # DELETE
    deleted, _ = SavedScholarship.objects.filter(
        user=request.user, scholarship=scholarship
    ).delete()
    if deleted == 0:
        return Response(
            {"detail": "Not in your saved list."}, status=status.HTTP_400_BAD_REQUEST
        )
    return Response({"detail": "Scholarship removed from saved."}, status=status.HTTP_200_OK)


# ── GET /api/scholarships/saved/ ─────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def saved_list(request):
    """All scholarships the current users has bookmarked."""
    saved = SavedScholarship.objects.filter(user=request.user).select_related("scholarship")
    serializer = SavedScholarshipSerializer(saved, many=True)
    return Response(serializer.data)


# ── GET /api/scholarships/stats/ ─────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def stats_view(request):
    """
    Aggregates for the four stat-cards at the top of the dashboard.
    """
    today = timezone.now().date()
    thirty_days = today + timedelta(days=30)

    total = Scholarship.objects.count()
    total_awards = Scholarship.objects.aggregate(total=Sum("amount"))["total"] or 0
    urgent = Scholarship.objects.filter(deadline__lte=thirty_days, deadline__gte=today).count()

    # "Matched" – scholarships whose min_gpa ≤ 3.5 (mirrors the JS heuristic)
    matched = Scholarship.objects.filter(min_gpa__lte=3.5).count()

    return Response(
        {
            "total_scholarships": total,
            "total_awards": total_awards,
            "matched": matched,
            "urgent": urgent,
        }
    )
