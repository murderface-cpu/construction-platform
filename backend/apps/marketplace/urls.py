"""URL routes for the marketplace app."""

from django.urls import path

from .views import (
    ContractorDetailView,
    ContractorListView,
    MyContractorProfileView,
    PortfolioImageUploadURLView,
    PortfolioProjectDetailView,
    PortfolioView,
)

urlpatterns = [
    # Public contractor browsing
    path("", ContractorListView.as_view(), name="contractor-list"),
    path("<uuid:pk>/", ContractorDetailView.as_view(), name="contractor-detail"),

    # Contractor self-management
    path("me/", MyContractorProfileView.as_view(), name="contractor-me"),
    path("me/portfolio/", PortfolioView.as_view(), name="portfolio-list"),
    path("me/portfolio/<uuid:pk>/", PortfolioProjectDetailView.as_view(), name="portfolio-detail"),
    path("me/portfolio/<uuid:pk>/upload-url/", PortfolioImageUploadURLView.as_view(), name="portfolio-upload-url"),
]
