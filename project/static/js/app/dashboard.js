/**
 * SelfLearn Dashboard Application
 * Main dashboard logic for monitoring and controlling the training process
 */

const API_BASE = '';
let refreshInterval = null;

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', () => {
    refreshData();
    // Auto-refresh every 5 seconds
    refreshInterval = setInterval(refreshData, 5000);
});

/**
 * Fetch and update all dashboard data
 */
async function refreshData() {
    try {
        await Promise.all([
            fetchStatus(),
            fetchResults()
        ]);
        hideAlert();
    } catch (error) {
        console.error('Failed to refresh data:', error);
        showAlert('Failed to connect to server. Please check if the API is running.', 'error');
    }
}

/**
 * Fetch current system status
 */
async function fetchStatus() {
    const response = await fetch(`${API_BASE}/status`);
    if (!response.ok) throw new Error('Status request failed');
    
    const data = await response.json();
    updateStatusUI(data.data);
}

/**
 * Update status UI elements
 */
function updateStatusUI(status) {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    if (status.is_running) {
        statusDot.className = 'status-dot running';
        statusText.textContent = 'Training in Progress';
    } else {
        statusDot.className = 'status-dot idle';
        statusText.textContent = 'Idle';
    }
    
    // Update stats
    document.getElementById('competitionsCount').textContent = 
        status.total_competitions || 0;
    document.getElementById('currentRound').textContent = 
        status.current_round || 0;
    document.getElementById('tasksCompleted').textContent = 
        status.tasks_completed || 0;
    
    // Update progress bar
    const progress = calculateProgress(status);
    document.getElementById('progressFill').style.width = `${progress}%`;
    document.getElementById('progressPercent').textContent = `${Math.round(progress)}%`;
}

/**
 * Calculate overall training progress percentage
 */
function calculateProgress(status) {
    if (!status.total_competitions || !status.rounds_per_competition) return 0;
    
    const totalRounds = status.total_competitions * status.rounds_per_competition;
    const completedRounds = status.completed_rounds || 0;
    
    return (completedRounds / totalRounds) * 100;
}

/**
 * Fetch competition results
 */
async function fetchResults() {
    const response = await fetch(`${API_BASE}/results`);
    if (!response.ok) throw new Error('Results request failed');
    
    const data = await response.json();
    updateResultsUI(data.data);
}

/**
 * Update results table UI
 */
function updateResultsUI(results) {
    const container = document.getElementById('resultsTable');
    
    if (!results.competitions || results.competitions.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No results yet. Start training to see progress.</p>';
        return;
    }
    
    // Get latest competition
    const latestCompetition = results.competitions[results.competitions.length - 1];
    const latestRound = latestCompetition.rounds[latestCompetition.rounds.length - 1];
    
    // Update accuracy display
    if (latestRound && latestRound.metrics) {
        const accuracy = (latestRound.metrics.accuracy * 100).toFixed(1);
        document.getElementById('accuracy').textContent = `${accuracy}%`;
    }
    
    // Build results table
    let html = `
        <table class="results-table">
            <thead>
                <tr>
                    <th>Competition</th>
                    <th>Round</th>
                    <th>Accuracy</th>
                    <th>F1-Score</th>
                    <th>Tasks</th>
                    <th>Completed</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    // Add rows for last 10 rounds
    const allRounds = [];
    results.competitions.forEach(comp => {
        comp.rounds.forEach(round => {
            allRounds.push({
                competition: comp.id,
                round: round.round_number,
                metrics: round.metrics,
                tasks: round.tasks_count,
                completed_at: round.completed_at
            });
        });
    });
    
    allRounds.slice(-10).reverse().forEach(row => {
        const accuracy = row.metrics ? (row.metrics.accuracy * 100).toFixed(1) : 'N/A';
        const f1 = row.metrics ? (row.metrics.f1_score * 100).toFixed(1) : 'N/A';
        const date = row.completed_at ? new Date(row.completed_at).toLocaleString() : 'In progress';
        
        html += `
            <tr>
                <td>#${row.competition}</td>
                <td>${row.round}</td>
                <td><strong>${accuracy}%</strong></td>
                <td>${f1}%</td>
                <td>${row.tasks}</td>
                <td style="color: #666; font-size: 0.9em;">${date}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

/**
 * Start training via API
 */
async function startTraining() {
    try {
        const response = await fetch(`${API_BASE}/train`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                competitions: 5,
                rounds: 10,
                tasks_per_round: 50,
                epochs: 10,
                batch_size: 32
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to start training');
        }
        
        showAlert('Training started successfully!', 'info');
        refreshData();
    } catch (error) {
        console.error('Failed to start training:', error);
        showAlert(`Failed to start training: ${error.message}`, 'error');
    }
}

/**
 * Stop training via API
 */
async function stopTraining() {
    if (!confirm('Are you sure you want to stop the current training?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/admin/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ confirm: true })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to stop training');
        }
        
        showAlert('Stop requested. Training will finish current task and stop.', 'info');
        refreshData();
    } catch (error) {
        console.error('Failed to stop training:', error);
        showAlert(`Failed to stop training: ${error.message}`, 'error');
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const container = document.getElementById('alertContainer');
    const alertClass = type === 'error' ? 'alert-error' : 'alert-info';
    
    container.innerHTML = `
        <div class="alert ${alertClass}">
            ${message}
        </div>
    `;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

/**
 * Hide alert message
 */
function hideAlert() {
    document.getElementById('alertContainer').innerHTML = '';
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}
