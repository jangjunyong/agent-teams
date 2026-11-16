# -*- coding: utf-8 -*-
"""AI-HQ 관제 대시보드 v2 — 조직도 중심 (표준 라이브러리만).

  py dashboard.py --project <projects/xxx> [--port 8765]

- 조직도: HQ → 팀(플러그인) → 에이전트. 살아 있는 에이전트는 깜빡인다. 클릭하면 오른쪽 패널에 "지금 뭐 하는지" (현재 노드·최근 이벤트·산출물·역할 정의)
- 편집: 팀 추가 / 에이전트 추가 / 제거(보관으로 이동). 파일과 marketplace.json 에 바로 반영, 다음 세션부터 로드
- 운행: 현재 run 노선도 · 이벤트 스트림 · 산출물 · 게이트
API: GET /api/state?project=<path>  POST /api/team/add  POST /api/agent/add  POST /api/remove  GET /api/projects
"""
import argparse
import datetime as dt
import io
import json
import os
import re
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hqlib  # noqa: E402

PROJECT = os.getcwd()
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{1,40}$")


# ------------------------------------------------------------------ 데이터 읽기

def _read(p):
    try:
        with io.open(p, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _body_after_fm(text: str, n=600) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            text = text[end + 4:]
    return text.strip()[:n]


def _marketplace():
    mp = os.path.join(hqlib.teams_dir(), ".claude-plugin", "marketplace.json")
    try:
        return json.loads(_read(mp)), mp
    except Exception:
        return {"name": "ai-hq", "plugins": []}, mp


def _teams() -> list:
    d, _ = _marketplace()
    out = []
    for p in d.get("plugins", []):
        name = p.get("name")
        root = os.path.join(hqlib.teams_dir(), name)
        agents = []
        ad = os.path.join(root, "agents")
        if os.path.isdir(ad):
            for f in sorted(os.listdir(ad)):
                if f.endswith(".md"):
                    fp = os.path.join(ad, f)
                    fm = hqlib.read_frontmatter(fp) or {}
                    tools = fm.get("tools", "")
                    if isinstance(tools, list):
                        tools = ", ".join(tools)
                    agents.append({"name": fm.get("name", f[:-3]), "file": fp, "model": fm.get("model", ""), "tools": tools,
                                   "desc": fm.get("description", "") or "", "body": _body_after_fm(_read(fp))})
        cmds = []
        cd = os.path.join(root, "commands")
        if os.path.isdir(cd):
            for f in sorted(os.listdir(cd)):
                if f.endswith(".md"):
                    fm = hqlib.read_frontmatter(os.path.join(cd, f)) or {}
                    cmds.append({"name": f[:-3], "desc": fm.get("description", "")})
        graphs = []
        gd = os.path.join(root, "graphs")
        if os.path.isdir(gd):
            for f in sorted(os.listdir(gd)):
                if f.endswith(".json"):
                    try:
                        g = json.loads(_read(os.path.join(gd, f)))
                        graphs.append({"name": g.get("name", f[:-5]), "title": g.get("title", ""), "nodes": [{"id": n["id"], "agent": n.get("agent", "orchestrator"), "title": n.get("title", "")} for n in g.get("nodes", [])]})
                    except Exception:
                        pass
        skills = []
        sd = os.path.join(root, "skills")
        if os.path.isdir(sd):
            skills = [s for s in sorted(os.listdir(sd)) if os.path.isdir(os.path.join(sd, s))]
        ver = ""; disp = ""
        try:
            pj = json.loads(_read(os.path.join(root, ".claude-plugin", "plugin.json")))
            ver = pj.get("version", ""); disp = pj.get("displayName", "")
        except Exception:
            pass
        hooks = []
        hp = os.path.join(root, "hooks", "hooks.json")
        if os.path.isfile(hp):
            try:
                hooks = list(json.loads(_read(hp)).get("hooks", {}).keys())
            except Exception:
                pass
        out.append({"name": name, "version": ver, "displayName": disp, "desc": p.get("description", ""), "category": p.get("category", ""), "agents": agents,
                    "commands": cmds, "graphs": graphs, "skills": skills, "hooks": hooks, "root": root})
    return out


def _artifacts(project: str) -> list:
    out = []
    for sub in ("_work", "deliverables"):
        base = os.path.join(project, sub)
        if not os.path.isdir(base):
            continue
        for dp, dns, fs in os.walk(base):
            dns[:] = [d for d in dns if not d.startswith(".")]
            for f in fs:
                if not f.lower().endswith(".md"):
                    continue
                p = os.path.join(dp, f)
                fm = hqlib.read_frontmatter(p) or {}
                try:
                    mt = os.path.getmtime(p)
                except OSError:
                    mt = 0
                out.append({"file": os.path.relpath(p, project).replace("\\", "/"), "type": fm.get("type", ""), "status": fm.get("status", ""),
                            "owner": fm.get("owner", ""), "verdict": fm.get("verdict", ""), "round": fm.get("verify_round", ""),
                            "mtime": mt, "mtime_h": dt.datetime.fromtimestamp(mt).strftime("%m-%d %H:%M") if mt else "", "in_deliverables": sub == "deliverables"})
    out.sort(key=lambda a: -a["mtime"])
    return out


def _gate(arts):
    bad = [a["file"] for a in arts if a["in_deliverables"] and a["status"] != "approved"]
    return {"ok": not bad, "violations": bad, "deliverables": sum(1 for a in arts if a["in_deliverables"])}


def _run_view(project, rid):
    m = hqlib.load_manifest(project, rid) or {}
    evs = hqlib.read_events(project, rid)
    live = {}
    for e in evs:
        if e.get("event") == "agent.start" and e.get("agent_id"):
            live[e["agent_id"]] = {"agent_type": e.get("agent_type"), "since": e.get("ts"), "node": (e.get("detail") or {}).get("node")}
        if e.get("event") == "agent.stop" and e.get("agent_id") in live:
            live.pop(e["agent_id"], None)
    nodes = []
    running_node = None
    for n in m.get("nodes", []):
        nid = n["id"]
        t = (m.get("node_times") or {}).get(nid, {})
        st = (m.get("node_state") or {}).get(nid, "pending")
        if st == "running":
            running_node = n
        nodes.append({"id": nid, "title": n.get("title", ""), "agent": n.get("agent", "orchestrator"), "gate": n.get("gate"), "state": st,
                      "outputs": n.get("outputs", []), "start": t.get("start"), "end": t.get("end")})
    children = []
    for r in hqlib.list_runs(project):
        cm = hqlib.load_manifest(project, r) or {}
        if cm.get("parent_run") == rid:
            children.append({"run_id": r, "graph": cm.get("graph"), "status": cm.get("status")})
    return {"run_id": rid, "graph": m.get("graph"), "title": m.get("title"), "status": m.get("status"), "round": m.get("round"), "parent_run": m.get("parent_run"), "children": children,
            "started": m.get("started"), "ended": m.get("ended"), "inputs": m.get("inputs", {}), "nodes": nodes,
            "running_node": running_node and {"id": running_node["id"], "agent": running_node.get("agent"), "title": running_node.get("title")},
            "live_agents": list(live.values()), "events": evs[-300:],
            "counts": {"agents": sum(1 for e in evs if e.get("event") == "agent.start"), "artifacts": sum(1 for e in evs if e.get("event") == "artifact.write"),
                       "denied": sum(1 for e in evs if e.get("event") == "guard.deny")}}


def _projects():
    pd = os.path.join(hqlib.HQ_ROOT, "projects")
    out = []
    try:
        for n in sorted(os.listdir(pd)):
            p = os.path.join(pd, n)
            if os.path.isdir(p) and not n.startswith("_"):
                out.append({"name": n, "path": p, "runs": len(hqlib.list_runs(p)), "live": bool(hqlib.current_run(p))})
    except OSError:
        pass
    return out


def state(project: str) -> dict:
    rid = hqlib.current_run(project)
    runs = hqlib.list_runs(project)
    cur = _run_view(project, rid) if rid else (_run_view(project, runs[0]) if runs else None)
    arts = _artifacts(project)
    # 에이전트별 활동 집계 (현재/마지막 run + 전체 run 최근 이벤트)
    activity = {}
    for r in runs[:15]:
        for e in hqlib.read_events(project, r):
            at = e.get("agent_type") or ""
            if not at:
                continue
            key = at.split(":")[-1] if not at.startswith("external:") else at
            a = activity.setdefault(key, {"events": [], "runs": set(), "last": None})
            if e.get("event") in ("agent.start", "agent.stop", "guard.deny", "artifact.write"):
                a["events"].append({"ts": e.get("ts"), "event": e.get("event"), "run": r, "detail": e.get("detail") or {}})
                a["last"] = e.get("ts")
                a["runs"].add(r)
    for k, a in activity.items():
        a["events"] = sorted(a["events"], key=lambda x: x["ts"] or "")[-12:]
        a["runs"] = sorted(a["runs"], reverse=True)[:5]
    live_types = {(x.get("agent_type") or "").split(":")[-1] for x in (cur or {}).get("live_agents", [])} if rid else set()
    return {"now": hqlib.now_iso(), "project": project, "project_name": os.path.basename(project), "projects": _projects(), "hq_root": hqlib.HQ_ROOT,
            "teams": _teams(), "current": cur, "is_live": bool(rid), "live_types": sorted(live_types), "activity": activity,
            "runs": [{"run_id": r, **{k: v for k, v in (hqlib.load_manifest(project, r) or {}).items() if k in ("graph", "status", "started", "ended", "round")}} for r in runs[:12]],
            "artifacts": arts[:80], "gate": _gate(arts)}


# ------------------------------------------------------------------ 편집 (팀/에이전트 추가·제거)

def _refresh_marketplace_async():
    def go():
        try:
            subprocess.run(["claude", "plugin", "marketplace", "update", "ai-hq"], capture_output=True, timeout=120, shell=(os.name == "nt"))
        except Exception:
            pass
    threading.Thread(target=go, daemon=True).start()


def add_team(d: dict) -> dict:
    name = (d.get("name") or "").strip().lower()
    title = (d.get("title") or name).strip()
    desc = (d.get("desc") or "").strip()
    if not NAME_RE.match(name):
        return {"ok": False, "error": "이름은 영문 소문자·숫자·하이픈 2~40자 (예: design-team)"}
    root = os.path.join(hqlib.teams_dir(), name)
    if os.path.exists(root):
        return {"ok": False, "error": "이미 있는 팀 이름"}
    for sub in (".claude-plugin", "agents", "commands", "graphs", "skills"):
        os.makedirs(os.path.join(root, sub), exist_ok=True)
    with io.open(os.path.join(root, ".claude-plugin", "plugin.json"), "w", encoding="utf-8") as f:
        json.dump({"name": name, "version": "0.1.0", "description": f"{title}. {desc}".strip(), "author": {"name": "Junyong"}}, f, ensure_ascii=False, indent=2)
    with io.open(os.path.join(root, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {title} ({name})\n\n{desc}\n\n생성: {dt.date.today().isoformat()} (대시보드에서 추가)\n\n"
                "다음 할 일: agents/ 에 에이전트 추가 → graphs/<name>.json 그래프 정의(hq-core graph 스킬) → commands/<name>.md 커맨드.\n")
    mp, mpath = _marketplace()
    mp.setdefault("plugins", []).append({"name": name, "source": "./" + name, "description": f"{title}: {desc}".strip(": "), "category": "workflow"})
    with io.open(mpath, "w", encoding="utf-8") as f:
        json.dump(mp, f, ensure_ascii=False, indent=2)
    _refresh_marketplace_async()
    return {"ok": True, "path": root, "hint": f"설치: claude plugin install {name}@ai-hq (새 세션부터 로드)"}


AGENT_TEMPLATE = """---
name: {name}
description: {desc}
tools: {tools}
model: {model}
---

너는 AI-HQ {team} 의 **{title}** 다. {desc}

## 역할
- (이 에이전트가 맡는 일 한 줄씩. 목표·입력·출력은 그래프 prompt 가 준다 — 여기는 '어떻게 판단하는가')

## 판단 기준
- 근거 없는 주장은 쓰지 않는다. 웹 출처는 URL 과 날짜를 붙인다
- {kind_rule}

## 금지
- 배경 맥락을 추측해 옹호하지 않는다. 입력 파일만 근거로 삼는다
- `deliverables/`·`runs/` 에 쓰지 않는다 (하네스가 막는다)

## 출력 형식
- 지정된 출력 경로에 md 하나. frontmatter 에 type / status: draft / owner: {team}:{name} / inputs / created 필수
- 본문은 제목 → 요약 3줄 → 상세(표 또는 번호 목록) → 한계·불확실성 순서
"""

KIND = {
    "collect": {"model": "sonnet", "tools": "WebSearch, WebFetch, Read, Grep, Glob, Write", "rule": "수집형: 많이 찾되 요약은 짧게. 같은 사실은 한 번만. 못 찾으면 '못 찾음'이라고 쓴다"},
    "make": {"model": "inherit", "tools": "Read, Grep, Glob, Write, Edit, Bash", "rule": "제작형: 작게 만들고 바로 검증 가능한 형태로. 가정은 파일 상단에 적는다"},
    "judge": {"model": "inherit", "tools": "Read, Grep, Glob, WebSearch, Write", "rule": "판단형: 결론보다 근거를 먼저. 반대 근거를 반드시 하나 이상 찾아 적는다"},
}


def add_agent(d: dict) -> dict:
    team = (d.get("team") or "").strip()
    name = (d.get("name") or "").strip().lower()
    title = (d.get("title") or name).strip()
    desc = (d.get("desc") or "").strip()
    kind = d.get("kind") or "judge"
    if not NAME_RE.match(name):
        return {"ok": False, "error": "에이전트 이름은 영문 소문자·숫자·하이픈 (예: market-scanner)"}
    root = os.path.join(hqlib.teams_dir(), team)
    if not os.path.isdir(root):
        return {"ok": False, "error": "팀 없음: " + team}
    ad = os.path.join(root, "agents")
    os.makedirs(ad, exist_ok=True)
    fp = os.path.join(ad, name + ".md")
    if os.path.exists(fp):
        return {"ok": False, "error": "이미 있는 에이전트"}
    k = KIND.get(kind, KIND["judge"])
    with io.open(fp, "w", encoding="utf-8") as f:
        f.write(AGENT_TEMPLATE.format(name=name, desc=desc or title, tools=k["tools"], model=k["model"], team=team, title=title, kind_rule=k["rule"]))
    _refresh_marketplace_async()
    return {"ok": True, "path": fp, "hint": f"그래프 노드에서 \"agent\": \"{team}:{name}\" 로 부른다. 새 세션부터 로드"}


def remove_item(d: dict) -> dict:
    kind = d.get("kind")
    team = (d.get("team") or "").strip()
    name = (d.get("name") or "").strip()
    if team in ("hq-core",) and kind == "team":
        return {"ok": False, "error": "hq-core 는 하네스라 제거할 수 없다"}
    arch = os.path.join(hqlib.teams_dir(), "_archive", dt.datetime.now().strftime("%Y%m%d-%H%M%S"))
    if kind == "team":
        src = os.path.join(hqlib.teams_dir(), team)
        if not os.path.isdir(src):
            return {"ok": False, "error": "팀 없음"}
        os.makedirs(arch, exist_ok=True)
        shutil.move(src, os.path.join(arch, team))
        mp, mpath = _marketplace()
        mp["plugins"] = [p for p in mp.get("plugins", []) if p.get("name") != team]
        with io.open(mpath, "w", encoding="utf-8") as f:
            json.dump(mp, f, ensure_ascii=False, indent=2)
        _refresh_marketplace_async()
        return {"ok": True, "archived_to": os.path.join(arch, team), "hint": f"복구: 폴더를 teams/ 로 되돌리고 marketplace.json 에 다시 등록. 설치 해제: claude plugin uninstall {team}@ai-hq"}
    if kind == "agent":
        src = os.path.join(hqlib.teams_dir(), team, "agents", name + ".md")
        if not os.path.isfile(src):
            return {"ok": False, "error": "에이전트 파일 없음"}
        os.makedirs(os.path.join(arch, team, "agents"), exist_ok=True)
        shutil.move(src, os.path.join(arch, team, "agents", name + ".md"))
        _refresh_marketplace_async()
        return {"ok": True, "archived_to": os.path.join(arch, team, "agents", name + ".md"), "hint": "그래프에서 이 에이전트를 참조하는 노드가 있으면 고쳐야 한다"}
    return {"ok": False, "error": "kind 는 team|agent"}


# ------------------------------------------------------------------ HTML

HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.html")


def _html() -> str:
    try:
        with io.open(HTML_PATH, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return "<h1>dashboard.html 없음</h1>"



class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body: bytes, ctype="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/state":
            q = parse_qs(u.query)
            proj = q.get("project", [PROJECT])[0]
            if not os.path.isdir(proj):
                proj = PROJECT
            return self._send(200, json.dumps(state(proj), ensure_ascii=False).encode("utf-8"))
        if u.path == "/api/projects":
            return self._send(200, json.dumps(_projects(), ensure_ascii=False).encode("utf-8"))
        return self._send(200, _html().encode("utf-8"), "text/html; charset=utf-8")

    def do_POST(self):
        u = urlparse(self.path)
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
        except Exception:
            body = {}
        try:
            if u.path == "/api/team/add":
                res = add_team(body)
            elif u.path == "/api/agent/add":
                res = add_agent(body)
            elif u.path == "/api/remove":
                res = remove_item(body)
            else:
                res = {"ok": False, "error": "unknown endpoint"}
        except Exception as e:
            res = {"ok": False, "error": str(e)}
        return self._send(200, json.dumps(res, ensure_ascii=False).encode("utf-8"))


def main():
    global PROJECT
    hqlib.utf8_stdio()
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=None)
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    PROJECT = os.path.abspath(a.project or hqlib.find_project())
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), H)
    print(f"AI-HQ 조직도 대시보드  http://127.0.0.1:{a.port}/   project={PROJECT}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
