"""호박등 커버: 온라인 STL(feedback/dynia+led+2+stl.stl)을 램프용으로 변형.

work/rmap.py   원본에서 중심 기준 방사 반경 맵(바깥 표면) 추출 (느림, 1회만; rmap.npz 캐시)
work/maps.py   뒷문 메꿈 / 윗면 오류 보정 / 얼굴 구멍 마스크
work/build.py  비등방 스케일 + 벽 1.2mm 껍질 + 위·아래 개구부 -> work/pumpkin.stl
"""
import subprocess
import sys
from pathlib import Path

from models._lib.iter import finalize_mesh_iteration

HERE = Path(__file__).resolve().parent


def run(script):
    subprocess.run([sys.executable, str(HERE / "work" / script)], cwd=HERE, check=True)


def build(tag="", sz=0.5, out_d=70.0):
    """tag 가 비면 v1(기존 파일명), 아니면 `<폴더명>_<tag>` 로 내보낸다."""
    import os
    if not (HERE / "work/rmap.npz").exists():
        run("rmap.py")
    run("maps.py")
    suffix = f"_{tag}" if tag else ""
    stl_work = f"work/pumpkin{suffix}.stl"
    os.environ["PUMPKIN_SZ"] = str(sz)
    os.environ["PUMPKIN_OUT_D"] = str(out_d)
    os.environ["PUMPKIN_STL"] = stl_work
    run("build.py")

    # **STEP 을 만들지 않는다.** 처음부터 메시인 모델이라 삼각형마다 B-rep 면을 만들어야
    # 하는데, 그렇게 나온 STEP 은 뱀부랩이 로딩을 끝내지 못한다 (실사용 확인). STL 은 바로 열린다
    return finalize_mesh_iteration(HERE / stl_work, suffix=suffix)


# `__main__` 가드가 있어야 패널이 "다시 빌드"할 수 있는 파트로 인식한다
# (modeler/app/discover.py 의 _runnable). python -m 으로 돌리는 동작은 그대로다.
if __name__ == "__main__":
    build()
