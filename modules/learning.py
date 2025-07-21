from flask import Blueprint, jsonify, request, render_template
import json

# Create a Blueprint for the learning module
learning_bp = Blueprint('learning', __name__, template_folder='templates')

# Load predefined roadmaps (ensure this file exists in the root)
with open('roadmaps.json') as f:
    roadmaps = json.load(f)

# Route to serve the main roadmap interface
@learning_bp.route('/generate-roadmap', methods=['GET'])
def show_roadmap_page():
    return render_template('learning.html')  # loads your learning.html

# API endpoint to return roadmap JSON based on skill and duration
@learning_bp.route('/generate-roadmap', methods=['POST'])
def generate_roadmap():
    data = request.get_json()
    skill = data.get('skill')
    duration = data.get('duration')

    if not skill or not duration:
        return jsonify({"error": "Missing skill or duration"}), 400

    if skill not in roadmaps:
        return jsonify({"error": "Skill not found"}), 400

    roadmap = roadmaps[skill]
    if duration == "3 Months":
        roadmap = {k: v[:4] for k, v in roadmap.items()}
    elif duration == "6 Months":
        roadmap = {k: v[:6] for k, v in roadmap.items()}

    return jsonify(roadmap)

# Goal saving route (optional)
@learning_bp.route('/save_goal', methods=['POST'])
def save_goal():
    goal = request.json.get('goal')
    if goal:
        print(f"Goal saved: {goal}")
        return jsonify({"message": "Goal saved!"}), 200
    else:
        return jsonify({"error": "No goal provided"}), 400
