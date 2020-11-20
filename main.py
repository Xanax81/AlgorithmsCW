import copy
import time
import tkinter as tk
from collections import OrderedDict
from tkinter import ttk

import pandas  # add pandas and xlrd into interpreter

start_time = time.time()
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
    # we can just increase all the times since first node will not be affected and last one is common for all paths
    # just have to remember to subtract 1 from final solution (destination node time)
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
        print("Shortest journey time is: " + str(shortest_distance[destination] - 1) + " minutes")
        print("Optimal path is: " + str(track_path))
        print(track_lines)
        # Creating_Table
        # header
        print(': List of Stations in journey: List of Lines : Travel time to next station :Total time travel ')
        # for item in track_path :
        #         print(':',item," "*(25-len(item)),':')
        return shortest_distance[destination] - 1, track_path, track_lines


class UndergroundGUI(tk.Tk):

    def __init__(self, root):

        self.root = root  # TK object
        self.root.geometry('620x400')
        Label_0 = ttk.Label(self.root, text='Welcome to Fantastic Route Planner', width="300", font=("Calibri", 30))
        Label_0.pack(padx=(10, 0))

        # User inputs
        self.user_starting_point = tk.StringVar()
        self.user_destination = tk.StringVar()

        staring_label = ttk.Label(self.root, text='Starting station:')
        staring_label.pack()
        starting_entry = ttk.Entry(self.root, width=15, textvariable=self.user_starting_point)
        starting_entry.pack()

        destination_label = ttk.Label(self.root, text='Destination:')
        destination_label.pack()
        self.destination_entry = ttk.Entry(self.root, width=15, textvariable=self.user_destination)
        self.destination_entry.pack()

        Planning_button = ttk.Button(self.root, text='Start planning your journey', command=self.plan_journey_now)
        Planning_button.pack()

        quit_button = ttk.Button(self.root, text='Exit Fantastic route Planner', command=self.root.destroy)
        quit_button.pack()
        self.bakerloo_Lane_checkbox = tk.IntVar()
        c = ttk.Checkbutton(root,
                            text='Tick the box if your journey take place between 9am-4pm or 7pm-midnight',
                            variable=self.bakerloo_Lane_checkbox,
                            onvalue=1,
                            offvalue=0)
        c.pack()

    def tranform_data(self, track_path, track_lines, is_bakerloo_lane):
        path = OrderedDict()  # store the path as dict as {station_name: [line_name, travel time]}
        global possibleMoves
        prev_station = None
        total_Time = 0
        for station, lane in zip(track_path, track_lines):

            path[station] = [station, set(lane)]
            if not prev_station:
                path[station].append(1)  # first station is always 1
                total_Time += 1
            else:
                travel_time = possibleMoves[prev_station[0]][station] if not is_bakerloo_lane \
                    else possibleMoves[prev_station[0]][station] / 2
                path[station].append(travel_time)
                total_Time += travel_time
                # Updating travelling lane
                prev_station[1] = prev_station[1].intersection(
                    path[station][1])  # updating the lane name where both have the common lane
                path[prev_station[0]] = path[prev_station[0]][
                                        1:5]  # Just keep lane name and station_name from the array
            path[station].append(total_Time)
            prev_station = path[station]
        # path[track_path[-1]][2] = 0 # setting the last station to 0
        path[track_path[-1]] = path[track_path[-1]][1:5]  # last station
        return path

    def plan_journey_now(self):

        print("Planning Journey")
        # getting the input values
        start_station = self.user_starting_point.get()
        destination = self.user_destination.get()
        # calling dijkstra alg find the route
        path = dijkstra(start_station, destination)
        tranformed_data = self.tranform_data(path[1], path[2],
                                             self.bakerloo_Lane_checkbox.get())

        for station in tranformed_data:
            print(':', station, " " * (25 - len(station)), ':', " OR ".join(tranformed_data[station][0]), ":",
                  tranformed_data[station][1], ":", tranformed_data[station][2])

        print("If you are travelling within the stated time and your journey uses bakerloo line (else ignore this line )your total travel time will decrease to:", tranformed_data[list(tranformed_data.keys())[-1]][2],'minutes')


    def input_starting_station(self):

        # TODO: consider if the user input is lower case, it's also a bit confusing, maybe recheck the logic and the code
        startingStation = self.user_starting_point.get()
        print(startingStation)
        if startingStation not in dataFromStation:
            if startingStation not in dataToStation:
                print("There is no such a station D:")
                startingStation = self.input_starting_station()
                return startingStation
            else:
                return startingStation
        else:
            return startingStation

    def input_destination(self):
        destination = self.user_destination.get()
        print(destination)
        if destination not in dataToStation:
            if destination not in dataFromStation:
                print("There is no such a station D:")
                destination = self.input_destination()
                return destination
            else:
                return destination
        else:
            return destination


def start_gui():
    root = tk.Tk()
    app = UndergroundGUI(root)
    root.mainloop()


if __name__ == '__main__':
    start_gui()
    print("time elapsed: {:.2f}s".format(time.time() - start_time))
