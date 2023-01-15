import signal
from django.conf import settings
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.shortcuts import get_object_or_404 as _get_object_or_404
from django.core.exceptions import ValidationError
from django.http import Http404
from django.db import transaction

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from asgiref.sync import sync_to_async

from datetime import datetime, timedelta, date
from django.db.models import Avg

from .models import Data, Bbox, ManualLog, Margin, State, InferencePath
from .serializers import DataSerializer, BboxSerializer, ManualLogSerializer, MarginSerializer
from celery.schedules import crontab
from .tasks import model_lock
import os, shutil, sys, time, random, argparse, json
sys.path.append("C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system")
from mlcc_self_train_seg_det_eval import self_train_eval


# Main Page


@api_view(['GET'])
def main(request):
    queryset = Data.objects.all()
    threshold = request.query_params.get('threshold')
    period = request.query_params.get('period')
    if period is not None:
        from_date, to_date = period.split('~')
        from_date = list(map(int, from_date.split('.')))
        to_date = list(map(int, to_date.split('.')))
        queryset = queryset.filter(
            created_date__range=[date(from_date[0], from_date[1], from_date[2]), date(to_date[0], to_date[1], to_date[2])])
    else:
        today = date.today()
        queryset = queryset.filter(
            created_date__range=[today, today])
    queryset = queryset.order_by('-created_datetime')
    if threshold is None:
        threshold = 85
    queryset = DataSerializer(queryset, many=True, context={
                            'request': request}).data
    learning_timestamp = State.objects.all()[0].progress
    result = {
        "List": queryset,
        "Learning_Timestamp": learning_timestamp
    }
    return Response(result, headers={"description": "SUCCESS"})


@api_view(['GET'])
def detail(request, name):
    threshold = request.query_params.get('threshold')

    # Data, Bbox Query and Serializer
    data = DataSerializer(Data.objects.get(name=name),
                          context={'request': request}).data
    bbox = BboxSerializer(
        Bbox.objects.all().filter(data=name), many=True).data

    ratio = {}
    bbox_data = {}
    margin_list = {}

    for b in bbox:
        bbox_name = b['name']
        ratio[bbox_name] = b['min_margin_ratio']
        b.pop('name')
        b.pop('data')
        b.pop('min_margin_ratio')
        bbox_data[bbox_name] = b
        margin_data = MarginSerializer(
            Margin.objects.all().filter(bbox=bbox_name), many=True).data
        for m in margin_data:
            m.pop('name')
            m.pop('bbox')
        margin_list[bbox_name] = margin_data

    result = {
        "Original_image": data['original_image'],
        "Segmentation_image": data['segmentation_image'],
        "Box": bbox_data,
        "Ratio": ratio,
        "Margin_list": margin_list,
        "Cvat_url": data['cvat_url']
    }

    return Response(result, headers={"description": "SUCCESS"})


class DataListView(ListCreateAPIView):
    def get_normal_queryset(self):
        queryset = Data.objects.all()
        threshold = self.request.query_params.get('threshold')
        if threshold is not None:
            # SELECT ... WHERE margin_ratio >= threshold
            queryset = queryset.filter(margin_ratio__gte=threshold)
        return queryset

    queryset = Data.objects.all()
    serializer_class = DataSerializer


class DataRetrieveView(RetrieveUpdateDestroyAPIView):
    queryset = Data.objects.all()
    serializer_class = DataSerializer


class BboxListView(ListCreateAPIView):
    queryset = Bbox.objects.all()
    serializer_class = BboxSerializer


class BboxRetrieveView(RetrieveUpdateDestroyAPIView):
    queryset = Bbox.objects.all()
    serializer_class = BboxSerializer


class MarginListView(ListCreateAPIView):
    queryset = Margin.objects.all()
    serializer_class = MarginSerializer


class MarginRetrieveView(RetrieveUpdateDestroyAPIView):
    queryset = Margin.objects.all()
    serializer_class = MarginSerializer
    

class ManualLogListView(ListCreateAPIView):
    queryset = ManualLog.objects.all()
    serializer_class = ManualLogSerializer

# schedule set
@api_view(['GET'])
def set_schedule(request):
    if request.method == 'GET':
        mode = State.objects.all()[0].mode
        return Response({"mode": mode})

# thr set
@api_view(['GET'])
def set_thr(request):
    if request.method == 'GET':
        thr = State.objects.all()[0].threshold * 100
        return Response({thr})

