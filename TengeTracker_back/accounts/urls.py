from django.urls import path
from .views import register, login, logout, test_auth, TransactionListView, TransactionCreateView, TransactionDeleteView, TransactionUpdateView
 
urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('logout/', logout),
    path('test/', test_auth),
    ## Transactions endpoint (Bota)
    path('transactions/', TransactionListView.as_view()),
    path('transactions/create/', TransactionCreateView.as_view()),
    path('transactions/delete/<int:pk>/', TransactionDeleteView.as_view()),
    path('transactions/update/<int:pk>/', TransactionUpdateView.as_view()),
]