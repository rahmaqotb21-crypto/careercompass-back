from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Career


class CareerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        careers = Career.objects.all()
        data = []
        for career in careers:
            resources = []
            for r in career.resources.all():
                resources.append({
                    'name': r.name,
                    'url': r.url,
                    'type': r.resource_type,
                })
            data.append({
                'id': career.id,
                'title': career.title,
                'description': career.description,
                'avg_salary_min': career.avg_salary_min,
                'avg_salary_max': career.avg_salary_max,
                'demand_level': career.demand_level,
                'required_skills': career.required_skills,
                'job_titles': career.job_titles,
                'learning_duration': career.learning_duration,
                'image_url': career.image_url,
                'resources': resources,
            })

        return Response({
            'success': True,
            'data': data
        })


class CareerDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, career_id):
        try:
            career = Career.objects.get(id=career_id)
        except Career.DoesNotExist:
            return Response({'success': False, 'error': 'Career not found'}, status=404)

        resources = []
        for r in career.resources.all():
            resources.append({
                'name': r.name,
                'url': r.url,
                'type': r.resource_type,
            })

        return Response({
            'success': True,
            'data': {
                'id': career.id,
                'title': career.title,
                'description': career.description,
                'avg_salary_min': career.avg_salary_min,
                'avg_salary_max': career.avg_salary_max,
                'demand_level': career.demand_level,
                'required_skills': career.required_skills,
                'job_titles': career.job_titles,
                'learning_duration': career.learning_duration,
                'image_url': career.image_url,
                'resources': resources,
            }
        })
