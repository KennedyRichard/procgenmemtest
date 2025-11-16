"""Facility to run scenario X.

This scenario is just a procgen playground: it displays a UV sphere model
at the center. The sphere is generated procedurally and the user can provide
arguments to control how the end result: radius, number of segments and rings
of the sphere (vertical and horizontal sections, respectively).

A white sphere of radius 0.5 (diameter 1) is also shown besides the generated
sphere, for comparison.
"""

### standard library imports

from itertools import cycle

from pathlib import Path

from math import ceil


### third-party imports

from direct.showbase.ShowBase import ShowBase

from direct.task import Task

from direct.gui.OnscreenText import OnscreenText

from panda3d.core import GeomNode, Filename


### local imports

from ..modelgen.uvspheregeom import get_uv_sphere_geom
from ..modelgen.uvsphereegg import get_uv_sphere_egg_data

from ..points2d import yield_2d_circle_points



def run_scenario(
    radius=1.0,
    no_of_segments=16,
    no_of_rings=8,
    filename='',
):
    """Generate sphere w/ arguments provided by user (or default values)."""

    ### instantiate showcase
    base = ShowBase()

    ### disable mouse control over camera
    base.disableMouse()

    ### display text describing scenario

    no_of_vertices = (no_of_segments * no_of_rings) + 2
    no_of_tris = no_of_segments * no_of_rings * 2


    text_lines = [

        "Scenario X: UV sphere from user arguments (generated Geom+GeomNode)",
        "(plus white sphere of diameter 1, for comparison)",

        (
            f"radius={radius} segments={no_of_segments} rings={no_of_rings};"
            f" vertices={no_of_vertices} tris={no_of_tris}"
        ),
    ]

    if filename:

        treated_filename = str(Path(filename).with_suffix('.egg'))
        text_lines.append(f"filename={treated_filename}")

    x = 0

    for i, line_text in enumerate(reversed(text_lines)):
        
        y = .02 + i*.07
        #y = ((i+1) *.02) + (i*.02)

        OnscreenText(
            text=line_text,
            pos=(x, y),
            fg=(1.,1.,1.,1.),
            shadow=(0.,0.,0.,1.),
            parent=base.a2dBottomCenter,
        )

    ### generate main sphere

    uv_sphere_node = GeomNode('uv_sphere')

    uv_sphere_node.addGeom(

        get_uv_sphere_geom(

            radius = radius,
            no_of_segments = no_of_segments,
            no_of_rings = no_of_rings,
            vdata_name='uv_sphere',

        )

    )

    uv_sphere_np = base.render.attachNewNode(uv_sphere_node)

    uv_sphere_np.setPos(0, 0, .001)
    uv_sphere_np.setColor(0., 0., 1., 1.)
    uv_sphere_np.set_render_mode_filled_wireframe((1.,1.,1.,1.))


    ### if filename is provided, generate egg data and save as
    ### egg file as well

    if filename:

        get_uv_sphere_egg_data(

            radius = radius,
            no_of_segments = no_of_segments,
            no_of_rings = no_of_rings,
            vpool_name='uv_sphere',

        ).writeEgg(Filename(treated_filename))

    ###


    ### define and schedule procedure to move the camera

    ## preparation

    # function to cycle through 2d points representing circle in x and y axes
    next_xy = cycle(yield_2d_circle_points(360, radius * 4)).__next__

    # function to cycle through points forming a vertical line segment going
    # up and down

    int_radius = ceil(radius)

    lowest = -int_radius * 2
    highest = int_radius * 4
    factor = 100
    speed = int_radius * 4

    next_z = cycle(

        # up

        tuple(
            i/factor
            for i in range(lowest*factor, highest*factor, speed)
        )

        # down

        + tuple(
            i/factor
            for i in range(highest*factor, lowest*factor, -speed)
        )

    ).__next__


    ## defining procedure

    def spinCameraTask(task):

        base.camera.setPos(*next_xy(), next_z())
        base.camera.look_at(0, 0, radius)

        return Task.cont


    ## white sphere of radius 1 for comparison

    small_uv_sphere_node = GeomNode('small_uv_sphere')

    small_uv_sphere_node.addGeom(

        get_uv_sphere_geom(

            radius = .5,
            no_of_segments = 16,
            no_of_rings = 8,
            vdata_name='uv_sphere',

        )

    )

    small_uv_sphere_np = base.render.attachNewNode(small_uv_sphere_node)

    small_uv_sphere_np.setColor(1., 1., 1., 1.)
    small_uv_sphere_np.setPos(radius + 1, 0, radius)

    ##

    ## scheduling
    base.taskMgr.add(spinCameraTask, "SpinCameraTask")

    ### accept Escape key press to close app
    base.accept('escape', base.userExit)

    ### finally, run
    base.run()
