from django.db import models

# Create your models here.

class Config(models.Model):
    # db_table = "config"

    name: models.CharField = models.CharField(max_length=100, unique=True, null=False)
    value: models.CharField = models.CharField(max_length=255, null=False)
    description: models.CharField = models.CharField(max_length=600, null=False)


class Period(models.Model):
    # db_table = "periods"

    name: models.CharField = models.CharField(max_length=100, unique=True, null=False)
    description: models.CharField = models.CharField(max_length=600, null=False)


class Collection(models.Model):
    # db_table = "collections"

    name: models.CharField = models.CharField(max_length=100, unique=True, null=False)
    description: models.CharField = models.CharField(max_length=600, null=False)
    enabled: models.BooleanField = models.BooleanField(null=False, default=True)
    periods: models.ManyToManyField = models.ManyToManyField(Period, through="PeriodCollection")


class PeriodCollection(models.Model):
    # db_table = "period_collections"

    period: models.ForeignKey = models.ForeignKey(Period, on_delete=models.CASCADE)
    collection: models.ForeignKey = models.ForeignKey(Collection, on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['period', 'collection'], name='period_collection_unique_constraint'),
        ]


class CollectionConfig(models.Model):
    # db_table = "collection_configs"

    collection: models.ForeignKey = models.ForeignKey(Collection, on_delete=models.CASCADE)
    name: models.CharField = models.CharField(max_length=100, null=False)
    value: models.CharField = models.CharField(max_length=255, null=False)
    description: models.CharField = models.CharField(max_length=600, null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['collection', 'name'], name='collection_config_unique_constraint'),
        ]


class PeriodAssignment(models.Model):
    # db_table = "period_assignments"

    period_collection: models.ForeignKey = models.ForeignKey(PeriodCollection, on_delete=models.CASCADE)
    attendant_name: models.CharField = models.CharField(max_length=100, null=False)
    attendant_email: models.CharField = models.CharField(max_length=80)
    attendant_phone_number: models.CharField = models.CharField(max_length=15)