@api_view(['POST'])
def set_environment_variable(request):
    if request.method == 'POST':
        mode = request.META.get('HTTP_MODE')
        thr = request.META.get('HTTP_THRESHOLD')
        if mode == 'auto':
            s = State.objects.all()[0]
            s.mode = 'auto'
            s.save()
        elif mode == 'manual':
            s = State.objects.all()[0]
            s.mode = 'manual'
            s.save()
        elif mode == None:
            pass
        else:
            return Response({'400': 'Bad request'})
    
        if thr == None:
            pass
        elif 0 <= int(thr) <= 100:
            s = State.objects.all()[0]
            s.threshold = int(thr) / 100
            s.save()   
        else:
            return Response({'400': 'Bad request'})

        return Response({"200", f"ok"})

@api_view(['GET', 'POST', 'DELETE'])

def self_train(request):
    if request.method == 'GET':
        s = State.objects.all()[0]
        return Response(s.progress)

    if request.method == 'DELETE':
        s = State.objects.all()[0]
        pid = s.pid
        try:
            os.kill(pid, signal.SIGTERM)
        finally:
            s.pid = -1
            s.save()
            return Response({"200", f"ok"})
    
    # TODO HEADER CORS ADD
    if request.method == 'POST':
        learning_type = json.loads(request.META.get('HTTP_LEARNING_TYPE'))
        seg_data_type = json.loads(request.META.get('HTTP_SEGMENTATION_DATA_TYPE'))
        det_epochs = int(request.META.get('HTTP_DETECTION_EPOCHS', 4))
        seg_iter = int(request.META.get('HTTP_SEGMENTATION_ITERATIONS', 200))
        det_rate = int(request.META.get('HTTP_DETECTION_LEARNING_RATE', 0))
        seg_rate = int(request.META.get('HTTP_SEGMENTATION_DATA_RATE', 0))
        det_date = request.META.get('HTTP_DETECTION_LEARNING_DATE', '')
        seg_date = request.META.get('HTTP_SEGMENTATION_LEARNING_DATE', '')
        det_start_date, det_end_date = det_date.split('~')
        seg_start_date, seg_end_date = seg_date.split('~')
        det_start_date = det_start_date.replace('.', '')
        det_end_date = det_end_date.replace('.', '')
        seg_start_date = seg_start_date.replace('.', '')
        seg_end_date = seg_end_date.replace('.', '')
        det = learning_type['detection']
        seg = learning_type['segmentation']
        gen = seg_data_type['created']
        inf = seg_data_type['result']
        mod = seg_data_type['modified']

        # celery 구동 중지 기다리기
        while True:
            s = State.objects.all()[0]
            if s.work:
                time.sleep(1)
            else:
                s.work = True
                s.progress = 0
                s.save()
                break
        ts = datetime.today().timestamp()
        print(datetime.today())
        s = State.objects.all()[0]
        s.progress = ts
        s.save()
        try:
            print(det, seg, gen)
            # 자가학습 실행
            # def train(det=True, seg=True, det_epochs=4, seg_iter=20000, det_rate=100, seg_rate=100, start_date='', end_date='', gen=True, inf=True, mod=True)
            system_str = f"python C:\\Users\\user\\Desktop\\IITP\\mmcv_laminate_alignment_system\\mlcc_self_train_seg_det_train.py \
                --det_epochs {det_epochs} --seg_iter {seg_iter} --det_rate {det_rate} --seg_rate {seg_rate} \
                --det_start_date {det_start_date} --det_end_date {det_end_date} --seg_start_date {seg_start_date} --seg_end_date {seg_end_date}"
            if det:
                system_str += f" --det {det}"
            if seg:
                system_str += f" --seg {seg}"
            if inf:
                system_str += f" --inf {inf}"
            if mod:
                system_str += f" --mod {mod}"
            if gen:
                system_str += f" --gen {gen}"
            print(system_str)
            os.system(system_str)
            
            # os.system("sh C:/Users/user/Desktop/IITP/mmcv_laminate_alignment_system/run_self_train.sh")
            return Response({"200", f"ok"})
        except:
            s.progress = -1
            s.save()
            return Response({'400': 'Bad request'})
        finally:
            s.progress = -1
            s.save()

