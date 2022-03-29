from django.contrib import admin
from valdata.models import Data
from valdata.models import Anotations
from valdata.models import Bbox
from valdata.models import Box_segmentation
from valdata.models import Margin
# Register your models here.

admin.site.register(Data)
admin.site.register(Anotations)
admin.site.register(Bbox)
admin.site.register(Box_segmentation)
admin.site.register(Margin)

