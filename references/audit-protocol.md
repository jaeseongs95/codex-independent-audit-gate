# Audit Protocol

이 문서는 감사 범위를 정하고 fresh auditor에게 briefing을 전달하거나 `PASS`, `FAIL`, `BLOCKED`를 판정할 때 사용한다. 예시 YAML은 대화 안의 논리적 형식이며 파일 생성을 요구하지 않는다.

## 1. 감사 단계와 위험 분류

`phase`는 다음 중 하나다.

- `pre-execution`: 비가역적이거나 외부 영향을 주는 변경 실행 직전
- `post-execution`: 비배포 고위험 작업을 실행한 뒤 결과와 영향을 확인할 때
- `pre-deploy`: 검증된 최종 후보를 병합·배포·공개하기 직전
- `post-deploy`: 실제 배포 또는 공개 릴리스 뒤 상태 확인

다음 표의 신호가 하나라도 중요하면 고위험으로 분류한다.

| 영역 | 필수 감사 신호 |
| --- | --- |
| 보안·권한 | 인증, 인가, 관리자 권한, 비밀값, 암호화, 격리, 외부 노출 |
| 결제·금전 | 과금, 환불, 가격, 청구, 지급, 거래 실행, 회계 기록 |
| 데이터 | 영구 삭제, 대량 수정, 개인정보, 정합성, 백업·복원, 검증되지 않은 복구 |
| 스키마 | 스키마·제약 변경, 데이터 변환, rollback 불명확, 호환성 단절 |
| 배포·운영 | 프로덕션, 공개 릴리스, 인프라, CI/CD, 장애 대응, 가용성 |
| 전역 설정 | 조직·프로젝트 전체 정책, 기본 권한, 공용 런타임·네트워크 |

환경 이름만으로 위험을 낮추지 않는다. staging이나 개발 환경도 실데이터, 민감 데이터, 공유 자원 또는 외부 연동을 건드리면 감사 대상이다. 다음 조건을 모두 충족하는 작업만 저위험 예외로 둘 수 있다.

- 로컬 또는 완전히 격리된 환경이다.
- 합성 데이터만 사용한다.
- 변경을 즉시 재생성하거나 복구할 수 있다.
- 다른 사용자, 서비스, 비용 또는 권한에 영향을 주지 않는다.
- 예외 판단의 근거를 기록했다.

## 2. 감사자 독립성

감사자는 다음 조건을 모두 충족해야 한다.

- 구현·수정·구현자 검증을 수행한 worker가 아니다.
- 이전 구현 대화를 상속하지 않은 fresh context에서 시작한다.
- 다른 에이전트에게 감사를 재위임하지 않는다.
- 요구사항과 원자료를 직접 열람할 수 있다.
- 구현자의 예상 결론과 자기평가를 briefing으로 받지 않는다.

협업 도구가 fresh context나 worker identity를 관찰할 수 없다면 독립성을 충족했다고 주장하지 말고 `BLOCKED`로 판정한다.

## 3. 감사자 briefing

다음 입력을 가능한 범위에서 완결해 전달한다.

```yaml
phase: "pre-execution | post-execution | pre-deploy | post-deploy"
requirements: []
applicable_instructions: []
risk_classification:
  areas: []
  rationale: ""
implementers: []
auditor_constraints:
  fresh_context: true
  delegation_allowed: false
final_target:
  kind: "commit | diff | artifact | deployment | observable-state"
  identifier: ""
  scope: []
evidence_locations:
  changed_files: []
  test_commands: []
  raw_results: []
  logs: []
rollback:
  procedure: ""
  verification: ""
known_limitations: []
```

필수 정보가 없다고 해서 구현자의 설명으로 메우지 않는다. 최종 판정에 필요한 정보라면 `BLOCKED`의 근거로 기록한다.

## 4. 직접 확인할 증거

감사자는 작업에 관련된 항목만 선택해 직접 확인한다.

