# -*- coding: utf-8 -*-
"""AI-HQ 하네스 CLI — 그래프 러너 + 런 레저.

사용법 (프로젝트 폴더에서, 또는 --project 로 지정)
  py hq.py graphs                                  사용 가능한 그래프 목록
  py hq.py plan  <team/graph> key=value ...        실행 계획만 출력 (run 생성 안 함)
  py hq.py run start <team/graph> key=value ...    run 생성 + current 설정 + 실행 계획 출력
  py hq.py node start|done|fail|skip <node_id> [--note "..."]
  py hq.py check <node_id>                         노드 출력 파일 존재·frontmatter 검사 (exit 0/2)
  py hq.py run end --status done|failed|escalated [--note "..."]
  py hq.py run resume [--run <run_id>]                끊긴 run 을 실패 노드부터 재개 (체크포인트=manifest)
  py hq.py status [--json] [--run <run_id>]
  py hq.py context                                 세션 주입용 한 줄 요약
  py hq.py dashboard [--port 8765]                 실시간 대시보드 서버

오케스트레이터(메인 세션)가 이 CLI 로 레저를 남기고, 훅(trace.py)이 서브에이전트·산출물 이벤트를 자동으로 덧붙인다.
"""
import argparse
import datetime as dt
import io
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hqlib  # noqa: E402


def _kv(items):
    out = {}
    for it in items or []:
        if "=" in it:
            k, v = it.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def _print_plan(g: dict, run_id: str | None, project: str) -> None:
    head = f"RUN {run_id}" if run_id else "PLAN (run 미생성)"
    print(f"{head}  graph={g.get('team','?')}/{g.get('name')}  project={project}")
    print(f"inputs: " + ", ".join(f"{k}={v}" for k, v in g.get("resolved_inputs", {}).items()))
    pol = g.get("policy", {})
    if pol:
        print("policy: " + ", ".join(f"{k}={v}" for k, v in pol.items()))
    print("nodes (실행 순서):")
    for i, n in enumerate(hqlib.topo(g["nodes"]), 1):
        who = n.get('agent','orchestrator') if not n.get('subgraph') else '서브그래프 ▶ ' + n['subgraph']
        print(f" {i}. {n['id']}  [{who}]" + (f"  gate={n['gate']}" if n.get("gate") else "") + (f"  when: {n['when']}" if n.get("when") else ""))
        if n.get("title"):
            print(f"    제목: {n['title']}")
        for x in n.get("inputs", []):
            print(f"    in : {x}")
        for x in n.get("outputs", []):
            print(f"    out: {x}")
        if n.get("subgraph_inputs"):
            print("    child inputs: " + ", ".join(f"{k}={v}" for k, v in n["subgraph_inputs"].items()))
        if n.get("prompt"):
            print("    prompt:")
            for ln in n["prompt"].rstrip().split("\n"):
                print("      " + ln)
    print("\n실행 규약: 각 노드마다 `py hq.py node start <id>` → (에이전트 노드면 Agent 호출, orchestrator 노드면 스킬대로 직접 작성) → `py hq.py node done <id>` (출력 검사 자동). 실패 시 `node fail`, 조건 불충족 시 `node skip`. 끝나면 `py hq.py run end --status done|failed|escalated`.")


def cmd_graphs(a):
    gs = hqlib.list_graphs()
    if not gs:
        print("(그래프 없음) teams/<team>/graphs/*.json 을 확인하라")
        return 0
    for g in gs:
        print(f"{g['team']}/{g['name']:<14} 노드 {g['nodes']:2d}  {g['title']}")
    return 0


def cmd_plan(a):
    project = os.path.abspath(a.project or hqlib.find_project())
    g = hqlib.resolve_graph(hqlib.load_graph(a.graph), _kv(a.inputs))
    if a.json:
        print(json.dumps(g, ensure_ascii=False, indent=2))
    else:
        _print_plan(g, None, project)
    return 0


