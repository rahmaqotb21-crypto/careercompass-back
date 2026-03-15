from django.shortcuts import render

import google.generativeai as genai
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ChatSession, ChatMessage

genai.configure(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = """You are CareerCompass AI, a professional career coach and learning path advisor.

Your job is to help users discover their ideal career path and create a personalized learning plan.

Follow these steps in order:
1. Greet the user warmly and ask about their career goal
2. Ask about their current skills and experience level
3. Ask about their education background
4. Ask if they have a CV/Resume (ask them to describe it briefly)
5. Ask about their LinkedIn and GitHub profiles if they have them
6. Ask about their available time per week for learning
7. Ask about their preferred learning style (videos, reading, projects)

After collecting all information, generate a learning plan in this EXACT JSON format:
{
  "career_path": "Job Title",
  "level": "Beginner/Intermediate/Advanced",
  "total_duration": "X months",
  "skills": ["skill1", "skill2", "skill3"],
  "phases": [
    {
      "phase": 1,
      "title": "Phase Title",
      "duration": "X weeks",
      "topics": ["topic1", "topic2"],
      "resources": ["resource1", "resource2"]
    }
  ],
  "message": "Your personalized test will be generated based on this plan"
}

Rules:
- Always respond in the same language the user uses (Arabic or English)
- Be encouraging, professional, and friendly
- Ask one or two questions at a time
- Only generate the JSON plan after collecting ALL information
- When generating the plan, output ONLY the JSON, nothing else
"""

class ChatbotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get('message')
        session_id = request.data.get('session_id')

        if not user_message:
            return Response({'success': False, 'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create session
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                return Response({'success': False, 'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            session = ChatSession.objects.create(user=request.user)

        # Save user message
        ChatMessage.objects.create(session=session, role='user', content=user_message)

        # Get conversation history
        messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        history = []
        messages_list = list(messages)
        for msg in messages_list[:-1]:
            history.append({
                'role': 'user' if msg.role == 'user' else 'model',
                'parts': [msg.content]
            })

        # Generate AI response
        try:
            model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                system_instruction=SYSTEM_PROMPT
            )
            chat = model.start_chat(history=history)
            response = chat.send_message(user_message)
            ai_message = response.text

            # Save AI response
            ChatMessage.objects.create(session=session, role='assistant', content=ai_message)

            # Check if learning plan is generated
            if 'learning plan' in ai_message.lower() or 'خطة' in ai_message:
                session.learning_plan = ai_message
                session.is_completed = True
                session.save()

            return Response({
                'success': True,
                'data': {
                    'session_id': session.id,
                    'message': ai_message,
                    'is_completed': session.is_completed
                }
            })

        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            messages = ChatMessage.objects.filter(session=session).order_by('created_at')
            history = [{'role': msg.role, 'content': msg.content, 'created_at': msg.created_at} for msg in messages]
            return Response({
                'success': True,
                'data': {
                    'session_id': session.id,
                    'is_completed': session.is_completed,
                    'messages': history
                }
            })
        except ChatSession.DoesNotExist:
            return Response({'success': False, 'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)# Create your views here.
