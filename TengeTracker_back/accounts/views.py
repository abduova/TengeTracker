from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Sum

from .models import Wallet, Category, Transaction
from .serializers import (
    RegisterSerializer,
    WalletSerializer,
    CategorySerializer,
    TransactionSerializer,
)


# AUTH
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
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
        return Response({'token': token.key, 'username': user.username})
    return Response({'error': 'Invalid credentials'}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response({'message': 'Logged out'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_auth(request):
    return Response({"message": "You are authenticated", "username": request.user.username})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Return the current logged-in user."""
    u = request.user
    return Response({
        'id': u.id,
        'username': u.username,
        'email': u.email,
    })


# WALLETS (CRUD)
class WalletListCreateView(generics.ListCreateAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WalletDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)


# CATEGORIES (CRUD)
class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Category.objects.filter(user=self.request.user) | Category.objects.filter(user__isnull=True)

        type_filter = self.request.GET.get('type')
        if type_filter:
            qs = qs.filter(type=type_filter)
        return qs.order_by('name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


# TRANSACTIONS (CRUD + filtering)
class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)

        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__name=category)

        wallet = self.request.GET.get('wallet')
        if wallet:
            queryset = queryset.filter(wallet__name=wallet)

        type_filter = self.request.GET.get('type')
        if type_filter:
            queryset = queryset.filter(type=type_filter)

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        min_amount = self.request.GET.get('min_amount')
        max_amount = self.request.GET.get('max_amount')
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)

        order = self.request.GET.get('order')
        if order == 'desc':
            queryset = queryset.order_by('-amount')
        elif order == 'asc':
            queryset = queryset.order_by('amount')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset


def _apply_wallet_delta(wallet, amount, t_type, sign=1):
    """Helper: update wallet balance. sign=+1 to apply, -1 to revert."""
    if not wallet:
        return
    if t_type == 'income':
        wallet.balance += sign * amount
    else:
        wallet.balance -= sign * amount
    wallet.save()


class TransactionCreateView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        transaction = serializer.save(user=self.request.user)
        _apply_wallet_delta(transaction.wallet, transaction.amount, transaction.type, sign=1)


class TransactionDeleteView(generics.DestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        _apply_wallet_delta(instance.wallet, instance.amount, instance.type, sign=-1)
        instance.delete()


class TransactionUpdateView(generics.UpdateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        old = self.get_object()
        _apply_wallet_delta(old.wallet, old.amount, old.type, sign=-1)
        new = serializer.save()
        _apply_wallet_delta(new.wallet, new.amount, new.type, sign=1)


# SUMMARIES
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balance(request):
    user = request.user
    income = Transaction.objects.filter(user=user, type='income') \
        .aggregate(total=Sum('amount'))['total'] or 0
    expense = Transaction.objects.filter(user=user, type='expense') \
        .aggregate(total=Sum('amount'))['total'] or 0
    balance = income - expense
    return Response({"income": income, "expense": expense, "balance": balance})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_summary(request):
    """Totals spent per expense category."""
    data = (
        Transaction.objects
        .filter(user=request.user, type='expense')
        .values('category__name', 'category__icon', 'category__color')
        .annotate(total=Sum('amount'))
    )
    return Response(list(data))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def income_summary(request):
    """Totals earned per income category."""
    data = (
        Transaction.objects
        .filter(user=request.user, type='income')
        .values('category__name', 'category__icon', 'category__color')
        .annotate(total=Sum('amount'))
    )
    return Response(list(data))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_summary(request):
    """Per-wallet net flow (income - expense)."""
    from django.db.models import Case, When, F, FloatField
    data = (
        Transaction.objects
        .filter(user=request.user)
        .values('wallet__name', 'wallet__icon', 'wallet__color')
        .annotate(
            total=Sum(Case(
                When(type='income', then=F('amount')),
                When(type='expense', then=-F('amount')),
                output_field=FloatField(),
            ))
        )
    )
    return Response(list(data))


# HEALTH / TEST
@api_view(['GET'])
@permission_classes([AllowAny])
def test_api(request):
    return Response({"message": "API is working"})


@api_view(['GET'])
@permission_classes([AllowAny])
def status_api(request):
    return Response({"status": "OK"})


# SIMPLE APIVIEW (for requirement)

class SimpleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "This is APIView",
            "user": request.user.username
        })


class SecondAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "status": "Second APIView works"
        })

