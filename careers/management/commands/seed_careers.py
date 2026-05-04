from django.core.management.base import BaseCommand

from careers.models import Career


DEFAULT_CAREERS = [
    {
        'title': 'Data Analyst',
        'description': 'Transform data into actionable insights using analytics and visualization.',
        'salary_range': '$65K - $120K',
        'growth': '+25%',
        'skills': ['Python', 'SQL', 'Excel', 'Tableau', 'Power BI'],
        'path': ['Junior Data Analyst', 'Data Analyst', 'Senior Analyst', 'Analytics Manager', 'Head of Data'],
        'countries': [
            {'name': 'USA', 'salary': '$90K-$120K'},
            {'name': 'UK', 'salary': 'GBP 45K-75K'},
            {'name': 'Germany', 'salary': 'EUR 50K-80K'},
            {'name': 'Egypt', 'salary': 'EGP 25K-60K/mo'},
        ],
    },
    {
        'title': 'Data Scientist',
        'description': 'Build predictive models and experiments to solve business problems with data.',
        'salary_range': '$95K - $170K',
        'growth': '+32%',
        'skills': ['Python', 'Statistics', 'SQL', 'Machine Learning', 'Experimentation'],
        'path': ['Junior Data Scientist', 'Data Scientist', 'Senior Data Scientist', 'ML Lead', 'Head of Data Science'],
        'countries': [
            {'name': 'USA', 'salary': '$120K-$170K'},
            {'name': 'UK', 'salary': 'GBP 60K-95K'},
            {'name': 'Germany', 'salary': 'EUR 70K-110K'},
            {'name': 'Egypt', 'salary': 'EGP 40K-90K/mo'},
        ],
    },
    {
        'title': 'BI Engineer',
        'description': 'Design data pipelines and dashboards for reliable business intelligence reporting.',
        'salary_range': '$80K - $145K',
        'growth': '+24%',
        'skills': ['SQL', 'Python', 'Tableau', 'Data Warehousing', 'ETL'],
        'path': ['BI Developer', 'BI Engineer', 'Senior BI Engineer', 'Analytics Engineering Manager', 'Director of BI'],
        'countries': [
            {'name': 'USA', 'salary': '$105K-$145K'},
            {'name': 'UK', 'salary': 'GBP 52K-85K'},
            {'name': 'Germany', 'salary': 'EUR 58K-95K'},
            {'name': 'Egypt', 'salary': 'EGP 32K-75K/mo'},
        ],
    },
    {
        'title': 'Machine Learning Engineer',
        'description': 'Deploy and scale ML models for production-grade intelligent applications.',
        'salary_range': '$110K - $190K',
        'growth': '+36%',
        'skills': ['Python', 'Statistics', 'Model Deployment', 'MLOps', 'SQL'],
        'path': ['ML Engineer I', 'Machine Learning Engineer', 'Senior ML Engineer', 'ML Platform Lead', 'Head of AI Engineering'],
        'countries': [
            {'name': 'USA', 'salary': '$135K-$190K'},
            {'name': 'UK', 'salary': 'GBP 70K-110K'},
            {'name': 'Germany', 'salary': 'EUR 78K-125K'},
            {'name': 'Egypt', 'salary': 'EGP 55K-120K/mo'},
        ],
    },
    {
        'title': 'Backend Developer',
        'description': 'Build secure APIs, data models, and core services for web and mobile products.',
        'salary_range': '$85K - $155K',
        'growth': '+28%',
        'skills': ['Python', 'SQL', 'Django', 'REST APIs', 'System Design'],
        'path': ['Junior Backend Developer', 'Backend Developer', 'Senior Backend Engineer', 'Backend Architect', 'Engineering Manager'],
        'countries': [
            {'name': 'USA', 'salary': '$110K-$155K'},
            {'name': 'UK', 'salary': 'GBP 55K-90K'},
            {'name': 'Germany', 'salary': 'EUR 62K-98K'},
            {'name': 'Egypt', 'salary': 'EGP 35K-85K/mo'},
        ],
    },
    {
        'title': 'Frontend Developer',
        'description': 'Create high-quality responsive user interfaces and delightful web experiences.',
        'salary_range': '$75K - $145K',
        'growth': '+27%',
        'skills': ['JavaScript', 'TypeScript', 'React', 'UI Performance', 'APIs'],
        'path': ['Junior Frontend Developer', 'Frontend Developer', 'Senior Frontend Engineer', 'Frontend Lead', 'Principal Engineer'],
        'countries': [
            {'name': 'USA', 'salary': '$100K-$145K'},
            {'name': 'UK', 'salary': 'GBP 50K-85K'},
            {'name': 'Germany', 'salary': 'EUR 58K-92K'},
            {'name': 'Egypt', 'salary': 'EGP 30K-75K/mo'},
        ],
    },
    {
        'title': 'Full Stack Developer',
        'description': 'Own end-to-end product features across frontend, backend, and data layers.',
        'salary_range': '$90K - $165K',
        'growth': '+31%',
        'skills': ['JavaScript', 'React', 'Python', 'SQL', 'Cloud Basics'],
        'path': ['Junior Full Stack Developer', 'Full Stack Developer', 'Senior Full Stack Engineer', 'Tech Lead', 'Engineering Director'],
        'countries': [
            {'name': 'USA', 'salary': '$115K-$165K'},
            {'name': 'UK', 'salary': 'GBP 58K-95K'},
            {'name': 'Germany', 'salary': 'EUR 66K-105K'},
            {'name': 'Egypt', 'salary': 'EGP 38K-90K/mo'},
        ],
    },
    {
        'title': 'DevOps Engineer',
        'description': 'Automate delivery pipelines and improve reliability with modern infrastructure tooling.',
        'salary_range': '$95K - $170K',
        'growth': '+29%',
        'skills': ['Linux', 'Docker', 'Kubernetes', 'CI/CD', 'Python'],
        'path': ['DevOps Associate', 'DevOps Engineer', 'Senior DevOps Engineer', 'Platform Lead', 'Head of Infrastructure'],
        'countries': [
            {'name': 'USA', 'salary': '$120K-$170K'},
            {'name': 'UK', 'salary': 'GBP 62K-98K'},
            {'name': 'Germany', 'salary': 'EUR 70K-108K'},
            {'name': 'Egypt', 'salary': 'EGP 45K-100K/mo'},
        ],
    },
    {
        'title': 'Cloud Engineer',
        'description': 'Design and operate scalable cloud architecture with strong security and cost control.',
        'salary_range': '$100K - $175K',
        'growth': '+30%',
        'skills': ['Cloud Platforms', 'Infrastructure as Code', 'Networking', 'Security', 'Python'],
        'path': ['Cloud Support Engineer', 'Cloud Engineer', 'Senior Cloud Engineer', 'Cloud Architect', 'Head of Cloud'],
        'countries': [
            {'name': 'USA', 'salary': '$125K-$175K'},
            {'name': 'UK', 'salary': 'GBP 65K-102K'},
            {'name': 'Germany', 'salary': 'EUR 72K-112K'},
            {'name': 'Egypt', 'salary': 'EGP 48K-105K/mo'},
        ],
    },
    {
        'title': 'Cybersecurity Analyst',
        'description': 'Monitor threats, respond to incidents, and improve security posture across systems.',
        'salary_range': '$85K - $155K',
        'growth': '+35%',
        'skills': ['Security Monitoring', 'Incident Response', 'Risk Assessment', 'Networking', 'Python'],
        'path': ['Security Analyst', 'Cybersecurity Analyst', 'Senior Security Analyst', 'Security Lead', 'Security Manager'],
        'countries': [
            {'name': 'USA', 'salary': '$110K-$155K'},
            {'name': 'UK', 'salary': 'GBP 55K-90K'},
            {'name': 'Germany', 'salary': 'EUR 62K-100K'},
            {'name': 'Egypt', 'salary': 'EGP 34K-82K/mo'},
        ],
    },
    {
        'title': 'Product Manager',
        'description': 'Define product strategy, coordinate teams, and deliver user-centric outcomes.',
        'salary_range': '$95K - $180K',
        'growth': '+23%',
        'skills': ['Product Strategy', 'Roadmapping', 'Stakeholder Management', 'Analytics', 'SQL'],
        'path': ['Associate Product Manager', 'Product Manager', 'Senior Product Manager', 'Group Product Manager', 'Head of Product'],
        'countries': [
            {'name': 'USA', 'salary': '$125K-$180K'},
            {'name': 'UK', 'salary': 'GBP 68K-115K'},
            {'name': 'Germany', 'salary': 'EUR 75K-120K'},
            {'name': 'Egypt', 'salary': 'EGP 50K-115K/mo'},
        ],
    },
    {
        'title': 'QA Automation Engineer',
        'description': 'Build test automation frameworks to improve release quality and engineering velocity.',
        'salary_range': '$75K - $140K',
        'growth': '+21%',
        'skills': ['Test Automation', 'Python', 'API Testing', 'CI/CD', 'Quality Engineering'],
        'path': ['QA Analyst', 'QA Automation Engineer', 'Senior QA Engineer', 'QA Lead', 'Quality Manager'],
        'countries': [
            {'name': 'USA', 'salary': '$95K-$140K'},
            {'name': 'UK', 'salary': 'GBP 48K-82K'},
            {'name': 'Germany', 'salary': 'EUR 54K-88K'},
            {'name': 'Egypt', 'salary': 'EGP 28K-70K/mo'},
        ],
    },
    {
        'title': 'UI/UX Designer',
        'description': 'Design intuitive digital products with strong user-centered workflows.',
        'salary_range': '$60K - $130K',
        'growth': '+22%',
        'skills': ['Figma', 'Prototyping', 'Design Systems', 'User Research', 'Analytics'],
        'path': ['Junior Designer', 'UI/UX Designer', 'Senior Designer', 'Design Lead', 'Head of Design'],
        'countries': [
            {'name': 'USA', 'salary': '$80K-$130K'},
            {'name': 'UK', 'salary': 'GBP 40K-70K'},
            {'name': 'Germany', 'salary': 'EUR 45K-75K'},
            {'name': 'Egypt', 'salary': 'EGP 20K-50K/mo'},
        ],
    },
    {
        'title': 'Mobile App Developer',
        'description': 'Build high-performance mobile applications with seamless user experiences.',
        'salary_range': '$80K - $150K',
        'growth': '+26%',
        'skills': ['Mobile Development', 'React Native', 'API Integration', 'Performance', 'SQL'],
        'path': ['Junior Mobile Developer', 'Mobile App Developer', 'Senior Mobile Engineer', 'Mobile Lead', 'Principal Mobile Engineer'],
        'countries': [
            {'name': 'USA', 'salary': '$105K-$150K'},
            {'name': 'UK', 'salary': 'GBP 55K-90K'},
            {'name': 'Germany', 'salary': 'EUR 62K-96K'},
            {'name': 'Egypt', 'salary': 'EGP 33K-78K/mo'},
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed default careers.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update existing seeded careers if they already exist.',
        )

    def handle(self, *args, **options):
        force = options['force']
        created = 0
        updated = 0
        skipped = 0

        for item in DEFAULT_CAREERS:
            career, is_created = Career.objects.get_or_create(
                title=item['title'],
                defaults={
                    'description': item['description'],
                    'salary_range': item['salary_range'],
                    'growth': item['growth'],
                    'skills': item['skills'],
                    'path': item['path'],
                    'countries': item['countries'],
                    'is_active': True,
                },
            )

            if is_created:
                created += 1
                continue

            if not force:
                skipped += 1
                continue

            changed = False
            for field in ['description', 'salary_range', 'growth', 'skills', 'path', 'countries']:
                if getattr(career, field) != item[field]:
                    setattr(career, field, item[field])
                    changed = True
            if not career.is_active:
                career.is_active = True
                changed = True

            if changed:
                career.save(update_fields=['description', 'salary_range', 'growth', 'skills', 'path', 'countries', 'is_active'])
                updated += 1
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Seed complete: created={created}, updated={updated}, skipped={skipped}'
            )
        )