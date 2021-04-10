# Fix OpenCv2 configuration error with ROS
# import sys
# sys.path.remove("/opt/ros/kinetic/lib/python2.7/dist-packages")


import bcd  # The Boustrophedon Cellular decomposition
import dfs  # The Depth-first Search Algorithm
import bfs  # The Breadth First Search Algorithm
import distance_optim  # Distance based optimization of TSP --> genetic, hill climbing etc.

import move_boustrophedon  # Uses output of bcd cells in order to move the robot
import exceptions
import solve_graph



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
bcd_out_im, bcd_out_cells, cell_numbers, cell_boundaries, non_neighboor_cell_numbers, cell_list = bcd.bcd(binary_map)
# Show the decomposed cells on top of original map
bcd.display_separate_map(bcd_out_im, bcd_out_cells)
move_boustrophedon.plt.show(block=False)

print("CELL PATH:")
# order = solve_graph.breadth_first_search(cell_list,10)