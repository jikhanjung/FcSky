# 20260616_031 — 유튜브 임베드 referrerpolicy 수정 + 폴백 링크

## 증상
- 임베드 영상이 "Error 153"으로 재생 안 됨(공개·임베드 가능한 영상인데도).

## 원인 / 수정
- iframe에 `referrerpolicy`가 없어 YouTube가 referer를 못 받아 재생 거부.
  → `referrerpolicy="strict-origin-when-cross-origin"` 추가(YouTube 권장값).
- 공유 링크의 `?si=...`(추적 토큰)는 임베드에 불필요 — `extract_youtube_id()`가 ID만 추출하므로
  이미 무시됨. 임베드는 소유자 아니어도 공개/일부공개+퍼가기 허용이면 ID만으로 가능.

## 추가 (안전망)
- 각 영상 위에 **"유튜브에서 보기 ↗"** 링크(`MatchVideo.watch_url`) — 임베드 실패 영상도 클릭 시청 가능.

## 배포
- `honestjung/fcsky:0.2.9`.
