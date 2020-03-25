from django.shortcuts import render
from django.views.generic import FormView, DetailView
from .forms import InitForm, SolveForm
from .mixins import SimplexInitMixin, SimplexSolveActionMixin


# Create your views here.
class InitView(SimplexInitMixin, FormView):
    template_name = 'simplex/simplex_init.html'
    form_class = InitForm


class SolveView(SimplexSolveActionMixin, SimplexInitMixin, FormView):
    template_name = 'simplex/simplex_solve.html'
    form_class = SolveForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        variables = self.request.GET.get('variables',
                                         self.request.POST.get('variables'))
        constraints = self.request.GET.get('constraints',
                                           self.request.POST.get('constraints'))
        kwargs.update({'variables': variables})
        kwargs.update({'constraints': constraints})

        return kwargs
