from django.urls import path

from . import views

app_name = "competitions"

urlpatterns = [
    path("standings/", views.standings, name="standings"),
    path("awards/", views.awards, name="awards"),
    path("seasons/", views.season_index, name="season_index"),
    path("seasons/<int:pk>/", views.season_detail, name="season_detail"),
]
