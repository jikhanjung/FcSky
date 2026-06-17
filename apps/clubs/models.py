from django.conf import settings
from django.db import models


class Club(models.Model):
    """테넌트(클럽). 멀티테넌트 SaaS 전환의 루트 — 모든 클럽 단위 데이터가 이 FK로 묶인다.

    slug 는 URL 식별자라 전역 unique. (Phase A: 데이터 모델만 도입, 스코핑은 Phase B)
    """

    name = models.CharField("클럽명", max_length=120)
    slug = models.SlugField("URL 슬러그", max_length=140, unique=True)
    logo = models.ImageField("로고", upload_to="clubs/logos/", blank=True)
    is_active = models.BooleanField("활성", default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "클럽"
        verbose_name_plural = "클럽"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ClubMembership(models.Model):
    """사용자의 클럽 소속·역할. 전역 is_staff 대신 클럽별 운영진 판정에 사용(Phase C)."""

    class Role(models.TextChoices):
        OWNER = "OWNER", "소유자"
        STAFF = "STAFF", "운영진"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="club_memberships", verbose_name="사용자",
    )
    club = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="memberships", verbose_name="클럽",
    )
    role = models.CharField("역할", max_length=8, choices=Role.choices, default=Role.STAFF)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "클럽 멤버십"
        verbose_name_plural = "클럽 멤버십"
        unique_together = [("user", "club")]
        ordering = ["club", "user"]

    def __str__(self):
        return f"{self.user} @ {self.club} ({self.get_role_display()})"
