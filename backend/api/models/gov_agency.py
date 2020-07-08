from django.db import models


class GovAgency(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True, verbose_name='ID')
    agency_name = models.CharField(max_length=20, unique=True, db_index=True)
    zip_code = models.DecimalField(max_digits=6, decimal_places=0)
    address = models.CharField(max_length=100)
