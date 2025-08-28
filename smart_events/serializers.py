from collections import Counter

from rest_framework import serializers
from smart_apa_api.models import Employee, Region
from .models import Event, Comment, Like, BirthdayMessage, BirthdayMessageUsed, QuoteMessageUsed

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['type', 'date', 'time', 'title', 'title_kz', 'description', 'description_kz', 'image']


class EventUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['type', 'date', 'time', 'title', 'title_kz', 'description', 'description_kz']

class BirthdayMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BirthdayMessage
        fields = ['id', 'text_ru', 'text_kz', 'created_at']

class EventWithStatsSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_comments_count(self, obj):
        return self.context['comments_count'].get(obj.id, 0)

    def get_likes_count(self, obj):
        return self.context['likes_count'].get(obj.id, 0)


class EmployeeWithBirthdaySerializer(serializers.ModelSerializer):
    birthday_comments_count = serializers.SerializerMethodField()
    birthday_likes_count = serializers.SerializerMethodField()
    birthday_message_ru = serializers.SerializerMethodField()
    birthday_message_kz = serializers.SerializerMethodField()
    position_ru = serializers.SerializerMethodField() 
    position_kz = serializers.SerializerMethodField() 
    department_ru = serializers.SerializerMethodField() 
    department_kz = serializers.SerializerMethodField()
    region_ru = serializers.SerializerMethodField()
    region_kz = serializers.SerializerMethodField()
    

    class Meta:
        model = Employee
        fields = '__all__'  # или только нужные + birthday_* поля

    def get_birthday_comments_count(self, obj):
        return self.context['birthday_comment_counts'].get(obj.id, 0)

    def get_birthday_likes_count(self, obj):
        return self.context['birthday_like_counts'].get(obj.id, 0)

    def get_birthday_message_ru(self, obj):
        message_used = self.context['birthday_messages_map'].get(obj.id)
        return message_used.message.text_ru if message_used else None

    def get_birthday_message_kz(self, obj):
        message_used = self.context['birthday_messages_map'].get(obj.id)
        return message_used.message.text_kz if message_used else None

    def get_position_ru(self, obj):
        return obj.position.ru if obj.position else None
    
    def get_position_kz(self, obj):
        return obj.position.kz if obj.position else None

    def get_department_ru(self, obj):
        return obj.department.ru if obj.department else None

    def get_department_kz(self, obj):
        return obj.department.kz if obj.department else None

    def get_region_ru(self, obj):
        if obj.region_id:
            region = Region.objects.filter(id=obj.region_id).first()
            return region.ru if region else None
        return None

    def get_region_kz(self, obj):
        if obj.region_id:
            region = Region.objects.filter(id=obj.region_id).first()
            return region.kz if region else None
        return None



class EventWithBirthdaysSerializer(serializers.Serializer):
    events = serializers.SerializerMethodField()
    birthdays = serializers.SerializerMethodField()

    def get_events(self, obj):
        date_obj = self.context['date']
        events = Event.objects.filter(date=date_obj).order_by('time')
        event_ids = events.values_list('id', flat=True)

        # Подсчёт комментариев и лайков
        comment_counts = Counter(Comment.objects.filter(event_id__in=event_ids)
                                 .values_list('event_id', flat=True))
        like_counts = Counter(Like.objects.filter(event_id__in=event_ids)
                              .values_list('event_id', flat=True))

        return EventWithStatsSerializer(
            events, many=True,
            context={**self.context,
                     'comments_count': comment_counts,
                     'likes_count': like_counts}
        ).data

    def get_birthdays(self, obj):
        date_obj = self.context['date']
        birth_year = date_obj.year

        employees = Employee.objects.filter(
            birth_date__month=date_obj.month,
            birth_date__day=date_obj.day
        )

        # Подсчёт комментов и лайков на ДР
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

        # Сообщения на ДР
        messages = list(BirthdayMessage.objects.all())
        messages_count = len(messages)
        birthday_messages_map = {}

        for i, emp in enumerate(employees):
            try:
                message_used = BirthdayMessageUsed.objects.get(
                    birthday_employee_id=emp.id,
                    birth_year=birth_year
                )
            except BirthdayMessageUsed.DoesNotExist:
                message_used = None
                if messages_count > 0:
                    index = i % messages_count
                    msg = messages[index]
                    message_used = BirthdayMessageUsed.objects.create(
                        birthday_employee_id=emp.id,
                        birth_year=birth_year,
                        message=msg
                    )
            birthday_messages_map[emp.id] = message_used

        return EmployeeWithBirthdaySerializer(
            employees, many=True,
            context={**self.context,
                     'birthday_comment_counts': birthday_comment_counts,
                     'birthday_like_counts': birthday_like_counts,
                     'birthday_messages_map': birthday_messages_map}
        ).data

class EmployeeShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'photo']

    def get_full_name(self, obj):
        return f"{obj.user_surename} {obj.user_name} {obj.user_patronymic or ''}".strip()

    def get_photo(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.user_image.url) if obj.user_image and request else None

class CommentSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'event_id', 'employee', 'text', 'created_at', 'replies']

    def get_employee(self, obj):
        try:
            employee = Employee.objects.get(id=obj.employee_id)
            return EmployeeShortSerializer(employee, context=self.context).data
        except Employee.DoesNotExist:
            return {
                'id': obj.employee_id,
                'full_name': None,
                'photo': None,
            }

    def get_replies(self, obj):
        replies_map = self.context.get('replies_map', {})
        child_comments = replies_map.get(obj.id, [])
        return CommentSerializer(child_comments, many=True, context=self.context).data
class LikeSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=False, allow_null=True)
    birthday_employee_id = serializers.IntegerField(required=False, allow_null=True)
    birth_year = serializers.IntegerField(required=False, allow_null=True)
    employee_id = serializers.IntegerField(required=True)

    def validate(self, data):
        if not data.get('event_id') and not (data.get('birthday_employee_id') and data.get('birth_year')):
            raise serializers.ValidationError(
                "Должен быть указан либо event_id, либо birthday_employee_id вместе с birth_year."
            )
        return data


class AddCommentSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField(required=False, allow_null=True)
    birthday_employee_id = serializers.IntegerField(required=False, allow_null=True)
    birth_year = serializers.IntegerField(required=False, allow_null=True)
    employee_id = serializers.IntegerField(required=True)
    comment_id = serializers.IntegerField(required=False, allow_null=True)
    text = serializers.CharField(required=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'employee_id', 'event_id', 'birthday_employee_id', 'birth_year', 'comment_id', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        return Comment.objects.create(**validated_data)



class CommentSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {
            'employee': {'required': False, 'allow_null': True},
            'event': {'required': False, 'allow_null': True},
            'birthday_employee': {'required': False, 'allow_null': True},
            'birth_year': {'required': False, 'allow_null': True},
            'comment': {'required': False, 'allow_null': True},  # родительский коммент
        }

    def get_employee(self, obj):
        try:
            employee = Employee.objects.get(id=obj.employee_id)
            return EmployeeShortSerializer(employee, context=self.context).data
        except Employee.DoesNotExist:
            return {
                'id': obj.employee_id,
                'full_name': None,
                'photo': None,
            }

    def get_replies(self, obj):
        # Получаем только прямые ответы (1 уровень)
        replies = Comment.objects.filter(comment_id=obj.id).order_by('created_at')
        return CommentSerializer(replies, many=True, context=self.context).data