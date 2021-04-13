# Import necessary libraries
import numpy as np
from matplotlib import pyplot as plt
from typing import Tuple, List
import cv2
import random
import itertools

Slice = List[Tuple[int, int]]


class Cell:

    def __init__(self,
                 start: int = None,
                 end: int = None,
                 boundaries: list = [],
                 neighbours: list = None,
                 ):
        self.start = start
        self.end = end
        self.boundaries = boundaries
        self.neighbours = neighbours
        self.discovered = False
        self. cleaned = False



def calc_connectivity(slice: np.ndarray) -> Tuple[int, Slice]:
    """
    Calculates the connectivity of a slice and returns the connected area of the slice.

    Args:
        slice: rows. A slice of map.

    Returns:
        The connectivity number and connectivity parts.
        connectivity --> total number of connected parts

    Examples:
        >>> data = np.array([0,0,0,0,1,1,1,0,1,0,0,0,1,1,0,1,1,0])
        >>> print(calc_connectivity(data))
        (4, [(4, 7), (8, 9), (12, 14), (15, 17)])
        (4,7) --> 4 is the point where connectivity is started
              --> 7 is the point where it finished
    """
    connectivity = 0
    last_data = 0
    open_part = False
    connective_parts = []
    for i, data in enumerate(slice):
        if last_data == 0 and data == 1:
            open_part = True
            start_point = i
        elif last_data == 1 and data == 0 and open_part:
            open_part = False
            connectivity += 1
            end_point = i
            connective_parts.append((start_point, end_point))

        last_data = data
    return connectivity, connective_parts


# todo. mby use more than just the previous, so it doesn't create places, where robot can't drive
def get_adjacency_matrix(parts_left: Slice, parts_right: Slice) -> np.ndarray:
    """
    Get adjacency matrix of 2 neighborhood slices.

    Args:
        slice_left: left slice
        slice_right: right slice

    Returns:
        [L, R] Adjacency matrix.
    """
    adjacency_matrix = np.zeros([len(parts_left), len(parts_right)])
    for l, lparts in enumerate(parts_left):
        for r, rparts in enumerate(parts_right):
            if min(lparts[1], rparts[1]) - max(lparts[0], rparts[0]) > 0:
                adjacency_matrix[l, r] = 1

    return adjacency_matrix


def remove_duplicates(in_list):
    """
        This function removes duplicates in the input list, where
        input list is composed of unhashable elements
        Example:
            in_list = [[1,2],[1,2],[2,3]]
            output = remove_duplicates(in_list)
            output --> [[1,2].[2,3]]
    """
    out_list = []
    in_list.sort()
    out_list = list(in_list for in_list, _ in itertools.groupby(in_list))
    # print("input_list: ", in_list)
    # print("output list: ",out_list)
    return out_list


def find_neighbours(cells: List[Cell], robot_width: int = 30):
    for i in range(len(cells)-1):  # last one has only neighbours on one side
        ending = cells[i].end
    # TODO when to break the j loop?(when there is a guarantee that no more new neighbours can be found)
        for j in range(1, len(cells)):  # first has no cells on one side
            if j != i and cells[j].start - 1 == ending:
                if min(cells[i].boundaries[-1][1], cells[j].boundaries[0][1]) -\
                        max(cells[i].boundaries[-1][0], cells[j].boundaries[0][0]) >= robot_width:
                    # get smallest of bottom boundaries and get biggest of upper boundaries check
                    # if there is enough width for robot to drive,
                    # if there is thn the cells can be considered neighbours
                    cells[i].neighbours.append(cells[j])
                    cells[j].neighbours.append(cells[i])


