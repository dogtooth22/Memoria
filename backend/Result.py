from tabulate import tabulate
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import copy

matplotlib.use('agg')

class Result:
    def __init__(self, paths, longestDistance, shelters, pickupPoints):
        self.paths = paths
        self.longestDistance = longestDistance
        self.shelters = shelters
        self.pickupPoints = pickupPoints
        self.statistics = []

    def tabulateResults(self, result):
        resultCopy = copy.deepcopy(result.paths)
        resultCopy = self.plusOneTable(resultCopy)

        busDictionary = {"Bus": [i + 1 for i in range(len(resultCopy))]}
        maxPath = max([len(resultCopy[i].path) for i in range(len(resultCopy))]) # Max number of paths for a bus

        for i in range(maxPath):
            #if i % 2 == 1 or i == 0: # Deleted this line bc I did a transformPath function before
            bus = "Trip " + str(i + 1)
            route = []
            for j in range(len(resultCopy)):
                if i < len(resultCopy[j].path):
                    route.append(tuple(resultCopy[j].path[i]))
                else:
                    route.append("")
            busDictionary[bus] = route

        busDictionary["Distance"] = [resultCopy[i].pathDistance for i in range(len(resultCopy))]

        print("\n" + tabulate(busDictionary, headers="keys", tablefmt="github"))
        print("\nLongest Path: " + str(result.longestDistance))
        print("\nFinal Shelters")

        sheltersDictionary = {"Shelters": [i + 1 for i in range(len(result.shelters))], "Available": result.shelters}
        print("\n" + tabulate(sheltersDictionary, headers="keys", tablefmt="github"))

    def plusOneTable(self, paths): # This function adds 1 to the indexes of the paths, for better readability
        for i in range(len(paths)):
            for j in range(len(paths[i].path)):
                for k in range(len(paths[i].path[j])):
                    paths[i].path[j][k] += 1
        return paths
    
    def transformPaths(self, result): # This function is made to make simpler tables
        for i in range(len(result.paths)):
            newPaths = []
            #print(result.paths[i].path)
            for j in range(len(result.paths[i].path)):
                if j % 2 == 1 or j == 0:
                    newPaths.append(result.paths[i].path[j])
            result.paths[i].path = newPaths
    
    def calculateDistances(self, paths, firstDistances, secondDistances): # This function is for larger tables. Not used atm
        for i in range(len(paths)):
            paths[i].pathDistance = firstDistances[paths[i].path[0][0]][paths[i].path[0][1]]
            for j in range(1, len(paths[i].path)):
                if j % 2 == 1:
                    paths[i].pathDistance += secondDistances[paths[i].path[j][0]][paths[i].path[j][1]]
                else:
                    paths[i].pathDistance += secondDistances.T[paths[i].path[j][0]][paths[i].path[j][1]]
    
    def calculateShorterDistances(self, paths, firstDistances, secondDistances): # This function is for shorter tables. Not used atm
        for i in range(len(paths)):
            paths[i].pathDistance = firstDistances[paths[i].path[0][0]][paths[i].path[0][1]]
            for j in range(1, len(paths[i].path), 2):
                paths[i].pathDistance += secondDistances[paths[i].path[j][0]][paths[i].path[j][1]]
                paths[i].pathDistance += secondDistances.T[paths[i].path[j][i]][paths[i].path[j + 1][0]]
    
    def calculatePathDistance(self, path, firstDistances, secondDistances): # This function is for single paths
        distance = firstDistances[path[0][0]][path[0][1]]
        for i in range(1, len(path)):
            distance += secondDistances[path[i][0]][path[i][1]]
            if i != len(path) - 1:
                distance += secondDistances.T[path[i][1]][path[i + 1][0]]
        return distance
    
    def plotSolutions(self, solutions): # When there are larger iterations, correlation is not as visible, but with smaller iterations there is a little correlation.
        # I believe this is important because it can escape local maximums. Might try a reset of the pheromones when the correlation is too low
        
        plt.close()

        xpoints = np.array([i for i in range(len(solutions))])
        ypoints = solutions

        plt.plot(xpoints, ypoints, label='Results')
        plt.title("Longest Path per Iteration")
        plt.xlabel("Iterations")
        plt.ylabel("Longest Path")

        corr = np.corrcoef(xpoints, ypoints)
        plt.plot(np.unique(xpoints), np.poly1d(np.polyfit(xpoints, ypoints, 1)) (np.unique(xpoints)), color='red', label='Correlation: ' + str(round(corr[0][1], 3)))
        plt.legend(loc='upper right')
        return plt
