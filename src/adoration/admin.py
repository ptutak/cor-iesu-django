from django.contrib import admin

# Register your models here.
from .models import Collection, CollectionConfig, Period, PeriodAssignment, PeriodCollection

admin.site.register([Collection, CollectionConfig, Period, PeriodAssignment, PeriodCollection])
