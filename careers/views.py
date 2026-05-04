from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Career


def serialize_career(career):
    return {
        'id': career.id,
        'title': career.title,
        'description': career.description,
        'salary_range': career.salary_range,
        'growth': career.growth,
        'required_skills': career.skills or [],
        'skills': career.skills or [],
        'path': career.path or [],
        'countries': career.countries or [],
    }


class CareerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        careers = Career.objects.filter(is_active=True)
        data = []
        for career in careers:
            data.append({
                'id': career.id,
                'title': career.title,
                'description': career.description,
                'salary_range': career.salary_range,
                'growth': career.growth,
                'required_skills': career.skills or [],
                'skills': career.skills or [],
                'path': career.path or [],
                'countries': career.countries or [],
                'avg_salary_min': career.avg_salary_min,
                'avg_salary_max': career.avg_salary_max,
                'demand_level': career.demand_level,
                'job_titles': career.job_titles,
                'learning_duration': career.learning_duration,
                'image_url': career.image_url,
            })

        return Response({
            'success': True,
            'data': {
                'careers': data,
                'count': len(data),
                'results_count': len(data),
            }
        })


class CareerDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, career_id):
        try:
            career = Career.objects.get(id=career_id, is_active=True)
        except Career.DoesNotExist:
            return Response({'success': False, 'error': 'Career not found'}, status=404)

        return Response({
            'success': True,
            'data': {
                'career': {
                    'id': career.id,
                    'title': career.title,
                    'description': career.description,
                    'salary_range': career.salary_range,
                    'growth': career.growth,
                    'required_skills': career.skills or [],
                    'skills': career.skills or [],
                    'path': career.path or [],
                    'countries': career.countries or [],
                    'avg_salary_min': career.avg_salary_min,
                    'avg_salary_max': career.avg_salary_max,
                    'demand_level': career.demand_level,
                    'job_titles': career.job_titles,
                    'learning_duration': career.learning_duration,
                    'image_url': career.image_url,
                }
            }
        })


class RelatedCareersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, career_id):
        try:
            career = Career.objects.get(id=career_id, is_active=True)
        except Career.DoesNotExist:
            return Response({'success': False, 'error': 'Career not found'}, status=404)

        career_skills = set(career.skills or [])
        related = []
        for c in Career.objects.filter(is_active=True).exclude(id=career_id):
            c_skills = set(c.skills or [])
            shared = career_skills & c_skills
            if shared:
                related.append({
                    **serialize_career(c),
                    'shared_skills': list(shared),
                    'match_score': len(shared),
                })

        related.sort(key=lambda x: x['match_score'], reverse=True)
        related = related[:3]

        return Response({
            'success': True,
            'data': {
                'careers': related
            }
        })
