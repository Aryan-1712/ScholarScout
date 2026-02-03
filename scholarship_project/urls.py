from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

def index_view(request):
    return render(request, "index.html")

def dashboard_view(request):
    return render(request, "dashboard.html")

urlpatterns = [
    path("", index_view, name="home"),
    path("dashboard/", dashboard_view, name="dashboard"),

    # Admin panel
    path("admin/", admin.site.urls),

    # API routes
    path("api/auth/", include("users.urls")),  # ← Make sure this line exists
    path("api/scholarships/", include("scholarships.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)