"""Original layered 3D symbols; Blender-only, no external model downloads."""

import bpy, math
from mathutils import Vector

COLORS = {
    "white": (0.88, 0.94, 1, 1),
    "navy": (0.015, 0.055, 0.11, 1),
    "orange": (1, 0.28, 0.025, 1),
    "gold": (1, 0.65, 0.04, 1),
    "blue": (0.04, 0.3, 0.58, 1),
    "red": (0.75, 0.045, 0.025, 1),
    "green": (0.015, 0.28, 0.11, 1),
    "glass": (0.025, 0.12, 0.19, 1),
    "metal": (0.3, 0.4, 0.47, 1),
    "black": (0.018, 0.025, 0.03, 1),
}


def material(n, c):
    m = bpy.data.materials.get(n)
    if not m:
        m = bpy.data.materials.new(n)
    m.diffuse_color = COLORS[c] if isinstance(c, str) else c
    return m


def bind(o, n, parent, c):
    o.name = n
    o.parent = parent
    color_key = c if isinstance(c, str) else tuple(float(q) for q in c)
    o.data.materials.append(material("symbol_" + str(color_key), c))
    return o


def cube(parent, n, loc, scale, c, bevel=0.05):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bind(bpy.context.object, n, parent, c)
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        b = o.modifiers.new("Soft manufactured edges", "BEVEL")
        b.width = bevel
        b.segments = 2
        o.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return o


def sphere(parent, n, loc, scale, c):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=20, ring_count=12, radius=1, location=loc
    )
    o = bind(bpy.context.object, n, parent, c)
    o.scale = scale
    for f in o.data.polygons:
        f.use_smooth = True
    return o


def cylinder(parent, n, loc, r, depth, c, rotation=(0, 0, 0), vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=r, depth=depth, location=loc
    )
    o = bind(bpy.context.object, n, parent, c)
    o.rotation_euler = rotation
    return o


def mesh(parent, n, vs, fs, c):
    d = bpy.data.meshes.new(n)
    d.from_pydata(vs, [], fs)
    o = bpy.data.objects.new(n, d)
    bpy.context.collection.objects.link(o)
    bind(o, n, parent, c)
    return o


def empty(n):
    o = bpy.data.objects.new(n, None)
    bpy.context.collection.objects.link(o)
    return o


