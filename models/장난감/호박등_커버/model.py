"""호박등 커버: 온라인 STL(feedback/dynia+led+2+stl.stl)을 램프용으로 변형.

work/rmap.py   원본에서 중심 기준 방사 반경 맵(바깥 표면) 추출 (느림, 1회만; rmap.npz 캐시)
work/maps.py   뒷문 메꿈 / 윗면 오류 보정 / 얼굴 구멍 마스크
work/build.py  비등방 스케일 + 벽 1.2mm 껍질 + 위·아래 개구부 -> work/pumpkin.stl
"""
import shutil
import subprocess
import sys
from pathlib import Path

import trimesh
from build123d import Face, Wire, Vector, Shell, Solid, export_step
from models._lib.iter import _next_iter_number, _render_four_views

HERE = Path(__file__).resolve().parent


def run(script):
    subprocess.run([sys.executable, str(HERE / "work" / script)], cwd=HERE, check=True)

# `__main__` 가드가 있어야 패널이 "다시 빌드"할 수 있는 파트로 인식한다
# (modeler/app/discover.py 의 _runnable). python -m 으로 돌리는 동작은 그대로다.
if __name__ == "__main__":
    if not (HERE / "work/rmap.npz").exists():
        run("rmap.py")
    run("maps.py")
    run("build.py")

    inter = HERE / "intermediate"
    exports = HERE / "exports"
    inter.mkdir(exist_ok=True)
    exports.mkdir(exist_ok=True)
    n = _next_iter_number(inter)
    stl = inter / f"iter_{n:03d}.stl"
    shutil.copy(HERE / "work/pumpkin.stl", stl)
    shutil.copy(stl, exports / f"{HERE.name}.stl")
    for p in _render_four_views(stl, inter, n):
        print("png:", p)
    print("iter", n, stl)

    # 패널 표시용 STEP (4만 면으로 줄여 변환; 출력은 STL 사용)
    d = trimesh.load(HERE / "work/pumpkin.stl").simplify_quadric_decimation(face_count=40000)
    solid = Solid(Shell([Face(Wire.make_polygon([Vector(*d.vertices[i]) for i in f], close=True)) for f in d.faces]))
    export_step(solid, str(exports / f"{HERE.name}.step"))
