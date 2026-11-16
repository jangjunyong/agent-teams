---
name: course-note
description: 수업팀(class-team) study 그래프 산출물 4종 — 개념 노트(notes)·문제지(quiz)·검사표(examine)·최종 수업 노트(course-note) — 의 양식과 status 규칙, 그리고 최종 노트를 vault courses/<과목>/ 에 적재할 때의 변환 규칙. class-team/study 그래프의 모든 노드 출력과 오케스트레이터의 수업 노트 작성은 이 규격을 따른다.
---

# course-note 규격

수업팀의 원칙은 하나다. **원문 위치를 댈 수 없는 문장은 노트에 들어오지 못한다.** 노트·문제·검사표·최종 노트 전부 이 원칙 위에서 쓴다.

## 0. 공통 규칙

- frontmatter 필수 3 + 권장: `type` `status` `owner` 는 없으면 `node done` 이 실패한다. `course`(과목) `inputs`(읽은 파일) `created`(YYYY-MM-DD) `run`(run_id) 을 함께 쓴다
- **status 는 class-team 의 모든 산출물에서 `draft` 다** (`draft | in-review | approved | rejected` 네 값 외 금지). 최종 수업 노트만 examine PASS 일 때 `in-review`. `approved` 는 verify-team 판정 뒤 오케스트레이터가 쓴다
- **원문 위치 표기**: 자료 형식에 맞춰 `p.12`(pdf 페이지) · `§3.2`(md 헤딩) · `slide 7` · `L120-134`(txt 줄 번호). 한 문장에 위치 하나 이상. 원문 인용은 따옴표로 한 문장 이내
- **추정 표기**: 원문에 없는 내용은 `[추정]` 을 앞에 붙인다. 표기 없는 원문 밖 내용은 검사에서 MAJOR 다
- 파일 위치: 중간 산출물은 `_work/class/`, 최종 노트만 `_work/<stem>.course-note.md`. `deliverables/` 와 vault 에는 에이전트가 쓰지 않는다
- 길이: 개념 노트 ≤ 4,000자 · 문제지 제한 없음(10문제 전부) · 검사표 제한 없음(개념 목록 전부 대조) · 최종 노트 ≤ 5,000자

## 1. 개념 노트 (notes) — `_work/class/{stem}.notes.md`

```markdown
---
type: report
status: draft
owner: class-team:notetaker
course: <과목>
source_file: <강의자료 경로>
concepts_count: <개념 수>
inputs: [<강의자료 경로>]
created: YYYY-MM-DD
run: <run_id>
---
# 개념 노트: <과목> — <자료 제목> (<stem>)

## 1. 자료 구조
(목차·헤딩·슬라이드 범위 한눈에. 어떤 표기로 위치를 적는지 — p./§/slide/L — 여기서 선언)

## 2. 핵심 개념
### 2.1 <개념명> (위치)
- 정의: … (위치)
- 왜 중요한가: … (위치) | 원문에 이유 없음 [+ [추정] 한 줄]
- 예시: … (위치) | 원문에 예시 없음
- 흔한 오해: … (위치) | 원문에 없음
### 2.2 … (개념 수만큼)

## 3. 개념 사이 관계
(선행 → 후행, 포함, 대비. 각 관계에 위치)

## 4. 원문에서 강조된 것
(자료가 "중요", "시험", "반드시" 로 표시한 것. 위치)

## 5. 용어만 나온 것
(개념으로 승격하지 않은 용어 — 이름과 위치만)

## 6. 근거 목록
(개념별로 참조한 위치 모음. 추정으로 채운 칸 목록)
```

## 2. 문제지 (quiz) — `_work/class/{stem}.quiz.md`

유형·개수·순서 고정: **객관식 5(Q1~Q5) · 단답 3(Q6~Q8) · 서술 2(Q9~Q10)**.

```markdown
---
type: report
status: draft
owner: class-team:quiz-maker
course: <과목>
source_file: <강의자료 경로>
questions: 10
inputs: [<강의자료 경로>]
created: YYYY-MM-DD
run: <run_id>
---
# 문제지: <과목> — <자료 제목> (<stem>)

## 1. 출제 분포
| 유형 | 번호 | 난이도(하/중/상) | 출제 지점(위치) | 묻는 개념 |
|---|---|---|---|---|

## 2. 문제
### Q1 [객관식 · 난이도]
문제 본문
① … ② … ③ … ④ …
- 정답: ②
- 해설: (정답 이유 한 줄 + 오답 보기마다 한 줄)
- 근거 위치: p.12
- 개념: <개념명>
### Q2 … Q5 (객관식)
### Q6 [단답 · 난이도] … Q8
- 정답 / 해설 / 근거 위치 / 개념
### Q9 [서술 · 난이도] … Q10
- 채점 기준: 핵심어 (3개 이내) · 반드시 들어갈 논지 1개
- 모범 답안 요지 / 근거 위치 / 개념

## 3. 출제하지 않은 것
(정답이 원문 두 곳에서 충돌하거나 원문만으로 확정 불가라 뺀 지점 — 위치와 이유)
```