def cmd_run_start(a):
    project = os.path.abspath(a.project or hqlib.find_project())
    graph = hqlib.load_graph(a.graph)
    inputs = _kv(a.inputs)
    missing = [k for k in graph.get("inputs", {}) if k not in inputs]
    if missing:
        print(f"입력 누락: {missing}. 예: {' '.join(k+'=<값>' for k in missing)}", file=sys.stderr)
        return 2
    g = hqlib.resolve_graph(graph, inputs)
    rid = hqlib.new_run_id(g.get("name", "graph"))
    manifest = {
        "run_id": rid,
        "graph": f"{g.get('team','?')}/{g.get('name')}",
        "graph_file": g.get("_file"),
        "title": g.get("title", ""),
        "project": project,
        "inputs": inputs,
        "ctx": g.get("ctx", {}),
        "policy": g.get("policy", {}),
        "nodes": [{k: v for k, v in n.items() if k != "prompt"} | {"prompt": n.get("prompt", "")} for n in hqlib.topo(g["nodes"])],
        "node_state": {n["id"]: "pending" for n in g["nodes"]},
        "round": int(inputs.get("round", "1")),
        "parent_run": a.parent or None,
        "started": hqlib.now_iso(),
        "ended": None,
        "status": "running",
    }
    hqlib.save_manifest(project, rid, manifest)
    hqlib.set_current_run(project, rid)
    hqlib.append_event(project, rid, {"event": "run.start", "detail": {"graph": manifest["graph"], "inputs": inputs, "round": manifest["round"], "parent_run": manifest["parent_run"]}})
    if a.parent:
        hqlib.append_event(project, a.parent, {"event": "child.start", "detail": {"child_run": rid, "graph": manifest["graph"]}})
    _print_plan(g, rid, project)
    return 0


def cmd_run_resume(a):
    project = os.path.abspath(a.project or hqlib.find_project())
    rid = a.run
    if not rid:  # 최근 미완료 run 자동 선택
        for r in hqlib.list_runs(project):
            m = hqlib.load_manifest(project, r) or {}
            if m.get("status") in ("running", "failed", "aborted"):
                rid = r
                break
    if not rid:
        print("재개할 run 이 없다 (running/failed/aborted 상태 없음).", file=sys.stderr)
        return 2
    m = hqlib.load_manifest(project, rid)
    if not m:
        print(f"manifest 없음: {rid}", file=sys.stderr)
        return 2
    # running 이던 노드는 pending 으로 되돌린다 (끊긴 작업)
    reset = [k for k, v in m["node_state"].items() if v == "running"]
    for k in reset:
        m["node_state"][k] = "pending"
    m["status"] = "running"
    m["ended"] = None
    hqlib.save_manifest(project, rid, m)
    hqlib.set_current_run(project, rid)
    hqlib.append_event(project, rid, {"event": "run.resume", "detail": {"reset_nodes": reset}})
    print(f"RUN {rid} 재개  graph={m.get('graph')}  (running→pending 리셋: {reset or '없음'})")
    print("남은 노드:")
    order = {"pending": 0, "failed": 1}
    todo = [n for n in m["nodes"] if m["node_state"].get(n["id"]) in ("pending", "failed")]
    for n in todo:
        print(f"  - {n['id']} [{n.get('agent','orchestrator')}] 상태={m['node_state'].get(n['id'])}")
        for o in n.get("outputs", []):
            print(f"      out: {o}")
    if not todo:
        print("  (없음 — 판정/마감만 남음. node/run end 를 이어서)")
    return 0


def _load_current(a):
    project = os.path.abspath(a.project or hqlib.find_project())
    rid = getattr(a, "run", None) or hqlib.current_run(project)
    if not rid:
        print("진행 중 run 이 없다. `py hq.py run start ...` 먼저.", file=sys.stderr)
        return project, None, None
    m = hqlib.load_manifest(project, rid)
    if not m:
        print(f"manifest 없음: {rid}", file=sys.stderr)
        return project, rid, None
    return project, rid, m


