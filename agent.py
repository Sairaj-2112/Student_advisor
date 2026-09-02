import json
import os
import google.generativeai as genai
from typing import List, Dict, Any
from dotenv import load_dotenv
import pydantic

load_dotenv()

# Configure Gemini API
# Assuming the user has set GEMINI_API_KEY in their .env file
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Use the flash model which is widely supported
model = genai.GenerativeModel('gemini-3.5-flash')

def load_courses(filepath: str = "data/courses.json") -> List[Dict[str, Any]]:
    """Loads course data from a JSON file."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading courses: {e}")
        return []

def get_available_courses(all_courses: List[Dict], completed_course_codes: List[str]) -> List[Dict]:
    """Filters courses to find electives the student is eligible for and hasn't taken yet."""
    available = []
    for course in all_courses:
        # Only recommend electives
        if course.get("course_type", "") != "Elective":
            continue
            
        # Skip if already completed
        if course["course_code"] in completed_course_codes:
            continue
        
        # Check if prerequisites are met
        prereqs = course.get("prerequisites", [])
        if all(prereq in completed_course_codes for prereq in prereqs):
            available.append(course)
            
    return available

class RecommendationResult(pydantic.BaseModel):
    recommended_courses: List[str]
    reasoning: Dict[str, str]

def recommend_electives(completed_courses: List[str], interests: str, top_n: int = 3) -> Dict[str, Any]:
    """Uses Gemini to recommend electives based on completed courses and interests."""
    all_courses = load_courses()
    
    if not all_courses:
        return {"error": "Course database is empty or could not be loaded."}
        
    available_courses = get_available_courses(all_courses, completed_courses)
    
    if not available_courses:
        return {"error": "No available courses found based on your prerequisites."}
        
    # Format available courses for the prompt
    courses_context = ""
    for c in available_courses:
        courses_context += f"- {c['course_code']}: {c['course_name']} (Domain: {c['domain']})\n  Description: {c['description']}\n"
        
    prompt = f"""
You are an expert Academic Advisor Agent. A student is asking for elective recommendations.

Student's Completed Courses: {', '.join(completed_courses) if completed_courses else 'None'}
Student's Interests: {interests}

Here are the courses available for the student to take (prerequisites are already met):
{courses_context}

Based on the student's interests and completed courses, recommend up to {top_n} electives from the available list.
Provide your response as a JSON object with the following schema:
{{
  "recommendations": [
    {{
      "course_code": "...",
      "course_name": "...",
      "reasoning": "Explain why this course is a good fit based on their interests and past courses."
    }}
  ]
}}

Ensure the response is ONLY valid JSON, with no markdown formatting.
"""

    try:
        # Use Gemini to generate recommendations
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.7,
            )
        )
        
        # Parse the JSON response
        recommendations = json.loads(response.text)
        return recommendations
        
    except Exception as e:
        return {"error": f"Failed to generate recommendations: {str(e)}"}
