from flask import Blueprint, render_template, request
import json

# Define the Blueprint for courses
courses_bp = Blueprint('courses', __name__)

# Load all courses from JSON
def load_courses():
    with open('courses.json', 'r') as file:
        return json.load(file)

# Filter courses by skill
def get_courses_by_skill(skill):
    courses = load_courses()
    if skill:
        return [course for course in courses if course["skill"] == skill]
    return courses

# Define the route for displaying and filtering courses
@courses_bp.route('/courses', methods=['GET', 'POST'])
def courses():
    skill_selected = None
    filtered_courses = []

    if request.method == 'POST':
        skill_selected = request.form.get('skill')
        filtered_courses = get_courses_by_skill(skill_selected)
    else:
        filtered_courses = load_courses()

    return render_template('courses.html', courses=filtered_courses, selected_skill=skill_selected)
