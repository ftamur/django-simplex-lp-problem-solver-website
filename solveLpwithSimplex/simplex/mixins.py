from django.contrib import messages

from django.shortcuts import redirect, render

from .exceptions import SimplexInitException


class SimplexInitMixin:

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except SimplexInitException as error:
            messages.add_message(request, messages.ERROR, str(error))
            return redirect('simplex:init')


class SimplexSolveActionMixin:
    template_name_success = 'simplex/simplex_result.html'

    def form_valid(self, form):
        """
        If the form is valid, solve linear programming problem.
        """
        solution, result = form.solve()

        return render(self.request, self.template_name_success, {
            'result': result,
            'solution_steps': solution,
        })
