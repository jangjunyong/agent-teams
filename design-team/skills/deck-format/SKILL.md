---
name: deck-format
description: 디자인팀(design-team) deck 그래프 산출물 4종 — 스토리라인(storyline)·슬라이드 본문(slides)·검토표(review)·최종 덱(deck) — 의 양식과 status 규칙. 최종 덱은 그대로 pptx 로 옮길 수 있는 구조다. design-team/deck 그래프의 모든 노드 출력과 오케스트레이터의 덱 작성은 이 규격을 따른다. 발표자료 산출물을 쓰거나 읽어 판단할 때 사용한다.
---

# deck-format 규격

디자인팀의 deck 그래프는 **스토리라인 → 슬라이드 본문 → 검토표 → 최종 덱** 순으로 흐른다. 원칙은 하나다. **슬라이드 한 장 = 주장 한 문장(헤드라인) = 근거 위치 한 곳.** 내용 md 에 없는 숫자·사실은 덱에 들어올 수 없다.

## 0. 공통 규칙

- frontmatter 필수 3 + 권장: `type` `status` `owner` 는 없으면 `node done` 이 실패한다. `inputs` `created` `run` 을 함께 쓴다
- **status 는 `draft | in-review | approved | rejected` 네 값뿐이다.** 스토리라인·슬라이드·검토표는 항상 `draft`. 최종 덱은 검토 PASS 면 `in-review`, 아니면 `draft`. 디자인팀은 `approved` 를 쓰지 않는다
- **헤드라인은 문장이다.** "시장 현황" 같은 명사구는 헤드라인이 아니다. "국내 시장은 3년간 2배로 커졌다" 처럼 주어+서술어가 있는 한 문장, 40자 이내
- **숫자·고유명사·인용은 전부 `경로#섹션` 근거.** 내용 md 에 없는 숫자는 쓰지 않는다. 꼭 필요하면 `[원문에 없음 — 확인 필요]` 를 붙이고 검토에서 지적 대상이 된다
- 슬라이드 수 10~15장 (표지·마무리 포함). 장당 본문 불릿 3개 이내, 불릿 한 줄 40자 이내
- 시각 요소 지시는 "차트" 가 아니라 **종류·축/항목·데이터 출처·강조점** 4가지를 적는다 (예: `막대 — x: 연도 2023~2025, y: 매출(억원), 출처 brief.md#3, 강조: 2025 막대`)
- 파일 위치: 중간 산출물은 `_work/deck/`, 최종 덱만 `_work/<stem>.deck.md`. `deliverables/` 에는 쓰지 않는다
- 길이: 스토리라인 ≤ 1,500자 · 슬라이드 본문 제한 없음(장당 양식 전부) · 검토표 제한 없음 · 덱 제한 없음

## 1. 스토리라인 (storyline) — `_work/deck/<stem>.storyline.md`

판단형 산출물. 무엇을 말하고 무엇을 빼는지를 정한다. 슬라이드 본문은 아직 쓰지 않는다.

```markdown
---
type: design
status: draft
owner: design-team:deck-writer
stage: storyline
audience: <한 줄>
purpose: <발표 후 청중이 할 행동 한 문장>
slide_count: <10~15>
inputs: [<내용 md 경로>]
created: YYYY-MM-DD
run: <run_id>
---
# 스토리라인: <발표 제목>

## 1. 청중
(누구인가 · 이미 아는 것 · 모르는 것 · 의심할 것. 내용 md 어디서 끌어냈는지 `경로#섹션`. 원문에 없으면 `[원문에 없음 — 가정]`)

## 2. 목적
(발표가 끝난 뒤 청중이 해야 할 행동 한 문장. "이해시킨다" 는 목적이 아니다)

## 3. 핵심 메시지 (정확히 3개)
| M# | 메시지 (한 문장) | 근거 `경로#섹션` | 청중의 예상 반론 |
|---|---|---|---|

## 4. 슬라이드 흐름 (10~15장)
| # | 헤드라인 (한 문장, 40자 이내) | 역할 | 메시지 | 근거 `경로#섹션` |
|---|---|---|---|---|
(역할: 표지·문제·근거·제안·비교·계획·리스크·요청·마무리 중. 메시지: M1/M2/M3 또는 '-'(표지·마무리). 근거 없는 장은 쓸 수 없다)

