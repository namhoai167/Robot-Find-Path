import tkinter as ck
import numpy as np
import itertools
import sys

from Search import *

# Numpy hỗ trợ mảng 2 chiều, in ra mảng 2 chiều theo 2 chiều, không phải như một dòng như list
# Chuyển về list của python vẫn được. Numpy chủ yếu để visualize

DEFAULT_VALUE_ID = 0
START_POINT_ID = 1
PICKUP_POINT_ID = 2
GOAL_POINT_ID = 3
EDGE_ID = 4
OBSTACLE_ID = 5
TRAVEL_ID = 6
RESULT_ID = 7
PICKUP_POINT_COMPLETE_ID = 8


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# Hàm vẽ đường thẳng nối hai đỉnh A, B vật cản theo thuật toán Bresenham
def print_obstacle_sides(array, A, B):
    dx = abs(B.x - A.x)
    dy = abs(B.y - A.y)
    p = 2 * dy - dx
    c1 = 2 * dy
    c2 = 2 * dy - 2 * dx
    x = A.x
    y = A.y
    stepx = 1
    stepy = 1
    if B.x - A.x < 0:
        stepx = -1
    if B.y - A.y < 0:
        stepy = -1
    if A.x == B.x:
        for k in range(dy):
            y -= -stepy
            array[y][x] = OBSTACLE_ID
    elif A.y == B.y:
        for k in range(dx):
            x += stepx
            array[y][x] = OBSTACLE_ID
    else:
        m = dy / dx
        if m <= 1:
            while x != B.x:
                x += stepx
                if p < 0:
                    array[y][x] = OBSTACLE_ID
                    p += c1
                else:
                    y += stepy
                    array[y][x] = OBSTACLE_ID
                    p += c2
        elif m > 1:
            while y != B.y:
                y += stepy
                if p < 0:
                    y += stepy
                    array[y][x] = OBSTACLE_ID
                    p += c2
                else:
                    array[y][x] = OBSTACLE_ID
                    p += c1


# Đọc file input
def read_input(file_name):
    f = open(file_name, "r")

    # Đọc kích thước map
    map_size_string = f.readline()
    size = get_map_size(map_size_string)
    if size == 0:
        f.close()
        return 0, 0
    width = size[0]
    height = size[1]

    # Khởi tạo map toàn phần từ 0
    # Map tọa độ x,y chạy từ 0 nên kích thước + 1
    # map = np.zeros((height + 1, width + 1))
    map = np.empty((height + 1, width + 1))
    map.fill(DEFAULT_VALUE_ID)

    # Các điểm ở viền bản đồ sẽ mang giá trị 4
    print_map_edge(map, height, width)

    # Đọc điểm bắt đầu, kết thúc, và các điểm đón
    coordinates_str = f.readline()
    S, G, pickup_point_list = get_point_coordinates_then_print(coordinates_str, map, height)

    # Đọc từ file số vật cản
    nObstacle = int(f.readline())

    # Không có vật cản
    if nObstacle == 0:
        f.close()
        return map, size, S, G, pickup_point_list

    # Duyệt qua từng dòng, đọc tọa độ các đỉnh của vật cản
    for i in range(nObstacle):
        obs_coordinates_str = f.readline()
        print_obstacle(obs_coordinates_str, map, height)

    # Đóng file
    f.close()

    return map, size, S, G, pickup_point_list


# Lấy kích thước map
def get_map_size(map_size_string):
    map_size = map_size_string.split(",")
    width = int(map_size[0])
    height = int(map_size[1])
    if width <= 2 | height <= 2:
        print("Kích thước bản đồ không hợp lệ")
        return 0
    return width, height


# Các điểm ở viền bản đồ sẽ mang giá trị 4
def print_map_edge(map, height, width):
    for i in range(width + 1):
        map[0][i] = EDGE_ID
        map[height][i] = EDGE_ID
    for i in range(height + 1):
        map[i][0] = EDGE_ID
        map[i][width] = EDGE_ID