def cmd_node(a):
    project, rid, m = _load_current(a)
    if not m:
        return 2
    node = next((n for n in m["nodes"] if n["id"] == a.node_id), None)
    if not node:
        print(f"노드 없음: {a.node_id}. 있는 노드: {[n['id'] for n in m['nodes']]}", file=sys.stderr)
        return 2
    action = a.action
    status_map = {"start": "running", "done": "done", "fail": "failed", "skip": "skipped"}
    if action == "done":
        ok, problems = _check_node(project, node)
        if not ok:
            m["node_state"][a.node_id] = "failed"
            hqlib.save_manifest(project, rid, m)
            hqlib.append_event(project, rid, {"event": "node.fail", "node": a.node_id, "detail": {"reason": "output-check", "problems": problems, "note": a.note}})
            print("출력 검사 실패:\n  " + "\n  ".join(problems), file=sys.stderr)
            return 2
    m["node_state"][a.node_id] = status_map[action]
    if action == "start":
        node_started = hqlib.now_iso()
        m.setdefault("node_times", {}).setdefault(a.node_id, {})["start"] = node_started
    if action in ("done", "fail", "skip"):
        m.setdefault("node_times", {}).setdefault(a.node_id, {})["end"] = hqlib.now_iso()
    hqlib.save_manifest(project, rid, m)
    hqlib.append_event(project, rid, {"event": f"node.{action}", "node": a.node_id, "detail": {"agent": node.get("agent"), "outputs": node.get("outputs"), "note": a.note}})
    print(f"{a.node_id}: {status_map[action]}")
    return 0


def _check_node(project: str, node: dict):
    problems = []
    for o in node.get("outputs", []):
        p = o if os.path.isabs(o) else os.path.join(project, o)
        if not os.path.isfile(p):
            problems.append(f"출력 파일 없음: {o}")
            continue
        if os.path.getsize(p) == 0:
            problems.append(f"빈 파일: {o}")
        if p.lower().endswith(".md"):
            fm = hqlib.read_frontmatter(p)
            if fm is None:
                problems.append(f"frontmatter 없음: {o}")
            else:
                for k in ("type", "status", "owner"):
                    if k not in fm:
                        problems.append(f"frontmatter {k} 누락: {o}")
    return (not problems), problems


def cmd_check(a):
    project, rid, m = _load_current(a)
    if not m:
        return 2
    node = next((n for n in m["nodes"] if n["id"] == a.node_id), None)
    if not node:
        print(f"노드 없음: {a.node_id}", file=sys.stderr)
        return 2
    ok, problems = _check_node(project, node)
    print("OK" if ok else "\n".join(problems))
    return 0 if ok else 2


def cmd_run_end(a):
    project, rid, m = _load_current(a)
    if not m:
        return 2
    m["status"] = a.status
    m["ended"] = hqlib.now_iso()
    if a.note:
        m["note"] = a.note
    hqlib.save_manifest(project, rid, m)
    hqlib.append_event(project, rid, {"event": "run.end", "detail": {"status": a.status, "note": a.note}})
    parent = m.get("parent_run")
    if parent:
        hqlib.append_event(project, parent, {"event": "child.end", "detail": {"child_run": rid, "status": a.status}})
        pm = hqlib.load_manifest(project, parent)
        if pm and pm.get("status") == "running":
            hqlib.set_current_run(project, parent)
            print(f"부모 run 으로 복귀: {parent}")
            return 0
    hqlib.set_current_run(project, None)
    print(f"run {rid} → {a.status}")
    return 0


def _summarize(project: str, rid: str) -> dict:
    m = hqlib.load_manifest(project, rid) or {}
    evs = hqlib.read_events(project, rid)
    agents = [e for e in evs if e.get("event") in ("agent.start", "agent.stop")]
    arts = [e for e in evs if e.get("event") == "artifact.write"]
    return {
        "run_id": rid,
        "graph": m.get("graph"),
        "status": m.get("status"),
        "round": m.get("round"),
        "started": m.get("started"),
        "ended": m.get("ended"),
        "node_state": m.get("node_state", {}),
        "agents_spawned": len([e for e in agents if e["event"] == "agent.start"]),
        "artifacts": sorted({e["detail"]["file"] for e in arts if e.get("detail", {}).get("file")}),
        "events": len(evs),
    }


