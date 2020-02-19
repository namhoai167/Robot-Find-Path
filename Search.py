try:
    import Queue as Q  # python ver 2.7
except ImportError:
    import queue as Q

START_POINT_ID = 1
PICKUP_POINT_ID = 2
GOAL_POINT_ID = 3
EDGE_ID = 4
OBSTACLE_ID = 5
TRAVEL_ID = 6
RESULT_ID = 7
PICKUP_POINT_COMPLETE_ID = 8
GREEDY_MARK = -1

color = ["coral", "cyan", "fuchsia", "yellow", "lime", "pink"]

arr_global = [[1, 0, -1, 0], [0, 1, 0, -1]]


class GreedyNode:
    def __init__(self, x=0, y=0, cost=0, parent=0):
        self.x = x
        self.y = y
        self.cost = cost
        self.parent = parent

    def __lt__(self, other):
        return self.cost < other.cost


# Hàm tính khoảng cách Manhattan
def path_cost(x_start, y_start, x_end, y_end):
    return abs(x_start - x_end) + abs(y_start - y_end)


def check_greedy(map, start, x, y, n_pickup):
    if x == start.x and y == start.y: return 0
    if map[x][y] == EDGE_ID: return 0
    if map[x][y] == OBSTACLE_ID: return 0
    if map[x][y] == TRAVEL_ID * (n_pickup + 1): return 0
    if map[x][y] == GREEDY_MARK * (n_pickup + 1): return 0
    if map[x][y] == PICKUP_POINT_COMPLETE_ID: return 0
    if map[x][y] == PICKUP_POINT_ID: return 0
    return 1


def greedy_best_first(map, width, height, x_start, y_start, list_pickup, max_npickup, n_pickup, board):
    map[x_start][y_start] = PICKUP_POINT_COMPLETE_ID    # Điểm khởi đầu chứng tỏ đã được duyệt qua.
    z = max_npickup - n_pickup

    # Tham lam, chọn điểm đến là điểm gần điểm bắt đầu nhất.
    x_end = list_pickup[z].x
    y_end = list_pickup[z].y

    # Hàng đợi ưu tiên
    pq = Q.PriorityQueue()
    start = GreedyNode(x_start, y_start, path_cost(x_start, y_start, x_end, y_end), 0)
    pq.put(start)

    # Danh sách kề
    lend = width * height
    dsach = [0] * lend
    i = 0

    while not pq.empty():
        dsach[i] = pq.get()
        if i != 0:
            map[dsach[i].x][dsach[i].y] = GREEDY_MARK * (n_pickup + 1)
        if path_cost(dsach[i].x, dsach[i].y, x_end, y_end) == 1 or (pq.empty() and i != 0):
            if pq.empty():
                n_pickup = 0
            if n_pickup > 0:
                greedy_best_first(map, width, height, x_end, y_end, list_pickup, max_npickup, n_pickup - 1, board)
                break
            else:
                break

        for j in range(4):
            x_new = dsach[i].x + arr_global[0][j]
            y_new = dsach[i].y + arr_global[1][j]
            if check_greedy(map, start, x_new, y_new, n_pickup):
                pq.put(GreedyNode(x_new, y_new, path_cost(x_new, y_new, x_end, y_end), i))
                map[x_new][y_new] = TRAVEL_ID * (n_pickup + 1)
                board.way(x_new, y_new, color)
        i += 1

    if path_cost(dsach[i].x, dsach[i].y, x_end, y_end) == 1:
        map[dsach[i].x][dsach[i].y] = RESULT_ID
        board.Way(dsach[i].x, dsach[i].y, color)               # thêm tô màu

        h = dsach[i].parent
        while h != 0:
            map[dsach[h].x][dsach[h].y] = RESULT_ID
            board.Way(dsach[h].x, dsach[h].y, color)
            h = dsach[h].parent
    else:
        print("NO WAY")


# Check for breadth first search
def check_BFS(map, x_start, y_start, x, y, n_pickup):
    if x == x_start and y == y_start: return 0
    if map[x][y] == EDGE_ID: return 0
    if map[x][y] == TRAVEL_ID * (n_pickup + 1): return 0
    if map[x][y] == OBSTACLE_ID: return 0
    if map[x][y] == PICKUP_POINT_COMPLETE_ID: return 0
    return 1


