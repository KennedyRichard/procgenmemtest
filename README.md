
# procgenmemtest

This repository consists of a small experiment by me ([Kennedy](https://kennedyrichard.com), born in 1990) to determine which is the best method to save memory when reusing procedurally generated geometry. In it, we generate geometry or load the equivalent pre-generated .egg file representing a UV sphere to check how much RAM is used when we replicate such geometry using different scenarios and their methods.

![UV sphere displayed in scenario X (demo/playground)](https://i.imgur.com/6oMyDQY.png)

> [!WARNING]
> The Python code in this repo is supposed to be executed from the top-level directory of this repository like this: 
>
> `python3 -m procgenmemtest [args]`
>
> The `-m` switch is required in order for the interpreter to execute `procgenmemtest` as a package. It looks for the `__main__.py` entry point inside the `procgenmemtest` folder and executes it, allowing the interpreter to find the relative imports inside the package. Trying to execute `__main__.py` from within the procgenmemtest and without the `-m` flag wouldn't work.

This code is in the public domain using [The Unlicense](https://unlicense.org/) license, all plain Python code that relies solely on Panda3D and the standard library. Feel free to use it as you see fit. The `modelgen/uvspheregeom.py` module, the one used to generate a Geom representing a UV sphere, may be useful if you want to generate UV spheres, and it only relies on 02 small functions from another module, kept separate only for the sake of organization. The `modelgen/uvsphereegg.py` module does the same, but generates the equivalent EggData instead.


## Scenarios and how to execute them

05 simple scenarios are presented:

- A: a `uv_sphere.egg` model is loaded, then instantiated several times,
all models added to the scene graph.
- B: a Geom instance representing a UV shpere is procedurally generated,
then fed to several GeomNode instances that are added to the scene graph.
- A1 and B1: variations of scenarios A and B respectively, which load/create
a single model using the methods A or B, but instead duplicate the model
via instancing.
- X: this is the default scenario and simplest one: just a playground/test demo that shows a single sphere defined with arguments provided by the user (another sphere which has a diameter of 1 unit is also shown for comparison).

Except for the scenario X, all other scenarios are supposed to be executed like this (depending on your machine, the framerate might be very low, due to the high number of geometry to draw, but that's okay, we are only interested in RAM usage in this experiment):

```
python3 -m procgenmemtest --scenario A
python3 -m procgenmemtest --scenario A1
python3 -m procgenmemtest --scenario B
python3 -m procgenmemtest --scenario B1
```

Scenario X can be executed with additional values provided by the user (or default values for the ones that are ommited). These commands are equivalent and will run scenario X with default values:

```
python3 -m procgenmemtest
python3 -m procgenmemtest --scenario X
```

This is the scenario depicted in the image at the top of this document and serves solely as a demo/playground so users can test the procedural generation of a UV sphere.

Optionally, you can specify additional arguments to define the geometry. These include the radius of the sphere, the number of segments (vertical edge loops), the number of rings (horizontal edge loops) and a multiplier that is applied to the number of segments and rings. This is an example (the values used here are also the default ones):

```
python3 -m procgenmemtest --radius 1.0 --segments 16 --rings 8 --multiplier 1
```

If you provide a filename, we'll also save an egg file with the UV sphere generated with the specified values:

```
python3 -m procgenmemtest --filename my_uvsphere.egg
```

When in doubt, you can simply use `--help` or `-h` for an explanation of all available arguments:

```
python3 -m procgenmemtest --help
```

## Discussion

The scenario X is just for showing the generation capabilities. For the sake of this experiment on memory usage though, the relevant scenarios are the other ones, A, A1, B and B1.

As this is a memory usage test, we are not worried about framerate or the speed with which the geometry is generated/loaded/replicated (either with or without instancing).

In each relevant scenario (A, A1, B, B1), the user is supposed to check its system's task manager or equivalent software to see how much memory the Panda3D app is using.

Both scenarios use several instances of the same sphere geometry. Such geometry has a high number of triangles (25600), in order for the difference in memory used to be easier to notice. Such sphere is replicated 250 times using the different methods in each scenario.  Even so, such face density is still not that high as far as RAM usage goes, but it was enough to clearly perceive significant differences between some of the scenarios.

For the sake of simplicity, the geometry used was generated with no materials/textures/shading, only the vertices and faces they form. In order for us to see them in detail, once added they are all given colors for both their volume and wireframe.

Although geometry can be procedurally generated both as a Geom instance or as an EggData instance, we only explored the Geom approach here, since earlier tests showed us that the EggData approach was slower. This is to be expected, since the EggData has to be converted into Geom(s) in the end anyway to be loaded, requiring additional steps and more memory.

Even so, we included code for generating spheres using both approaches, for various reasons. First, for the sake of completeness, but also because the EggData approach has its own usages in other contexts (specially to create/store models for exchange between different Panda3D versions).

Additionally, the function that employs the EggData approach was also the one used to generate the sphere's egg file used in scenarios A and A1, and it is used in scenario X to save a new egg file. That is, it is included in case you want to generate and save your own egg data for inspection or fun.

As we said before, this generated EggData could also be loaded as a model, but again, we ignored that possibility, because for that purpose the Geom approach is undeniably faster (at least in my machine?!). Moreover, this process of loading EggData generated on the spot also incurs a spike in RAM usage, which also contributed for related scenarios to be discarded.


## Results and conclusions

I initially thought 250 instances with 25600 faces each would use quite a lot of RAM, regardless of the scenario, but I was mistaken.

Some of the scenarios barely added 5 MB on top of the 139 MB of RAM used by a bare window initialized with `base = ShowBase()` in my machine. The worst scenario just barely added a bit more than 10 MB.

Even so, the differences between the scenarios were still enough for me to draw conclusions about their memory efficiency. In my machine, the ranking, from the scenario that used less RAM (best) to the one that used more (worst), was:

1. B1 (~5 extra MB)
1. B (~5 extra MB)
1. A1(~12 extra MB)
1. A (~12 extra MB)

However, the A1 and B1 variants (the ones relying on instancing) were not significantly better than their counterparts (A and B). Scenarios B and B1, the ones where a single Geom instances was generated, were significantly better than the A and A1, though.

Taking all that into consideration, my conclusions were that:

1. Reusing a generated Geom uses less RAM than the reuse of the equivalent pre-generated `.egg` file that is cached in the ModelPool.
1. Despite instancing using slightly less RAM, the difference was so tiny as to be insignificant in my opinion. This means that, for generated geometry, the extra setup and management required by instancing is probably not worth it. That is, it is better to keep references to the generated geom and reuse them in additional GeomNode instances created.

That is not to say that instancing isn't valuable. The true strength of instancing is probably for instancing actors (direct.actor.Actor.Actor), as it is taught in the manual, scenario in which it spares the machine needless recalculations related to the animation of the geometry.

This is only a very simple experiment and I don't consider myself an experienced Panda3D user. So, please, take all of this with a grain of salt and, preferably, try these scenarios A, A1, B, B1 for yourself in your own machine as well and draw your own conclusions. If you have valuable feedback or anything else relevant to add, I'll be glad to review and accept PRs, but keep in mind this repository is meant as a one-off experiment, not a project I intend to maintain indefinitely.

I also created a [post on Panda3D's forum](https://discourse.panda3d.org/t/experiment-comparing-memory-usage-when-reusing-procedurally-generated-models/31381) for those willing to discuss this experiment and its results further.
