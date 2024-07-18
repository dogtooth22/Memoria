import numpy as np

class Instancia:
    def __init__(self, file):
        splited = file.splitlines()
        firstLine = splited[0].split(":")
        self.numeroBuses = int(firstLine[0])
        self.capacidadBuses = int(firstLine[1])

        secondLine = splited[1].split(":")
        self.numeroEstaciones = int(secondLine[0])
        self.busesEstacion = list(map(int, secondLine[1].strip().split(" ")))

        thirdLine = splited[2].split(":")
        self.puntosEncuentro = int(thirdLine[0])
        self.personasTotal = int(thirdLine[1])
        self.personasEnPuntosEncuentro = list(map(int, thirdLine[2].strip().split(" ")))

        fourthLine = splited[3].split(":")
        self.refugios = int(fourthLine[0])
        self.sumaCapacidadesRefugios = int(fourthLine[1])
        self.capacidadesRefugios = list(map(int, fourthLine[2].strip().split(" ")))

        self.distanciasEstacionesPuntosEncuentros = []

        for i in range(self.numeroEstaciones):
            distanciasEstacionPuntosEncuentros = splited[5 + i].strip("\n").split(":")
            self.distanciasEstacionesPuntosEncuentros.append(distanciasEstacionPuntosEncuentros[1].strip().split(" "))

        self.distanciasEstacionesPuntosEncuentros = np.array(self.distanciasEstacionesPuntosEncuentros).astype(int)

        self.distanciasPuntosEncuentrosRefugios = []

        for i in range(self.puntosEncuentro):
            distanciasPuntoEncuentroRefugios = splited[6 + self.numeroEstaciones + i].split(":")
            self.distanciasPuntosEncuentrosRefugios.append(distanciasPuntoEncuentroRefugios[1].strip().split(" "))

        self.distanciasPuntosEncuentrosRefugios = np.array(self.distanciasPuntosEncuentrosRefugios).astype(int)