def breadth_first(map, width, height, x_start, y_start, n_pickup, board):
    _isFindNewPickUp = 0
    _isFindEndPoint = 0
    map[x_start][y_start] = PICKUP_POINT_COMPLETE_ID

    # list[0] lưu hoành độ, list[1] lưu tung độ, list[2] truy vết
    lend = width * height
    dsach = [[0 for _ in range(lend)] for _ in range(3)]

    # dsach = [0] * 3
    # for i in range(3):
    #     dsach[i] = [0] * lend

    dsach[0][0] = x_start
    dsach[1][0] = y_start
    dsach[2][0] = 0
    i = 0
    tail = 0
    while i <= tail:
        for j in range(4):
            if check_BFS(map, x_start, y_start, dsach[0][i] + arr_global[0][j], dsach[1][i] + arr_global[1][j], n_pickup):
                tail += 1
                dsach[0][tail] = dsach[0][i] + arr_global[0][j]
                dsach[1][tail] = dsach[1][i] + arr_global[1][j]
                dsach[2][tail] = i

                # Nếu mà gặp điểm đón thì xem điểm đó là điểm bắt đầu và gọi hàm BFS, số điểm cần đón giảm đi 1 đơn vị
                if map[dsach[0][tail]][dsach[1][tail]] == PICKUP_POINT_ID:
                    _isFindNewPickUp = 1
                    breadth_first(map, width, height, dsach[0][tail], dsach[1][tail], n_pickup - 1, board)
                    break

                # Nếu gặp điểm kết thúc và đã đón hết các điểm pick_up thì break để in đường đi
                if map[dsach[0][tail]][dsach[1][tail]] == GOAL_POINT_ID and n_pickup == 0:
                    _isFindEndPoint = 1
                    map[dsach[0][tail]][dsach[1][tail]] = PICKUP_POINT_COMPLETE_ID
                    break

                # Còn lại những điểm đi qua sẽ được đánh dấu, trừ những điểm đón. cho phép đi qua nhưng không đổi màu.
                # Với mỗi điểm start mới sẽ có màu khác nhau với quy ước số này là bội của TRAVEL_ID
                if map[dsach[0][tail]][dsach[1][tail]] != PICKUP_POINT_COMPLETE_ID and map[dsach[0][tail]][
                    dsach[1][tail]] != PICKUP_POINT_ID and map[dsach[0][tail]][dsach[1][tail]] != GOAL_POINT_ID:
                    map[dsach[0][i] + arr_global[0][j]][dsach[1][i] + arr_global[1][j]] = TRAVEL_ID * (n_pickup + 1)
                    board.way(dsach[0][i] + arr_global[0][j],dsach[1][i] + arr_global[1][j],color)

        i += 1
        if map[dsach[0][tail]][dsach[1][tail]] == PICKUP_POINT_COMPLETE_ID and (_isFindNewPickUp or _isFindEndPoint):
            break

    if map[dsach[0][tail]][dsach[1][tail]] == PICKUP_POINT_COMPLETE_ID:     # Truy vết
        h = dsach[2][tail]
        while h != 0:
            map[dsach[0][h]][dsach[1][h]] = RESULT_ID
            board.way(dsach[0][h], dsach[1][h], color)
            h = dsach[2][h]
    else:
        print("NO WAY")


# algorithm A*
class A_star_Node:
    def __init__(self, x=0, y=0, cost=0, gscore=0, parent=0):
        self.x = x
        self.y = y
        self.cost = cost
        self.gscore = gscore
        self.parent = parent

    def __lt__(self, other):
        return self.cost < other.cost

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


# # Hàm tính khoảng cách Manhattan
def heuristic(x_start, y_start, x_end, y_end):
    return abs(x_start - x_end) + abs(y_start - y_end)


def check_A(map, x_start, y_start, x, y, n_pickup):  # vị trí tránh đi
    if x == x_start and y == y_start: return 0
    if map[x][y] == EDGE_ID: return 0
    if map[x][y] == OBSTACLE_ID: return 0
    if map[x][y] == TRAVEL_ID * (n_pickup + 1): return 0    # mở rộng
    if map[x][y] == GREEDY_MARK * (n_pickup + 1): return 0  # đường đi
    if map[x][y] == PICKUP_POINT_COMPLETE_ID: return 0
    return 1


def A_star(map, width, height, x_start, y_start, list_pickup, max_npickup, n_pickup, board):
    map[x_start][y_start] = PICKUP_POINT_COMPLETE_ID
    z = max_npickup - n_pickup               # lấy giá trị kết thúc
    x_end = list_pickup[z].x
    y_end = list_pickup[z].y

    pq = Q.PriorityQueue()
    Node = A_star_Node(x_start, y_start, heuristic(x_start, y_start, x_end, y_end), 0, 0)
    pq.put(Node)
    temp = Q.Queue()
    lend = width * height
    dsach = [0] * lend

    i = 0
    while not pq.empty():  # vòng lặp cho tới khi đến đích
        dsach[i] = pq.get()

        if i != 0:
            if dsach[i].x != x_end or dsach[i].y != y_end:
                if  map[dsach[i].x][dsach[i].y] != PICKUP_POINT_ID:
                    map[dsach[i].x][dsach[i].y] = TRAVEL_ID * (n_pickup + 1)
                board.way(dsach[i].x, dsach[i].y, color)
        if (dsach[i].x == x_end and dsach[i].y == y_end) or (pq.empty() and i != 0):
            if pq.empty():
                n_pickup = 0
            if n_pickup > 0:
                A_star(map, width, height, x_end, y_end, list_pickup, max_npickup, n_pickup - 1, board)
                break
            else:
                break

        for j in range(4):  # mở frontier
            x_new = dsach[i].x + arr_global[0][j]
            y_new = dsach[i].y + arr_global[1][j]
            if check_A(map, x_start, y_start, x_new, y_new, n_pickup) :
                gscore = dsach[i].gscore + 1
                node = A_star_Node(x_new, y_new, heuristic(x_new, y_new, x_end, y_end) + gscore, gscore, i)
                k =0
                while not pq.empty():  # kiểm tra có nằm trong node, có nằm trong pq không?
                    check = pq.get()
                    if check.x == node.x and check.y == node.y :
                        if check.cost > node.cost:
                            check.cost = node.cost
                            check.parent = node.parent
                            check.gscore = node.gscore
                            temp.put(check)
                            k = 1
                    else:
                        temp.put(check)
                while not temp.empty():
                    pq.put(temp.get())
                if k == 0:
                    pq.put(node)
                    if  map[x_new][y_new] != PICKUP_POINT_ID:   # thêm điều kiện
                        map[x_new][y_new] = TRAVEL_ID * (n_pickup + 1)
        i += 1

    if dsach[i].x == x_end and dsach[i].y == y_end:     # Truy vết
        map[dsach[i].x][dsach[i].y] = RESULT_ID
        h = dsach[i].parent
        while h != 0:
            map[dsach[h].x][dsach[h].y] = RESULT_ID
            board.way(dsach[h].x, dsach[h].y, color)
            h = dsach[h].parent
    else:
        print("NO WAY")