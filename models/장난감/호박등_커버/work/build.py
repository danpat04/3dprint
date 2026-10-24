import numpy as np, scipy.ndimage as ndi, trimesh
from skimage import measure
mp=np.load('work/maps.npz'); R=mp['R']; H=mp['H'].astype(float)
ZC=52.0
# --- 파라미터 (최종 mm) ---
import os
OUT_D=float(os.environ.get('PUMPKIN_OUT_D','70.0'))   # 최대 외경 (v1/v2=70)
import os
sz=float(os.environ.get('PUMPKIN_SZ','0.5'))   # 세로 배율 (v1=0.5, v2=0.555)
Z_CUT=9.0
WALL=1.2
TOP_HOLE_R=9.0
PITCH=0.3
sxy=OUT_D/140.0
H_TOT=(104.0-Z_CUT)*sz
print('sxy',sxy,'sz',sz)
NT,NP=R.shape
xs=np.arange(-OUT_D/2-3,OUT_D/2+3+PITCH,PITCH)
zs=np.arange(-3,H_TOT+3,PITCH)
X,Y,Z=[a.astype(np.float32) for a in np.meshgrid(xs,xs,zs,indexing="ij")]
xo=X/sxy; yo=Y/sxy; zo=Z/sz+Z_CUT-ZC
r=np.sqrt(xo**2+yo**2+zo**2)+1e-9
th=np.mod(np.arctan2(yo,xo),2*np.pi)/(2*np.pi)*NT
ph=(np.degrees(np.arcsin(np.clip(zo/r,-1,1)))+90)
def samp(A,order=1):
    Ap=np.vstack([A,A[:1]])
    return ndi.map_coordinates(Ap,[th.ravel(),ph.ravel()],order=order,mode='nearest').reshape(th.shape)
Rv=samp(R)
E=r<Rv
def sdf(B):
    return ndi.distance_transform_edt(B,sampling=PITCH)-ndi.distance_transform_edt(~B,sampling=PITCH)
sE=ndi.gaussian_filter(sdf(E),1.0)          # +: 안쪽
g=np.minimum(sE,WALL-sE)                   # 벽 두께 WALL 의 껍질
g=np.minimum(g,Z)                           # 아래 절단면
Hs=samp(mp['Hs'],order=1)                 # 연속 필드: 0.5 등치선이 구멍 윤곽
sH=ndi.gaussian_filter((Hs-0.5)*3.0,0.8)    # +: 구멍 안쪽
g=np.minimum(g,-sH)                         # 얼굴 구멍
top=(np.hypot(X,Y)<TOP_HOLE_R)&(Z>H_TOT*0.5)
sT=ndi.gaussian_filter(sdf(top),1.0)
g=np.minimum(g,-sT)
# 아래 개구부: 깨끗한 원통 보어 + 일정 높이의 매끈한 립
R_BORE=24.5; H_LIP=3.0
RXY=np.hypot(X,Y)
g=np.where(Z<H_LIP,np.minimum(g,RXY-R_BORE),g)
lip=np.minimum(np.minimum(sE,H_LIP-Z),np.minimum(RXY-R_BORE,Z))   # 몸통 외곽 안쪽만 채우는 안쪽 칼라
g=np.maximum(g,lip)
f=g.astype(np.float32)
v,fc,_,_=measure.marching_cubes(f,0.0,spacing=(PITCH,)*3)
v+=np.array([xs[0],xs[0],zs[0]])
m=trimesh.Trimesh(v,fc)
m=max(m.split(only_watertight=False),key=lambda c:len(c.faces))
trimesh.smoothing.filter_taubin(m,iterations=8)
print(m.is_watertight,m.bounds,m.volume, len(m.faces))
if m.volume<0: m.invert()
m.export(os.environ.get('PUMPKIN_STL','work/pumpkin.stl'))
