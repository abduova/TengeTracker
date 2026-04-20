from django.urls import path
from .views import (
    register, login, logout, test_auth, me_view,
    TransactionListView, TransactionCreateView,
    TransactionDeleteView, TransactionUpdateView,
    WalletListCreateView, WalletDetailView,
    CategoryListCreateView, CategoryDetailView,
    get_balance, category_summary, income_summary, wallet_summary,
    test_api, status_api,
)

urlpatterns = [
    # --- Auth ---
    path('register/', register),
    path('login/', login),
    path('logout/', logout),
    path('test-auth/', test_auth),
    path('me/', me_view),

    # --- Wallets ---
    path('wallets/', WalletListCreateView.as_view()),
    path('wallets/<int:pk>/', WalletDetailView.as_view()),

    # --- Categories ---
    path('categories/', CategoryListCreateView.as_view()),
    path('categories/<int:pk>/', CategoryDetailView.as_view()),

    # --- Transactions ---
    path('transactions/', TransactionListView.as_view()),
    path('transactions/create/', TransactionCreateView.as_view()),
    path('transactions/delete/<int:pk>/', TransactionDeleteView.as_view()),
    path('transactions/update/<int:pk>/', TransactionUpdateView.as_view()),
    path('transactions/balance/', get_balance),
    path('transactions/summary/', category_summary),
    path('transactions/income-summary/', income_summary),
    path('transactions/wallet-summary/', wallet_summary),

    # --- Health ---
    path('test/', test_api),
    path('status/', status_api),
]
