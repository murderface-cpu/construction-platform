from django.urls import path
from .views import DesignDetailView, DesignListView, MySavedDesignsView, SaveDesignView

urlpatterns = [
    path("", DesignListView.as_view(), name="design-list"),
    path("saved/", MySavedDesignsView.as_view(), name="saved-designs"),
    path("<uuid:pk>/", DesignDetailView.as_view(), name="design-detail"),
    path("<uuid:pk>/save/", SaveDesignView.as_view(), name="design-save"),
]
