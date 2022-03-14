from .serializers import UserCreateSerializer
from .models import User
from rest_framework import generics

class HWUserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer