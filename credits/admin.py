from django.contrib import admin
from records.models import Station, StationLimit, Sensor, Record


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name',)
@admin.register(StationLimit)
class StationLimitAdmin(admin.ModelAdmin):
    list_display = ('min', 'max')
@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('id','idx', 'station')
@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'datetime', 'value')
