from django.db import models

from django.contrib.auth.models import User

# Create your models here.

class Neighborhood(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class PizzaStyle(models.Model):
    style = models.CharField(max_length = 64)

    def __str__(self):
        return self.style

class Pizzeria(models.Model):
    name = models.CharField(max_length=512)
    url = models.CharField(max_length=512)
    neighborhood = models.ForeignKey('club.Neighborhood')
    specialty = models.ForeignKey('club.PizzaStyle')

    def __str__(self):
        return '%s in %s, specializing in %s' % (self.name, self.neighborhood,
                                                 self.specialty)

class Visit(models.Model):
    pizzeria = models.ForeignKey('club.Pizzeria')
    visitDate = models.DateField(auto_now=True)
    
    diningNotes = models.TextField()

    def __str__(self):
        return '%s to %s' % (self.visitDate, self.pizzeria.name)

class Vote(models.Model):
    visit = models.ForeignKey('club.Visit')
    voter = models.ForeignKey(User)

    crust = models.FloatField()
    sauce = models.FloatField()
    service = models.FloatField()
    creativity = models.FloatField()
    overall = models.FloatField()

    def __str__(self):
        return '%s: voted crust: %s, sauce: %s, service: %s, creativity: %s,\
  overall: %s' % (self.voter.username, self.crust, self.sauce, self.service,
                  self.creativity, self.overall)

