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




def index(request):
    
    return render(request, "index.html")


def new(request): 
    # formularz inicjiujacy nowa symulacje
    if request.method =="POST":
        form = simulation_form(request.POST)
        if form.is_valid():
            print("OK")
            start_ang = form.cleaned_data['start_ang']
            finish_ang = form.cleaned_data['finish_ang']
            time = form.cleaned_data['time']
            x = pid_sim(start_ang, finish_ang,time)
            Kat = pickle.loads(x.Kat)
            return render(request, "index.html")

    return render(request, 'new_sim.html', {
        "form":simulation_form()
    })




# old functions


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'charts.html', {"customers": 10})

def get_data(request, *args, **kwargs):
    data = {
        "sales": 100,
        "customers": 10,
    }
    return JsonResponse(data) # http response


class ChartData(APIView):
    last_recorded_pid = PID_db.objects.all().order_by('-id')[0]
    Katy = pickle.loads(last_recorded_pid.Kat)
    n = last_recorded_pid.n
    t = last_recorded_pid.t
    N = np.arange(0,n+1, t/n)


    def get(self, request, format=None):
        last_recorded_pid = PID_db.objects.all().order_by('-id')[0]
        Katy = pickle.loads(last_recorded_pid.Kat)
        n = last_recorded_pid.n
        t = last_recorded_pid.t
        N = np.arange(0,t, t/n)

        labels = N
        default_items = Katy[0]
        y = 1

        qs_count = User.objects.all().count()

        data = {
                "labels": labels,
                "default": default_items,
        }
        return Response(data)

