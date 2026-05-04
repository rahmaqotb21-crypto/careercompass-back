import json
import traceback

from groq import Groq
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ChatSession, ChatMessage
from .plan_parser import parse_learning_plan

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
            if not settings.GROQ_API_KEY:
                return Response({
                    'success': False,
                    'error': 'GROQ_API_KEY not configured. Please set your Groq API key in .env file.'
                }, status=500)
            
            client = Groq(api_key=settings.GROQ_API_KEY)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=history,
                max_tokens=1500,
            )
            ai_message = response.choices[0].message.content

            # Debug: print first 200 chars of response
            print(f"AI Response (first 200): {ai_message[:200]}")

            # Try to find and parse JSON learning plan
            plan_data = parse_learning_plan(ai_message)

            if plan_data:
                print(f"Learning plan detected: {plan_data.get('career_path')}")

                # Save the learning plan to DB
                session.learning_plan = json.dumps(plan_data)
                session.is_completed = True
                session.name = f"{plan_data.get('career_path', 'Career')} Plan"
                session.save(update_fields=['learning_plan', 'is_completed', 'name'])

                # Create a nice response message instead of raw JSON
                career = plan_data.get('career_path', 'professional')
                duration = plan_data.get('total_duration', '')
                phases = len(plan_data.get('phases', []))
                skills_list = plan_data.get('skills', [])
                skills = ', '.join(skills_list) if skills_list else 'various skills'
                user_msg = plan_data.get('message', '')

                if user_msg:
                    ai_message = (
                        f"Great news. Your personalized learning plan for becoming a {career} is ready.\n\n"
                        f"{user_msg}\n\n"
                        f"Your plan covers {duration} of learning with {phases} phases covering: {skills}.\n\n"
                        "Take a skill test now to measure your current level and start your journey."
                    )
                else:
                    ai_message = (
                        f"Great news. Your personalized learning plan for becoming a {career} is ready.\n\n"
                        f"I've designed a {duration} learning path with {phases} phases covering: {skills}.\n\n"
                        "Take a skill test now to measure your current level and start your journey."
                    )
            else:
                # Don't replace with generic message - let the AI response through as-is
                print("No valid learning plan found in response")
            
            # Save the assistant message to DB
            ChatMessage.objects.create(session=session, role='assistant', content=ai_message)
            
            # Generate session name if not set and not already from plan
            if session.name == 'New Chat':
                first_user_msg = ChatMessage.objects.filter(session=session, role='user').first()
                if first_user_msg:
                    msg_lower = first_user_msg.content.lower()
                    if 'data scientist' in msg_lower or 'data science' in msg_lower:
                        session.name = 'Data Science Chat'
                    elif 'software' in msg_lower or 'developer' in msg_lower or 'programming' in msg_lower:
                        session.name = 'Software Dev Chat'
                    elif 'design' in msg_lower or 'ux' in msg_lower or 'ui' in msg_lower:
                        session.name = 'UI/UX Design Chat'
                    elif 'help' in msg_lower or 'decide' in msg_lower:
                        session.name = 'Career Guidance'
                    else:
                        words = first_user_msg.content.split()[:4]
                        session.name = ' '.join(words) + ('...' if len(first_user_msg.content.split()) > 4 else '')
                    session.save(update_fields=['name'])

            print(f"Returning response with is_completed={session.is_completed}")
            return Response({
                'success': True,
                'data': {
                    'session_id': session.id,
                    'message': ai_message,
                    'is_completed': session.is_completed
                }
            })

        except Exception as e:
            print(f"Groq Error: {str(e)}")
            print(traceback.format_exc())
            return Response({
                'success': False,
                'error': f'AI service error: {str(e)}'
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
                    'learning_plan': parse_learning_plan(session.learning_plan) if session.learning_plan else None,
                    'messages': history
                }
            })

        except ChatSession.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Session not found'
            }, status=404)


class ChatSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = ChatSession.objects.filter(
            user=request.user
        ).order_by('-created_at')[:20]

        session_list = []
        for session in sessions:
            career_path = None
            if session.learning_plan:
                plan = parse_learning_plan(session.learning_plan)
                career_path = plan.get('career_path') if plan else None
            
            session_list.append({
                'session_id': session.id,
                'name': session.name,
                'created_at': session.created_at.isoformat(),
                'is_completed': session.is_completed,
                'career_path': career_path,
            })

        return Response({
            'success': True,
            'data': {
                'sessions': session_list
            }
        })


class PlanStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        has_completed_plan = ChatSession.objects.filter(
            user=request.user,
            is_completed=True,
            learning_plan__isnull=False
        ).exists()
        
        return Response({
            'success': True,
            'has_plan': has_completed_plan
        })