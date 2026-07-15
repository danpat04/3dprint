# 3D Printing Modeling

**코드로 3D 모델을 설계하고 → 렌더링으로 확인·피드백하며 다듬어 → STEP으로 내보내 3D 프린팅**하는 자율 모델링 워크플로 저장소.

사용자가 스펙(요구사항)을 대화로 정의하면, AI 에이전트가 [build123d](https://github.com/gumyr/build123d) 코드로 모델을 만들고 스스로 렌더링해 검증한다. 사용자는 브라우저 뷰어로 결과를 보고 **스크린샷 위에 그림을 그려 피드백**한다. 이 사이클을 반복해 완성하고 STEP 파일로 출력한다.

## 워크플로

```
① 스펙 정의        사용자 ↔ 에이전트 대화로 치수·용도·제약 확정
        │
② 모델링          build123d 로 파라메트릭 모델 작성 (models/<project>/model.py)
        │
③ 렌더 & 검증      ├─ 에이전트: f3d 로 5방향 PNG 자동 생성 → 읽고 형상 검증
        │          └─ 사용자: 브라우저 뷰어로 3D 직접 확인
        │
④ 피드백          사용자가 뷰어 화면을 캡처 → 그 위에 덧그림 → 업로드
        │          에이전트가 그 이미지를 읽고 의도 파악
        │
⑤ 반복            ②~④ 를 만족할 때까지 (iter_001, iter_002, …)
        │
⑥ 출력            STEP export → 슬라이서 → 3D 프린팅
```

에이전트는 3D 뷰어를 볼 수 없으므로 **③에서 f3d로 PNG를 떠서 스스로 검증**하고, **④에서 사용자의 덧그림 이미지를 읽어** 사람의 의도를 시각적으로 받는다. 이 두 경로가 "AI가 화면을 못 보는" 약점을 메운다.

## 도구

| 도구 | 역할 |
|---|---|
| **[build123d](https://github.com/gumyr/build123d)** | Python 코드로 3D 모델을 정의하는 파라메트릭 CAD 라이브러리. 모든 `model.py` 의 본체 |
| **[ocp_vscode](https://github.com/bernhard-42/vscode-ocp-cad-viewer)** | 브라우저 3D 뷰어 (three.js 기반). `show()` 로 모델을 띄워 사용자가 회전·확대로 확인 |
| **[f3d](https://f3d.app/)** | 헤드리스 렌더러. STEP 를 iso/iso2/front/top/side **5방향 PNG** 로 변환 → 에이전트가 읽고 시각 검증 |
| **feedback_tool** (자작) | 뷰어에 드로잉 오버레이(`inject.js`)를 주입 + 업로드 서버. **캡처 → 펜 덧그림 → 업로드** → `models/<project>/feedback/` 저장. 에이전트가 읽음 |

핵심 접착제는 `models/_lib/iter.py` 의 **`finalize_iteration(part)`** — model.py 끝에서 한 번 호출하면 **STEP export + 5방향 PNG 렌더 + exports 갱신 + 뷰어 표시** 를 한꺼번에 처리한다.

## 디렉토리 구조

```
models/                    자율 모델링 영역 (워크플로 정본: models/CLAUDE.md)
  _lib/iter.py             finalize_iteration() — 렌더/export 헬퍼
  <project>/
    model.py               단일 파트 모델
    # 다중 파트: case.py + cover.py, 또는 params.py + assembly.py
    README.md              스펙·조립·출력 방향
    images/                README 임베드용 최종 PNG (git 추적)
    exports/               STEP 출력 (gitignore, 재생성 가능)
    intermediate/          iter 별 PNG/STEP (gitignore)
    feedback/              사용자 덧그림 피드백 (gitignore)
  coffee/                  카테고리 그룹핑 예: tamper_stand, portafilter_stand, …
  toy/                     예: bubble (WIP)
```

git 에는 **소스(`*.py`) + `README.md` + `images/` 만** 남고, STEP·중간 PNG·피드백은 `.gitignore` 로 제외한다 (언제든 재생성 가능).

## 사용법

```bash
# 모델 빌드 → STEP export + 5방향 PNG + 뷰어에 표시
python -m models.<project>.model
# 카테고리 하위: python -m models.coffee.<project>.model

# 다중 파트 조립 확인 / 개별 STEP export
python -m models.<project>.assembly
python -m models.<project>.export
```

## 모델 목록 (일부)

- **camping/** — cutlery_holder(수저통) · tarp_magnet_holder(타프 자석) · knife_cover(식칼 시스)
- **coffee/** — tamper_stand · portafilter_stand · feimaobuk_a2_cup · distributor_stand · dutch_knob
- **mouse_case** — 무선 마우스 여행용 케이스 (자석 결합)
- **shrimp_scoop · juice_pack_holder · monitor_stand · puck_screen_holder** 등

각 모델의 상세 스펙·이미지는 해당 폴더의 `README.md` 참고.
