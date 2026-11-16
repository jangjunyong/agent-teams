---
name: graph
description: AI-HQ 파이프라인 그래프(graph.json)의 스키마와 오케스트레이터 실행 규약. 팀 커맨드(/verify-team:verify, /planning-team:plan 등)나 /hq-core:run 으로 파이프라인을 돌릴 때, 또는 새 팀의 그래프를 설계할 때 반드시 이 규약을 따른다.
---

# 그래프 규약 (graph engineering)

파이프라인은 **선언적 그래프**다. 노드 = 에이전트(또는 오케스트레이터 단계), 엣지 = 파일 핸드오프. 오케스트레이터는 그래프를 읽고 `hq.py` 로 레저를 남기며 순서대로 실행한다. 대화 맥락이 아니라 **파일과 레저**가 상태의 진실이다.

## 1. graph.json 스키마 — `teams/<team>/graphs/<name>.json`

```json
{
  "name": "verify", "team": "verify-team", "version": 2,
  "title": "선행조사 → 레드팀 → 판정",
  "inputs": {"target": "검증 대상 md 경로(프로젝트 루트 기준)"},
  "policy": {"max_rounds": 2, "escalate_to": "human", "on_fail": "loopback"},
  "nodes": [
    {
      "id": "originality", "title": "선행사례 조사",
      "agent": "verify-team:originality-checker",
      "inputs": ["{target}"],
      "outputs": ["_work/verify/{stem}.originality.md"],
      "when": "대상이 아이디어·기획·주제일 때. 코드·기술문서면 skip",
      "prompt": "목표: … 제약: … 완료조건: … (플레이스홀더 사용 가능)"
    },
    { "id": "verdict", "title": "판정", "agent": "orchestrator", "skill": "verify-team:verdict",
      "inputs": ["{originality.out}", "{redteam.out}"], "outputs": ["{dir}/{stem}.verdict.md"], "gate": "G3" }
  ]
}
```

- `agent`: `"<plugin>:<agent-name>"` → 서브에이전트 호출. `"orchestrator"` → 메인 세션이 `skill` 규격대로 직접 작성
- 플레이스홀더: `{<input>}` `{stem}` `{dir}` `{today}` `{<node>.out}` `{<node>.outN}`
- 실행 순서는 `inputs` 가 참조하는 노드 출력으로 자동 결정(토폴로지). 서로 독립인 노드는 **병렬 호출**해도 된다(Agent 를 한 메시지에 여러 개)
- `when` 은 사람 말로 쓴 실행 조건. 오케스트레이터가 판단해 `node skip` 한다
- 출력은 항상 `_work/` 아래. `deliverables/` 는 게이트 통과 후 오케스트레이터만 옮긴다

## 2. 실행 규약 (오케스트레이터 알고리즘)

hq.py 경로: `%AI_HQ_ROOT%\teams\hq-core\scripts\hq.py` (기본 `%AI_HQ_ROOT%`). 아래 `HQ` 로 표기.

```
1. 프로젝트 루트(=_work/ 가 있는 폴더)에서 시작한다. 아니면 --project 로 지정
2. py HQ run start <team>/<graph> target=<경로> [round=N]
   → run_id 생성, 실행 계획(노드·입출력·프롬프트) 출력. 이 출력만 보고 진행한다
3. 각 노드를 순서대로:
   a. py HQ node start <id>
   b. agent 노드: Agent 도구로 subagent_type=<agent> 호출. 프롬프트는 계획에 찍힌 prompt 를 그대로 쓴다
      (목표·제약·완료조건 + 입력 경로 + 출력 경로). 배경 설명·옹호성 맥락을 덧붙이지 않는다
      orchestrator 노드: 지정된 skill 규격대로 직접 파일을 쓴다
   c. py HQ node done <id>  ← 출력 파일 존재·frontmatter(type/status/owner) 검사. 실패하면 exit 2 → 에이전트에게 보완 지시 후 재시도(최대 1회), 그래도 실패면 node fail
   d. when 조건 불충족이면 b 대신 py HQ node skip <id> --note "사유"
4. 마지막 노드가 판정(verdict)이면 결과에 따라:
   PASS  → 대상 status: approved, verified_by 갱신 → run end --status done
   FAIL/CONDITIONAL → 대상 status 갱신 + verify_round +1 → run end --status failed → 사용자에게 반려 사유 보고
   round ≥ policy.max_rounds 인데 또 FAIL → run end --status escalated → 사람에게 에스컬레이션
5. 사용자 보고: 판정 · 핵심 근거 3줄 · 반려 사유 · 다음 액션. run_id 와 산출물 경로를 반드시 적는다
```

