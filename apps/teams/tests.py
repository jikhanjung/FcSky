from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from apps.matches.models import Match
from apps.teams.models import Player, Team


class PublicPagesSmokeTest(TestCase):
    """시드 데이터 기반 공개 페이지 스모크 테스트."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed")

    def test_list_pages_ok(self):
        for url in ["/", "/teams/", "/matches/", "/matches/scorers/",
                    "/stats/", "/standings/", "/awards/", "/notices/",
                    "/gallery/"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_detail_pages_ok(self):
        self.assertEqual(
            self.client.get(f"/matches/{Match.objects.first().pk}/").status_code, 200)
        self.assertEqual(
            self.client.get(f"/players/{Player.objects.first().pk}/").status_code, 200)
        self.assertEqual(
            self.client.get(f"/teams/{Team.objects.first().slug}/").status_code, 200)

    def test_seed_idempotent(self):
        before = Player.objects.count()
        call_command("seed")  # 다시 실행해도 중복 생성 없음
        self.assertEqual(Player.objects.count(), before)


class AuthTest(TestCase):
    """운영진 로그인 / 방문자 구분."""

    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user(
            "관리자아이디", password="pw1234", is_staff=True)

    def test_login_page_ok(self):
        resp = self.client.get("/accounts/login/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "운영진 로그인")

    def test_anonymous_sees_login_link(self):
        resp = self.client.get("/")
        self.assertContains(resp, "로그인")
        self.assertNotContains(resp, "로그아웃")

    def test_staff_sees_admin_and_logout(self):
        self.client.force_login(self.staff)
        resp = self.client.get("/")
        self.assertContains(resp, "로그아웃")
        self.assertContains(resp, "/admin/")

    def test_logout_redirects_home(self):
        self.client.force_login(self.staff)
        resp = self.client.post("/accounts/logout/")
        self.assertRedirects(resp, "/")