def bcd(erode_img: np.ndarray) -> Tuple[np.ndarray, int]:
    """
    Boustrophedon Cellular Decomposition

    Args:
        erode_img: [H, W], eroded map. The pixel value 0 represents obstacles and 1 for free space.

    Returns:
        [H, W], separated map. The pixel value 0 represents obstacles and others for its' cell number.
        current_cell and seperate_img is for display purposes --> which is used to show
        decomposed cells into a separate figure
        all_cell_numbers --> contains all cell index numbers
        cell_boundaries --> contains all cell boundary coordinates (only y coordinate)
        non_neighboor_cells --> contains cell index numbers of non_neighboor_cells, i.e.
        cells which are separated by the objects
        cells --> contins a list of all the
    """

    assert len(erode_img.shape) == 2, 'Map should be single channel.'
    last_connectivity = 0
    last_connectivity_parts = []
    current_cell = 1  # offset by 1 because 0 is obstacles
    current_cells = []
    separate_img = np.copy(erode_img)
    fig, ax = plt.subplots(1, frameon=False)
    ax.imshow(separate_img, cmap='Greys', interpolation='nearest', alpha=1)
    plt.show()
    cell_boundaries = {}
    non_neighboor_cells = []
    cell_start_end = [[0, 0]]
    # cells = [Cell(0, 0)]

    for col in range(erode_img.shape[1]):
        current_slice = erode_img[:, col]
        connectivity, connective_parts = calc_connectivity(current_slice)

        if last_connectivity == 0:
            current_cells = []
            for i in range(connectivity):  # slice intersects with the object for the first time
                current_cells.append(current_cell)
                current_cell += 1  # we are creating different cells on the same column
                # which are seperated by the objects
        elif connectivity == 0:
            current_cells = []
            continue
        else:
            adj_matrix = get_adjacency_matrix(last_connectivity_parts, connective_parts)
            new_cells = [0] * len(connective_parts)

            for i in range(adj_matrix.shape[0]):
                if np.sum(adj_matrix[i, :]) == 1:
                    new_cells[np.argwhere(adj_matrix[i, :])[0][0]] = current_cells[i]
                # If a previous part is connected to multiple parts this time, it means that IN has occurred.
                elif np.sum(adj_matrix[i, :]) > 1:  # left slice is connected to more than one part of right slice
                    for idx in np.argwhere(adj_matrix[i, :]):
                        new_cells[idx[0]] = current_cell
                        current_cell = current_cell + 1
                        cell_start_end.append([col, col])
                        # cells.append(Cell(col, col))

            for i in range(adj_matrix.shape[1]):
                # If a part of this time is connected to the last multiple parts, it means that OUT has occurred.
                if np.sum(adj_matrix[:, i]) > 1:  # right slice is connected to more than one part of left slice
                    new_cells[i] = current_cell
                    current_cell = current_cell + 1
                    cell_start_end.append([col, col])
                    # cells.append(Cell(col, col))
                # If this part of the part does not communicate with any part of the last time, it means that it happened in
                elif np.sum(adj_matrix[:, i]) == 0:
                    new_cells[i] = current_cell
                    current_cell = current_cell + 1
                    cell_start_end.append([col, col])
                    # cells.append(Cell(col, col))
            current_cells = new_cells

        # Draw the partition information on the map.
        for cell, slice in zip(current_cells, connective_parts):
            # print("Debug")
            # print(current_cells, connective_parts)
            separate_img[slice[0]:slice[1], col] = cell
            # fig, ax = plt.subplots(1, frameon=False)
            # ax.imshow(separate_img, cmap='Greys', interpolation='nearest', alpha=1)
            # plt.show()

            # print('Slice {}: connectivity from {} to {}'.format(col, last_connectivity, connectivity))
        last_connectivity = connectivity
        last_connectivity_parts = connective_parts

        # print("Debug")
        # print(current_cells,connective_parts)

        # print("Current cell: ", current_cell)
        # todo put this in for loop next to rest of append cell boundaries
        if len(current_cells) == 1:  # no object in this cell
            cell_index = current_cell - 1  # cell index starts from 1, because 0 is obstacles
            cell_boundaries.setdefault(cell_index, [])
            cell_boundaries[cell_index].append(connective_parts[0])
            # cells[cell_index - 1].end = col
            cell_start_end[cell_index - 1][1] = col  # change cell last colon index

        elif len(current_cells) > 1:  # cells separated by the object
            # cells separated by the objects are not neighbor to each other
            if current_cells not in non_neighboor_cells:
                non_neighboor_cells.append(current_cells)
            # in this logic, all other cells must be neighboor to each other
            # if their cell number are adjacent to each other
            # like cell1 is neighboor to cell2

            for i in range(len(current_cells)):
                # current cells list doesn't need cell -1 operation 
                # it is already in the proper form
                cell_index = current_cells[i]
                # connective_parts and current_cells contain more than one
                # cell info which are separated by the object ,so we are iterating
                # with the for loop to reach all the cells
                # todo Valter, vai te vajag .set default??
                cell_boundaries.setdefault(cell_index, [])
                cell_boundaries[cell_index].append(connective_parts[i])
                # cells[cell_index - 1].boundaries.append(connective_parts[i])
                # cells[cell_index - 1].end = col
                cell_start_end[cell_index - 1][1] = col  # change cell last colon index

    # Cell 1 is the left most cell and cell n is the right most cell
    # where n is the total cell number
    all_cell_numbers = cell_boundaries.keys()
    # non_neighboor_cells = remove_duplicates(non_neighboor_cells)#no need the added if not in non_neighbour does the job

    fig, ax = plt.subplots(1, frameon=False)
    ax.imshow(separate_img, cmap='Greys', interpolation='none', alpha=1)
    plt.show()

    cells = []
    for i in range(len(all_cell_numbers)):
        cells.append(
            Cell(start=cell_start_end[i][0],
                 end=cell_start_end[i][1],
                 boundaries=cell_boundaries[i + 1],
                 neighbours=[]
                 )
        )

    find_neighbours(cells)

    return separate_img, current_cell, list(all_cell_numbers), cell_boundaries, non_neighboor_cells, cells  # , cell_start_end

