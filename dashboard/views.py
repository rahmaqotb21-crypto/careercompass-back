import json
from collections import defaultdict
import re
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chatbot.models import ChatSession
from skill_test.models import SkillTest
from dashboard.models import RecommendedCourse, SkillRequirement


def baseline_from_level(level):
    if (level or '').lower() == 'advanced':
        return 70
    if (level or '').lower() == 'intermediate':
        return 50
    return 30


def build_profile_context(user):
    return {
        'career_goal': user.career_goal or '',
        'current_level': user.current_level or 'Beginner',
        'learning_style': user.learning_style or 'Video Courses',
        'hours_per_week': user.hours_per_week or '4-8 hours',
        'notifications': {
            'weekly_progress': user.notify_weekly_progress if hasattr(user, 'notify_weekly_progress') else True,
            'new_courses': user.notify_new_courses if hasattr(user, 'notify_new_courses') else True,
            'daily_reminder': user.notify_daily_reminder if hasattr(user, 'notify_daily_reminder') else False,
        },
    }


def build_recommendations(user):
    recommendations = []
    
    if not user.career_goal:
        recommendations.append('Set your career goal in settings to unlock more targeted recommendations.')
    
    if user.learning_style and user.hours_per_week:
        recommendations.append(
            f'Build a {user.learning_style.lower()} study plan around {user.hours_per_week} each week for faster consistency.'
        )
    
    if not recommendations:
        recommendations.append('Start a chat with AI Coach to create your personalized learning plan.')
        recommendations.append('Take a skill test to measure your current abilities.')
    
    return recommendations[:4]


def build_level_progress(current_level, overall_progress):
    levels = ['Beginner', 'Intermediate', 'Advanced']
    normalized_level = (current_level or 'Beginner').strip().title()
    
    if normalized_level not in levels:
        normalized_level = 'Beginner'
    
    current_index = levels.index(normalized_level)
    progress_map = {}
    
    for index, level in enumerate(levels):
        if index < current_index:
            progress_map[level] = 100
        elif index == current_index:
            progress_map[level] = max(0, min(100, int(overall_progress)))
        else:
            progress_map[level] = 0
    
    return progress_map


def goal_alignment_score(goal, course):
    if not goal:
        return 0.0
    goal_lower = goal.lower()
    title_lower = course.title.lower()
    tags_lower = ' '.join(course.tags).lower() if course.tags else ''
    skill_lower = course.skill.lower()

    keywords = {
        'data science': ['data', 'science', 'analytics', 'python', 'pandas', 'statistics'],
        'software developer': ['programming', 'developer', 'javascript', 'algorithm', 'git', 'web'],
        'web developer': ['html', 'css', 'javascript', 'react', 'web', 'frontend'],
        'ui/ux design': ['design', 'figma', 'ui', 'ux', 'prototype'],
        'data analyst': ['sql', 'excel', 'tableau', 'analytics', 'visualization'],
    }

    for key, terms in keywords.items():
        if key in goal_lower:
            matches = sum(1 for t in terms if t in title_lower or t in tags_lower or t in skill_lower)
            return min(1.0, matches / 3.0)

    if skill_lower in title_lower or skill_lower in tags_lower:
        return 0.5

    return 0.0


def style_platform_score(style, course):
    if not style or not course.platform:
        return 0.5

    style_lower = style.lower()
    platform = course.platform.lower()

    video_platforms = ['coursera', 'udemy', 'linkedin']
    interactive_platforms = ['kaggle']
    reading_platforms = ['edx', 'freecodecamp']

    if 'video' in style_lower:
        return 1.0 if any(p in platform for p in video_platforms) else 0.3
    if 'interactive' in style_lower or 'practice' in style_lower:
        return 1.0 if any(p in platform for p in interactive_platforms) else 0.4
    if 'reading' in style_lower or 'book' in style_lower:
        return 1.0 if any(p in platform for p in reading_platforms) else 0.4

    return 0.5


