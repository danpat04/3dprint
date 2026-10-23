import f3d,sys
f3d.Engine.autoload_plugins()
e=f3d.Engine.create(offscreen=True)
e.window.size=(1024,768)
e.options["scene.up_direction"]="+Z"
e.options["render.effect.ambient_occlusion"]=True
e.scene.add("work/pumpkin.stl")
c=e.window.camera
c.reset_to_bounds()
e.window.render_to_image().save("/tmp/r/p1.png")
c.azimuth(180); e.window.render_to_image().save("/tmp/r/p2.png")
c.azimuth(90);c.elevation(-60); e.window.render_to_image().save("/tmp/r/p3.png")
c.elevation(150); e.window.render_to_image().save("/tmp/r/p4.png")
