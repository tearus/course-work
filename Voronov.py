def read_coordinates_from_file(file_path):
    coordinates = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Удаляем символ новой строки и пробелы вокруг чисел
                line = line.strip().replace(',', '')
                # Разбиваем строку на две части по пробелу и преобразуем в float
                x, y = map(float, line.split())
                coordinates.append((x, y))
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
    return coordinates


def read_triangles_from_file(file_path):
    triangles = []
    with open(file_path, 'r') as file:
        for line in file:
            # Удаляем пробелы и преобразуем строку в список кортежей
            points_str = line.strip().replace('[', '').replace(']', '')
            points_list = [tuple(map(float, point.split(','))) for point in points_str.split()]
            triangles.append(points_list)
    return triangles


triangles = read_triangles_from_file('path_to_your_file.txt')
for i, triangle in enumerate(triangles, start=1):
    print(f"Треугольник {i}:")
    for point in triangle:
        print(point)
    print()

# Пример использования функции
coordinates = read_coordinates_from_file('points.txt')
print(coordinates)