## 5. 뺀 것
(내용 md 에 있지만 이 청중·목적에 넣지 않은 것 2개 이상 + 이유)

## 6. 근거 공백
(말하고 싶은데 내용 md 에 근거가 없는 것. 슬라이드에 넣지 말고 여기 둔다. 없으면 '없음')

## 7. 근거
(원문 인용 `경로#섹션`, 가정은 `[원문에 없음 — 가정]`)
```

## 2. 슬라이드 본문 (slides) — `_work/deck/<stem>.slides.md`

제작형 산출물. 스토리라인 4절 흐름표의 장 번호·헤드라인을 **그대로** 쓴다. 장을 늘리거나 순서를 바꾸려면 바꾸지 말고 `## 변경 제안` 에 적는다.

```markdown
---
type: design
status: draft
owner: design-team:deck-writer
stage: slides
slide_count: <n>
inputs: [<내용 md>, <storyline>]
created: YYYY-MM-DD
run: <run_id>
---
# 슬라이드 본문: <발표 제목>

## S1. <헤드라인 — 스토리라인 #4 와 동일>
- 역할: 표지 | 문제 | 근거 | 제안 | 비교 | 계획 | 리스크 | 요청 | 마무리
- 메시지: M1 | M2 | M3 | -
- 본문:
  - <불릿 1, 40자 이내>
  - <불릿 2>
  - <불릿 3>
- 시각: <종류 — 축/항목, 출처 경로#섹션, 강조점> (없으면 '없음 — 텍스트만' 과 이유)
- 노트: <발표자가 말할 것 3~5문장. 본문 불릿을 읽지 않고 덧붙일 맥락·전환 문장>
- 근거: <경로#섹션> (숫자가 있으면 숫자마다)

## S2. …
(장마다 같은 꼴. 표지·마무리는 본문 불릿 0~1개 허용)

## 변경 제안
(스토리라인 흐름을 바꾸고 싶은 곳 — 장 번호·이유. 없으면 '없음'. 본문에서 임의로 바꾸지 않는다)
```

## 3. 검토표 (review) — `_work/deck/<stem>.review.md`

적대적 문서. 덱이 청중 앞에서 무너지는 지점을 찾는다. 칭찬·완충 문장 없이 쓴다.

```markdown
---
type: analysis
status: draft
owner: design-team:design-critic
inputs: [<내용 md>, <storyline>, <slides>]
review_verdict: PASS | REVISE | FAIL
revise_target: storyline | slides | none
round: <회차>
created: YYYY-MM-DD
run: <run_id>
---
# 검토: <stem>

## 1. 체크리스트 (장별 위반 수)
| 항목 | 위반 장 수 | 기준 |
|---|---|---|
| 논리 비약 | | 앞 장의 주장이 다음 장의 전제가 되지 않는 곳, 근거 없이 결론으로 점프하는 곳 |
| 근거 없는 숫자 | | 내용 md 에 없는 숫자·비율·고유명사 (장 번호와 숫자 나열) |
| 장당 메시지 1개 위반 | | 헤드라인이 두 주장을 담거나, 본문 불릿이 헤드라인과 다른 말을 하는 장 |
| 헤드라인 문장성 | | 명사구 헤드라인, 40자 초과 |
| 시각 지시 불명확 | | 종류·축/항목·출처·강조점 4요소 중 빠진 것이 있는 장 |
| 청중 적합 | | 청중(스토리라인 #1)이 모르는 용어를 설명 없이 쓴 장, 청중이 이미 아는 것을 길게 설명한 장 |
| 분량 | | 장수 10~15 밖, 불릿 4개 이상, 불릿 40자 초과 |

## 2. 장별 지적
| S# | 항목 | 근거(인용 또는 위치) | 수정 요구 |
|---|---|---|---|
(위반이 있는 장 전부. 없는 장은 쓰지 않는다)

## 3. 숫자 검증표
| S# | 숫자/고유명사 | 내용 md 위치 `경로#섹션` | 결과(일치·불일치·없음) |
|---|---|---|---|
(슬라이드의 숫자 전부. 하나도 빠뜨리지 않는다)

## 4. 판정 근거 (3줄 이내)

