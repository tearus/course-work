import sys, os, math


# Функция для определения окружности, описывающей любые три точки
def circumcircle(tri):
    try:
        D = ((tri[0][0] - tri[2][0]) * (tri[1][1] - tri[2][1]) - (tri[1][0] - tri[2][0]) * (tri[0][1] - tri[2][1]))

        center_x = (((tri[0][0] - tri[2][0]) * (tri[0][0] + tri[2][0]) + (tri[0][1] - tri[2][1]) * (
                tri[0][1] + tri[2][1])) / 2 * (tri[1][1] - tri[2][1]) - (
                            (tri[1][0] - tri[2][0]) * (tri[1][0] + tri[2][0]) + (tri[1][1] - tri[2][1]) * (
                            tri[1][1] + tri[2][1])) / 2 * (tri[0][1] - tri[2][1])) / D

        center_y = (((tri[1][0] - tri[2][0]) * (tri[1][0] + tri[2][0]) + (tri[1][1] - tri[2][1]) * (
                tri[1][1] + tri[2][1])) / 2 * (tri[0][0] - tri[2][0]) - (
                            (tri[0][0] - tri[2][0]) * (tri[0][0] + tri[2][0]) + (tri[0][1] - tri[2][1]) * (
                            tri[0][1] + tri[2][1])) / 2 * (tri[1][0] - tri[2][0])) / D

        radius = math.sqrt((tri[2][0] - center_x) ** 2 + (tri[2][1] - center_y) ** 2)

        return [[center_x, center_y], radius]
    except:
        print("Divide By Zero error")
        print(tri)


# Определение, находится ли данная точка внутри круга
def pointInCircle(point, circle):
    # Это довольно просто; достаточно найти расстояние между точкой и центром. Если оно меньше или равно радиусу, то точка находится внутри круга

    d = math.sqrt(math.pow(point[0] - circle[0][0], 2) + math.pow(point[1] - circle[0][1], 2))
    if d < circle[1]:
        return True
    else:
        return False


# Базовый класс Точка
class Point():
    def __init__(self, x, y):
        self._x = x
        self._y = y

    # Позиция точки
    def pos(self):
        return [self._x, self._y]

    # Определяет, являются ли две точки эквивалентными
    def isEqual(self, other_point):
        if (self._x == other_point._x and self._y == other_point._y):
            return True
        else:
            return False

    # Преобразование точки в строку (для отладочных целей)
    def pointToStr(self):
        return str(self.pos())


