from django import forms


class InitForm(forms.Form):
    variables = forms.ChoiceField(
        initial=3, choices=[(i, i) for i in range(1, 11)],
        label = 'Variables'
    )
    constraints = forms.ChoiceField(
        initial=3, choices=[(i, i) for i in range(1, 11)],
        label = 'Constraints'
    )
