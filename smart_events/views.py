from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event
from .serializers import EventSerializer
from collections import Counter
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

from datetime import datetime

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-date', 'time')
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date']

class EventWithBirthdaysAPIView(APIView):
    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'Date is required'}, status=400)

        try:
            date_obj = parse_date(date_str)
            if not date_obj:
                raise ValueError
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        # Получаем события по дате
        events = Event.objects.filter(date=date_obj).order_by('time')
        events_data = EventSerializer(events, many=True).data

        # Получаем список ID событий
        event_ids = [event['id'] for event in events_data]

        # Подсчёт комментариев и лайков к событиям
        comment_counts = Counter(Comment.objects.filter(event_id__in=event_ids).values_list('event_id', flat=True))
        like_counts = Counter(Like.objects.filter(event_id__in=event_ids).values_list('event_id', flat=True))

        for event in events_data:
            event['comments_count'] = comment_counts.get(event['id'], 0)
            event['likes_count'] = like_counts.get(event['id'], 0)

        # Сотрудники с ДР
        employees = Employee.objects.filter(
            birth_date__month=date_obj.month,
            birth_date__day=date_obj.day
        )

        birth_year = date_obj.year

        # Подсчёт комментов и лайков к ДР
        birthday_comment_counts = Counter(
            Comment.objects.filter(
                birthday_employee_id__in=employees.values_list('id', flat=True),
                birth_year=birth_year,
                event_id__isnull=True
            ).values_list('birthday_employee_id', flat=True)
        )

        birthday_like_counts = Counter(
            Like.objects.filter(
                birthday_employee_id__in=employees.values_list('id', flat=True),
                birth_year=birth_year,
                event_id__isnull=True
            ).values_list('birthday_employee_id', flat=True)
        )

        messages = list(BirthdayMessage.objects.all())
        messages_count = len(messages)

        employees_data = []
        for i, employee in enumerate(employees):
            # Пропускаем сотрудников без ID
            if not employee.id:
                continue

            emp_data = EmployeeSerializer(employee).data
            emp_data['birthday_comments_count'] = birthday_comment_counts.get(employee.id, 0)
            emp_data['birthday_likes_count'] = birthday_like_counts.get(employee.id, 0)

            try:
                message_used = BirthdayMessageUsed.objects.get(
                    birthday_employee_id=employee.id,
                    birth_year=birth_year
                )
            except BirthdayMessageUsed.DoesNotExist:
                message_used = None
                if messages_count > 0:
                    index = i % messages_count
                    message = messages[index]
                    message_used = BirthdayMessageUsed.objects.create(
                        birthday_employee_id=employee.id,
                        birth_year=birth_year,
                        message=message
                    )

            emp_data['birthday_message_ru'] = (
                message_used.message.text_ru if message_used else None
            )
            emp_data['birthday_message_kz'] = (
                message_used.message.text_kz if message_used else None
            )

            employees_data.append(emp_data)



        return Response({
            'events': events_data,
            'birthdays': employees_data
        })


def get_comments_by_event(request, event_id):
    comments = Comment.objects.filter(event_id=event_id).order_by('created_at')

    # Сначала делаем словарь комментариев по ID
    comment_map = {}
    for comment in comments:
        comment_map[comment.id] = comment

    # Словарь для хранения вложенности
    comment_tree = {}

    # Отдельный список для корневых комментариев
    root_comments = []

    for comment in comments:
        try:
            employee = Employee.objects.get(id=comment.employee_id)
            employee_data = {
                'id': employee.id,
                'full_name': f"{employee.user_surename} {employee.user_name} {employee.user_patronymic or ''}".strip(),
                'photo': request.build_absolute_uri(employee.user_image.url) if employee.user_image else None,
            }
        except Employee.DoesNotExist:
            employee_data = {
                'id': comment.employee_id,
                'full_name': None,
                'photo': None,
            }

        comment_data = {
            'id': comment.id,
            'event_id': comment.event_id,
            'employee': employee_data,
            'text': comment.text,
            'created_at': comment.created_at,
            'replies': []
        }

        if comment.comment_id:  # Это ответ
            parent = comment_tree.get(comment.comment_id)
            if parent:
                parent['replies'].append(comment_data)
            else:
                # если родитель ещё не добавлен, сохраняем временно
                comment_tree.setdefault(comment.comment_id, {'replies': []})['replies'].append(comment_data)
        else:
            root_comments.append(comment_data)
            comment_tree[comment.id] = comment_data

    return JsonResponse(root_comments, safe=False)

