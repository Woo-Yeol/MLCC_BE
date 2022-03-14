from rest_framework import serializers
from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = User.objects.create(
            id=validated_data['id'],
            email=validated_data['email'],
            nickname=validated_data['nickname'],
            name=validated_data['name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ['id', 'nickname', 'name', 'email', 'password']
