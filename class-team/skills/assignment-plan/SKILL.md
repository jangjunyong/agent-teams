---
name: assignment-plan
description: 수업팀(class-team) assignment 그래프 산출물 4종 — 요구사항 표(req)·해결 초안(draft)·채점표(grade)·제출 전 계획(assignment-plan) — 의 양식과 status 규칙. class-team/assignment 그래프의 모든 노드 출력과 오케스트레이터의 제출 전 체크리스트·수정 계획 작성은 이 규격을 따른다.
---

# assignment-plan 규격

과제 파이프라인의 원칙은 하나다. **과제 설명의 요구사항 한 줄 = 초안의 한 항목 = 채점표의 한 행.** 셋 중 하나라도 대응이 끊기면 누락이다.

## 0. 공통 규칙

- frontmatter 필수 3 + 권장: `type` `status` `owner` 는 없으면 `node done` 이 실패한다. `course` `assignment`(과제명) `inputs` `created` `run` 을 함께 쓴다
- **status 는 class-team 의 모든 산출물에서 `draft` 다** (`draft | in-review | approved | rejected` 외 금지). 제출 전 계획만 grade PASS 일 때 `in-review`. `approved` 는 verify-team 판정 뒤 오케스트레이터가 쓴다
- **근거 표기**: 과제 설명 원문은 위치(`§`, 줄 번호, 불릿 번호)로, 파이프라인 파일은 `req#R3` `draft#2.1` `grade#4` 처럼 `파일#항목` 으로. 추정은 `[추정]`
- 요구사항 ID 는 `R1, R2, …` 로 고정하고 draft·grade·plan 전부 같은 ID 를 쓴다. 재작성 회차에도 ID 를 바꾸지 않는다(삭제는 '삭제' 표시)
- 파일 위치: 중간 산출물은 `_work/class/`, 제출 전 계획만 `_work/<stem>.assignment-plan.md`. `deliverables/` 에는 쓰지 않는다
- 이 파이프라인은 **제출물을 대신 만들지 않는다.** 과제 설명이 AI 사용을 금지·제한하면 그 규정을 req·draft·plan 모두의 맨 앞에 옮겨 적고, 초안은 구조·계획 수준에 머문다
- 길이: req ≤ 2,500자 · draft ≤ 5,000자 · grade 제한 없음(요구사항 전부 대조) · plan ≤ 3,000자

## 1. 요구사항 표 (req) — `_work/class/{stem}.req.md`

```markdown
---
type: analysis
status: draft
owner: class-team:assignment-coach
course: <과목>
assignment: <과제명>
due: <YYYY-MM-DD HH:MM 또는 '원문에 없음'>
requirements_count: <R 개수>
inputs: [<과제 설명 경로>]
created: YYYY-MM-DD
run: <run_id>
---
# 요구사항: <과목> — <과제명> (<stem>)

## 0. AI·협업 규정 (원문 인용, 위치. 없으면 '원문에 없음')

## 1. 제출물
| ID | 무엇을 | 형식·이름·위치 | 완료 기준(검사 가능) | 원문 위치 |
|---|---|---|---|---|

## 2. 제약
| ID | 제약 | 완료 기준 | 원문 위치 |
|---|---|---|---|
(언어·도구·분량·금지 사항)

## 3. 채점 기준
| ID | 항목 | 배점 | 근거(원문 위치 또는 [추정]+이유) |
|---|---|---|---|
(원문에 배점이 없으면 100점 추정 배분, 전부 [추정])

## 4. 마감·제출 경로
(날짜·시각·시간대·지각 규정·제출처. 원문 위치)

## 5. 질문할 것
(두 가지로 읽히는 문장 — 원문 인용 + 두 해석. 임의로 고르지 않는다)

## 6. 암묵 요구 ([추정] 3개 이하)
| ID | 요구 | 왜 채점자가 볼 것으로 보는가 |
|---|---|---|
```

## 2. 해결 초안 (draft) — `_work/class/{stem}.draft.md`

