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

betweenCertainHours = 1 # TODO: make tickbox in GUI and link it here

if betweenCertainHours:
    for i in range(len(data)):
        if dataLine[i] == 'Bakerloo':
            dataTravelTime[i] /= 2


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


def common_line(list1, list2):
    answer = False
    for x in list1:
        if x in list2:
            answer = True
            return answer
    return answer


def dijkstra(starting_station, destination):  # TODO: hard test
    shortest_distance = {}
    track_predecessor = {}
    track_predecessor_line = {starting_station: stationLines[starting_station]}
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

    # TODO: make GUI displaying results color stations and stuff... I hate frontend D:
    if shortest_distance[destination] != 999999:
        print("Shortest journey time is: " + str(shortest_distance[destination] - 1) + " minutes")
        print("Optimal path is: " + str(track_path))
        print(track_lines)


#  inputs TODO: put them in GUI
startingStation = input_starting_station()
destination = input_destination()

dijkstra(startingStation, destination)
