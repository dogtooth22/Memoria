import time
import numpy as np
from flask import Flask, request
from flask_cors import CORS
from Instancia import Instancia
from ACO import ACO

app = Flask(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})

@app.route("/")
def hello_world():
    return [1,2,3,4,5,6,7]

@app.route("/", methods=['POST'])
def post_world():
    start_time = time.time()
    file = request.files['file']
    file_content = file.read()
    string = file_content.decode('utf-8')

    instancia = Instancia(string)
    print(request.form['algorithm'])
    n_iterations = int(request.form['n_iterations']); decay = float(request.form['decay']); alpha = float(request.form['alpha']); beta = float(request.form['beta']); q = float(request.form['q'])
    algorithm = request.form['algorithm']

    colony = ACO(instancia.distanciasPuntosEncuentrosRefugios, n_ants=instancia.numeroBuses, n_iterations=n_iterations, decay=decay,
                alpha=alpha, beta=beta, q=q, algorithm=algorithm, vehicle_capacity=instancia.capacidadBuses,
                shelters=instancia.capacidadesRefugios, pickup_points=instancia.personasEnPuntosEncuentro, starting_points=instancia.numeroEstaciones,
                starting_point_distances=instancia.distanciasEstacionesPuntosEncuentros,
                starting_point_buses=instancia.busesEstacion)
    
    best_route = colony.run()

    end_time = time.time()

    final_time = round((end_time - start_time), 2)

    best_route.tabulateResults(best_route)

    paths = [convert_numpy_int_to_int(i.path) for i in best_route.paths]

    print("\nExecution Time: " + str(final_time) + " seconds")
    return [instancia.distanciasEstacionesPuntosEncuentros.tolist(), instancia.distanciasPuntosEncuentrosRefugios.tolist(), paths, best_route.shelters.tolist(), final_time]

@app.route("/hello")
def hello():
    return "Hola"

def convert_numpy_int_to_int(item):
    if isinstance(item, np.integer):
        return int(item)
    elif isinstance(item, list):
        return [convert_numpy_int_to_int(i) for i in item]
    else:
        return item