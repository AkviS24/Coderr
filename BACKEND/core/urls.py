from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from offers_app.api.views import OfferDetailsView
from orders_app.api.views import OrderCountView, CompletedOrderCountView

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/',
        include('profile_app.api.urls'),
    ),
    path(
        'api/',
        include('auth_app.api.urls'),
    ),
    path(
        'api/offers/',
        include('offers_app.api.urls'),
    ),
    path(
        'api/offerdetails/<int:pk>/',
        OfferDetailsView.as_view(),
        name='offerdetail-detail',
    ),
    path(
        'api/orders/',
        include('orders_app.api.urls'),
    ),
    path(
        'api/order-count/<int:business_user_id>/',
        OrderCountView.as_view(),
        name='order-count',
    ),
    path(
        'api/completed-order-count/<int:business_user_id>/',
        CompletedOrderCountView.as_view(),
        name='completed-order-count',
    ),
    path(
        'api/reviews/',
        include('reviews_app.api.urls'),
    ),
    path(
        'api/base-info/',
        include('api_app.api.urls'),
    ),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)
