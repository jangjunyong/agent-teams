# -*- coding: utf-8 -*-
"""외부 작업자 어댑터 — 그래프 노드를 Claude 서브에이전트 대신 외부 코딩 에이전트(Cursor Agent, OpenCode)에게 맡긴다.

  py worker.py cursor   --project <dir> --node <id> --prompt-file <md> [--model <m>] [--mode plan|ask] [--timeout 900]
  py worker.py opencode --project <dir> --node <id> --prompt-file <md> [--model <m>] [--timeout 900]
  py worker.py list                               설치된 외부 작업자 확인

동작: 프롬프트 파일을 읽어 외부 에이전트를 비대화형으로 실행하고, 표준출력을 runs/<run>/workers/<node>.<worker>.log 에 남기며,
레저에 agent.start / agent.stop (agent_type = external:<worker>) 이벤트를 기록한다. 출력 파일 생성은 프롬프트가 지시한 경로에 외부 에이전트가 직접 한다
(→ 이후 `hq.py node done <id>` 가 검사한다).
"""
import argparse
import io
import os
import shutil
import subprocess
import sys
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hqlib  # noqa: E402

CURSOR_CANDIDATES = [
    os.path.expandvars(r"%LOCALAPPDATA%\cursor-agent\cursor-agent.cmd"),
    os.path.expandvars(r"%LOCALAPPDATA%\cursor-agent\agent.cmd"),
]


def find_cursor():
    p = shutil.which("cursor-agent") or shutil.which("agent")
    if p:
        return p
    for c in CURSOR_CANDIDATES:
        if os.path.isfile(c):
            return c
    return None


def find_opencode():
    return shutil.which("opencode")


def cmd_list(a):
    c = find_cursor(); o = find_opencode()
    print(f"cursor   : {c or '없음'}")
    print(f"opencode : {o or '없음 (설치: https://opencode.ai)'}")
    return 0


def run_worker(kind: str, exe: str, args: list, a) -> int:
    project = os.path.abspath(a.project or hqlib.find_project())
    rid = hqlib.current_run(project)
    with io.open(a.prompt_file, encoding="utf-8") as f:
        prompt = f.read()
    aid = f"ext-{kind}-{uuid.uuid4().hex[:6]}"
    atype = f"external:{kind}"
    logdir = os.path.join(hqlib.run_dir(project, rid or "_unassigned"), "workers")
    os.makedirs(logdir, exist_ok=True)
    logp = os.path.join(logdir, f"{a.node}.{kind}.log")
    hqlib.append_event(project, rid, {"event": "agent.start", "agent_id": aid, "agent_type": atype, "detail": {"node": a.node, "exe": exe}})
    t0 = time.time()
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        with io.open(logp, "w", encoding="utf-8", errors="replace") as log:
            proc = subprocess.run([exe] + args + [prompt], cwd=project, stdout=log, stderr=subprocess.STDOUT, timeout=a.timeout, env=env, shell=(os.name == "nt" and exe.lower().endswith(".cmd")))
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        rc = 124
    dur = round(time.time() - t0, 1)
    tail = ""
    try:
        with io.open(logp, encoding="utf-8", errors="replace") as f:
            tail = f.read()[-400:]
    except OSError:
        pass
    hqlib.append_event(project, rid, {"event": "agent.stop", "agent_id": aid, "agent_type": atype, "detail": {"node": a.node, "rc": rc, "seconds": dur, "log": os.path.relpath(logp, project), "last_message": tail}})
    print(f"[{atype}] rc={rc} {dur}s  log={logp}")
    return 0 if rc == 0 else 2


def cmd_cursor(a):
    exe = find_cursor()
    if not exe:
        print("cursor-agent 를 찾지 못했다. Cursor 앱에서 Agent CLI 를 설치하거나 PATH 에 추가하라.", file=sys.stderr)
        return 2
    args = ["-p", "--output-format", "text", "--force"]
    if a.model:
        args += ["--model", a.model]
    if a.mode:
        args += ["--mode", a.mode]
    return run_worker("cursor", exe, args, a)


def cmd_opencode(a):
    exe = find_opencode()
    if not exe:
        print("opencode 미설치. https://opencode.ai 참조 (설치 후 `opencode run` 을 쓴다).", file=sys.stderr)
        return 2
    args = ["run"]
    if a.model:
        args += ["--model", a.model]
    return run_worker("opencode", exe, args, a)


def main():
    hqlib.utf8_stdio()
    p = argparse.ArgumentParser(prog="worker")
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("list").set_defaults(fn=cmd_list)
    for name, fn in (("cursor", cmd_cursor), ("opencode", cmd_opencode)):
        q = sp.add_parser(name)
        q.add_argument("--project"); q.add_argument("--node", required=True); q.add_argument("--prompt-file", required=True)
        q.add_argument("--model"); q.add_argument("--mode", choices=["plan", "ask"]); q.add_argument("--timeout", type=int, default=900)
        q.set_defaults(fn=fn)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