def time_fit_score(available_time, course_duration):
    if not available_time or not course_duration:
        return 0.5

    time_map = {
        '1-2 hours': 2,
        '2-4 hours': 4,
        '4-8 hours': 8,
        '8+ hours': 12,
    }

    hours = time_map.get(available_time, 4)

    dur_lower = course_duration.lower()
    if 'free' in dur_lower:
        return 1.0
    elif 'week' in dur_lower:
        nums = re.findall(r'\d+', dur_lower)
        weeks = int(nums[0]) if nums else 4
        return 1.0 if weeks * 2 <= hours else 0.5 if weeks * 4 <= hours else 0.2
    elif 'hr' in dur_lower or 'hour' in dur_lower:
        nums = re.findall(r'\d+', dur_lower)
        course_hours = int(nums[0]) if nums else 4
        return 1.0 if course_hours <= hours else 0.5 if course_hours <= hours * 2 else 0.2

    return 0.5


def rating_quality_score(rating):
    try:
        r = float(rating) if rating else 0
        if r >= 4.7:
            return 1.0
        elif r >= 4.5:
            return 0.8
        elif r >= 4.0:
            return 0.6
        elif r >= 3.5:
            return 0.4
        return 0.2
    except:
        return 0.5


def serialize_course(course):
    return {
        'title': course.title,
        'skill': course.skill,
        'platform': course.platform,
        'duration': course.duration,
        'rating': course.rating,
        'url': course.url,
        'tags': course.tags or [],
    }


