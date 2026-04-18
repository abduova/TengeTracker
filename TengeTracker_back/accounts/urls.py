from django.urls import path
from .views import register, login, logout, test_auth, TransactionListView

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('logout/', logout),
    path('test/', test_auth),
    ## Transactions endpoint (Bota)
    path('transactions/', TransactionListView.as_view()),
]