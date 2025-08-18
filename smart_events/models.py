from django.db import models
from smart_apa_api.models import Employee

class Event(models.Model):
    ACADEMY_EVENTS = 'academy_events'
    NEWS = 'news'

    EVENT_TYPE_CHOICES = [
        (ACADEMY_EVENTS, 'Academy Events'),
        (NEWS, 'News'),
    ]

    type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default=ACADEMY_EVENTS,
    )
    date = models.DateField()
    time = models.TimeField()
    title = models.CharField(max_length=255)
    description = models.TextField()

    image = models.ImageField(upload_to='events/', blank=True, null=True) 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_type_display()}) on {self.date}"

class Comment(models.Model):
    event_id = models.IntegerField(null=True, blank=True)
    
    employee_id = models.IntegerField()

    birth_year = models.IntegerField(null=True, blank=True)
    birthday_employee_id = models.IntegerField(null=True, blank=True)
    comment_id = models.IntegerField(null=True, blank=True)

    
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_comment'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f"Comment by Employee #{self.employee_id} on Event #{self.event_id}"

class Like(models.Model):
    event_id = models.IntegerField(null=True, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)
    birthday_employee_id = models.IntegerField(null=True, blank=True)
    employee_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_like'
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
        # Обновляем unique_together
        constraints = [
            models.UniqueConstraint(
                fields=['event_id', 'employee_id'],
                name='unique_event_like',
                condition=models.Q(event_id__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['birthday_employee_id', 'birth_year', 'employee_id'],
                name='unique_birthday_like',
                condition=models.Q(birthday_employee_id__isnull=False, birth_year__isnull=False)
            ),
        ]

    def __str__(self):
        if self.event_id:
            return f"Like by Employee #{self.employee_id} on Event #{self.event_id}"
        else:
            return f"Like by Employee #{self.employee_id} on Birthday #{self.birthday_employee_id} ({self.birth_year})"

class BirthdayMessage(models.Model):
    text_ru = models.TextField("Текст на русском")
    text_kz = models.TextField("Мәтін қазақша")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'birthday_message'
        verbose_name = 'Birthday Message'
        verbose_name_plural = 'Birthday Messages'

    def __str__(self):
        return f"Поздравление RU: {self.text_ru[:30]}... | KZ: {self.text_kz[:30]}..."

class BirthdayMessageUsed(models.Model):
    birthday_employee_id = models.IntegerField()
    birth_year = models.IntegerField()
    message = models.ForeignKey(BirthdayMessage, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'birthday_message_used'
        verbose_name = 'Used Birthday Message'
        verbose_name_plural = 'Used Birthday Messages'
        constraints = [
            models.UniqueConstraint(
                fields=['birthday_employee_id', 'birth_year'],
                name='unique_birthday_message_per_year'
            )
        ]

    def __str__(self):
        return f"Message #{self.message_id} for Employee #{self.birthday_employee_id} ({self.birth_year})"

class QuoteMessage(models.Model):
    text_ru = models.TextField()
    text_kz = models.TextField()

    class Meta:
        verbose_name = "Цитата"
        verbose_name_plural = "Цитаты"

    def __str__(self):
        return self.text_ru[:50]


class QuoteMessageUsed(models.Model):
    employee_id = models.IntegerField()
    date_used = models.DateField()
    message = models.ForeignKey(QuoteMessage, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quote_message_used'
        verbose_name = 'Used Quote Message'
        verbose_name_plural = 'Used Quote Messages'
        constraints = [
            models.UniqueConstraint(
                fields=['employee_id', 'date_used'],
                name='unique_quote_per_employee_per_day'
            )
        ]

    def __str__(self):
        return f"Quote #{self.message_id} for Employee #{self.employee_id} ({self.date_used})"