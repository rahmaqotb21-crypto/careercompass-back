from django.db import models
from users.models import CustomUser
from chatbot.models import ChatSession


class SkillTest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_submitted = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)

    def __str__(self):
        return f"Test for {self.user.email} - Score: {self.score}"


class Question(models.Model):
    test = models.ForeignKey(SkillTest, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1)  # A, B, C, or D
    user_answer = models.CharField(max_length=1, null=True, blank=True)

    def __str__(self):
        return self.question_text[:50]