# Lấy điểm bắt đầu, kết thúc, và các điểm đón và in vào bản đồ
def get_point_coordinates_then_print(coordinates_str, map, height):
    # Tách tọa độ theo dấu "," và đưa vào list
    coordinates = coordinates_str.split(",")

    # Số lượng tọa độ điểm
    n_coordinate = len(coordinates)

    # Trường hợp tọa độ không phù hợp
    for i in range(n_coordinate):
        if int(coordinates[i]) <= 0:
            print("Tọa độ điểm mang giá trị âm")
            return 0, 0, 0

    # Trường hợp số tọa độ điểm không phù hợp
    if n_coordinate < 4 | n_coordinate % 2 == 1:
        print("Không đủ dữ kiện về điểm bắt đầu, kết thúc, và các điểm đón")
        return 0, 0, 0
    elif n_coordinate == 4:
        # Trường hợp chỉ có điểm bắt đầu, kết thúc
        # Xử lý về tọa độ xO-y trên tkinter
        xS = int(coordinates[0])
        yS = height - int(coordinates[1])
        xG = int(coordinates[2])
        yG = height - int(coordinates[3])
        S = Point(xS, yS)
        G = Point(xG, yG)

        # In 2 điểm S, G này vào map
        map[S.y, S.x] = START_POINT_ID
        map[G.y, G.x] = GOAL_POINT_ID

        return S, G, 0
    else:
        # Tách list tọa độ ra 2 list tọa độ x và tọa độ y
        x_coordinates = []
        y_coordinates = []

        # Đưa tọa độ vào list x_coordinates, y_coordinates
        for i in range(n_coordinate):
            if i % 2 == 0:
                # Ép kiểu về int vì list đang mang kiểu string
                x = int(coordinates[i])
                x_coordinates.append(x)
            else:
                # Xử lý về tọa độ xO-y trên tkinter
                y = height - int(coordinates[i])
                y_coordinates.append(y)

        # Số lượng điểm S + G + điểm đón
        n_point = len(x_coordinates)

        # Tạo list tọa độ của các điểm đón để trả ra
        pickup_point_list = []

        # Đưa điểm đón vào mảng pickup_point_list
        for i in range(2, n_point):
            pickup_point = Point(x_coordinates[i], y_coordinates[i])
            pickup_point_list.append(pickup_point)

        # Tọa độ S, G
        S = Point(x_coordinates[0], y_coordinates[0])
        G = Point(x_coordinates[1], y_coordinates[1])

        # In 2 điểm S, G này vào map
        map[S.y, S.x] = START_POINT_ID
        map[G.y, G.x] = GOAL_POINT_ID

        # In tọa độ của các điểm đón vào map
        for i in range(2, n_point):
            map[pickup_point_list[i].y, pickup_point_list[i].x] = PICKUP_POINT_ID

    return S, G, pickup_point_list


# Lấy tọa độ các đỉnh của vật cản, rồi in vào map
def print_obstacle(obs_coordinates_str, map, height):
    obs_coordinates_list = obs_coordinates_str.split(",")

    # Số lượng tọa độ đỉnh vật cản
    n_obs_coord = len(obs_coordinates_list)

    # Trường hợp tọa độ không phù hợp
    for i in range(n_obs_coord):
        if int(obs_coordinates_list[i]) <= 0:
            print("Tọa độ đỉnh của vật cản mang giá trị âm")
            return 0

    # Trường hợp số tọa độ điểm không phù hợp
    if n_obs_coord % 2 == 1:
        print("Không đủ dữ kiện về đỉnh vật cản")
        return 0

    # Tách list tọa độ ra 2 list tọa độ x và tọa độ y
    x_obs_coordinates = []
    y_obs_coordinates = []
    for j in range(n_obs_coord):
        if j % 2 == 0:
            # Ép kiểu về int vì list đang mang kiểu string
            x = int(obs_coordinates_list[j])
            x_obs_coordinates.append(x)
        else:
            y = int(obs_coordinates_list[j])
            y_obs_coordinates.append(y)

    # Số lượng đỉnh vật cản
    n_obstacle = len(x_obs_coordinates)

    # Đưa tọa độ đỉnh vật cản vào mảng cấu trúc Point
    obstacle_point_list = []
    for k in range(n_obstacle):
        obstacle_point = Point(x_obs_coordinates[k], y_obs_coordinates[k])
        obstacle_point_list.append(obstacle_point)
        map[height - obstacle_point_list[k].y, obstacle_point_list[k].x] = OBSTACLE_ID

    # Thêm tọa độ đỉnh đầu tiên của vật cản để phục vụ hàm vẽ viền vật cản giữa đỉnh đầu và cuối
    obstacle_point = Point(x_obs_coordinates[0], y_obs_coordinates[0])
    obstacle_point_list.append(obstacle_point)

    # Xử lý vẽ đường thẳng giữa hai đỉnh vật cản
    for i in range(n_obstacle):
        A = Point(obstacle_point_list[i].x, height - obstacle_point_list[i].y)
        B = Point(obstacle_point_list[i + 1].x, height - obstacle_point_list[i + 1].y)
        print_obstacle_sides(map, A, B)

    return 1


# Hàm tính khoảng cách Manhattan
def manhattan_distance(start, end):
    return sum(abs(start - end))