class EventDetailAPIView(APIView):
    def get(self, request, event_id):  # 👈 добавляем event_id сюда
        event = get_object_or_404(Event, id=event_id)
        event_data = EventSerializer(event).data

        # Подсчёт комментариев
        comments = Comment.objects.filter(event_id=event.id).order_by('-created_at')
        comment_counts = comments.count()

        # Подсчёт лайков
        like_counts = Like.objects.filter(event_id=event.id).count()

        # Список комментариев с данными сотрудников
        comments_data = []
        for comment in comments:
            try:
                employee = Employee.objects.get(id=comment.employee_id)
                employee_data = {
                    'id': employee.id,
                    'full_name': f"{employee.user_surename} {employee.user_name} {employee.user_patronymic or ''}".strip(),
                    'photo': request.build_absolute_uri(employee.user_image.url) if employee.user_image else None,
                }
            except Employee.DoesNotExist:
                employee_data = {
                    'id': comment.employee_id,
                    'full_name': None,
                    'photo': None,
                }

            comments_data.append({
                'id': comment.id,
                'event_id': comment.event_id,
                'employee': employee_data,
                'text': comment.text,
                'created_at': comment.created_at,
            })

        # Собираем итоговый ответ
        event_data.update({
            'comments_count': comment_counts,
            'likes_count': like_counts,
            'comments': comments_data,
        })

        return Response(event_data, status=200)

