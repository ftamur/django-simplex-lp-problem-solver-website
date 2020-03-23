from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, HTML, Submit


class InitForm(forms.Form):
    variables = forms.ChoiceField(
        initial=3, choices=[(i, i) for i in range(2, 11)],
        label='Variables'
    )
    constraints = forms.ChoiceField(
        initial=3, choices=[(i, i) for i in range(1, 11)],
        label='Constraints'
    )


class SolveForm(forms.Form):
    pass