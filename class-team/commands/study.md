---
description: 강의자료 하나(md/pdf/txt)를 수업 파이프라인(개념 노트 ∥ 문제 10개 → 적대적 검사(원문 대조) → 수업 노트)에 태운다. hq-core 그래프 규약으로 실행되어 runs/ 에 기록되고, vault courses/<과목>/ 규격과 호환되는 수업 노트가 _work/ 에 남는다 (vault 적재는 사람 확인 뒤)
argument-hint: '<강의자료 경로> <과목명>   예: _work/lecture03.pdf 운영체제'
---

hq-core 의 **graph 스킬 규약**대로 `class-team/study` 그래프를 실행하라.
HQ=`%AI_HQ_ROOT%\teams\hq-core\scripts\hq.py` (환경변수 AI_HQ_ROOT 가 있으면 그 아래).

0. **인자를 나눈다.** `$ARGUMENTS` 의 첫 토큰 = `target`(강의자료 경로, md/pdf/txt), 나머지 전부 = `course`(과목명).
   - target 파일이 없으면 실행하지 말고 경로를 다시 달라고 한다. course 가 비어 있으면 과목명을 물어본다(임의로 정하지 않는다)
   - course 에 공백이 있으면 하이픈으로 잇는다(예: `자료구조-및-알고리즘`). vault tags `course/<과목>` 과 `courses/<과목>/` 폴더명에 쓰인다
   - 회차: `_work/class/<stem>.examine.md` 가 있고 frontmatter `examine_verdict` 가 REVISE|FAIL 이면 round = 그 파일의 `round` + 1, 아니면 round = 1.
     round ≥ 2 면 이전 검사표를 `_work/class/<stem>.examine.r<이전 round>.md` 로, 다시 쓸 쪽의 이전 산출물을 `.notes.r<이전 round>.md` / `.quiz.r<이전 round>.md` 로 보존한다(덮어쓰지 않는다)
1. `py HQ run start class-team/study target=<경로> course=<과목> round=<round>` → run_id 와 실행 계획을 받는다. 이 출력만 보고 진행한다.
2. 노드를 규약대로 처리한다.
   - **notes / quiz** 는 서로 독립이다. `node start` 두 번 → Agent 를 **한 메시지에 두 개** 병렬 호출 → 각각 `node done`.
     서브에이전트에게는 계획에 찍힌 prompt 를 **그대로** 준다. 자료의 배경·시험 범위·원하는 방향을 덧붙이지 않는다.
     round ≥ 2 면 이전 검사표의 `notes_verdict` / `quiz_verdict` 가 PASS 인 쪽은 `node skip --note "기존 산출물 사용 (examine PASS)"`, PASS 가 아닌 쪽만 prompt 끝에 "추가 입력: `_work/class/<stem>.examine.r<이전 round>.md` 의 #6 수정 요구(대상이 notes|quiz 인 행만)" 한 줄을 덧붙여 다시 호출한다.
   - **examine** 은 notes·quiz 가 모두 done(또는 skip) 인 뒤에. prompt 의 `round:` 자리에 현재 회차를 넣어 준다. round ≥ 2 면 prompt 끝에 "이전 검사표: `_work/class/<stem>.examine.r<이전 round>.md` (수정 요구 반영 확인용)" 한 줄을 덧붙인다. 결과 파일의 `examine_verdict` 를 읽는다.
   - **note** 는 오케스트레이터가 **course-note 스킬 4절** 규격대로 `_work/<stem>.course-note.md` 를 직접 쓴다. notes·quiz·examine 세 파일에 적힌 것만 근거로 삼고 요약·윤색하지 않는다. examine 에서 걸린 개념·문제는 싣지 않고 #5 로 보낸다. `run` 에 run_id, `round` 에 회차, `examine` 에 examine_verdict, `status` 는 PASS 면 `in-review` 아니면 `draft`. vault 필드(title/created/updated/tags: [course/<과목>]/source/vault_status: seed)를 handoff 3필드와 함께 둔다. **vault 에 직접 쓰지 않는다.**
   - 각 노드 `node start` → 호출 → `node done`. `node done` 이 frontmatter 누락으로 exit 2 면 보완 지시 1회, 그래도 실패면 `node fail`.
3. 종료 처리.
   - **PASS** → note 까지 done → `run end --status done`.
   - **REVISE / FAIL** 이고 round < 2 → note 는 `status: draft` 로 쓰고 `run end --status failed --note "examine <판정>, loopback"` 후 사용자에게 판정 근거(검사표 #5)와 수정 요구 개수를 보고하고 같은 커맨드 재실행을 안내한다(재실행이 round 2 다).
   - **REVISE / FAIL** 이고 round ≥ 2 → note 는 `status: draft`, `examine: <판정>` 으로 쓰고 `run end --status escalated` 후 사람에게 에스컬레이션: 두 검사표 경로, 미해결 지적 목록, 제외된 개념·문제. 더 돌리지 않는다.
4. 사용자 보고: examine 판정(노트 점수·문제지 점수) · 실린 개념 수/제외 개념 수 · 실린 문제 수/제외 문제 수 · 미해결 지적 요약 · 다음 액션(vault 적재 여부 확인 — course-note 스킬 5절 변환 규칙, 필요하면 `/verify-team:verify _work/<stem>.course-note.md`) · run_id · 산출물 경로 전부(`_work/<stem>.course-note.md` + `_work/class/` 3종).

규칙: 노트 작성자와 출제자는 서로의 파일을 보지 않는다. 검사관은 원문을 먼저 읽고 자기 개념 목록을 만든 뒤 대조한다. 수업팀은 `approved` 를 쓰지 않고 vault 에 직접 쓰지 않는다 — 적재는 사람 확인 뒤 오케스트레이터가 course-note 스킬 5절대로 한다. 같은 자료의 루프백은 최대 2회(examine `round` 로 추적). 3회째는 사람에게.
