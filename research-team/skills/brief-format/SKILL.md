---
name: brief-format
description: 조사팀(research-team) 산출물 4종 — 조사 노트(sweep)·종합(synthesis)·사실확인(factcheck)·브리프(brief) — 의 양식과 신뢰도 표기 규칙(1차/2차/추정). 조사팀 에이전트의 모든 출력과 오케스트레이터의 브리프 작성은 이 규격을 따른다. 다른 팀이 조사 결과를 인용할 때도 이 표기를 쓴다.
---

# brief-format 규격

조사팀의 원칙은 하나다. **링크 없는 주장은 주장이 아니라 추정이다.** 아래 4종 문서는 전부 이 원칙 위에서 작성한다.

## 0. 신뢰도 표기 규칙 (모든 문서 공통)

모든 발견·주장 줄은 신뢰도 태그로 시작한다. 태그는 정확히 세 가지뿐이다.

| 태그 | 뜻 | 해당하는 출처 |
|---|---|---|
| `[1차]` | 원출처를 직접 확인했다 | 공식 문서·API 레퍼런스·표준 문서(RFC 등)·논문 원문·공시·법령·정부 통계·소스코드·제작사 공식 발표·당사자 본인 글 |
| `[2차]` | 원출처를 인용·요약한 자료를 확인했다 | 기사·블로그·위키·리뷰·보고서의 요약부·커뮤니티 글(실사용 후기 포함)·벤더 마케팅 자료 |
| `[추정]` | 출처가 없거나, 출처가 있어도 본문을 직접 확인하지 못했다 | 에이전트의 기억·추론, 검색 스니펫만 본 것, 접속 불가 링크, 날짜 미상의 전언 |

표기 형식 (한 줄):

```
- [1차] <주장 한 문장> — 출처: <URL> (게시 YYYY-MM-DD | 접속 YYYY-MM-DD)
```

규칙:
- URL 이 없으면 태그는 자동으로 `[추정]` 이다. 기억으로 쓴 내용은 반드시 `[추정]` 으로 적고 "기억" 이라고 밝힌다
- 게시일을 알 수 없으면 `게시 ?` 로 쓴다. 접속일은 생략하지 않는다
- 스니펫만 보고 본문을 열지 않았으면 `[1차]` 를 붙일 수 없다. `[추정]` + "스니펫만 확인"
- 벤더 마케팅·이해관계자 글은 `[2차]` 뒤에 `(이해관계)` 를 붙인다
- 커뮤니티 단일 후기는 `[2차]` 뒤에 `(n=1)` 을 붙인다. 같은 취지 글이 3건 이상이면 `(n≥3)`
- 인용은 한 주장당 한 문장 이내, 따옴표로. 장문 복붙 금지. 요약은 내 말로 다시 쓴다
- 두 출처가 충돌하면 어느 한쪽을 고르지 않는다. `⚔ 충돌` 로 표시하고 양쪽을 모두 적는다

## 1. 조사 노트 — `_work/research/{slug}.{lens}.md`

렌즈(`lens`)는 `docs` | `academic` | `community` 중 하나. 렌즈마다 파일 하나.

```markdown
---
type: research
status: draft
owner: research-team:web-researcher
lens: docs | academic | community
question: <질문 원문>
inputs: []
searched: ["<검색어1>", "<검색어2>", ...]
sources_count: <URL 개수>
created: YYYY-MM-DD
---

# 조사 노트 ({lens}): <질문>

## 질문 재진술
(이 렌즈에서 답하려는 하위 질문 2~4개)

## 검색어
(한국어·영어 각 3개 이상. 실제로 실행한 것만)

## 발견 사항
- F1. [1차|2차|추정] <주장> — 출처: <URL> (게시 YYYY-MM-DD | 접속 YYYY-MM-DD) · 메모: <문맥·조건·버전>
- F2. ...
(각 항목에 F번호를 붙인다. 종합·사실확인 단계가 이 번호로 참조한다)

## 이 렌즈에서 찾지 못한 것
(찾으려 했으나 못 찾은 것. "없음" 이면 없음과 그 이유)

## 검색 한계
(접속 불가·유료벽·언어·기간 등)
```

완료 기준: 발견 사항 5개 이상 · 모든 발견에 URL 과 날짜 · `[1차]` 는 본문을 실제로 연 것만 · 렌즈 밖 출처(예: docs 렌즈에서 커뮤니티 글) 금지.

## 2. 종합 — `_work/research/{slug}.synthesis.md`

```markdown
---
type: analysis
status: draft
owner: research-team:synthesizer
question: <질문 원문>
inputs: [_work/research/{slug}.docs.md, _work/research/{slug}.academic.md, _work/research/{slug}.community.md]
verify_round: 0
created: YYYY-MM-DD
---

# 종합: <질문>

## 쟁점 목록
(질문을 푸는 데 필요한 쟁점을 3~7개로 쪼갠다. 쟁점마다 아래 블록)

### 쟁점 1. <한 줄>
- 합의: [1차|2차|추정] <세 렌즈가 같은 말을 하는 것> — 근거: docs F2, academic F1
- ⚔ 충돌: <A 는 X 라 하고(docs F5, [1차]) B 는 Y 라 한다(community F3, [2차] n=1)>. 해소하지 않음
- 공백: <이 쟁점에서 어느 렌즈도 답하지 못한 것>

## 주장 목록 (사실확인 대상)
| ID | 주장 | 신뢰도 | 근거 (노트.F번호) | 질문에 대한 중요도 |
|---|---|---|---|---|
| C1 | ... | 1차 | docs F2, academic F1 | 핵심 |
| C2 | ... | 2차 (이해관계) | community F4 | 보조 |

## 미해결·공백
(세 노트를 합쳐도 답이 안 나오는 것)

## 종합자 메모
(세 노트 밖에서 종합자가 보탠 것이 있다면 전부 여기에 `[추정]` 으로. 없으면 "없음")
```