def path_sort(all_pickup_point, start, end):
    n_pickup_point = len(all_pickup_point)
    cost = []
    path = []
    minn = 0
    temp = 0
    perm = itertools.permutations(all_pickup_point)

    # Print the obtained permutations
    for i in list(perm):
        path.append(i)
    path_len = np.size(path, 0)

    for j in range(path_len):
        path_cost = manhattan_distance(start, path[j][0])
        for i in range(n_pickup_point - 1):
            path_cost += manhattan_distance(path[j][i], path[j][i + 1])

        path_cost += manhattan_distance(path[j][n_pickup_point - 1], end)
        if minn >= path_cost or minn == 0:
            cost = path[j]
            temp = path_cost
            minn = path_cost
        path_cost = 0
        cost = cost + (end,)
    return temp, cost


class GameBoard(ck.Frame):
    def __init__(self, parent, map, rows, columns, size=32, color1="white"):
        """size is the size of a square, in pixels"""

        self.rows = rows        # số hàng
        self.columns = columns  # số cột
        self.size = size        # kích thước ô
        self.color1 = color1
        self.pieces = {}

        canvas_width = columns * size
        canvas_height = rows * size

        ck.Frame.__init__(self, parent)     # khởi tạo măc định
        self.canvas = ck.Canvas(self, borderwidth=0, highlightthickness=0, width=canvas_width, height=canvas_height,
                                background="bisque")
        self.canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)

        # this binding will cause a refresh if the user interactively
        # changes the window size
        self.canvas.bind("<Configure>", self.resize)

    def resize(self, event):
        x_size = int((event.width - 1) / self.columns)
        y_size = int((event.height - 1) / self.rows)
        self.size = min(x_size, y_size)

    def addpiece(self, name, image, row=0, column=0):
        # Add a piece
        self.canvas.create_image(0, 0, image=image, tags=(name, "piece"), anchor="c")
        self.place_piece(name, row, column)

    def place_piece(self, name, row, column):
        # Place a piece at the given row/column
        self.pieces[name] = (row, column)
        x0 = (column * self.size) + int(self.size / 2)
        y0 = (row * self.size) + int(self.size / 2)
        self.canvas.coords(name, x0, y0)

    def way(self, row, col, color):
        i = int(map[row][col] / 6)
        if map[row][col] == RESULT_ID:
            x1 = (col * self.size)
            y1 = (row * self.size)
            x2 = x1 + self.size
            y2 = y1 + self.size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="red", tags="square")
        elif (map[row][col] % 6) == 0:
            x1 = (col * self.size)
            y1 = (row * self.size)
            x2 = x1 + self.size
            y2 = y1 + self.size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color[i], tags="square")

    def refresh(self):
        color = self.color1
        for row in range(self.rows):
            for col in range(self.columns):
                if map[row][col] == 0:
                    x1 = (col * self.size)
                    y1 = (row * self.size)
                    x2 = x1 + self.size
                    y2 = y1 + self.size
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
                elif map[row][col] == OBSTACLE_ID:
                    x1 = (col * self.size)
                    y1 = (row * self.size)
                    x2 = x1 + self.size
                    y2 = y1 + self.size
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="black", tags="square")
                elif map[row][col] == EDGE_ID:
                    x1 = (col * self.size)
                    y1 = (row * self.size)
                    x2 = x1 + self.size
                    y2 = y1 + self.size
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="gray", tags="square")
                elif map[row][col] == START_POINT_ID:
                    x1 = (col * self.size)
                    y1 = (row * self.size)
                    x2 = x1 + self.size
                    y2 = y1 + self.size
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="blue", tags="square")
                elif map[row][col] == GOAL_POINT_ID:
                    x1 = (col * self.size)
                    y1 = (row * self.size)
                    x2 = x1 + self.size
                    y2 = y1 + self.size
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="blue", tags="square")
                elif map[row][col] == PICKUP_POINT_COMPLETE_ID:
                    x1 = (col * self.size)
                    y1 = (row * self.size)
                    x2 = x1 + self.size
                    y2 = y1 + self.size
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="teal", tags="square")
                elif map[row][col] == PICKUP_POINT_ID:
                    x1 = (col * self.size)
                    y1 = (row * self.size)
                    x2 = x1 + self.size
                    y2 = y1 + self.size
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="teal", tags="square")
        self.canvas.tag_lower("square")
        self.canvas.tag_raise("piece")


