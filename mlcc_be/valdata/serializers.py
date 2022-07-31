from rest_framework import serializers
from .models import Data, Bbox, ManualLog, Margin


class MarginSerializer(serializers.ModelSerializer):
    # bbox = BboxSerializer(many=True, read_only=True)

    class Meta:
        model = Margin
        fields = '__all__'


class BboxSerializer(serializers.ModelSerializer):
    # margins = MarginSerializer(many=True, read_only=True)
    # data = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Bbox
        fields = '__all__'


class DataSerializer(serializers.ModelSerializer):
    original_image = serializers.ImageField(use_url=True)
    segmentation_image = serializers.ImageField(use_url=True)
    bbox = BboxSerializer(many=True, read_only=True)

    class Meta:
        model = Data
        fields = '__all__'
        read_only_fields = ('bbox',)

class ManualLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualLog
        fields = '__all__'
