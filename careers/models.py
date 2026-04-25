from django.db import models


class Career(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    avg_salary_min = models.IntegerField()
    avg_salary_max = models.IntegerField()
    demand_level = models.CharField(max_length=50)
    required_skills = models.JSONField(default=list)
    job_titles = models.JSONField(default=list)
    learning_duration = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title


class CareerResource(models.Model):
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='resources')
    name = models.CharField(max_length=200)
    url = models.URLField()
    resource_type = models.CharField(max_length=50)

    def __str__(self):
        return self.name
