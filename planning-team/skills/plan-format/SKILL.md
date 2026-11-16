---
name: plan-format
description: 기획팀(planning-team) 산출물 4종 — 기획안(option)·심사표(judge)·스펙(spec)·실행 계획(plan) — 의 양식과 status 규칙. planning-team/plan 그래프의 모든 노드 출력과 오케스트레이터의 실행 계획 작성은 이 규격을 따른다. 기획 산출물을 쓰거나 읽어 판단할 때 사용한다.
---

# plan-format 규격

기획팀의 산출물은 **기획안 → 심사표 → 스펙 → 실행 계획** 순으로 흐른다. 각 단계는 앞 단계 파일만 근거로 삼고, 근거는 항상 `파일경로#섹션` 으로 적는다. 이 규격에 없는 섹션을 빼거나 이름을 바꾸면 다음 노드가 읽지 못한다.

## 0. 공통 규칙

- frontmatter 필수 3 + 권장: `type` `status` `owner` 는 없으면 `node done` 이 실패한다. `inputs`(읽은 파일 경로 목록) `created`(YYYY-MM-DD) `run`(run_id) 을 함께 쓴다
- **status 는 planning-team 의 모든 산출물에서 `draft` 다.** 기획팀은 `approved` 를 쓰지 않는다 (승인은 verify-team 판정 뒤 오케스트레이터가 한다 — 아래 5절)
- **근거 표기**: `_work/plan/<stem>.option-b.md#4` 처럼 `경로#섹션번호`. 원문 인용은 한 문장 이내로 따옴표. 근거 없는 문장은 '추정' 이라고 표시한다
- **G1 어휘 금지**: originality 검증(verify-team) 통과 전에는 기획안·스펙·실행 계획 본문에 "확정" "최종" "승인됨" 을 쓰지 않는다. 대신 "선정안" "현재안" 이라고 쓴다
- 파일 위치: 중간 산출물은 `_work/plan/`, 실행 계획만 `_work/<stem>.plan.md` (검증 대상이 되는 파일이므로 verify 그래프가 찾기 쉬운 곳에 둔다). `deliverables/` 에는 쓰지 않는다
- 길이: 기획안 ≤ 1,500자 · 심사표 제한 없음(근거 12칸 전부 채움) · 스펙 ≤ 2,000자 · 실행 계획 ≤ 2,500자. 길이를 채우려 문장을 늘리지 않는다

## 1. 기획안 (option) — `_work/plan/<stem>.option-{a|b|c}.md`

관점 하나로만 쓴 독립 기획안. 관점은 노드 프롬프트가 주입한다.

| 노드 | perspective | 최우선 | 의도적 후순위 |
|---|---|---|---|
| brainstorm_a | `user-value` | 사용자가 얻는 가치·쓰는 장면·전환 이유 | 구현 난이도, 경쟁 |
| brainstorm_b | `feasibility` | 지금 가진 기술·시간·사람으로 되는가, 최소 구현 경로 | 확장성, 차별성 |
| brainstorm_c | `risk-differentiation` | 무엇이 다르고 무엇이 이 안을 죽이는가 | 편의 기능, 구현 순서 |

```markdown
---
type: proposal
status: draft
owner: planning-team:brainstormer
perspective: user-value | feasibility | risk-differentiation
inputs: [<idea 경로>]
created: YYYY-MM-DD
run: <run_id>
---
# 기획안 A|B|C: <한 줄 제목> (관점: <perspective>)

## 1. 문제 재정의
(이 관점에서 본 문제 한 문단. 아이디어 원문의 어느 문장에서 나왔는지 인용)

## 2. 핵심 가설
(검증 가능한 문장 1~3개. "~하면 ~할 것이다" 꼴. 무엇이 참이어야 이 안이 성립하는가)

## 3. 제안
(무엇을 만들 것인가 한 문단. 이 관점이 아니면 나오지 않았을 선택 1개 이상 포함)

## 4. 핵심 기능 후보 (최대 5, 우선순위 순)
| # | 기능 | 이 관점에서 필요한 이유 | 근거 |
|---|---|---|---|

## 5. 이 관점이 포기한 것 (최소 2개)
(의도적으로 후순위에 둔 것과 그 이유. 심사관이 다른 안과 비교할 때 쓴다)

## 6. 가장 약한 고리
(이 안이 무너진다면 어디서 먼저 무너지는가 — 1개, 이유 포함. 빈칸 금지)

## 7. 근거
(아이디어 원문 인용·섹션, 추정은 '추정' 표기)
```

