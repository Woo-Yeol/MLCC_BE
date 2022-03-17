from dataclasses import field
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from .models import User
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import update_last_login

User = get_user_model()
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER
JWT_ALLOW_REFRESH = api_settings.JWT_ALLOW_REFRESH
JWT_DECODE_HANDLER = api_settings.JWT_DECODE_HANDLER
JWT_PAYLOAD_GET_USER_ID_HANDLER = api_settings.JWT_PAYLOAD_GET_USER_ID_HANDLER


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

class UserLoginSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=64)
    password = serializers.CharField(write_only =True)
    token = serializers.CharField(max_length=255, read_only=True)


    def validate(self, data):
        id = data['id']
        password = data['password']
        user = authenticate(id = id, password=password)
        if user is None:
            return {
                'id' : 'None'
            }
        
        try:
            payload = JWT_PAYLOAD_HANDLER(user)
            jwt_token = JWT_ENCODE_HANDLER(payload)
            update_last_login(None, user)

        except User.DoesNotExist:
            raise serializers.ValidationError(
                '잘못된 아이디 또는 패스워드 입니다.'
            )
        return {
            'id': user.id,
            'token':jwt_token
        }
