# Independent Audit Gate

`independent-audit-gate` is a Codex skill that checks whether a high-risk change has received an independent, evidence-based audit before it is marked complete.

보안·권한·결제·데이터 손실·스키마 마이그레이션·프로덕션 배포·전역 설정처럼 실패 영향이 큰 변경을 완료하기 전에 사용합니다. 구현에 참여하지 않은 감사자가 최종 변경과 검증 자료를 직접 확인하고 `PASS`, `FAIL`, `BLOCKED` 중 하나로 판정합니다. 실제 상태를 바꾼 뒤에는 실행·배포 식별자, 영향 범위, 부분 실패와 복구 필요성도 확인합니다.

## 언제 사용하나요

다음 작업을 실행하거나 릴리스하려 할 때 맞습니다.

- 인증·인가·비밀값·외부 노출 변경
- 결제·환불·가격·거래 실행 변경
- 영구 삭제, 대량 수정, 개인정보 또는 복구 절차 변경
- 스키마 마이그레이션과 호환성 변경
- 프로덕션 배포, 공개 릴리스, 인프라와 CI/CD 변경
- 조직이나 프로젝트 전체에 적용되는 설정 변경

단순 조사, 저위험 수정, 일반 코드 리뷰, 구현할 대상이 없는 설계 토론에는 사용하지 않습니다. 복잡한 판단을 여러 관점에서 논쟁하고 합의안을 만드는 `independent-deliberation-panel`과도 역할이 다릅니다. 이 스킬은 패널이나 Judge를 구성하지 않고, 최종 변경에 독립 감사와 완료 게이트가 제대로 적용됐는지만 다룹니다.

## 설치

### 사용자 범위

Windows PowerShell:

```powershell
git clone https://github.com/jaeseongs95/codex-independent-audit-gate "$env:USERPROFILE\.agents\skills\independent-audit-gate"
```

macOS 또는 Linux:

```bash
git clone https://github.com/jaeseongs95/codex-independent-audit-gate "$HOME/.agents/skills/independent-audit-gate"
```

### 저장소 범위

특정 프로젝트에서만 사용하려면 그 프로젝트 루트에서 설치합니다.

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path '.agents\skills' | Out-Null
git clone https://github.com/jaeseongs95/codex-independent-audit-gate '.agents\skills\independent-audit-gate'
```

macOS 또는 Linux:

```bash
mkdir -p .agents/skills
git clone https://github.com/jaeseongs95/codex-independent-audit-gate .agents/skills/independent-audit-gate
```

Codex가 새 스킬을 자동으로 찾지 못하면 Codex를 다시 시작합니다.

특정 버전을 고정하려면 clone 명령에 `--branch v1.0.0 --depth 1`을 추가합니다.

## 사용

직접 호출하려면 요청에 `$independent-audit-gate`를 넣습니다.

```text
$independent-audit-gate를 사용해 이 권한 변경의 최종 diff와 테스트 결과를 독립 감사하고 완료 가능 여부를 판정해 줘.
```

```text
$independent-audit-gate로 이 마이그레이션의 rollback 검증과 배포 후 상태를 확인해 줘.
```

자동 호출도 켜져 있습니다. 고위험 변경을 실행·배포·완료하려는 요청과 일치하면 Codex가 이 스킬을 선택할 수 있습니다.

## 판정

- `PASS`: 독립성, 최종 대상 일치, 필수 증거, 발견사항 처리와 재감사를 모두 확인했습니다.
- `FAIL`: 확인된 열린 `blocking` 발견사항이 있습니다.
- `BLOCKED`: 감사자, 최종 대상 또는 필수 증거를 확보하지 못해 판정을 마칠 수 없습니다.

테스트가 성공했다는 이유만으로 `PASS`하지 않습니다. 감사 뒤 동작이나 검증 근거가 바뀌면 이전 판정은 효력을 잃으며, 변경된 범위를 다시 감사해야 합니다.

## 업데이트와 제거

사용자 범위 설치를 업데이트하려면 다음 명령을 실행합니다.

Windows PowerShell:

```powershell
git -C "$env:USERPROFILE\.agents\skills\independent-audit-gate" pull --ff-only
```

macOS 또는 Linux:

```bash
git -C "$HOME/.agents/skills/independent-audit-gate" pull --ff-only
```

제거할 때는 설치한 `independent-audit-gate` 디렉터리만 삭제합니다. 다른 스킬 디렉터리나 `.agents` 상위 폴더는 삭제하지 마세요.

## 플러그인에 포함하기

여러 전문 스킬을 묶은 오케스트레이션 플러그인에는 이 저장소의 `SKILL.md`, `agents/`, `references/`, `scripts/`를 `skills/independent-audit-gate/` 아래에 복사합니다. 플러그인 루트에는 대상 도구가 지원하는 `plugin.json` 또는 `.codex-plugin/plugin.json`이 있어야 합니다. `README.md`, `LICENSE`, `.github/`, `.gitattributes`, `.gitignore`는 플러그인 루트에서 관리합니다.

연동할 때는 [orchestrator integration guide](references/orchestrator-integration.md)에 정의된 책임 분리와 handoff 형식을 따릅니다. orchestrator는 요청 분류와 감사자 배정을 맡고, 이 스킬은 독립 감사와 `PASS`, `FAIL`, `BLOCKED` 판정을 맡습니다. 복사한 하위 스킬 디렉터리에서 다음 명령으로 구성요소를 검사할 수 있습니다.

```bash
python scripts/validate_skill.py --strict
```

검증기는 지원되는 플러그인 배치를 자동으로 감지합니다. 자동 감지를 사용하지 않으려면 `--profile plugin-component`를 지정합니다. 저장소 자체를 검사할 때는 `--profile standalone`을 사용할 수 있습니다.

이 스킬은 `independent-deliberation-panel`을 개발 검토에만 사용하며 런타임 의존성으로 두지 않습니다.

## 개발 검증

Windows:

```powershell
py -3 scripts/validate_skill.py --strict
py -3 scripts/test_plugin_component.py
```

macOS 또는 Linux:

```bash
python3 scripts/validate_skill.py --strict
python3 scripts/test_plugin_component.py
```

검증기는 패키지 구조, 메타데이터, 로컬 링크와 공개 저장소에 포함하면 안 되는 흔적을 확인합니다. 감사 내용의 사실성이나 실제 에이전트 독립성을 자동으로 증명하지는 않습니다.

## 라이선스

[MIT License](LICENSE)
