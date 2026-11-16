---
description: 그래프 하나를 하네스 규약대로 실행한다 (run 레저 기록 + 노드 순차/병렬 실행 + 판정 처리)
argument-hint: "<team/graph> <key=value ...>  예) verify-team/verify target=_work/idea.md"
---

hq-core 의 **graph 스킬 규약**대로 `$ARGUMENTS` 를 실행하라.

HQ=`%AI_HQ_ROOT%\teams\hq-core\scripts\hq.py` (환경변수 AI_HQ_ROOT 가 있으면 그 아래).

1. `py HQ run start $ARGUMENTS` 를 실행해 run_id 와 실행 계획을 받는다. 입력 누락 에러가 나면 사용자에게 필요한 입력을 묻는다.
2. 계획의 노드를 순서대로 `node start` → (Agent 호출 또는 orchestrator 작업) → `node done` 으로 처리한다. 독립 노드는 병렬 호출한다. 건너뛰면 `node skip --note`.
3. 마지막에 `run end --status ...` 로 닫고, 사용자에게 **run_id · 노드별 결과 · 산출물 경로 · 다음 액션**을 보고한다. 대시보드가 떠 있으면 거기서도 보인다고 알려준다.

규칙: 서브에이전트에게는 계획에 찍힌 prompt 를 그대로 준다(배경 설명 금지). 레저(runs/)·deliverables/ 를 직접 쓰지 않는다. 판정 파일에 없는 말을 지어내지 않는다.
