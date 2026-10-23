import f3d,sys,math
f3d.Engine.autoload_plugins()
e=f3d.Engine.create(offscreen=True)
e.window.size=(900,700)
e.options["scene.up_direction"]="+Z"
e.options["render.effect.ambient_occlusion"]=True
e.scene.add("work/pumpkin.stl")
c=e.window.camera
c.reset_to_bounds()
st=c.state; f=tuple(st.focal_point); dist=math.dist(f,tuple(st.position))*1.0
views={"top":((0,0,dist),(0,1,0)),"bot":((0,0,-dist),(0,1,0)),"right":((dist,0,0),(0,0,1)),"left":((-dist,0,0),(0,0,1)),"back":((0,dist,0),(0,0,1))}
for n,(o,u) in views.items():
    c.position=tuple(a+b for a,b in zip(f,o)); c.focal_point=f; c.view_up=u
    e.window.render_to_image().save(f"/tmp/r/v_{n}.png")