## 2. 심사표 (judge) — `_work/plan/<stem>.judge.md`

세 안을 같은 잣대로 채점하고 승자 하나를 고른다. 적대적 문서다 — 칭찬·완충 문장 없이 쓴다.

```markdown
---
type: analysis
status: draft
owner: planning-team:judge
inputs: [<idea>, <option-a>, <option-b>, <option-c>]
winner: A | B | C | NONE
round: <회차>
created: YYYY-MM-DD
run: <run_id>
---
# 심사: <stem>

## 1. 채점표 (1~5, 정수)
| 축 | A | B | C | 채점 기준 |
|---|---|---|---|---|
| 가치 | | | | 5=대상 사용자가 바꿀 이유가 명확하고 측정 가능 · 1=왜 쓰는지 설명 못 함 |
| 실현가능성 | | | | 5=현재 자원으로 최소 구현 경로가 보임 · 1=핵심 기능이 미검증 기술/자원에 의존 |
| 차별성 | | | | 5=대체재 대비 각도가 분명 · 1=기존 것과 구분 못 함 |
| 리스크 | | | | 5=치명 리스크 없음 · 1=성립을 막는 리스크 존재 (점수가 높을수록 리스크 낮음) |
| **합계** | | | | 20점 만점 |

## 2. 축별 근거 (12칸 전부)
### 가치
- A <점수>: 근거 `경로#섹션` → 반박(왜 더 못 줬는가)
- B …
- C …
### 실현가능성 / ### 차별성 / ### 리스크 (같은 꼴)

## 3. 승자와 선정 사유 (3줄 이내)

## 4. 승자의 치명 약점
(스펙이 반드시 보완해야 할 것. 승자의 `#6 가장 약한 고리` 와 심사관 자체 발견을 합친다)

## 5. 패자의 살릴 아이디어 (패자별 1개 이상)
| 출처 | 아이디어 | 승자에 어떻게 이식하는가 | 이식 비용 |
|---|---|---|---|
(없으면 '없음' 과 이유)

## 6. 버린 것
(살리지 않은 패자 요소와 이유 — 스펙 작성자가 다시 넣지 못하게)

## 7. NONE 일 때: 재기획 지시
(관점 a/b/c 별로 무엇을 바꿔 다시 써야 하는가. winner 가 NONE 이 아니면 '해당 없음')
```

**승자 규칙**
- 합계 최고. 동점이면 리스크 → 실현가능성 → 가치 순으로 높은 쪽
- 다음 중 하나면 `winner: NONE`: (1) 최고 합계 < 12 (2) 모든 안에 1점 축이 있음 (3) 세 안 모두 아이디어 원문의 문제와 다른 문제를 풀고 있음
- 점수는 정수. 근거 없는 칸은 채점하지 않고 심사를 중단한다 (빈칸 금지 — 근거가 없으면 1점이 아니라 '근거 부족' 으로 표기하고 해당 안을 NONE 후보로 본다)

## 3. 스펙 (spec) — `_work/plan/<stem>.spec.md`

승자 기획안 + 심사표의 '살릴 아이디어' 만으로 쓴다. 새 기능 발명 금지.

```markdown
---
type: spec
status: draft
owner: planning-team:spec-writer
based_on: option-a | option-b | option-c
inputs: [<idea>, <judge>, <승자 option>]
created: YYYY-MM-DD
run: <run_id>
---
# 스펙: <제목> (선정안: <A|B|C>, 미확정)

## 1. 문제 정의
(한 문단 + 성공 지표 1~3개. 지표는 숫자나 관찰 가능한 사건)

## 2. 대상
- 1차 사용자:
- 2차 사용자:
- 명시적 비대상:

## 3. 핵심 기능 (최대 5)
| # | 기능 | 사용자 스토리 (누가·언제·무엇을) | 수용 기준 (검사 가능) | 출처 |
|---|---|---|---|---|
(출처는 `option-x#4` 또는 `judge#5`. 출처 없는 기능은 쓸 수 없다)

## 4. 비기능 요구
(성능·보안·비용·운영·규제·데이터 중 해당하는 것만. 각 항목에 수치나 조건)

## 5. 범위 밖
(명시적으로 하지 않는 것 + 이유. 심사표 `#6 버린 것` 을 빠짐없이 포함)

