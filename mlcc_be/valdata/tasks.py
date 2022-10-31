import typing, os, pathlib, shutil, sys, re, cv2
import pandas as pd
import numpy as np
from math import inf
from PIL import Image
from datetime import datetime, date, timedelta
from .models import Data, Bbox, Margin, ManualLog, State, InferencePath
from django.conf import settings
from django.core.files.images import ImageFile
from django.shortcuts import get_object_or_404 
from django.db import transaction
from asgiref.sync import sync_to_async
sys.path.append("C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system")
from mlcc_django import auto_run_model, manual_run_model
from mlcc_systemkits.mlcc_system import MLCC_SYSTEM
from celery import shared_task
# db에 데이터 넣을 때 역순으로 넣기

running: bool = False
results = []
# model_root = "C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system"
model_root = "D:"
OriginalFunc = typing.Callable[..., typing.Any]
DecoratedFunc = typing.Callable[..., typing.Any]

# running Flag
def model_lock(func: OriginalFunc) -> DecoratedFunc:
    def wrapper():
        s = State.objects.all()[0]
        if s.work:
            print("Model Working")
            return
        s.work = True
        s.save()
        func()                        
    return wrapper

# 모델 경로 설정
def set_input_dir(input_dir_path: str) -> str:
    first_create_time = datetime.now()
    first_create_pc = ''
    for path, subdirs, files in os.walk(input_dir_path):
        for name in files:
            if 'input' in path: 
                t = datetime.fromtimestamp(os.path.getmtime(pathlib.PurePath(path, name)))
                if t < first_create_time:
                    first_create_time = t
                    first_create_pc = re.compile('pc[0-9]*').search(path).group()
                    print(first_create_pc) # test print
    pc_name = first_create_pc

    return pc_name

@shared_task
def get_model_output() -> None:
    auto_get_result()
    # system_mode = State.objects.all()[0].mode
    # if system_mode == 'auto':
    #     auto_get_result()
    # elif system_mode == 'manual':
    #     manual_get_result()


@model_lock
def auto_get_result() -> None:
    try:
        # 실행 경로 정하기
        input_dir_path: str = f"{model_root}/mlcc_datasets/smb"
        dt = datetime.now().strftime('%y%m%d_%H%M%S')
        pc_name = set_input_dir(input_dir_path)
        target_model = State.objects.all()[0].target_model
        if target_model == 'auto':
            seg_cp_pth = InferencePath.objects.all().order_by("-acc")[0].path
        else:
            seg_cp_pth = InferencePath.objects.get(name=target_model).path
        

        # 모델 실행 및 결과파일 생성
        if pc_name != '':
            threshold = State.objects.all()[0].threshold
            results = auto_run_model(seg_cp_pth, dt, pc_name, threshold)
            for i, result in enumerate(results):
                save_result(i, result, pc_name)

            # 3. DB 적재한 모델 원본 데이터 삭제
            entries = os.scandir(f'{model_root}/mlcc_datasets/smb/{pc_name}/input')
            for entry in entries:
                if not entry.is_dir():
                    os.remove(entry.path)
        else:
            print("Folder empty")

    except Exception as e:
        print(e)
    finally:
        s = State.objects.all()[0]
        s.work = False
        s.save()

@model_lock
def manual_get_result() -> None:
    try:   
        # 실행 경로 정하기
        input_dir_path = f"{model_root}/mlcc_datasets/smb"
        backup_path = f"{input_dir_path}/backup"
        dt = datetime.now().strftime('%y%m%d_%H%M%S')
        pc_name = set_input_dir(input_dir_path)

        # 2. 모델 실행 및 결과파일 생성
        if pc_name != '':
            global results
            threshold = State.objects.all()[0].threshold
            results = manual_run_model(pc_name, threshold)
            os.makedirs(f'{input_dir_path}/{pc_name}/{dt}')
            for result in results:
                assessment = True
                for qa_result in result['qa_result_list']:
                    if qa_result['decision_result'] == False:
                        assessment = False
                        break

                f = open(f'{input_dir_path}/{pc_name}/{dt}/{result["img_basename"]}_{str(assessment)}.txt', 'w')
                f.close()
                shutil.copyfile(f'{input_dir_path}/{pc_name}/{result["img_basename"]}', f'{backup_path}/{dt}_{result["img_basename"]}')
                shutil.move(f'{input_dir_path}/{pc_name}/{result["img_basename"]}', f'{input_dir_path}/{pc_name}/{dt}/{result["img_basename"]}')
                # 3. DB에 Log 적재
                log = ManualLog()
                log.filename = result["img_basename"]
                log.dt = datetime.now()
                log.save()

    except:
        print("Failed run model")

