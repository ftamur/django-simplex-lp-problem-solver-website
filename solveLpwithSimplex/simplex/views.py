from django.shortcuts import render
from django.views.generic import FormView
from .forms import InitForm

# Create your views here.
class InitView(FormView):
    template_name = 'simplex/simplex_init.html'
    form_class = InitForm
    # success_url = '/solve/'


class SolveView(FormView):
    template_name = 'simplex/simplex_solve.html'
    form_class = InitForm
    # success_url = '/solve/'


class ResultView(FormView):
    template_name = 'simplex/simplex_result.html'
    form_class = InitForm
    # success_url = '/solve/'
