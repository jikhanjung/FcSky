from django.urls import path

from . import views

app_name = "teams"

urlpatterns = [
    path("", views.home, name="home"),
    path("teams/", views.team_list, name="list"),
    path("teams/add/", views.team_create, name="team_add"),
    # Player(멤버 마스터) 전체 관리 — 팀과 무관한 선수 레코드 CRUD(삭제는 soft delete)
    path("manage/players/", views.player_manage, name="player_manage"),
    path("manage/players/add/", views.player_create, name="player_create"),
    path("manage/players/<int:pk>/edit/", views.player_master_edit, name="player_master_edit"),
    path("manage/players/<int:pk>/delete/", views.player_master_delete, name="player_master_delete"),
    path("manage/players/<int:pk>/restore/", views.player_restore, name="player_restore"),
    path("teams/<slug:slug>/edit/", views.team_edit, name="team_edit"),
    path("teams/<slug:slug>/players/add/", views.player_add, name="player_add"),
    path("teams/<slug:slug>/players/<int:pk>/edit/", views.player_edit, name="player_edit"),
    path("teams/<slug:slug>/players/<int:pk>/remove/", views.player_remove, name="player_remove"),
    path("teams/<slug:slug>/", views.team_detail, name="detail"),
    path("players/<int:pk>/", views.player_detail, name="player"),
]
