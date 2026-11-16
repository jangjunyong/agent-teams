---
description: 아이디어 md 하나를 기획 파이프라인(3관점 기획안 병렬 → 적대적 심사 → 스펙 → 실행 계획)에 태운다. hq-core 그래프 규약으로 실행되어 runs/ 에 기록된다. 결과는 G1(originality) 통과 전까지 확정이 아니다
argument-hint: "<아이디어 md 경로>  예) _work/idea.md"
---

hq-core 의 **graph 스킬 규약**대로 `planning-team/plan` 그래프를 `target=$ARGUMENTS` 로 실행하라.
HQ=`%AI_HQ_ROOT%\teams\hq-core\scripts\hq.py`.

1. 회차를 정한다. `_work/plan/<stem>.judge.md` 가 있고 그 frontmatter 가 `winner: NONE` 이면 round = 그 파일의 `round` + 1, 아니면 round = 1.
   round ≥ 2 면 이전 심사표를 `_work/plan/<stem>.judge.r<이전 round>.md` 로, 이전 기획안 세 개를 `.option-{a,b,c}.r<이전 round>.md` 로 보존한다 (덮어쓰지 않는다).
2. `py HQ run start planning-team/plan target=$ARGUMENTS round=<round>` → 실행 계획을 받는다. 이 출력만 보고 진행한다.
3. 노드를 규약대로 처리한다.
   - **brainstorm_a / brainstorm_b / brainstorm_c** 는 서로 독립이다. `node start` 세 번 → Agent 를 **한 메시지에 세 개** 병렬 호출 → 각각 `node done`.
     서브에이전트에게는 계획의 prompt 를 **그대로** 준다 (관점 줄 포함). 작성 맥락·옹호성 설명을 덧붙이지 않는다.
     round ≥ 2 면 prompt 끝에 "추가 입력: `_work/plan/<stem>.judge.r<이전 round>.md` 의 #7 재기획 지시(자기 관점 항목만)" 한 줄만 덧붙인다.
   - **judge** 는 세 option 이 모두 done 인 뒤에. prompt 의 `round:` 자리에 현재 회차를 넣어 준다. 결과 파일의 `winner` 를 읽는다.
   - **spec** 은 `winner` 가 A|B|C 일 때만. NONE 이면 `node skip spec --note "judge NONE"`, `node skip plan --note "judge NONE"` 후 4번으로.
   - **plan** 은 오케스트레이터가 **plan-format 스킬 4절** 규격대로 `_work/<stem>.plan.md` 를 직접 쓴다. 심사표·스펙에 적힌 것만 근거로 삼고 요약·윤색하지 않는다. `status: draft`, `gate: G1-pending`, 본문 첫 줄 G1 인용문 유지. "확정"이라고 쓰지 않는다.
4. 종료 처리.
   - winner A|B|C 이고 plan 까지 done → `run end --status done`.
   - winner NONE 이고 round < 2 → `run end --status failed --note "judge NONE, loopback"` 후 사용자에게 NONE 사유(심사표 #7)를 보고하고 같은 커맨드 재실행을 안내한다 (재실행이 round 2 다).
   - winner NONE 이고 round ≥ 2 → `run end --status escalated` 후 사람에게 에스컬레이션: 두 심사표 경로, 여섯 기획안 경로, NONE 사유 요약. 더 돌리지 않는다.
5. 사용자 보고: 승자(A|B|C, 관점) · 채점표 합계 3개 · 승자의 치명 약점 1줄 · 살릴 아이디어 개수 · 다음 액션(`/verify-team:verify _work/<stem>.plan.md`) · run_id · 산출물 경로 전부.

규칙: 기획안 작성자는 서로의 안을 보지 않는다. 심사관·스펙 작성자는 파일만 보고 판단한다. 기획팀은 `approved` 를 쓰지 않는다 — 승인은 verify-team 판정 뒤 오케스트레이터의 일이다(G1). 같은 아이디어의 NONE 루프백은 최대 2회(judge `round` 로 추적). 3회째는 사람에게.
