from django.urls import path
from . import views

urlpatterns = [
    # Scholarship catalogue
    path("",           views.scholarship_list,   name="scholarship-list"),
    path("<int:pk>/",  views.scholarship_detail, name="scholarship-detail"),

    # Saved / bookmarked scholarships
    path("saved/",            views.saved_list,        name="saved-list"),
    path("saved/<int:pk>/",   views.save_scholarship,  name="save-scholarship"),

    # Dashboard stat cards
    path("stats/",            views.stats_view,        name="scholarship-stats"),
]
