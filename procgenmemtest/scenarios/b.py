"""Facility to run scenario B.

In this scenario, a Geom instance representing a UV sphere is
procedurally generated added to multiple instances of GeomNode.
"""

### standard library import
from itertools import cycle


### third-party imports

from direct.showbase.ShowBase import ShowBase

from direct.task import Task

from direct.gui.OnscreenText import OnscreenText

from panda3d.core import ModelPool, GeomNode


### local imports

from ..modelgen.uvspheregeom import get_uv_sphere_geom

from ..points2d import yield_2d_circle_points



def run_scenario():
    """Generate Geom and feed it to multiple GeomNode instances."""

    ### define number of spheres to be instantiated in total
    NO_OF_SPHERES = 250

    ### instantiate showcase
    base = ShowBase()

    ### disable mouse control over camera
    base.disableMouse()

    ### display text describing scenario

    OnscreenText(
        text="Scenario B: generated Geom shared among multiple GeomNodes",
        pos=(0, .02),
        fg=(1.,1.,1.,1.),
        shadow=(0.,0.,0.,1.),
        parent=base.a2dBottomCenter,
    )

    ### create group wherein to attach sphere in the scene graph
    sphere_group = base.render.attachNewNode('sphere_group')

    ### generate UV sphere Geom

    SPHERE_RADIUS = 5

    MULTIPLIER = 10
    NO_OF_SEGMENTS = 16
    NO_OF_RINGS = 8

    sphere_geom = get_uv_sphere_geom(
        radius=SPHERE_RADIUS,
        no_of_segments=NO_OF_SEGMENTS * MULTIPLIER,
        no_of_rings=NO_OF_RINGS * MULTIPLIER,
        vdata_name='uv_sphere_vertices',
    )

    ### load sphere model NO_OF_SPHERES times (after the first, the subsequent
    ### instances should all use the same geometry from the model pool)

    cam_xy_move_radius = NO_OF_SPHERES * 3

    ## iterate over points forming a 2D sphere in the xy plane, placing a
    ## sphere in each point

    z = .1

    for sphere_index, (x, y) in enumerate(

        yield_2d_circle_points(
            quantity=NO_OF_SPHERES,
            radius=cam_xy_move_radius,
        )

    ):

        node = GeomNode(f'node_name_{sphere_index:>03}')
        node.addGeom(sphere_geom)

        uv_sphere_np = sphere_group.attach_new_node(node)

        uv_sphere_np.setPos(x, y, z)
        uv_sphere_np.setColor(0., 0., 1., 1.)
        uv_sphere_np.set_render_mode_filled_wireframe((1.,1.,1.,1.))

    ### define and schedule procedure to move the camera

    ## preparation

    # function to cycle through 2D points representing circle in xy plane

    next_xy = cycle(
        yield_2d_circle_points(cam_xy_move_radius*20, cam_xy_move_radius + 20)
    ).__next__

    # function to cycle through points forming a vertical line segment going
    # up and down on the z axis;

    lowest = -SPHERE_RADIUS * 1
    highest = SPHERE_RADIUS * 2
    factor = 100
    speed = SPHERE_RADIUS * 2

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
        base.camera.look_at(0, 0, SPHERE_RADIUS)

        return Task.cont

    ##
    print()
    print('Children in sphere_group:', sphere_group.getNumChildren())
    print()
    ModelPool.list_contents()

    ## scheduling
    base.taskMgr.add(spinCameraTask, "SpinCameraTask")

    ### accept Escape key press to close app
    base.accept('escape', base.userExit)

    ### finally, run
    base.run()