def cmd_status(a):
    project = os.path.abspath(a.project or hqlib.find_project())
    rid = a.run or hqlib.current_run(project)
    runs = hqlib.list_runs(project)
    if a.json:
        print(json.dumps({"project": project, "current": rid, "runs": [_summarize(project, r) for r in runs[:10]]}, ensure_ascii=False, indent=2))
        return 0
    print(f"project: {project}")
    print(f"current run: {rid or '(없음)'}")
    if not runs:
        print("runs: (없음)")
        return 0
    for r in runs[:8]:
        s = _summarize(project, r)
        ns = s["node_state"]
        bar = " ".join(f"{k}:{v[:4]}" for k, v in ns.items())
        print(f"- {r}  {s['graph']}  [{s['status']}] round={s['round']} agents={s['agents_spawned']} events={s['events']}")
        print(f"    {bar}")
    return 0


def cmd_context(a):
    project = os.path.abspath(a.project or hqlib.find_project())
    rid = hqlib.current_run(project)
    if rid:
        s = _summarize(project, rid)
        print(f"진행 중 run {rid} ({s['graph']}, {s['status']}): " + ", ".join(f"{k}={v}" for k, v in s["node_state"].items()))
    else:
        print("진행 중 run 없음")
    return 0


def cmd_dashboard(a):
    here = os.path.dirname(os.path.abspath(__file__))
    project = os.path.abspath(a.project or hqlib.find_project())
    cmd = [sys.executable, os.path.join(here, "dashboard.py"), "--project", project, "--port", str(a.port)]
    print("대시보드: http://127.0.0.1:%d/  (Ctrl+C 로 종료)" % a.port)
    return subprocess.call(cmd)


def main(argv=None) -> int:
    hqlib.utf8_stdio()
    p = argparse.ArgumentParser(prog="hq", description="AI-HQ 하네스 CLI")
    p.add_argument("--project", help="프로젝트 루트 (기본: cwd 에서 탐색)")
    sp = p.add_subparsers(dest="cmd", required=True)

    sp.add_parser("graphs").set_defaults(fn=cmd_graphs)

    q = sp.add_parser("plan"); q.add_argument("graph"); q.add_argument("inputs", nargs="*"); q.add_argument("--json", action="store_true"); q.set_defaults(fn=cmd_plan)

    r = sp.add_parser("run"); rs = r.add_subparsers(dest="sub", required=True)
    r1 = rs.add_parser("start"); r1.add_argument("graph"); r1.add_argument("inputs", nargs="*"); r1.add_argument("--parent", help="부모 run_id (미션의 서브그래프로 실행될 때)"); r1.set_defaults(fn=cmd_run_start)
    r2 = rs.add_parser("end"); r2.add_argument("--status", required=True, choices=["done", "failed", "escalated", "aborted"]); r2.add_argument("--note"); r2.add_argument("--run"); r2.set_defaults(fn=cmd_run_end)
    r3 = rs.add_parser("resume"); r3.add_argument("--run", help="run_id (생략 시 최근 미완료 run)"); r3.set_defaults(fn=cmd_run_resume)

    n = sp.add_parser("node"); n.add_argument("action", choices=["start", "done", "fail", "skip"]); n.add_argument("node_id"); n.add_argument("--note"); n.add_argument("--run"); n.set_defaults(fn=cmd_node)

    c = sp.add_parser("check"); c.add_argument("node_id"); c.add_argument("--run"); c.set_defaults(fn=cmd_check)

    s = sp.add_parser("status"); s.add_argument("--json", action="store_true"); s.add_argument("--run"); s.set_defaults(fn=cmd_status)

    sp.add_parser("context").set_defaults(fn=cmd_context)

    d = sp.add_parser("dashboard"); d.add_argument("--port", type=int, default=8765); d.set_defaults(fn=cmd_dashboard)

    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
