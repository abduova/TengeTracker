from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.create(user=user)

        return Response({
            'token': token.key,
            'message': 'User created successfully'
        })

    return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    user = authenticate(
        username=request.data.get('username'),
        password=request.data.get('password')
    )

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

    return Response({'error': 'Invalid credentials'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response({'message': 'Logged out'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_auth(request):
    return Response({"message": "You are authenticated"})

#bota 
from rest_framework import generics
from .models import Transaction
from .serializers import TransactionSerializer

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Transaction.objects.all()

        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__name=category)

        order = self.request.GET.get('order')
        if order == 'desc':
            queryset = queryset.order_by('-amount')
        elif order == 'asc':
            queryset = queryset.order_by('amount')

        return queryset