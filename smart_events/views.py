from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event
from .serializers import EventSerializer
from collections import Counter
from collections import defaultdict
from django.http import JsonResponse

from django.db.models import Count
import random

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from datetime import date
from django.utils.timezone import now

from django.utils.dateparse import parse_date
from django.shortcuts import get_list_or_404, get_object_or_404

from smart_events.models import Event, Comment, Like, BirthdayMessage, BirthdayMessageUsed, QuoteMessage, QuoteMessageUsed
from smart_apa_api.models import Employee
from .serializers import EventSerializer
from smart_apa_api.serializers import EmployeeSerializer
from smart_events.serializers import EventWithStatsSerializer, LikeSerializer, BirthdayMessageSerializer, EventCreateSerializer, EventUpdateSerializer, EmployeeWithBirthdaySerializer, EventWithBirthdaysSerializer, EmployeeShortSerializer, CommentSerializer, AddCommentSerializer, CommentSerializer

from datetime import datetime

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-date', 'time')
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date']

class EventCreateAPIView(APIView):
    def post(self, request):
        serializer = EventCreateSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()
            return Response({
                "message": "Event created successfully",
                "event": EventCreateSerializer(event).data
            }, status=status.HTTP_201_CREATED)

        # Собираем безопасный словарь для JSON
        data_received_safe = dict(request.data)
        if 'image' in data_received_safe:
            data_received_safe['image'] = str(data_received_safe['image'])

        return Response({
            "message": "Validation failed",
            "errors": serializer.errors,
            "data_received": data_received_safe
        }, status=status.HTTP_400_BAD_REQUEST)

class EventUpdateAPIView(APIView):
    def put(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"message": "Событие не найдено"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EventUpdateSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventWithBirthdaysAPIView(APIView):
    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'Date is required'}, status=400)

        date_obj = parse_date(date_str)
        if not date_obj:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        serializer = EventWithBirthdaysSerializer(
            {'date': date_obj}, 
            context={'date': date_obj}
        )
        return Response(serializer.data)

def get_comments_by_event(request, event_id):
    comments = list(Comment.objects.filter(event_id=event_id).order_by('created_at'))

    # Группируем ответы по comment_id
    replies_map = defaultdict(list)
    root_comments = []
    for c in comments:
        if c.comment_id:
            replies_map[c.comment_id].append(c)
        else:
            root_comments.append(c)

    serializer = CommentSerializer(
        root_comments, many=True,
        context={'request': request, 'replies_map': replies_map}
    )
    return JsonResponse(serializer.data, safe=False)

class BirthdaysInMonthAPIView(APIView):
    """
    Возвращает сотрудников с днями рождения в месяце указанной даты.
    """
    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'Date is required'}, status=400)

        date_obj = parse_date(date_str)
        if not date_obj:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        month = date_obj.month
        year = date_obj.year

        employees = Employee.objects.filter(birth_date__month=month)
        # Группируем по дню месяца
        birthdays_map = defaultdict(list)
        for emp in employees:
            day = emp.birth_date.day
            birthdays_map[day].append({
                "id": emp.id,
                "full_name": f"{emp.first_name} {emp.last_name}",
                "birth_date": emp.birth_date,
            })

        # Преобразуем в список с сортировкой по дню
        result = [{"day": day, "employees": birthdays_map[day]} for day in sorted(birthdays_map)]

        return Response({
            "month": month,
            "year": year,
            "birthdays": result
        })

class EventDetailAPIView(APIView):
    def get(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        event_data = EventSerializer(event, context={'request': request}).data

        # Подсчёт комментариев и лайков
        comments = Comment.objects.filter(event_id=event.id).order_by('created_at')
        comment_counts = comments.count()
        like_counts = Like.objects.filter(event_id=event.id).count()

        replies_map = defaultdict(list)
        root_comments = []

        for comment in comments:
            if comment.comment_id:
                replies_map[comment.comment_id].append(comment)
            else:
                root_comments.append(comment)

        comments_data = CommentSerializer(
            root_comments,
            many=True,
            context={'request': request, 'replies_map': replies_map}
        ).data

        # Формируем итоговый ответ
        event_data.update({
            'comments_count': comment_counts,
            'likes_count': like_counts,
            'comments': comments_data,
        })

        return Response(event_data, status=200)

class LikeEventAPIView(APIView):
    def post(self, request):
        print("=== LIKE EVENT API CALLED ===")
        print("Request data:", request.data)
        print("Request user:", request.user)
        
        serializer = LikeSerializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)  # <-- добавь это
            return Response(serializer.errors, status=400)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if data.get("event_id"):
            like_filter = {"event_id": data["event_id"], "employee_id": data["employee_id"]}
        else:
            like_filter = {
                "birthday_employee_id": data["birthday_employee_id"],
                "birth_year": data["birth_year"],
                "employee_id": data["employee_id"]
            }

        try:
            like = Like.objects.get(**like_filter)
            like.delete()
            print("=== UNLIKED ===", like_filter)
            return Response({"message": "Unliked successfully"}, status=200)
        except Like.DoesNotExist:
            Like.objects.create(**like_filter)
            print("=== LIKED ===", like_filter)
            return Response({"message": "Liked successfully"}, status=201)


class CheckLikeAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        event_id = request.query_params.get("event_id")
        birthday_employee_id = request.query_params.get("birthday_employee_id")
        birth_year = request.query_params.get("birth_year")
        employee_id = request.query_params.get("employee_id")

        if not employee_id:
            return Response({"error": "Missing employee_id"}, status=400)

        if event_id:
            liked = Like.objects.filter(event_id=event_id, employee_id=employee_id).exists()
        elif birthday_employee_id and birth_year:
            liked = Like.objects.filter(
                birthday_employee_id=birthday_employee_id,
                birth_year=birth_year,
                employee_id=employee_id
            ).exists()
        else:
            return Response({"error": "Missing event_id or birthday data"}, status=400)

        return Response({"liked": liked}, status=200)


class AddCommentAPIView(APIView):
    def post(self, request):
        serializer = AddCommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save()
            return Response({
                "message": "Comment added successfully",
                "comment": AddCommentSerializer(comment).data
            }, status=201)
        else:
            # Возвращаем подробности при ошибке
            return Response({
                "message": "Validation failed",
                "errors": serializer.errors,
                "data_received": request.data
            }, status=400)


class BirthdayCommentsAPIView(APIView):
    def get(self, request):
        birthday_employee_id = request.query_params.get('birthday_employee_id')
        birth_year = request.query_params.get('birth_year')

        if not birthday_employee_id or not birth_year:
            return Response({"error": "Missing birthday_employee_id or birth_year"}, status=400)

        comments = Comment.objects.filter(
            birthday_employee_id=birthday_employee_id,
            birth_year=birth_year,
            event_id__isnull=True,
            comment_id__isnull=True  # только корневые
        ).order_by('created_at')

        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data, status=200)

class UpdateBirthdayMessageUsedAPIView(APIView):
    def put(self, request):
        employee_id = request.data.get('birthday_employee_id')
        birth_year = request.data.get('birth_year')
        new_message_id = request.data.get('message_id')

        if not all([employee_id, birth_year, new_message_id]):
            return Response({"message": "Необходимо указать birthday_employee_id, birth_year и message_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем существует ли сообщение
        new_message = get_object_or_404(BirthdayMessage, id=new_message_id)

        # Получаем или создаем запись
        obj, created = BirthdayMessageUsed.objects.update_or_create(
            birthday_employee_id=employee_id,
            birth_year=birth_year,
            defaults={'message': new_message}
        )

        return Response({
            "message": "Сообщение успешно обновлено" if not created else "Сообщение создано",
            "birthday_employee_id": obj.birthday_employee_id,
            "birth_year": obj.birth_year,
            "message_id": obj.message.id,
            "text_ru": obj.message.text_ru,
            "text_kz": obj.message.text_kz
        })

class BirthdayMessagesListAPIView(APIView):
    def get(self, request):
        messages = BirthdayMessage.objects.all().order_by('created_at')
        serializer = BirthdayMessageSerializer(messages, many=True)
        return Response(serializer.data)

class ReplyToCommentAPIView(APIView):
    def post(self, request):
        serializer = AddCommentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "message": "Validation failed",
                "errors": serializer.errors,
                "data_received": request.data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        employee_id = serializer.validated_data.get("employee_id")
        try:
            Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        
        comment = serializer.save()
        
        return Response({
            "message": "Reply added successfully",
            "reply": AddCommentSerializer(comment).data
        }, status=status.HTTP_201_CREATED)

class GetDailyQuoteAPIView(APIView):
    def post(self, request):
        employee_id = request.data.get('employee_id')
        date_str = request.data.get('date')

        if not employee_id:
            return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee_id = int(employee_id)
        except ValueError:
            return Response({'error': 'Invalid employee_id'}, status=status.HTTP_400_BAD_REQUEST)

        current_date = date.fromisoformat(date_str) if date_str else now().date()

        try:
            used = QuoteMessageUsed.objects.get(employee_id=employee_id, date_used=current_date)
        except QuoteMessageUsed.DoesNotExist:
            used = None

        if not used:
            all_quotes = list(QuoteMessage.objects.all())
            if not all_quotes:
                return Response({'error': 'No quotes available'}, status=status.HTTP_404_NOT_FOUND)

            used_ids_today = set(
                QuoteMessageUsed.objects.filter(date_used=current_date)
                .values_list('message_id', flat=True)
            )
            available_quotes = [q for q in all_quotes if q.id not in used_ids_today]

            if not available_quotes:
                index = employee_id % len(all_quotes)
                selected = all_quotes[index]
            else:
                selected = random.choice(available_quotes)

            try:
                print("Creating new quote usage for:", employee_id, current_date, selected.id)
                used = QuoteMessageUsed.objects.create(
                    employee_id=employee_id,
                    date_used=current_date,
                    message=selected
                )
                print("Successfully created:", used.id)
            except Exception as e:
                return Response({'error': f'Failed to assign quote: {str(e)}'}, status=500)

        return Response({
            'quote_ru': used.message.text_ru,
            'quote_kz': used.message.text_kz,
        }, status=status.HTTP_200_OK)