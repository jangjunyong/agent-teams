---
description: 기획/스펙 md 하나를 디자인 파이프라인(2방향 방향서+HTML 목업 병렬 → 적대적 비평 → 디자인 스펙)에 태운다. hq-core 그래프 규약으로 실행되어 runs/ 에 기록된다. 스펙은 verify-team 검증 전까지 확정이 아니다
argument-hint: '<기획/스펙 md 경로>  예) _work/plan/idea.spec.md'
---

hq-core 의 **graph 스킬 규약**대로 `design-team/design` 그래프를 `target=$ARGUMENTS` 로 실행하라.
HQ=`%AI_HQ_ROOT%\teams\hq-core\scripts\hq.py`.

1. 회차를 정한다. `_work/design/<stem>.critique.md` 가 있고 그 frontmatter 가 `winner: NONE` 이면 round = 그 파일의 `round` + 1, 아니면 round = 1.
   round ≥ 2 면 이전 비평표를 `_work/design/<stem>.critique.r<이전 round>.md` 로, 이전 방향 파일 4개를 `.dir-a.r<이전 round>.md` `.dir-a.r<이전 round>.html` `.dir-b.r<이전 round>.md` `.dir-b.r<이전 round>.html` 로 보존한다 (덮어쓰지 않는다).
2. `py HQ run start design-team/design target=$ARGUMENTS round=<round>` → 실행 계획을 받는다. 이 출력만 보고 진행한다.
3. 노드를 규약대로 처리한다.
   - **direction_a / direction_b** 는 서로 독립이다. `node start` 두 번 → Agent 를 **한 메시지에 두 개** 병렬 호출 → 각각 `node done`.
     서브에이전트에게는 계획의 prompt 를 **그대로** 준다 (방향 줄 포함). 작성 맥락·옹호성 설명을 덧붙이지 않는다.
     round ≥ 2 면 prompt 끝에 "추가 입력: `_work/design/<stem>.critique.r<이전 round>.md` 의 #9 재작업 지시(자기 방향 항목만)" 한 줄만 덧붙인다.
   - **critique** 는 두 방향의 4파일이 모두 done 인 뒤에. prompt 의 `<오케스트레이터가 알려준 회차>` 자리에 현재 round 를 넣어 준다. 결과 파일의 `winner` 를 읽는다.
   - **spec** 은 `winner` 가 A|B 일 때만. 오케스트레이터가 **design-spec 스킬 4절** 규격대로 `_work/<stem>.design-spec.md` 를 직접 쓴다. 비평표·승자 방향서·승자 목업에 적힌 것만 근거로 삼고 요약·윤색하지 않는다. 패자 파일은 읽지 않는다. `status: in-review`, 제목에 '(미확정)' 유지, critique #6 필수 수정은 #9 비평 반영 내역에서 전부 처리. "확정"이라고 쓰지 않는다. `winner` 가 NONE 이면 `node skip spec --note "critique NONE"` 후 4번으로.
4. 종료 처리.
   - winner A|B 이고 spec 까지 done → `run end --status done`.
   - winner NONE 이고 round < 2 → `run end --status failed --note "critique NONE, loopback"` 후 사용자에게 NONE 사유(비평표 #9 재작업 지시)를 보고하고 같은 커맨드 재실행을 안내한다 (재실행이 round 2 다).
   - winner NONE 이고 round ≥ 2 → `run end --status escalated` 후 사람에게 에스컬레이션: 두 비평표 경로, 방향 파일 8개 경로, NONE 사유 요약. 더 돌리지 않는다.
5. 사용자 보고: 승자(A|B, 방향) · 채점표 합계 2개 · 승자의 필수 수정 1줄 · 패자에서 가져온 요소 개수 · 다음 액션(`/verify-team:verify _work/<stem>.design-spec.md`) · run_id · 산출물 경로 전부.

규칙: 두 방향 작성자는 서로의 파일을 보지 않는다. 비평가는 방향서의 자기 설명이 아니라 HTML 파일의 실제 값(hex·px·선택자)만 근거로 삼는다. 디자인팀은 `approved` 를 쓰지 않는다 — 승인은 verify-team 판정 뒤 오케스트레이터의 일이다(G3). 같은 대상의 NONE 루프백은 최대 2회(critique `round` 로 추적). 3회째는 사람에게.
