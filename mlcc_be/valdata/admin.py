from django.contrib import admin
from valdata.models import Data, Bbox, ManualLog, Margin


# Register your models here.
admin.site.register(Data)
admin.site.register(Bbox)
admin.site.register(Margin)
admin.site.register(ManualLog)