def make_model(kind, name=None):
    root = empty(name or kind)
    if kind == "plane":
        sphere(root, "fuselage", (0, 0, 0.28), (0.13, 0.88, 0.13), "white")
        sphere(root, "cockpit", (0, 0.65, 0.34), (0.105, 0.17, 0.065), "glass")
        for side in [-1, 1]:
            mesh(
                root,
                "swept_wing",
                [
                    (side * 0.08, 0.18, 0.28),
                    (side * 0.89, -0.25, 0.27),
                    (side * 0.88, -0.43, 0.27),
                    (side * 0.08, -0.17, 0.28),
                ],
                [(0, 1, 2, 3)],
                "white",
            )
            mesh(
                root,
                "tailplane",
                [
                    (side * 0.06, -0.57, 0.29),
                    (side * 0.34, -0.77, 0.31),
                    (side * 0.32, -0.85, 0.31),
                    (side * 0.05, -0.72, 0.29),
                ],
                [(0, 1, 2, 3)],
                "orange",
            )
            sphere(
                root, "engine", (side * 0.38, -0.08, 0.17), (0.085, 0.22, 0.08), "metal"
            )
            for y in [-0.5, -0.35, -0.2, -0.05, 0.1, 0.25, 0.4]:
                sphere(
                    root,
                    "cabin_window",
                    (side * 0.122, y, 0.315),
                    (0.012, 0.025, 0.027),
                    "glass",
                )
        mesh(
            root,
            "tail_fin",
            [(0, -0.8, 0.28), (0, -0.72, 0.66), (0, -0.47, 0.29)],
            [(0, 1, 2)],
            "orange",
        )
    elif kind == "train":
        for j in range(3):
            y = -j * 0.75
            cube(root, f"car_{j}_body", (0, y, 0.2), (0.32, 0.68, 0.3), "white", 0.08)
            cube(
                root,
                f"car_{j}_orange",
                (0, y, 0.18),
                (0.33, 0.69, 0.085),
                "orange",
                0.025,
            )
            cube(root, f"car_{j}_roof", (0, y, 0.37), (0.27, 0.55, 0.07), "metal", 0.03)
            if j == 0:
                cube(
                    root,
                    "front_glazing",
                    (0, y + 0.32, 0.27),
                    (0.26, 0.025, 0.12),
                    "glass",
                    0.02,
                )
            for side in [-1, 1]:
                for wy in [-0.21, -0.07, 0.07, 0.21]:
                    cube(
                        root,
                        "window",
                        (side * 0.165, y + wy, 0.27),
                        (0.015, 0.095, 0.075),
                        "glass",
                        0.01,
                    )
                for wy in [-0.22, 0.22]:
                    cylinder(
                        root,
                        "wheel",
                        (side * 0.12, y + wy, 0.065),
                        0.065,
                        0.055,
                        "black",
                        (0, math.pi / 2, 0),
                    )
            if j < 2:
                cube(
                    root,
                    "coupler",
                    (0, y - 0.375, 0.12),
                    (0.055, 0.1, 0.045),
                    "black",
                    0,
                )
    elif kind in ["ship", "boat"]:
        vs = [
            (-0.25, -0.65, 0.08),
            (0.25, -0.65, 0.08),
            (0.27, 0.42, 0.08),
            (0, 0.78, 0.08),
            (-0.27, 0.42, 0.08),
            (-0.19, -0.57, -0.12),
            (0.19, -0.57, -0.12),
            (0.2, 0.4, -0.12),
            (0, 0.65, -0.12),
            (-0.2, 0.4, -0.12),
        ]
        mesh(
            root,
            "hull",
            vs,
            [
                (0, 1, 2, 3, 4),
                (0, 5, 6, 1),
                (1, 6, 7, 2),
                (2, 7, 8, 3),
                (3, 8, 9, 4),
                (4, 9, 5, 0),
                (5, 9, 8, 7, 6),
            ],
            "navy",
        )
        cube(root, "waterline", (0, -0.03, -0.025), (0.44, 1.15, 0.1), "red", 0.03)
        for y in [-0.22, 0.04, 0.3]:
            for x in [-0.125, 0.125]:
                for z in [0.16, 0.3]:
                    cube(
                        root,
                        "container",
                        (x, y, z),
                        (0.22, 0.23, 0.13),
                        "orange" if (y + x + z) > 0.2 else "blue",
                        0.008,
                    )
        cube(root, "bridge", (0, -0.49, 0.28), (0.4, 0.22, 0.4), "white", 0.015)
        cube(root, "bridge_glass", (0, -0.48, 0.39), (0.42, 0.21, 0.065), "glass", 0.01)
        cylinder(root, "mast", (0, -0.49, 0.67), 0.015, 0.4, "white")
        for side in [-1, 1]:
            o = cube(
                root,
                "wake",
                (side * 0.23, -0.89, -0.12),
                (0.035, 0.5, 0.012),
                "white",
                0,
            )
            o.rotation_euler.z = side * 0.25
    elif kind == "car":
        cube(root, "body", (0, 0, 0.17), (0.42, 0.8, 0.22), "orange", 0.08)
        cube(root, "cabin", (0, -0.04, 0.34), (0.33, 0.4, 0.2), "glass", 0.06)
        for x in [-0.21, 0.21]:
            for y in [-0.24, 0.24]:
                cylinder(
                    root, "wheel", (x, y, 0.09), 0.1, 0.07, "black", (0, math.pi / 2, 0)
                )
    elif kind == "track":
        for x in [-0.15, 0.15]:
            cube(root, "rail", (x, 0, 0.05), (0.025, 2, 0.04), "metal", 0)
        for i in range(13):
            cube(
                root,
                "sleeper",
                (0, -0.95 + i * 0.15, 0.015),
                (0.46, 0.06, 0.04),
                "black",
                0,
            )
    elif kind in ["building", "city", "factory"]:
        layout = (
            [(0, 0, 0.9, 0.45, 0.4)]
            if kind == "building"
            else [
                (-0.5, 0, 0.7, 0.38, 0.4),
                (0, 0.2, 1.3, 0.4, 0.45),
                (0.5, 0, 0.9, 0.38, 0.4),
                (-0.3, -0.5, 0.35, 0.4, 0.32),
                (0.3, -0.5, 0.5, 0.42, 0.32),
            ]
        )
        for i, (x, y, h, w, d) in enumerate(layout):
            cube(root, "building", (x, y, h / 2), (w, d, h), "white", 0.025)
            cube(
                root,
                "glass_facade",
                (x, y - d * 0.51, h * 0.55),
                (w * 0.86, 0.012, h * 0.7),
                "glass",
                0.005,
            )
            for z in range(1, int(h / 0.1)):
                cube(
                    root,
                    "floor_line",
                    (x, y - d * 0.53, z * 0.1),
                    (w, 0.018, 0.012),
                    "gold",
                    0,
                )
        if kind == "factory":
            for x in [-0.5, 0, 0.5]:
                cylinder(root, "chimney", (x, 0.5, 0.7), 0.075, 1.4, "red")
    elif kind in ["dam", "reservoir"]:
        cube(root, "water", (0, 0.4, 0.025), (1.6, 0.9, 0.04), "blue", 0.1)
        for i in range(9):
            x = -0.8 + i * 0.2
            y = -0.1 + 0.13 * (1 - (x / 0.85) ** 2)
            cube(root, "concrete_dam", (x, y, 0.28), (0.22, 0.17, 0.55), "white", 0.01)
        for x in [-0.55, 0, 0.55]:
            cube(root, "spillway", (x, -0.23, 0.12), (0.08, 0.35, 0.025), "blue", 0)
    elif kind == "tree":
        cylinder(root, "trunk", (0, 0, 0.2), 0.055, 0.4, (0.22, 0.1, 0.025, 1))
        for z, r in [(0.38, 0.25), (0.56, 0.21), (0.73, 0.15)]:
            bpy.ops.mesh.primitive_cone_add(
                vertices=10, radius1=r, radius2=0, depth=0.36, location=(0, 0, z)
            )
            bind(bpy.context.object, "foliage", root, "green")
    elif kind == "mountain":
        mesh(
            root,
            "peak",
            [
                (-0.6, -0.4, 0),
                (0.6, -0.4, 0),
                (0.5, 0.45, 0),
                (-0.45, 0.5, 0),
                (0, 0, 1),
            ],
            [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)],
            "green",
        )
    elif kind == "pin":
        sphere(root, "head", (0, 0, 0.5), (0.2, 0.2, 0.2), "red")
        cylinder(root, "stem", (0, 0, 0.2), 0.035, 0.4, "gold")
    else:
        raise ValueError("Unknown model " + kind)
    return root


