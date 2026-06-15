"""경기 집계 헬퍼.

통계 대시보드(stats)와 시즌 아카이브(season_detail)가 공유하는 집계 로직을 모은다.
시즌 단위 필터를 인자로 받아 동일한 결과 구조를 반환한다.
"""

from django.db.models import Count

from .models import Match, MatchEvent

# 부문(연령대) 표시 순서.
AGE_ORDER = {"K7": 0, "40": 1, "50": 2}


def finished_matches(season=None):
    """점수가 입력된 종료 경기 쿼리셋. season(id)이 주어지면 해당 시즌으로 한정."""
    qs = Match.objects.filter(
        status=Match.Status.FINISHED,
        our_score__isnull=False,
        opponent_score__isnull=False,
    )
    if season and str(season).isdigit():
        qs = qs.filter(season_id=season)
    return qs


def club_record(matches):
    """팀별 전적 리스트와 클럽 합계 dict를 반환.

    반환: (teams, club)
      teams — 부문 순으로 정렬된 팀별 전적 dict 리스트
      club  — 전 팀 합산 전적 dict
    """
    team_rows = {}
    for m in matches.select_related("our_team"):
        r = team_rows.setdefault(
            m.our_team_id,
            {"team": m.our_team, "p": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0},
        )
        r["p"] += 1
        r["gf"] += m.our_score
        r["ga"] += m.opponent_score
        result = m.result
        if result == "W":
            r["w"] += 1
        elif result == "L":
            r["l"] += 1
        else:
            r["d"] += 1

    club = {"p": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0}
    teams = []
    for r in team_rows.values():
        r["gd"] = r["gf"] - r["ga"]
        r["pts"] = r["w"] * 3 + r["d"]
        r["winrate"] = round(r["w"] / r["p"] * 100) if r["p"] else 0
        for k in ("p", "w", "d", "l", "gf", "ga"):
            club[k] += r[k]
        teams.append(r)
    teams.sort(key=lambda x: AGE_ORDER.get(x["team"].age_group, 9))
    club["gd"] = club["gf"] - club["ga"]
    club["winrate"] = round(club["w"] / club["p"] * 100) if club["p"] else 0
    return teams, club


def our_events(season=None):
    """우리 팀(선수 지정) 이벤트 쿼리셋. season(id)이 주어지면 해당 시즌으로 한정."""
    ev = MatchEvent.objects.filter(
        side=MatchEvent.Side.OUR, player__isnull=False
    )
    if season and str(season).isdigit():
        ev = ev.filter(match__season_id=season)
    return ev


def event_ranking(events, event_type, limit=None):
    """이벤트 종류별 선수 순위 리스트(player_id·player__name·n). limit이 있으면 상위 N명."""
    qs = (
        events.filter(event_type=event_type)
        .values("player_id", "player__name")
        .annotate(n=Count("id"))
        .order_by("-n", "player__name")
    )
    if limit:
        qs = qs[:limit]
    return list(qs)
