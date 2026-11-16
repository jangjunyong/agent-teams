---
description: 공모전 미션 — 아이디어 하나를 4팀 릴레이(조사→기획→검증→발표 덱)에 태운다. 각 팀은 자식 run 으로 돌고 대시보드에 체인으로 보인다
argument-hint: '<아이디어 md 경로> [question="사전 조사 질문"]'
---

hq-core 의 **graph 스킬 §5 미션 규약**대로 `hq-core/contest` 그래프를 실행하라.
HQ=`%AI_HQ_ROOT%\teams\hq-core\scripts\hq.py`.

1. `py HQ run start hq-core/contest idea=$1 [question=...]` → 부모 run_id 확보.
2. 각 서브그래프 노드: 부모 `node start` → `py HQ run start <subgraph> <child inputs> --parent <부모 run_id>` → 자식 그래프를 그 팀 커맨드 규약대로 끝까지(자식 run end 까지) → 부모 `node done`. question 이 없으면 research 는 `node skip`.
3. verify 자식이 FAIL 이면: 부모 `node fail verify` → 반려 사유를 기획에 반영해 plan 부터 루프백(최대 2회) 또는 escalated.
4. 보고: 미션 run_id · 팀별 자식 run 결과 · 최종 산출물(기획·판정·덱 경로) · 다음 액션.
