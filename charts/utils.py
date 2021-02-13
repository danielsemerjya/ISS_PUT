import math
import numpy as np
import time
import pickle, base64
from .models import PID_db, FUZZY_db
from .FLogicIIS import fuzzyIIS



def fuzzySimulate(startAng, finishAng, time, x, minTau, maxTau):
    # Kat - wektor kąta
    # calculatrdSumArray - wektor momentu sterujacego
    # errorArray - wektor błedu
    Tp = 0.01
    fuzzy = fuzzyIIS(minTau, maxTau)
    kat, Predkosc, Przyspieszenie, Tau, blad, errorDifferenceArray, momentSterujacy = fuzzy.simulate(
         finishAng, startAng,time, Tp)
    N = int(time/0.01)
    
    #Transformacja danych do postaci binarnej
    momentSterujacy = pickle.dumps(momentSterujacy)

    kat = pickle.dumps(kat)

    blad = pickle.dumps(blad)

    add_record = FUZZY_db.objects.create(parent=x, Tau=momentSterujacy, Kat=kat, E=blad, t=time, n= N)
        
    return add_record


def PID(Tp, e, e_sum, delta_e, Kp, Ki, Kd):
    u = Kp*(e + Ki*e_sum + Kd*delta_e)
    if u < 0:
        u = 0
    return u

def deg_to_rad(deg):
    rad = deg*2*math.pi/360
    return rad

def rad_to_deg(rad):
    deg = rad*360/(2*math.pi)
    return deg

def wahadlo(tau, q_old, q_new, q_prim, q_bis):
    # Model matematyczny opisujący dynamikę wahadła
    m = 1 # masa kuli
    L = 1 # dlugosc ramienia
    g = 9.81 # przysp. grawitacyjne
    l = L
    b = 0.1 # tarcie wiskotyczne
    

    a = l*q_bis/g + b*q_prim/(m*g*l) + tau/(m*g*l)
    
    if a > 1:
        a = 1
    if a < -1:
        a = -1
        
    q = math.asin(a)
    q_prim_new = q - q_old

    return q, q_prim_new

def pid_sim(start_ang, finish_ang, Tsim, Kp, Ki, Kd):
    # poczatkowe polozenie w stopniach (zakres 0 - 90 stopni)
    q0_stopnie = start_ang
    # koncowe polozenie w stopniach (zakres 0 - 90 stopni)
    q_zad_stopnie = finish_ang

    # przeksztalcenie na radiany
    q0 = deg_to_rad(q0_stopnie) # [rad] pozycja początkowa wahadła
    q_zad = deg_to_rad(q_zad_stopnie)   # [rad] wartosc zadana

    ### Dalej w kodzie wszedzie uzywane sa radiany, dane w bazie danych rowniez w radianach

    e = q_zad - q0
    e_sum = e # poczatkowa suma bledow
    delta_e = 0
    q_prim = 0 # początkowa predkosc wahadla
    q_bis = 0 # poczatkowe przyspieszenie wahadla

    ### symulacja
    Tp = 0.01
    N = int(Tsim/Tp) # ilość iteracji
    n = np.arange(N+1)

    ### inicjalizacja wektora zbierajacego wyniki
    Kat = np.zeros((1, N+1)) # przebieg kata
    Kat[0,0] = q0
    Tau = np.zeros((1, N+1)) # przebieg momentow nastaw
    E = np.zeros((1, N+1)) # przebieg bledu
    E[0,0] = q_zad - q0
    Q_prim = np.zeros((1, N+1))
    Q_prim[0][1] = q_prim


    # petla obliczeniowa - przegląd zupełny możliwości

    for i in range(N):
        Qd = PID(Tp, e, e_sum, delta_e, Kp, Ki, Kd) # obliczenie nowej wartosci sterującej

        q, q_prim = wahadlo(Qd, Kat[0][i], q_zad, q_prim, q_bis) # obliczenie nowego kata

        Tau[0][i+1] = Qd # wektor momentow sterujacych
        Q_prim[0][i+1] = q_prim # wektor predkosci katowej
        Kat[0][i+1] = q
        q_bis = Q_prim[0][i+1] - Q_prim[0][i]

        # obliczenia bledow
        e = q_zad - q
        E[0][i+1] = e # wektor bledow pozycji
        e_sum += e
        delta_e = e - (q_zad - Kat[0][i])

    #Transforacja danych do postaci Binarner = > Tau, Q_prim, Kat, E
    Tau_bytes = pickle.dumps(Tau)

    Q_prim_bytes = pickle.dumps(Q_prim)

    Kat_bytes = pickle.dumps(rad_to_deg(Kat))

    E_bytes = pickle.dumps(rad_to_deg(E))
    
    #Zapis do db = > Tau, Q_prim, Kat, E
    add_record = PID_db.objects.create(Tau=Tau_bytes, Q_prim=Q_prim_bytes, Kat=Kat_bytes, E=E_bytes, t=Tsim, n=N)
    #add_record = PID_db.objects.create(Tau=Tau_base64, Q_prim=Q_prim_base64, Kat=Kat_base64, E=E_base64)
    return add_record


