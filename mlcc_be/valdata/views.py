from django.shortcuts import render
from rest_framework.generics import ListAPIView,RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Data, Bbox, Margin
from .serializers import DataSerializer, BboxSerializer, MarginSerializer
# Create your views here.


# Data
class DataListView(ListAPIView):
    queryset = Data.objects.all()
    serializer_class = DataSerializer

# class DataListView(APIView):
#     def get(self, request):
#         object = Data.objects.all()
#         serializer = DataSerializer(object, many=True)
#         return Response(serializer.data)

class DataRetrieveView(RetrieveAPIView):
    queryset = Data.objects.all()
    serializer_class = DataSerializer

# Bbox
class BboxListView(ListAPIView):
    queryset = Bbox.objects.all()
    serializer_class = BboxSerializer

class BboxRetrieveView(RetrieveAPIView):
    queryset = Bbox.objects.all()
    serializer_class = BboxSerializer
    lookup_fields = ['data']


# Margin
class MarginListView(ListAPIView):
    queryset = Margin.objects.all()
    serializer_class = MarginSerializer

class MarginRetrieveView(RetrieveAPIView):
    queryset = Margin.objects.all()
    serializer_class = MarginSerializer
    lookup_fields = ['bbox']
