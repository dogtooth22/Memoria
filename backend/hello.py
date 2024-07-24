import time
import numpy as np
import base64
import zipfile
from io import BytesIO, StringIO
from flask import Flask, request, send_file
from flask_cors import CORS
from Instancia import Instancia
from ACO import ACO

app = Flask(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})

@app.route("/", methods=['POST'])
def post_world():
    start_time = time.time()
    file = request.files['file']
    file_content = file.read()
    string = file_content.decode('utf-8')

    instancia = Instancia(string)
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
    #best_route.tabulateResults(best_route)

    paths = [convert_numpy_int_to_int(i.path) for i in best_route.paths]

    pathsDistances = [convert_numpy_int_to_int(i.pathDistance) for i in best_route.paths]

    image = best_route.plotSolutions(best_route.statistics)
    
    output = BytesIO()
    image.savefig(output, format='png')
    output.seek(0)  # Rewind the buffer

    encoded_image = base64.b64encode(output.read()).decode('utf-8')
    
    return [instancia.distanciasEstacionesPuntosEncuentros.tolist(), instancia.distanciasPuntosEncuentrosRefugios.tolist(), paths, pathsDistances, best_route.shelters.tolist(), final_time, encoded_image]

@app.route("/download", methods=['POST'])
def download_zip():
    img = request.form['img']
    image_bytes = base64.b64decode(img + '===')

    data = BytesIO()
    #in_memory_file = StringIO()
    #in_memory_file.write('This is the content of the new file.')
    #in_memory_file.seek(0)

    #fig, ax = plt.subplots()
    #ax.plot([0, 1, 2], [0, 1, 4])
    image_output = BytesIO()
    image_output.write(image_bytes)
    image_output.seek(0)

    with zipfile.ZipFile(data, mode='w') as z:
        #z.writestr('new_file.txt', in_memory_file.read())
        z.writestr('plot.png', image_output.getvalue())

    data.seek(0)
    return send_file(data, mimetype='application/zip', as_attachment=True, download_name='data.zip')

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
