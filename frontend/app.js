/* ══════════════════════════════════════════════
   T14 AI — SOC Analyst Assistant
   Frontend Application Logic
   ══════════════════════════════════════════════ */

const API_BASE = 'http://localhost:8000';

// ── State ─────────────────────────────────────
let currentView = 'chat';
let isLoading = false;

// ── Initialization ────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupDragAndDrop();
});

// ── View Switching ────────────────────────────
function switchView(view) {
    currentView = view;

    document.querySelectorAll('.view-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    document.getElementById(`view-${view}`).classList.add('active');

    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    const navItem = document.querySelector(`[data-view="${view}"]`);
    if (navItem) navItem.classList.add('active');

    const titles = {
        chat: 'Security Chat',
        analyze: 'Log Analysis',
        incident: 'Incident Summary',
        upload: 'Upload Documents'
    };
    document.getElementById('viewTitle').textContent = titles[view] || 'T14 AI';

    // Close mobile sidebar
    closeSidebar();
}

// ── Sidebar Toggle (Mobile) ──────────────────
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    sidebar.classList.toggle('open');
    overlay.classList.toggle('visible');
}

function closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebarOverlay').classList.remove('visible');
}

// ── Health Check ──────────────────────────────
async function checkHealth() {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');

    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();

        dot.className = 'status-dot';
        text.textContent = `${data.model} · ${data.rag_documents} docs`;

        const badge = document.getElementById('ragBadge');
        badge.textContent = `RAG: ${data.rag_documents} docs`;
    } catch (err) {
        dot.className = 'status-dot offline';
        text.textContent = 'Service Offline';
    }
}

// ── Chat Functions ────────────────────────────
function handleChatKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
    }
}

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function sendQuickAction(question) {
    document.getElementById('chatInput').value = question;
    sendChatMessage();
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const question = input.value.trim();
    if (!question || isLoading) return;

    // Hide welcome message
    const welcome = document.getElementById('welcomeMessage');
    if (welcome) welcome.style.display = 'none';

    // Add user message
    addMessage('user', question);
    input.value = '';
    input.style.height = 'auto';

    // Show loading
    isLoading = true;
    updateSendButton(true);
    const loadingId = addLoadingMessage();

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });

        removeLoadingMessage(loadingId);

        if (!response.ok) {
            const err = await response.json();
            addMessage('assistant', `⚠️ Error: ${err.detail || 'Request failed'}`, []);
            return;
        }

        const data = await response.json();
        addMessage('assistant', data.answer, data.sources || []);

    } catch (err) {
        removeLoadingMessage(loadingId);
        addMessage('assistant', `⚠️ Could not connect to the server. Make sure all services are running.\n\n\`${err.message}\``, []);
    } finally {
        isLoading = false;
        updateSendButton(false);
    }
}

function addMessage(role, content, sources = []) {
    const container = document.getElementById('chatMessages');

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🛡️';

    const body = document.createElement('div');
    body.className = 'message-body';
    body.innerHTML = formatMarkdown(content);

    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'message-sources';
        sources.forEach(src => {
            const tag = document.createElement('span');
            tag.className = 'source-tag';
            tag.textContent = `📄 ${src}`;
            sourcesDiv.appendChild(tag);
        });
        body.appendChild(sourcesDiv);
    }

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(body);
    container.appendChild(msgDiv);

    container.scrollTop = container.scrollHeight;
}

function addLoadingMessage() {
    const container = document.getElementById('chatMessages');
    const id = 'loading-' + Date.now();

    const msgDiv = document.createElement('div');
    msgDiv.className = 'message assistant';
    msgDiv.id = id;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🛡️';

    const body = document.createElement('div');
    body.className = 'message-body';
    body.innerHTML = '<div class="loading-dots"><span></span><span></span><span></span></div>';

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(body);
    container.appendChild(msgDiv);

    container.scrollTop = container.scrollHeight;
    return id;
}

function removeLoadingMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function updateSendButton(loading) {
    const btn = document.getElementById('sendBtn');
    btn.disabled = loading;
    btn.textContent = loading ? '⏳' : '➤';
}

function clearChat() {
    const container = document.getElementById('chatMessages');
    container.innerHTML = '';

    // Show welcome again
    container.innerHTML = `
        <div class="welcome-message" id="welcomeMessage">
            <div class="welcome-icon">🛡️</div>
            <h2>T14 AI Security Assistant</h2>
            <p>Ask me anything about cybersecurity — from MITRE ATT&CK techniques to incident response procedures.</p>
            <div class="quick-actions">
                <button class="quick-action" onclick="sendQuickAction('What is Pass-the-Hash and how do I detect it?')">
                    <span class="qa-icon">🔑</span>
                    <span>Explain Pass-the-Hash attack</span>
                </button>
                <button class="quick-action" onclick="sendQuickAction('How do I investigate suspicious PowerShell activity?')">
                    <span class="qa-icon">⚡</span>
                    <span>Investigate PowerShell abuse</span>
                </button>
                <button class="quick-action" onclick="sendQuickAction('What are the steps for incident response?')">
                    <span class="qa-icon">📋</span>
                    <span>Incident response steps</span>
                </button>
                <button class="quick-action" onclick="sendQuickAction('Explain MITRE ATT&CK T1110 brute force technique')">
                    <span class="qa-icon">🎯</span>
                    <span>MITRE T1110 Brute Force</span>
                </button>
            </div>
        </div>`;
}

