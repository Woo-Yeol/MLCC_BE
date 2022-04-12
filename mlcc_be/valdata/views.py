from django.shortcuts import render
from .models import Data, Bbox, Margin


# Create your views here.

# 모델에서 데이터 가져오기
def get_model_data():
    data = Data.object.all()



def set_data():
    data = load_notionAPI_seminar()['body']
    temp = []
    for d in data:
        s, created = Seminar.objects.update_or_create(
            title=d['title'])
        s.date = d['date']
        s.speaker = d['speaker']
        s.source = d['source']
        s.slide = d['slide']
        s.year = d['year']
        s.area = d['area']
        s.paper = d['paper']
        s.save()
        temp.append(d['title'])
    # Data Delete
    for db in Seminar.objects.all():
        if not db.title in temp:
            Seminar.objects.get(title=db.title).delete()
# 프론트에 그릴 데이터 넘기기