## 6. 열린 질문
(사람이 결정해야 할 것. 에이전트가 임의로 정하지 않은 항목)

## 7. 근거 추적표
| 스펙 항목 | 근거 |
|---|---|
```

## 4. 실행 계획 (plan) — `_work/<stem>.plan.md`

오케스트레이터가 심사표·스펙을 근거로 직접 쓴다. **G1 게이트 대상.**

```markdown
---
type: plan
status: draft
owner: planning-team
verified_by: []
verify_round: 0
gate: G1-pending
based_on: option-a | option-b | option-c
inputs: [<idea>, <judge>, <spec>]
run: <run_id>
created: YYYY-MM-DD
---
> G1: 이 기획은 originality 검증을 거치지 않았다. 확정안이 아니다.
> 다음 단계: `/verify-team:verify _work/<stem>.plan.md`

# 실행 계획: <제목> (선정안 <A|B|C>, 미확정)

## 0. 한 줄 요약
(무엇을 · 누구에게 · 왜 — 스펙 #1 에서)

## 1. 마일스톤
| M# | 목표 | 산출물 (경로) | 검증 게이트 | 완료 기준 | 의존 |
|---|---|---|---|---|---|
(M0 는 항상 "originality 검증 통과" — G1. 코드 산출물이 있는 마일스톤은 G2 를 건다)

## 2. 산출물 목록
| 산출물 | 경로 | 만드는 팀/에이전트 | 최종 위치 |
|---|---|---|---|
(최종 위치는 `deliverables/` 여도 되지만, 옮기는 건 G3 통과 뒤 오케스트레이터만)

## 3. 검증 게이트
| 게이트 | 대상 | 통과 조건 | 실패 시 |
|---|---|---|---|
| G1 | 이 문서 | verify-team PASS | 반려 사유 반영 후 재검증, 2회 초과 시 사람 |
| G2 | 코드 마일스톤 | 보안·코드리뷰 통과 | … |
| G3 | deliverables/ 이동 | status: approved | … |

## 4. 리스크 대응
| 리스크 | 출처 | 징후 | 대응 | 트리거 |
|---|---|---|---|---|
(출처는 `judge#4` `judge#2` `spec#4`. 심사표 `#4 승자의 치명 약점` 은 반드시 한 행 이상)

## 5. 범위 밖
(스펙 #5 그대로. 줄이거나 늘리지 않는다)

## 6. 다음 액션
1. 사람이 결정할 것 (스펙 #6 열린 질문)
2. 다음 커맨드: `/verify-team:verify _work/<stem>.plan.md`
```

## 5. status 규칙과 게이트

| 파일 | type | status (planning-team 이 쓰는 값) | 이후 |
|---|---|---|---|
| option-a/b/c | proposal | draft | 심사 후 보존만. 갱신하지 않는다 |
| judge | analysis | draft | `winner: NONE` 이면 루프백 트리거 |
| spec | spec | draft | 실행 계획의 근거 |
| plan | plan | draft · `gate: G1-pending` | `/verify-team:verify` → PASS 면 verify-team 이 `approved` + `verified_by` 추가. CONDITIONAL → `in-review`, FAIL → `rejected` (verdict 규격) |

- **루프백**: judge 가 NONE 이면 `_work/plan/<stem>.judge.md` 를 `.judge.r<회차>.md` 로 보존하고, 다음 회차 brainstorm 은 그 파일의 `#7 재기획 지시` 를 추가 입력으로 받는다. 회차는 judge frontmatter `round` 로 추적. `policy.max_rounds`(2) 에 도달한 뒤 또 NONE 이면 사람 에스컬레이션 (세 안·두 심사표 경로와 NONE 사유를 보고)
- **G1**: plan.md 는 originality(verify-team) 통과 전까지 `status: draft`, `gate: G1-pending`. 본문 첫 줄 인용문(위 양식)을 지우지 않는다. 통과 시 오케스트레이터가 `gate: G1-passed` 로 바꾼다
- 기획팀 에이전트는 `deliverables/` `runs/` 에 쓰지 않는다. 스펙·실행 계획을 `deliverables/` 로 옮기는 것은 G3 통과 뒤 오케스트레이터의 일이다
- 재실행 시 같은 경로의 option 파일이 있고 최신이면 `node skip --note "기존 산출물 사용"`. 단 루프백 회차에서는 반드시 다시 쓴다 (이전 안은 `.option-a.r<회차>.md` 로 보존)