// ── Log Analysis ──────────────────────────────
async function analyzeLog() {
    const input = document.getElementById('logInput');
    const log = input.value.trim();
    if (!log || isLoading) return;

    const btn = document.getElementById('analyzeBtn');
    btn.disabled = true;
    btn.innerHTML = '<span>⏳</span> Analyzing...';
    isLoading = true;

    const resultsDiv = document.getElementById('analysisResults');

    try {
        const response = await fetch(`${API_BASE}/analyze-log`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ log })
        });

        if (!response.ok) {
            const err = await response.json();
            showError(resultsDiv, err.detail || 'Analysis failed');
            return;
        }

        const data = await response.json();
        renderLogAnalysis(resultsDiv, data);

    } catch (err) {
        showError(resultsDiv, `Connection error: ${err.message}`);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>🔍</span> Analyze Log';
        isLoading = false;
    }
}

function renderLogAnalysis(container, data) {
    const severityClass = data.severity.toLowerCase();

    let iocsHtml = '';
    if (data.iocs && data.iocs.length > 0) {
        iocsHtml = `
            <div class="result-card" style="grid-column: 1 / -1;">
                <h4>🔗 Indicators of Compromise</h4>
                <ul class="ioc-list">
                    ${data.iocs.map(ioc => `
                        <li>
                            <span class="ioc-type">${ioc.type}</span>
                            <span>${escapeHtml(ioc.value)}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>`;
    }

    let recsHtml = '';
    if (data.recommendations && data.recommendations.length > 0) {
        recsHtml = `
            <div class="result-card" style="grid-column: 1 / -1;">
                <h4>✅ Recommendations</h4>
                <ul class="rec-list">
                    ${data.recommendations.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
                </ul>
            </div>`;
    }

    container.innerHTML = `
        <div class="result-header">
            <h3 style="font-size:18px; font-weight:600;">Analysis Results</h3>
            <span class="severity-badge ${severityClass}">${data.severity}</span>
        </div>
        <div class="result-cards">
            <div class="result-card">
                <h4>⚔️ Attack Type</h4>
                <div class="value">${escapeHtml(data.attack_type)}</div>
            </div>
            <div class="result-card">
                <h4>🎯 MITRE ATT&CK</h4>
                <div class="value">${escapeHtml(data.mitre_technique)}</div>
                <div class="sub-value">${escapeHtml(data.mitre_name)}</div>
            </div>
            ${iocsHtml}
            ${recsHtml}
        </div>
        <div class="summary-text">${escapeHtml(data.summary)}</div>
    `;

    container.classList.add('visible');
}

// ── Incident Summary ──────────────────────────
async function generateIncidentSummary() {
    const input = document.getElementById('incidentInput');
    const text = input.value.trim();
    if (!text || isLoading) return;

    const events = text.split('\n').filter(line => line.trim());
    if (events.length === 0) return;

    const btn = document.getElementById('incidentBtn');
    btn.disabled = true;
    btn.innerHTML = '<span>⏳</span> Generating...';
    isLoading = true;

    const resultsDiv = document.getElementById('incidentResults');

    try {
        const response = await fetch(`${API_BASE}/incident-summary`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ events })
        });

        if (!response.ok) {
            const err = await response.json();
            showError(resultsDiv, err.detail || 'Summary generation failed');
            return;
        }

        const data = await response.json();
        renderIncidentSummary(resultsDiv, data);

    } catch (err) {
        showError(resultsDiv, `Connection error: ${err.message}`);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>📋</span> Generate Summary';
        isLoading = false;
    }
}

function renderIncidentSummary(container, data) {
    const severityClass = data.severity.toLowerCase();

    let assetsHtml = '';
    if (data.affected_assets && data.affected_assets.length > 0) {
        assetsHtml = `
            <div class="result-card">
                <h4>🖥️ Affected Assets</h4>
                <ul class="rec-list">
                    ${data.affected_assets.map(a => `<li>${escapeHtml(a)}</li>`).join('')}
                </ul>
            </div>`;
    }

    let indicatorsHtml = '';
    if (data.indicators && data.indicators.length > 0) {
        indicatorsHtml = `
            <div class="result-card">
                <h4>🔗 Indicators of Compromise</h4>
                <ul class="ioc-list">
                    ${data.indicators.map(ioc => `
                        <li>
                            <span class="ioc-type">${ioc.type}</span>
                            <span>${escapeHtml(ioc.value)}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>`;
    }

    let timelineHtml = '';
    if (data.timeline && data.timeline.length > 0) {
        timelineHtml = `
            <div class="result-card" style="grid-column: 1 / -1;">
                <h4>🕐 Timeline</h4>
                <ul class="rec-list">
                    ${data.timeline.map(t => `<li>${escapeHtml(t)}</li>`).join('')}
                </ul>
            </div>`;
    }

    let recsHtml = '';
    if (data.recommendations && data.recommendations.length > 0) {
        recsHtml = `
            <div class="result-card" style="grid-column: 1 / -1;">
                <h4>✅ Recommendations</h4>
                <ul class="rec-list">
                    ${data.recommendations.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
                </ul>
            </div>`;
    }

    container.innerHTML = `
        <div class="result-header">
            <h3 style="font-size:18px; font-weight:600;">Incident Summary</h3>
            <span class="severity-badge ${severityClass}">${data.severity}</span>
        </div>
        <div class="summary-text">${escapeHtml(data.executive_summary)}</div>
        <div class="result-cards">
            ${assetsHtml}
            ${indicatorsHtml}
            ${timelineHtml}
            ${recsHtml}
        </div>
    `;

    container.classList.add('visible');
}

// ── File Upload ───────────────────────────────
function setupDragAndDrop() {
    const zone = document.getElementById('uploadZone');
    if (!zone) return;

    ['dragenter', 'dragover'].forEach(evt => {
        zone.addEventListener(evt, e => {
            e.preventDefault();
            zone.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(evt => {
        zone.addEventListener(evt, e => {
            e.preventDefault();
            zone.classList.remove('drag-over');
        });
    });

    zone.addEventListener('drop', e => {
        const files = e.dataTransfer.files;
        if (files.length > 0) handleFileUpload(files[0]);
    });
}

function uploadFile(input) {
    if (input.files.length > 0) {
        handleFileUpload(input.files[0]);
    }
}

async function handleFileUpload(file) {
    const resultDiv = document.getElementById('uploadResult');

    const formData = new FormData();
    formData.append('file', file);

    resultDiv.innerHTML = `
        <div style="display:flex;align-items:center;gap:12px;">
            <div class="loading-dots"><span></span><span></span><span></span></div>
            <span style="color:var(--text-secondary);">Uploading and processing <strong>${escapeHtml(file.name)}</strong>...</span>
        </div>`;
    resultDiv.className = 'upload-result visible';

    try {
        const response = await fetch(`${API_BASE}/upload-document`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const err = await response.json();
            resultDiv.innerHTML = `
                <div style="display:flex;align-items:center;gap:10px;color:#f87171;">
                    <span style="font-size:20px;">❌</span>
                    <div>
                        <strong>Upload Failed</strong>
                        <p style="margin:4px 0 0;font-size:13px;color:var(--text-secondary);">${escapeHtml(err.detail || 'Unknown error')}</p>
                    </div>
                </div>`;
            resultDiv.className = 'upload-result visible error';
            return;
        }

        const data = await response.json();
        resultDiv.innerHTML = `
            <div style="display:flex;align-items:center;gap:10px;color:#34d399;">
                <span style="font-size:20px;">✅</span>
                <div>
                    <strong>${escapeHtml(data.filename)}</strong> ingested successfully
                    <p style="margin:4px 0 0;font-size:13px;color:var(--text-secondary);">
                        ${data.chunks_created} chunks created and embedded in the knowledge base.
                    </p>
                </div>
            </div>`;
        resultDiv.className = 'upload-result visible success';

        // Refresh health to update doc count
        checkHealth();

    } catch (err) {
        resultDiv.innerHTML = `
            <div style="display:flex;align-items:center;gap:10px;color:#f87171;">
                <span style="font-size:20px;">❌</span>
                <div>
                    <strong>Connection Error</strong>
                    <p style="margin:4px 0 0;font-size:13px;color:var(--text-secondary);">${escapeHtml(err.message)}</p>
                </div>
            </div>`;
        resultDiv.className = 'upload-result visible error';
    }
}

// ── Utilities ─────────────────────────────────
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatMarkdown(text) {
    if (!text) return '';

    let html = escapeHtml(text);

    // Code blocks
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');

    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Bold
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Italic
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Headers
    html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>');
    html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>');

    // Bullet lists
    html = html.replace(/^[-•] (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

    // Numbered lists
    html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

    // Line breaks
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');

    // Wrap in paragraph
    html = '<p>' + html + '</p>';

    // Clean up empty paragraphs
    html = html.replace(/<p>\s*<\/p>/g, '');

    return html;
}

function showError(container, message) {
    container.innerHTML = `
        <div class="result-card" style="border-color: rgba(239,68,68,0.3);">
            <h4 style="color:#f87171;">⚠️ Error</h4>
            <p style="color:var(--text-secondary);font-size:14px;">${escapeHtml(message)}</p>
        </div>
    `;
    container.classList.add('visible');
}
