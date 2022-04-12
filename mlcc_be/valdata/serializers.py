from rest_framework import serializers
from .models import Data, Bbox, Margin

class MarginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Margin
        fields = ['__all__']

class BboxSerializer(serializers.ModelSerializer):
    # margin_list = MarginSerializer(many=True, read_only=True)
    class Meta:
        model = Bbox
        fields = ['__all__']

class DataSerializer(serializers.ModelSerializer):
    # bboxs = serializers.StringRelatedField(many=True)
    # bbox_list = BboxSerializer(many=True, read_only=True)
    class Meta:
        model = Data
        fields = ['__all__']

