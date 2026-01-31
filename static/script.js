document.addEventListener('DOMContentLoaded', () => {
    const movieInput = document.getElementById('movieInput');
    const recommendBtn = document.getElementById('recommendBtn');
    const resultsDiv = document.getElementById('results');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');

    // Allow Enter key to submit
    movieInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            getRecommendations();
        }
    });

    recommendBtn.addEventListener('click', getRecommendations);

    async function getRecommendations() {
        const title = movieInput.value.trim();
        if (!title) return;

        // Reset UI
        resultsDiv.innerHTML = '';
        resultsDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        loadingDiv.classList.remove('hidden');

        try {
            // Fetch from API
            const response = await fetch(`/recommend?title=${encodeURIComponent(title)}`);
            const data = await response.json();

            loadingDiv.classList.add('hidden');

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to fetch recommendations');
            }

            if (data.data && data.data.length > 0) {
                displayResults(data.data);
            } else {
                showError(data.message || 'No recommendations found.');
            }

        } catch (err) {
            loadingDiv.classList.add('hidden');
            showError(err.message);
        }
    }

    function displayResults(movies) {
        resultsDiv.classList.remove('hidden');
        
        movies.forEach(movie => {
            const card = document.createElement('div');
            card.className = 'movie-card';
            
            // Format score to percentage
            const scorePercent = Math.round(movie.score * 100);
            
            card.innerHTML = `
                <span class="badge">${movie.source || 'Hybrid'}</span>
                <h3>${movie.title}</h3>
                <p class="genres">${movie.genres}</p>
                <div class="score">Match: ${scorePercent}%</div>
            `;
            
            resultsDiv.appendChild(card);
        });
    }

    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }
});
