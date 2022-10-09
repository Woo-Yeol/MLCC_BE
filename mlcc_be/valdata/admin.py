from django.contrib import admin
from valdata.models import Data, Bbox, ManualLog, Margin, State, InferencePath


# Register your models here.
admin.site.register(Data)
admin.site.register(Bbox)
admin.site.register(Margin)
admin.site.register(ManualLog)
admin.site.register(State)
admin.site.register(InferencePath)



