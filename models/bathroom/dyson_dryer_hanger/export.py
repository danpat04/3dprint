"""dyson_dryer_hanger — 부품별 STEP export.

    uv run python -m models.bathroom.dyson_dryer_hanger.export

  exports/rib.step          리브 — **2개 필요**. 좌우 완전 동일품
  exports/connector_a.step  선반 위 십자 맞춤 커넥터 — 1개
  exports/beam.step         하단 보 — 1개
  exports/assembly.step     조립 확인용 (출력물 아님)

출력 방향 (전부 서포트 불필요):
  리브        프로파일 면을 bed 에. 힘이 전부 면 안쪽 방향이라 압출선이 그대로 받는다
  커넥터 A    모델 좌표 그대로. 맞물림 홈이 위로 열려 오버행 없음
  보          **90° 눕혀서** 구멍이 수직이 되게. 모델 좌표 그대로 뽑으면
              구멍이 가로 터널이 되어 윗부분에 브리지가 생긴다
"""

from pathlib import Path

from build123d import export_step

from models.bathroom.dyson_dryer_hanger.hanger import (
    build_assembly,
    build_beam,
    build_connector_a,
    build_rib_right,
)

EXPORTS = Path(__file__).parent / "exports"

PARTS = {
    "rib": (build_rib_right, 2),
    "connector_a": (build_connector_a, 1),
    "beam": (build_beam, 1),
    "assembly": (lambda: build_assembly(with_dryer=False), 0),
}

if __name__ == "__main__":
    EXPORTS.mkdir(exist_ok=True)
    total = 0.0
    for name, (fn, qty) in PARTS.items():
        part = fn()
        path = EXPORTS / f"{name}.step"
        export_step(part, str(path))
        g = part.volume * 1.27e-3
        if qty:
            total += g * qty
        bb = part.bounding_box()
        note = f"× {qty}" if qty else "(조립 확인용)"
        print(f"  {path.name:<18} {bb.size.X:6.1f} × {bb.size.Y:6.1f} × {bb.size.Z:6.1f}"
              f"   PETG {g:5.1f} g  {note}")
    print(f"\n출력 합계: PETG 약 {total:.0f} g")
