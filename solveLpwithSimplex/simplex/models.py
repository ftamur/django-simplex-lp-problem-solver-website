from django.db import models

# Create your models here.
class LpProblem(models.Model):
    name = models.CharField(max_length=50, blank=True)
    objective = models.OneToOneField("Equation", blank=True, on_delete=models.CASCADE)
    constrains = models.ManyToManyField("Equation", blank=True, related_name='lps')

    class Meta:
        verbose_name = "LpProblem"
        verbose_name_plural = "LpProblems"

    def __str__(self):
        return self.name



class Equation(models.Model):
    class EqualityType(models.TextChoices):
        EQUAL = '='
        LESS_THAN_EQUAL = '<='
        GREATER_THAN_EQUAL = '>='

    variable_count = models.IntegerField()
    right_hand_side = models.IntegerField()
    equality_type = models.CharField(max_length=2, 
    choices=EqualityType.choices, default=EqualityType.EQUAL)
    coefficients = models.CharField(max_length=1024)
    is_objective = models.BooleanField()
    is_constraint = models.BooleanField()

    
    class Meta:
        verbose_name = "Equation"
        verbose_name_plural = "Equations"

    def __str__(self):
        if self.is_objective: return "Objective"
        else: return "Constraint"


