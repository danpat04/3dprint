import numpy as np, scipy.ndimage as ndi
d=np.load('work/rmap.npz'); R=d['R'].copy()
NT,NP=R.shape
# 문(뒷면 구멍) 패치
nan=np.isnan(R)
M=ndi.binary_dilation(nan,structure=np.ones((3,3)),iterations=1)
M=ndi.binary_dilation(M,structure=np.ones((7,3)))   # 약 3° 여유
ths=np.where(M.any(1))[0]; print('door theta',ths.min()*.5,ths.max()*.5)
a,b=ths.min(),ths.max()
best=None
for s in range(100,200):  # 50..100 deg
    sh=s
    if not (b+sh)*0.5<205: continue
    L=np.nanmean(np.abs(R[a-12:a,60:121]-R[(a-12+sh):(a+sh),60:121]))
    Rr=np.nanmean(np.abs(R[b+1:b+13,60:121]-R[(b+1+sh):(b+13+sh),60:121]))
    sc=L+Rr
    if best is None or sc<best[0]: best=(sc,s)
print(best)
s=best[1]
R2=R.copy()
for i in range(NT):
    R2[i][M[i]]=R[(i+s)%NT][M[i]]
# 윗부분 오류 띠 복구: 정상 구간(θ 25~160)의 갈비 무늬를 주기 반복
j0=131; good0,good1=60,320   # 인덱스(0.5°): 25°~160°
L=good1-good0; per=225        # 112.5° = 10 갈비
Rg=R2.copy()
for i in range(NT):
    if good0<=i<good1: continue
    ig=good0+((i-good0)%per)
    off=R2[i,j0-1]-R2[ig,j0-1]
    for j in range(j0,NP):
        fade=max(0.0,1-(j-j0)/18.0)
        Rg[i,j]=R2[ig,j]+off*fade
R2=Rg
# 얼굴 구멍
H=np.zeros_like(M)
box=np.zeros_like(M); box[400:680,45:136]=True
H=(R2<58)&box
H=ndi.binary_opening(H,iterations=1); H=ndi.binary_closing(H,iterations=2)
print('hole px',H.sum())
# 구멍 메우기 (라플라스 확산)
Rf=R2.copy(); Rf[H]=np.nan
H=ndi.gaussian_filter(H.astype(float),1.2)>0.5; H=ndi.binary_dilation(H,iterations=1); Hd=ndi.binary_dilation(H,iterations=3)
Rf[Hd]=np.nan
known=~np.isnan(Rf)
Rf[~known]=np.nanmean(Rf)
for it in range(3000):
    avg=(np.roll(Rf,1,0)+np.roll(Rf,-1,0)+np.roll(Rf,1,1)+np.roll(Rf,-1,1))/4
    Rf[~known]=avg[~known]
# 거친 부분 정리
Rm=ndi.median_filter(Rf,size=(5,3),mode='wrap')
Rf=np.where(ndi.binary_dilation(M|Hd,iterations=4),Rm,Rf)
Rs=ndi.gaussian_filter(Rf,(2.0,1.0),mode=('wrap','nearest'))
w=np.zeros(NP); w[130:]=1.0; w=ndi.gaussian_filter(w,3)   # 위쪽(φ>40)은 더 부드럽게
Rf=Rf*(1-w[None,:])+Rs*w[None,:]
# 위쪽 줄기 영향 제거
j=np.argmin(np.abs(np.degrees(d['ph'])-66)); Rf[:,j:]=Rf[:,[j]]
np.savez('work/maps.npz',R=Rf,H=H,Hd=Hd,M=M,s=s)
