---
description: 산출물 하나를 검증 파이프라인(선행조사 → 레드팀 → 판정)에 태운다. hq-core 그래프 규약으로 실행되어 runs/ 에 기록된다
argument-hint: "<검증할 파일 경로>  예) _work/idea.md"
---

hq-core 의 **graph 스킬 규약**대로 `verify-team/verify` 그래프를 `target=$ARGUMENTS` 로 실행하라.
HQ=`%AI_HQ_ROOT%\teams\hq-core\scripts\hq.py`.

1. 대상 파일의 frontmatter 를 읽어 `verify_round`(없으면 0)를 확인한다. round = verify_round + 1.
2. `py HQ run start verify-team/verify target=$ARGUMENTS round=<round>` → 실행 계획을 받는다.
3. 노드를 규약대로 처리한다: originality(아이디어·기획일 때만; 코드·기술문서면 skip) → redteam → verdict.
   - 서브에이전트에게는 계획의 prompt 를 **그대로** 준다. 작성 맥락·옹호성 설명을 덧붙이지 않는다.
   - verdict 노드는 오케스트레이터가 **verdict 스킬** 규격대로 직접 쓴다. 두 결과 파일에 적힌 것만 근거로 삼는다.
4. 판정 후: PASS → 대상 `status: approved`, `verified_by` 에 verify-team 추가 → `run end --status done`.
   FAIL/CONDITIONAL → 대상 status 갱신 + `verify_round: <round>` 기록 → `run end --status failed`.
   round ≥ 2 인데 또 FAIL → `run end --status escalated` 후 사람에게 에스컬레이션(판정문 + 지금까지의 반려 사유 요약).
5. 사용자 보고: 판정 · 핵심 근거 3줄 · 반려 사유(있다면) · 다음 액션 · run_id · 산출물 경로.

규칙: 검증자는 파일만 보고 판단한다. 같은 파일 반려는 최대 2회(verify_round 로 추적). 3회째는 사람에게.
