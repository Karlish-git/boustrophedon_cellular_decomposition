# Fix OpenCv2 configuration error with ROS
# import sys
# sys.path.remove("/opt/ros/kinetic/lib/python2.7/dist-packages")

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import bcd  # The Boustrophedon Cellular decomposition
import move_boustrophedon  # Uses output of bcd cells in order to move the robot
from ccp_v0 import complete_coverage0
import exceptions


def display_path_on_map(separate_map, cells, xx, yy):
    fig, ax1 = plt.subplots()
    map_img = np.empty([*separate_map.shape, 3], dtype=np.uint8)
    random_colors = np.random.randint(0, 255, [cells, 3])
    for cell_id in range(1, cells):
        map_img[separate_map == cell_id, :] = random_colors[cell_id, :]
    ax1.imshow(map_img)
    ax1.plot(xx, yy)
    plt.show()


# Read the original data
# original_map = bcd.cv2.imread("../data/real_ex4.png") # image from the git
original_map = bcd.cv2.imread("../data/map0001.png")

# We need binary image
# 1's represents free space while 0's represents objects/walls
# this git uses 1 and 0, but it shouldn't be hard to convert to True and False
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

# define and add all cells(nodes) to the graph
g = nx.Graph()
g.add_nodes_from([i for i in range(bcd_out_cells)])

# Create links between all of the neighbouring cells(nodes)
for node in cell_list:
    for neighbour in node.neighbours:
        g.add_edge(cell_list.index(node), cell_list.index(neighbour))
        print(f'From {cell_list.index(node)} to {cell_list.index(neighbour)}')

nx.draw(g, with_labels=True)
plt.show()

# quick and dirty way to get a Symmetric matrix(simetrija pret galveno diognāli)
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


depth_first = nx.algorithms.dfs_tree(g, 10).nodes
print(f'meklesana plasuma no 10:{nx.algorithms.bfs_tree(g, 10).nodes}')
print(f'meklesana dziļumā no 10:{depth_first}')

# PLAN THE PATH IN EACH CELL
# todo check if it is better to go horizontally or vertically
x, y = complete_coverage0(cell_list, depth_first, 2)
# try to draw one plot on other:
display_path_on_map(bcd_out_im, bcd_out_cells, x, y)