image_data = '''
    R0lGODlhEAAQAOeSAKx7Fqx8F61/G62CILCJKriIHM+HALKNMNCIANKKANOMALuRK7WOVLWPV9eR
    ANiSANuXAN2ZAN6aAN+bAOCcAOKeANCjKOShANKnK+imAOyrAN6qSNaxPfCwAOKyJOKyJvKyANW0
    R/S1APW2APW3APa4APe5APm7APm8APq8AO28Ke29LO2/LO2/L+7BM+7BNO6+Re7CMu7BOe7DNPHA
    P+/FOO/FO+jGS+/FQO/GO/DHPOjBdfDIPPDJQPDISPDKQPDKRPDIUPHLQ/HLRerMV/HMR/LNSOvH
    fvLOS/rNP/LPTvLOVe/LdfPRUfPRU/PSU/LPaPPTVPPUVfTUVvLPe/LScPTWWfTXW/TXXPTXX/XY
    Xu/SkvXZYPfVdfXaY/TYcfXaZPXaZvbWfvTYe/XbbvHWl/bdaPbeavvadffea/bebvffbfbdfPvb
    e/fgb/Pam/fgcvfgePTbnfbcl/bfivfjdvfjePbemfjelPXeoPjkePbfmvffnvbfofjlgffjkvfh
    nvjio/nnhvfjovjmlvzlmvrmpvrrmfzpp/zqq/vqr/zssvvvp/vvqfvvuPvvuvvwvfzzwP//////
    ////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////yH+FUNyZWF0ZWQgd2l0aCBU
    aGUgR0lNUAAh+QQBCgD/ACwAAAAAEAAQAAAIzAD/CRxIsKDBfydMlBhxcGAKNIkgPTLUpcPBJIUa
    +VEThswfPDQKokB0yE4aMFiiOPnCJ8PAE20Y6VnTQMsUBkWAjKFyQaCJRYLcmOFipYmRHzV89Kkg
    kESkOme8XHmCREiOGC/2TBAowhGcAyGkKBnCwwKAFnciCAShKA4RAhyK9MAQwIMMOQ8EdhBDKMuN
    BQMEFPigAsoRBQM1BGLjRIiOGSxWBCmToCCMOXSW2HCBo8qWDQcvMMkzCNCbHQga/qMgAYIDBQZU
    yxYYEAA7
'''


if __name__ == "__main__":
    # mapcuathay
    # mapkhongvatcan
    # mapkhongduongdi
    # mapco1vatcan
    # mapco2vatcan
    # mapco3vatcan
    # mapkhongvatcan,co1diemdon
    # mapkhongvatcan,co2diemdon
    # mapkhongvatcan,co3diemdon
    # mapkhongduongdi,co1diemdon
    # mapkhongduongdi,co2diemdon
    # mapkhongduongdi,co3diemdon
    # mapcovatcan,co1diemdon
    # mapcovatcan,co2diemdon
    # mapcovatcan,co3diemdon

    map, size, S, G, pickup_point_list = read_input("mapcuathay.txt")

    print(S)
    print(G)
    print(pickup_point_list)
    print(map)

    columns = size[0]  # so cot
    rows = size[1]  # so hang

    # Xử lý tọa độ để dùng cho hàm sau
    start = Point(S.y, S.x)
    goal = Point(G.y, G.x)
    all_pickup_point = []
    if pickup_point_list != 0:
        for i in range(len(pickup_point_list)):
            if i % 2 == 0:
                all_pickup_point.append(Point(pickup_point_list[i].y, pickup_point_list[i].x))

    n_pickup = len(all_pickup_point)
    list_pickup = []

    # rows - y, x danh sach diem don va dich
    if n_pickup > 0:
        minn, list_pickup = path_sort(all_pickup_point, start, goal)
        print("Duong ngan nhat: ", minn)
    else:
        list_pickup.append(goal)

    # Board
    root = ck.Tk()
    root.title("Robot found the way")
    board = GameBoard(root, map, rows+1, columns+1)
    board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    # in ky hieu diem dau
    player1 = ck.PhotoImage(data=image_data)
    board.addpiece("player1", player1, start.x, start.y)
    board.refresh()

    # greedy_best_first(map, columns + 1, rows + 1, start.x, start.y, list_pickup, n_pickup, n_pickup, board)
    # breadth_first(map, columns + 1, rows + 1, start.x, start.y, n_pickup, board)
    A_star(map, columns + 1, rows + 1, start.x, start.y, list_pickup, n_pickup, n_pickup, board)
    root.mainloop()

    # # Sử dụng tham số dòng lệnh
    # argv = sys.argv
    #
    # # Algorithm search
    # if int(argv[2]) == 1:
    #     breadth_first(map, columns+1, rows+1, start.x, start.y, n_pickup, board)
    # elif int(argv[2]) == 2:
    #     greedy_best_first(map, columns+1, rows+1, start.x, start.y, list_pickup, n_pickup, n_pickup, board)
    # elif int(argv[2]) == 3:
    #     A_star(map, columns+1, rows+1, start.x, start.y, list_pickup, n_pickup, n_pickup, board)
    # root.mainloop()