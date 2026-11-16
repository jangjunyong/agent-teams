#!/usr/bin/env bash
# G3 게이트: deliverables/ 안에 status: approved가 아닌 md가 있으면 종료를 한 번 막고 알린다.
# 방어 규칙: stop 훅 재진입 시(stop_hook_active) 무조건 통과시켜 무한루프를 막는다.
# 주의: hooks.json 은 gate-check.py 만 호출한다. 이 파일은 WSL/리눅스용 예비 구현이며
#       판정 로직은 gate-check.py 와 동일하게 유지할 것 (v0.2.1 에서 동기화).

input=$(cat 2>/dev/null || true)

if printf '%s' "$input" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi

# stdin JSON 의 cwd 필드를 기준 경로로 사용 (없으면 현재 디렉토리)
base=$(printf '%s' "$input" | sed -n 's/.*"cwd"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
[ -n "$base" ] && [ -d "$base" ] || base=$(pwd)

# frontmatter 블록(--- ~ ---) 안의 status: approved 정확 일치만 승인으로 판정
is_approved() {
  awk '
    NR==1 { if ($0 !~ /^---[[:space:]]*$/) { exit 1 }; next }
    /^---[[:space:]]*$/ { exit 1 }
    /^status:[[:space:]]*approved[[:space:]]*$/ { found=1; exit }
    NR>200 { exit 1 }
    END { exit found ? 0 : 1 }
  ' "$1"
}

roots=""
[ -d "$base/deliverables" ] && roots="$base/deliverables"
for d in "$base"/projects/*/deliverables; do
  [ -d "$d" ] && roots="$roots
$d"
done

[ -n "$roots" ] || exit 0

violations=""
while IFS= read -r f; do
  [ -n "$f" ] || continue
  if ! is_approved "$f"; then
    violations="${violations}${f}\n"
  fi
done < <(printf '%s\n' "$roots" | while IFS= read -r r; do
  [ -n "$r" ] && find "$r" -name "*.md" -type f 2>/dev/null
done)

if [ -n "$violations" ]; then
  printf '게이트 위반(G3): deliverables/ 안에 status: approved가 아닌 파일이 있습니다.\n' >&2
  printf '%b' "$violations" >&2
  printf '해당 파일을 /verify-team:verify로 검증해 승인받거나 _work/로 옮긴 뒤 종료하세요.\n' >&2
  exit 2
fi

exit 0
