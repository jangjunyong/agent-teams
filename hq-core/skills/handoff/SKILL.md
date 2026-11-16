---
name: handoff
description: AI-HQ 산출물 계약(frontmatter 스키마)과 런 레저 규약. 에이전트 간 파일 핸드오프, 산출물 status 갱신, runs/ 이벤트 해석이 필요할 때 따른다. 모든 팀의 모든 md 산출물에 적용된다.
---

# 핸드오프 계약 (harness engineering)

노드 간 전달은 **파일로만** 한다. 파일의 frontmatter 가 계약이고, `hq.py node done` 이 그 계약을 기계적으로 검사한다.

## 1. 산출물 frontmatter (필수 3 + 권장)

```yaml
---
type: proposal | report | design | analysis | verdict | plan | spec | research | brief
status: draft | in-review | approved | rejected
owner: <팀명 또는 에이전트명>        # 예: verify-team, research-team:web-researcher
created: YYYY-MM-DD
verified_by: []                       # 검증 통과 시 검증자 추가
inputs: [<이 산출물이 읽은 파일 경로들>]   # 권장 — 추적성
run: <run_id>                         # 권장 — 어느 run 이 만들었나
verify_round: 0                       # 검증 대상 파일에만. 반려될 때마다 +1 (C5)
---
```

- `type` `status` `owner` 가 없으면 `node done` 이 실패한다 → 에이전트 프롬프트의 완료조건에 항상 명시하라
- `status` 는 **정확히** 위 4값 중 하나. `not-approved` 같은 변형 금지 (게이트는 정확 일치로 본다)
- 검증 대상 파일의 `verify_round` 는 verdict FAIL/CONDITIONAL 때 오케스트레이터가 +1 한다. 이 값이 `policy.max_rounds` 에 도달한 뒤 또 FAIL 이면 사람 에스컬레이션

## 2. 노드 프롬프트 3요소

서브에이전트 지시는 항상 이 꼴이다 (그래프 `prompt` 필드에 그대로 쓴다):

```
목표: <무엇을 만들 것인가 한 문장>
입력: <읽을 파일 경로들> (이 파일만 근거로 삼는다. 배경 맥락은 없다)
출력: <쓸 파일 경로 하나> — frontmatter type/status/owner 필수, status 는 draft
제약: <하지 말 것 — 예: 옹호 금지, 웹 검색 범위, 길이>
완료조건: <검사 가능한 기준 — 예: 발견 사항 5개 이상, 각 항목에 근거 링크>
```

## 3. 런 레저 — `projects/<p>/runs/<run_id>/`

| 파일 | 누가 쓰나 | 내용 |
|---|---|---|
| `manifest.json` | hq.py | 그래프 스냅샷, inputs, node_state, node_times, status, round |
| `events.jsonl` | hq.py + 훅 | 한 줄 = 한 이벤트 (아래 표) |
| `_work/.hq/current_run` | hq.py | 진행 중 run_id. 훅이 이걸로 run 을 찾는다 |

| event | 발생원 | 의미 |
|---|---|---|
| `run.start` / `run.end` | hq.py | 실행 시작/종료 (status: done·failed·escalated·aborted) |
| `node.start` / `node.done` / `node.fail` / `node.skip` | hq.py | 노드 상태 전이 |
| `agent.start` / `agent.stop` | 훅 SubagentStart/Stop | 서브에이전트 생명주기 (agent_type, agent_id) |
| `artifact.write` | 훅 PostToolUse Write/Edit | 파일 기록 + frontmatter status 스냅샷 |
| `guard.deny` | 훅 PreToolUse | deliverables/·runs/ 직접 쓰기 차단 |
| `session.start` / `turn.stop` | 훅 | 세션 경계 |

레저는 **읽기 전용**이다. 사람도 에이전트도 손으로 고치지 않는다 (가드가 막는다). 해석은 `py hq.py status` 또는 대시보드로 한다.

## 4. 게이트
- **G1** 아이디어·기획은 originality 노드 통과 전 "확정" 금지
- **G2** 코드 산출물은 완료 선언 전 보안·코드리뷰 노드 통과
- **G3** `deliverables/` 에는 `status: approved` 만. Stop 훅(verify-team gate-check)이 종료를 1회 막고, PreToolUse 가드가 서브에이전트의 직접 쓰기를 차단한다
