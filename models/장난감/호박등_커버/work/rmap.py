import numpy as np, vtk, trimesh
from vtk.util.numpy_support import numpy_to_vtk
m=trimesh.load('feedback/dynia+led+2+stl.stl')
CX,CY,ZC=70.004,69.354,52.0
m.apply_translation([-CX,-CY,0])
pd=vtk.vtkPolyData(); pts=vtk.vtkPoints(); pts.SetData(numpy_to_vtk(m.vertices.astype(float)))
pd.SetPoints(pts); ca=vtk.vtkCellArray()
f=np.hstack([np.full((len(m.faces),1),3),m.faces]).astype(np.int64).ravel()
ca.SetCells(len(m.faces), numpy_to_vtk(f, deep=True, array_type=vtk.VTK_ID_TYPE)); pd.SetPolys(ca)
tree=vtk.vtkOBBTree(); tree.SetDataSet(pd); tree.BuildLocator()
NT,NP=720,181
th=np.linspace(0,2*np.pi,NT,endpoint=False); ph=np.radians(np.linspace(-90,90,NP))
R=np.full((NT,NP),np.nan); Rin=np.full((NT,NP),np.nan)
L=200.0
for i,t in enumerate(th):
    for j,p in enumerate(ph):
        d=np.array([np.cos(p)*np.cos(t),np.cos(p)*np.sin(t),np.sin(p)])
        o=np.array([0,0,ZC]); out=vtk.vtkPoints()
        if tree.IntersectWithLine(o,o+d*L,out,None):
            n=out.GetNumberOfPoints()
            rs=sorted(np.linalg.norm(np.array(out.GetPoint(k))-o) for k in range(n))
            R[i,j]=rs[-1]; Rin[i,j]=rs[0]
np.savez('work/rmap.npz',R=R,Rin=Rin,th=th,ph=ph,ZC=ZC)
print(np.isnan(R).sum(), R.shape)
