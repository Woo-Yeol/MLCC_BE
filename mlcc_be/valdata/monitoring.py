import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from celery import shared_task
import json
import pandas as pd
import numpy as np
from PIL import Image
from .models import Data, Bbox, Margin
from django.core.files.images import ImageFile
from datetime import datetime



# db에 데이터 넣을 때 역순으로 넣기

@shared_task
def set_data(date):
    # 1. 모델 실행 조건 설정 (이 파일은 어떤식으로 호출 및 동작할지 결정)
    #    (1). watchdog를 통한 mlcc_datasets/val/ 폴더 파일 개수 or 용량 감지 후 일정 조건 만족시 모델 실행
    #    (2). celery_beat를 통한 일정시간마다 쌓인 이미지에 대한 모델 실행
    # 2. 모델 실행 후에 set_data 메소드 실행되도록
    # python mlcc_inference.py
    # --source 'mlcc_datasets/val/' --remove_edge_bbox --project 'mmcl_results' --name 'demo1'
    with os.scandir(os.getcwd() + '/mmcv_laminate_alignment_system/mmcl_results/' + date + '/mlcc') as entries:
        for entry in entries:
            if entry.is_dir:
                c_dir = os.getcwd() + '/mmcv_laminate_alignment_system/mmcl_results/' + date + '/mlcc/' + entry.name
                f_name = entry.name[0:len(entry.name)-4] + '.json'
                with open(c_dir + '/' + f_name) as f:
                    result = json.loads(f.read())
                    img_name = result['img_basename']
                    seg_name = img_name[0:len(img_name)-5] + '_seg.jpg'
                    seg_img = Image.fromarray(np.uint8(np.array(result['seg0'])*255))
                    seg_img.save(c_dir + '/' + f_name + seg_name + ".jpg")
                    d = Data.objects.create(
                        name=result['img_basename'], 
                        original_image=ImageFile(open(c_dir + img_name, "rb")),
                        segmentation_image=ImageFile(open(c_dir + seg_name, "rb")))
                    for bbox_id, anotation in enumerate(result['qa_result_list']):
                        b = Bbox.objects.create(
                            name=result['img_basename'][0:len(result['img_basename'])-5] + '_bbox_' + bbox_id+1,
                            data=result['img_basename'][0:len(result['img_basename'])-5],
                            min_margn_ratio=anotation['min_margin_ratio'],
                            # 박스 그리기 위해 필요했던 4개의 값이 신규 json 출력에는 존재하지 않음.
                            # qa_result의 first_lst, last_lst로 박스 자체의 크기 및 모양은 알 수 있음
                            # 박스 그리기 위해 박스의 절대좌표를 알 수 있는 값이 필요
                            box_center_x = anotation['bbox'][0],
                            box_center_y = anotation['bbox'][1],
                            box_width = anotation['bbox'][2],
                            box_height = anotation['bbox'][3])
                        for i in range(len(anotation['first_lst'])):
                            m = Margin.objects.create(
                                margin_num=result['img_basename'][0:len(result['img_basename'])-5] + '_bbox_' + bbox_id+1 + '_magrin_' + i+1,
                                bbox=result['img_basename'][0:len(result['img_basename'])-5] + '_bbox_' + bbox_id+1,
                                margin_x = anotation['first_lst'][i],
                                real_margin = anotation['real_margin'],
                                margin_ratio = anotation['margin_ratio'],
                                margin_width = anotation['last_lst'][i]-anotation['first_lst'][i],
                                # 현재 컷오프 0인 값만 모델에서 출력중인데 변경가능한지
                                cut_off = 0
                            )
                            m.save()
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
        set_data(datetime.today().strftime("%Y%m%d"))

if __name__ == '__main__': #본 파일에서 실행될 때만 실행되도록 함
    
   
    w = Target()
    w.run()