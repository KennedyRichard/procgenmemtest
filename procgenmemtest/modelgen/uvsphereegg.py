"""Facility with function for UV sphere Egg data generation."""

### standard library imports

from collections import deque

from itertools import islice


### third-party imports

from panda3d.core import Point3D, CSZupRight

from panda3d.egg import (
    EggData,
    EggCoordinateSystem,
    EggVertexPool,
    EggPolygon,
)

### local imports
from ..points2d import yield_2d_circle_points, yield_2d_circle_points_plus



def get_uv_sphere_egg_data(
    radius,
    no_of_segments,
    no_of_rings,
    vpool_name,
):
    """Return Egg data representing UV sphere.

    Note: in order to add the geometry to the scene graph and see it,
    or save it to the disc, do as instructed below (adapted from Panda3D's
    manual).

    To load the egg file and render it, use the returned egg data along
    with panda3d.core.NodePath and panda3d.egg.loadEggData like this:

    model = NodePath(loadEggData(data))
    model.reparentTo(base.render)

    To write the egg file to disk, use the returned egg data with
    panda3d.core.Filename like this:

    data.writeEgg(Filename('name_of_your_file.egg'))
    """

    ### check error conditions

    if radius <= 0:
        raise ValueError(f"radius must be > 0, not {radius}")

    if no_of_segments < 3:
        raise ValueError(f"no_of_segments must be >= 3, not {no_of_segments}")

    if no_of_rings < 3:
        raise ValueError(f"no_of_rings must be >= 3, not {no_of_rings}")

    ### instantiate egg data and reference its addChild method

    data = EggData()
    add_to_egg_data = data.addChild

    ### define and store coordinate system

    z_up = EggCoordinateSystem()
    z_up.setValue(CSZupRight)
    add_to_egg_data(z_up)

    ### define and store vertex pool

    vpool = EggVertexPool(vpool_name)
    add_to_egg_data(vpool)

    ### reference its vertex making method
    makeNewVertex = vpool.makeNewVertex

    ### as we define the points forming the sphere, add them to the vertex
    ### pool and also define the respective faces as polygons, adding them
    ### to the egg data

    ## start by gathering data for looping while we define the structure

    # indices of first and last rings

    first_ring_index = 0
    last_ring_index = no_of_rings - 1

    # index of last point
    index_of_last_point = (

      # no of points
      (2 + (no_of_segments * no_of_rings))

      # minus one
      - 1

    )

    # points forming a segment of the circle (vertical cross-section),
    # excluding the first and last points (the points below and at the
    # top of the sphere)
    #
    # note that these are 2d points forming a circle in the xz plane

    quantity_of_points = no_of_rings + 2

    segment_points_xz = (

        islice(

            yield_2d_circle_points_plus(
                quantity=quantity_of_points,
                radius=radius,
                start_degrees=270,
                include_last=True,
                circle_proportion=.5,
                center=(0, radius)
            ),

            1,
            quantity_of_points - 1,

        )

    )

    ## create collections to assist in gathering vertices for rings

    current_ring_vertices = deque((), maxlen=no_of_segments)
    previous_ring_vertices = deque((), maxlen=no_of_segments)

    ## iterate over the segment points defined earlier, each of them
    ## representing a point in the horizontal ring that touches the
    ## segment;
    ##
    ## since the points are in the xz plane and each of them also touches
    ## a horizontal ring, we can use the x coordinate of each point to
    ## represent the radius of the circle forming the ring in the xy plane

    for ring_index, (segment_x, segment_z) in enumerate(segment_points_xz):

        ### now, we'll add points and respective faces depending on which
        ### ring we are traversing

        ## if this ring is the first one...

        if ring_index == first_ring_index:

            ## add first point, catching a reference to it
            first_vertex = makeNewVertex(Point3D(0, 0, 0))

            ## add points on first ring as you define them, catching the
            ## returned references in a deque;
            ##
            ## we define the ring as a 

            current_ring_vertices.extend(

                makeNewVertex(Point3D(ring_x, ring_y, segment_z))

                for ring_x, ring_y in yield_2d_circle_points(
                    quantity=no_of_segments,
                    radius=segment_x,
                )

            )

            ## add tris formed between each pair of points on
            ## the ring and the first point


            for _ in range(no_of_segments):

                ## create and add polygon

                poly = EggPolygon()
                add_to_egg_data(poly)

                ## add vertices forming tri;
                ##
                ## deques are quick at retrieving values from its edges; take
                ## advantage of that to grab vertices at edges to form triangle
                ## with first point;

                for vertex in (

                    first_vertex,

                    # neighboor vertices in first ring

                    current_ring_vertices[0],
                    current_ring_vertices[-1],

                ):
                    poly.addVertex(vertex)

                ## rotate deque;
                ##
                ## this amount of rotation causes the next value to end up
                ## at the deque's index 0 and what was at index 0 is now at
                ## index -1;
                current_ring_vertices.rotate(-1)

            ## move the vertices of the current ring to deque holding vertices
            ## for previous ring;
            ##
            ## since we rotate the deque by the same amount of values it holds,
            ## its vertices are in their initial positions within the deque
            previous_ring_vertices.extend(current_ring_vertices)

        ## if not the first ring...

        else:

            ## add points from this ring as you define them, catching the
            ## returned references in a deque

            current_ring_vertices.extend(

                makeNewVertex(Point3D(ring_x, ring_y, segment_z))

                for ring_x, ring_y in yield_2d_circle_points(
                    quantity=no_of_segments,
                    radius=segment_x,
                )

            )

            ## add pair of tris formed between a pair of points in the
            ## the previous ring and the respective pair of points in
            ## this ring

            for _ in range(no_of_segments):

                ## grab vertices

                vertex_a0 = previous_ring_vertices[-1]
                vertex_a1 = previous_ring_vertices[0]

                vertex_b0 = current_ring_vertices[-1]
                vertex_b1 = current_ring_vertices[0]

                ## create and add polygons

                poly_a = EggPolygon()
                add_to_egg_data(poly_a)

                poly_b = EggPolygon()
                add_to_egg_data(poly_b)

                ## add pair of tris, one in each polygon

                for vertex in (vertex_a0, vertex_b1, vertex_b0):
                    poly_a.addVertex(vertex)

                for vertex in (vertex_b1, vertex_a0, vertex_a1):
                    poly_b.addVertex(vertex)

                ## rotate deques

                previous_ring_vertices.rotate(-1)
                current_ring_vertices.rotate(-1)

            ## move the vertices of the current ring to deque holding vertices
            ## for previous ring;
            previous_ring_vertices.extend(current_ring_vertices)

            ## if we are actually on the last ring...

            if ring_index == last_ring_index:

                ## add last point (the one at the top of the sphere), catching
                ## a reference to it
                last_vertex = makeNewVertex(Point3D(0, 0, radius * 2))

                ## add tris formed between each pair of points on
                ## the last ring and the last point

                for _ in range(no_of_segments):

                    ## create and add polygon

                    poly = EggPolygon()
                    add_to_egg_data(poly)

                    ## add vertices forming tri

                    for vertex in (

                        last_vertex,
                        previous_ring_vertices[-1],
                        previous_ring_vertices[0],

                    ):
                        poly.addVertex(vertex)

                    ## rotate deque
                    previous_ring_vertices.rotate(-1)


    ### we don't need the vertices's references stored in these deques anymore

    previous_ring_vertices.clear()
    current_ring_vertices.clear()

    ### finally, return the egg data
    return data
