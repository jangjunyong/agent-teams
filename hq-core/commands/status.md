---
description: 현재 프로젝트의 run 상태(진행 중 run, 노드별 상태, 최근 run 목록)를 보여준다
---

`py "%AI_HQ_ROOT%\teams\hq-core\scripts\hq.py" status` 를 실행하고 결과를 그대로 보여준 뒤, 진행 중 run 이 있으면 다음에 해야 할 노드를 한 줄로 알려줘라. 진행 중 run 이 끊긴 상태(세션이 바뀐 경우)면 이어서 할지 `run end --status aborted` 로 닫을지 사용자에게 묻는다.