def make_arrow(name, style, mat):
    """Layered arrow heads pointing +Y; triangle matches the default route head."""
    root = empty(name)
    if style == "triangle":
        o = mesh(
            root,
            "arrow_head",
            [(-0.13, -0.14, 0), (0.13, -0.14, 0), (0, 0.19, 0), (0, 0, 0.06)],
            [(0, 1, 2), (0, 3, 1), (1, 3, 2), (2, 3, 0)],
            mat.diffuse_color,
        )
    elif style in ["chevron", "diamond"]:
        vs = (
            [(-0.13, -0.14, 0), (0, -0.035, 0), (0.13, -0.14, 0), (0, 0.19, 0)]
            if style == "chevron"
            else [(-0.13, 0, 0), (0, -0.19, 0), (0.13, 0, 0), (0, 0.19, 0)]
        )
        o = mesh(root, "arrow_" + style, vs, [(0, 1, 3), (1, 2, 3)], mat.diffuse_color)
        solid = o.modifiers.new("Head depth", "SOLIDIFY")
        solid.thickness = 0.04
    elif style == "double":
        for y in [0, -0.22]:
            o = mesh(
                root,
                "arrow_head",
                [
                    (-0.13, y - 0.14, 0),
                    (0.13, y - 0.14, 0),
                    (0, y + 0.19, 0),
                    (0, y, 0.06),
                ],
                [(0, 1, 2), (0, 3, 1), (1, 3, 2), (2, 3, 0)],
                mat.diffuse_color,
            )
    else:
        raise ValueError("Unknown arrowhead " + style)
    return root
