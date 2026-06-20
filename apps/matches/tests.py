from datetime import timedelta

from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from django.utils import timezone

from apps.clubs.models import Club
from apps.competitions.models import Competition, CompetitionEntry
from apps.teams.models import Player, Team

from .models import Match, Opponent
from .views import _handle_live_action


class MatchResultTest(TestCase):
    """Match.result 프로퍼티(승/무/패/미정) 검증 — home/away entry 기준 우리 관점."""

    @classmethod
    def setUpTestData(cls):
        cls.club = Club.objects.create(name="클럽", slug="c")
        cls.team = Team.objects.create(name="우리", slug="us", age_group="50", club=cls.club)
        cls.opp = Opponent.objects.create(name="상대")
        cls.comp = Competition.objects.create(
            name="컵", slug="cup", kind=Competition.Kind.TOURNAMENT)
        cls.our_e = CompetitionEntry.objects.create(competition=cls.comp, team=cls.team)
        cls.opp_e = CompetitionEntry.objects.create(competition=cls.comp, opponent=cls.opp)

    def _match(self, gf, ga):
        # 우리 팀을 home 으로 두면 our_score=home_score.
        return Match.objects.create(
            club=self.club, competition=self.comp, kickoff=timezone.now(),
            home_entry=self.our_e, away_entry=self.opp_e,
            home_score=gf, away_score=ga)

    def test_win(self):
        self.assertEqual(self._match(2, 1).result, "W")

    def test_draw(self):
        self.assertEqual(self._match(1, 1).result, "D")

    def test_loss(self):
        self.assertEqual(self._match(0, 2).result, "L")

    def test_unscored_is_none(self):
        self.assertIsNone(self._match(None, None).result)


class LiveStartTest(TestCase):
    """중계 콘솔 'LIVE 시작' 의 live_started_at 처리:
    예정→시작은 시각을 새로 세팅, 종료→재개는 기존 시각 보존."""

    @classmethod
    def setUpTestData(cls):
        cls.club = Club.objects.create(name="클럽", slug="c")
        cls.team = Team.objects.create(name="우리", slug="us", age_group="50", club=cls.club)
        cls.opp = Opponent.objects.create(name="상대")
        cls.comp = Competition.objects.create(
            name="컵", slug="cup", kind=Competition.Kind.TOURNAMENT)
        cls.our_e = CompetitionEntry.objects.create(competition=cls.comp, team=cls.team)
        cls.opp_e = CompetitionEntry.objects.create(competition=cls.comp, opponent=cls.opp)

    def _match(self, status, live_started_at):
        return Match.objects.create(
            club=self.club, competition=self.comp, kickoff=timezone.now(),
            home_entry=self.our_e, away_entry=self.opp_e,
            status=status, live_started_at=live_started_at)

    def _start(self, match):
        req = RequestFactory().post("/", {"action": "start"})
        req.session = {}
        setattr(req, "_messages", FallbackStorage(req))
        _handle_live_action(req, match, Player.objects.none())

    def test_fresh_start_resets_time(self):
        """예정 상태에서 시작하면 옛 live_started_at 을 무시하고 새로 세팅."""
        stale = timezone.now() - timedelta(hours=2)
        match = self._match(Match.Status.SCHEDULED, stale)
        self._start(match)
        match.refresh_from_db()
        self.assertEqual(match.status, Match.Status.LIVE)
        self.assertGreater(match.live_started_at, stale)

    def test_resume_preserves_time(self):
        """종료 후 재개는 시계 연속성을 위해 기존 시각 보존."""
        started = timezone.now() - timedelta(hours=1)
        match = self._match(Match.Status.FINISHED, started)
        self._start(match)
        match.refresh_from_db()
        self.assertEqual(match.status, Match.Status.LIVE)
        self.assertEqual(match.live_started_at, started)

    def test_first_start_sets_time(self):
        """처음 시작(시각 없음)이면 현재 시각으로 세팅."""
        match = self._match(Match.Status.SCHEDULED, None)
        self._start(match)
        match.refresh_from_db()
        self.assertIsNotNone(match.live_started_at)
