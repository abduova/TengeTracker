from django.urls import path
from .views import register, login, logout, test_auth, TransactionListView, TransactionCreateView, TransactionDeleteView, TransactionUpdateView
from .views import get_balance, category_summary
from .views import test_api, status_api
urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('logout/', logout),
    path('test-auth/', test_auth),
    ## Transactions endpoint (Bota)
    path('transactions/', TransactionListView.as_view()),
    path('transactions/create/', TransactionCreateView.as_view()),
    path('transactions/delete/<int:pk>/', TransactionDeleteView.as_view()),
    path('transactions/update/<int:pk>/', TransactionUpdateView.as_view()),
    path('transactions/balance/', get_balance),
    path('test/', test_api),
    path('status/', status_api),
    path('transactions/summary/', category_summary),
]