def build_recommended_courses(snapshot, user, required_levels):
    baseline = baseline_from_level(user.current_level)

    catalog = list(RecommendedCourse.objects.filter(is_active=True).order_by('sort_order', 'id'))
    if not catalog:
        return []

    scored = []
    for course in catalog:
        current_score = float(snapshot.get(course.skill, baseline))
        target_score = float(required_levels.get(course.skill, 70))
        skill_gap = max(0.0, target_score - current_score)
        gap_score = min(1.0, skill_gap / 100.0)

        goal_score = goal_alignment_score(user.career_goal, course)
        style_score = style_platform_score(user.learning_style, course)
        pacing_score = time_fit_score(user.hours_per_week, course.duration)
        quality_score = rating_quality_score(course.rating)

        fit_score = (
            (gap_score * 0.45)
            + (goal_score * 0.22)
            + (style_score * 0.18)
            + (pacing_score * 0.10)
            + (quality_score * 0.05)
        ) * 100

        reasons = []
        if skill_gap >= 12:
            reasons.append(f'{course.skill} is below your target by {round(skill_gap)}%, so this course closes a high-priority gap.')
        if user.career_goal and goal_score >= 0.3:
            reasons.append(f'Content aligns with your career goal: {user.career_goal}.')
        if user.learning_style and style_score >= 0.6:
            reasons.append(f'Format matches your preferred learning style: {user.learning_style}.')
        if user.hours_per_week and pacing_score >= 0.6:
            reasons.append(f'Estimated pace fits your weekly availability ({user.hours_per_week}).')
        if not reasons:
            reasons.append('Balanced option based on your current profile and skill baseline.')

        scored.append({
            **serialize_course(course),
            'fit_score': round(fit_score),
            'goal_alignment': round(goal_score * 100),
            'skill_gap': round(skill_gap),
            'current_score': round(current_score),
            'target_score': round(target_score),
            'recommendation_reason': reasons[:2],
        })

    scored.sort(key=lambda x: x['fit_score'], reverse=True)
    return scored[:20]


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        sessions = ChatSession.objects.filter(user=user).order_by('-created_at')
        tests = SkillTest.objects.filter(user=user, is_submitted=True).order_by('-created_at')[:20]
        
        total_sessions = sessions.count()
        completed_sessions = sessions.filter(is_completed=True).count()
        tests_taken = SkillTest.objects.filter(user=user, is_submitted=True).count()
        
        profile_points = 0
        if user.career_goal:
            profile_points += 10
        if user.current_level:
            profile_points += 5
        if hasattr(user, 'learning_style') and user.learning_style:
            profile_points += 5
        if hasattr(user, 'hours_per_week') and user.hours_per_week:
            profile_points += 5
        
        overall_progress = min(100, (completed_sessions * 20) + (min(tests_taken, 5) * 8) + profile_points)
        
        latest_session = sessions.filter(is_completed=True).first()
        learning_plan = None
        if latest_session and latest_session.learning_plan:
            try:
                learning_plan = json.loads(latest_session.learning_plan)
            except:
                pass
        
        # Skill name normalization mapping
        skill_normalization = {
            'python basics': 'Python',
            'python programming': 'Python',
            'machine learning': 'Python',
            'data structures': 'Algorithms',
            'algorithms': 'Algorithms',
            'sql': 'SQL',
            'database': 'SQL',
            'excel': 'Excel',
            'javascript': 'JavaScript',
            'web development': 'JavaScript',
            'react': 'JavaScript',
            'git': 'Git',
            'linux': 'Algorithms',
            'aws': 'Algorithms',
            'docker': 'Algorithms',
            'kubernetes': 'Algorithms',
            'figma': 'Figma',
            'ui design': 'Figma',
            'design': 'Design',
            'ux': 'Design',
            'css': 'CSS',
        }
        
        skills_snapshot = {}
        
        # First, collect all skills from learning plan to use as base
        all_plan_skills = []
        if learning_plan:
            all_plan_skills = learning_plan.get('skills', [])
            for phase in learning_plan.get('phases', []):
                for topic in phase.get('topics', []):
                    if topic not in all_plan_skills:
                        all_plan_skills.append(topic)
        
        # Then fill in with test scores
        for test in tests:
            if test.score is not None:
                # Try to get skill names from the test's session learning plan
                if test.session and test.session.learning_plan:
                    try:
                        plan = json.loads(test.session.learning_plan)
                        skills = plan.get('skills', [])
                        # Also get topics from phases
                        for phase in plan.get('phases', []):
                            for topic in phase.get('topics', []):
                                if topic not in skills:
                                    skills.append(topic)
                        
                        # Normalize skill names
                        normalized_skills = []
                        for skill in skills:
                            normalized = skill_normalization.get(skill.lower(), skill)
                            normalized_skills.append(normalized)
                        skills = list(set(normalized_skills))
                        
                        # Distribute the score across skills
                        if skills:
                            per_skill = test.score / len(skills)
                            for skill in skills:
                                # If skill already exists, average the scores
                                if skill in skills_snapshot:
                                    skills_snapshot[skill] = (skills_snapshot[skill] + per_skill) / 2
                                else:
                                    skills_snapshot[skill] = per_skill
                    except:
                        pass
        
        # If no test data, use learning plan skills with default 30 score
        if not skills_snapshot and all_plan_skills:
            for skill in all_plan_skills:
                skills_snapshot[skill] = 30
        
        required_skill_levels = {}
        plan_skills = []
        
        if learning_plan:
            plan_skills = learning_plan.get('skills', [])
            for phase in learning_plan.get('phases', []):
                for topic in phase.get('topics', []):
                    if topic not in plan_skills:
                        plan_skills.append(topic)
        
        # Deduplicate and normalize
        unique_skills = list(set(plan_skills))
        
        if unique_skills:
            for skill in unique_skills:
                # Normalize skill name
                normalized = skill_normalization.get(skill.lower(), skill)
                # Try to find in database
                existing = SkillRequirement.objects.filter(skill=normalized, is_active=True).first()
                target = existing.target_score if existing else 70
                # Use normalized name as key for consistency
                required_skill_levels[normalized] = target
        else:
            for req in SkillRequirement.objects.filter(is_active=True):
                required_skill_levels[req.skill] = req.target_score

        if not skills_snapshot and plan_skills:
            skills_snapshot = {skill: 30 for skill in plan_skills}

        profile_context = build_profile_context(user)
        recommendations = build_recommendations(user)
        level_progress = build_level_progress(user.current_level, overall_progress)

        recommended_courses = build_recommended_courses(skills_snapshot, user, required_skill_levels)
        
        test_history = []
        for test in tests:
            test_history.append({
                'test_id': test.id,
                'score': test.score,
                'correct_answers': test.correct_answers,
                'total_questions': test.total_questions,
                'date': test.created_at.strftime('%Y-%m-%d'),
            })
        
        return Response({
            'success': True,
            'data': {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'career_goal': user.career_goal or '',
                    'current_level': user.current_level or 'Beginner',
                },
                'progress': {
                    'overall_progress': overall_progress,
                    'total_sessions': total_sessions,
                    'completed_sessions': completed_sessions,
                    'tests_taken': tests_taken,
                    'latest_session_id': latest_session.id if latest_session else None,
                },
                'level_progress': level_progress,
                'skills_snapshot': skills_snapshot,
                'required_skill_levels': required_skill_levels,
                'profile_context': profile_context,
                'recommendations': recommendations,
                'recommended_courses': recommended_courses,
                'learning_plan': learning_plan,
                'test_history': test_history[:10],
            },
        })