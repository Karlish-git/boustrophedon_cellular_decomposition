import numpy as np
import matplotlib.pyplot as plt
from typing import List
from bcd import Cell


class Point:  # from og coverage planner
    def __init__(self, x, y, angle=0, parent=None):
        self.x = x
        self.y = y
        # self.angle = angle  # not needed
        # self.parent = parent  # not needed
        # self.score = 0  # not needed
        # self.childs = None  # not needed
        # self.map = None  # not needed


# def postprocess_trajectory(trajectory): # from og planner
#        point_list = []
#        for point in self.trajectory:
#            point_in_meters = np.matmul(self.pix_to_meters, np.array([[point.x, point.y, 1]]).T)
#            point_list.append([point_in_meters[0,0], point_in_meters[1,0]])
#        return point_list

def draw_path(path: List[Point]):
    point_list_x = []
    point_list_y = []
    for lisst in path:
        for point in lisst[0]:
            point_list_x.append(point.x)
            point_list_y.append(point.y)
    return point_list_x, point_list_y


# Start planner from firs nearest cell

def plan(cell: Cell, radius: int = 1):
    delta = abs(cell.end - cell.start)
    path: list = []
    lines = []
    if radius * 2 < delta:
        line = cell.start
        for i in range(0, delta - radius * 2, radius * 2):
            line += radius
            line_start = Point(line, cell.boundaries[i][0] + radius)
            line_end = Point(line, cell.boundaries[i][1] - radius)
            path.append(line_start)
            path.append(line_end)
            lines.append([line_start, line_end])
            # add next line
            line += radius
            line_start = Point(line, cell.boundaries[i + radius][1] - radius)
            line_end = Point(line, cell.boundaries[i + radius][0] + radius)
            path.append(line_start)
            path.append(line_end)
            # lines.append(line_start, line_end)
    return path,# lines


def find_closest_edges(cell1: Cell, cell2: Cell):
    pass
    # Compare all four edges and make that as the start



def complete_coverage0(cell_list: List[Cell], solved_graph: list, radius: int):
    # path = plan(cell_list[1], 5)
    # xx, yy = draw_path(path)
    # plt.plot(xx, yy)
    # plt.gca()
    # plt.show()
    # print(path)
    all_lines = []
    for index in range(len(solved_graph)):
        # find closest edges of both cells:
        cell_lines = plan(cell_list[index], 10)
        all_lines.append([_ for _ in cell_lines])

    xx, yy = draw_path(all_lines)
    plt.plot(xx, yy)
    plt.show()
    return xx, yy
