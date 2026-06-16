from django.urls import path

from . import views

app_name = "competitions"

urlpatterns = [
    path("standings/", views.standings, name="standings"),
    path("awards/", views.awards, name="awards"),
    path("years/", views.year_index, name="year_index"),
    path("years/<int:year>/", views.year_detail, name="year_detail"),
    # 대회 관리(staff) — <slug> 경로보다 먼저 둔다.
    path("manage/competitions/", views.competition_manage, name="competition_manage"),
    path("manage/competitions/add/", views.competition_create, name="competition_create"),
    path("manage/competitions/<slug:slug>/edit/", views.competition_edit, name="competition_edit"),
    path("manage/competitions/<slug:slug>/delete/", views.competition_delete, name="competition_delete"),
    # 대회 목록·상세 (공개)
    path("competitions/", views.competition_list, name="competition_list"),
    path("competitions/<slug:slug>/", views.competition_detail, name="competition_detail"),
]
