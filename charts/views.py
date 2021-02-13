from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import PID_db, FUZZY_db
import random
from .form import simulation_form
from .utils import pid_sim, fuzzySimulate
import pickle
import numpy as np

User = get_user_model()


def history(request):
    # Historia wykonanych symulacji
    hist = PID_db.objects.all().order_by('-id')
    return render(request, "history.html", {
        "hist":hist,
    })


def index(request):
    
    return render(request, "index.html")


def new(request): 
    # formularz inicjujacy nowa symulacje
    if request.method =="POST":
        form = simulation_form(request.POST)
        if form.is_valid():
            print("OK")
            start_ang = form.cleaned_data['start_ang']
            finish_ang = form.cleaned_data['finish_ang']
            time = form.cleaned_data['time']
            Kp = form.cleaned_data['Kp']
            Ki = form.cleaned_data['Ki']
            Kd = form.cleaned_data['Kd']
            x = pid_sim(start_ang, finish_ang,time, Kp, Ki, Kd)
            Kat = pickle.loads(x.Kat)
            minTau = form.cleaned_data['minTau']
            maxTau = form.cleaned_data['maxTau']
            y = fuzzySimulate(start_ang, finish_ang, time, x, minTau, maxTau)
            return redirect('/chart/0')
    
    
    return render(request, 'new_sim.html', {
        "form":simulation_form()
    })

class HomeView(View):
    def get(self, request, id, **kwargs):
        if id == '0':
            pid = PID_db.objects.all().order_by('-id')[0]
        else:
            pid = PID_db.objects.get(id=id)
        fuzzy = FUZZY_db.objects.get(parent=pid)

        pid_blad = 0
        fuzzy_blad = 0

        pid_koszt = 0
        fuzzy_koszt = 0

        for i in pid.E:
            pid_blad += i
        for i in fuzzy.E:
            fuzzy_blad += i
        for i in pid.Tau:
            pid_koszt += i
        for i in fuzzy.Tau:
            fuzzy_koszt += i
            print(i)

        return render(request, 'charts.html', {
            "id":id,
            "pid":pid,
            "fuzzy":fuzzy,
            "pid_blad":pid_blad,
            "fuzzy_blad":fuzzy_blad,
            "pid_koszt":pid_koszt,
            "fuzzy_koszt":fuzzy_koszt
            })

class ChartData(APIView):
    last_recorded_pid = PID_db.objects.all().order_by('-id')[0]
    Katy_pid = pickle.loads(last_recorded_pid.Kat)


    n = last_recorded_pid.n
    t = last_recorded_pid.t
    N = np.arange(0,n+1, t/n)


    def get(self, request, id, format=None):
        if id == '0':
            last_recorded_pid = PID_db.objects.all().order_by('-id')[0]
        else:
            last_recorded_pid = PID_db.objects.get(id=id)

        last_recorded_fuzzy = FUZZY_db.objects.get(parent=last_recorded_pid)


        Katy_pid = pickle.loads(last_recorded_pid.Kat)
        Katy_fuzzy = pickle.loads(last_recorded_fuzzy.Kat)

        E_pid = pickle.loads(last_recorded_pid.E)
        E_fuzzy = pickle.loads(last_recorded_fuzzy.E)

        Tau_pid = pickle.loads(last_recorded_pid.Tau)
        Tau_fuzzy = pickle.loads(last_recorded_fuzzy.Tau)
        n = last_recorded_pid.n
        t = last_recorded_pid.t
        N = np.arange(0,t, t/n)
        labels = N
        Katy_pid = Katy_pid[0]
        Katy_fuzzy = Katy_fuzzy[0]

        qs_count = User.objects.all().count()

        data = {
                "labels": labels,
                "default": Katy_pid,
                "default2": Katy_fuzzy,
                "default3": E_pid,
                "default4": E_fuzzy,
                "default5": Tau_pid,
                "default6": Tau_fuzzy,
        }
        return Response(data)

