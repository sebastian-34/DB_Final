const API_BASE_URL = '/api';

// Elements
const bassGrid = document.getElementById('bassGrid');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const clearBtn = document.getElementById('clearBtn');
const pickupFilter = document.getElementById('pickupFilter');
const stringsFilter = document.getElementById('stringsFilter');
const fretsFilter = document.getElementById('fretsFilter');
const minScoreFilter = document.getElementById('minScoreFilter');
const maxScoreFilter = document.getElementById('maxScoreFilter');
const loading = document.getElementById('loading');
const noResults = document.getElementById('noResults');
const statsText = document.getElementById('statsText');

// Event listeners
searchBtn.addEventListener('click', handleSearch);
clearBtn.addEventListener('click', handleClear);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSearch();
});
pickupFilter.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSearch();
});
minScoreFilter.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSearch();
});
maxScoreFilter.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSearch();
});

// Load all basses on page load
document.addEventListener('DOMContentLoaded', () => {
    loadAllBasses();
});

function buildFilterParams() {
    const params = new URLSearchParams();
    const name = searchInput.value.trim();
    const pickup = pickupFilter.value.trim();
    const strings = stringsFilter.value;
    const frets = fretsFilter.value;
    const minScore = minScoreFilter.value;
    const maxScore = maxScoreFilter.value;

    if (name) params.set('name', name);
    if (pickup) params.set('pickup', pickup);
    if (strings) params.set('strings', strings);
    if (frets) params.set('frets', frets);
    if (minScore) params.set('min_score', minScore);
    if (maxScore) params.set('max_score', maxScore);

    return params;
}

function getFilterSummary() {
    const parts = [];

    if (searchInput.value.trim()) parts.push(`name "${searchInput.value.trim()}"`);
    if (pickupFilter.value.trim()) parts.push(`pickup containing "${pickupFilter.value.trim()}"`);
    if (stringsFilter.value) parts.push(`${stringsFilter.value} strings`);
    if (fretsFilter.value) parts.push(`${fretsFilter.value} frets`);
    if (minScoreFilter.value) parts.push(`min score ${minScoreFilter.value}`);
    if (maxScoreFilter.value) parts.push(`max score ${maxScoreFilter.value}`);

    return parts.join(', ');
}

async function loadAllBasses() {
    try {
        showLoading(true);
        const params = buildFilterParams();
        const queryString = params.toString();
        const response = await fetch(`${API_BASE_URL}/basses${queryString ? `?${queryString}` : ''}`);
        const basses = await response.json();
        
        if (basses.length > 0) {
            displayBasses(basses);
            updateStats(basses.length, getFilterSummary() || null);
        } else {
            showNoResults();
            updateStats(0, getFilterSummary() || null);
        }
    } catch (error) {
        console.error('Error loading basses:', error);
        showError('Failed to load basses. Please try again.');
    } finally {
        showLoading(false);
    }
}

async function handleSearch() {
    loadAllBasses();
}

function handleClear() {
    searchInput.value = '';
    pickupFilter.value = '';
    stringsFilter.value = '';
    fretsFilter.value = '';
    minScoreFilter.value = '';
    maxScoreFilter.value = '';
    loading.style.display = 'none';
    noResults.style.display = 'none';
    loadAllBasses();
}

function displayBasses(basses) {
    bassGrid.innerHTML = '';
    noResults.style.display = 'none';

    basses.forEach(bass => {
        const card = createBassCard(bass);
        bassGrid.appendChild(card);
    });
}

function createBassCard(bass) {
    const card = document.createElement('div');
    card.className = 'bass-card';
    const scoreColor = getScoreColor(bass.score);

    card.innerHTML = `
        <div class="bass-image-container">
            ${bass.image ? 
                `<img class="bass-image" src="${bass.image}" alt="${escapeHtml(bass.name)}">` :
                `<div class="bass-image-placeholder">No image</div>`
            }
        </div>
        <div class="bass-info">
            <div class="bass-name">${escapeHtml(bass.name)}</div>
            
            <div class="bass-pickup">
                <strong>Pickup:</strong> ${escapeHtml(bass.pickup || 'N/A')}
            </div>

            <div class="bass-specs">
                <div class="spec-item">
                    <div class="spec-label">Strings</div>
                    <div class="spec-value">${bass.strings}</div>
                </div>
                <div class="spec-item">
                    <div class="spec-label">Frets</div>
                    <div class="spec-value">${bass.frets}</div>
                </div>
            </div>

            <div class="bass-footer">
                <div class="bass-price">$${bass.price.toFixed(2)}</div>
                <div class="bass-score">
                    <span class="score-badge" style="background: ${scoreColor};">Score: ${bass.score}</span>
                </div>
            </div>
        </div>
    `;

    const image = card.querySelector('.bass-image');
    if (image) {
        image.addEventListener('error', () => {
            const container = image.parentElement;
            container.innerHTML = '<div class="bass-image-placeholder">No image</div>';
        });
    }

    return card;
}

function getScoreColor(score) {
    const normalized = Math.max(0, Math.min(100, Number(score) || 0));
    const hue = (normalized / 100) * 120;
    return `hsl(${hue}, 70%, 42%)`;
}

function showLoading(show) {
    loading.style.display = show ? 'flex' : 'none';
}

function showNoResults() {
    noResults.style.display = 'block';
    bassGrid.innerHTML = '';
}

function updateStats(count, searchTerm = null) {
    if (searchTerm) {
        statsText.textContent = `Found ${count} bass${count !== 1 ? 'es' : ''} matching ${searchTerm}`;
    } else {
        statsText.textContent = `Showing ${count} bass${count !== 1 ? 'es' : ''} in database`;
    }
}

function showError(message) {
    alert(message);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
