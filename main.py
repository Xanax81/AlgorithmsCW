import base64
import copy
import io
import tkinter as tk
from collections import OrderedDict
from tkinter import ttk
import matplotlib.pyplot as plt
import networkx as nx
import pandas  # add pandas and xlrd into interpreter

data = pandas.read_excel('data.xlsx')  # receiving data from given excel file
dataLine = []
dataFromStation = []
dataToStation = []
dataTravelTime = []

for i in range(len(data)):
    dataLine.append(data['Line'][i])
    dataFromStation.append(data['From Station'][i])
    dataToStation.append(data['To Station'][i])
    dataTravelTime.append(data['Travel time Between stations'][i])

    # Some stations in .xlsx ends with blank space; following code will fix it
    if dataFromStation[i][-1] == ' ':
        dataFromStation[i] = dataFromStation[i][:-1]

    if dataToStation[i][-1] == ' ':
        dataToStation[i] = dataToStation[i][:-1]

dataActualTravelTime = dataTravelTime
for i in range(len(data)):
    dataActualTravelTime[i] += 1  # this is open doors timing
    # we can just increase all the times since first node will not be affected

possibleMoves = {}  # this is nested dictionary of travel times to all adjacent nodes (stations)
for i in range(len(data)):
    if dataFromStation[i] in possibleMoves.keys():
        possibleMoves[dataFromStation[i]][dataToStation[i]] = dataActualTravelTime[i]
    else:
        possibleMoves[dataFromStation[i]] = {}
        possibleMoves[dataFromStation[i]][dataToStation[i]] = dataActualTravelTime[i]

    if dataToStation[i] in possibleMoves.keys():
        possibleMoves[dataToStation[i]][dataFromStation[i]] = dataActualTravelTime[i]
    else:
        possibleMoves[dataToStation[i]] = {}
        possibleMoves[dataToStation[i]][dataFromStation[i]] = dataActualTravelTime[i]

stationLines = {}  # this is dictionary of lists of lines to which every station belongs to
for i in range(len(data)):
    if dataFromStation[i] in stationLines.keys():
        if dataLine[i] not in stationLines[dataFromStation[i]]:  # to avoid duplication
            stationLines[dataFromStation[i]].append(dataLine[i])
    else:
        stationLines[dataFromStation[i]] = []
        stationLines[dataFromStation[i]].append(dataLine[i])

    if dataToStation[i] in stationLines.keys():
        if dataLine[i] not in stationLines[dataToStation[i]]:
            stationLines[dataToStation[i]].append(dataLine[i])
    else:
        stationLines[dataToStation[i]] = []
        stationLines[dataToStation[i]].append(dataLine[i])


def common_line(list1, list2):
    answer = False
    for x in list1:
        if x in list2:
            answer = True
            return answer
    return answer


def dijkstra(starting_station, destination):
    shortest_distance = {}
    track_predecessor = {}
    track_predecessor_line = {starting_station: stationLines[starting_station]}
    unseen_nodes = copy.deepcopy(possibleMoves)

    for node in unseen_nodes:
        shortest_distance[node] = 999999
    shortest_distance[starting_station] = 0

    while unseen_nodes:
        minimal_distance_node = None

        for node in unseen_nodes:
            if minimal_distance_node is None:
                minimal_distance_node = node
            elif shortest_distance[node] < shortest_distance[minimal_distance_node]:
                minimal_distance_node = node

        path_options = unseen_nodes[minimal_distance_node].items()

        for childNode, weight in path_options:
            if not common_line(stationLines[childNode], track_predecessor_line[minimal_distance_node]):
                weight += 3
            if weight + shortest_distance[minimal_distance_node] < shortest_distance[childNode]:
                shortest_distance[childNode] = weight + shortest_distance[minimal_distance_node]
                track_predecessor[childNode] = minimal_distance_node
                track_predecessor_line[childNode] = stationLines[minimal_distance_node]
        if minimal_distance_node == destination:  # when the algorithm reaches the final destination it stops the calculation
            break
        unseen_nodes.pop(minimal_distance_node)

    current_node = destination

    track_path = []
    track_lines = []

    while current_node != starting_station:
        try:
            track_path.insert(0, current_node)
            track_lines.insert(0, track_predecessor_line[current_node])
            current_node = track_predecessor[current_node]
        except KeyError:
            print("Path is not reachable")
            break

    track_path.insert(0, starting_station)
    track_lines.insert(0, stationLines[starting_station])

    if shortest_distance[destination] != 999999:
        print("Optimal path is: " + str(track_path))
        print(track_lines)
        # Creating_Table_for_the_console
        # header_of_the_table
        print(': List of Stations in journey: List of Lines : Travel time to next station :Total time travel ')
        return shortest_distance[destination] - 1, track_path, track_lines


def transform_data(track_path, track_lines, is_bakerloo_lane):
    path = OrderedDict()  # store the path as dict as {station_name: [line_name, travel time, cumulative_total_tile]}
    global possibleMoves
    prev_station = None
    for station, lane in zip(track_path, track_lines):

        path[station] = [station, set(lane)]
        if not prev_station:
            path[station].append(1)  # first station is always 1
        else:
            prev_station[1] = prev_station[1].intersection(
                path[station][1])  # updating the lane name where both have the common lane

            if is_bakerloo_lane and 'Bakerloo' in prev_station[1]:
                prev_station[2] = ((prev_station[2] - 1) / 2) + 1  # Aboding time stays always stays same

            travel_time = possibleMoves[prev_station[0]][station]

            path[station].append(travel_time)
            # Updating travelling lane

            path[prev_station[0]] = path[prev_station[0]][
                                    1:5]  # Just keep lane name and station_name from the array
        # path[station].append(total_Time)
        prev_station = path[station]
    # path[track_path[-1]][2] = 0 # setting the last station to 0
    path[track_path[-1]] = path[track_path[-1]][1:5]  # last station

    total_time = 0
    for station in path.keys():
        travel_time = path[station][1]
        total_time += travel_time
        path[station].append(total_time)

    return path


