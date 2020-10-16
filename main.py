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

def input_starting_station():
    startingStation = input("What is your starting station?")
    if startingStation not in dataFromStation:
        if startingStation not in dataToStation:
            print("There is no such a station D:")
            input_starting_station()
    else:
        return startingStation


def input_destination():
    destination = input("What is your destination?")
    if destination not in dataToStation:
        if destination not in dataFromStation:
            print("There is no such a station D:")
            input_destination()
    else:
        return destination

#  inputs TODO: put them in GUI
startingStation = input_starting_station()
destination = input_destination()