# TODO model det, seg로 분리, seg_det_eval.py에 경로 인자 전달 및 기능 구현
@api_view(['GET'])
def eval_self_train(request):
    # 모델 저장
    s = State.objects.all()[0]
    new_det_path = request.GET.get('det_path')
    new_seg_path = request.GET.get('seg_path')
    curr_det_path = InferencePath.objects.get(name=s.target_det_model).path
    curr_seg_path = InferencePath.objects.get(name=s.target_seg_model).path
    det_acc, seg_acc = self_train_eval(new_det_path, new_seg_path, curr_det_path, curr_seg_path)

    if det_acc:
        det_name = new_det_path.split('det')[1].split("\\")
        det_name = f"det_{det_name[2]}"
        InferencePath.objects.create(name = det_name, path = new_det_path, acc = det_acc)
        # 기본 inference 모델 설정
        det_highest = InferencePath.objects.filter(path__contains = 'det').order_by('-acc')[0]
        s.target_det_model = det_highest.name
        # 하위 모델 삭제
        if InferencePath.objects.filter(path__contains = 'det').exclude(name = "Default").count() > 5:
            models = InferencePath.objects.filter(path__contains = 'det').exclude(name = "Default").order_by('-acc')[5:]
            for model in models:
                path = model.path
                if os.path.exists(path):
                    shutil.rmtree(path)
    
    if seg_acc:
        seg_name = new_seg_path.split('seg')[1].split("\\")
        seg_name = f"seg_{seg_name[2]}"
        InferencePath.objects.create(name = seg_name, path = new_seg_path, acc = seg_acc)
        # 기본 inference 모델 설정
        seg_highest = InferencePath.objects.filter(path__contains = 'seg').order_by('-acc')[0]
        s.target_seg_model = seg_highest.name
        # 하위 모델 삭제
        if InferencePath.objects.filter(path__contains = 'det').exclude(name = "Default").count() > 5:
            models = InferencePath.objects.filter(path__contains = 'seg').exclude(name = "Default").order_by('-acc')[5:]
            for model in models:
                path = model.path
                if os.path.exists(path):
                    shutil.rmtree(path)
            
    # celery 구동 재개
    s = State.objects.all()[0]
    s.progress = -1
    s.work = False
    s.save()
    return Response({"200", f"ok"})

@api_view(['GET', 'POST'])
def det_model(request): # 현재모델, 모델선택
    if request.method == 'GET':
        target_model = State.objects.all()[0].target_det_model
        return Response({target_model})

    if request.method == 'POST':
        name = request.query_params.get('name')
        if InferencePath.objects.filter(name=name).exists():
            s = State.objects.all()[0]
            s.target_det_model = name
            s.save()
            return Response({"200", f"ok"})
        else:
            return Response({"405", f"Model not found"})


@api_view(['GET', 'POST'])
def seg_model(request): # 현재모델, 모델선택
    if request.method == 'GET':
        target_model = State.objects.all()[0].target_seg_model
        return Response({target_model})

    if request.method == 'POST':
        name = request.query_params.get('name')
        if InferencePath.objects.filter(name=name).exists():
            s = State.objects.all()[0]
            s.target_seg_model = name
            s.save()
            return Response({"200", f"ok"})
        else:
            return Response({"405", f"Model not found"})


# 전체 이미지 중 랜덤..?
@api_view(['GET'])
def det_sample_img(request):
    num = request.query_params.get('num')
    if num == None:
        num = "0"
    if num == "0":
        num = random.randint(1, 10)
    else:
        num = int(num)
    det_models = InferencePath.objects.filter(path__contains = 'det').exclude(name="Dafault").order_by('-acc')[:5].values("name", "path")
    default = InferencePath.objects.get(name="Detection_Default")
    root = "127.0.0.1:8000"
    res = {}
    res[default.name] = f"{root}/{default.path}/{num}.jpg"
    for model in det_models:
        name = model["name"]
        path = model["path"]
        res[name] = f"{root}/{path}/{num}.jpg"

    return Response(res)


@api_view(['GET'])
def seg_sample_img(request):
    num = request.query_params.get('num')
    if num == None:
        num = "0"
    if num == "0":
        num = random.randint(1, 10)
    else:
        num = int(num)
    det_models = InferencePath.objects.filter(path__contains = 'seg').exclude(name="Dafault").order_by('-acc')[:5].values("name", "path")
    default = InferencePath.objects.get(name="Segmentation_Default")
    root = "127.0.0.1:8000"
    res = {}
    res[default.name] = f"{root}/{default.path}/{num}.jpg"
    for model in det_models:
        name = model["name"]
        path = model["path"]
        res[name] = f"{root}/{path}/{num}.jpg"

    return Response(res)


@api_view(['GET'])
def pid(request):
    pid = request.query_params.get('pid')
    s = State.objects.all()[0]
    s.pid = pid
    s.save()
    return Response({'200': 'ok'})



@api_view(['GET'])
def reset(request):
    data = Data.objects.all()
    data.delete()
    return Response({'200': 'ok'})