### 불변 규칙
- 세션이 끊겼거나 이전 run 이 미완료면 새 run 을 만들지 말고 `py HQ run resume` 으로 이어라 (running 노드는 pending 으로 리셋됨)
- 노드를 건너뛸 때는 반드시 `node skip`. 레저에 안 남는 진행은 없다
- 출력 파일이 이미 있고 최신이면 재실행하지 않고 `node skip --note "기존 산출물 사용"` (멱등)
- 서브에이전트는 `deliverables/`·`runs/` 에 쓰지 못한다 (가드가 차단). 쓰려고 하면 설계가 틀린 것이다
- 같은 run 안에서 판정 횟수는 `verify_round` 로 대상 파일 frontmatter 에 남긴다 (세션이 바뀌어도 회차 추적)
- 에이전트 호출 결과를 오케스트레이터가 요약·윤색하지 않는다. 판정은 파일에 쓰인 것이 전부다

## 3. 새 그래프 설계 체크리스트
- 각 노드가 **파일 하나 이상**을 출력하는가 (출력 없는 노드는 노드가 아니다)
- 판단형 노드(심사·반박·종합)와 수집형 노드(검색·요약)를 분리했는가 (모델 라우팅 힌트)
- 실패 경로가 있는가: 반려 루프백 횟수, 에스컬레이션 조건
- 적대적 검증 노드가 있는가 (자기 산출물을 자기가 통과시키지 않는다)
- 병렬 가능한 노드를 굳이 직렬로 묶지 않았는가

## 4. 외부 작업자 노드 (Cursor Agent · OpenCode)

`"agent": "external:cursor"` 또는 `"external:opencode"` 로 선언하면 Claude 서브에이전트 대신 외부 코딩 에이전트가 그 노드를 맡는다 (대량 코드 작성·리팩터·테스트 실행 같은 제작형 작업에 적합).

실행: 오케스트레이터가 계획의 prompt 를 `_work/.hq/prompts/<node>.md` 에 쓰고
`py %HQ%/worker.py cursor --node <id> --prompt-file _work/.hq/prompts/<id>.md [--model ...] [--mode plan|ask]`
(opencode 도 동일). 어댑터가 레저에 `agent.start/stop (agent_type=external:cursor)` 를 남기고 로그를 `runs/<run>/workers/` 에 둔다. 그 뒤 `node done` 으로 출력 검사는 똑같이 한다.
원칙: 외부 작업자에게도 3요소 프롬프트·파일 입출력만. 외부 작업자 산출물은 **반드시** 검증 노드(레드팀·코드리뷰·테스트)를 거친다 — 신뢰하지 않고 검사한다.

## 5. 미션 그래프 (팀 릴레이 — 서브그래프 노드)

여러 팀을 하나의 미션으로 묶을 때는 노드에 `"subgraph": "<team>/<graph>"` 와 `"subgraph_inputs": {…}` 를 선언한다 (예: `hq-core/graphs/contest.json` — 조사→기획→검증→덱).

실행 규약 (오케스트레이터):
1. 부모 미션: `py HQ run start hq-core/contest idea=… [question=…]` → 부모 run_id 확보
2. 서브그래프 노드마다: `node start <id>` → **`py HQ run start <subgraph> <subgraph_inputs…> --parent <부모 run_id>`** 로 자식 run 생성 → 자식 그래프를 그 팀 규약대로 끝까지 실행 → `run end` (자식이 끝나면 current 는 자동으로 부모로 복귀) → 부모의 `node done <id>`
3. 자식이 failed 면 부모 `node fail` 후 policy 대로 루프백/에스컬레이션 (예: verify FAIL → plan 반려 반영 후 재기획)
4. 레저: 부모 events 에 `child.start/child.end` 가 남고 자식 manifest 에 `parent_run` 이 남는다 — 대시보드가 이 체인으로 미션 전체를 그린다

원칙: 자식 run 안에서의 상태는 자식 레저가 진실이고, 부모는 자식의 최종 산출물 파일만 본다 (팀 경계 = 파일).

