"""models iteration helper.

`finalize_iteration(part)` 를 model.py 끝에서 호출하면:
  1. 호출 파일이 속한 디렉토리를 프로젝트 루트로 인식
  2. intermediate/ 의 기존 iter 번호를 스캔해 다음 번호 결정
  3. 해당 iter 의 STEP 파일과 4방향 PNG (iso/front/top/side) 저장
  4. exports/<프로젝트명>.step 을 최신 결과로 덮어쓰기
  5. ocp_vscode 뷰어로 show()
"""

from __future__ import annotations

import inspect
import math
import re
from pathlib import Path

from build123d import export_step
from ocp_vscode import Camera, show


_ITER_PAT = re.compile(r"iter_(\d{3})")
_RENDER_SIZE = (1024, 768)


def _caller_project_dir() -> Path:
    frame = inspect.stack()[2]
    return Path(frame.filename).resolve().parent


def _next_iter_number(intermediate_dir: Path) -> int:
    if not intermediate_dir.exists():
        return 1
    nums = [int(m.group(1)) for p in intermediate_dir.iterdir() if (m := _ITER_PAT.match(p.name))]
    return (max(nums) + 1) if nums else 1


def _render_four_views(model_path: Path, out_dir: Path, iter_num: int) -> list[Path]:
    import f3d

    f3d.Engine.autoload_plugins()
    engine = f3d.Engine.create(offscreen=True)
    engine.window.size = _RENDER_SIZE
    engine.options["scene.up_direction"] = "+Z"
    engine.options["render.effect.ambient_occlusion"] = True
    engine.options["render.effect.antialiasing.enable"] = True
    engine.scene.add(str(model_path))

    cam = engine.window.camera
    cam.reset_to_bounds()
    state = cam.state
    focal = tuple(state.focal_point)
    pos = tuple(state.position)
    # default fit distance는 default direction 기준이라, 다른 view 에서는 부족할 수 있음.
    # 어떤 view 에서도 fit 되도록 충분한 margin 적용.
    dist = math.sqrt(sum((p - f) ** 2 for p, f in zip(pos, focal))) * 1.8

    views = {
        "iso":   ((dist * 0.577, -dist * 0.577, dist * 0.577), (0, 0, 1)),
        "iso2":  ((-dist * 0.577, dist * 0.577, dist * 0.577), (0, 0, 1)),
        "front": ((0, -dist, 0), (0, 0, 1)),
        "top":   ((0, 0, dist), (0, 1, 0)),
        "side":  ((dist, 0, 0), (0, 0, 1)),
    }

    paths: list[Path] = []
    for name, (offset, up) in views.items():
        cam.position = tuple(f + o for f, o in zip(focal, offset))
        cam.focal_point = focal
        cam.view_up = up
        out = out_dir / f"iter_{iter_num:03d}_{name}.png"
        engine.window.render_to_image().save(str(out))
        paths.append(out)
    return paths


def finalize_iteration(part, *, project_dir: Path | None = None, show_in_viewer: bool = True) -> int:
    """모델 빌드 후 호출. iter 번호 반환."""
    project_dir = project_dir or _caller_project_dir()
    project_name = project_dir.name

    intermediate_dir = project_dir / "intermediate"
    exports_dir = project_dir / "exports"
    intermediate_dir.mkdir(exist_ok=True)
    exports_dir.mkdir(exist_ok=True)

    iter_num = _next_iter_number(intermediate_dir)
    iter_step = intermediate_dir / f"iter_{iter_num:03d}.step"

    export_step(part, str(iter_step))
    final_step = exports_dir / f"{project_name}.step"
    final_step.write_bytes(iter_step.read_bytes())

    pngs = _render_four_views(iter_step, intermediate_dir, iter_num)

    print(f"[models] iter {iter_num:03d} done")
    print(f"  step:   {iter_step}")
    print(f"  final:  {final_step}")
    for p in pngs:
        print(f"  png:    {p}")

    if show_in_viewer:
        try:
            show(part, reset_camera=Camera.RESET)
        except Exception as e:
            print(f"[models] show() 실패 (ocp_vscode 컨테이너 미실행?): {e}")
        # 카테고리 하위 프로젝트는 "캠핑/modular_rack" 처럼 상대경로로 통지
        models_root = Path(__file__).resolve().parent.parent
        try:
            rel = project_dir.resolve().relative_to(models_root).as_posix()
        except ValueError:
            rel = project_name
        _notify_feedback_tool(rel)

    return iter_num


def finalize_mesh_iteration(stl: Path | str, *, suffix: str = "",
                            project_dir: Path | None = None) -> int:
    """**메시로 만든 모델**을 마무리한다. iter 번호 반환.

    build123d 로 솔리드를 쌓는 모델은 STEP 이 정본이지만, 온라인 STL 을 변형하거나
    등위면에서 뽑아내는 모델은 **처음부터 메시**다. 그걸 STEP 으로 내보내려면 삼각형마다
    B-rep 면을 만들어야 하는데, 그렇게 나온 파일은 아무 데서도 쓸 수 없다:

      - 뱀부랩 슬라이서가 로딩을 끝내지 못한다 (4 만 면 셸을 봉합·테셀레이션해야 한다).
        같은 모델의 STL 은 곧바로 열린다 — 실사용에서 확인했다.
      - 패널(danp.at/tools/modeling)의 STEP → STL 변환도 제한 시간을 넘긴다.
      - 파일이 103MB 로 STL(34MB)의 3 배다.

    그래서 메시 모델은 **STL 이 정본**이다. STEP 을 만들지 않는다.

    suffix 를 주면 `iter_007_<suffix>.stl` / `exports/<프로젝트명>_<suffix>.stl` 로 간다
    (한 프로젝트에서 치수 변종을 여러 개 뽑을 때).
    """
    project_dir = project_dir or _caller_project_dir()
    stl = Path(stl)

    intermediate_dir = project_dir / "intermediate"
    exports_dir = project_dir / "exports"
    intermediate_dir.mkdir(exist_ok=True)
    exports_dir.mkdir(exist_ok=True)

    iter_num = _next_iter_number(intermediate_dir)
    iter_stl = intermediate_dir / f"iter_{iter_num:03d}{suffix}.stl"
    iter_stl.write_bytes(stl.read_bytes())
    final_stl = exports_dir / f"{project_dir.name}{suffix}.stl"
    final_stl.write_bytes(iter_stl.read_bytes())

    pngs = _render_four_views(iter_stl, intermediate_dir, iter_num)

    print(f"[models] iter {iter_num:03d} done (mesh)")
    print(f"  stl:    {iter_stl}")
    print(f"  final:  {final_stl}")
    for p in pngs:
        print(f"  png:    {p}")
    return iter_num


def _notify_feedback_tool(project_name: str) -> None:
    """feedback_tool(:3940) 에 현재 프로젝트를 알려, 피드백 캡처 시 자동 선택되게 한다.
    서버가 안 떠 있어도 모델링은 계속되도록 best-effort."""
    import json
    import urllib.request

    try:
        req = urllib.request.Request(
            "http://localhost:3940/feedback/current",
            data=json.dumps({"project": project_name}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=1.5)
    except Exception:
        pass
