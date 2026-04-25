import json
import re
import traceback

from groq import Groq
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chatbot.models import ChatSession
from .models import SkillTest, Question


class GenerateTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get('session_id')

        if not session_id:
            return Response({'success': False, 'error': 'session_id is required'}, status=400)

        try:
            session = ChatSession.objects.get(id=session_id, user=request.user, is_completed=True)
        except ChatSession.DoesNotExist:
            return Response({'success': False, 'error': 'Session not found or not completed'}, status=404)

        if not session.learning_plan:
            return Response({'success': False, 'error': 'No learning plan found'}, status=400)

        learning_plan = json.loads(session.learning_plan)

        # عمل test جديد
        test = SkillTest.objects.create(
            user=request.user,
            session=session,
        )

        prompt = f"""You are a technical interviewer. Generate exactly 10 MCQ questions to test the user's REAL TECHNICAL KNOWLEDGE.

Career Path: {learning_plan.get('career_path')}
Level: {learning_plan.get('level')}
Skills: {learning_plan.get('skills')}
Topics: {[topic for phase in learning_plan.get('phases', []) for topic in phase.get('topics', [])]}

Rules:
- Ask about REAL technical concepts (code, definitions, differences)
- Match the {learning_plan.get('level')} level
- Do NOT ask about the learning plan itself

Output ONLY a valid JSON array like this:
[
  {{
    "question": "Question text here?",
    "option_a": "First option",
    "option_b": "Second option",
    "option_c": "Third option",
    "option_d": "Fourth option",
    "correct_answer": "A"
  }}
]

IMPORTANT: Output ONLY the JSON array, no extra text."""

        try:
            client = Groq(api_key=settings.GROQ_API_KEY)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
            )
            ai_response = response.choices[0].message.content

            json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
            if not json_match:
                return Response({'success': False, 'error': 'Failed to generate questions'}, status=500)

            questions_data = json.loads(json_match.group())

            questions_list = []
            for q in questions_data:
                question = Question.objects.create(
                    test=test,
                    question_text=q['question'],
                    option_a=q['option_a'],
                    option_b=q['option_b'],
                    option_c=q['option_c'],
                    option_d=q['option_d'],
                    correct_answer=q['correct_answer'].upper(),
                )
                questions_list.append({
                    'id': question.id,
                    'question': question.question_text,
                    'option_a': question.option_a,
                    'option_b': question.option_b,
                    'option_c': question.option_c,
                    'option_d': question.option_d,
                })

            test.total_questions = len(questions_list)
            test.save()

            return Response({
                'success': True,
                'data': {
                    'test_id': test.id,
                    'total_questions': test.total_questions,
                    'questions': questions_list
                }
            })

        except Exception as e:
            test.delete()
            print(traceback.format_exc())
            return Response({'success': False, 'error': str(e)}, status=500)


class SubmitTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        test_id = request.data.get('test_id')
        answers = request.data.get('answers')

        if not test_id or not answers:
            return Response({'success': False, 'error': 'test_id and answers are required'}, status=400)

        try:
            test = SkillTest.objects.get(id=test_id, user=request.user)
        except SkillTest.DoesNotExist:
            return Response({'success': False, 'error': 'Test not found'}, status=404)

        if test.is_submitted:
            return Response({'success': False, 'error': 'Test already submitted'}, status=400)

        correct = 0
        results = []
        for answer in answers:
            question_id = answer.get('question_id')
            user_answer = answer.get('answer', '').upper()

            try:
                question = Question.objects.get(id=question_id, test=test)
                question.user_answer = user_answer
                question.save()

                is_correct = user_answer == question.correct_answer
                if is_correct:
                    correct += 1

                results.append({
                    'question_id': question_id,
                    'question': question.question_text,
                    'your_answer': user_answer,
                    'correct_answer': question.correct_answer,
                    'is_correct': is_correct,
                })
            except Question.DoesNotExist:
                pass

        score = (correct / test.total_questions) * 100 if test.total_questions > 0 else 0
        test.correct_answers = correct
        test.score = round(score, 2)
        test.is_submitted = True
        test.save()

        return Response({
            'success': True,
            'data': {
                'test_id': test.id,
                'score': test.score,
                'correct_answers': correct,
                'total_questions': test.total_questions,
                'results': results
            }
        })