규칙:
- 주장의 신뢰도는 그 주장을 지지하는 근거 중 **가장 높은** 등급을 따른다. 단 `⚔ 충돌` 이 붙은 주장은 등급과 무관하게 충돌로 남긴다
- 주장 ID(C1…)는 사실확인·브리프가 그대로 쓴다. 재작성 회차에서도 번호를 바꾸지 않는다(삭제된 것은 "삭제" 표시)
- 권고·추천·결론 금지. 종합은 지도이지 답이 아니다

## 3. 사실확인 — `_work/research/{slug}.factcheck.md`

```markdown
---
type: analysis
status: draft
owner: research-team:fact-checker
question: <질문 원문>
inputs: [_work/research/{slug}.synthesis.md]
factcheck_verdict: PASS | REVISE | FAIL
checked: <확인한 주장 수>
round: <회차>
created: YYYY-MM-DD
---

# 사실확인: <질문> — 판정 PASS | REVISE | FAIL

## 판정 근거
(3줄 이내. 무엇이 틀렸고 무엇이 근거 없는지)

## 확인 결과
| 주장 ID | 원문 주장 | 결과 | 원출처 확인 URL (접속일) | 메모 |
|---|---|---|---|---|
| C1 | ... | CONFIRMED | https://... (2026-08-20) | 원문 그대로 |
| C3 | ... | PARTIAL | https://... (2026-08-20) | 수치는 맞으나 2024년 기준 |
| C5 | ... | WRONG | https://... (2026-08-20) | 원문은 반대로 말함 |
| C7 | ... | UNSUPPORTED | — | 링크 404, 대체 출처 못 찾음 |

## 반대 증거 탐색
(주장마다 "이걸 뒤집는 출처가 있는가" 를 최소 1회 검색한 결과. 찾았으면 URL, 못 찾았으면 검색어와 함께 "못 찾음")

## 수정 요구 (REVISE/FAIL 일 때만)
1. C5 를 삭제하거나 반전할 것 — 근거 URL
2. ...
```

결과 4값:
- `CONFIRMED` 원출처가 그 주장을 그대로 말한다
- `PARTIAL` 방향은 맞으나 수치·날짜·조건·버전이 다르다
- `WRONG` 원출처가 반대로 말하거나, 출처가 그 주장을 전혀 담고 있지 않다
- `UNSUPPORTED` 원출처에 접근할 수 없고 대체 출처도 없다

판정 규칙(기계적으로 적용):
- 중요도 "핵심" 주장 중 `WRONG` 1개 이상 → **FAIL**
- `UNSUPPORTED` 가 확인 대상의 40% 이상 → **FAIL**
- `PARTIAL` 2개 이상, 또는 보조 주장의 `WRONG` → **REVISE**
- 그 외 → **PASS**

## 4. 브리프 — `_work/{slug}.brief.md` (오케스트레이터만 쓴다)

```markdown
---
type: brief
status: draft | in-review
owner: research-team
verified_by: []
question: <질문 원문>
factcheck: PASS | REVISE | FAIL
round: <회차>
run: <run_id>
inputs: [_work/research/{slug}.synthesis.md, _work/research/{slug}.factcheck.md]
created: YYYY-MM-DD
---

# 브리프: <질문>

## 핵심 답 (3줄)
1. [1차|2차|추정] <한 문장> (C1)
2. [1차|2차|추정] <한 문장> (C2, C4)
3. [1차|2차|추정] <한 문장> (C6)

## 근거
| 주장 | 신뢰도 | 출처 (URL, 게시일) | 사실확인 |
|---|---|---|---|
| C1 ... | 1차 | https://... (2025-11-03) | CONFIRMED |

## 반대 증거·충돌
(⚔ 충돌로 남은 것, 반대 증거 탐색에서 나온 것. 없으면 "없음 — 단 탐색 범위: …")

## 모르는 것 (정보 한계)
(UNSUPPORTED 주장, 공백, 검색 한계. 추정으로 메우지 않는다)

## 다음 질문
(이 브리프로 답이 안 된 것 중 다음에 조사하면 값이 나올 질문 3개 이상)

## 출처 목록
(본문에 쓰인 URL 전부, 신뢰도 태그와 함께)
```

규칙:
- 핵심 답은 **정확히 3줄**. 각 줄은 종합의 주장 ID 를 달고, 그 주장의 사실확인 결과가 `CONFIRMED` 또는 `PARTIAL`(수정 반영) 인 것만 쓸 수 있다
- `WRONG` 주장은 브리프에 들어오지 못한다. `UNSUPPORTED` 는 "모르는 것" 으로만 간다
- 브리프는 종합·사실확인 두 파일에 없는 주장을 새로 만들지 않는다
- `status` 는 factcheck 가 PASS 면 `in-review`(verify-team 검증 대기), REVISE/FAIL 이면 `draft`
- 브리프를 `deliverables/` 로 옮기는 것은 verify-team 판정 PASS 뒤 오케스트레이터만 한다(G3)
