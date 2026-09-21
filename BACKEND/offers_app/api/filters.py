from django.db.models import F, Min, Q
from rest_framework.exceptions import ValidationError


def order_by_min_price(offers, descending=False):
    """Order offers by their lowest detail price."""

    offers = offers.annotate(
        ordering_min_price=Min('details__price'),
    )

    if descending:
        return offers.order_by('-ordering_min_price')

    return offers.order_by(
        F('ordering_min_price').asc(nulls_last=True),
    )


def order_offers(request, offers):
    """Apply the requested ordering to the offer queryset."""

    ordering = request.query_params.get('ordering')

    if ordering == 'min_price':
        return order_by_min_price(offers)

    if ordering == '-min_price':
        return order_by_min_price(
            offers,
            descending=True,
        )

    if ordering in ['updated_at', '-updated_at']:
        return offers.order_by(ordering)

    if ordering is not None:
        raise ValidationError(
            {'detail': 'Invalid ordering field.'},
        )

    return offers.order_by('-created_at')


def filter_by_creator(request, offers):
    """Filter offers by their creator ID."""

    creator_id = request.query_params.get('creator_id')

    if not creator_id:
        return offers

    try:
        creator_id = int(creator_id)
    except ValueError:
        raise ValidationError(
            {'detail': 'Invalid creator_id.'},
        )

    return offers.filter(user_id=creator_id)


def get_max_delivery_time(request):
    """Read and validate the maximum delivery parameter."""

    max_delivery_time = request.query_params.get('max_delivery_time')

    if not max_delivery_time:
        return None

    try:
        return int(max_delivery_time)
    except ValueError:
        raise ValidationError(
            {'detail': 'Invalid max_delivery_time.'},
        )


def filter_by_delivery_time(request, offers):
    """Filter offers by their maximum delivery time."""

    max_delivery_time = get_max_delivery_time(request)

    if max_delivery_time is None:
        return offers

    return offers.filter(
        details__delivery_time_in_days__lte=max_delivery_time,
    )


def get_min_price(request):
    """Read and validate the minimum price parameter."""

    min_price = request.query_params.get('min_price')

    if not min_price:
        return None

    try:
        return float(min_price)
    except ValueError:
        raise ValidationError(
            {'detail': 'Invalid min_price'},
        )


def filter_by_min_price(request, offers):
    """Filter offers by their minimum detail price."""

    min_price = get_min_price(request)

    if min_price is None:
        return offers

    return offers.filter(
        details__price__gte=min_price,
    )


def filter_by_search(request, offers):
    """Filter offers by title or description."""

    search = request.query_params.get('search')

    if not search:
        return offers

    return offers.filter(
        Q(title__icontains=search)
        | Q(description__icontains=search),
    ).distinct()


def filter_offers(request, offers):
    """Apply ordering and all supported offer filters."""

    offers = order_offers(request, offers)
    offers = filter_by_creator(request, offers)
    offers = filter_by_delivery_time(request, offers)
    offers = filter_by_min_price(request, offers)
    offers = filter_by_search(request, offers)

    return offers