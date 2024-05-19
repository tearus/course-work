import matplotlib.pyplot as plt
import numpy as np
from Delaunay import Graph, Point, Edge, Triangle
import random
from scipy.spatial import Delaunay


def plot_graph(graph, triangle_type="custom", color=None):
    fig, ax = plt.subplots()

    # Рисуем точки
    for point in graph._points:
        ax.scatter(*point.pos(), color='blue')

    # Рисуем ребра
    for edge in graph._edges:
        x_coords = [edge._a.pos()[0], edge._b.pos()[0]]
        y_coords = [edge._a.pos()[1], edge._b.pos()[1]]
        ax.plot(x_coords, y_coords, color=color)

    # Рисуем треугольники
    if triangle_type == "custom":
        for triangle in graph._triangles:
            x_coords = [triangle._a.pos()[0], triangle._b.pos()[0], triangle._c.pos()[0]]
            y_coords = [triangle._a.pos()[1], triangle._b.pos()[1], triangle._c.pos()[1]]
            ax.fill(x_coords, y_coords, color=color, alpha=0.5)
            # Рисуем треугольники
    elif triangle_type == "scipy":
        for simplex in delaunay_sc.simplices:
            x_coords = [points[simplex[0]][0], points[simplex[1]][0], points[simplex[2]][0]]
            y_coords = [points[simplex[0]][1], points[simplex[1]][1], points[simplex[2]][1]]
            ax.fill(x_coords, y_coords, color=color, alpha=0.5)

    ax.set_xlim(min(point.pos()[0] for point in graph._points), max(point.pos()[0] for point in graph._points))
    ax.set_ylim(min(point.pos()[1] for point in graph._points), max(point.pos()[1] for point in graph._points))
    ax.set_aspect('equal')
    plt.show()


# Пример использования
if __name__ == "__main__":
    # Создание графа
    graph = Graph()
    random.seed(2)

    print("Adding points...")
    for x in range(0, 10):
        while graph.addPoint(Point(random.randint(50, 974), random.randint(50, 718))) is False:
            print("Couldn't add point")

    print("Generating custom Delaunay Mesh...")
    graph.generateDelaunayMesh()

    # Создание объекта Delaunay из scipy
    points = np.array([[p.pos()[0], p.pos()[1]] for p in graph._points])
    delaunay_sc = Delaunay(points)

    plt.figure(figsize=(10, 5))  # Создаем новую фигуру для пользовательской сетки
    plot_graph(graph, triangle_type="custom", color='green')

    # Визуализация графа с сеткой из scipy
    plt.figure(figsize=(10, 5))  # Создаем новую фигуру для сетки из scipy
    plot_graph(graph, triangle_type="scipy", color='purple')
    with open('points.txt', 'w') as file:
        for point in graph._points:
            file.write(str(point.pos()) + '\n')

    with open('triangle.txt', 'w') as file:
        for triangle in graph._triangles:
            file.write(str(triangle._a.pos())+ ',' + str(triangle._b.pos())
                       + ',' + str(triangle._c.pos()) + '\n')
