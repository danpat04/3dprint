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


def _render_four_views(step_path: Path, out_dir: Path, iter_num: int) -> list[Path]:
    import f3d

    f3d.Engine.autoload_plugins()
    engine = f3d.Engine.create(offscreen=True)
    engine.window.size = _RENDER_SIZE
    engine.options["scene.up_direction"] = "+Z"
    engine.options["render.effect.ambient_occlusion"] = True
    engine.options["render.effect.antialiasing.enable"] = True
    engine.scene.add(str(step_path))

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
        # 카테고리 하위 프로젝트는 "camping/modular_rack" 처럼 상대경로로 통지
        models_root = Path(__file__).resolve().parent.parent
        try:
            rel = project_dir.resolve().relative_to(models_root).as_posix()
        except ValueError:
            rel = project_name
        _notify_feedback_tool(rel)

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