- 요구사항과 적용 지침이 최종 변경에 반영됐는가
- 감사 대상 식별자가 현재 최종 대상과 정확히 일치하는가
- diff와 생성 산출물에 범위 밖 변경, 비밀값, 개인정보 또는 내부 경로가 없는가
- 테스트 명령과 원시 결과를 재현하거나 신뢰할 수 있는 출처에서 확인했는가
- 실패 경로, 부분 실패, 재시도, rollback과 복구 절차를 검증했는가
- 권한, 데이터, 금전, 호환성, 가용성과 공급망 영향이 누락되지 않았는가
- `post-execution`이라면 실제 실행 ID, 최종 상태, 영향 범위, 부분 실패, 데이터 정합성과 복구 필요성을 확인했는가
- `post-deploy`라면 실제 배포 ID, 공개 상태, smoke test, 관측 결과와 rollback 필요성을 확인했는가

증거 우선순위는 사용자 제공 요구사항, 실제 파일·diff·데이터·로그·재현 가능한 테스트, 공식 계약·명세, 논리적 추론 순이다. 에이전트의 주장이나 같은 결론의 반복은 증거 수준을 높이지 않는다.

## 5. 발견사항과 판정

각 발견사항을 다음처럼 기록한다.

```yaml
id: "F1"
severity: "blocking | non_blocking"
status: "open | resolved | not_observable"
statement: ""
evidence_refs: []
impact: ""
required_remediation: ""
```

`blocking`은 요구사항 위반, 보안·권한·금전·데이터 손실 위험, rollback 불능, 잘못된 최종 대상, 필수 검증 누락 또는 완료 안전성을 바꾸는 결함에 사용한다. 나중에 개선해도 현재 완료 안전성이 달라지지 않는 항목만 `non_blocking`으로 둔다.

판정은 다음 순서를 따른다.

1. 확인된 열린 `blocking` 발견사항이 하나라도 있으면 `FAIL`이다.
2. 그렇지 않더라도 독립 감사자, 최종 대상, 필수 증거 또는 관측 가능성이 부족하면 `BLOCKED`다.
3. 독립성, 대상 일치, 필수 증거, 발견사항 처리, 재감사를 모두 충족했을 때만 `PASS`다.

테스트 성공만으로 `PASS`하지 않는다. v1.0에는 미해결 차단성 위험을 예외 승인으로 통과시키는 경로가 없다.

## 6. 수정과 재감사

감사 뒤 다음 중 하나가 바뀌면 기존 판정은 stale이다.

- 실행 동작, 권한, 데이터 흐름, 설정, dependency 또는 CI/CD
- 요구사항이나 완료 조건
- 테스트 명령, fixture, 기대값 또는 검증 결과
- 발견사항을 해결한 코드·문서·배포 상태
- 설치·운영·rollback 명령의 의미

구현자는 스스로 변경을 비의미적이라고 확정할 수 없다. 감사자가 diff를 확인해 영향 범위를 정하고 그 범위를 재감사한다. 범위가 불명확하거나 여러 위험 영역에 걸치면 전체 감사를 다시 수행한다. 공백·서식처럼 실행과 지침의 의미를 바꾸지 않는 변경도 감사자가 비의미적임을 확인하기 전까지 이전 판정을 재사용하지 않는다.

## 7. 결과 형식

```markdown
## Audit Target
- Phase:
- Final target:
- Scope:

## Independence
- Implementer(s):
- Auditor:
- Fresh context:
- Delegation:

## Evidence Checked
- Evidence and result

## Findings
- F1 [blocking|non_blocking] [open|resolved|not_observable]: finding, evidence, impact

## Remediation/Re-audit
- Changes, coverage, target identity, stale status

## Gate
- PASS | FAIL | BLOCKED
- Reason:

## Limitations
- Unobserved evidence or remaining uncertainty
```

결과는 확인한 증거에 연결한다. 섹션에 해당 내용이 없으면 `None` 또는 이유를 적어 누락과 무발견을 구분한다.

## 8. 종료 조건

다음 조건 중 하나에서 감사를 종료한다.

- 모든 완료 불변조건을 확인해 `PASS`했다.
- 열린 차단성 발견사항을 확인해 `FAIL`했고 필요한 수정이 명확하다.
- 감사자·증거·관측 가능성이 부족해 `BLOCKED`했고 필요한 다음 입력을 식별했다.

새 증거 없이 같은 검사를 반복하지 않는다. `FAIL` 뒤 수정하거나 `BLOCKED`의 원인이 해소되면 새 최종 대상을 확인하고 재감사한다.
