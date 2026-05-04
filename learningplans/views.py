from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from chatbot.models import ChatSession
from chatbot.plan_parser import parse_learning_plan


def parse_plan(raw_plan):
    if not raw_plan:
        return None

    return parse_learning_plan(raw_plan)


def serialize_session(session):
    parsed = parse_plan(session.learning_plan)

    return {
        'session_id': session.id,
        'created_at': session.created_at,
        'is_completed': session.is_completed,
        'structured_plan': parsed,
        'raw_plan': session.learning_plan if not parsed else None,
    }


class LearningPlanListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = (
            ChatSession.objects
            .filter(user=request.user)
            .exclude(learning_plan__isnull=True)
            .exclude(learning_plan='')
            .order_by('-created_at')
        )

        plans = [serialize_session(session) for session in sessions]

        return Response({'success': True, 'data': {'count': len(plans), 'plans': plans}})


class LearningPlanLatestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session = (
            ChatSession.objects
            .filter(user=request.user)
            .exclude(learning_plan__isnull=True)
            .exclude(learning_plan='')
            .order_by('-created_at')
            .first()
        )

        if not session:
            return Response({'success': False, 'error': 'No learning plan found'}, status=404)

        return Response({'success': True, 'data': {'plan': serialize_session(session)}})


class LearningPlanDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = (
            ChatSession.objects
            .filter(user=request.user, id=session_id)
            .exclude(learning_plan__isnull=True)
            .exclude(learning_plan='')
            .first()
        )

        if not session:
            return Response({'success': False, 'error': 'Learning plan not found'}, status=404)

        return Response({'success': True, 'data': {'plan': serialize_session(session)}})