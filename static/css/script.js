let chartInstance = null;

async function uploadData() {
    const fileInput = document.getElementById('csvFile');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const res = await fetch('/upload', { method: 'POST', body: formData });
    const data = await res.json();
    document.getElementById('uploadStatus').innerText = `Loaded ${data.rows} records successfully.`;
}

async function runPartition() {
    const threshold = document.getElementById('popThreshold').value;
    const res = await fetch('/partition', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ threshold })
    });
    const data = await res.json();
    document.getElementById('partitionResults').innerText = `Created ${data.length} spatial cells.`;
}

async function generateBoundaries() {
    const count = document.getElementById('constCount').value;
    const res = await fetch('/generate-boundaries', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ count })
    });
    const data = await res.json();
    
    renderMetrics(data.metrics);
    renderChart(data.results);
}

function renderMetrics(metrics) {
    const container = document.getElementById('metrics-view');
    container.innerHTML = `
        <div class="metric-card"><h3>Pop. Variance</h3><p>${metrics.pop_variance_pct}%</p></div>
        <div class="metric-card"><h3>Socio Parity</h3><p>${metrics.socio_parity_score}</p></div>
        <div class="metric-card"><h3>Constituencies</h3><p>${metrics.total_constituencies}</p></div>
    `;
}

function renderChart(results) {
    const ctx = document.getElementById('resultsChart').getContext('2d');
    if(chartInstance) chartInstance.destroy();
    
    chartInstance = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Constituency Mapping',
                data: results.map(r => ({ x: r.avg_lon, y: r.avg_lat, label: r.constituency_id })),
                backgroundColor: results.map(r => `hsl(${r.constituency_id * 60}, 70%, 50%)`)
            }]
        }
    });
}