from math import inf
import pathlib
from django.conf import settings
import os
import shutil
import sys
import cv2
import time
from celery import shared_task
import json
import pandas as pd
import numpy as np
from PIL import Image
from .models import Data, Bbox, Margin, ManualLog
from django.core.files.images import ImageFile
from datetime import datetime, date, timedelta
import subprocess 
sys.path.append("C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system")
from mlcc_django import auto_run_model, manual_run_model
from mlcc_systemkits.mlcc_system import MLCC_SYSTEM
import time
from multiprocessing import Pool
import typing
# db에 데이터 넣을 때 역순으로 넣기


system_mode = 'auto'
threshold = 0.85
running = False
results = []
model_root = "C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system"
dt = datetime.now().strftime('%y%m%d_%H%M%S')

@shared_task
def get_model_output() -> None:
    if system_mode == 'auto':
        auto_get_result()
    elif system_mode == 'manual':
        manual_get_result()


def auto_get_result() -> None:
    if running:
        return -1
    running = True
    try:
        # 1. 모델 실행
        dir_path = f"{model_root}/mlcc_datasets/val_test"
        entries = os.scandir(dir_path)
        length = 0
        pic = []
        for entry in entries:
            length += 1
            pic.append(entry.path)

        if length != 0:
            # 2. 데이터 적재
            results = auto_run_model(dt) 
            for i, result in enumerate(results):
                save_result(i)

        # 3. DB 적재한 모델 원본 데이터 삭제
        entries = os.scandir(f'{model_root}/mlcc_datasets/val_test')
        for entry in entries:
            os.remove(entry.path)

    # semaphore unlock
    finally:
        running = False

def manual_get_result() -> None:
    if running:
        return -1
    running = True
    try:   
        # 실행 경로 정하기
        dir_path = f"{model_root}/mlcc_datasets/smb"
        backup_path = f"{dir_path}/backup"

        first_create_time = datetime.now()
        first_create_pc = ''
        for path, subdirs, files in os.walk(dir_path):
            for name in files:
                if path[len(path)-3:len(path)-1] == 'pc':
                    t = datetime.fromtimestamp(os.path.getctime(pathlib.PurePath(path, name)))
                    if t < first_create_time:
                        first_create_time = t
                        first_create_pc = path[len(path)-3:]

        pc_name = first_create_pc
        entries = os.scandir(dir_path)
        length = 0
        # 2. 모델 실행 및 결과파일 생성
        if pc_name != '':
            global results
            results = manual_run_model(pc_name, threshold)
            os.makedirs(f'{dir_path}/{pc_name}/{dt}')
            for result in results:
                assessment = True
                for qa_result in result['qa_result_list']:
                    if qa_result['decision_result'] == False:
                        assessment = False
                        break

                f = open(f'{dir_path}/{pc_name}/{dt}/{result["img_basename"]}_{str(assessment)}.txt', 'w')
                f.close()
                shutil.copyfile(f'{dir_path}/{pc_name}/{result["img_basename"]}', f'{backup_path}/{dt}_{result["img_basename"]}')
                shutil.move(f'{dir_path}/{pc_name}/{result["img_basename"]}', f'{dir_path}/{pc_name}/{dt}/{result["img_basename"]}')
                # 3. DB에 Log 적재
                log = ManualLog()
                log.filename = result["img_basename"]
                log.dt = datetime.now()
                log.save()

    # semaphore unlock
    finally:
        running = False

def save_result(i) -> None:
    result = results[i]
    server_root = "C:/Users/user/Desktop/IITP/MLCC_BE"
    img_name = result['img_basename']
    seg_name = img_name[0:len(img_name)-4] + '_seg.jpg'
    # seg_img = Image.fromarray(np.uint8(np.array(result['seg_img'])))
    # seg_img.save(dir_path + '/' + seg_name)
    img_dir = f"{server_root}/mlcc_be/media/data/{datetime.now().strftime('%m.%d')}"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    os.makedirs(f"{img_dir}/{result['img_basename'][0:len(result['img_basename'])-4]}")
    
    r = np.array(result['img0'])
    s = np.array(result['seg_img'])
    cv2.imwrite( f"{img_dir}/{result['img_basename'][0:len(result['img_basename'])-4]}/{img_name}", r)
    cv2.imwrite( f"{img_dir}/{result['img_basename'][0:len(result['img_basename'])-4]}/{seg_name}", s)
    #shutil.copyfile(dir_path + '/' + img_name, f"{img_dir}/{result['img_basename'][0:len(result['img_basename'])-4]}/{img_name}")
    #shutil.copyfile(dir_path + '/' + seg_name, f"{img_dir}/{result['img_basename'][0:len(result['img_basename'])-4]}/{seg_name}")
    start = time.time()
    d = Data()
    d.name = result['img_basename'][0:len(img_name)-4],
    d.original_image = f"{server_root}/mlcc_be/media/data/{datetime.now().strftime('%m.%d')}/{result['img_basename'][0:len(result['img_basename'])-4]}/{img_name}"
    d.segmentation_image = f"{server_root}/mlcc_be/media/data/{datetime.now().strftime('%m.%d')}/{result['img_basename'][0:len(result['img_basename'])-4]}/{seg_name}"
    d.created_date = date.today()
    d.cvat_url = f'http://localhost:8080/tasks/1/jobs/1?frame={i}'
    d.save()
    total_min_ratio = inf
    for bbox_id, qa_result in enumerate(result['qa_result_list']):
        b = Bbox.objects.create(
            name=result['img_basename'][0:len(result['img_basename'])-4] + '_bbox_' + str(bbox_id+1),
            data=d,
            min_margin_ratio=qa_result['min_margin_ratio']*100,
            box_width = (result['bboxes'][bbox_id][2] - result['bboxes'][bbox_id][0]),
            box_height = (result['bboxes'][bbox_id][3] - result['bboxes'][bbox_id][1]),
            box_x = result['bboxes'][bbox_id][0],
            box_y = result['bboxes'][bbox_id][1],
        )
        b.save()
        for i in range(len(qa_result['first_lst'])):
            m = Margin.objects.create(
                name=result['img_basename'][0:len(result['img_basename'])-4] + '_bbox_' + str(bbox_id+1) + '_magrin_' + str(i+1),
                bbox=b,
                margin_x = result['bboxes'][bbox_id][0] + qa_result['first_lst'][i],
                margin_y = result['bboxes'][bbox_id][1] + i,
                real_margin = qa_result['real_margin'],
                margin_ratio = qa_result['margin_ratio'][i]*100,
                margin_width = qa_result['last_lst'][i]-qa_result['first_lst'][i],
            )
            m.save()
        total_min_ratio = min(total_min_ratio, qa_result['min_margin_ratio']) * 100
    d.margin_ratio = total_min_ratio
    d.save()
    print(time.time()-start)



# delete log, file
@shared_task
def reset_data():
    today = date.today()
    log_list = ManualLog.objects.exclude(dt__gte=today)
    for log in log_list:
        log.delete()
    model_root = "C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system"  
    dir_path = f"{model_root}/mlcc_datasets/smb"
    for i in range(1, 6):
        path = f'{dir_path}/pc{i}'
        if os.path.exists(path):
            shutil.rmtree(path)
            os.mkdir(path)
