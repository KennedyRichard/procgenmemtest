"""Facility with function for UV sphere Geom generation."""

### standard library imports

from collections import deque

from itertools import islice


### third-party imports

from panda3d.core import (

    Geom,
    GeomVertexFormat,
    GeomVertexData,
    GeomVertexWriter,
    GeomTriangles,

)


### local imports
from ..points2d import yield_2d_circle_points, yield_2d_circle_points_plus



def get_uv_sphere_geom(
    radius,
    no_of_segments,
    no_of_rings,
    vdata_name,
):
    """Return Geom representing UV sphere.

    Note: in order to add the geometry to the scene graph and see it,
    make sure to add the Geom returned by this function to a
    panda3d.core.GeomNode instance and add that instance to the scene graph.

    Like this:

    node = GeomNode('node_name')
    node.addGeom(generated_geom)
    base.render.attach_new_node(node)
    """

    ### check error conditions

    if radius <= 0:
        raise ValueError(f"radius must be > 0, not {radius}")

    if no_of_segments < 3:
        raise ValueError(f"no_of_segments must be >= 3, not {no_of_segments}")

    if no_of_rings < 3:
        raise ValueError(f"no_of_rings must be >= 3, not {no_of_rings}")

    ### create vertex data

    vdata = GeomVertexData(
        vdata_name,
        GeomVertexFormat.getV3(),
        Geom.UHStatic,
    )

    # we'll need this not only for the next call, but later as well
    no_of_points = 2 + (no_of_segments * no_of_rings)

    vdata.uncleanSetNumRows(no_of_points)

    ### create writer to add points, referencing the method to add them
    add_point = GeomVertexWriter(vdata, 'vertex').addData3

    ### create primitive to hold faces (triangles), referencing the method
    ### to add the indices of the vertices forming the triangles

    triangle_primitives_holder = GeomTriangles(Geom.UHStatic)
    add_tri_points_indices = triangle_primitives_holder.addVertices

    ### as we define the points forming the sphere, add them to the vertex
    ### data table and the respective faces to the primitive holder instance

    ## start by gathering data for looping while we define the structure

    # indices of first and last rings

    first_ring_index = 0
    last_ring_index = no_of_rings - 1

    # index of last point
    index_of_last_point = no_of_points - 1

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

    ## create collections to assist in gathering points for rings

    current_ring_indices = deque((), maxlen=no_of_segments)
    previous_ring_indices = deque((), maxlen=no_of_segments)

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

            ## add first point
            add_point((0, 0, 0))

            ## add points on first ring as you define them;
            ##
            ## we define the ring as a 

            for ring_x, ring_y in yield_2d_circle_points(
                quantity=no_of_segments,
                radius=segment_x,
            ):
                add_point((ring_x, ring_y, segment_z))

            ## add tris formed between each pair of points on
            ## the ring and the first point

            current_ring_indices.extend(range(1, no_of_segments + 1))

            for _ in range(no_of_segments):

                ## add indices of vertices forming tri;
                ##
                ## deques are quick at retrieving values from its edges; take
                ## advantage of that to grab indices at edges to form triangle
                ## with first point (index 0 in vertex data collection);

                add_tri_points_indices(

                    # index of first point
                    0,

                    # indices of neighboor points in first ring

                    current_ring_indices[0],
                    current_ring_indices[-1],

                )

                ## rotate deque;
                ##
                ## this amount of rotation causes the next value to end up
                ## at the deque's index 0 and what was at index 0 is now at
                ## index -1;
                current_ring_indices.rotate(-1)

            ## move the indices of the current ring to deque holding indices
            ## for previous ring;
            ##
            ## since we rotate the deque by the same amount of values it holds,
            ## its indices are in their initial positions within the deque
            previous_ring_indices.extend(current_ring_indices)

        ## if not the first ring...

        else:

            ## add points from this ring as you define them

            for ring_x, ring_y in yield_2d_circle_points(
                quantity=no_of_segments,
                radius=segment_x,
            ):
                add_point((ring_x, ring_y, segment_z))

            ## add pair of tris formed between a pair of points in the
            ## the previous ring and the respective pair of points in
            ## this ring

            first_index_on_ring = (

                (
                    ring_index
                    * no_of_segments

                ) + 1 # offset to compensate for first point at the bottom
                      # of the sphere (0, 0, 0)
            )

            current_ring_indices.extend(

                range(
                    first_index_on_ring,
                    first_index_on_ring + no_of_segments,
                )

            )

            for _ in range(no_of_segments):

                ## grab vertices indices

                index_a0 = previous_ring_indices[-1]
                index_a1 = previous_ring_indices[0]

                index_b0 = current_ring_indices[-1]
                index_b1 = current_ring_indices[0]

                ## add pair of tris

                add_tri_points_indices(index_a0, index_b1, index_b0)
                add_tri_points_indices(index_b1, index_a0, index_a1)

                ## rotate deques

                previous_ring_indices.rotate(-1)
                current_ring_indices.rotate(-1)

            ## move the indices of the current ring to deque holding indices
            ## for previous ring;
            previous_ring_indices.extend(current_ring_indices)

            ## if we are actually on the last ring...

            if ring_index == last_ring_index:

                ## add last point (the one at the top of the sphere)
                add_point((0, 0, radius * 2))

                ## add tris formed between each pair of points on
                ## the last ring and the last point

                for _ in range(no_of_segments):

                    ## add tri

                    add_tri_points_indices(

                        index_of_last_point,
                        previous_ring_indices[-1],
                        previous_ring_indices[0],

                    )

                    ## rotate deque
                    previous_ring_indices.rotate(-1)


    ### we don't need the indices stored in these deques anymore

    previous_ring_indices.clear()
    current_ring_indices.clear()

    ### finally, instantiate and return the geom after adding
    ### the primitives holder

    geom = Geom(vdata)
    geom.addPrimitive(triangle_primitives_holder)

    return geom