```markdown
---
type: design
status: draft
owner: class-team:assignment-coach
course: <과목>
assignment: <과제명>
kind: code | writing | mixed
round: <회차>
inputs: [<과제 설명>, <req>]
created: YYYY-MM-DD
run: <run_id>
---
# 초안: <과목> — <과제명> (<stem>, 회차 N)

## 0. AI·협업 규정 (req#0 그대로)

## 1. 접근 한 줄
(무엇을 어떤 순서로. 요구사항 ID 전부가 아래 어디선가 다뤄진다)

## 2. 초안
### code 과제
#### 2.1 설계 — 모듈·입출력·데이터 구조·핵심 알고리즘 (항목마다 대응 R-ID, 출처)
#### 2.2 테스트 계획 — | R-ID | 테스트 | 입력 | 기대 | 경계/실패 케이스 |
#### 2.3 핵심 코드 조각 (핵심 로직만, 출처 표기)
### writing 과제
#### 2.1 개요 — 섹션별 핵심 주장 한 줄 (대응 R-ID)
#### 2.2 근거 계획 — | 주장 | 필요한 근거 | 가진 것 / 찾을 것 | 출처 |
### mixed 면 둘 다

## 3. 대응표
| R-ID | 초안 위치(draft#…) | 상태(계획됨/초안 있음/미정) |
|---|---|---|
(req 의 모든 R-ID 가 행으로 있어야 한다)

## 4. 마감 역산
| 항목 | 예상 소요 | 막힐 지점 | 시작 기한 |
|---|---|---|---|

## 5. 표절·출처 위험 자가 점검
(가져오는 곳과 출처 쓸 자리, 규정에 걸릴 지점)

## 6. 회차 반영 (재작성 회차만)
(grade#6 수정 요구 각각 → 어떻게 반영. 첫 회차면 '해당 없음')

## 7. 범위 밖
(추가 점수용·하고 싶지만 요구 아닌 것)
```

## 3. 채점표 (grade) — `_work/class/{stem}.grade.md`

적대적 문서다. 검사관이 원문에서 직접 만든 요구사항 목록이 잣대다.

```markdown
---
type: analysis
status: draft
owner: class-team:examiner
course: <과목>
assignment: <과제명>
grade_verdict: PASS | REVISE | FAIL
expected_score: <예상 점수>
max_score: <만점 (원문 배점 또는 100 [추정])>
round: <회차>
inputs: [<과제 설명>, <req>, <draft>]
created: YYYY-MM-DD
run: <run_id>
---
# 채점: <stem> (회차 N)

## 1. 검사관의 요구사항 목록 (원문에서 직접 작성)
| # | 요구 | 원문 위치 | req 에 있음?(R-ID/없음) | draft 에 있음?(draft#/없음) |
|---|---|---|---|---|

## 2. 요구사항 분해 지적 (req 의 누락·오해)
| # | 심각도 | 지적 | 원문 위치 |
|---|---|---|---|

## 3. 축별 감점
| 축 | 감점 사유 | 근거(req#/draft#/원문 위치) | 감점 |
|---|---|---|---|
| 요구사항 충족 | | | |
| 근거·논리 | | | |
| 표절·출처 위험 | | | |
| 형식·제출 규정 | | | |

## 4. 예상 점수
(만점 − 감점 합계 = expected_score. 만점이 추정이면 [추정])

## 5. 판정
- grade_verdict: <PASS|REVISE|FAIL> — 판정 근거 3줄 이내 (규칙: 필수 제출물 누락 또는 표절 위험 ≥1 → FAIL / 요구사항 누락 ≥2 또는 근거 부실 MAJOR ≥2 → REVISE / 그 외 PASS)

## 6. 수정 요구 (REVISE/FAIL 일 때)
| # | 대상(req|draft) | 항목(R-ID/draft#) | 바꿀 것 | 원문 위치 |
|---|---|---|---|---|

## 7. 회차 반영 확인 (재검사 회차만)
```