# Базовый класс Ребро
class Edge():
    def __init__(self, a, b):
        if a is not b:
            self._a = a
            self._b = b

    # Проверка, являются ли два ребра эквивалентными друг другу
    def isEqual(self, other_edge):
        if (self._a.isEqual(other_edge._a) or self._b.isEqual(other_edge._a)) and (
                self._a.isEqual(other_edge._b) or self._b.isEqual(other_edge._b)):
            return True
        elif self == other_edge:
            return True
        else:
            return False

    # Конвертирует ребро в строку (для отладочных целей)
    def edgeToStr(self):
        return str([self._a.pos(), self._b.pos()])

    # Вычисление длины ребра
    def length(self):
        return math.sqrt(
            math.pow(self._b.pos()[0] - self._a.pos()[0], 2) + math.pow(self._b.pos()[1] - self._a.pos()[1], 2))

    # Определение пересечения двух ребер
    def edgeIntersection(self, other_edge):

        if self.isEqual(other_edge):
            return False
        else:
            try:
                x1 = self._a.pos()[0]
                x2 = self._b.pos()[0]
                x3 = other_edge._a.pos()[0]
                x4 = other_edge._b.pos()[0]
                y1 = self._a.pos()[1]
                y2 = self._b.pos()[1]
                y3 = other_edge._a.pos()[1]
                y4 = other_edge._b.pos()[1]
                t = (((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))) / (
                        ((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))
                u = (((x2 - x1) * (y1 - y3)) - ((y2 - y1) * (x1 - x3))) / (
                        ((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))

                # Если 0 <= t <= 1 или 0 <= u <= 1, то происходит пересечение.
                if (t >= 0 and t <= 1) and (u >= 0 and u <= 1):
                    int_x = int(x1 + t * (x2 - x1))
                    int_y = int(y1 + t * (y2 - y1))
                    int_point = Point(int_x, int_y)

                    # Если точка пересечения является одной из вершин ребра, то считается,
                    # то пересечение не произошло (то есть эти ребра соединены в одной точке)
                    if self._a.isEqual(int_point) or self._b.isEqual(int_point) or other_edge._a.isEqual(
                            int_point) or other_edge._b.isEqual(int_point):
                        return False

                    # Если нет точки, эти ребра пересекаются
                    else:
                        return True

                else:
                    return False
            except:
                # Ошибка деления на ноль интерпретируется как отсутствие пересечения ребер
                return False


# Базовый класс Треугольник
class Triangle():

    # Необходимо создать треугольник только если любые две точки не совпадают
    def __init__(self, a, b, c):
        if a is not b and a is not c:
            self._a = a
        if b is not a and b is not c:
            self._b = b
        if c is not a and c is not b:
            self._c = c

    # Проверка, являются ли два треугольника равными (определено как совместное наличие всех трех точек)
    def isEqual(self, other_tri):
        if (self._a is other_tri._a or self._a is other_tri._b or self._a is other_tri._c) and (
                self._b is other_tri._a or self._b is other_tri._b or self._b is other_tri._c) and (
                self._c is other_tri._a or self._c is other_tri._b or self._c is other_tri._c):
            return True
        else:
            return False

    # Вывод треугольника в удобочитаемый формат (для отладочных целей)
    def printTriangle(self):
        print("A: " + self._a.pointToStr() + " B: " + self._b.pointToStr() + " C: " + self._c.pointToStr())


# Класс Граф
class Graph():
    def __init__(self):

        # Это будет список объектов точек, как определено выше
        self._points = []

        # Это будет список объектов треугольников, как определено выше
        self._triangles = []

        # Это список ребер, как определено выше
        self._edges = []

        # Границы точек для сортировки
        self._point_min_x = 0
        self._point_max_x = 0

    def addPoint(self, point):

        # Проверка на существование эквивалентной точки
        for x in self._points:
            if x.isEqual(point):
                return False

        # Если у точки значение X ниже, чем у любой другой точки
        if self._point_min_x > point.pos()[0] or self._point_min_x == 0:
            self._points.insert(0, point)
            self._point_min_x = point.pos()[0]
            return True

        # Если у точки значение X выше, чем у любой другой точки
        elif self._point_max_x < point.pos()[0]:
            self._points.append(point)
            self._point_max_x = point.pos()[0]
            return True

        # Если значение X находится посередине
        else:
            same_x = []
            for x in self._points:
                if x.pos()[0] == point.pos()[0]:
                    same_x.append(x)

            # Если у точки нет такого же значения X, как у новой точки,
            # найдите первую точку, у которой значение X больше, и вставьте новую точку перед ней
            if len(same_x) == 0:
                first_greater = 0
                for x in self._points:
                    if x.pos()[0] > point.pos()[0]:
                        first_greater = self._points.index(x)
                        break
                self._points.insert(first_greater, point)
                return True

            # Если у нас только одна точка в графе с таким же значением X,
            # сравните значения Y, чтобы определить порядок их расположения
            elif len(same_x) == 1:
                index = self._points.index(same_x[0])
                if same_x[0].pos()[1] > point.pos()[1]:
                    self._points.insert(index - 1, point)
                    return True
                else:
                    self._points.insert(index + 1, point)
                    return True

            # Если у нескольких точек одно и то же значение X, определите,
            # куда должна быть помещена новая точка на основе ее значения Y
            else:
                first_greater_y = 0
                for x in same_x:
                    if x.pos()[1] > point.pos()[1]:
                        first_greater_y = self._points.index(x)
                        break
                if (first_greater_y != 0):
                    self._points.insert(first_greater_y, point)
                    return True
                else:
                    self._points.insert(self._points.index(same_x[len(same_x) - 1]), point)
                    return True

    def addEdge(self, edge):

        # Проверка на существование эквивалентного ребра в графе, добавьте его, если такового нет

        for x in self._edges:
            if x.isEqual(edge):
                return False
        self._edges.append(edge)
        return True

    # Добавляет треугольник в список треугольников и возвращает true, если успешно, проверяет,
    # является ли он эквивалентным какому-либо другому треугольнику. Возвращает false, если существует
    # эквивалентный треугольник
    def addTriangle(self, triangle):

        # Сначала проверяем, существует ли эквивалентный треугольник
        for x in self._triangles:
            if x.isEqual(triangle): return False

        # Если нет, мы можем добавить треугольник в граф
        self._triangles.append(triangle)
        tri = [triangle._a.pos(), triangle._b.pos(), triangle._c.pos()]
        return True

    # Проверка, является ли данный треугольник Делоне (т.е., ни одна другая точка не находится внутри окружности,
    # описывающей треугольник)
    def triangleIsDelaunay(self, triangle):
        tri = [triangle._a.pos(), triangle._b.pos(), triangle._c.pos()]
        cc = circumcircle(tri)
        for x in self._points:
            # Если получается ошибка деления на ноль, предполагается, что треугольник не является Делоне
            if not (x.isEqual(triangle._a) and x.isEqual(triangle._b) and x.isEqual(triangle._c)):
                try:
                    if pointInCircle(x.pos(), cc):
                        return False
                except:
                    return False
        return True

    # Генерирует полную сетку Делоне, проверяя каждый возможный треугольник на условие Делоне,
    # затем отмечает любые пересекающиеся ребра и удаляет более длинное из пересекающихся ребер
    def generateDelaunayMesh(self):

        # Создает каждый возможный треугольник и проверяет его на условие Делоне
        for p1 in self._points:
            for p2 in self._points:
                for p3 in self._points:
                    if not p1.isEqual(p2) and not p2.isEqual(p3) and not p3.isEqual(p1):
                        test_tri = Triangle(p1, p2, p3)
                        if self.triangleIsDelaunay(test_tri):
                            self.addTriangle(test_tri)

        # Еще один проверка условия Делоне (вероятно, избыточна) и затем добавление ребер треугольника в граф
        for t in self._triangles:
            if not self.triangleIsDelaunay(t):
                self._triangles.remove(t)
            else:
                self.addEdge(Edge(t._a, t._b))
                self.addEdge(Edge(t._b, t._c))
                self.addEdge(Edge(t._c, t._a))

        # Проверка на пересечение ребер
        bad_edges = []
        for e1 in self._edges:
            for e2 in self._edges:
                if not e1.isEqual(e2):
                    if e1.edgeIntersection(e2):
                        len_e1 = e1.length()
                        len_e2 = e2.length()
                        if len_e1 >= len_e2:
                            bad_edges.append(e1)

                        else:
                            bad_edges.append(e2)

        # Удаление любых плохих (пересекающихся) ребер из графа
        for x in bad_edges:
            for y in self._edges:
                if x.isEqual(y):
                    self._edges.remove(y)
                    continue