## 5. 수정 요구 목록
| # | 대상(S# 또는 storyline#섹션) | 무엇을 어떻게 | 근거 |
|---|---|---|---|
(REVISE/FAIL 때. 작성자가 이것만 보고 고칠 수 있는 수준. PASS 면 '없음')
```

**판정 규칙** (재량으로 완화하지 않는다)
- 근거 없는 숫자 1건 이상 또는 논리 비약 2장 이상 → **FAIL**
- 그 외 위반 합계 3건 이상, 또는 시각 지시 불명확 3장 이상 → **REVISE**
- 그 외 → **PASS**
- `revise_target`: 위반이 흐름·메시지·청중 정의에서 비롯되면 `storyline`(스토리라인부터 다시), 장 안의 문제면 `slides`. PASS 면 `none`

## 4. 최종 덱 (deck) — `_work/<stem>.deck.md`

오케스트레이터가 슬라이드 본문과 검토표를 근거로 직접 쓴다. **이 파일의 장 블록 하나 = pptx 슬라이드 하나.** 필드 이름·순서를 바꾸지 않는다 (변환 스크립트·사람이 그대로 옮긴다).

```markdown
---
type: design
status: in-review | draft
owner: design-team
verified_by: []
verify_round: 0
review: PASS | REVISE | FAIL
round: <회차>
slide_count: <n>
aspect: 16:9
inputs: [<storyline>, <slides>, <review>]
run: <run_id>
created: YYYY-MM-DD
---
# 덱: <발표 제목>

> 청중: <storyline #1 한 줄> · 목적: <storyline #2> · 핵심 메시지: M1 … / M2 … / M3 …

---

## 1. <헤드라인 한 문장>
- layout: title | section | bullets | two-column | chart | table | quote | closing
- 본문:
  - <불릿>
- 시각: <종류 — 축/항목, 출처, 강조점> | 없음
- 노트: <발표자 노트>
- 근거: <경로#섹션>

---

## 2. …
```

규칙:
- 장 사이는 `---` 한 줄로 구분한다 (pptx 변환 시 슬라이드 경계)
- `layout` 은 위 8값 중 하나. 표지는 `title`, 마무리·요청은 `closing`, 차트 지시가 있으면 `chart`, 표 지시가 있으면 `table`
- 검토표 `#5 수정 요구` 가 반영된 상태여야 한다. 반영되지 않은 요구가 있으면 해당 장 `노트` 끝에 `[미반영: review#5-<번호>]` 를 남긴다 (지우지 않는다)
- 검토표 `#3 숫자 검증표` 에서 '없음' 판정된 숫자는 덱에 들어오지 못한다. 그 장은 숫자 없이 다시 쓰거나 `[원문에 없음 — 확인 필요]` 를 붙인다
- 슬라이드 본문·검토표에 없는 내용을 새로 쓰지 않는다. 요약·윤색으로 근거를 지우지 않는다

## 5. status 규칙과 루프백

| 파일 | type | status (design-team 이 쓰는 값) | 이후 |
|---|---|---|---|
| storyline | design | draft | 슬라이드의 근거. 검토가 `revise_target: storyline` 이면 다시 쓴다 |
| slides | design | draft | 검토 대상 |
| review | analysis | draft | `review_verdict` 가 REVISE/FAIL 이면 루프백 트리거 |
| deck | design | PASS → in-review · 그 외 draft | `/verify-team:verify _work/<stem>.deck.md` → PASS 면 verify-team 이 `approved`. 이후 pptx 변환은 사람 또는 별도 도구 |

- **루프백**: review 가 REVISE/FAIL 이면 `_work/deck/<stem>.review.md` 를 `.review.r<회차>.md` 로 보존하고, `revise_target` 에 따라 storyline 또는 slides 부터 다시 쓴다 (이전 본은 `.slides.r<회차>.md` 등으로 보존). 재작성 노드는 그 검토표의 `#5 수정 요구` 를 추가 입력으로 받는다. 회차는 review frontmatter `round` 로 추적. `policy.max_rounds`(2) 에 도달한 뒤 또 REVISE/FAIL 이면 사람 에스컬레이션 (두 검토표·미반영 요구 목록 보고). 이때도 덱은 쓰되 `status: draft`, `review: <판정>` 으로 남긴다
- 디자인팀 에이전트는 `deliverables/` `runs/` 에 쓰지 않는다
- 재실행 시 같은 경로의 storyline 이 있고 최신이면 `node skip --note "기존 산출물 사용"`. 단 `revise_target: storyline` 루프백에서는 반드시 다시 쓴다
