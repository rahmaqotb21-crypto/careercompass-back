from django.db import models


class Career(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    salary_range = models.CharField(max_length=50, blank=True, default='')
    growth = models.CharField(max_length=20, blank=True, default='')
    skills = models.JSONField(default=list)
    path = models.JSONField(default=list)
    countries = models.JSONField(default=list)
    avg_salary_min = models.IntegerField(null=True, blank=True)
    avg_salary_max = models.IntegerField(null=True, blank=True)
    demand_level = models.CharField(max_length=50, blank=True, default='')
    required_skills = models.JSONField(default=list)
    job_titles = models.JSONField(default=list)
    learning_duration = models.CharField(max_length=100, blank=True, default='')
    image_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class CareerResource(models.Model):
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='resources')
    name = models.CharField(max_length=200)
    url = models.URLField()
    resource_type = models.CharField(max_length=50)

    def __str__(self):
        return self.name
