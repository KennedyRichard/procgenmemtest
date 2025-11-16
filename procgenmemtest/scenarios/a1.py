"""Facility to run scenario A1.

In this scenario, an Egg file representing a UV sphere is loaded once
and replicated multiple times via instancing.
"""

### standard library import
from itertools import cycle


### third-party imports

from direct.showbase.ShowBase import ShowBase

from direct.task import Task

from direct.gui.OnscreenText import OnscreenText

from panda3d.core import ModelPool


### local imports
from ..points2d import yield_2d_circle_points



def run_scenario():
    """Load Egg file once, replicate via instancing."""

    ### define number of spheres to be instantiated in total
    NO_OF_SPHERES = 250

    ### instantiate showcase
    base = ShowBase()

    ### disable mouse control over camera
    base.disableMouse()

    ### display text describing scenario

    OnscreenText(
        text="Scenario A1: single Egg file replicated via instancing",
        pos=(0, .02),
        fg=(1.,1.,1.,1.),
        shadow=(0.,0.,0.,1.),
        parent=base.a2dBottomCenter,
    )

    ### create group wherein to attach sphere in the scene graph
    sphere_group = base.render.attachNewNode('sphere_group')

    ### load and set render mode to sphere model

    model_np = base.loader.loadModel('uv_sphere.egg')

    model_np.setColor(0., 0., 1., 1.)
    model_np.set_render_mode_filled_wireframe((1.,1.,1.,1.))

    ### iterate over points forming a 2D sphere in the xy plane, placing
    ### instancing replicas in each point

    cam_xy_move_radius = NO_OF_SPHERES * 3

    z = .1

    for sphere_index, (x, y) in enumerate(

        yield_2d_circle_points(
            quantity=NO_OF_SPHERES,
            radius=cam_xy_move_radius,
        )

    ):

        uv_sphere_np = (
            sphere_group.attachNewNode(
                f'instancing_replica_{sphere_index:>03}'
            )
        )

        uv_sphere_np.setPos(x, y, z)

        model_np.instance_to(uv_sphere_np)

    ### from this point on we assume the sphere's radius is 5, in our
    ### calculations, which is the value used when generating the geometry,
    ### both in real-time and for the .egg file
    SPHERE_RADIUS = 5

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
    print('children in sphere_group:', sphere_group.getNumChildren())
    print()
    ModelPool.list_contents()

    ## scheduling
    base.taskMgr.add(spinCameraTask, "SpinCameraTask")

    ### accept Escape key press to close app
    base.accept('escape', base.userExit)

    ### finally, run
    base.run()
