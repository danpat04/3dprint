# models — 스펙 드리븐 자율 모델링 워크플로

이 디렉토리(`models/`)는 **사용자가 스펙(요구사항)을 정의하고, Claude가 처음부터 끝까지 모델링/검증을 자율 수행**하는 워크플로 영역입니다. 과거 협업 모델링 작업물(사용자가 한 단계씩 지시하던 방식)은 `legacy/` 로 보존되어 있습니다.

## 디렉토리 구조

```
models/
  CLAUDE.md                    이 파일 (워크플로 정본)
  _lib/
    iter.py                    finalize_iteration() 헬퍼
  <project_name>/              각 모델링 프로젝트
    README.md                  스펙 + 진행 기록 + 최종 결과 문서
    model.py                   모델링 코드 (단일 파트)
    # 다중 파트일 경우:
    # body.py, handle.py ...
    # assembly.py              전체 조립 + finalize 호출
    intermediate/              iter 별 결과물 (.gitignore에 어차피 제외됨)
      iter_001.step
      iter_001_iso.png
      iter_001_front.png
      iter_001_top.png
      iter_001_side.png
      iter_002_*.{step,png}
      ...
    exports/
      <project_name>.step      최신 iter 결과 (덮어쓰기)
    images/                    완료 후 README에 임베드할 최종 이미지
```

## 작업 절차

### 1. 프로젝트 시작
사용자가 모델링 주제와 이름을 제시 (예: "커피 탬퍼 만들자, 이름은 coffee_tamper").
- `models/<snake_case_name>/` 디렉토리 생성
- 빈 `README.md` 생성 (스펙 섹션 골격만)

### 2. 스펙 작성 (대화 기반 반복)
README.md 를 사용자와 함께 채워나감. 권장 섹션:
- **목적/용도** — 무엇을 위한 모델인가
- **치수/제약** — 정확한 수치 (mm). 인터페이스(다른 파트와 결합하는 치수)는 명시
- **acceptance criteria** — 검증 가능한 형태 (예: "외경 30mm ± 0.1", "구멍 8개가 반경 10mm 원주에 등간격")
- **재료/공정 가정** — 3D 프린팅 전제 (오버행, 서포트, 톨러런스 등)
- **참고 이미지/도면** — 손스케치는 `models/<프로젝트>/refs/` 에 저장

### 3. 모델링
`model.py` 작성. **모든 모델 코드는 끝에서 `finalize_iteration()` 호출**:

```python
from build123d import BuildPart, Cylinder, ...
from models._lib.iter import finalize_iteration

with BuildPart() as part:
    # ... modeling ...
    pass

finalize_iteration(part.part)
```

`finalize_iteration` 동작:
1. 호출한 .py 파일의 디렉토리를 프로젝트 루트로 인식 (inspect 기반)
2. `intermediate/` 의 기존 `iter_NNN.*` 스캔 → 다음 번호 결정
3. `intermediate/iter_NNN.step` + 4방향 PNG (iso/front/top/side) 저장
4. `exports/<프로젝트명>.step` 덮어쓰기
5. ocp_vscode 뷰어로 `show()` (컨테이너 미실행 시 graceful fail)

다중 파트 프로젝트는 `body.py` 등 분리 + `assembly.py` 끝에서 `finalize_iteration(assembled_part)` 호출.

### 4. 검증
모델 실행 후 Claude는 `intermediate/iter_NNN_*.png` 4장을 모두 Read 해서:
- 사용자가 명시한 acceptance criteria 가 시각적으로 충족되는지 확인
- 의도하지 않은 형상 결함(잘못된 위치 구멍, 누락된 feature, 꼬임 등) 점검
- 발견된 문제는 다음 iter 에서 수정

### 5. 사용자 확인 → 피드백 → 다음 iter
사용자가 ocp_vscode 뷰어(`localhost:3939`)로 결과 확인 → 피드백 제공 → Claude 가 `model.py` 수정 → `uv run python -m models.<프로젝트>.model` 재실행 → iter_002 자동 생성.

**iter 번호는 자동 증가. 사용자가 "iter 3" 처럼 번호로 참조하면 그 시점의 PNG/STEP을 확인.**

### 6. 종료 선언
사용자가 "완료" 선언 시:
1. 마지막 iter 의 4장 PNG 를 `images/` 로 복사 (또는 직접 `intermediate/` 참조해도 됨)
2. `README.md` 에 결과 이미지 임베드 (`![iso](images/iter_NNN_iso.png)` 등)
3. README 의 스펙 섹션이 최종 결과와 일치하는지 점검, 필요 시 갱신
4. `intermediate/` 정리는 **사용자에게 확인 후** 진행 (디버깅 흔적 보존 원할 수 있음)
5. `exports/<프로젝트명>.step` 유지

## 사전 조건 / 운영 메모

- **Python 실행**: 항상 `uv run` (예: `uv run python -m models.<프로젝트>.model`)
- **ocp_vscode 뷰어**: 사용자가 docker compose 로 띄워둠 (`localhost:3939`). 미실행이면 show() 만 실패하고 export/render는 정상 동작
- **`.gitignore`**: `*.step`, `*.stl`, `exports/`, `intermediate/` 는 루트 `.gitignore` 에 제외 (재생성 가능). git 에 남는 결과물은 `images/` 의 최종 PNG + `model.py` 소스. `uv.lock` 은 의존성 재현성 위해 커밋됨
- **f3d 렌더 옵션**: scene up=+Z, AO+AA 활성화. 변경하려면 `_lib/iter.py` 수정

## 검증 한계 (Claude 가 못 보는 것)

- **실제 조립 가능성** — 다른 파트와의 fit 은 사용자가 ocp_vscode 에서 직접 확인
- **3D 프린트 가능성** — 오버행/얇은 벽/서포트 필요성 같은 출력 관점 검토는 사용자 영역
- **내부 구조** — 단면(section) PNG 는 현재 기본 셋에 없음. 필요하면 사용자가 요청
- **치수 정확성** — PNG 만으로는 mm 단위 검증 불가능. STEP 파일의 BBox/볼륨/면 개수 같은 정량 지표는 별도 코드 assert로 보완해야 함 (현재 미구현, 필요해지면 헬퍼 확장)