class LikeEventAPIView(APIView):
    def post(self, request):
        event_id = request.data.get("event_id")
        birthday_employee_id = request.data.get("birthday_employee_id")
        birth_year = request.data.get("birth_year")
        employee_id = request.data.get("employee_id")

        if not employee_id:
            return Response({"error": "Missing employee_id"}, status=400)

        if event_id:
            like_filter = {"event_id": event_id, "employee_id": employee_id}
        elif birthday_employee_id and birth_year:
            like_filter = {
                "birthday_employee_id": birthday_employee_id,
                "birth_year": birth_year,
                "employee_id": employee_id
            }
        else:
            return Response({"error": "Missing event_id or birthday data"}, status=400)

        try:
            like = Like.objects.get(**like_filter)
            like.delete()
            return Response({"message": "Unliked successfully"}, status=200)
        except Like.DoesNotExist:
            Like.objects.create(**like_filter)
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
        event_id = request.data.get("event_id")
        birthday_employee_id = request.data.get("birthday_employee_id")
        birth_year = request.data.get("birth_year")
        employee_id = request.data.get("employee_id")
        text = request.data.get("text")

        # Проверка обязательных полей
        if not employee_id or not text:
            return Response({"error": "Missing required fields"}, status=400)

        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        if event_id:
            # Комментарий к событию
            try:
                event = Event.objects.get(id=event_id)
            except Event.DoesNotExist:
                return Response({"error": "Event not found"}, status=404)

            comment = Comment.objects.create(
                event_id=event.id,
                employee_id=employee.id,
                text=text
            )

            return Response({
                "message": "Event comment added successfully",
                "comment": {
                    "id": comment.id,
                    "event_id": comment.event_id,
                    "employee_id": comment.employee_id,
                    "text": comment.text,
                    "created_at": comment.created_at,
                }
            }, status=201)

        elif birthday_employee_id and birth_year:
            # Комментарий ко дню рождения
            comment = Comment.objects.create(
                birthday_employee_id=birthday_employee_id,
                birth_year=birth_year,
                employee_id=employee.id,
                text=text
            )

            return Response({
                "message": "Birthday comment added successfully",
                "comment": {
                    "id": comment.id,
                    "birthday_employee_id": comment.birthday_employee_id,
                    "birth_year": comment.birth_year,
                    "employee_id": comment.employee_id,
                    "text": comment.text,
                    "created_at": comment.created_at,
                }
            }, status=201)

        else:
            return Response({
                "error": "You must provide either event_id or (birthday_employee_id and birth_year)"
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
            event_id__isnull=True
        ).order_by('created_at')

        # Создаём мапу по ID
        comment_map = {}
        comment_tree = {}
        root_comments = []

        for comment in comments:
            try:
                employee = Employee.objects.get(id=comment.employee_id)
                employee_data = {
                    'id': employee.id,
                    'full_name': f"{employee.user_surename} {employee.user_name} {employee.user_patronymic or ''}".strip(),
                    'photo': request.build_absolute_uri(employee.user_image.url) if employee.user_image else None,
                }
            except Employee.DoesNotExist:
                employee_data = {
                    'id': comment.employee_id,
                    'full_name': None,
                    'photo': None,
                }

            comment_data = {
                'id': comment.id,
                'birthday_employee_id': comment.birthday_employee_id,
                'birth_year': comment.birth_year,
                'employee': employee_data,
                'text': comment.text,
                'created_at': comment.created_at,
                'replies': []
            }

            comment_map[comment.id] = comment_data

            if comment.comment_id:
                # Это ответ на комментарий
                parent = comment_map.get(comment.comment_id)
                if parent:
                    parent['replies'].append(comment_data)
                else:
                    # Если родитель ещё не загружен, временно отложим
                    comment_tree.setdefault(comment.comment_id, {'replies': []})['replies'].append(comment_data)
            else:
                root_comments.append(comment_data)

        return Response(root_comments, status=200)

class AddBirthdayCommentAPIView(APIView):
    def post(self, request):
        birthday_employee_id = request.data.get("birthday_employee_id")
        birth_year = request.data.get("birth_year")
        employee_id = request.data.get("employee_id")
        text = request.data.get("text")

        if not birthday_employee_id or not birth_year or not employee_id or not text:
            return Response({"error": "Missing required fields"}, status=400)

        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        comment = Comment.objects.create(
            birthday_employee_id=birthday_employee_id,
            birth_year=birth_year,
            employee_id=employee.id,
            text=text
        )

        return Response({
            "message": "Birthday comment added successfully",
            "comment": {
                "id": comment.id,
                "birthday_employee_id": comment.birthday_employee_id,
                "birth_year": comment.birth_year,
                "employee_id": comment.employee_id,
                "text": comment.text,
                "created_at": comment.created_at,
            }
        }, status=status.HTTP_201_CREATED)

class ReplyToCommentAPIView(APIView):
    def post(self, request):
        comment_id = request.data.get("comment_id")
        text = request.data.get("text")
        employee_id = request.data.get("employee_id")
        event_id = request.data.get("event_id")
        birthday_employee_id = request.data.get("birthday_employee_id")
        birth_year = request.data.get("birth_year")

        if not comment_id or not employee_id or not text:
            return Response({"error": "Missing required fields"}, status=400)

        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        # Создание ответа на комментарий
        comment = Comment.objects.create(
            comment_id=comment_id,
            employee_id=employee.id,
            text=text,
            event_id=event_id if event_id else None,
            birthday_employee_id=birthday_employee_id if birthday_employee_id else None,
            birth_year=birth_year if birth_year else None,
        )

        return Response({
            "message": "Reply added successfully",
            "reply": {
                "id": comment.id,
                "comment_id": comment.comment_id,
                "employee_id": comment.employee_id,
                "event_id": comment.event_id,
                "birthday_employee_id": comment.birthday_employee_id,
                "birth_year": comment.birth_year,
                "text": comment.text,
                "created_at": comment.created_at,
            }
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

        # Проверяем, есть ли уже назначенная цитата на эту дату
        try:
            used = QuoteMessageUsed.objects.get(employee_id=employee_id, date_used=current_date)
        except QuoteMessageUsed.DoesNotExist:
            used = None

        if not used:
            all_quotes = list(QuoteMessage.objects.all())
            if not all_quotes:
                return Response({'error': 'No quotes available'}, status=status.HTTP_404_NOT_FOUND)

            # Проверяем, какие цитаты уже использованы другими в этот день
            used_ids_today = set(
                QuoteMessageUsed.objects.filter(date_used=current_date)
                .values_list('message_id', flat=True)
            )
            available_quotes = [q for q in all_quotes if q.id not in used_ids_today]

            # Если все использованы — применим fallback: выдать по индексу
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