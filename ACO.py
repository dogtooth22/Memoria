import numpy as np
import copy
import gc
from Result import Result

class Ant:
    def __init__(self, position, capacity):
        self.position = position
        self.capacity = capacity
        self.carrying = capacity
        self.path = []
        self.pathDistance = 0

class ACO:
    def __init__(self, distances, n_ants, n_iterations, decay, 
                 alpha, beta, q, algorithm, vehicle_capacity, 
                 shelters, pickup_points, starting_points, 
                 starting_point_distances, starting_point_buses):
        
        self.distances = distances # From meeting points to shelters
        self.pheromone = np.ones(self.distances.shape) / len(self.distances)
        self.all_inds = range(distances.shape[1])
        self.n_ants = n_ants # Recomended to be equal as the number of cities
        # self.n_best = n_best # Maximum paths which pheromones will be spread. Should be deleted for now
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha # The higher the alpha, the more are emphasized the pheromones
        self.beta = beta # The higher the beta, the more is emphasized the distance between cities
        self.q = q
        self.algorithm = algorithm
        self.vehicle_capacity = vehicle_capacity
        self.shelters = shelters
        self.pickup_points = pickup_points
        self.starting_points = starting_points
        self.starting_point_distances = starting_point_distances # From starting points to meeting points
        self.starting_point_buses = starting_point_buses
        self.ants = [Ant(i, self.vehicle_capacity) for i in range(self.n_ants)] # Ants are created
        self.original_pickup_points = np.copy(pickup_points) # For copy purposes
        self.original_shelters = np.copy(shelters) # For copy purposes

    def run(self): # Maybe have a parameter to improve the m best solutions
        bestSolution = copy.deepcopy(self.ants)
        bestSolutionPathDistance = np.inf
        shelterSolution = np.copy(self.shelters)
        pickupPointsSolution = np.copy(self.pickup_points)

        statistics = []
        bestSolutions = []
        shelterSolutions = []
        pickupPointsSolutions = []
        bestSolutionsPathDistance = []

        previousPheromones = np.zeros(self.distances.shape) / len(self.distances)

        for i in range(self.n_iterations):
            self.gen_all_paths(self.ants) # There are n_ants paths
            self.spread_pheronomes(self.ants)
            longestPath = max(self.ants, key=lambda x: x.pathDistance)
            #mean = np.mean([ant.pathDistance for ant in self.ants]) # Mean of all paths
            #minimum = min([ant.pathDistance for ant in self.ants]) # Minimum of all paths

            statistics.append(longestPath.pathDistance)
            #statistics.append(mean)
            # All solutions are saved, this is because the shorter initial solution is not always the best
            #if longestPath.pathDistance < bestSolutionPathDistance:
            bestSolution = copy.deepcopy(self.ants)
            bestSolutionPathDistance = longestPath.pathDistance
            shelterSolution = np.copy(self.shelters)
            pickupPointsSolution = np.copy(self.pickup_points)

            bestSolutions.append(bestSolution)
            shelterSolutions.append(shelterSolution)
            pickupPointsSolutions.append(pickupPointsSolution)
            bestSolutionsPathDistance.append(longestPath.pathDistance)

            #elif longestPath.pathDistance == bestSolutionPathDistance:
            #    bestSolution = copy.deepcopy(self.ants)
            #    bestSolutions.append(bestSolution)
            #    shelterSolutions.append(np.copy(self.shelters))
            #    pickupPointsSolutions.append(np.copy(self.pickup_points))
            #    bestSolutionsPathDistance.append(longestPath.pathDistance)

            #else:
            #    maxDistance = bestSolutionsPathDistance.index(max(bestSolutionsPathDistance))
            #    if longestPath.pathDistance < bestSolutionsPathDistance[maxDistance]:
            #        bestSolutions.pop(maxDistance)
            #        shelterSolutions.pop(maxDistance)
            #        pickupPointsSolutions.pop(maxDistance)
            #        bestSolutionsPathDistance.pop(maxDistance)

            #        bestSolution = copy.deepcopy(self.ants)
            #        bestSolutions.append(bestSolution)
            #        shelterSolutions.append(np.copy(self.shelters))
            #        pickupPointsSolutions.append(np.copy(self.pickup_points))
            #        bestSolutionsPathDistance.append(longestPath.pathDistance)

            #if (len(bestSolutions) > 10): # Compare the 10 best solutions, when there are more than 10, the worst solution is deleted
            #    maxDistance = bestSolutionsPathDistance.index(max(bestSolutionsPathDistance))
            #    bestSolutions.pop(maxDistance)
            #    shelterSolutions.pop(maxDistance)
            #    pickupPointsSolutions.pop(maxDistance)
            #    bestSolutionsPathDistance.pop(maxDistance)

            self.pheromone = (1 - self.decay)*self.pheromone + (self.pheromone - previousPheromones) # Pheromones are updated. Delta is the new pheromones minus the old pheromones
            previousPheromones = self.pheromone
            
            # Reset values
            for i in range(self.n_ants):
                self.ants[i].path = []
                self.ants[i].pathDistance = 0

            self.pickup_points = np.copy(self.original_pickup_points)
            self.shelters = np.copy(self.original_shelters)

        improvedResults = []
        originalResults = []
        for i in range(len(bestSolutions)):
            result = Result(bestSolutions[i], bestSolutionsPathDistance[i], shelterSolutions[i], pickupPointsSolutions[i])
            result.transformPaths(result)
            originalResults.append(result)
            improvedResult = self.improveBestSolution(result)
            #print("Original longest path: " + str(result.longestDistance) + ", Improved longest path: " + str(improvedResult.longestDistance))
            improvedResults.append(improvedResult)

        betterSolutionIndex = improvedResults.index(min(improvedResults, key=lambda x: x.longestDistance))
        originalBestSolution = originalResults[betterSolutionIndex]
        originalBestSolution.tabulateResults(originalBestSolution)

        betterSolution = improvedResults[betterSolutionIndex]
        betterSolution.statistics = statistics

        min_values = [x for x in range(len(improvedResults)) if improvedResults[x].longestDistance == betterSolution.longestDistance]

        print(min_values)

        return betterSolution

    def gen_all_paths(self, ants):
        for i in range(self.starting_points):
            for j in range(self.starting_point_buses[i]):
                norm_row = (1 / self.starting_point_distances[i]) / (sum(1 / self.starting_point_distances[i]))
                for k in range(len(self.pickup_points)):
                    if self.pickup_points[k] == 0:
                        norm_row[k] = 0

                norm_row /= norm_row.sum()
                rango = range(len(norm_row))
                move = np.random.choice(rango, 1, p=norm_row)[0]
                if i == 0:
                    ants[j].path.append([i, move])
                    ants[j].pathDistance += self.starting_point_distances[i][move]
                else:
                    ants[sum(self.starting_point_buses[:i]) + j].path.append([i, move])
                    ants[sum(self.starting_point_buses[:i]) + j].pathDistance += self.starting_point_distances[i][move]
                self.pickup_points[move] -= self.vehicle_capacity
                # add carrying capacity

        while (sum(self.pickup_points) > 0):
            for i in range(self.n_ants):
                if sum(self.pickup_points) == 0:
                    break
                ant_position = ants[i].path[len(ants[i].path) - 1][1]
                firstMove = self.pick_move_shelter(ant_position, i)
                ants[i].path.append([ant_position, firstMove])
            
            for i in range(self.n_ants):
                ant_position = ants[i].path[len(ants[i].path) - 1][1]
                secondMove = self.pick_move_meeting_point(ant_position, i)
                if secondMove == None:
                    for j in range(i):
                        ant_position = ants[j].path[len(ants[j].path) - 1][1]
                        firstMove = self.pick_move_shelter(ant_position, j)
                        ants[j].path.append([ant_position, firstMove])
                    return ants
                ants[i].path.append([ant_position, secondMove])
        return ants
    
    def pick_move_shelter(self, ant_position, ant_id): # From meeting point to shelter
        pheromone = np.copy(self.pheromone[ant_position])

        row = pheromone ** self.alpha * ((1.0 / self.distances[ant_position]) ** self.beta)
        for i in range(len(self.shelters)):
            if row[i] == 0 and self.shelters[i] != 0: # This is for moments where there are only a couple of options to choose and the pheromones are zero
                # When decay is too high, pheromones tend to be zero, which might be a problem
                row[i] = 1
            if self.shelters[i] == 0:
                row[i] = 0
        norm_row = row / row.sum()
        try: # There's a moment where there are zeros in the row
            move = np.random.choice(self.all_inds, 1, p=norm_row)[0]

            if (self.ants[ant_id].carrying >= self.shelters[move]):
                self.shelters[move] = 0
            else:
                self.shelters[move] -= self.ants[ant_id].carrying

            self.ants[ant_id].carrying = self.ants[ant_id].capacity
            self.ants[ant_id].pathDistance += self.distances[ant_position][move]

            return move
        except:
            print("Shelter", row, norm_row)
            #self.pheromone = np.ones(self.distances.shape) / len(self.distances) # Pheromones are reseted
    
    def pick_move_meeting_point(self, ant_position, ant_id): # From shelter to meeting point
        if (sum(self.pickup_points) == 0):
            return
        pheromone = np.copy(self.pheromone[:, ant_position])

        row = pheromone ** self.alpha * ((1.0 / self.distances[:, ant_position]) ** self.beta)
        for i in range(len(self.pickup_points)):
            if row[i] == 0 and self.pickup_points[i] != 0: # This is for moments where there are only a couple of options to choose and the pheromones are zero
                row[i] = 1
            if self.pickup_points[i] == 0:
                row[i] = 0
        norm_row = row / row.sum()
        try:
            move = np.random.choice(range(self.distances.shape[0]), 1, p=norm_row)[0]
            if ((self.ants[ant_id].capacity >= self.pickup_points[move]) and (self.pickup_points[move] > 0)):
                self.ants[ant_id].carrying = self.pickup_points[move]
                self.pickup_points[move] = 0
            else:
                self.pickup_points[move] -= self.ants[ant_id].carrying

            self.ants[ant_id].pathDistance += self.distances.T[ant_position][move]
            return move
        except:
            print("Meeting point", row, norm_row)
            #self.pheromone = np.ones(self.distances.shape) / len(self.distances) # Pheromones are reseted. Necessary but I don't know why

    def spread_pheronomes(self, ants):
        sorted_paths = sorted(ants, key=lambda x: x.pathDistance)
        for ant in sorted_paths:
            for i in range(1, len(ant.path)): # First paths don't update pheromones
                move = ant.path[i]
                if i % 2 == 0:
                    move = [ant.path[i][1], ant.path[i][0]]
                if self.algorithm == "ant_density":
                    self.pheromone[move[0]][move[1]] += self.q
                if self.algorithm == "ant_quantity":
                    self.pheromone[move[0]][move[1]] += self.q / self.distances[move[0]][move[1]]
                if self.algorithm == "ant_cycle":
                    self.pheromone[move[0]][move[1]] += self.q / ant.pathDistance

    def improveBestSolution(self, result):
        resetWhile = True
        resultCopy = copy.deepcopy(result)
        while resetWhile:
            resetWhile = False 
            for i in range(len(resultCopy.paths)):
                if resultCopy.paths[i].pathDistance == resultCopy.longestDistance:
                    popedPath = resultCopy.paths[i].path[-1]
                    for j in range(len(resultCopy.paths)):
                        if j != i:
                            if len(resultCopy.paths[i].path) == 2:
                                break
                            possiblePaths = []
                            for k in range(len(resultCopy.paths[j].path) - 1): # -1 to avoid the second trip
                                newPath = copy.deepcopy(resultCopy.paths[j].path)
                                newPath.insert(len(newPath) - k, popedPath)
                                possiblePaths.append(newPath)
                                #del newPath
                                #gc.collect()
                            bestPath = min(possiblePaths, key=lambda x: resultCopy.calculatePathDistance(x, self.starting_point_distances, self.distances))
                            bestPathDistance = resultCopy.calculatePathDistance(bestPath, self.starting_point_distances, self.distances)
                            if bestPathDistance < resultCopy.longestDistance:
                                resultCopy.paths[j].path = bestPath
                                resultCopy.paths[j].pathDistance = bestPathDistance
                                resultCopy.paths[i].path.pop()
                                resultCopy.paths[i].pathDistance = result.calculatePathDistance(resultCopy.paths[i].path, self.starting_point_distances, self.distances)
                                resultCopy.longestDistance = max([resultCopy.paths[i].pathDistance for i in range(len(resultCopy.paths))])
                                resetWhile = True
                                break
                if resetWhile:
                    break
        #del result # This is to free memory
        #gc.collect()  # Garbage collector is called, to improve performance
        return resultCopy