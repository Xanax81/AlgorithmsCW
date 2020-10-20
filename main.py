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

possibleMoves = {}  # this is nested dictionary of travel times to all adjacent nodes (stations)
for i in range(len(data)):
    if dataFromStation[i] in possibleMoves.keys():
        possibleMoves[dataFromStation[i]][dataToStation[i]] = dataTravelTime[i]
    else:
        possibleMoves[dataFromStation[i]] = {}
        possibleMoves[dataFromStation[i]][dataToStation[i]] = dataTravelTime[i]

    if dataToStation[i] in possibleMoves.keys():
        possibleMoves[dataToStation[i]][dataFromStation[i]] = dataTravelTime[i]
    else:
        possibleMoves[dataToStation[i]] = {}
        possibleMoves[dataToStation[i]][dataFromStation[i]] = dataTravelTime[i]

def input_starting_station():
    startingStation = input("What is your starting station?")
    if startingStation not in dataFromStation:
        if startingStation not in dataToStation:
            print("There is no such a station D:")
            startingStation = input_starting_station()
            return startingStation
        else:
            return startingStation
    else:
        return startingStation


def input_destination():
    destination = input("What is your destination?")
    if destination not in dataToStation:
        if destination not in dataFromStation:
            print("There is no such a station D:")
            destination = input_destination()
            return destination
        else:
            return destination
    else:
        return destination


def dijkstra(starting_station, destination):  # TODO: implement tracking line and add +1 to time whenever we swap trains
    shortest_distance = {}
    track_predecessor = {}
    unseen_nodes = possibleMoves

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

        path_options = possibleMoves[minimal_distance_node].items()

        for childNode, weight in path_options:
            if weight + shortest_distance[minimal_distance_node] < shortest_distance[childNode]:
                shortest_distance[childNode] = weight + shortest_distance[minimal_distance_node]
                track_predecessor[childNode] = minimal_distance_node

        unseen_nodes.pop(minimal_distance_node)

    current_node = destination

    track_path = []

    while current_node != starting_station:
        try:
            track_path.insert(0, current_node)
            current_node = track_predecessor[current_node]
        except KeyError:
            print("Path is not reachable")
            break

    track_path.insert(0, starting_station)

    # TODO: make GUI displaying results color stations and stuff... I hate frontend D:
    if shortest_distance[destination] != 999999:
        print("Shortest journey time is: " + str(shortest_distance[destination]) + "minutes")
        print("Optimal path is: " + str(track_path))


#  inputs TODO: put them in GUI
startingStation = input_starting_station()
destination = input_destination()

dijkstra(startingStation, destination)
