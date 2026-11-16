# -*- coding: utf-8 -*-
"""PreToolUse 가드 (Write|Edit|MultiEdit).

규칙
- G3 보호: `deliverables/` 아래 파일은 서브에이전트가 직접 쓰지 못한다 (agent_id 가 있으면 차단).
  승인본 이동은 오케스트레이터(메인 세션)가 verdict PASS 후에만 한다.
- 오케스트레이터가 deliverables/ 에 쓸 때도 frontmatter status: approved 가 아니면 경고 컨텍스트를 붙인다 (차단은 Stop 훅 G3 가 한다).
- runs/ 레저는 사람·에이전트가 손으로 고치지 않는다 → 차단.
차단은 JSON permissionDecision=deny 로, 이유를 남긴다. 오류 시에는 절대 막지 않는다(exit 0).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hqlib  # noqa: E402


def deny(reason: str) -> int:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}, ensure_ascii=False))
    return 0


def main() -> int:
    hqlib.utf8_stdio()
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    try:
        ti = data.get("tool_input") or {}
        path = ti.get("file_path") or ti.get("path") or ""
        if not path:
            return 0
        cwd = data.get("cwd") or os.getcwd()
        project = hqlib.find_project(cwd)
        pr = os.path.normpath(os.path.join(hqlib.HQ_ROOT, "projects")).lower()
        if pr not in os.path.normpath(project).lower():
            return 0
        rel = os.path.relpath(os.path.abspath(path), project).replace("\\", "/")
        agent = data.get("agent_id")
        rid = hqlib.current_run(project)

        if rel.startswith("runs/"):
            hqlib.append_event(project, rid, {"event": "guard.deny", "agent_id": agent, "agent_type": data.get("agent_type"), "detail": {"file": rel, "rule": "runs-ledger-readonly"}})
            return deny("runs/ 레저는 하네스만 쓴다. 직접 수정 금지.")

        if rel.startswith("deliverables/") and agent:
            hqlib.append_event(project, rid, {"event": "guard.deny", "agent_id": agent, "agent_type": data.get("agent_type"), "detail": {"file": rel, "rule": "G3-subagent-no-deliverables"}})
            return deny("G3: 서브에이전트는 deliverables/ 에 쓸 수 없다. _work/ 에 쓰고 오케스트레이터가 verdict PASS 후 옮긴다.")

        if rel.startswith("deliverables/") and not agent:
            # 오케스트레이터: 경고만
            content = ti.get("content") or ti.get("new_string") or ""
            if "status: approved" not in content:
                print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "G3 주의: deliverables/ 에는 status: approved 파일만 둘 수 있다. verdict PASS 전이면 _work/ 에 써라."}}, ensure_ascii=False))
            return 0
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
