from django.urls import path

from .views import *

app_name = 'simplex'
urlpatterns = [
    path('', InitView.as_view(), name='init'),
    path('solve/', SolveView.as_view(), name='solve'),
    path('transportation/', TransportationInit.as_view(), name='transportation_init'),
    path('assigment/', AssignmentInit.as_view(), name='assignment_init')
]
