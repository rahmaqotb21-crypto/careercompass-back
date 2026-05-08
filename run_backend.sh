#!/bin/bash
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Seeding data..."
python manage.py seed_courses
python manage.py seed_careers

echo "Starting server..."
python manage.py runserver
