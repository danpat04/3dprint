"""Example: 간단한 박스 모델."""

from build123d import BuildPart, Box, fillet
from ocp_vscode import Camera, show

# 모서리가 둥근 박스
with BuildPart() as box:
    Box(30, 20, 10)
    fillet(box.edges(), radius=2)

show(box, reset_camera=Camera.RESET)
