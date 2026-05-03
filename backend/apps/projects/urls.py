"""URL routes for the projects app."""

from django.urls import path

from .views import (
    AssignContractorView,
    MilestoneDetailView,
    MilestoneListCreateView,
    ProjectDetailView,
    ProjectListCreateView,
)

urlpatterns = [
    path("", ProjectListCreateView.as_view(), name="project-list-create"),
    path("<uuid:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("<uuid:pk>/assign/", AssignContractorView.as_view(), name="project-assign"),
    path("<uuid:pk>/milestones/", MilestoneListCreateView.as_view(), name="milestone-list-create"),
    path("<uuid:pk>/milestones/<uuid:mid>/", MilestoneDetailView.as_view(), name="milestone-detail"),
]
