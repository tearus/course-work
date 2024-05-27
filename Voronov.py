import re
import matplotlib.pyplot as plt
from collections import namedtuple
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.spatial._plotutils import _adjust_bounds
from matplotlib.collections import LineCollection

Point = namedtuple('Point', 'x y')
Triangle = namedtuple('Triangle', 'v1 v2 v3')
Edge = namedtuple('Edge', 'a b')


def read_points_from_file(file_path: str) -> list[Point]:
    with open(file_path, 'r') as file:
        points = []
        for line in file.readlines():
            coordinates = line.strip()[1:-1].split(',')
            points.append(Point(int(coordinates[0]), int(coordinates[1])))
    return points


def read_triangle_coordinates(file_path: str) -> list[Triangle]:
    with open(file_path, 'r') as file:
        lines = file.readlines()

    triangles = []
    for line in lines:
        match = re.findall(r'\[(\d+), (\d+)\]', line)
        if match:
            tc = [Point(int(coord[0]), int(coord[1])) for coord in match]
            triangles.append(Triangle(tc[0], tc[1], tc[2]))
    return triangles


def get_circle_center(tri: Triangle) -> Point:
    D = ((tri.v1.x - tri.v3.x) * (tri.v2.y - tri.v3.y) - (tri.v2.x - tri.v3.x) * (tri.v1.y - tri.v3.y))
    center_x = (((tri.v1.x - tri.v3.x) * (tri.v1.x + tri.v3.x) + (tri.v1.y - tri.v3.y) * (
            tri.v1.y + tri.v3.y)) / 2 * (tri.v2.y - tri.v3.y) - (
                        (tri.v2.x - tri.v3.x) * (tri.v2.x + tri.v3.x) + (tri.v2.y - tri.v3.y) * (
                        tri.v2.y + tri.v3.y)) / 2 * (tri.v1.y - tri.v3.y)) / D
    center_y = (((tri.v2.x - tri.v3.x) * (tri.v2.x + tri.v3.x) + (tri.v2.y - tri.v3.y) * (
            tri.v2.y + tri.v3.y)) / 2 * (tri.v1.x - tri.v3.x) - (
                        (tri.v1.x - tri.v3.x) * (tri.v1.x + tri.v3.x) + (tri.v1.y - tri.v3.y) * (
                        tri.v1.y + tri.v3.y)) / 2 * (tri.v2.x - tri.v3.x)) / D
    return Point(center_x, center_y)


def common_points(tri1: Triangle, tri2: Triangle) -> list[Point]:
    result = []
    if tri1.v1 == tri2.v1 or tri1.v1 == tri2.v2 or tri1.v1 == tri2.v3:
        result.append(tri1.v1)
    if tri1.v2 == tri2.v1 or tri1.v2 == tri2.v2 or tri1.v2 == tri2.v3:
        result.append(tri1.v2)
    if tri1.v3 == tri2.v1 or tri1.v3 == tri2.v2 or tri1.v3 == tri2.v3:
        result.append(tri1.v3)
    return result


def find_common_edges(triangles: list[Triangle]) -> list[tuple[Triangle, Triangle]]:
    result = []
    for tri1 in triangles:
        for tri2 in triangles:
            points = common_points(tri1, tri2)
            if len(points) == 2:
                result.append((tri1, tri2))
    return result


def voronoi_finite_polygons_2d(vor, radius=None):
    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()

    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            new_regions.append(vertices)
            continue

        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                continue

            t = vor.points[p2] - vor.points[p1]
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:, 1] - c[1], vs[:, 0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)


def infinite_edges(vor, ax=None, **kw):
    if vor.points.shape[1] != 2:
        raise ValueError("Voronoi diagram is not 2-D")
    if kw.get('show_points', True):
        point_size = kw.get('point_size', None)
        ax.plot(vor.points[:, 0], vor.points[:, 1], '.', markersize=point_size)
    if kw.get('show_vertices', True):
        ax.plot(vor.vertices[:, 0], vor.vertices[:, 1], 'o')
    line_colors = kw.get('line_colors', 'k')
    line_width = kw.get('line_width', 1.0)
    line_alpha = kw.get('line_alpha', 1.0)
    center = vor.points.mean(axis=0)
    ptp_bound = np.ptp(vor.points, axis=0)
    finite_segments = []
    infinite_segments = []
    for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):
        simplex = np.asarray(simplex)
        if np.all(simplex >= 0):
            finite_segments.append(vor.vertices[simplex])
        else:
            i = simplex[simplex >= 0][0]

            t = vor.points[pointidx[1]] - vor.points[pointidx[0]]
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])

            midpoint = vor.points[pointidx].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            if (vor.furthest_site):
                direction = -direction
            aspect_factor = abs(ptp_bound.max() / ptp_bound.min())
            far_point = vor.vertices[i] + direction * ptp_bound.max() * aspect_factor

            infinite_segments.append([vor.vertices[i], far_point])
    ax.add_collection(LineCollection(infinite_segments, colors=line_colors, lw=line_width, alpha=line_alpha,
                                     linestyle='dashed'))
    _adjust_bounds(ax, vor.points)
    return ax.figure


def plot_all(points, triangles, vor):
    fig, ax = plt.subplots(figsize=(10, 8))

    center = []
    for tri in triangles:
        center.append(get_circle_center(tri))

    infinite_edges(vor, ax=ax, line_colors='red',
                   line_width=1, show_points=False, show_vertices=False)

    common_side_triangles = find_common_edges(triangles)
    for pair in common_side_triangles:
        center1 = get_circle_center(pair[0])
        center2 = get_circle_center(pair[1])
        plt.plot([center1.x, center2.x], [center1.y, center2.y], 'r-')
    ax.scatter([p.x for p in points], [p.y for p in points], color='blue', label='Изначальные точки')

    ax.scatter([c.x for c in center], [c.y for c in center], label='Центры окружностей', color='red')

    regions, vertices = voronoi_finite_polygons_2d(vor)
    for region in regions:
        polygon = vertices[region]
        plt.fill(*zip(*polygon), alpha=0.4)

    plt.title('Диаграмма Вороного')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    plt.legend(loc='upper left')

    plt.show()


def main():
    triangles = read_triangle_coordinates('triangle.txt')
    points = read_points_from_file('points.txt')
    vor = Voronoi(points)
    voronoi_plot_2d(vor)
    plt.title('Диаграмма Вороного')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    plt.legend(loc='upper left')

    plt.show()
    # plot_all(points, triangles, vor)


if __name__ == '__main__':
    main()
