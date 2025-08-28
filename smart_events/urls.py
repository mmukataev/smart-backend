from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, EventCreateAPIView, BirthdaysInMonthAPIView, EventUpdateAPIView, EventWithBirthdaysAPIView, BirthdayMessagesListAPIView, UpdateBirthdayMessageUsedAPIView, ReplyToCommentAPIView, get_comments_by_event, LikeEventAPIView, CheckLikeAPIView, EventDetailAPIView, AddCommentAPIView, BirthdayCommentsAPIView, GetDailyQuoteAPIView

router = DefaultRouter()
router.register(r'events', EventViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create/', EventCreateAPIView.as_view(), name='create-event'),
    path('edit/<int:pk>/update/', EventUpdateAPIView.as_view(), name='event-update'),
    path('with-birthdays/', EventWithBirthdaysAPIView.as_view(), name='events-with-birthdays'),
    path('birthdays-in-month/', BirthdaysInMonthAPIView.as_view(), name='birthdays-in-month'),
    path('detail/<int:event_id>/', EventDetailAPIView.as_view(), name='event-detail'),
    path('comments/<int:event_id>/', get_comments_by_event, name='event-comments'),
    path('birthday-comments/', BirthdayCommentsAPIView.as_view(), name='birthday-comments'),
    path('birthday-message/all/', BirthdayMessagesListAPIView.as_view(), name='birthday-comments'),
    path('birthday-message/update/', UpdateBirthdayMessageUsedAPIView.as_view(), name='update-birthday-message'),
    path("comment/reply", ReplyToCommentAPIView.as_view(), name="reply-to-comment"),
    path('comment/add/', AddCommentAPIView.as_view(), name='add-event-comment'),
    path('like/', LikeEventAPIView.as_view(), name='event-like'),
    path('liked/', CheckLikeAPIView.as_view(), name='has-liked'),
    path('quote/', GetDailyQuoteAPIView.as_view(), name='get_daily_quote'),
]
