import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from celery import shared_task
import json
import pandas as pd
from .models import Data, Bbox, Margin
from django.core.files.images import ImageFile


# db에 데이터 넣을 때 역순으로 넣기

@shared_task
def set_data():
    # 데이터 적재함수. 모델 json구조 파악후 수정 필요
    # image :id, width, height, file_name
    # anotation : id, img_id, category_id, segmentation, area, bbox(4개)
    with open(os.getcwd() + 'alignment_system/result', 'r') as f:
        data = json.loads(f.read())
    df = pd.json_normalize(data)
    for idx, row in df.iterrows():
        # insert data
        d = Data.objects.create(name=row['image']['file_name'], 
                            original_image=ImageFile(open(os.getcwd() +
                                'alignment_system/result' + row['image']['file_name'], "rb")),
                            segmentation_image=ImageFile(open(os.getcwd() +
                                'alignment_system/result' + row['image']['file_name'] + '_seg', "rb")))
        for anotation in row['anotation']:
            b = Bbox.objects.create(name=row['image']['file_name'] + 'bbox' + anotation['id'],
                                data_name=row['image']['file_name'],
                                min_margn_ratio=None,
                                box_center_x = anotation['bbox'][0],
                                box_center_y = anotation['bbox'][1],
                                box_width = anotation['bbox'][2],
                                box_height = anotation['bbox'][3])
            for segmentation in anotation['segmentation']:
                Margin.objects.create()
            b.min_margin_ratio = ''
            b.save()
        d.save()

class Target:
    watchDir = os.getcwd() + 'alignment_system/input'
    
    def __init__(self):
        self.observer = Observer()   #observer객체를 만듦

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDir, 
                                            recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            print("Error")
            self.observer.join()

class Handler(FileSystemEventHandler):
    def on_created(self, event): #파일, 디렉터리가 생성되면 실행
        # 해당 디렉토리에 생성된 파일로 모델 실행
        # 모델 작업경로 비우기
        set_data()

if __name__ == '__main__': #본 파일에서 실행될 때만 실행되도록 함
    w = Target()
    w.run()