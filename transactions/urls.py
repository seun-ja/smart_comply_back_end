from django.urls import include
from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import TransactionViewSet

router = DefaultRouter()

router.register(
    "",
    TransactionViewSet,
    basename="transactions",
)

urlpatterns = [
    path("", include(router.urls)),
]