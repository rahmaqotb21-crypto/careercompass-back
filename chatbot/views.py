import json
import re
import traceback

from groq import Groq
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ChatSession, ChatMessage

SYSTEM_PROMPT = """You are CareerCompass AI, a career coach. Collect these 7 things one by one:
1. Career goal
2. Current skills & experience
3. Education
4. CV summary
5. LinkedIn/GitHub
6. Weekly learning hours
7. Learning style (videos/reading/projects)

After all 7, output ONLY valid JSON like this example:
{"career_path":"Frontend Developer","level":"Beginner","total_duration":"6 months","skills":["HTML","CSS","JavaScript"],"phases":[{"phase":1,"title":"Foundations","duration":"2 months","topics":["HTML basics"],"resources":["FreeCodeCamp"]},{"phase":2,"title":"Advanced","duration":"4 months","topics":["React"],"resources":["React docs"]}],"message":"Your personalized test will be generated based on this plan"}

IMPORTANT: Output ONLY the JSON with no extra text. Make sure the JSON is valid and complete."""


class ChatbotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get('message')
        session_id = request.data.get('session_id')

        if not user_message:
            return Response({'success': False, 'error': 'Message is required'}, status=400)

        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                return Response({'success': False, 'error': 'Session not found'}, status=404)
        else:
            session = ChatSession.objects.create(user=request.user)

        ChatMessage.objects.create(session=session, role='user', content=user_message)

        messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        history = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in messages:
            role = "user" if msg.role == "user" else "assistant"
            history.append({"role": role, "content": msg.content})

        try:
            client = Groq(api_key=settings.GROQ_API_KEY)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=history,
                max_tokens=1500,
            )
            ai_message = response.choices[0].message.content

            ChatMessage.objects.create(session=session, role='assistant', content=ai_message)

            try:
                json_match = re.search(r'\{.*\}', ai_message, re.DOTALL)
                if json_match:
                    cleaned = json_match.group()
                    parsed = json.loads(cleaned)
                    if 'career_path' in parsed and 'phases' in parsed:
                        session.learning_plan = json.dumps(parsed)
                        session.is_completed = True
                        session.save()
            except (json.JSONDecodeError, ValueError):
                pass

            return Response({
                'success': True,
                'data': {
                    'session_id': session.id,
                    'message': ai_message,
                    'is_completed': session.is_completed
                }
            })

        except Exception as e:
            print(traceback.format_exc())
            return Response({
                'success': False,
                'error': str(e)
            }, status=500)


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            messages = ChatMessage.objects.filter(session=session).order_by('created_at')

            history = [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'created_at': msg.created_at
                }
                for msg in messages
            ]

            return Response({
                'success': True,
                'data': {
                    'session_id': session.id,
                    'is_completed': session.is_completed,
                    'learning_plan': json.loads(session.learning_plan) if session.learning_plan else None,
                    'messages': history
                }
            })

        except ChatSession.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Session not found'
            }, status=404)