## 3. 검사표 (examine) — `_work/class/{stem}.examine.md`

적대적 문서다. 검사관이 원문에서 직접 만든 핵심 개념 목록이 잣대다.

```markdown
---
type: analysis
status: draft
owner: class-team:examiner
course: <과목>
examine_verdict: PASS | REVISE | FAIL
notes_verdict: PASS | REVISE | FAIL
quiz_verdict: PASS | REVISE | FAIL
notes_score: <0~100>
quiz_score: <0~100>
round: <회차>
inputs: [<강의자료>, <notes>, <quiz>]
created: YYYY-MM-DD
run: <run_id>
---
# 검사: <stem> (회차 N)

## 1. 검사관의 핵심 개념 목록 (원문에서 직접 작성)
| # | 개념 | 위치 | 노트에 있음? | 문제로 다룸? |
|---|---|---|---|---|
(목록 전부. '없음' 이 누락 후보)

## 2. 노트 발견 사항
| # | 심각도(CRITICAL/MAJOR/MINOR) | 노트 위치 | 지적 | 원문 위치 | 원문에는 이렇게 |
|---|---|---|---|---|---|

## 3. 문제지 발견 사항 (10문제 전부 확인)
| Q | 정답 재확인(일치/불일치) | 심각도 | 지적 | 원문 위치 |
|---|---|---|---|---|
(문제 없는 행도 '일치 · —' 로 남긴다 — 전수 확인의 증거)

## 4. 노트 ↔ 문제지 교차
(같은 개념을 다르게 설명한 곳. 원문 기준 누가 맞는가)

## 5. 점수와 판정
- 노트: CRITICAL n · MAJOR n · MINOR n → <점수> → <판정>
- 문제지: CRITICAL n · MAJOR n · MINOR n → <점수> → <판정>
- examine_verdict: <둘 중 나쁜 쪽> — 판정 근거 3줄 이내

## 6. 수정 요구 (REVISE/FAIL 일 때. 작성자가 이것만 보고 고칠 수 있게)
| # | 대상(notes|quiz) | 항목 | 바꿀 것 | 원문 위치 |
|---|---|---|---|---|
(PASS 면 '해당 없음')

## 7. 회차 반영 확인 (재검사 회차만)
(이전 검사표의 수정 요구 각각이 반영됐는가. 첫 회차면 '해당 없음')
```

**심각도·판정 규칙** (examiner 에이전트 정의와 동일)
- CRITICAL: 원문과 반대되는 정의 · 원문에 없는 개념을 원문처럼 씀 · 댄 위치에 그 내용이 없음 · 틀린 정답 · 복수 정답 · 원문으로 풀 수 없는 문제
- MAJOR: 핵심 개념 누락 · `[추정]` 없는 원문 밖 내용 · 원문과 다른 서술 · 틀린 해설 · 근거 위치 오류 · 유형 배분 위반 · 서술 채점 기준 없음
- MINOR: 위치 표기 누락(내용 맞음) · `[추정]` 표기가 있는 원문 밖 내용 · 약한 예시 · 부정확한 표현 · 난이도 누락 · 출제 지점 편중(앞 1/3 에 6개 이상)
- 점수 = 100 − (CRITICAL×20 + MAJOR×10 + MINOR×3), 하한 0. 참고값
- 판정: CRITICAL ≥ 1 → FAIL / MAJOR ≥ 2 → REVISE / 그 외 PASS. `examine_verdict` 는 노트·문제지 중 나쁜 쪽

## 4. 최종 수업 노트 (course-note) — `_work/{stem}.course-note.md`

오케스트레이터가 notes·quiz·examine 세 파일만 근거로 직접 쓴다. **vault `courses/<과목>/` 규격 호환** — handoff 필수 3필드와 vault 필드를 함께 둔다. vault 의 `status` 값(seed|growing|evergreen)과 handoff 의 `status` 값이 충돌하므로 vault 쪽은 `vault_status` 로 들고 다니다 적재 때 바꾼다(5절).

