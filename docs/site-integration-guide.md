# Site Integration Guide

## Goal

`1% Better Counter`를 메인 사이트 밖의 별도 앱처럼 두지 않고,
`onepercentbetter.poker` 안의 자연스러운 제품 진입점으로 둔다.

## Product Architecture

사이트 안에는 지금 두 개의 입구가 있다.

### 1. Upload Review

역할:

- 이미 끝난 플레이를 업로드한다.
- 패턴을 해석한다.
- 다음 조정 하나를 제안한다.

유저 감정:

- `내가 뭘 반복하는지 알고 싶다`

### 2. Live Counter

역할:

- 지금 세션에서 한 행동을 의식한다.
- 한 습관만 잡는다.
- 기록을 남긴다.

유저 감정:

- `오늘은 이거 하나만 바꿔본다`

## Why They Belong Together

둘은 같은 문제를 다른 시점에서 푼다.

- Counter = before / during session
- Upload review = after session

같은 철학:

- 패턴을 본다
- 작은 조정을 한다
- 1% better를 쌓는다

## Current Integration Approach

홈에서 카운터는 너무 크게 주도권을 잡지 않는다.

현재 배치:

- 상단 `Live counter`
- 히어로 `Open counter`
- 중간 `One promise. One session.` 섹션

이유:

- 카운터가 메인 제품을 먹어버리면 안 된다.
- 하지만 숨겨두면 독립 유저 진입이 죽는다.
- 그래서 `보조 진입점이지만 분명한 제품`으로 보여야 한다.

## Current Messaging Structure

홈 메시지:

- 업로드 = 패턴 읽기
- 카운터 = 라이브 자기 약속

현재 연결 문장:

- `Upload one tournament for a pattern read.`
- `Or walk into a live session with one habit and count it honestly.`

## Branding Rule

카운터는 별도 브랜드가 아니다.

규칙:

- 항상 `onepercentbetter.poker` 세계 안에서 보인다
- 홈과 같은 색/재질/태도를 쓴다
- 카운터만 다른 앱처럼 보여선 안 된다

## UX Rule

홈은 이해를 돕는다.
카운터는 즉시 행동하게 만든다.

즉:

- 홈 = read
- counter = tap

## Recommended Direction Going Forward

### Keep

- 홈에서 카운터 진입 열어두기
- 업로드와 카운터를 같은 제품군처럼 설명하기
- 카운터를 `live tool`로 포지셔닝하기

### Improve

- 홈의 카운터 미리보기 카드를 실제 카운터 UI와 더 가깝게 맞추기
- 업로드 리뷰 CTA와 카운터 CTA의 우선순위 더 세밀하게 다듬기
- 카운터 완료 화면에서 업로드 리뷰로 이어지는 CTA 설계

### Avoid

- 카운터를 메인 브랜드와 완전히 분리하기
- 카운터가 단순 클릭커를 넘어 너무 많은 설명을 하게 두기
- 홈에서 카운터가 업로드 제품보다 더 중요해 보이게 만들기

## Ideal Journey

### Journey A

1. 유저가 홈에 온다
2. 무료 업로드 리뷰를 본다
3. 패턴 해석의 가치를 이해한다
4. 더 가벼운 입구로 카운터도 시도한다

### Journey B

1. 유저가 카운터를 먼저 쓴다
2. 자기 습관을 세기 시작한다
3. `내가 반복하는 패턴을 더 알고 싶다`가 생긴다
4. 업로드 리뷰로 들어간다

이 두 흐름이 모두 자연스러워야 한다.

