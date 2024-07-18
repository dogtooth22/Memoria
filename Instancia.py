import numpy as np

class Instancia:
    def __init__(self, fileName):
        self.fileName = fileName
        f = open(fileName, 'r')

        firstLine = f.readline().strip("\n").split(" ")
        self.numeroBuses = int(firstLine[0].split(":")[0])
        self.capacidadBuses = int(firstLine[1])

        secondLine = f.readline().strip("\n").split(":")
        self.numeroEstaciones = int(secondLine[0])
        self.busesEstacion = list(map(int, secondLine[1].strip().split(" ")))

        thirdLine = f.readline().strip("\n").split(":")
        self.puntosEncuentro = int(thirdLine[0])
        self.personasTotal = int(thirdLine[1])
        self.personasEnPuntosEncuentro = list(map(int, thirdLine[2].strip().split(" ")))

        fourthLine = f.readline().strip("\n").split(":")
        self.refugios = int(fourthLine[0])
        self.sumaCapacidadesRefugios = int(fourthLine[1])
        self.capacidadesRefugios = list(map(int, fourthLine[2].strip().split(" ")))

        f.readline() # Empty line
        self.distanciasEstacionesPuntosEncuentros = []

        for _ in range(self.numeroEstaciones):
            distanciasEstacionPuntosEncuentros = f.readline().strip("\n").split(":")
            self.distanciasEstacionesPuntosEncuentros.append(distanciasEstacionPuntosEncuentros[1].strip().split(" "))

        self.distanciasEstacionesPuntosEncuentros = np.array(self.distanciasEstacionesPuntosEncuentros).astype(int)

        f.readline() # Empty line
        self.distanciasPuntosEncuentrosRefugios = []

        for _ in range(self.puntosEncuentro):
            distanciasPuntoEncuentroRefugios = f.readline().strip("\n").split(":")
            self.distanciasPuntosEncuentrosRefugios.append(distanciasPuntoEncuentroRefugios[1].strip().split(" "))

        self.distanciasPuntosEncuentrosRefugios = np.array(self.distanciasPuntosEncuentrosRefugios).astype(int)