document.addEventListener('DOMContentLoaded', async () => {
    const courseSelect = document.getElementById('completed-courses');
    const interestsInput = document.getElementById('interests');
    const numRecommendations = document.getElementById('num-recommendations');
    const numDisplay = document.getElementById('num-display');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');
    const resultsSection = document.getElementById('results-section');
    const recommendationsContainer = document.getElementById('recommendations-container');

    // Update slider value display
    numRecommendations.addEventListener('input', (e) => {
        numDisplay.textContent = e.target.value;
    });

    // Fetch available courses to populate the dropdown
    try {
        const response = await fetch('/api/courses');
        const data = await response.json();
        
        if (data.courses) {
            data.courses.forEach(course => {
                const option = document.createElement('option');
                option.value = course.course_code;
                option.textContent = `${course.course_code} - ${course.course_name} (${course.course_type})`;
                courseSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error fetching courses:', error);
    }

    // Handle form submission
    submitBtn.addEventListener('click', async () => {
        const interests = interestsInput.value.trim();
        
        if (!interests) {
            alert('Please provide your interests so the AI can tailor the recommendations.');
            interestsInput.focus();
            return;
        }

        // Get selected courses
        const selectedOptions = Array.from(courseSelect.selectedOptions);
        const completedCourses = selectedOptions.map(opt => opt.value);

        // UI Loading state
        btnText.classList.add('hidden');
        loader.classList.remove('hidden');
        submitBtn.disabled = true;
        resultsSection.classList.add('hidden');

        try {
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    completed_courses: completedCourses,
                    interests: interests,
                    top_n: parseInt(numRecommendations.value)
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to fetch recommendations');
            }

            renderRecommendations(data.recommendations || []);
            resultsSection.classList.remove('hidden');
            
            // Scroll to results
            resultsSection.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            // Restore UI state
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });

    function renderRecommendations(recs) {
        recommendationsContainer.innerHTML = '';
        
        if (recs.length === 0) {
            recommendationsContainer.innerHTML = '<p style="color: var(--text-muted)">No suitable elective recommendations found based on your criteria.</p>';
            return;
        }

        recs.forEach((rec, index) => {
            const delay = index * 0.15;
            const recEl = document.createElement('div');
            recEl.className = 'recommendation-item';
            recEl.style.animationDelay = `${delay}s`;
            
            recEl.innerHTML = `
                <div class="rec-header">
                    <div class="rec-title">⭐ ${rec.course_name}</div>
                    <div class="rec-code">${rec.course_code}</div>
                </div>
                <div class="rec-reason">${rec.reasoning}</div>
            `;
            
            recommendationsContainer.appendChild(recEl);
        });
    }
});
