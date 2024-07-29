import random

class CreateInstances:
    def __init__(self, buses, busCapacity, startingPoints, stations, shelters):
        self.buses = buses
        self.busCapacity = busCapacity
        self.startingPoints = startingPoints
        self.stations = stations
        self.shelters = shelters

    def createInstance(self, textFile):
        with open(textFile, "w") as file:
            file.write(str(self.buses) + ": " + str(self.busCapacity) + "\n")

            randomBuses = self.generateRandomNumbers(self.buses, self.startingPoints)
            file.write(str(self.startingPoints) + ": " + " ".join([str(i) for i in randomBuses]) + "\n")

            randomStationsPeople = random.randint(self.stations + 10, self.stations + 15) # Create bigger instances idk
            stationsPeople = self.busCapacity * randomStationsPeople
            randomStations = self.generateRandomNumbers(randomStationsPeople, self.stations)
            file.write(str(self.stations) + ": " + str(stationsPeople) + ": " + " ".join([str(i * self.busCapacity) for i in randomStations]) + "\n")

            randomSheltersDifference = randomStationsPeople + random.randint(1, 10)
            sheltersCapacity = stationsPeople + (self.busCapacity * (randomSheltersDifference - randomStationsPeople))
            randomShelters = self.generateRandomNumbers(randomSheltersDifference, self.shelters)
            file.write(str(self.shelters) + ": " + str(sheltersCapacity) + ": " + " ".join([str(i * self.busCapacity) for i in randomShelters]) + "\n")

            file.write("\n")
            for i in range(self.startingPoints):
                file.write(str(i + 1) + ": " + " ".join([str(random.randint(1, 10)) for _ in range(self.stations)]) + "\n")
            file.write("\n")
            for i in range(self.stations):
                file.write(str(i + 1) + ": " + " ".join([str(random.randint(1, 10)) for _ in range(self.shelters)]) + "\n")

    def generateRandomNumbers(self, total, num_numbers):
        numbers = [random.uniform(1, 2) for _ in range(num_numbers)]
        s = sum(numbers)
        numbers = [round(total * (i/s)) for i in numbers]
        numbers[-1] = total - sum(numbers[:-1])  # adjust last value to make sum correct

        return numbers

startingPoints = int(input("Enter the number of starting points: "))
stations = int(input("Enter the number of stations: "))
shelters = int(input("Enter the number of shelters: "))
buses = int(input("Enter the number of buses: "))
busCapacity = int(input("Enter the bus capacity: "))

for i in range(7): # Seven random instances are created
    instance = CreateInstances(buses, busCapacity, startingPoints, stations, shelters)
    textFile = "instancias/InstanceBEP-" + str(instance.startingPoints) + "-" + str(instance.stations) + "-" + str(instance.shelters) + "-" + str(instance.buses) + "_" + str(i) + ".txt"
    instance.createInstance(textFile=textFile)
