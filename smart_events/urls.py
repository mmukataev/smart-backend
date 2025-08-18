from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, EventWithBirthdaysAPIView, ReplyToCommentAPIView, get_comments_by_event, LikeEventAPIView, CheckLikeAPIView, EventDetailAPIView, AddCommentAPIView, BirthdayCommentsAPIView, AddBirthdayCommentAPIView, GetDailyQuoteAPIView

router = DefaultRouter()
router.register(r'events', EventViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('with-birthdays/', EventWithBirthdaysAPIView.as_view(), name='events-with-birthdays'),
    path('detail/<int:event_id>/', EventDetailAPIView.as_view(), name='event-detail'),
    path('comments/<int:event_id>/', get_comments_by_event, name='event-comments'),
    path('birthday-comments/', BirthdayCommentsAPIView.as_view(), name='birthday-comments'),
    path('birthday-comments/add/', AddBirthdayCommentAPIView.as_view(), name='add-birthday-comments'),
    path("comment/reply", ReplyToCommentAPIView.as_view(), name="reply-to-comment"),
    path('comment/add/', AddCommentAPIView.as_view(), name='add-event-comment'),
    path('like/', LikeEventAPIView.as_view(), name='event-like'),
    path('liked/', CheckLikeAPIView.as_view(), name='has-liked'),
    path('quote/', GetDailyQuoteAPIView.as_view(), name='get_daily_quote'),
]
