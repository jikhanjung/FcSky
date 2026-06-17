"""Phase A 데이터 마이그레이션 — 기존 단일 클럽(FC Sky) 데이터를 테넌트로 귀속.

- `fcsky` 클럽 1건 생성
- club FK 가 추가된 8개 루트 모델의 기존 행 전부 club=fcsky 로 backfill
- 기존 운영진(is_staff)·관리자(is_superuser) → ClubMembership(fcsky) 생성
"""
from django.conf import settings
from django.db import migrations, models


# (app_label, model_name) — club FK 가 직접 달린 루트 모델들.
ROOT_MODELS = [
    ("teams", "Team"),
    ("teams", "Player"),
    ("matches", "Opponent"),
    ("matches", "Match"),
    ("matches", "OpponentMatch"),
    ("notices", "Notice"),
    ("gallery", "GalleryItem"),
    ("competitions", "Award"),
]


def backfill(apps, schema_editor):
    Club = apps.get_model("clubs", "Club")
    ClubMembership = apps.get_model("clubs", "ClubMembership")

    club, _ = Club.objects.get_or_create(
        slug="fcsky", defaults={"name": "FC Sky", "is_active": True}
    )

    for app_label, model_name in ROOT_MODELS:
        Model = apps.get_model(app_label, model_name)
        Model.objects.filter(club__isnull=True).update(club=club)

    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    for u in User.objects.filter(models.Q(is_staff=True) | models.Q(is_superuser=True)):
        ClubMembership.objects.get_or_create(
            user=u, club=club,
            defaults={"role": "OWNER" if u.is_superuser else "STAFF"},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("clubs", "0001_initial"),
        ("teams", "0006_player_club_team_club_alter_team_slug_and_more"),
        ("competitions", "0006_award_club"),
        ("matches", "0012_match_club_opponent_club_opponentmatch_club_and_more"),
        ("notices", "0002_notice_club"),
        ("gallery", "0002_galleryitem_club"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
