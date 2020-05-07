from django.contrib import admin
from .models import Case, Nodule
# Register your models here.
admin.site.site_header = 'Administration Portal'
admin.site.index_title = 'Adminsitration'

admin.site.register(Case)
admin.site.register(Nodule)