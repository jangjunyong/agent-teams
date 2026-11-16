# -*- coding: utf-8 -*-
"""AI-HQ 하네스 공용 라이브러리 (표준 라이브러리만 사용).

개념
- project   : projects/<이름>/ 폴더. `_work/` 와 `deliverables/` 를 가진다
- run       : 그래프 1회 실행. projects/<p>/runs/<run_id>/{manifest.json, events.jsonl}
- current   : projects/<p>/_work/.hq/current_run 에 진행 중 run_id 가 적혀 있다 (훅이 이걸로 run 을 찾는다)
- graph     : teams/<team>/graphs/<name>.json — 노드(에이전트)·입출력(파일)·게이트·정책 선언
"""
from __future__ import annotations

import datetime as _dt
import io
import json
import os
import re
import sys
import uuid

# 기본값: 이 레포를 <AI_HQ_ROOT>/teams 로 받았을 때의 상위 폴더
HQ_ROOT = os.environ.get("AI_HQ_ROOT") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def now_iso() -> str:
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def utf8_stdio() -> None:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


# ---------------------------------------------------------------- project / run

def find_project(start: str | None = None) -> str:
    """cwd 에서 위로 올라가며 프로젝트 루트를 찾는다. `_work` 또는 `deliverables` 폴더가 있는 가장 가까운 조상."""
    cur = os.path.abspath(start or os.getcwd())
    for _ in range(12):
        if os.path.isdir(os.path.join(cur, "_work")) or os.path.isdir(os.path.join(cur, "deliverables")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return os.path.abspath(start or os.getcwd())


def hq_dir(project: str) -> str:
    return os.path.join(project, "_work", ".hq")


def runs_dir(project: str) -> str:
    return os.path.join(project, "runs")


def run_dir(project: str, run_id: str) -> str:
    return os.path.join(runs_dir(project), run_id)


def current_run(project: str) -> str | None:
    p = os.path.join(hq_dir(project), "current_run")
    try:
        with io.open(p, encoding="utf-8") as f:
            rid = f.read().strip()
        return rid or None
    except OSError:
        return None


def set_current_run(project: str, run_id: str | None) -> None:
    os.makedirs(hq_dir(project), exist_ok=True)
    p = os.path.join(hq_dir(project), "current_run")
    if run_id is None:
        try:
            os.remove(p)
        except OSError:
            pass
        return
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(run_id)


def new_run_id(graph_name: str) -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + graph_name + "-" + uuid.uuid4().hex[:4]


def append_event(project: str, run_id: str | None, event: dict) -> None:
    """events.jsonl 에 한 줄 추가. run_id 가 없으면 runs/_unassigned/ 에 쌓는다 (훅이 run 밖에서 불릴 때)."""
    rid = run_id or "_unassigned"
    d = run_dir(project, rid)
    os.makedirs(d, exist_ok=True)
    event = dict(event)
    event.setdefault("ts", now_iso())
    event.setdefault("run_id", run_id)
    with io.open(os.path.join(d, "events.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def read_events(project: str, run_id: str) -> list[dict]:
    p = os.path.join(run_dir(project, run_id), "events.jsonl")
    out: list[dict] = []
    try:
        with io.open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    except OSError:
        pass
    return out


def load_manifest(project: str, run_id: str) -> dict | None:
    p = os.path.join(run_dir(project, run_id), "manifest.json")
    try:
        with io.open(p, encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return None


def save_manifest(project: str, run_id: str, manifest: dict) -> None:
    d = run_dir(project, run_id)
    os.makedirs(d, exist_ok=True)
    with io.open(os.path.join(d, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def list_runs(project: str) -> list[str]:
    d = runs_dir(project)
    try:
        names = [n for n in os.listdir(d) if os.path.isdir(os.path.join(d, n)) and not n.startswith("_")]
    except OSError:
        return []
    return sorted(names, reverse=True)


# ---------------------------------------------------------------- frontmatter

_FM_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_\-]*):\s*(.*)$")


def read_frontmatter(path: str, max_lines: int = 200) -> dict | None:
    """첫 줄이 --- 인 md 의 YAML 블록을 아주 단순하게 파싱한다 (키: 값 한 줄씩, 리스트는 [a, b] 또는 - 항목)."""
    try:
        with io.open(path, encoding="utf-8", errors="ignore") as f:
            first = f.readline()
            if first.strip() != "---":
                return None
            fm: dict = {}
            last_key = None
            for _ in range(max_lines):
                line = f.readline()
                if not line:
                    break
                s = line.rstrip("\n")
                if s.strip() == "---":
                    return fm
                if s.startswith("- ") or s.startswith("  - "):
                    if last_key is not None:
                        v = fm.get(last_key)
                        if not isinstance(v, list):
                            v = [] if v in (None, "", "[]") else [v]
                        v.append(s.strip()[2:].strip())
                        fm[last_key] = v
                    continue
                m = _FM_LINE.match(s)
                if m:
                    k, v = m.group(1), m.group(2).strip()
                    if v.startswith("[") and v.endswith("]"):
                        inner = v[1:-1].strip()
                        v = [x.strip().strip("'\"") for x in inner.split(",") if x.strip()] if inner else []
                    else:
                        v = v.strip("'\"")
                    fm[k] = v
                    last_key = k
            return fm
    except OSError:
        return None


def update_frontmatter(path: str, updates: dict) -> bool:
    """frontmatter 의 키를 갱신(없으면 추가). 본문은 건드리지 않는다. 리스트 값은 [a, b] 형식으로 쓴다."""
    try:
        with io.open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return False
    if not text.startswith("---"):
        return False
    end = text.find("\n---", 3)
    if end < 0:
        return False
    head, rest = text[3:end], text[end + 4 :]
    lines = head.strip("\n").split("\n")
    done = set()
    out = []
    for ln in lines:
        m = _FM_LINE.match(ln)
        if m and m.group(1) in updates:
            k = m.group(1)
            out.append(f"{k}: {_fmt(updates[k])}")
            done.add(k)
        else:
            out.append(ln)
    for k, v in updates.items():
        if k not in done:
            out.append(f"{k}: {_fmt(v)}")
    new = "---\n" + "\n".join(out) + "\n---" + rest
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(new)
    return True


def _fmt(v) -> str:
    if isinstance(v, list):
        return "[" + ", ".join(str(x) for x in v) + "]"
    return str(v)


# ---------------------------------------------------------------- graphs

def teams_dir() -> str:
    return os.path.join(HQ_ROOT, "teams")


def find_graph(ref: str) -> str | None:
    """ref = 'verify-team/verify' 또는 'verify' (모든 팀에서 검색) 또는 파일 경로."""
    if os.path.isfile(ref):
        return os.path.abspath(ref)
    team, _, name = ref.partition("/")
    if name:
        p = os.path.join(teams_dir(), team, "graphs", name + ".json")
        return p if os.path.isfile(p) else None
    # 이름만 주어진 경우: 모든 팀 탐색
    try:
        for t in os.listdir(teams_dir()):
            p = os.path.join(teams_dir(), t, "graphs", ref + ".json")
            if os.path.isfile(p):
                return p
    except OSError:
        pass
    return None


def list_graphs() -> list[dict]:
    out = []
    try:
        for t in sorted(os.listdir(teams_dir())):
            gd = os.path.join(teams_dir(), t, "graphs")
            if not os.path.isdir(gd):
                continue
            for f in sorted(os.listdir(gd)):
                if f.endswith(".json"):
                    try:
                        with io.open(os.path.join(gd, f), encoding="utf-8") as fh:
                            g = json.load(fh)
                        out.append({"team": t, "name": g.get("name", f[:-5]), "file": os.path.join(gd, f), "title": g.get("title", ""), "nodes": len(g.get("nodes", []))})
                    except Exception:
                        pass
    except OSError:
        pass
    return out


def load_graph(ref: str) -> dict:
    p = find_graph(ref)
    if not p:
        raise FileNotFoundError(f"graph not found: {ref}")
    with io.open(p, encoding="utf-8") as f:
        g = json.load(f)
    g["_file"] = p
    return g


_PLACE = re.compile(r"\{([A-Za-z0-9_\.]+)\}")


def resolve_graph(graph: dict, inputs: dict) -> dict:
    """플레이스홀더 치환. 사용 가능: {<input>}, {stem}, {dir}, {<node>.out<N>}, {<node>.out}(=out0), {today}, {run_id}."""
    ctx = dict(inputs)
    target = inputs.get("target") or next(iter(inputs.values()), "")
    if target:
        ctx.setdefault("stem", os.path.splitext(os.path.basename(target))[0])
        ctx.setdefault("dir", os.path.dirname(target) or ".")
    ctx.setdefault("today", _dt.date.today().isoformat())
    nodes = []
    for n in graph.get("nodes", []):
        n = dict(n)
        outs = [_sub(o, ctx) for o in n.get("outputs", [])]
        n["outputs"] = outs
        for i, o in enumerate(outs):
            ctx[f"{n['id']}.out{i}"] = o
        if outs:
            ctx[f"{n['id']}.out"] = outs[0]
        nodes.append(n)
    # 두 번째 패스: inputs/prompt/subgraph_inputs 에 노드 출력 참조
    for n in nodes:
        n["inputs"] = [_sub(x, ctx) for x in n.get("inputs", [])]
        if "prompt" in n:
            n["prompt"] = _sub(n["prompt"], ctx)
        if isinstance(n.get("subgraph_inputs"), dict):
            n["subgraph_inputs"] = {k: _sub(str(v), ctx) for k, v in n["subgraph_inputs"].items()}
    g = dict(graph)
    g["nodes"] = nodes
    g["resolved_inputs"] = inputs
    g["ctx"] = {k: v for k, v in ctx.items() if isinstance(v, str)}
    return g


def _sub(s: str, ctx: dict) -> str:
    def rep(m):
        k = m.group(1)
        return str(ctx.get(k, m.group(0)))
    return _PLACE.sub(rep, s)


def topo(nodes: list[dict]) -> list[dict]:
    """inputs 가 다른 노드의 출력을 참조하면 그 뒤에 오도록 정렬 (선언 순서 보존 우선)."""
    by_out = {}
    for n in nodes:
        for o in n.get("outputs", []):
            by_out[o] = n["id"]
    deps = {n["id"]: {by_out[i] for i in n.get("inputs", []) if i in by_out and by_out[i] != n["id"]} for n in nodes}
    order: list[dict] = []
    placed = set()
    remaining = list(nodes)
    while remaining:
        progressed = False
        for n in list(remaining):
            if deps[n["id"]] <= placed:
                order.append(n)
                placed.add(n["id"])
                remaining.remove(n)
                progressed = True
        if not progressed:  # 순환 — 선언 순서대로 강제
            order.extend(remaining)
            break
    return order