class UndergroundGUI(tk.Tk):

    def __init__(self, root):
        super().__init__()
        self.root = root  # TK object
        self.root.geometry('1200x1200')  # Setting the size of the GUI window
        self.root.title('Fantastic Route Planner')  # Setting the name of the GUI window
        label_0 = ttk.Label(self.root, text='Welcome to Fantastic Route Planner', width="300",
                            font=("Calibri", 30))  # Adding a header to the GUI
        label_0.pack(padx=(250, 0))
        # User inputs
        self.user_starting_point = tk.StringVar()
        self.user_destination = tk.StringVar()

        starting_label = ttk.Label(self.root, text='Starting station:')  # Labelling the entry
        starting_label.pack()
        starting_entry = ttk.Entry(self.root, width=15,
                                   textvariable=self.user_starting_point)  # Creating an entry for user's input
        starting_entry.pack()

        destination_label = ttk.Label(self.root, text='Destination:')  # Labelling the entry
        destination_label.pack()
        self.destination_entry = ttk.Entry(self.root, width=15,
                                           textvariable=self.user_destination)  # Creating an entry for user's input
        self.destination_entry.pack()

        planning_button = ttk.Button(self.root, text='Start planning your journey',
                                     command=self.plan_journey_now)  # Creating a button to start planning the journey
        planning_button.pack()

        quit_button = ttk.Button(self.root, text='Exit Fantastic route Planner',
                                 command=self.root.destroy)  # Creating a button to exit the GUi
        quit_button.pack()
        self.bakerloo_Lane_checkbox = tk.IntVar()
        c = ttk.Checkbutton(root,
                            text='Tick the box if your journey take place between 9am-4pm or 7pm-midnight',
                            variable=self.bakerloo_Lane_checkbox,
                            onvalue=1,
                            offvalue=0)  # Adding the checkbox for the extra functionality
        c.pack()
        # Store journey image
        self.image_journey = tk.PhotoImage()  # Creating a space in the GUI for the table's image
        self.image_journey_label = tk.Label(self.root, image=self.image_journey, padx=20, pady=20)
        self.image_journey_label.pack()

    def update_journey_plan(self, img):
        self.image_journey.put(img)
        self.image_journey_label.pack()

    def plan_journey_now(self):

        print("Planning Journey")
        # getting the input values from the user
        start_station = self.user_starting_point.get().lower()
        destination = self.user_destination.get().lower()

        # calling dijkstra Algorithm to find the route
        path = dijkstra(start_station, destination)
        transformed_data = transform_data(path[1], path[2], self.bakerloo_Lane_checkbox.get())

        for station in transformed_data:
            print(':', station, " " * (25 - len(station)), ':', " OR ".join(transformed_data[station][0]), ":",
                  transformed_data[station][1], ":", transformed_data[station][2])  # print to console
        # initializing an empty graph
        G = nx.DiGraph()
        prev_station = None
        formatted_edge_labels = {}  # Using labels for the each path
        for station in transformed_data.keys():
            G.add_node(station)
            if prev_station:
                G.add_edge(prev_station, station, weight=transformed_data[station][1])  # Adding node to the graph
                formatted_edge_labels[(prev_station, station)] = transformed_data[station][
                    1]  # Time of current station to next station
            prev_station = station

        pos = nx.spring_layout(G)  # Position nodes in adjacent
        plt.clf()  # Clears the current figure

        columns_labels = ["Station", "Travel Time", "Total Time", "Lane"]
        plt.subplots_adjust(left=0.2, top=0.8)
        fig, axs = plt.subplots(2, 1)

        clust_data = [[station] + transformed_data[station][1:3] + [' OR '.join(transformed_data[station][0:1][0])]
                      for station in transformed_data.keys()]  # Combining data to fit in the table
        print(clust_data)
        axs[0].axis('tight')
        axs[0].axis('off')

        the_table = axs[0].table(cellText=clust_data, colLabels=columns_labels,
                                 loc='center')  # Creating table on the figure
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(5.5)
        the_table.auto_set_column_width(
            col=list(range(len(columns_labels))))  # Provide integer list of columns to adjust

        nx.draw(G, pos, font_size=3, with_labels=True, arrows=True,
                edge_color='b', arrowsize=5, arrowstyle='fancy', ax=axs[1]
                )  # drawing the graph on the 1st axis
        nx.draw_networkx_edge_labels(G, pos, edge_labels=formatted_edge_labels, font_color='red', )
        # labels to the station
        axs[1].set_axis_off()
        # Saving the image on the memory for it display on the GUI
        pic_IObytes = io.BytesIO()
        plt.savefig(pic_IObytes, format='png', dpi=200)
        pic_IObytes.seek(0)
        pic_hash = base64.b64encode(pic_IObytes.read())
        self.update_journey_plan(pic_hash)
        # Saves cache onto the hard disk
        plt.savefig('plotgraph.png', dpi=800, bbox_inches='tight')

        print("TOTAL JOURNEY TIME:", transformed_data[list(transformed_data.keys())[-1]][2])


def start_gui():
    root = tk.Tk()
    app = UndergroundGUI(root)
    root.mainloop()


if __name__ == '__main__':
    start_gui()
