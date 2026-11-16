# -*- coding: utf-8 -*-
"""훅 → 런 레저 추적기. 모든 훅 이벤트(SessionStart/SubagentStart/SubagentStop/PostToolUse/Stop)에서 호출된다.

- 현재 run 이 있으면 runs/<run_id>/events.jsonl, 없으면 runs/_unassigned/events.jsonl 에 기록
- SessionStart 에서는 현재 HQ 상태를 additionalContext 로 주입한다 (오케스트레이터가 이어서 일할 수 있게)
- 절대 세션을 막지 않는다: 어떤 오류가 나도 exit 0
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hqlib  # noqa: E402


def main() -> int:
    hqlib.utf8_stdio()
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    ev = data.get("hook_event_name", "")
    cwd = data.get("cwd") or os.getcwd()
    project = hqlib.find_project(cwd)
    # ai-hq/projects/ 밖 세션(볼트·일반 폴더)에서는 레저를 쓰지 않는다 — 외부 폴더 오염 금지
    pr = os.path.normpath(os.path.join(hqlib.HQ_ROOT, "projects")).lower()
    if pr not in os.path.normpath(project).lower():
        return 0
    rid = hqlib.current_run(project)
    base = {
        "event": None,
        "session_id": data.get("session_id"),
        "agent_id": data.get("agent_id"),
        "agent_type": data.get("agent_type"),
    }
    try:
        if ev == "SessionStart":
            base["event"] = "session.start"
            base["detail"] = {"source": data.get("source"), "cwd": cwd}
            hqlib.append_event(project, rid, base)
            _ensure_dashboard(project)
            ctx = _session_context(project, rid)
            if ctx:
                print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}}, ensure_ascii=False))
            return 0
        if ev == "SubagentStart":
            base["event"] = "agent.start"
            hqlib.append_event(project, rid, base)
            return 0
        if ev == "SubagentStop":
            base["event"] = "agent.stop"
            msg = data.get("last_assistant_message") or ""
            base["detail"] = {"last_message": msg[:400]}
            hqlib.append_event(project, rid, base)
            return 0
        if ev == "PostToolUse":
            ti = data.get("tool_input") or {}
            path = ti.get("file_path") or ti.get("path") or ""
            if not path:
                return 0
            base["event"] = "artifact.write"
            rel = _rel(path, project)
            d = {"file": rel, "tool": data.get("tool_name")}
            if path.lower().endswith(".md"):
                fm = hqlib.read_frontmatter(path) or {}
                for k in ("type", "status", "owner", "verdict", "verify_round"):
                    if k in fm:
                        d[k] = fm[k]
            base["detail"] = d
            hqlib.append_event(project, rid, base)
            return 0
        if ev == "Stop":
            base["event"] = "turn.stop"
            hqlib.append_event(project, rid, base)
            return 0
        base["event"] = ev.lower() if ev else "unknown"
        hqlib.append_event(project, rid, base)
    except Exception as e:  # 추적기는 절대 막지 않는다
        try:
            sys.stderr.write(f"[hq-core trace] {e}\n")
        except Exception:
            pass
    return 0


def _ensure_dashboard(project: str) -> None:
    """ai-hq 프로젝트에서 세션이 시작되면 관제 대시보드를 자동으로 띄우고 브라우저를 연다.
    이미 8765 포트가 살아 있으면 아무것도 안 한다. 끄고 싶으면 HQ_NO_DASHBOARD=1."""
    import os as _os
    import socket
    import subprocess
    if _os.environ.get("HQ_NO_DASHBOARD"):
        return
    # ai-hq/projects/ 아래에서만 발동
    norm = _os.path.normpath(project).lower()
    if _os.path.normpath(_os.path.join(hqlib.HQ_ROOT, "projects")).lower() not in norm:
        return
    try:
        s = socket.create_connection(("127.0.0.1", 8765), timeout=0.3)
        s.close()
        return  # 이미 떠 있음
    except OSError:
        pass
    here = _os.path.dirname(_os.path.abspath(__file__))
    try:
        flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | NEW_PROCESS_GROUP
        subprocess.Popen(["py", "-3", _os.path.join(here, "dashboard.py"), "--project", project, "--port", "8765"],
                         creationflags=flags, close_fds=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.Popen(["cmd", "/c", "start", "", "http://127.0.0.1:8765/?project=" + project],
                         creationflags=flags, close_fds=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def _rel(path: str, project: str) -> str:
    try:
        r = os.path.relpath(path, project)
        return path if r.startswith("..") else r
    except Exception:
        return path


def _session_context(project: str, rid) -> str:
    lines = ["[AI-HQ] 하네스 활성. 파이프라인은 hq-core 의 graph 스킬 규약으로만 실행한다 (/hq-core:run, /hq-core:status, /hq-core:dashboard)."]
    if rid:
        m = hqlib.load_manifest(project, rid) or {}
        st = m.get("status", "?")
        lines.append(f"[AI-HQ] 진행 중 run: {rid} ({m.get('graph','?')}, 상태 {st}). `py hq.py status` 로 확인 후 이어서 진행할 것.")
    try:
        gs = hqlib.list_graphs()
        if gs:
            lines.append("[AI-HQ] 사용 가능 그래프: " + ", ".join(f"{g['team']}/{g['name']}" for g in gs))
    except Exception:
        pass
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