```markdown
---
type: report
status: draft | in-review        # examine PASS 면 in-review, 아니면 draft
owner: class-team
verified_by: []
verify_round: 0
title: <과목> — <자료 제목>
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [course/<과목>]
source: <과목> 강의자료 <강의자료 경로>
vault_status: seed
course: <과목>
examine: PASS | REVISE | FAIL
round: <회차>
run: <run_id>
inputs: [<강의자료>, <notes>, <quiz>, <examine>]
---
> 이 노트는 class-team/study 가 만든 초안이다. examine: <판정>. vault 적재는 5절 규칙대로 사람 확인 뒤.

# <과목> — <자료 제목>

## 1. 한눈에 (3줄)
(이 자료가 다루는 것 · 가장 중요한 개념 · 다음 자료와의 연결 — 각 줄에 위치)

## 2. 핵심 개념
(notes #2 중 examine 에서 CRITICAL/MAJOR 지적이 **없는** 개념만. 지적이 있었고 수정 요구가 반영되지 않은 개념은 #5 로. 개념마다 정의·왜 중요·예시·흔한 오해·위치 — notes 의 네 칸을 그대로 옮기되 요약·윤색하지 않는다)

## 3. 개념 관계
(notes #3)

## 4. 확인 문제
(quiz 중 examine #3 에서 '일치' 이고 CRITICAL/MAJOR 없는 문제만. 번호·유형·문제 본문·근거 위치. 정답·해설은 말미 "정답" 절에 모아 둔다)

## 5. 검사에서 걸린 것 · 아직 모르는 것
(examine 의 미해결 지적 — 제외한 개념·문제와 이유. 원문에 이유/예시가 없던 칸. 빈 섹션 금지 — 없으면 '없음' 과 examine 점수)

## 6. 관련 노트
([[백링크]] 후보 — vault 의 기존 노트 제목. 오케스트레이터가 vault 를 열 수 없는 세션이면 '적재 시 검색' 으로 표기)

## 정답
(Q번호: 정답 · 해설 한 줄 · 위치)
```

## 5. status 규칙 · 루프백 · vault 적재

| 파일 | type | status | 이후 |
|---|---|---|---|
| notes | report | draft | 검사 후 보존. 루프백 회차에는 다시 쓴다 |
| quiz | report | draft | 검사 후 보존. 루프백 회차에는 다시 쓴다 |
| examine | analysis | draft | `examine_verdict` 가 REVISE/FAIL 이면 루프백 트리거 |
| course-note | report | draft · PASS 면 `in-review` | `/verify-team:verify _work/<stem>.course-note.md` → PASS 면 `approved` |

- **루프백**: examine 이 REVISE/FAIL 이면 이전 검사표를 `_work/class/<stem>.examine.r<회차>.md` 로 보존하고, 다음 회차에 `notes_verdict` 가 PASS 가 아닌 쪽(notes/quiz, 둘 다일 수 있음)만 다시 쓴다(이전 파일은 `.notes.r<회차>.md` / `.quiz.r<회차>.md` 로 보존). 재작성 노드는 `#6 수정 요구` 를 추가 입력으로 받는다. PASS 인 쪽은 `node skip --note "기존 산출물 사용"`. 회차는 examine 의 `round` 로 추적. `policy.max_rounds`(2) 에 도달한 뒤 또 REVISE/FAIL 이면 최종 노트는 `status: draft` 로 쓰고 사람에게 에스컬레이션 (두 검사표 경로 + 미해결 지적)
- **vault 적재 규칙** (`<vault>\courses\<과목>\`):
  1. 적재는 **사람이 확인한 뒤 오케스트레이터만** 한다. 에이전트는 vault 에 쓰지 않는다. `examine: FAIL` 인 노트는 적재하지 않는다
  2. 적재 전 vault 전체에서 같은 자료·같은 주제의 기존 노트를 검색한다. 있으면 새로 만들지 않고 기존 노트를 갱신한다(`updated` 갱신, 내용 보강)
  3. 변환: handoff 전용 필드(`type` `owner` `verified_by` `verify_round` `course` `examine` `round` `run` `inputs`)와 본문 첫 줄 인용문을 제거하고, `vault_status` 를 `status` 로 바꾼다(첫 적재는 `seed`). 남는 frontmatter = `title / created / updated / tags / source / status` — vault CLAUDE.md 규격 그대로
  4. `#6 관련 노트` 의 `[[백링크]]` 를 최소 1개 실제 존재하는 노트로 건다. 없으면 과목 MOC(예: `[[<과목>]]`)로
  5. 파일명은 `<자료 제목 또는 stem>.md`. 과목 폴더가 없으면 생성 여부를 사람에게 먼저 묻는다
  6. "#정답" 절은 vault 노트에서 접기(`> [!answer]-`) 또는 말미 유지 — 지우지 않는다
