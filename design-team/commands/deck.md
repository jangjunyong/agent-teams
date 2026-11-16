---
description: 내용 md(기획서·브리프·보고서) 하나를 발표 덱 파이프라인(스토리라인 → 슬라이드 본문 → 적대적 검토 → pptx 1:1 구조의 덱 md)에 태운다. hq-core 그래프 규약으로 실행되어 runs/ 에 기록된다. 덱은 verify-team 검증 전까지 확정이 아니다
argument-hint: '<내용 md 경로>  예) _work/idea.plan.md'
---

hq-core 의 **graph 스킬 규약**대로 `design-team/deck` 그래프를 `target=$ARGUMENTS` 로 실행하라.
HQ=`%AI_HQ_ROOT%\teams\hq-core\scripts\hq.py`.

1. 회차를 정한다. `_work/deck/<stem>.review.md` 가 있고 그 frontmatter 의 `review_verdict` 가 REVISE 또는 FAIL 이면 round = 그 파일의 `round` + 1 이고 그 `revise_target` 을 적어 둔다. 아니면 round = 1.
   round ≥ 2 면 이전 검토표를 `_work/deck/<stem>.review.r<이전 round>.md` 로 보존하고, 재작성 대상만 보존한다 — revise_target 이 storyline 이면 `.storyline.r<이전 round>.md` 와 `.slides.r<이전 round>.md` 둘 다, slides 면 `.slides.r<이전 round>.md` 만 (덮어쓰지 않는다).
2. `py HQ run start design-team/deck target=$ARGUMENTS round=<round>` → 실행 계획을 받는다. 이 출력만 보고 진행한다.
3. 노드를 규약대로 처리한다. storyline → slides → deck_review 는 직렬이다 (앞 노드의 출력이 뒤 노드의 입력이다).
   - **storyline**: round ≥ 2 이고 revise_target 이 slides 면 기존 파일을 그대로 쓴다 — `node skip storyline --note "기존 산출물 사용 (revise_target: slides)"`. 그 외에는 Agent 호출. 서브에이전트에게는 계획의 prompt 를 **그대로** 준다 (모드 줄 포함). round ≥ 2 이고 revise_target 이 storyline 이면 prompt 끝에 "추가 입력: `_work/deck/<stem>.review.r<이전 round>.md` 의 #5 수정 요구(storyline 대상 항목만)" 한 줄만 덧붙인다.
   - **slides**: storyline 이 done(또는 skip) 인 뒤에. round ≥ 2 면 prompt 끝에 "추가 입력: `_work/deck/<stem>.review.r<이전 round>.md` 의 #5 수정 요구(slides 대상 항목만)" 한 줄만 덧붙인다.
   - **deck_review**: slides 가 done 인 뒤에. prompt 의 `<오케스트레이터가 알려준 회차>` 자리에 현재 round 를 넣어 준다. 결과 파일의 `review_verdict` 와 `revise_target` 을 읽는다.
   - **deck**: `review_verdict` 가 PASS 면 오케스트레이터가 **deck-format 스킬 4절** 규격대로 `_work/<stem>.deck.md` 를 직접 쓴다 (`status: in-review`). 스토리라인·슬라이드·검토표에 적힌 것만 근거로 삼고 요약·윤색하지 않는다. REVISE/FAIL 이고 round < 2 면 `node skip deck --note "review <판정>, loopback"` 후 4번으로. REVISE/FAIL 이고 round ≥ 2 면 덱을 `status: draft` 로 쓰되 미반영 수정 요구를 해당 장 노트 끝에 `[미반영: review#5-<번호>]` 로 남기고 `node done` 후 에스컬레이션한다.
4. 종료 처리.
   - PASS 이고 deck 까지 done → `run end --status done`.
   - REVISE/FAIL 이고 round < 2 → `run end --status failed --note "review <판정>, loopback"` 후 사용자에게 수정 요구(검토표 #5)와 revise_target 을 보고하고 같은 커맨드 재실행을 안내한다 (재실행이 round 2 다).
   - REVISE/FAIL 이고 round ≥ 2 → `run end --status escalated` 후 사람에게 에스컬레이션: 두 검토표 경로, 미반영 수정 요구 목록, 덱 경로(`status: draft`). 더 돌리지 않는다.
5. 사용자 보고: 판정(PASS|REVISE|FAIL) · 장수 · 숫자 검증 결과(일치/불일치/없음 건수) · 수정 요구 개수 · 다음 액션(PASS 면 `/verify-team:verify _work/<stem>.deck.md`, 아니면 재실행 또는 에스컬레이션) · run_id · 산출물 경로 전부.

규칙: 슬라이드 작성자는 스토리라인의 장수·순서·헤드라인을 바꾸지 않는다 (변경은 '## 변경 제안' 에만). 검토자는 슬라이드의 숫자·고유명사를 원문에서 직접 찾아 대조한다 — 슬라이드가 단 근거 경로를 믿지 않는다. 디자인팀은 `approved` 를 쓰지 않는다 — 승인은 verify-team 판정 뒤 오케스트레이터의 일이다(G3). 같은 대상의 REVISE/FAIL 루프백은 최대 2회(review `round` 로 추적). 3회째는 사람에게 (덱은 draft 로 남긴다).
