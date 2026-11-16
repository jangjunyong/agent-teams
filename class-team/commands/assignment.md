---
description: 과제 설명 md 하나를 과제 파이프라인(요구사항 분해 → 해결 초안/계획 → 채점자 관점 적대적 검토 → 제출 전 체크리스트·수정 계획)에 태운다. hq-core 그래프 규약으로 실행되어 runs/ 에 기록된다. 제출물을 대신 만들지 않는다 — 구조·계획·점검까지다
argument-hint: '<과제 설명 md 경로> <과목명>   예: _work/hw2.md 운영체제'
---

hq-core 의 **graph 스킬 규약**대로 `class-team/assignment` 그래프를 실행하라.
HQ=`%AI_HQ_ROOT%\teams\hq-core\scripts\hq.py` (환경변수 AI_HQ_ROOT 가 있으면 그 아래).

0. **인자를 나눈다.** `$ARGUMENTS` 의 첫 토큰 = `target`(과제 설명 md 경로), 나머지 전부 = `course`(과목명).
   - target 파일이 없으면 실행하지 말고 경로를 다시 달라고 한다. course 가 비어 있으면 과목명을 물어본다(임의로 정하지 않는다)
   - course 에 공백이 있으면 하이픈으로 잇는다
   - 회차: `_work/class/<stem>.grade.md` 가 있고 frontmatter `grade_verdict` 가 REVISE|FAIL 이면 round = 그 파일의 `round` + 1, 아니면 round = 1.
     round ≥ 2 면 이전 채점표를 `_work/class/<stem>.grade.r<이전 round>.md`, 이전 초안을 `.draft.r<이전 round>.md` 로 보존한다. 이전 채점표 #2 에 req 지적이 있으면 `.req.r<이전 round>.md` 도 보존한다(덮어쓰지 않는다)
1. `py HQ run start class-team/assignment target=<경로> course=<과목> round=<round>` → run_id 와 실행 계획을 받는다. 이 출력만 보고 진행한다.
2. 노드를 규약대로 처리한다: decompose → draft → grade → plan (순차. 각 노드가 앞 노드 출력을 읽는다).
   - 서브에이전트에게는 계획에 찍힌 prompt 를 **그대로** 준다. 과제의 배경·원하는 점수·"대신 해 줘" 류 맥락을 덧붙이지 않는다.
   - **decompose**: round ≥ 2 이고 이전 채점표 #2 에 req 지적이 있을 때만 다시 호출한다(prompt 끝에 "추가 입력: `_work/class/<stem>.grade.r<이전 round>.md` 의 #2·#6(대상 req 행)" 한 줄). 그 외 round ≥ 2 면 `node skip --note "기존 산출물 사용"`.
   - **draft**: prompt 의 `round:` 자리에 현재 회차. round ≥ 2 면 prompt 끝에 "추가 입력: `_work/class/<stem>.grade.r<이전 round>.md` 의 #6 수정 요구(대상 draft 행 전부). 이전 초안 `.draft.r<이전 round>.md` 는 번호 유지 확인용" 한 줄을 덧붙인다.
   - **grade**: prompt 의 `round:` 자리에 현재 회차. round ≥ 2 면 "이전 채점표: `_work/class/<stem>.grade.r<이전 round>.md` (수정 요구 반영 확인용)" 한 줄을 덧붙인다. 결과 파일의 `grade_verdict` 와 `expected_score` 를 읽는다.
   - **plan**: 오케스트레이터가 **assignment-plan 스킬 4절** 규격대로 `_work/<stem>.assignment-plan.md` 를 직접 쓴다. req·draft·grade 세 파일에 적힌 것만 근거로 삼고 요약·윤색하지 않는다. grade #6 수정 요구를 전부 수정 계획에 옮기고, grade #1 의 req 누락 지적도 대응표에 넣는다. `run` 에 run_id, `round` 에 회차, `grade` 에 grade_verdict, `expected_score` 에 `<점수>/<만점>`, `status` 는 PASS 면 `in-review` 아니면 `draft`.
   - 각 노드 `node start` → 호출 → `node done`. `node done` 이 frontmatter 누락으로 exit 2 면 보완 지시 1회, 그래도 실패면 `node fail`.
3. 종료 처리.
   - **PASS** → plan 까지 done → `run end --status done`.
   - **REVISE / FAIL** 이고 round < 2 → plan 은 `status: draft` 로 쓰고 `run end --status failed --note "grade <판정>, loopback"` 후 사용자에게 판정 근거(채점표 #5)·예상 점수·수정 요구 개수를 보고하고 같은 커맨드 재실행을 안내한다(재실행이 round 2 다).
   - **REVISE / FAIL** 이고 round ≥ 2 → plan 은 `status: draft`, `grade: <판정>` 으로 쓰고 `run end --status escalated` 후 사람에게 에스컬레이션: 두 채점표 경로, 미해결 수정 요구, 표절·출처 위험 항목. 더 돌리지 않는다.
4. 사용자 보고: grade 판정 · 예상 점수/만점 · 요구사항 수와 대응 상태(완료/수정 필요/미착수 개수) · 표절·출처 위험 항목 · 사람이 결정할 것(req #5) · 마감 · 다음 액션(수정 계획 1순위) · run_id · 산출물 경로 전부(`_work/<stem>.assignment-plan.md` + `_work/class/` 3종).

규칙: 코치는 과제 설명에 없는 요구를 만들지 않고 제출물을 통째로 써 주지 않는다. 검사관은 원문을 먼저 읽고 자기 요구사항 목록을 만든 뒤 깎는다. 과제 설명의 AI·협업 규정은 req·draft·plan 맨 앞에 그대로 옮기고 넘지 않는다. 수업팀은 `approved` 를 쓰지 않는다. 같은 과제의 루프백은 최대 2회(grade `round` 로 추적). 3회째는 사람에게.
