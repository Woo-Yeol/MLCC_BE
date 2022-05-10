import os
import sys
import time
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
def set_data():
    # 1. 모델 실행
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dir_path="../mmcv_laminate_alignment_system"
    if len(os.scandir(dir_path + "/mlcc_datasets/val/")) != 0:
        terminal_command = f"python mlcc_inference.py \
            --det_cfg 'work_dirs/det/mask_rcnn_r50_fpn_1x_mlcc_refine/mask_rcnn_r50_fpn_1x_mlcc_refine.py' \
            --det_cp 'work_dirs/det/mask_rcnn_r50_fpn_2x_mlcc_refine/latest.pth' \
            --seg_cfg 'work_dirs/seg/mlcc_sementic_1k_refine/mlcc_sementic_1k_refine.py \
            --seg_cp 'work_dirs/seg/mlcc_sementic_1k_refine/latest.pth' \
            --source 'mlcc_datasets/val/' \
            --remove_edge_bbox --project 'mmcl_results' --name '{date}'"
        os.system(terminal_command)

        # 2. 모델 실행 후 데이터 적재
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
                                box_width = (anotation['bbox'][2] - anotation['bbox'][0]),
                                box_height = (anotation['bbox'][3] - anotation['bbox'][1]),
                                box_center_x = (anotation['bbox'][2] - (anotation['bbox'][2] - anotation['bbox'][0]) / 2),
                                box_center_y = (anotation['bbox'][3] - (anotation['bbox'][3] - anotation['bbox'][1]) / 2)
                            )
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


