from django.db import models


class State(models.Model):
    title = models.CharField(unique=True, max_length=32, null=False)

    def __str__(self):
        return self.title


class Province(models.Model):
    title = models.CharField(unique=True, null=False, max_length=250)
    state = models.ForeignKey(State, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title


class Location(models.Model):
    title = models.CharField(unique=True, null=False, max_length=250)
    address = models.TextField()
    lat = models.CharField(max_length=255, null=True, blank=True)
    lng = models.CharField(max_length=255, null=True, blank=True)
    province = models.ForeignKey(Province, null=True, on_delete=models.SET_NULL)
    is_individual = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Scheduling(models.Model):
    deliver_date_time = models.DateTimeField()
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    is_enable = models.BooleanField(default=True)

    def __str__(self):
        return f'time is {self.deliver_date_time} - location address in {self.location.address}' \
               f' ,this province {self.location.province}'
