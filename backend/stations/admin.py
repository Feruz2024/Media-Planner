from django.contrib import admin
from .models import Station, Show, Daypart, RateCard

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name','type','region')

@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('name','station','genre')

@admin.register(Daypart)
class DaypartAdmin(admin.ModelAdmin):
    list_display = ('name','start_time','end_time')

@admin.register(RateCard)
class RateCardAdmin(admin.ModelAdmin):
    list_display = ('station','show','daypart','price','currency')
