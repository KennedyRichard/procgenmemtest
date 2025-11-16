"""procgenmemtest: scenarios for memory usage with/without real-time procgen

05 simple scenarios are presented:

X: this is just a playground/test demo.

A: a uv_sphere.egg model is loaded, then instantiated several times,
all models added to the scene graph.

B: a Geom instance representing a UV shpere is procedurally generated,
then fed to several GeomNode instances that are added to the scene graph.

A1 and B1: variations of scenarios A and B respectively, which load/create
a single model using the methods A or B, but instead duplicate the model
via instancing.

As this is a memory usage test, we are not worried about framerate or
the speed with which the geometry is generated/loaded/replicated (either
with or without instancing).

In each scenario, the user is supposed to check its system's task manager
or equivalent software to see how much memory the Panda3D app is using.

Both scenarios use several instances of the same sphere geometry. Such
geometry has a high number of triangles (25600), in order for the
difference in memory used to be easier to notice. Such sphere is
replicated 250 times using the different methods in each scenario.
Even so, such face density is still not that high as far as RAM usage
goes, but it was enough to clearly perceive significant differences
between some of the scenarios.

For the sake of simplicity, the geometry used was generated with no
materials/textures/shading, only the vertices and faces they form. In
order for us to see them in detail, once added, they are all given colors
for both their volume and wireframe.

Although geometry can be procedurally generated both as a Geom instance
or as an EggData instance, we only explored the Geom approach here, since
earlier tests showed us that the EggData approach was way, way slower.
This is to be expected, since the EggData has to be converted into Geom(s)
in the end anyway to be loaded, requiring additional steps and more memory,
as well as other factors we didn't consider.

Even so, we included code for generating spheres using both approaches,
for various reasons. First, for the sake of completeness, but also because
the EggData approach has its own usages in other contexts (specially to
create/store models for exchange between different Panda3D versions).

Additionally, the function that employs the EggData approach was also the
one used to generate the sphere's egg file used in scenarios A and A1, and
it is used in scenario X to save a new egg file. That is, it is included in
case you want to generate and save your own egg data for inspection or fun.

As we said before, this generated EggData could also be loaded as a model,
but again, we ignored that possibility, because for that purpose the Geom
approach is undeniably faster (at least in my machine?!). Moreover, this
process of loading EggData generated on the spot also incurs a spike in
RAM usage, which also contributed for related scenarios to be discarded.
"""

### standard library import
from argparse import ArgumentParser


### local import
from . import scenarios



VALID_SCENARIOS = scenarios.SCENARIO_MAP.keys()
SCENARIO_NAMES = ', '.join(map(repr, VALID_SCENARIOS))


def main(
    scenario_name='A',
    radius = 1.0,
    no_of_segments = 16,
    no_of_rings = 8,
    filename = '',
):
    
    if scenario_name not in VALID_SCENARIOS:
        raise ValueError(f"Scenario must be one of ({SCENARIO_NAMES})")

    run_scenario = (

        getattr(

            # scenario
            getattr(scenarios, scenario_name.lower()),

            # run_scenario function
            'run_scenario',
        )

    )

    print(f"Running scenario {scenario_name}")
    print()

    if scenario_name == 'X':

        run_scenario(

            radius=radius,
            no_of_segments=no_of_segments,
            no_of_rings=no_of_rings,
            filename=filename,

        )

    else:
        run_scenario()



if __name__ == '__main__':
    
    parser = ArgumentParser(
        prog="procgenmemtest",
        description=(
            "Scenarios for memory usage with/without real-time procgen"
        )
    )

    add_argument = parser.add_argument

    scenario_x_help_text = (
        f"Scenario to execute (one of {SCENARIO_NAMES})"
        " (other arguments only used in scenario X)"
    )

    for arg_name, default, help_text in (
        ('scenario', 'X', scenario_x_help_text),
        ('radius', 1.0, "Sphere radius (positive number)"),
        ('segments', 16, "Number of vertical segments (integer >=3)"),
        ('rings', 8, "Number of horizontal segments (integer >=3)"),
        ('multiplier', 1, "Multiplies segments and rings (integer >= 1)"),
        ('filename', '', "If not empty, saves Egg file in that location."),
    ):

        add_argument(
            f'--{arg_name}',
            type=type(default),
            default=default,
            help=help_text + f" (default: {default})",
        )

    parsed_args = parser.parse_args()

    scenario = parsed_args.scenario

    if scenario == 'X':

        multiplier = parsed_args.multiplier

        error_msg = "Multiplier must be integer >= 1"

        if type(multiplier) != int:
            raise TypeError(error_message)

        elif multiplier < 1:
            raise ValueError(error_message)

        extra_kwargs = dict(
            radius = parsed_args.radius,
            no_of_segments = parsed_args.segments * multiplier,
            no_of_rings = parsed_args.rings * multiplier,
            filename = parsed_args.filename,
        )

    else:
        extra_kwargs = {}

    main(scenario_name=scenario, **extra_kwargs)
