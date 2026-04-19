from unicodedata import category
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
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)

        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__name=category)

        order = self.request.GET.get('order')
        if order == 'desc':
            queryset = queryset.order_by('-amount')
        elif order == 'asc':
            queryset = queryset.order_by('amount')
        # ФИЛЬТР ПО ТИПУ (доход / расход)
        type_filter = self.request.GET.get('type')

        if type_filter:
            queryset = queryset.filter(type=type_filter)

    # ФИЛЬТР ПО ДАТЕ
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)

        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
    # ФИЛЬТР ПО СУММЕ
        min_amount = self.request.GET.get('min_amount')
        max_amount = self.request.GET.get('max_amount')

        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)

        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)


        return queryset 
    

class TransactionCreateView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    
class TransactionDeleteView(generics.DestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
    

class TransactionUpdateView(generics.UpdateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
        
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balance(request):
    user = request.user

    # считаем доходы
    income = Transaction.objects.filter(
        user=user,
        type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    # считаем расходы
    expense = Transaction.objects.filter(
        user=user,
        type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    # считаем баланс
    balance = income - expense

    return Response({
        "income": income,
        "expense": expense,
        "balance": balance
    })
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_summary(request):
    user = request.user

    data = (
        Transaction.objects
        .filter(user=user, type='expense')
        .values('category__name')
        .annotate(total=Sum('amount'))
    )

    return Response(data)
# ДОХОДЫ ПО КАТЕГОРИЯМ
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def income_summary(request):
    user = request.user

    data = (
        Transaction.objects
        .filter(user=user, type='income')
        .values('category__name')
        .annotate(total=Sum('amount'))
    )

    return Response(data)


# БАЛАНС ПО КОШЕЛЬКАМ
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_summary(request):
    user = request.user

    data = (
        Transaction.objects
        .filter(user=user)
        .values('wallet__name')
        .annotate(total=Sum('amount'))
    )

    return Response(data)
    
    # ПРОСТОЙ ТЕСТ API
@api_view(['GET'])
@permission_classes([AllowAny])
def test_api(request):
    return Response({"message": "API is working"})


# СТАТУС СЕРВЕРА
@api_view(['GET'])
@permission_classes([AllowAny])
def status_api(request):
    return Response({"status": "OK"})