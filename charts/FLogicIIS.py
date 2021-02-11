import numpy as np
from skfuzzy import control as ctrl
import math

class fuzzyIIS:
    "Klasa sterująca sterownikiem rozmytym do projektu IIS v3"

    def __init__(self):
        self.delta = ctrl.Antecedent(np.arange(-180, 181, 1), 'delta')
        self.error = ctrl.Antecedent(np.arange(-210, 211, 1), 'error')
        self.tau = ctrl.Consequent(np.arange(-2, 3, 1), 'tau')
        self.__PopulateUniverses()
        self.output_ctrl = ctrl.ControlSystem(self.__InitRules())
        self.outputSim = ctrl.ControlSystemSimulation(self.output_ctrl)


    def __PopulateUniverses(self):
        names = ['nb', 'ns', 'ze', 'ps', 'pb']
        self.error.automf(names=names)
        self.delta.automf(names=names)
        self.tau.automf(names=names)

    def __InitRules(self):
        rule0 = ctrl.Rule(antecedent=((self.error['nb'] & self.delta['nb']) |
                                      (self.error['ns'] & self.delta['nb']) |
                                      (self.error['nb'] & self.delta['ns'])),
                          consequent=self.tau['nb'], label='rule nb')

        rule1 = ctrl.Rule(antecedent=((self.error['nb'] & self.delta['ze']) |
                                      (self.error['nb'] & self.delta['ps']) |
                                      (self.error['ns'] & self.delta['ns']) |
                                      (self.error['ns'] & self.delta['ze']) |
                                      (self.error['ze'] & self.delta['ns']) |
                                      (self.error['ze'] & self.delta['nb']) |
                                      (self.error['ps'] & self.delta['nb'])),
                          consequent=self.tau['ns'], label='rule ns')

        rule2 = ctrl.Rule(antecedent=((self.error['nb'] & self.delta['pb']) |
                                      (self.error['ns'] & self.delta['ps']) |
                                      (self.error['ze'] & self.delta['ze']) |
                                      (self.error['ps'] & self.delta['ns']) |
                                      (self.error['pb'] & self.delta['nb'])),
                          consequent=self.tau['ze'], label='rule ze')

        rule3 = ctrl.Rule(antecedent=((self.error['ns'] & self.delta['pb']) |
                                      (self.error['ze'] & self.delta['pb']) |
                                      (self.error['ze'] & self.delta['ps']) |
                                      (self.error['ps'] & self.delta['ps']) |
                                      (self.error['ps'] & self.delta['ze']) |
                                      (self.error['pb'] & self.delta['ze']) |
                                      (self.error['pb'] & self.delta['ns'])),
                          consequent=self.tau['ps'], label='rule ps')

        rule4 = ctrl.Rule(antecedent=((self.error['ps'] & self.delta['pb']) |
                                      (self.error['pb'] & self.delta['pb']) |
                                      (self.error['pb'] & self.delta['ps'])),
                          consequent=self.tau['pb'], label='rule pb')

        rules = [rule0, rule1, rule2, rule3, rule4]
        #rule0.view()
        return rules

    def __wahadlo(self, tau, rad_kat_stary, predkosc, przyspieszenie):
        #stale
        m = 1  #masa kuli
        L = 1  # dlugosc ramienia
        g = 9.81  #przysp. grawitacyjne
        l = L
        b = 0.1  #tarcie wiskotyczne

        a = l * przyspieszenie / g + b * predkosc / (m * g * l) + tau / (m * g * l)

        if a > 1:
            a = 1
        if a < -1:
            a = -1

        rad_kat = math.asin(a)
        predkosc_nowa = rad_kat - rad_kat_stary
        przyspieszenie_nowe = predkosc_nowa - predkosc

        return rad_kat, predkosc_nowa, przyspieszenie_nowe

    def __deg_to_rad(self, deg):
        rad = deg * 2 * math.pi / 360
        return rad

    def __rad_to_deg(self, rad):
        deg = rad * 360 / (2 * math.pi)
        return deg

    def __limit(self, target, min, max):
        if target < min:
            return min
        if target > max:
            return  max
        return target

    def simulate(self, targetPosition, startingPosition, simulationTime, simulationStep):
        #ustawianie zmiennych na poczatek symulacji
        simulationIterations = int(simulationTime / simulationStep)
        predkosc = 0
        przyspieszenie = 0
        actualPosition = startingPosition
        error = targetPosition - actualPosition

        Kat = np.zeros((1, simulationIterations + 1))  # przebieg kata
        Kat[0, 0] = startingPosition
        Tau = np.zeros((1, simulationIterations + 1))  # przebieg momentow nastaw
        predkoscTab = np.zeros((1, simulationIterations + 1))
        predkoscTab[0][1] = predkosc
        przyspieszenieTab = np.zeros((1, simulationIterations + 1))
        przyspieszenieTab[0][1] = przyspieszenie
        errorArray = np.zeros((1, simulationIterations + 1))
        errorArray[0][0] = error
        errorDifference = 0
        errorDifferenceArray = np.zeros((1, simulationIterations + 1))
        errorDifferenceArray[0][0] = errorDifference
        calculatedTau = 0
        calculatedTauSum = 0
        calculatedSumArray = np.zeros((1, simulationIterations + 1))
        calculatedSumArray[0][0] = 0
        for x in range(simulationIterations):
            self.outputSim.input['error'] = error
            self.outputSim.input['delta'] = errorDifference
            self.outputSim.compute()
            calculatedTau = self.outputSim.output['tau']
            calculatedTauSum += calculatedTau
            calculatedSumArray[0][x + 1] = calculatedTauSum
            actualPosition, predkosc, przyspieszenie = self.__wahadlo(calculatedTauSum, math.radians(actualPosition),
                                                                      predkosc, przyspieszenie)
            actualPosition = math.degrees(actualPosition)
            error = targetPosition - actualPosition
            Kat[0][x + 1] = actualPosition
            Tau[0][x + 1] = calculatedTau
            predkoscTab[0][x+1] = predkosc
            przyspieszenieTab[0][x+1] = przyspieszenie
            errorArray[0][x+1] = error
            errorDifference = error - errorArray[0][x]
            errorDifferenceArray[0][x+1] = errorDifference
            # self.tau.view(sim=self.outputSim)

        return Kat, predkoscTab, przyspieszenieTab, Tau, errorArray, errorDifferenceArray, calculatedSumArray