from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class PID_db(models.Model):
    sim_time = models.DateTimeField(auto_now=True, auto_now_add=False) # data symulacji
    id = models.AutoField(primary_key=True)
    #Zapis do db = > Tau, Q_prim, Kat, E
    Tau = models.BinaryField() # Wektor momentow sterujacych [Mn]
    Q_prim = models.BinaryField() # wektor predkosci katowych [rad]
    Kat = models.BinaryField() # wektor pozycji katowych [deg]
    E = models.BinaryField() # wektor bledu polozenia [deg]
    t = models.FloatField(default=1) # czas trwania symulacji [s]
    n = models.IntegerField(default=1) # liczba iteracji