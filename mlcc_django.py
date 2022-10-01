from datetime import datetime
import os
import os.path as osp
import time
import torch
import argparse
import mmcv
import json
import cv2
import matplotlib.pyplot as plt
import numpy as np
from mmcv import Config
from mlcc_systemkits.mlcc_system import MLCC_SYSTEM
from mlcc_systemkits.utils import load_img_paths, NumpyEncoder

def auto_run_model(date, pc_name, thr):
    args = {
        'det_cfg': 'C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system/work_dirs/det/mask_rcnn_r50_fpn_1x_mlcc_refine/mask_rcnn_r50_fpn_1x_mlcc_refine.py',
        'det_cp': 'C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system/work_dirs/det/mask_rcnn_r50_fpn_2x_mlcc_refine/latest.pth' ,
        'seg_cfg': 'C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system/work_dirs/seg/mlcc_sementic_1k_refine/mlcc_sementic_1k_refine.py',
        'seg_cp': 'C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system/work_dirs/seg/mlcc_sementic_1k_refine/latest.pth',
        'source': f'C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system/mlcc_datasets/smb/{str(pc_name)}/',
        'gpu_id': '0',
        'score_thr': 0.30,
        'remove_edge_bbox': True,
        'refine_ratio': 0.06,
        'margin_thr': thr,
        'cut_off': 0,
        'name': date,
        'project': 'mmcl_results'
    }   
    
    det_cfg = Config.fromfile(args['det_cfg'])
    seg_cfg = Config.fromfile(args['seg_cfg'])    
    if args['name'] is None:
        args['name'] = osp.splitext(osp.basename(args.det_cfg))[0]
    save_dir = f"C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system/{args['project']}/{args['name']}"
    mmcv.mkdir_or_exist(osp.abspath(save_dir))    
        
    det_cfg.dump(osp.join(save_dir, osp.basename(args['det_cfg'])))
    seg_cfg.dump(osp.join(save_dir, osp.basename(args['seg_cfg'])))
    
    device = torch.device("cuda:{}".format(args['gpu_id']) \
        if torch.cuda.is_available() else "cpu")         
        
    mlcc_system = MLCC_SYSTEM(
        det_cfg = args['det_cfg'], 
        det_cp = args['det_cp'], 
        seg_cfg = args['seg_cfg'],
        seg_cp = args['seg_cp'],
        device=device)

    img_paths = load_img_paths(args['source'])
    num_inctances = 0
    num_img = 0
    results = []
    for img_path in img_paths:           
        # bboxes, segms, labels = mlcc_system.get_results(img_path, args.score_thr)        
        result = mlcc_system.get_result(img_path = img_path, 
                                         score_thr = args['score_thr'], 
                                         remove_edge_bbox = args['remove_edge_bbox'],
                                         refine_ratio = args['refine_ratio'],
                                         margin_thr = args['margin_thr'],
                                         cut_off = args['cut_off'])
        results.append(result)
        #mlcc_system.save_results(result, save_dir)         
    return results


def manual_run_model(pc_name, thr):
    args = {
        'det_cfg': 'C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system/work_dirs/det/mask_rcnn_r50_fpn_1x_mlcc_refine/mask_rcnn_r50_fpn_1x_mlcc_refine.py',
        'det_cp': 'C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system/work_dirs/det/mask_rcnn_r50_fpn_2x_mlcc_refine/latest.pth' ,
        'seg_cfg': 'C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system/work_dirs/seg/mlcc_sementic_1k_refine/mlcc_sementic_1k_refine.py',
        'seg_cp': 'C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system/work_dirs/seg/mlcc_sementic_1k_refine/latest.pth',
        'source': f'C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system/mlcc_datasets/smb/{str(pc_name)}/',
        'gpu_id': '0',
        'score_thr': 0.30,
        'remove_edge_bbox': True,
        'refine_ratio': 0.06,
        'margin_thr': thr,
        'cut_off': 0,
        'name': '',
        'project': 'mmcl_results'
    }   
    
    det_cfg = Config.fromfile(args['det_cfg'])
    seg_cfg = Config.fromfile(args['seg_cfg'])    
    if args['name'] is None:
        args['name'] = osp.splitext(osp.basename(args.det_cfg))[0]
    save_dir = f"C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system/{args['project']}/{args['name']}"
    # mmcv.mkdir_or_exist(osp.abspath(save_dir))    
        
    # det_cfg.dump(osp.join(save_dir, osp.basename(args['det_cfg'])))
    # seg_cfg.dump(osp.join(save_dir, osp.basename(args['seg_cfg'])))
    
    device = torch.device("cuda:{}".format(args['gpu_id']) \
        if torch.cuda.is_available() else "cpu")         
        
    mlcc_system = MLCC_SYSTEM(
        det_cfg = args['det_cfg'], 
        det_cp = args['det_cp'], 
        seg_cfg = args['seg_cfg'],
        seg_cp = args['seg_cp'],
        device=device)

    img_paths = load_img_paths(args['source'])
    num_inctances = 0
    num_img = 0
    results = []
    for img_path in img_paths:           
        # bboxes, segms, labels = mlcc_system.get_results(img_path, args.score_thr)        
        result = mlcc_system.get_result(img_path = img_path, 
                                         score_thr = args['score_thr'], 
                                         remove_edge_bbox = args['remove_edge_bbox'],
                                         refine_ratio = args['refine_ratio'],
                                         margin_thr = args['margin_thr'],
                                         cut_off = args['cut_off'])
        results.append(result)
        #mlcc_system.save_results(result, save_dir)         
    return results