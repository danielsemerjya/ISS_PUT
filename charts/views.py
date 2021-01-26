from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import PID_db
import random
from .form import simulation_form
from .utils import pid_sim
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
            return render(request, "index.html")

    return render(request, 'new_sim.html', {
        "form":simulation_form()
    })

class HomeView(View):
    def get(self, request, id, **kwargs):
        pass            
        return render(request, 'charts.html', {
            "id":id,
            })

class ChartData(APIView):
    last_recorded_pid = PID_db.objects.all().order_by('-id')[0]
    Katy = pickle.loads(last_recorded_pid.Kat)

    n = last_recorded_pid.n
    t = last_recorded_pid.t
    N = np.arange(0,n+1, t/n)


    def get(self, request, id, format=None):
        if id == '0':
            last_recorded_pid = PID_db.objects.all().order_by('-id')[0]
        else:
            last_recorded_pid = PID_db.objects.get(id=id)


        Katy = pickle.loads(last_recorded_pid.Kat)

        n = last_recorded_pid.n
        t = last_recorded_pid.t
        N = np.arange(0,t, t/n)

        labels = N
        default_items = Katy[0]

        qs_count = User.objects.all().count()

        data = {
                "labels": labels,
                "default": default_items,
        }
        return Response(data)

