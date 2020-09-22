from django.db import models


class Station(models.Model):
    name = models.CharField(max_length=50,null=False)

    class Meta:
        db_table = 'Stations'

    def __str__(self):
        return self.name
    
    def get_limits_dict(self):
        limit = StationLimit.objects.filter(station=self).order_by('updateTime').last()
        limits = {"station": self.name, "min": limit.min, "max": limit.max}
        return limits

    def get_limits(self):
        limits = StationLimit.objects.filter(station=self).order_by('updateTime').last()
        return limits


class StationLimit(models.Model):
    min = models.PositiveSmallIntegerField(null=False)
    max = models.PositiveSmallIntegerField(null=False)
    updateTime = models.DateTimeField(auto_now=True)
    station = models.ForeignKey(Station, 
                on_delete=models.PROTECT, 
                related_name='limits')

    class Meta:
        db_table = 'StationLimits'
    
    def __str__(self):
        return f"{self.station.name}_{self.min}-{self.max}"


class Sensor(models.Model):
    idx = models.CharField(max_length=18,null=False)
    createTime = models.DateTimeField(auto_now_add=True)
    updateTime = models.DateTimeField(auto_now=True)
    station = models.ForeignKey(Station, 
                on_delete=models.PROTECT, 
                related_name='sensors')

    class Meta:
        db_table = 'Sensors'
    
    def __str__(self):
        return self.idx

class RecordManager(models.Manager):
    def latest(self):
        return self.objects.all().order_by('-datetime', '-id').first()


class Record(models.Model):
    sensor = models.ForeignKey(Sensor, 
                on_delete=models.PROTECT, 
                related_name='records')
    # TODO timezone setting
    datetime = models.DateTimeField()
    order = models.PositiveSmallIntegerField(null=False)
    value = models.PositiveIntegerField(null=False)
    # NOTE if status=1 -> high, elif status=-1 -> low
    status = models.SmallIntegerField(null=False, default=0)
    
    class Meta:
        db_table = 'Records'
        constraints = [
            # NOTE requires unique for above columns in db
            models.UniqueConstraint(fields=['sensor', 'datetime', 'order', 'value'], name='uniquerecord')
        ]
    
    def __str__(self):
        return f"{self.id}"
    
    @classmethod
    def get_latest(cls):
        last = cls.objects.all().order_by('-datetime', '-id').first()
        return last
        