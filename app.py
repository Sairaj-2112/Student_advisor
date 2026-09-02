import streamlit as st
import agent
import os

st.set_page_config(page_title="Academic Advisor Agent", page_icon="🎓", layout="centered")

st.title("🎓 Student Academic Advisor Agent")
st.markdown("Welcome! I am your AI-powered academic advisor. Tell me about the subjects you've completed and what you're interested in, and I'll recommend the best electives for you.")

# Check for API Key
if not os.environ.get("GEMINI_API_KEY"):
    st.warning("⚠️ GEMINI_API_KEY is not set in your environment. Please add it to your .env file.")

# Load courses for the multiselect
all_courses = agent.load_courses()
course_options = [c['course_code'] for c in all_courses]
course_descriptions = {c['course_code']: f"{c['course_code']} - {c['course_name']}" for c in all_courses}

# UI Layout
st.header("Your Profile")

completed_courses = st.multiselect(
    "Select Completed Subjects:",
    options=course_options,
    format_func=lambda x: course_descriptions[x],
    help="Select the subjects you have already passed."
)

interests = st.text_area(
    "What are your current academic or career interests?",
    placeholder="e.g., I'm really interested in building smart applications, analyzing data, and understanding user behavior.",
    help="Be as specific as possible to get better recommendations!"
)

num_recommendations = st.slider("How many recommendations do you want?", min_value=1, max_value=5, value=3)

# Action Button
if st.button("Get Elective Recommendations 🚀", type="primary"):
    if not interests.strip():
        st.error("Please provide your interests so I can tailor the recommendations.")
    else:
        with st.spinner("Analyzing your profile and finding the best electives..."):
            results = agent.recommend_electives(
                completed_courses=completed_courses,
                interests=interests,
                top_n=num_recommendations
            )
            
            if "error" in results:
                st.error(results["error"])
            else:
                st.success("Here are your personalized recommendations!")
                
                recommendations = results.get("recommendations", [])
                
                if not recommendations:
                    st.info("No suitable recommendations found based on your criteria.")
                
                for i, rec in enumerate(recommendations):
                    with st.expander(f"Top Choice {i+1}: {rec.get('course_code')} - {rec.get('course_name')}", expanded=True):
                        st.markdown(f"**Why this course?**")
                        st.write(rec.get('reasoning'))
                        
                        # Find the course details to show credits/domain
                        course_detail = next((c for c in all_courses if c['course_code'] == rec.get('course_code')), None)
                        if course_detail:
                            st.caption(f"Domain: {course_detail['domain']} | Credits: {course_detail['credits']}")

st.divider()
st.caption("Built with ❤️ using Streamlit & Google Gemini")
