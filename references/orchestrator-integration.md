# Orchestrator Integration

이 문서는 `independent-audit-gate`를 여러 전문 스킬이 참여하는 오케스트레이션 흐름에 연결할 때 사용한다. v1.0의 연동 방식은 자연어 briefing과 구조화된 Markdown 결과이며, 별도 API나 `audit-run.json`을 요구하지 않는다.

## 1. 책임 분리

- 상위 orchestrator는 요청 유형 판별, 작업 순서, 구현자와 감사자 식별, fresh auditor 배정, 결과 전달을 맡는다.
- 요구사항·설계·검증·패키징 스킬은 감사에 필요한 산출물과 근거를 만들 수 있지만 최종 `Gate` 판정을 대신하지 않는다.
- `independent-audit-gate`는 위험 분류, 독립성 확인, 증거 확인 범위, 발견사항 심각도, stale 판정과 완료 게이트를 맡는다.
- auditor는 최종 대상과 원자료를 직접 확인한다. orchestrator나 다른 worker에게 감사를 다시 맡기지 않는다.

단독 실행에서는 현재 작업의 coordinator가 orchestrator 역할을 겸한다. 오케스트레이션 흐름에서 적격 auditor가 이미 배정됐다면 이 스킬은 같은 대상을 위한 감사자를 추가로 만들지 않는다.

## 2. 입력 handoff

orchestrator는 [audit-protocol.md](audit-protocol.md)의 감사자 briefing을 다음 논리 형식으로 전달한다. YAML 파일을 만들거나 저장할 필요는 없다.

```yaml
contract: "independent-audit-gate/v1.0"
mode: "orchestrated"
phase: "pre-execution | post-execution | pre-deploy | post-deploy"
requirements: []
applicable_instructions: []
risk_classification:
  areas: []
  rationale: ""
implementers: []
auditor:
  worker_id: ""
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

`auditor.worker_id`, `final_target.identifier` 또는 판정에 필요한 증거가 없으면 값을 추측하지 않는다. 감사 전제에 필요한 항목이라면 `BLOCKED`로 처리한다.

## 3. 출력 handoff

결과는 `SKILL.md`에 정의된 일곱 섹션을 같은 순서로 반환한다. orchestrator는 다음 항목을 직접 확인한 뒤에만 작업을 완료로 표시한다.

- `Audit Target`의 단계와 식별자가 현재 최종 대상과 일치한다.
- `Independence`에 구현자·감사자 분리, fresh context와 재위임 금지가 기록됐다.
- `Evidence Checked`가 실제 파일, diff, 명령, 로그 또는 배포 상태를 가리킨다.
- 열린 `blocking` 발견사항이 없다.
- `Gate` 값이 정확히 `PASS`다.
- 감사 뒤 의미 있는 변경이 없어 판정이 stale하지 않다.
- 실제 상태를 바꿨다면 해당 `post-execution` 또는 `post-deploy` 확인이 끝났다.

`FAIL`은 확인된 차단성 결함을 수정한 뒤 같은 감사자가 영향 범위를 다시 확인해야 한다. `BLOCKED`는 누락된 감사자·대상·증거·관측 가능성을 확보한 뒤 새 최종 대상을 기준으로 다시 실행한다.

## 4. 라우팅 경계

| 요청 | 담당 |
| --- | --- |
| 요구사항 수집과 정규화 | requirement skill |
| 대안 설계와 구현안 작성 | design skill |
| 테스트와 일반 품질 확인 | validation skill |
| 설치·릴리스 산출물 준비 | packaging skill |
| 복잡한 판단의 다관점 반박과 합의 | `independent-deliberation-panel` |
| 최종 고위험 변경의 독립 감사와 완료 판정 | `independent-audit-gate` |

상위 orchestrator는 필요한 스킬만 선택한다. 구현 대상이 없는 설계 토론에는 이 게이트를 호출하지 않고, 고위험 변경의 최종 대상을 고정할 수 있을 때 호출한다.

## 5. 플러그인 배치

플러그인에는 다음처럼 넣는다.

```text
orchestration-plugin/
├── plugin.json 또는 .codex-plugin/plugin.json
└── skills/
    ├── orchestrator-skill/
    │   └── SKILL.md
    └── independent-audit-gate/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── references/
        └── scripts/
```

이 스킬의 `SKILL.md`, `agents/`, `references/`, `scripts/`를 함께 복사한다. 저장소용 `README.md`, `LICENSE`, `.github/`, `.gitattributes`, `.gitignore`는 플러그인 루트의 정책과 CI에서 관리한다. 복사한 구성요소는 `scripts/validate_skill.py --strict`로 검사한다. 스크립트는 플러그인 위치를 자동으로 감지하며, 필요하면 `--profile plugin-component`를 명시할 수 있다.
