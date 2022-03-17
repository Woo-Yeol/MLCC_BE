from rest_framework import generics
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import UserCreateSerializer, UserLoginSerializer
from .models import User

class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def signin(request):
    if request.method == "POST":
        serializer = UserLoginSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=True):
            return Response({"message" : "잘못된 Data 값 입니다."}, status=status.HTTP_409_CONFLICT)
        if serializer.validated_data['id'] == 'None':
            return Response({"message" : "로그인에 실패하였습니다."}, status=status.HTTP_409_CONFLICT)
        response = {
            'success' : 'True',
            'token' : serializer.data['token']
        }
        return Response(response, status=status.HTTP_200_OK)