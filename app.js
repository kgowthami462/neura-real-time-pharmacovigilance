// Auth Logic
if (!localStorage.getItem('hp_token')) {
    window.location.href = '/static/index.html';
}

function getAuthHeaders() {
    return {
        'Authorization': `Bearer ${localStorage.getItem('hp_token')}`,
        'Content-Type': 'application/json'
    };
}

function logout() {
    localStorage.removeItem('hp_token');
    window.location.href = '/static/index.html';
}

// Toast Notification System
function showToast(message, type = "success") {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    let icon = type === 'success' ? '✅' : '❌';
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Counter Animation Function
function animateCounter(id, start, end, duration, isFloat = false) {
    let obj = document.getElementById(id);
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        let value = progress * (end - start) + start;
        if(isFloat) {
            obj.innerHTML = value.toFixed(2);
        } else {
            obj.innerHTML = Math.floor(value);
        }
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Navigation
function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
    
    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}

// Fetch Projects
async function fetchProjects() {
    try {
        const res = await fetch('/projects/', { headers: getAuthHeaders() });
        if (res.status === 401) return logout();
        const projects = await res.json();
    const select = document.getElementById('source-project');
    select.innerHTML = '<option value="" disabled selected>Select Project</option>';
    projects.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = p.name;
        select.appendChild(opt);
    });
    } catch(e) { console.error("Error fetching projects", e); }
}

// Fetch Sources for simulation dropdown
async function fetchSourcesForSimulation() {
    try {
        const projRes = await fetch('/projects/', { headers: getAuthHeaders() });
        if (projRes.status === 401) return logout();
        const projects = await projRes.json();
        const select = document.getElementById('trigger-source');
    select.innerHTML = '';
    
    for (const p of projects) {
        const sourceRes = await fetch(`/sources/${p.id}`, { headers: getAuthHeaders() });
        const sources = await sourceRes.json();
        sources.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.id;
            opt.textContent = `${p.name} - ${s.type} (${s.url})`;
            select.appendChild(opt);
        });
    }
    } catch(e) { console.error("Error fetching sources", e); }
}

// Create Project
document.getElementById('project-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="animate-spin">↻</span> Saving...';
    btn.disabled = true;
    
    const payload = {
        name: document.getElementById('proj-name').value,
        description: document.getElementById('proj-desc').value,
        keywords: document.getElementById('proj-keywords').value
    };
    
    try {
        const res = await fetch('/projects/', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });
        if(res.status === 401) return logout();
        showToast('Project Created Successfully!', 'success');
        e.target.reset();
        fetchProjects();
    } catch(err) {
        showToast('Failed to create project', 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
});

// Add Source
document.getElementById('source-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="animate-spin">↻</span> Saving...';
    btn.disabled = true;
    
    const payload = {
        project_id: parseInt(document.getElementById('source-project').value),
        type: document.getElementById('source-type').value,
        url: document.getElementById('source-url').value,
        latency_metric: document.getElementById('source-latency').value
    };
    
    try {
        const res = await fetch('/sources/', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });
        if(res.status === 401) return logout();
        showToast('Source Added Successfully!', 'success');
        e.target.reset();
        fetchSourcesForSimulation();
    } catch(err) {
        showToast('Failed to add source', 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
});

// Trigger Crawl
async function triggerCrawl() {
    const sourceId = document.getElementById('trigger-source').value;
    
    if (!sourceId) {
        showToast("Please select a source first!", "error");
        return;
    }
    
    const payload = {};
    
    const btn = document.querySelector('.warning-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="animate-spin">↻</span> Processing...';
    btn.disabled = true;
    
    try {
        const res = await fetch(`/trigger-crawl/${sourceId}`, { 
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        
        if(!res.ok) throw new Error(data.detail || "Failed to crawl source");
        
        showToast("Crawl Triggered! AI Analysis complete.", "success");
        fetchSignals();
        showTab('dashboard');
    } catch(e) {
        showToast("Error: " + e.message, "error");
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Agentic Onboarding
async function runAgenticOnboarding() {
    const url = document.getElementById('agentic-url').value;
    
    if(!url) {
        showToast("A target URL is required.", "error");
        return;
    }
    
    const btn = document.getElementById('agentic-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="animate-spin">↻</span> Analyzing DOM...';
    btn.disabled = true;
    
    try {
        const res = await fetch('/agentic-onboard', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ url: url })
        });
        
        const data = await res.json();
        
        if(!res.ok) {
            throw new Error(data.detail || "Analysis failed");
        }
        
        showToast("Agent successfully mapped source!", "success");
        document.getElementById('agentic-result').style.display = 'block';
        document.getElementById('agentic-json').textContent = JSON.stringify(data.configuration, null, 2);
        
    } catch(err) {
        showToast("Error: " + err.message, "error");
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Fetch Signals
async function fetchSignals() {
    try {
        const res = await fetch('/signals/', { headers: getAuthHeaders() });
        if (res.status === 401) return logout();
        const signals = await res.json();
    
    const container = document.getElementById('signal-list');
    const emptyState = document.getElementById('empty-signals-state');
    
    if (signals.length === 0) {
        emptyState.style.display = 'block';
        container.style.display = 'none';
    } else {
        emptyState.style.display = 'none';
        container.style.display = 'block';
    }
    
    container.innerHTML = '';
    
    let adverseCount = 0;
    let totalSentiment = 0;
    
    signals.reverse().forEach((s, index) => {
        if(s.safety_issue) adverseCount++;
        totalSentiment += s.sentiment;
        
        const div = document.createElement('div');
        div.className = `signal-item new-entry ${s.safety_issue ? 'danger' : 'safe'}`;
        div.style.animationDelay = `${index * 0.1}s`;
        
        div.innerHTML = `
            <div class="badges">
                <span class="badge ${s.safety_issue ? 'danger' : 'neutral'}">
                    ${s.safety_issue ? '🚨 Adverse Event Detected' : '✅ Safe'}
                </span>
                <span class="badge neutral">Sentiment: ${s.sentiment}</span>
                <span class="badge neutral">Entities: ${s.entities}</span>
            </div>
            <p>"${s.content}"</p>
            <div class="explanation">AI Analysis: ${s.explanation}</div>
            <small style="color: #64748b; margin-top: 10px; display: block;">Source: ${s.url} | Time: ${new Date(s.timestamp).toLocaleString()}</small>
        `;
        container.appendChild(div);
    });
    
    const currentTotal = parseInt(document.getElementById('total-signals').textContent) || 0;
    const currentAdverse = parseInt(document.getElementById('total-adverse').textContent) || 0;
    const currentSent = parseFloat(document.getElementById('avg-sentiment').textContent) || 0.0;
    
    const finalSent = signals.length ? (totalSentiment/signals.length) : 0.0;
    
    animateCounter('total-signals', currentTotal, signals.length, 1000, false);
    animateCounter('total-adverse', currentAdverse, adverseCount, 1000, false);
    animateCounter('avg-sentiment', currentSent, finalSent, 1000, true);
    } catch(e) { console.error("Error fetching signals", e); }
}

// Refresh Handler
async function handleRefresh() {
    const icon = document.getElementById('refresh-icon');
    icon.classList.add('animate-spin');
    
    await fetchSignals();
    
    setTimeout(() => {
        icon.classList.remove('animate-spin');
        showToast("Dashboard synchronized.", "success");
    }, 500);
}

// Init
document.addEventListener("DOMContentLoaded", () => {
    if(localStorage.getItem('hp_token')) {
        setInterval(fetchSignals, 5000);
        fetchProjects();
        fetchSourcesForSimulation();
        fetchSignals();
    }
});
