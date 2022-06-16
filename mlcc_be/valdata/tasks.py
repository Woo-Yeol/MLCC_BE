import os
import shutil
import sys
import time
from celery import shared_task
import json
import pandas as pd
import numpy as np
from PIL import Image
from .models import Data, Bbox, Margin
from django.core.files.images import ImageFile
from datetime import datetime, date, timedelta
import subprocess 
sys.path.append("C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system")
from mlcc_django import run_model

# db에 데이터 넣을 때 역순으로 넣기


@shared_task
def set_data():
    # 1. 모델 실행
    
    model_root = "C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system"   
    server_root = "C:/Users/user/Desktop/IITP/MLCC_BE"
    dt = datetime.now().strftime('%Y%m%d%H%M%S')
    dir_path = f"{model_root}/mlcc_datasets/val_test"
    entries = os.scandir(dir_path)
    length = 0
    for entry in entries:
        length += 1
    if length != 0:
        run_model(dt)
        # 2. 데이터 적재
        # python mlcc_inference.py
        # --source 'mlcc_datasets/val/' --remove_edge_bbox --project 'mmcl_results' --name 'demo1'
        with os.scandir(f"{model_root}/mmcl_results/{dt}/mlcc") as entries:
            for entry in entries:
                if entry.is_dir:
                    c_dir = f"{model_root}/mmcl_results/{dt}/mlcc/" + entry.name
                    f_name = entry.name[0:len(entry.name)-4] + '.json'
                    with open(c_dir + '/' + f_name) as f:
                        result = json.loads(f.read())
                        img_name = result['img_basename']
                        seg_name = img_name[0:len(img_name)-4] + '_seg.jpg'
                        seg_img = Image.fromarray(np.uint8(np.array(result['seg0'])*255))
                        seg_img.save(c_dir + '/' + seg_name)
                        img_dir = f"{server_root}/mlcc_be/media/data/{datetime.now().strftime('%m.%d')}"
                        if not os.path.exists(img_dir):
                            os.makedirs(img_dir)
                        os.makedirs(f"{img_dir}/{result['img_basename'][0:len(result['img_basename'])-4]}")
                        shutil.copyfile(c_dir + '/' + img_name, f"{img_dir}/{result['img_basename'][0:len(result['img_basename'])-4]}/{img_name}")
                        shutil.copyfile(c_dir + '/' + seg_name, f"{img_dir}/{result['img_basename'][0:len(result['img_basename'])-4]}/{seg_name}")
                        d = Data()
                        d.name = result['img_basename'], 
                        d.original_image = f"{server_root}/mlcc_be/media/data/{datetime.now().strftime('%m.%d')}/{result['img_basename'][0:len(result['img_basename'])-4]}/{img_name}"
                        d.segmentation_image = f"{server_root}/mlcc_be/media/data/{datetime.now().strftime('%m.%d')}/{result['img_basename'][0:len(result['img_basename'])-4]}/{seg_name}"
                        d.created_date = date.today()
                        d.save()
                        for bbox_id, anotation in enumerate(result['qa_result_list']):
                            b = Bbox.objects.create(
                                name=result['img_basename'][0:len(result['img_basename'])-4] + '_bbox_' + str(bbox_id+1),
                                data=d,
                                min_margin_ratio=anotation['min_margin_ratio'],
                                box_width = (result['bboxes'][bbox_id][2] - result['bboxes'][bbox_id][0]),
                                box_height = (result['bboxes'][bbox_id][3] - result['bboxes'][bbox_id][1]),
                                box_center_x = (result['bboxes'][bbox_id][2] - (result['bboxes'][bbox_id][2] - result['bboxes'][bbox_id][0]) / 2),
                                box_center_y = (result['bboxes'][bbox_id][3] - (result['bboxes'][bbox_id][3] - result['bboxes'][bbox_id][1]) / 2)
                            )
                            b.save()
                            for i in range(len(anotation['first_lst'])):
                                m = Margin.objects.create(
                                    margin_num=result['img_basename'][0:len(result['img_basename'])-4] + '_bbox_' + str(bbox_id+1) + '_magrin_' + str(i+1),
                                    bbox=b,
                                    margin_x = anotation['first_lst'][i],
                                    real_margin = anotation['real_margin'],
                                    margin_ratio = anotation['margin_ratio'][i],
                                    margin_width = anotation['last_lst'][i]-anotation['first_lst'][i],
                                    # 현재 컷오프 0인 값만 모델에서 출력중인데 변경가능한지
                                    cut_off = 0
                                )
                                m.save()
                        d.save()
        # 3. DB 적재한 모델 원본 데이터 삭제
        # val 내부 이미지
        # mmcl_results 내부 폴더
        entries = os.scandir(f'{model_root}/mlcc_datasets/val_test')
        for entry in entries:
            os.remove(entry.path)
        entries = os.scandir(f'{model_root}/mmcl_results')
        for entry in entries:
            os.remove(entry.path)
    
    set_data()