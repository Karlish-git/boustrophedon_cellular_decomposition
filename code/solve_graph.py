# import numpy as np
# from matplotlib import pyplot as plt
# from bcd import Cell
#
#
# def breadth_first_search(cells: list[Cell], current_cell: int = 0):
#     # todo get algorithm that has weights relativee to possition
#     queue = []  # [cells[current_cell]]
#     while cells:  # len(queue) != len(cells):
#         queue.append(cells.pop(current_cell))
#         for node in queue[-1].neighbours:
#             if not node.discovered:
#                 queue.append(node)
#                 node.discovered = True
#
#
#
#     return queue