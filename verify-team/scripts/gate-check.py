#!/usr/bin/env python3
# G3 게이트: deliverables/ 안에 status: approved가 아닌 md가 있으면 종료를 한 번 막고 알린다.
# 방어 규칙: stop 훅 재진입 시(stop_hook_active) 무조건 통과시켜 무한루프를 막는다.
# Windows/macOS/Linux 공통. bash 불필요.
#
# v0.2.1 수정 (설계리뷰_v0.2.md 반영):
# - stdin JSON의 cwd 필드를 기준 경로로 사용 (없으면 os.getcwd() 폴백)
# - <cwd>/deliverables 외에 <cwd>/projects/*/deliverables 도 스캔
#   → ai-hq 루트 오케스트레이터 세션에서도 게이트가 작동한다
# - status 판정을 frontmatter 블록(--- ~ ---) 안의 정확 일치로 교체
#   → "status: not-approved"·본문 규격 인용 오통과, 15줄 초과 frontmatter 오차단 제거
# - 깊이 제한 제거: deliverables/ 전체를 재귀 검사 (G3 규칙에 깊이 제한 없음)

import io
import json
import os
import re
import sys

_STATUS_APPROVED = re.compile(r"^status:\s*approved\s*$")
_FRONTMATTER_MAX_LINES = 200  # 비정상 파일 방어용 상한


def emit(msg: str) -> None:
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    try:
        sys.stderr.write(msg + "\n")
    except Exception:
        try:
            sys.stderr.buffer.write(msg.encode("utf-8", "replace") + b"\n")
        except Exception:
            sys.stderr.write(msg.encode("ascii", "replace").decode() + "\n")


def is_approved(path: str):
    """frontmatter 블록 안에 status: approved 가 있으면 True.
    frontmatter 가 없거나 status 가 다르면 False. 읽기 실패는 None(검사 제외)."""
    try:
        with io.open(path, "r", encoding="utf-8", errors="ignore") as f:
            if f.readline().strip() != "---":
                return False
            for _ in range(_FRONTMATTER_MAX_LINES):
                line = f.readline()
                if not line:
                    return False
                s = line.strip()
                if s == "---":
                    return False
                if _STATUS_APPROVED.match(s):
                    return True
    except OSError:
        return None
    return False


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    if data.get("stop_hook_active"):
        return 0

    base = data.get("cwd") or os.getcwd()

    roots = []
    direct = os.path.join(base, "deliverables")
    if os.path.isdir(direct):
        roots.append(direct)
    projects = os.path.join(base, "projects")
    if os.path.isdir(projects):
        try:
            names = sorted(os.listdir(projects))
        except OSError:
            names = []
        for name in names:
            sub = os.path.join(projects, name, "deliverables")
            if os.path.isdir(sub):
                roots.append(sub)

    bad = []
    for root in roots:
        for dirpath, _dirs, files in os.walk(root):
            for name in files:
                if not name.lower().endswith(".md"):
                    continue
                path = os.path.join(dirpath, name)
                if is_approved(path) is False:
                    bad.append(os.path.relpath(path, base))

    if bad:
        emit("게이트 위반(G3): deliverables/ 안에 status: approved가 아닌 파일이 있습니다.")
        for p in bad[:10]:
            emit(" - " + p)
        emit("해당 파일을 /verify-team:verify 로 검증해 승인받거나 _work/ 로 옮긴 뒤 종료하세요.")
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