# all under this is not needed

def display_separate_map(separate_map, cells):
    display_img = np.empty([*separate_map.shape, 3], dtype=np.uint8)
    random_colors = np.random.randint(0, 255, [cells, 3])
    for cell_id in range(1, cells):
        display_img[separate_map == cell_id, :] = random_colors[cell_id, :]
    fig_new = plt.figure()
    plt.imshow(display_img)


def calculate_neighboor_matrix(cells, boundaries, non_neighboor_cells):
    # Doesn't work right now, let's look at later!
    """
        This function creates adjacency matrix for the decomposed cells
        Output: Matrix composed of zeros and ones
                output.shape --> total_cell_number x total_cell_number
        Assumption: One cell is not neighboor with itself, so diagonal elements
                    are always zero!        
        Example: let's say we have 3 cells: cell1 and cell2 are only neighboors
                adjacency_matrix = [ [0 1 0] #cell1 is neighboor with cell2 
                                     [1 0 0] #cell2 is neighboor with cell1
                                     [0 0 0]  ]
    """
    """
    adjacency_graph = {}
    total_cell_number = len(cells)
    for i in range(total_cell_number): #Iterate through all the cells
        if (nonneighboor_cells[0][0] != cells[0]): #if first cell doesn't contain any objects
            # previous cell is located at the left side of cells which are divided by the object(s)
            current_cell = cells[i]
            print("Current_cell: ", current_cell)
            next_cell = cells[i]+1
            for subneighboor in nonneighboor_cells:
                print("subneighboor: ", subneighboor)
                if subneighboor[0] == next_cell: #next cell is divided by an object
                    print("next cell sikintili")
                    adjacency_graph[current_cell] = subneighboor
                    for k in range(len(subneighboor)):
                        #if we already assigned something to subneighboord k
                        if adjacency_graph.get(subneighboor[k]):
                            print("debug")
                            print(subneighboor[k]) 
                            #adjacency_graph[subneighboor[k]].append(current_cell)
                        #else: #we are assigning for the first time
                            #adjacency_graph[subneighboor[k]] = current_cell
                    break #we already found so break out subneighboor loop
                else:  #current cell and next cell doesn't have object
                    adjacency_graph[current_cell] = next_cell
                    adjacency_graph[next_cell] = current_cell #bidirectional way
        #elif (nonneighboor_cells[0][0] == cells[0]):
    """

    # print("Debug")
    # print("Total cell number: ", total_cell_number)
    # print("Boundaries: ", boundaries)
    # print("Non-neighboor cells: ", nonneighboor_cells)
