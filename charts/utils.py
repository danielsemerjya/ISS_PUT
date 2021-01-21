import math
import numpy as np
import time
import pickle, base64
from .models import PID_db

def PID(Tp, e, e_sum, delta_e):
    kp = 2 # zwieksza przeregullowania ale szybciej e dazy do 0
    Ti = 0.005
    Td = 0.01
    Kd = Td/Tp #Td/Tp
    Ki = Tp/Ti #0.0001 #Tp/Ti
    u = kp*(e + Ki*e_sum + Kd*delta_e)
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
    # stale
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

def pid_sim(start_ang, finish_ang, Tsim):
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


    # petla obliczeniowa

    for i in range(N):
        Qd = PID(Tp, e, e_sum, delta_e) # obliczenie nowej wartosci sterującej

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


        # DAlej należy zrobić DB, symulacje do DB, ustalić zmiany symulacji tak by można ją było parametryzować z formularza utworzenia
        # symulacji

    #Transforacja danych do postaci Binarner = > Tau, Q_prim, Kat, E
    Tau_bytes = pickle.dumps(Tau)
    #Tau_base64 =base64.b64decode(Tau_bytes)

    Q_prim_bytes = pickle.dumps(Q_prim)
    #Q_prim_base64 =base64.b64decode(Q_prim_bytes)

    Kat_bytes = pickle.dumps(rad_to_deg(Kat))
    #Kat_base64 = base64.b64decode(Kat_bytes)

    E_bytes = pickle.dumps(rad_to_deg(E))
    #E_base64 =base64.b64decode(E_bytes)
    #Zapis do db = > Tau, Q_prim, Kat, E
    add_record = PID_db.objects.create(Tau=Tau_bytes, Q_prim=Q_prim_bytes, Kat=Kat_bytes, E=E_bytes, t=Tsim, n=N)
    #add_record = PID_db.objects.create(Tau=Tau_base64, Q_prim=Q_prim_base64, Kat=Kat_base64, E=E_base64)
    return add_record