## 4. 제출 전 계획 (assignment-plan) — `_work/<stem>.assignment-plan.md`

오케스트레이터가 req·draft·grade 세 파일만 근거로 직접 쓴다.

```markdown
---
type: plan
status: draft | in-review        # grade PASS 면 in-review, 아니면 draft
owner: class-team
verified_by: []
verify_round: 0
course: <과목>
assignment: <과제명>
due: <req 의 due>
grade: PASS | REVISE | FAIL
expected_score: <grade 의 expected_score>/<max_score>
round: <회차>
run: <run_id>
inputs: [<과제 설명>, <req>, <draft>, <grade>]
created: YYYY-MM-DD
---
> 이 계획은 class-team/assignment 가 만든 초안이다. grade: <판정>, 예상 <점수>. 제출물 자체가 아니다.

# 과제 계획: <과목> — <과제명>

## 0. 한 줄 요약
(무엇을 · 언제까지 · 어떤 형태로 · 어디에 제출. req#1·#4 에서)

## 0-1. AI·협업 규정 (req#0 그대로)

## 1. 요구사항 ↔ 초안 ↔ 채점 대응표
| R-ID | 요구 | 초안 위치 | grade 지적 | 상태(완료/수정 필요/미착수) |
|---|---|---|---|---|
(req 의 모든 R-ID + grade#1 에서 req 에 없다고 지적된 요구)

## 2. 수정 계획
| 순위 | 대상 | 무엇을 고치나 (grade#6) | 완료 기준 | 예상 소요 | 기한 |
|---|---|---|---|---|---|
(grade 수정 요구 전부. PASS 면 draft#4 막힐 지점만)

## 3. 제출 전 체크리스트
- [ ] 제출물 (req#1 행마다 한 줄)
- [ ] 형식·이름·위치
- [ ] 제약 (req#2 행마다)
- [ ] 출처·인용 표기 (draft#5 · grade#3 표절 축)
- [ ] AI·협업 규정 준수
- [ ] 마감 <due> 이전 제출 확인

## 4. 리스크
| 리스크 | 출처(grade#/draft#) | 징후 | 대응 |
|---|---|---|---|
(grade#3 표절·출처 위험 축과 근거 부실은 반드시 한 행 이상)

## 5. 사람이 결정할 것
(req#5 질문할 것 · 모호한 채점 기준 · 범위 밖 항목 채택 여부)

## 6. 다음 액션
1. 수정 계획 1순위부터
2. 다음 커맨드: `/verify-team:verify _work/<stem>.assignment-plan.md` (선택)
```

## 5. status 규칙 · 루프백

| 파일 | type | status | 이후 |
|---|---|---|---|
| req | analysis | draft | 검토 후 보존. grade 가 req 누락을 지적하면 루프백 회차에 갱신 |
| draft | design | draft | `grade_verdict` REVISE/FAIL 이면 루프백 회차에 다시 쓴다 |
| grade | analysis | draft | REVISE/FAIL → 루프백 트리거 |
| assignment-plan | plan | draft · PASS 면 `in-review` | verify-team 검증은 선택. `approved` 는 오케스트레이터만 |

- **루프백**: grade 가 REVISE/FAIL 이면 이전 채점표를 `_work/class/<stem>.grade.r<회차>.md`, 이전 초안을 `.draft.r<회차>.md` 로 보존하고 다음 회차에 draft 를 grade `#6 수정 요구` 를 추가 입력으로 다시 쓴다. grade `#2` 에 req 지적이 있으면 decompose 도 다시 쓴다(없으면 `node skip --note "기존 산출물 사용"`). 회차는 grade 의 `round` 로 추적. `policy.max_rounds`(2) 에 도달한 뒤 또 REVISE/FAIL 이면 계획은 `status: draft` 로 쓰고 사람에게 에스컬레이션 (두 채점표 경로 + 미해결 수정 요구)
- 수업팀 에이전트는 `deliverables/` `runs/` vault 에 쓰지 않는다
