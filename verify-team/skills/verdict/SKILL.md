---
name: verdict
description: 검증 결과 문서(verdict.md)를 작성하거나 산출물의 status frontmatter를 갱신할 때 사용하는 규격. 검증팀 에이전트의 모든 출력과 게이트 통과 처리는 이 규격을 따른다.
---

# verdict 규격

## 1. verdict.md 양식

검증 대상과 같은 폴더에 `<대상파일명>.verdict.md`로 저장한다.

```markdown
---
type: verdict
status: approved
owner: verify-team
verified_by: []
target: <검증 대상 파일 경로>
verdict: PASS | CONDITIONAL | FAIL
round: <회차>
run: <run_id>
created: YYYY-MM-DD
---

# 판정: PASS | CONDITIONAL | FAIL

## 근거
(판정의 핵심 근거를 3줄 이내로)

## 발견 사항
| 심각도 | 각도 | 내용 | 근거/링크 |
|---|---|---|---|

## 반려 사유 (FAIL/CONDITIONAL일 때만)
1. (수정해야 통과되는 항목을 번호로)

## 재검토 조건
(무엇이 바뀌면 재검토 대상인지)
```

## 2. 대상 파일 status 갱신 규칙

- PASS → 대상 frontmatter를 `status: approved`로 바꾸고 `verified_by`에 검증자 추가
- CONDITIONAL → `status: in-review`, `verify_round` +1, 반려 사유를 **frontmatter 종료(---) 바로 아래**에 인용
- FAIL → `status: rejected`, `verify_round` +1
- `verify_round` 는 대상 frontmatter 에 정수로 둔다(없으면 0에서 시작). 세션이 바뀌어도 이 값이 회차의 진실이다
- 재검증 때 이전 verdict 는 덮어쓰지 않고 `<대상파일명>.verdict.r<회차>.md` 로 보존한 뒤 새 verdict 를 쓴다
- verdict 문서 자체의 `status` 는 항상 `approved` (문서의 완결 상태이지 판정이 아니다). verdict 는 `_work/` 에 둔다

## 3. 판정 원칙

- CRITICAL 발견 1개 이상 = FAIL
- 근거 없는 판정 금지. 모든 발견 사항에는 근거나 링크를 붙인다
- approved가 아닌 파일은 deliverables/ 폴더로 옮기지 않는다 (게이트 규칙 G3)
