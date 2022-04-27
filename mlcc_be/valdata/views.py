from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.shortcuts import get_object_or_404 as _get_object_or_404
from django.core.exceptions import ValidationError
from django.http import Http404

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from asgiref.sync import sync_to_async

import datetime
from django.db.models import Avg

from .models import Data, Bbox, Margin
from .serializers import DataSerializer, BboxSerializer, MarginSerializer
# Main Page


@api_view(['GET'])
def main(request):
    queryset = Data.objects.all()
    threshold = request.query_params.get('threshold')
    period = request.query_params.get('period')
    cutoff = request.query_params.get('cutoff')
    if period is not None:
        from_date, to_date = period.split('~')
        from_date = list(map(int, from_date.split('.')))
        to_date = list(map(int, to_date.split('.')))
        queryset = queryset.filter(
            created_date__range=[datetime.date(from_date[0], from_date[1], from_date[2]), datetime.date(to_date[0], to_date[1], to_date[2])])
    if threshold is not None:
        # SELECT ... WHERE margin_ratio >= threshold
        normal = queryset.filter(margin_ratio__gte=threshold)
        # SELECT ... WHERE margin_ratio < threshold
        error = queryset.filter(margin_ratio__lt=threshold)
        normal = DataSerializer(normal, many=True, context={
                                'request': request}).data
        error = DataSerializer(error, many=True, context={
                               'request': request}).data
        result = {
            "Normal": normal,
            "Error": error
        }
    else:
        result = DataSerializer(queryset, many=True, context={
                                'request': request}).data
    return Response(result, headers={"description": "SUCCESS"})

# Detail


@api_view(['GET'])
def detail(request, name):
    box_name = request.query_params.get('box')
    cut_off = request.query_params.get(
        'cut-off') if request.query_params.get('cut-off') is not None else 0

    if box_name is not None:
        result = {}
        margin = Margin.objects.all().filter(bbox=box_name, cut_off=cut_off)
        margin = MarginSerializer(margin, many=True).data
        for m in margin:
            num = m['margin_num']
            m.pop('cut_off')
            m.pop('margin_num')
            m.pop('bbox')
            result[num] = m
    else:
        data = DataSerializer(Data.objects.get(name=name),
                              context={'request': request}).data
        bbox = BboxSerializer(
            Bbox.objects.all().filter(data=name), many=True).data
        ratio = {}
        bbox_data = {}
        for b in bbox:
            name = b['name']
            ratio[name] = b['min_margin_ratio']
            b.pop('name')
            b.pop('data')
            b.pop('min_margin_ratio')
            bbox_data[name] = b

        result = {
            "original_img": data['original_image'],
            "Box": bbox_data,
            "Ratio": ratio,
        }
    return Response(result, headers={"description": "SUCCESS"})

# Data


class DataListView(ListAPIView):
    def get_normal_queryset(self):
        queryset = Data.objects.all()
        threshold = self.request.query_params.get('threshold')
        if threshold is not None:
            # SELECT ... WHERE margin_ratio >= threshold
            queryset = queryset.filter(margin_ratio__gte=threshold)
        return queryset

    queryset = Data.objects.all()
    serializer_class = DataSerializer

# class DataListView(ListCreateAPIView):
#     queryset = Data.objects.all()
#     serializer_class = DataSerializer


class DataRetrieveView(RetrieveUpdateDestroyAPIView):
    queryset = Data.objects.all()
    serializer_class = DataSerializer

# Bbox


class BboxListView(ListCreateAPIView):
    queryset = Bbox.objects.all()
    serializer_class = BboxSerializer


class BboxRetrieveView(RetrieveUpdateDestroyAPIView):
    queryset = Bbox.objects.all()
    serializer_class = BboxSerializer
    # lookup_fields = ['data']

# Margin


class MarginListView(ListCreateAPIView):
    queryset = Margin.objects.all()
    serializer_class = MarginSerializer


class MarginRetrieveView(RetrieveUpdateDestroyAPIView):
    queryset = Margin.objects.all()
    serializer_class = MarginSerializer
    # lookup_fields = ['bbox']
