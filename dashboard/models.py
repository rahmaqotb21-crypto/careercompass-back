from django.db import models


class SkillRequirement(models.Model):
    skill = models.CharField(max_length=80, unique=True)
    target_score = models.PositiveSmallIntegerField(default=70)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['skill']

    def __str__(self):
        return f'{self.skill} ({self.target_score}%)'


class RecommendedCourse(models.Model):
    skill = models.CharField(max_length=80)
    platform = models.CharField(max_length=80)
    duration = models.CharField(max_length=60, blank=True)
    title = models.CharField(max_length=220)
    tags = models.JSONField(default=list)
    rating = models.CharField(max_length=10, blank=True)
    url = models.URLField(max_length=500)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'id']
        unique_together = ('skill', 'title')

    def __str__(self):
        return f'{self.skill}: {self.title}'