# Create Data and Make File
@transaction.atomic
def save_result(i: int, result: dict, pc_name: str) -> None:
    if Data.objects.filter(name = result['img_basename'][0:len(result['img_basename'])-4]).exists():
        return -1
    # set img url
    server_root = "D:"
    img_name = result['img_basename']
    seg_name = img_name[0:len(img_name)-4] + '_seg.jpg'
    img_dir = f"{server_root}/mlcc_datasets/smb/data/{datetime.now().strftime('%m.%d')}"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    os.makedirs(f"{img_dir}/{img_name[0:len(img_name)-4]}", exist_ok=True)
    r = np.array(result['img0'])
    s = np.array(result['seg_img'])
    cv2.imwrite(f"{img_dir}/{img_name[0:len(img_name)-4]}/{img_name}", r)
    cv2.imwrite(f"{img_dir}/{img_name[0:len(img_name)-4]}/{seg_name}", s)
    # Create data
    d, created = Data.objects.get_or_create(
        name = img_name[0:len(img_name)-4],
        source_pc = pc_name,
        original_image = f"{server_root}/mlcc_datasets/smb/data/{datetime.now().strftime('%m.%d')}/{img_name[0:len(img_name)-4]}/{img_name}",
        segmentation_image = f"{server_root}/mlcc_datasets/smb/data/{datetime.now().strftime('%m.%d')}/{img_name[0:len(img_name)-4]}/{seg_name}",
        created_date = date.today(),
        margin_ratio = 0,
        cvat_url = f'http://localhost:8080/tasks/1/jobs/1?frame={i}'
    )

    total_min_ratio = inf
    assessment = 'OK'

    for bbox_id, qa_result in enumerate(result['qa_result_list']):

        if qa_result['decision_result'] == False:
            assessment = 'NG'
        b, created = Bbox.objects.get_or_create(
            name=img_name[0:len(img_name)-4] + '_bbox_' + str(bbox_id+1),
            data=d,
            min_margin_ratio=qa_result['min_margin_ratio']*100,
            box_width = (result['bboxes'][bbox_id][2] - result['bboxes'][bbox_id][0]),
            box_height = (result['bboxes'][bbox_id][3] - result['bboxes'][bbox_id][1]),
            box_x = result['bboxes'][bbox_id][0],
            box_y = result['bboxes'][bbox_id][1],
        )
        for i in range(len(qa_result['first_lst'])):
            m, created = Margin.objects.get_or_create(
                name=img_name[0:len(img_name)-4] + '_bbox_' + str(bbox_id+1) + '_magrin_' + str(i+1),
                bbox=b,
                margin_x = result['bboxes'][bbox_id][0] + qa_result['first_lst'][i],
                margin_y = result['bboxes'][bbox_id][1] + i,
                real_margin = qa_result['real_margin'],
                margin_ratio = qa_result['margin_ratio'][i]*100,
                margin_width = qa_result['last_lst'][i]-qa_result['first_lst'][i],
            )
        
        total_min_ratio = min(total_min_ratio, qa_result['min_margin_ratio'])
    
    d.margin_ratio = total_min_ratio * 100
    d.save()

    # Make save
    input_dir_path = f"{model_root}/mlcc_datasets/smb"
    f = open(f'{input_dir_path}/{pc_name}/results/{result["img_basename"]}_{assessment}.txt', 'w')
    f.close()
    



# delete log, file
@shared_task
def reset_data():
    today = date.today()
    log_list = ManualLog.objects.exclude(dt__gte=today)
    for log in log_list:
        log.delete()
    input_dir_path = f"{model_root}/mlcc_datasets/smb"
    for i in range(1, 6):
        path = f'{input_dir_path}/pc{i}'
        if os.path.exists(path):
            shutil.rmtree(path)
            os.mkdir(path)
            os.mkdir(f"{path}/input")
            os.mkdir(f"{path}/results")
