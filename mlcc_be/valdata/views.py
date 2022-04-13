from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Data, Bbox, Margin
from .serializers import DataSerializer, BboxSerializer, MarginSerializer
# Create your views here.


# Data
class DataListView(ListCreateAPIView):
    queryset = Data.objects.all()
    serializer_class = DataSerializer

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
