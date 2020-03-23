from django.urls import path

from .views import *

app_name = 'simplex'
urlpatterns = [
    path('', InitView.as_view(), name='init'),
    path('solve/', SolveView.as_view(), name='solve'),
    path('result/', ResultView.as_view(), name='result'),
]
