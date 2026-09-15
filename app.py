import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)

CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL")
CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")

st.set_page_config(
    page_title="Canvas Assignment AI Assistant",
    page_icon="🎓",
    layout="wide"
)

if CANVAS_API_TOKEN:
    st.write("✅ Canvas token loaded securely")
else:
    st.write("❌ Canvas token was not loaded")


st.title("🎓 Canvas Assignment AI Assistant")
st.write(
    "View upcoming Canvas assignments, organize coursework, "
    "and manage deadlines from one place."
)

headers = {
    "Authorization": f"Bearer {CANVAS_API_TOKEN.strip()}"
}

url = f"{CANVAS_BASE_URL}/api/v1/users/self"

try:
    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        user = response.json()
        st.success("✅ Successfully connected to Canvas!")
        st.write(f"Welcome, **{user.get('name', 'Canvas User')}**")
    else:
        st.error(f"Canvas connection failed. Status code: {response.status_code}")
        st.write("Canvas response:")
        st.code(response.text[:1000])

except requests.RequestException as error:
    st.error(f"Unable to connect to Canvas: {error}")

st.subheader("📚 Canvas Courses")

courses_url = f"{CANVAS_BASE_URL}/api/v1/courses"

params = {
    "enrollment_state": "active",
    "per_page": 100
}

try:
    courses_response = requests.get(
        courses_url,
        headers=headers,
        params=params,
        timeout=10
    )

    if courses_response.status_code == 200:
        courses = courses_response.json()

        if courses:
            for course in courses:
                course_name = course.get("name")

                if course_name:
                    st.write(f"📘 {course_name}")
        else:
            st.info("No active courses found.")
    else:
        st.error(
            f"Could not load courses. "
            f"Status code: {courses_response.status_code}"
        )

except requests.RequestException as error:
    st.error(f"Unable to retrieve courses: {error}")

st.subheader("📝 Assignments")

all_assignments = []

for course in courses:
    course_id = course.get("id")
    course_name = course.get("name")

    if not course_id or not course_name:
        continue

    assignments_url = (
        f"{CANVAS_BASE_URL}/api/v1/courses/"
        f"{course_id}/assignments"
    )

    try:
        assignment_response = requests.get(
            assignments_url,
            headers=headers,
            params={"per_page": 100},
            timeout=10
        )

        if assignment_response.status_code == 200:
            for assignment in assignment_response.json():
                all_assignments.append({
                    "course": course_name,
                    "name": assignment.get("name"),
                    "due_at": assignment.get("due_at"),
                    "points": assignment.get("points_possible"),
                    "url": assignment.get("html_url")
                })

    except requests.RequestException:
        continue

if all_assignments:
    for assignment in all_assignments:
        st.write(f"### {assignment['name']}")
        st.write(f"📘 Course: {assignment['course']}")
        st.write(f"📅 Due: {assignment['due_at'] or 'No due date'}")
        st.write(f"⭐ Points: {assignment['points']}")
        
        if assignment["url"]:
            st.link_button(
                "Open in Canvas",
                assignment["url"]
            )

        st.divider()
else:
    st.info("No assignments found in the available courses.")