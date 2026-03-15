# Status Report

기준일: `2026-03-15`

## Summary

오늘까지의 핵심 결과는 아래와 같다.

- `onepercentbetter.poker`를 포커 전용 랜딩 기준으로 다시 복구했다.
- `/counter`는 별도 실험물이 아니라 메인 제품군 안의 라이브 도구로 다시 연결했다.
- 카운터 컬러와 분위기를 랜딩의 포커 톤에 맞춰 재정렬했다.
- `counter` 작업물은 살아 있고, 홈은 포커 전용 방향으로 유지된다.

## Current Live State

- 메인 도메인: `https://onepercentbetter.poker`
- 카운터: `https://onepercentbetter.poker/counter`
- 현재 기준 프로덕션 배포:
  - `frontend-oqnkrtezh-sukmincs-projects.vercel.app`

## What Was Restored

포커 전용 홈은 로컬 저장소 `one-percent-better-poker-site`를 기준으로 복구했다.

복구된 핵심:

- 포커 전용 히어로
- 무료 업로드 리뷰 데모
- MVP promise 섹션
- 철학 섹션
- 후원 섹션
- 포커 메타데이터와 아이콘

현재 코드 위치:

- 홈: `/Users/chrisyoon/GitHub/one-percent-better-poker/frontend/app/page.tsx`
- 레이아웃: `/Users/chrisyoon/GitHub/one-percent-better-poker/frontend/app/layout.tsx`
- 글로벌 스타일: `/Users/chrisyoon/GitHub/one-percent-better-poker/frontend/app/globals.css`
- 리뷰 데모: `/Users/chrisyoon/GitHub/one-percent-better-poker/frontend/app/components/InstantReviewDemo.tsx`
- 리뷰 API: `/Users/chrisyoon/GitHub/one-percent-better-poker/frontend/app/api/review/route.ts`

## Counter Work Preserved

카운터 본체는 살아 있다.

핵심 파일:

- `/Users/chrisyoon/GitHub/one-percent-better-poker/frontend/app/components/HookTracker.tsx`
- `/Users/chrisyoon/GitHub/one-percent-better-poker/frontend/app/counter/page.tsx`
- `/Users/chrisyoon/GitHub/one-percent-better-poker/frontend/app/hook/page.tsx`
- `/Users/chrisyoon/GitHub/one-percent-better-poker/frontend/tests/hook.spec.ts`

현재 카운터 요약:

- 액션: `Fold`, `Call`, `Raise`
- 목표 타입: `More`, `Less`
- 목표 범위:
  - `More`: `1-5`
  - `Less`: `0-5`
- 숨은 확장:
  - 포지션 선택
  - `Time Structure`는 `In progress`
- 진행 UI:
  - 원형 카운트 버튼
  - 진행률 링 일체형
- 완료 화면:
  - 목표 달성, 오버골, 미달성 모두 다른 메시지

## Counter + Site Integration Done

홈에 카운터를 너무 크게 밀어붙이지 않고 자연스럽게 녹였다.

추가된 것:

- 상단 `Live counter` 진입 버튼
- 히어로 `Open counter` CTA
- `One promise. One session.` 카운터 소개 섹션

의도:

- 업로드 리뷰와 카운터가 서로 경쟁하지 않게 한다.
- 둘 다 같은 철학의 다른 입구처럼 보이게 한다.

## Counter Visual Update Done

카운터는 원래의 보라 계열에서 랜딩페이지 팔레트로 이동했다.

현재 팔레트:

- 배경: 딥 네이비
- 주 액션: 블루
- 성취/오버골: 오렌지
- 보조 하이라이트: 밝은 블루/화이트

의미:

- 홈과 카운터가 이제 같은 서비스처럼 보인다.
- 이전보다 덜 앱 조각 같고, 더 제품군처럼 느껴진다.

## Important Product Decisions Made

- 카운터는 상대 기록보다 자기 성찰이 우선이다.
- 카운터는 `한 세션, 한 습관, 한 약속` 구조로 간다.
- 너무 많은 포커 용어는 피하지만, 포커 맥락은 잃지 않는다.
- 완벽한 분석보다 `반복 가능한 작은 변화`를 우선한다.
- 업로드 분석은 `패턴 해석`
- 카운터는 `실전 자기 트래킹`

## Known Cleanup Items

아직 정리되지 않은 작업 산출물:

- `frontend/.design-previews/`
- `frontend/playwright-report/`
- `frontend/test-results/`

이건 기능에는 영향 없지만, 작업트리를 깔끔하게 만들려면 나중에 정리하는 것이 좋다.

## Residual Risks

- 카운터는 아직 많은 실험의 흔적이 남아 있어서, 카피와 세부 UI는 더 정리할 여지가 있다.
- 홈과 카운터는 지금 같은 브랜드 톤으로 묶였지만, 완료 화면의 문장 톤은 한 번 더 다듬을 수 있다.
- `Time Structure`는 아직 기능이 아니라 기대 슬롯이다.

## Recommended Next Steps

1. 카운터 완료 화면의 문구를 포커 전용 랜딩 문체에 맞게 더 날카롭게 다듬기
2. 카운터 원형 버튼의 재질감과 인터랙션을 더 제품스럽게 다듬기
3. 홈의 카운터 소개 섹션을 실제 카운터 UI와 더 닮게 조정하기
4. `Time Structure`를 실제 기능으로 붙일지 계속 teaser로 둘지 결정하기
5. 문서 기준점이 생겼으니, 다음부터는 큰 변경 전 스냅샷 브랜치나 태그 남기기

