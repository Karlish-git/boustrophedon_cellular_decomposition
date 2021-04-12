# Fix OpenCv2 configuration error with ROS
# import sys
# sys.path.remove("/opt/ros/kinetic/lib/python2.7/dist-packages")


import numpy as np
import matplotlib.pyplot as plt

import bcd  # The Boustrophedon Cellular decomposition
import dfs  # The Depth-first Search Algorithm
import bfs  # The Breadth First Search Algorithm
import distance_optim  # Distance based optimization of TSP --> genetic, hill climbing etc.

import move_boustrophedon  # Uses output of bcd cells in order to move the robot
import exceptions
import solve_graph

import networkx as nx
from ant_colony import AntColony

# Read the original data
# original_map = bcd.cv2.imread("../data/real_ex4.png")
original_map = bcd.cv2.imread("../data/map0001.png")

# We need binary image
# 1's represents free space while 0's represents objects/walls
if len(original_map.shape) > 2:
    print("Map image is converted to binary")
    single_channel_map = original_map[:, :, 0]
    _, binary_map = bcd.cv2.threshold(single_channel_map, 127, 1, bcd.cv2.THRESH_BINARY)

# Call The Boustrophedon Cellular Decomposition function
cell_list: bcd.List[bcd.Cell] = None
bcd_out_im, bcd_out_cells, cell_numbers, cell_boundaries, non_neighboor_cell_numbers, cell_list = bcd.bcd(binary_map)
# Show the decomposed cells on top of original map
bcd.display_separate_map(bcd_out_im, bcd_out_cells)
move_boustrophedon.plt.show(block=False)


# CREATE AND SOLVE GRPH OF THE CELLS
print("CELL PATH:")
g = nx.Graph()
g.add_nodes_from([i for i in range(bcd_out_cells)])

for node in cell_list:
    for neighbour in node.neighbours:
        g.add_edge(cell_list.index(node), cell_list.index(neighbour))
        print(f'From {cell_list.index(node)} to {cell_list.index(neighbour)}')

nx.draw(g, with_labels=True)
bcd.plt.show()

# matrix = np.array(np.ones((bcd_out_cells, bcd_out_cells)) * np.inf)
# for i in range(len(cell_list)):
#     for j in range(len(cell_list)):
#         if cell_list[j] in cell_list[i].neighbours:
#             matrix[i][j] = 1
#             matrix[j][i] = 1
# matrix[16][17] = 1
# matrix[17][16] = 1
# ant_colony = AntColony(matrix, 1, 1, 100, 0.95, alpha=1, beta=1)
# shortest_path = ant_colony.run()
# print ("shorted_path: {}".format(shortest_path))

print("111  ")
# a = nx.algorithms.bfs_tree(g, 10)
# aaa = list(set(sum(list(a.edges()), ())))
print(f'meklesana plasuma no 10:{nx.algorithms.bfs_tree(g, 10).nodes}')
print(f'meklesana dziļumā no 10:{nx.algorithms.dfs_tree(g, 10).nodes}')

# PLAN THE PATH IN EACH CELL
# todo check if it is better to go horizontally or vertically

