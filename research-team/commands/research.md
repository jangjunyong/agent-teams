---
description: 질문 하나를 조사 파이프라인(3렌즈 병렬 웹조사 → 종합 → 사실확인 → 브리프)에 태운다. hq-core 그래프 규약으로 실행되어 runs/ 에 기록되고, 근거가 붙은 브리프가 _work/ 에 남는다
argument-hint: '"<질문>"   예: "2026년 기준 국내 증권사 OpenAPI 중 자동매매에 쓸 만한 것은?"'
---

hq-core 의 **graph 스킬 규약**대로 `research-team/research` 그래프를 `question=$ARGUMENTS` 로 실행하라.
HQ=`%AI_HQ_ROOT%\teams\hq-core\scripts\hq.py` (환경변수 AI_HQ_ROOT 가 있으면 그 아래).

0. **slug 를 만든다.** 질문에서 핵심어 2~4개를 뽑아 파일명으로 쓸 짧은 슬러그를 만든다.
   - 영문 소문자·숫자·하이픈(예: `kr-broker-openapi-2026`) 또는 한글(예: `증권사-openapi-비교`). 공백·특수문자·따옴표 금지, 40자 이내
   - 같은 slug 의 산출물이 `_work/research/` 에 이미 있으면 **재작성 회차**로 본다(아래 4번). 다른 질문인데 slug 가 겹치면 끝에 `-2` 를 붙인다
   - 질문이 비어 있거나 한 단어뿐이면 실행하지 말고 사용자에게 질문을 문장으로 다시 달라고 한다
1. `py HQ run start research-team/research slug=<slug> "question=<질문 원문>" round=<회차>` → run_id 와 실행 계획을 받는다. (question 은 공백이 있으니 `key=value` 전체를 따옴표로 감싼다. `$ARGUMENTS` 양끝에 사용자가 붙인 따옴표는 벗기고 원문만 넣는다. 첫 실행은 round=1)
2. 노드를 규약대로 처리한다: **sweep_docs · sweep_academic · sweep_community 는 서로 독립이므로 한 메시지에서 Agent 세 개를 병렬 호출**한다 → synthesize → factcheck → brief.
   - 서브에이전트에게는 계획에 찍힌 prompt 를 **그대로** 준다. 질문의 배경·의도·원하는 답 방향을 덧붙이지 않는다.
   - 각 노드 `node start` → 호출 → `node done`. `node done` 이 frontmatter 누락으로 exit 2 면 보완 지시 1회, 그래도 실패면 `node fail`.
   - 기존 산출물이 있고 최신이면 `node skip --note "기존 산출물 사용"` (재작성 회차의 sweep 세 노드가 이 경우다).
   - brief 노드는 오케스트레이터가 **brief-format 스킬 4절** 규격대로 직접 쓴다. synthesis·factcheck 두 파일에 적힌 것만 근거로 삼고, 두 파일에 없는 주장을 보태지 않는다. `run` 에 run_id, `round` 에 회차, `factcheck` 에 factcheck_verdict 를 적는다.
3. factcheck 결과 처리:
   - **PASS** → brief `status: in-review` 로 쓰고 `run end --status done`. 브리프는 verify-team 검증 대기 상태다(deliverables/ 로 옮기지 않는다, G3).
   - **REVISE / FAIL** (round < 2) → synthesis frontmatter `status: in-review`, `verify_round: <round>` 로 갱신하고 `run end --status failed`. 이어서 **round+1 로 새 run 을 시작**해 sweep 세 노드는 skip(기존 산출물), synthesize 를 factcheck 의 수정 요구를 반영해 재작성 → factcheck 재실행 → brief.
   - **REVISE / FAIL** 인데 round ≥ 2 → brief 는 쓰되 `status: draft`, `factcheck: FAIL|REVISE` 로 남기고 `run end --status escalated`. 사람에게 에스컬레이션(사실확인 판정문 + 두 회차의 수정 요구 요약). 브리프의 "모르는 것" 에 미해결 주장을 전부 옮긴다.
4. 사용자 보고: 핵심 답 3줄(신뢰도 태그 포함) · factcheck 판정 · 충돌·모르는 것 요약 · 다음 질문 · run_id · 산출물 경로(브리프 + `_work/research/` 5종).

규칙: 조사원은 링크 없는 주장을 쓰지 않고, 종합자는 충돌을 편들지 않으며, 사실확인관은 칭찬하지 않는다. 같은 질문 재작성은 최대 2회(synthesis 의 verify_round 로 추적). 3회째는 사람에게. 브리프에 두 입력 파일에 없는 말을 지어내지 않는다.
