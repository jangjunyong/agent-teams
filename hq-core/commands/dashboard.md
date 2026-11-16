---
description: 실시간 관제 대시보드(팀 조직도·노선도·이벤트·산출물·게이트)를 띄운다
argument-hint: [port]
---

대시보드 서버를 백그라운드로 띄워라: `py "%AI_HQ_ROOT%\teams\hq-core\scripts\dashboard.py" --project <현재 프로젝트 루트> --port ${1:-8765}` (Bash 의 run_in_background, 또는 PowerShell Start-Process). 이미 같은 포트가 열려 있으면 재사용한다.
그다음 사용자에게 `http://127.0.0.1:8765/` 를 열라고 안내하고, 브라우저 도구가 있으면 직접 열어 보여준다. 페이지는 2초마다 자동 갱신되므로 이후 `/hq:run` 이나 팀 커맨드를 실행하면 노선도에 불이 켜진다.
