from django.contrib import admin
import site
# Register your models here.

from .models import *

admin.site.register(Profile)
admin.site.register(Sell)
admin.site.register(Buy)


# Register your models here.
