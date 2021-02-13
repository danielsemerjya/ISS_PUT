from django import forms


class simulation_form(forms.Form):
    start_ang = forms.FloatField(label="Kąt startowy [deg]", initial="0", max_value=90, min_value=0)
    finish_ang = forms.FloatField(label="Kąt końcowy [deg]", initial="45",max_value=90, min_value=0)
    time = forms.FloatField(label="Czas trwania [s]", initial="7",max_value=90, min_value=1)
    Kp = forms.FloatField(label="Parametr Kp dla regulatora PiD", initial="1.3",max_value=100, min_value=0.01)
    Ki = forms.FloatField(label="Parametr Ki dla regulatora PiD", initial="1.2",max_value=100, min_value=0.01)
    Kd = forms.FloatField(label="Parametr Kd dla regulatora PiD", initial="2.0",max_value=100, min_value=0.01)
    minTau = forms.FloatField(label="Dolne ograniczenie wartośći sterującej", initial="-10",max_value=100, min_value=-100)
    maxTau = forms.FloatField(label="Górne ograniczenie wartości sterującej", initial="10",max_value=100, min_value=-100)
    algorytm_1 = forms.BooleanField(label="PiD", initial=True, disabled=True)
    algorytm_2 = forms.BooleanField(label="Fuzzy", initial=True, disabled=True)



    start_ang.widget.attrs.update({'class': 'form-control'})
    finish_ang.widget.attrs.update({'class': 'form-control'})
    time.widget.attrs.update({'class': 'form-control'})
    Kp.widget.attrs.update({'class': 'form-control'})
    Ki.widget.attrs.update({'class': 'form-control'})
    Kd.widget.attrs.update({'class': 'form-control'})
    minTau.widget.attrs.update({'class': 'form-control'})
    maxTau.widget.attrs.update({'class': 'form-control'})
