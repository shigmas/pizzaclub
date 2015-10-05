from django.contrib import admin

from club.models import Neighborhood
from club.models import PizzaStyle
from club.models import Pizzeria
from club.models import Visit
from club.models import Vote

# Register your models here.

admin.site.register(Neighborhood)
admin.site.register(PizzaStyle)
admin.site.register(Pizzeria)
admin.site.register(Visit)
admin.site.register(Vote)
