from ACO import ACO
from Instancia import Instancia
import time
import sys

start_time = time.time()

n_iterations = int(sys.argv[1])
alpha = float(sys.argv[2])
beta = float(sys.argv[3])
decay = float(sys.argv[4])
q = float(sys.argv[5])

instancia = Instancia(sys.argv[6])

colony = ACO(instancia.distanciasPuntosEncuentrosRefugios, n_ants=instancia.numeroBuses, n_iterations=n_iterations, decay=decay,
             alpha=alpha, beta=beta, q=q, algorithm="ant_quantity", vehicle_capacity=instancia.capacidadBuses,
             shelters=instancia.capacidadesRefugios, pickup_points=instancia.personasEnPuntosEncuentro, starting_points=instancia.numeroEstaciones,
             starting_point_distances=instancia.distanciasEstacionesPuntosEncuentros,
             starting_point_buses=instancia.busesEstacion)

best_route = colony.run()

end_time = time.time()

best_route.tabulateResults(best_route)
best_route.plotSolutions(best_route.statistics)

print("\nExecution Time: " + str(round((end_time - start_time), 2)) + " seconds")