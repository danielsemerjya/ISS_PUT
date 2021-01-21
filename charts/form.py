from django import forms


class simulation_form(forms.Form):
    start_ang = forms.FloatField(label="Kąt startowy [deg]", initial="0", max_value=90, min_value=0)
    finish_ang = forms.FloatField(label="Kąt końcowy [deg]", initial="45",max_value=90, min_value=0)
    time = forms.FloatField(label="Czas trwania [s]", initial="2",max_value=90, min_value=1)
    algorytm_1 = forms.BooleanField(label="PiD", initial=True, disabled=True)
    algorytm_2 = forms.BooleanField(label="Fuzzy", initial=True, disabled=True)


    start_ang.widget.attrs.update({'class': 'form-control'})
    finish_ang.widget.attrs.update({'class': 'form-control'})
    time.widget.attrs.update({'class': 'form-control'})
