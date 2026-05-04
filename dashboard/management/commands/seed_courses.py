from django.core.management.base import BaseCommand

from dashboard.models import RecommendedCourse, SkillRequirement


SKILL_REQUIREMENTS = {
    'Python': 85,
    'SQL': 80,
    'Excel': 75,
    'Tableau': 70,
    'Statistics': 75,
    'JavaScript': 70,
    'Git': 65,
    'Algorithms': 70,
    'Figma': 65,
    'Design': 70,
    'CSS': 65,
}


RECOMMENDED_COURSES = [
    {
        'skill': 'Python',
        'platform': 'Coursera',
        'duration': '4 weeks',
        'title': 'Python for Data Science & AI',
        'tags': ['Python', 'Pandas', 'NumPy'],
        'rating': '4.8',
        'url': 'https://www.coursera.org/learn/python-for-data-science-ai',
    },
    {
        'skill': 'Python',
        'platform': 'Udemy',
        'duration': '22 hrs',
        'title': 'Complete Python Bootcamp',
        'tags': ['Python', 'Programming', 'OOP'],
        'rating': '4.7',
        'url': 'https://www.udemy.com/course/complete-python-bootcamp/',
    },
    {
        'skill': 'Python',
        'platform': 'Kaggle',
        'duration': 'Free',
        'title': 'Intro to Python Programming',
        'tags': ['Python', 'Beginner', 'Free'],
        'rating': '4.9',
        'url': 'https://www.kaggle.io/learn/python',
    },
    {
        'skill': 'SQL',
        'platform': 'Udemy',
        'duration': '12 hrs',
        'title': 'Complete SQL Bootcamp for Analysts',
        'tags': ['SQL', 'PostgreSQL', 'Analytics'],
        'rating': '4.7',
        'url': 'https://www.udemy.com/course/the-complete-sql-bootcamp/',
    },
    {
        'skill': 'SQL',
        'platform': 'Coursera',
        'duration': '5 weeks',
        'title': 'SQL for Data Science',
        'tags': ['SQL', 'Data Science', 'SQLite'],
        'rating': '4.6',
        'url': 'https://www.coursera.org/learn/sql-data-science',
    },
    {
        'skill': 'SQL',
        'platform': 'Kaggle',
        'duration': 'Free',
        'title': 'Intro to SQL',
        'tags': ['SQL', 'BigQuery', 'Free'],
        'rating': '4.8',
        'url': 'https://www.kaggle.io/learn/sql',
    },
    {
        'skill': 'Excel',
        'platform': 'LinkedIn Learning',
        'duration': '6 hrs',
        'title': 'Excel for Data Analysis',
        'tags': ['Excel', 'Dashboards', 'Formulas'],
        'rating': '4.6',
        'url': 'https://www.linkedin.com/learning/excel-for-data-analysis',
    },
    {
        'skill': 'Excel',
        'platform': 'Coursera',
        'duration': '4 weeks',
        'title': 'Excel Skills for Business',
        'tags': ['Excel', 'Business', 'Spreadsheets'],
        'rating': '4.7',
        'url': 'https://www.coursera.org/specializations/excel-skills',
    },
    {
        'skill': 'Excel',
        'platform': 'Udemy',
        'duration': '8 hrs',
        'title': 'Microsoft Excel - Data Visualization',
        'tags': ['Excel', 'Charts', 'Visualization'],
        'rating': '4.5',
        'url': 'https://www.udemy.com/course/microsoft-excel-data-visualization/',
    },
    {
        'skill': 'Tableau',
        'platform': 'Kaggle',
        'duration': 'Free',
        'title': 'Data Visualization with Tableau',
        'tags': ['Tableau', 'Charts', 'Dashboards'],
        'rating': '4.9',
        'url': 'https://www.kaggle.io/learn/data-visualization',
    },
    {
        'skill': 'Tableau',
        'platform': 'Coursera',
        'duration': '6 weeks',
        'title': 'Data Visualization with Tableau',
        'tags': ['Tableau', 'Visualization', 'Business'],
        'rating': '4.7',
        'url': 'https://www.coursera.org/learn/data-visualization-tableau',
    },
    {
        'skill': 'Statistics',
        'platform': 'edX',
        'duration': '5 weeks',
        'title': 'Statistics for Data Science',
        'tags': ['Statistics', 'Probability', 'Inference'],
        'rating': '4.7',
        'url': 'https://www.edx.org/course/statistics-for-data-science',
    },
    {
        'skill': 'JavaScript',
        'platform': 'Udemy',
        'duration': '35 hrs',
        'title': 'The Complete JavaScript Course',
        'tags': ['JavaScript', 'ES6', 'Web Dev'],
        'rating': '4.8',
        'url': 'https://www.udemy.com/course/the-complete-javascript-course/',
    },
    {
        'skill': 'JavaScript',
        'platform': 'Coursera',
        'duration': '6 weeks',
        'title': 'Introduction to Web Development',
        'tags': ['JavaScript', 'HTML', 'CSS'],
        'rating': '4.6',
        'url': 'https://www.coursera.org/learn/web-development',
    },
    {
        'skill': 'Git',
        'platform': 'Udemy',
        'duration': '10 hrs',
        'title': 'Git & GitHub Bootcamp',
        'tags': ['Git', 'GitHub', 'Version Control'],
        'rating': '4.8',
        'url': 'https://www.udemy.com/course/git-and-github-bootcamp/',
    },
    {
        'skill': 'Git',
        'platform': 'Coursera',
        'duration': '3 weeks',
        'title': 'Version Control with Git',
        'tags': ['Git', 'GitHub', 'Collaboration'],
        'rating': '4.7',
        'url': 'https://www.coursera.org/learn/version-control-with-git',
    },
    {
        'skill': 'Algorithms',
        'platform': 'Coursera',
        'duration': '8 weeks',
        'title': 'Algorithms Specialization',
        'tags': ['Algorithms', 'Data Structures', 'DSA'],
        'rating': '4.8',
        'url': 'https://www.coursera.org/specializations/algorithms',
    },
    {
        'skill': 'Algorithms',
        'platform': 'Udemy',
        'duration': '15 hrs',
        'title': 'Data Structures & Algorithms',
        'tags': ['Algorithms', 'LeetCode', 'Interview Prep'],
        'rating': '4.6',
        'url': 'https://www.udemy.com/course/data-structures-algorithms-python/',
    },
    {
        'skill': 'Figma',
        'platform': 'Udemy',
        'duration': '8 hrs',
        'title': 'UI/UX Design with Figma',
        'tags': ['Figma', 'UI Design', 'Prototyping'],
        'rating': '4.7',
        'url': 'https://www.udemy.com/course/ui-ux-design-with-figma/',
    },
    {
        'skill': 'Figma',
        'platform': 'Coursera',
        'duration': '4 weeks',
        'title': 'Figma for Beginners',
        'tags': ['Figma', 'UI Design', 'Design System'],
        'rating': '4.6',
        'url': 'https://www.coursera.org/learn/figma-for-beginners',
    },
    {
        'skill': 'Design',
        'platform': 'Coursera',
        'duration': '6 weeks',
        'title': 'UX Design Fundamentals',
        'tags': ['Design', 'UX', 'User Research'],
        'rating': '4.7',
        'url': 'https://www.coursera.org/learn/ux-design-fundamentals',
    },
    {
        'skill': 'Design',
        'platform': 'LinkedIn Learning',
        'duration': '4 hrs',
        'title': 'Design Thinking',
        'tags': ['Design', 'Innovation', 'Problem Solving'],
        'rating': '4.5',
        'url': 'https://www.linkedin.com/learning/design-thinking-fundamentals',
    },
    {
        'skill': 'CSS',
        'platform': 'Udemy',
        'duration': '12 hrs',
        'title': 'Advanced CSS and Sass',
        'tags': ['CSS', 'Flexbox', 'Grid'],
        'rating': '4.8',
        'url': 'https://www.udemy.com/course/advanced-css-and-sass/',
    },
    {
        'skill': 'CSS',
        'platform': 'FreeCodeCamp',
        'duration': 'Free',
        'title': 'Responsive Web Design',
        'tags': ['CSS', 'HTML', 'Responsive'],
        'rating': '4.9',
        'url': 'https://www.freecodecamp.org/learn/2022/responsive-web-design/',
    },
]


class Command(BaseCommand):
    help = 'Seeds skill requirements and recommended courses.'

    def handle(self, *args, **options):
        req_created = 0
        req_updated = 0
        course_created = 0
        course_updated = 0

        for skill, target_score in SKILL_REQUIREMENTS.items():
            _, created = SkillRequirement.objects.update_or_create(
                skill=skill,
                defaults={
                    'target_score': target_score,
                    'is_active': True,
                },
            )

            if created:
                req_created += 1
            else:
                req_updated += 1

        for index, course in enumerate(RECOMMENDED_COURSES):
            defaults = {
                'platform': course['platform'],
                'duration': course['duration'],
                'tags': course['tags'],
                'rating': course['rating'],
                'url': course['url'],
                'sort_order': index,
                'is_active': True,
            }

            _, created = RecommendedCourse.objects.update_or_create(
                skill=course['skill'],
                title=course['title'],
                defaults=defaults,
            )

            if created:
                course_created += 1
            else:
                course_updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Dashboard seed complete. '
            f'Skill requirements: {req_created} created, {req_updated} updated. '
            f'Courses: {course_created} created, {course_updated} updated.'
        ))