"""Facility with functions to generate 2d points."""

### standard library imports
from math import tau, sin, cos



def yield_2d_circle_points(quantity, radius, center=(0, 0)):
    """Yield points of a 2D circle."""

    ### assign variables to each coordinate of the center point
    xc, yc = center

    for point_index in range(quantity):

        angle_radians = (

            # percentage of circumference where to find point
            (point_index / quantity)

            # constant to give us angle based on percentage above
            * tau

        )

        x = radius * cos(angle_radians)
        y = radius * sin(angle_radians)

        yield (x + xc, y + yc)


def yield_2d_circle_points_plus(

    quantity,
    radius,
    start_degrees=0,
    include_last=False,
    circle_proportion=1.0, # 1.0 for full circle, 0.5 for half-circle, etc.
    center=(0, 0),

):
    """Yield points of a 2D circle with more parameters for extra control."""

    ### calculate start angle in radians based on start degree

    tau_percentage  = (start_degrees % 360) / 360
    start_angle = tau_percentage * tau

    ### assign variables to each coordinate of the center point
    xc, yc = center

    tau_proportion = circle_proportion * tau

    divisor = quantity

    if include_last:
        divisor -= 1

    for point_index in range(quantity):

        angle_radians = (

            # percentage of circumference where to find point
            (point_index / divisor)

            # constant to give us angle based on percentage above
            * tau_proportion

        ) + start_angle

        if angle_radians > tau:
            angle_radians -= tau

        x = radius * cos(angle_radians)
        y = radius * sin(angle_radians)

        yield (x + xc, y + yc)
