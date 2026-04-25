import json
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chatbot.models import ChatSession
from skill_test.models import SkillTest


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # جيب آخر session مكتمل
        session = ChatSession.objects.filter(
            user=user, is_completed=True
        ).order_by('-created_at').first()

        if not session:
            return Response({
                'success': False,
                'error': 'No completed learning plan found'
            }, status=404)

        learning_plan = json.loads(session.learning_plan)

        # جيب كل التيستات
        tests = SkillTest.objects.filter(
            user=user, is_submitted=True
        ).order_by('-created_at')

        test_history = []
        scores = []
        for test in tests:
            test_history.append({
                'test_id': test.id,
                'score': test.score,
                'correct_answers': test.correct_answers,
                'total_questions': test.total_questions,
                'date': test.created_at.strftime('%Y-%m-%d'),
            })
            if test.score is not None:
                scores.append(test.score)

        latest_score = scores[0] if scores else None
        overall_progress = round(sum(scores) / len(scores), 2) if scores else 0
        total_tests = len(test_history)

        return Response({
            'success': True,
            'data': {
                'user': {
                    'name': user.username,
                    'email': user.email,
                },
                'learning_plan': learning_plan,
                'test_stats': {
                    'latest_score': latest_score,
                    'overall_progress': overall_progress,
                    'total_tests': total_tests,
                    'test_history': test_history,
                }
            }
        })

# Create your views here.
