from django.contrib import admin
from .models import Career, CareerResource

class CareerResourceInline(admin.TabularInline):
    model = CareerResource
    extra = 1

@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    inlines = [CareerResourceInline]
    list_display = ['title', 'demand_level', 'avg_salary_min', 'avg_salary_max']