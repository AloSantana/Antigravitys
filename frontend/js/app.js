// Configuration detection - will be populated from /config endpoint
        let backendConfig = null;
        
        // Initial fallback URLs (will be replaced by config)
        let API_BASE = window.location.protocol === 'file:' 
            ? 'http://localhost:8000' 
            : window.location.origin;
        let WS_BASE = window.location.protocol === 'file:' 
            ? 'ws://localhost:8000/ws' 
            : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;
        
        // Fetch backend configuration and update URLs
        async function fetchBackendConfig() {
            try {
                const configUrls = [];
                
                if (window.location.protocol === 'file:') {
                    configUrls.push('http://localhost:8000/config');
                } else {
                    configUrls.push(`${window.location.origin}/config`);
                    if (window.location.port && window.location.port !== '8000') {
                        configUrls.push(`${window.location.protocol}//${window.location.hostname}:8000/config`);
                    }
                    if (window.location.port && window.location.port !== '3000') {
                        configUrls.push(`${window.location.protocol}//${window.location.hostname}:3000/config`);
                    }
                }
                
                for (const configUrl of configUrls) {
                    
                    try {
                        const response = await fetch(configUrl, {
                            method: 'GET',
                            headers: { 'Accept': 'application/json' }
                        });
                        
                        if (response.ok) {
                            backendConfig = await response.json();
                            console.log('Backend configuration loaded:', backendConfig);
                            
                            // Update API and WebSocket base URLs
                            // Only override with config URLs if they're not localhost 
                            // OR if we're actually on localhost — prevents breaking remote access
                            const configBackend = backendConfig.urls.backend || '';
                            const configWs = backendConfig.urls.websocket || '';
                            const isLocalhost = ['localhost', '127.0.0.1'].includes(window.location.hostname);
                            const configPointsToLocalhost = configBackend.includes('localhost') || configBackend.includes('127.0.0.1');
                            
                            if (!configPointsToLocalhost || isLocalhost) {
                                // Config returns real URLs (ngrok, external host) OR we're on localhost — use them
                                API_BASE = configBackend;
                                WS_BASE = configWs;
                            } else {
                                // Config returns localhost but we're remote — keep window.location-based URLs
                                console.log('Config returned localhost URLs but accessing remotely — keeping window.location-based URLs');
                            }
                            
                            console.log('API Base:', API_BASE);
                            console.log('WebSocket Base:', WS_BASE);
                            
                            // Update connection info display
                            updateConnectionInfo();
                            return true;
                        }
                    } catch (e) {
                        // Try next port
                        continue;
                    }
                }
                
                console.warn('Could not fetch backend config, using fallback URLs');
                return false;
            } catch (error) {
                console.error('Error fetching backend config:', error);
                return false;
            }
        }
        
        // Update connection info in UI
        function updateConnectionInfo() {
            if (backendConfig) {
                const modeText = backendConfig.mode === 'remote' ? '🌐 Remote' : '💻 Local';
                const hostText = backendConfig.external_host || 'localhost';
                
                // Add connection info to header if it doesn't exist
                let connectionInfo = document.getElementById('connectionInfo');
                if (!connectionInfo) {
                    connectionInfo = document.createElement('div');
                    connectionInfo.id = 'connectionInfo';
                    connectionInfo.style.cssText = 'font-size: 0.75rem; color: var(--text-secondary); margin-left: 12px;';
                    const statusBadges = document.querySelector('.status-badges');
                    if (statusBadges) {
                        statusBadges.insertBefore(connectionInfo, statusBadges.firstChild);
                    }
                }
                connectionInfo.textContent = `${modeText} Mode | ${hostText}`;
            }
        }
        
        // WebSocket connection
        let ws;
        let selectedAgent = "full-stack-developer";
        let messageCount = 1;
        let editor;
        
        // Reconnection state
        let reconnectAttempts = 0;
        let reconnectTimeout = null;
        const INITIAL_RECONNECT_DELAY = 1000; // 1 second
        const MAX_RECONNECT_DELAY = 30000; // 30 seconds
        const RECONNECT_MULTIPLIER = 1.5;
        const JITTER_PERCENTAGE = 0.2; // ±20%
        
        /**
         * Calculate reconnection delay with exponential backoff and jitter
         * Formula: delay = min(initialDelay * (multiplier ^ attempts), maxDelay)
         * Jitter: actualDelay = delay * (1 + random(-0.2, 0.2))
         */
        function calculateReconnectDelay() {
            // Exponential backoff
            const exponentialDelay = INITIAL_RECONNECT_DELAY * Math.pow(RECONNECT_MULTIPLIER, reconnectAttempts);
            const cappedDelay = Math.min(exponentialDelay, MAX_RECONNECT_DELAY);
            
            // Add jitter (±20%)
            const jitter = (Math.random() * 2 - 1) * JITTER_PERCENTAGE;
            const delayWithJitter = cappedDelay * (1 + jitter);
            
            return Math.max(delayWithJitter, INITIAL_RECONNECT_DELAY);
        }
        
        function connectWebSocket() {
            ws = new WebSocket(WS_BASE);
            
            ws.onopen = () => {
                console.log('WebSocket connected to:', WS_BASE);
                // Reset reconnection state on successful connection
                reconnectAttempts = 0;
                if (reconnectTimeout) {
                    clearTimeout(reconnectTimeout);
                    reconnectTimeout = null;
                }
                updateConnectionStatus(true);
            };
            
            ws.onclose = () => {
                console.log('WebSocket disconnected');
                reconnectAttempts++;
                updateConnectionStatus(false);
                
                // Calculate delay with exponential backoff and jitter
                const delay = calculateReconnectDelay();
                console.log(`Reconnecting in ${(delay / 1000).toFixed(2)}s (attempt ${reconnectAttempts})...`);
                
                // Attempt to reconnect with exponential backoff
                reconnectTimeout = setTimeout(connectWebSocket, delay);
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                updateConnectionStatus(false);
            };
            
            ws.onmessage = (event) => {
                console.log('Message from server:', event.data);
                try {
                    const parsed = JSON.parse(event.data);
                    const thinking = document.getElementById("thinking");
                    if (thinking) thinking.remove();
                    if (parsed.error) {
                        addMessage(`❌ ${parsed.error}${parsed.details ? ': ' + parsed.details : ''}`, "system");
                    } else {
                        addMessage(parsed.response || parsed.text || parsed.content || event.data, "agent");
                    }
                } catch (e) {
                    const thinking = document.getElementById("thinking");
                    if (thinking) thinking.remove();
                    addMessage(event.data, "agent");
                }
            };
        }
        
        function updateConnectionStatus(connected) {
            const statusEl = document.querySelector('.status-dot');
            const statusBadge = document.getElementById('connectionStatus');
            const statusText = statusBadge ? statusBadge.querySelector('span:last-child') : null;
            
            if (statusEl) {
                statusEl.style.background = connected ? 'var(--success)' : 'var(--error)';
            }
            
            if (statusBadge) {
                if (connected) {
                    statusBadge.className = 'badge online';
                    if (statusText) {
                        statusText.textContent = 'Online';
                    }
                } else {
                    statusBadge.className = 'badge offline';
                    if (statusText && reconnectAttempts > 0) {
                        statusText.textContent = `Reconnecting... (attempt ${reconnectAttempts})`;
                    } else if (statusText) {
                        statusText.textContent = 'Offline';
                    }
                }
            }
        }

        // Initialize CodeMirror
        document.addEventListener('DOMContentLoaded', async function() {
            // Fetch backend configuration first
            await fetchBackendConfig();
            
            // Connect WebSocket
            connectWebSocket();
            
            editor = CodeMirror.fromTextArea(document.getElementById('codeEditor'), {
                mode: 'python',
                theme: 'monokai',
                lineNumbers: true,
                lineWrapping: true,
                indentUnit: 4,
                tabSize: 4,
                indentWithTabs: false
            });
            
            // Initial file fetch
            fetchFiles();
        });

        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', function() {
                const panelId = this.getAttribute('data-panel');
                switchPanel(panelId);
            });
        });

        function switchPanel(panelId) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.content-panel').forEach(p => p.classList.remove('active'));
            
            document.querySelector(`[data-panel="${panelId}"]`).classList.add('active');
            document.getElementById(`${panelId}-panel`).classList.add('active');
        }

        // Agent selection
        document.querySelectorAll('.agent-card').forEach(card => {
            card.addEventListener('click', function() {
                document.querySelectorAll('.agent-card').forEach(c => c.classList.remove('selected'));
                this.classList.add('selected');
                selectedAgent = this.getAttribute('data-agent');
                document.getElementById('selectedAgentLabel').textContent = `@${selectedAgent}`;
            });
        });

        // Chat functions
        function addMessage(text, sender) {
            const chat = document.getElementById('chat');
            const msg = document.createElement("div");
            msg.className = `message ${sender}`;

            let source = sender === "user" ? "You" : (sender === "system" ? "System" : selectedAgent);
            
            if (sender === "agent") {
                msg.innerHTML = `<span class="message-source">${source}</span>${text}`;
            } else if (sender === "system") {
                msg.innerHTML = text;
            } else {
                msg.innerHTML = `<span class="message-source">${source}</span>${text}`;
            }

            // Add "Handoff to Jules" button after each code block in agent messages
            if (sender === "agent") {
                msg.querySelectorAll("pre, code:not(pre > code)").forEach(function(codeEl) {
                    const btn = document.createElement("button");
                    btn.className = "handoff-btn";
                    btn.title = "Send this code to Jules for review";
                    btn.textContent = "⭐ Handoff to Jules";
                    btn.onclick = function() { handoffToJules(codeEl.textContent); };
                    codeEl.insertAdjacentElement("afterend", btn);
                });
            }
            
            chat.appendChild(msg);
            chat.scrollTop = chat.scrollHeight;
            
            messageCount++;
            document.getElementById('messagesCount').textContent = messageCount;
        }

        async function handoffToJules(codeSnippet) {
            addMessage("⭐ Handing off to Jules for code review...", "system");
            try {
                const res = await fetch(`${API_BASE}/api/agents/handoff`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        from_agent: selectedAgent,
                        to_agent: "jules",
                        context: { code: codeSnippet },
                        reason: "code review requested"
                    })
                });
                const data = await res.json();
                addMessage(data.response || data.message || JSON.stringify(data), "agent");
            } catch (err) {
                addMessage(`❌ Failed to handoff code to Jules: ${err}`, "system");
            }
        }

        function showThinking() {
            const chat = document.getElementById('chat');
            const msg = document.createElement("div");
            msg.id = "thinking";
            msg.className = "message agent";
            msg.innerHTML = `<span class="message-source">${selectedAgent}</span><span class="thinking-dots">Thinking</span>`;
            chat.appendChild(msg);
            chat.scrollTop = chat.scrollHeight;
        }

        function sendMessage() {
            const input = document.getElementById("input");
            const text = input.value.trim();
            if (!text) return;

            const dualAgentToggle = document.getElementById("dualAgentToggle");

            if (dualAgentToggle && dualAgentToggle.checked) {
                // Dual-Agent Mode: collect partners and collaboration mode
                const partnerCheckboxes = document.querySelectorAll(".partner-checkbox:checked");
                const partners = Array.from(partnerCheckboxes).map(cb => cb.value);
                const agents = [selectedAgent, ...partners];
                const modeRadio = document.querySelector("input[name='collab-mode']:checked");
                const mode = modeRadio ? modeRadio.value : "sequential";

                addMessage(text, "user");
                input.value = "";

                const thinkingMsg = document.createElement("div");
                thinkingMsg.id = "thinking";
                thinkingMsg.className = "message agent";
                thinkingMsg.innerHTML = `<span class="message-source">🤝 Dual-Agent (${agents.join(", ")})</span><span class="thinking-dots">Thinking</span>`;
                document.getElementById("chat").appendChild(thinkingMsg);
                document.getElementById("chat").scrollTop = document.getElementById("chat").scrollHeight;

                fetch(`${API_BASE}/api/agents/collaborate`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ request: text, agents: agents, mode: mode })
                })
                .then(res => res.json())
                .then(data => {
                    const thinking = document.getElementById("thinking");
                    if (thinking) thinking.remove();

                    const chat = document.getElementById("chat");
                    const wrapper = document.createElement("div");
                    wrapper.className = "message agent";

                    const results = data.results || {};
                    if (Object.keys(results).length === 0) {
                        wrapper.innerHTML = `<span class="message-source">🤝 Dual-Agent</span>${data.response || JSON.stringify(data)}`;
                    } else {
                        let html = `<span class="message-source">🤝 Dual-Agent Results (${mode})</span>`;
                        for (const [agentName, agentResult] of Object.entries(results)) {
                            const resultText = typeof agentResult === "string"
                                ? agentResult
                                : (agentResult.response || agentResult.text || agentResult.content || JSON.stringify(agentResult, null, 2));
                            html += `<div class="dual-agent-result">
                                <div class="dual-agent-result-header">@${agentName}</div>
                                <div>${resultText}</div>
                            </div>`;
                        }
                        wrapper.innerHTML = html;
                    }

                    chat.appendChild(wrapper);
                    chat.scrollTop = chat.scrollHeight;
                    messageCount++;
                    document.getElementById("messagesCount").textContent = messageCount;
                })
                .catch(err => {
                    const thinking = document.getElementById("thinking");
                    if (thinking) thinking.remove();
                    addMessage(`❌ Dual-agent error: ${err}`, "system");
                });
            } else {
                // Standard single-agent flow
                ws.send(`@${selectedAgent} ${text}`);
                addMessage(text, "user");
                showThinking();
                input.value = "";
            }
        }

        // Toggle dual-agent settings panel visibility
        document.getElementById("dualAgentToggle").addEventListener("change", function() {
            const settings = document.getElementById("dualAgentSettings");
            if (this.checked) {
                settings.classList.add("visible");
            } else {
                settings.classList.remove("visible");
            }
        });

        document.getElementById("input").addEventListener("keypress", function(event) {
            if (event.key === "Enter") sendMessage();
        });

        // File handling
        async function handleFileSelect(files) {
            if (files.length > 0) {
                const formData = new FormData();
                for (let i = 0; i < files.length; i++) {
                    formData.append("files", files[i]);
                }

                addMessage(`Uploading ${files.length} file(s)...`, "system");
                try {
                    const res = await fetch(`${API_BASE}/upload`, {
                        method: "POST",
                        body: formData
                    });
                    const result = await res.json();
                    addMessage(`✅ ${result.message}`, "system");
                    fetchFiles();
                } catch (err) {
                    addMessage(`❌ Upload failed: ${err}`, "system");
                }
            }
        }

        async function fetchFiles() {
            try {
                const res = await fetch(`${API_BASE}/files`);
                const data = await res.json();
                renderFileTree(data);
            } catch (e) {
                document.getElementById('fileTree').innerHTML = 
                    '<div style="color: var(--error); padding: 10px;">Failed to load files</div>';
            }
        }

        function renderFileTree(node) {
            const container = document.getElementById('fileTree');
            container.innerHTML = "";

            function createNode(item, parent) {
                const div = document.createElement("div");
                div.className = "file-item";
                const icon = item.type === "directory" ? "📁" : "📄";
                div.innerHTML = `<span class="file-icon">${icon}</span><span>${item.name}</span>`;
                
                if (item.type === "file") {
                    div.addEventListener('click', () => loadFile(item));
                }
                
                parent.appendChild(div);

                if (item.children) {
                    const childrenContainer = document.createElement("div");
                    childrenContainer.style.marginLeft = "20px";
                    item.children.forEach(child => createNode(child, childrenContainer));
                    parent.appendChild(childrenContainer);
                }
            }

            if (node.children && node.children.length > 0) {
                node.children.forEach(child => createNode(child, container));
                document.getElementById('filesCount').textContent = countFiles(node);
            } else {
                container.innerHTML = '<div style="padding: 10px; text-align: center; color: var(--text-muted); font-size: 0.875rem;">Drop zone is empty</div>';
            }
        }

        function countFiles(node) {
            let count = 0;
            if (node.type === "file") count++;
            if (node.children) {
                node.children.forEach(child => count += countFiles(child));
            }
            return count;
        }

        function loadFile(file) {
            // Switch to editor tab
            switchPanel('editor');
            document.getElementById('editorInfo').textContent = file.name;
            // In a real implementation, we would load the file content here
            editor.setValue(`// Content of ${file.name}\n// Loading...`);
        }

        function saveFile() {
            const content = editor.getValue();
            addMessage("💾 File saved successfully", "system");
            console.log("Saving file:", content);
        }

        function updateConnectionStatus(connected) {
            const badge = document.getElementById('connectionStatus');
            if (connected) {
                badge.classList.add('online');
                badge.classList.remove('offline');
                badge.innerHTML = '<span class="status-dot"></span><span>Online</span>';
            } else {
                badge.classList.remove('online');
                badge.classList.add('offline');
                badge.innerHTML = '<span class="status-dot"></span><span>Offline</span>';
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // Settings Panel Functions
        // ═══════════════════════════════════════════════════════════════

        // Load settings when switching to settings tab
        let settingsLoaded = false;
        const originalSwitchPanel = switchPanel;
        switchPanel = function(panelId) {
            originalSwitchPanel(panelId);
            if (panelId === 'settings') {
                if (!settingsLoaded) {
                    loadSettings();
                    settingsLoaded = true;
                } else {
                    // Restart live status refresh when returning to settings
                    startLiveStatusRefresh();
                }
            } else {
                // Stop live status refresh when leaving settings
                stopLiveStatusRefresh();
            }
        };

        async function loadSettings() {
            try {
                const response = await fetch(`${API_BASE}/settings?include_sensitive=true`);
                const data = await response.json();
                
                if (data.success) {
                    const settings = data.settings;
                    
                    // Load server settings
                    document.getElementById('serverHost').value = settings.server.host || '0.0.0.0';
                    document.getElementById('serverPort').value = settings.server.backend_port || 8000;
                    document.getElementById('frontendPort').value = settings.server.frontend_port || 3000;
                    document.getElementById('corsOrigins').value = settings.cors.allowed_origins.join(',');
                    
                    // Load AI models
                    await loadModels();
                    
                    // Load active model for radio buttons
                    await loadActiveModel();
                    
                    // Initialize live status banner and start auto-refresh
                    startLiveStatusRefresh();
                    
                    // Refresh ngrok status
                    await refreshNgrokStatus();
                    
                    // Load MCP servers
                    await loadMCPServers();
                    
                    // Load environment variables
                    await loadEnvironmentVariables();
                }
            } catch (error) {
                console.error('Error loading settings:', error);
                showStatus('serverSettingsStatus', 'Error loading settings', 'error');
            }
        }

        async function loadModels() {
            try {
                const response = await fetch(`${API_BASE}/settings/models`);
                const data = await response.json();
                
                if (data.success) {
                    const container = document.getElementById('modelsContainer');
                    if (!container) return;
                    container.innerHTML = '';
                    
                    data.models.forEach(model => {
                        const modelCard = document.createElement('div');
                        modelCard.className = `model-card ${model.id === data.active_model ? 'active' : ''}`;
                        modelCard.onclick = () => setActiveModel(model.id);
                        
                        const statusBadge = model.configured 
                            ? '<span class="status-indicator status-connected">✓ Configured</span>'
                            : '<span class="status-indicator status-disconnected">✗ Not Configured</span>';
                        
                        modelCard.innerHTML = `
                            <div class="model-card-header">
                                <div class="model-name">${model.name}</div>
                                ${statusBadge}
                            </div>
                            <div class="model-description">${model.description}</div>
                            ${model.id === data.active_model ? '<span style="color: var(--accent-green); font-size: 0.75rem; font-weight: 600;">● ACTIVE</span>' : ''}
                        `;
                        
                        container.appendChild(modelCard);
                    });
                }
            } catch (error) {
                console.error('Error loading models:', error);
            }
        }

        async function setActiveModel(modelId) {
            try {
                const response = await fetch(`${API_BASE}/settings/models?model_id=${modelId}`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    showStatus('connectionTestResult', `✓ ${modelId} is now the active model`, 'success');
                    await loadModels(); // Reload to update UI
                } else {
                    showStatus('connectionTestResult', `✗ ${data.error}`, 'error');
                }
            } catch (error) {
                console.error('Error setting active model:', error);
                showStatus('connectionTestResult', '✗ Failed to set active model', 'error');
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // New Enhanced Settings Functions
        // ═══════════════════════════════════════════════════════════════

        // Model Selection with Radio Buttons
        async function selectModel(modelValue) {
            showStatus('modelSelectionStatus', `Switching to ${modelValue}...`, 'info');
            
            try {
                const response = await fetch(`${API_BASE}/settings/models?model_id=${modelValue}`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    showStatus('modelSelectionStatus', `✓ Successfully switched to ${modelValue}`, 'success');
                    // Update live status banner
                    updateLiveStatusBanner();
                } else {
                    showStatus('modelSelectionStatus', `✗ ${data.error}`, 'error');
                }
            } catch (error) {
                console.error('Error selecting model:', error);
                showStatus('modelSelectionStatus', `✗ Failed to switch model`, 'error');
            }
        }

        // Load Active Model and update UI
        async function loadActiveModel() {
            try {
                const response = await fetch(`${API_BASE}/settings/models`);
                const data = await response.json();
                
                if (data.success && data.active_model) {
                    // Set the radio button to match active model
                    const radioButton = document.querySelector(`input[name="activeModel"][value="${data.active_model}"]`);
                    if (radioButton) {
                        radioButton.checked = true;
                    }
                }
            } catch (error) {
                console.error('Error loading active model:', error);
            }
        }

        // Reload Environment Variables
        async function reloadEnvironment() {
            showStatus('reloadEnvStatus', '🔄 Reloading environment...', 'info');
            
            try {
                const response = await fetch(`${API_BASE}/settings/reload-env`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    let message = '✓ Environment reloaded successfully';
                    
                    // Show what changed
                    if (data.changes && data.changes.length > 0) {
                        message += '<br><small>';
                        data.changes.forEach(change => {
                            message += `<br>• ${change}`;
                        });
                        message += '</small>';
                    }
                    
                    showStatus('reloadEnvStatus', message, 'success');
                    
                    // Refresh other UI elements
                    updateLiveStatusBanner();
                    loadActiveModel();
                    loadEnvironmentVariables();
                } else {
                    showStatus('reloadEnvStatus', `✗ ${data.error || 'Failed to reload environment'}`, 'error');
                }
            } catch (error) {
                console.error('Error reloading environment:', error);
                showStatus('reloadEnvStatus', '✗ Failed to reload environment', 'error');
            }
        }

        // Refresh Ngrok Status
        async function refreshNgrokStatus() {
            try {
                const response = await fetch(`${API_BASE}/ngrok/status`);
                const data = await response.json();
                
                const statusBadge = document.getElementById('ngrokStatusBadge');
                const urlContainer = document.getElementById('ngrokUrlContainer');
                const wsContainer = document.getElementById('ngrokWsContainer');
                const publicUrlInput = document.getElementById('ngrokPublicUrl');
                const wsUrlInput = document.getElementById('ngrokWsUrl');
                
                if (data.active && data.public_url) {
                    // Tunnel is active
                    statusBadge.innerHTML = '<span class="status-indicator status-connected">✓ Active</span>';
                    urlContainer.style.display = 'flex';
                    wsContainer.style.display = 'flex';
                    publicUrlInput.value = data.public_url;
                    wsUrlInput.value = data.ws_url || data.public_url.replace('https://', 'wss://').replace('http://', 'ws://') + '/ws';
                } else {
                    // Tunnel is inactive
                    statusBadge.innerHTML = '<span class="status-indicator status-disconnected">✗ Inactive</span>';
                    urlContainer.style.display = 'none';
                    wsContainer.style.display = 'none';
                }
            } catch (error) {
                console.error('Error fetching ngrok status:', error);
                const statusBadge = document.getElementById('ngrokStatusBadge');
                statusBadge.innerHTML = '<span class="status-indicator status-warning">⚠ Error</span>';
            }
        }

        // Update Live Status Banner
        async function updateLiveStatusBanner() {
            try {
                // Fetch active model
                const modelsResponse = await fetch(`${API_BASE}/settings/models`);
                const modelsData = await modelsResponse.json();
                
                if (modelsData.success) {
                    document.getElementById('statusActiveModel').textContent = modelsData.active_model || 'auto';
                }
                
                // Fetch ngrok status
                const ngrokResponse = await fetch(`${API_BASE}/ngrok/status`);
                const ngrokData = await ngrokResponse.json();
                
                const ngrokUrlElement = document.getElementById('statusNgrokUrl');
                if (ngrokData.active && ngrokData.public_url) {
                    const shortUrl = ngrokData.public_url.replace('https://', '').replace('http://', '');
                    ngrokUrlElement.innerHTML = `<span style="color: var(--success);">✓ ${shortUrl}</span>`;
                } else {
                    ngrokUrlElement.innerHTML = `<span style="color: var(--text-muted);">Not active</span>`;
                }
                
                // Check backend health
                const healthElement = document.getElementById('statusBackendHealth');
                try {
                    const healthResponse = await fetch(`${API_BASE}/health`);
                    if (healthResponse.ok) {
                        healthElement.innerHTML = `<span style="color: var(--success);">✓ Healthy</span>`;
                    } else {
                        healthElement.innerHTML = `<span style="color: var(--error);">✗ Error</span>`;
                    }
                } catch {
                    healthElement.innerHTML = `<span style="color: var(--error);">✗ Down</span>`;
                }
            } catch (error) {
                console.error('Error updating live status banner:', error);
            }
        }

        // Copy to Clipboard
        function copyToClipboard(inputId) {
            const input = document.getElementById(inputId);
            input.select();
            input.setSelectionRange(0, 99999); // For mobile devices
            
            try {
                document.execCommand('copy');
                showStatus('modelSelectionStatus', '✓ Copied to clipboard!', 'success');
            } catch (err) {
                // Fallback to navigator.clipboard API
                navigator.clipboard.writeText(input.value).then(() => {
                    showStatus('modelSelectionStatus', '✓ Copied to clipboard!', 'success');
                }).catch(() => {
                    showStatus('modelSelectionStatus', '✗ Failed to copy', 'error');
                });
            }
        }

        // Auto-refresh live status banner every 5 seconds
        let liveStatusInterval = null;
        
        function startLiveStatusRefresh() {
            // Initial update
            updateLiveStatusBanner();
            
            // Clear existing interval if any
            if (liveStatusInterval) {
                clearInterval(liveStatusInterval);
            }
            
            // Set up new interval
            liveStatusInterval = setInterval(() => {
                updateLiveStatusBanner();
            }, 5000); // Update every 5 seconds
        }

        function stopLiveStatusRefresh() {
            if (liveStatusInterval) {
                clearInterval(liveStatusInterval);
                liveStatusInterval = null;
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // End Enhanced Settings Functions
        // ═══════════════════════════════════════════════════════════════

        async function testConnection(service) {
            showStatus('connectionTestResult', `Testing ${service} connection...`, 'info');
            
            try {
                const response = await fetch(`${API_BASE}/settings/test-connection/${service}`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    showStatus('connectionTestResult', `✓ ${data.message}`, 'success');
                } else {
                    showStatus('connectionTestResult', `✗ ${data.error}`, 'error');
                }
            } catch (error) {
                console.error('Error testing connection:', error);
                showStatus('connectionTestResult', `✗ Failed to test ${service} connection`, 'error');
            }
        }

        async function updateApiKey(keyVar, inputId) {
            const value = document.getElementById(inputId).value;
            
            if (!value || value.length < 10) {
                showStatus('apiKeyStatus', '✗ API key is too short', 'error');
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/settings/api-keys`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        key_var: keyVar,
                        value: value
                    })
                });
                const data = await response.json();
                
                if (data.success) {
                    showStatus('apiKeyStatus', `✓ ${keyVar} updated successfully`, 'success');
                    document.getElementById(inputId).value = ''; // Clear for security
                } else {
                    showStatus('apiKeyStatus', `✗ ${data.error}`, 'error');
                }
            } catch (error) {
                console.error('Error updating API key:', error);
                showStatus('apiKeyStatus', '✗ Failed to update API key', 'error');
            }
        }

        function togglePasswordVisibility(inputId) {
            const input = document.getElementById(inputId);
            input.type = input.type === 'password' ? 'text' : 'password';
        }

        async function loadMCPServers() {
            try {
                const response = await fetch(`${API_BASE}/settings/mcp`);
                const data = await response.json();
                
                if (data.success) {
                    const container = document.getElementById('mcpServersContainer');
                    container.innerHTML = '';
                    
                    if (data.servers.length === 0) {
                        container.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 20px;">No MCP servers configured</div>';
                        return;
                    }
                    
                    data.servers.forEach(server => {
                        const serverItem = document.createElement('div');
                        serverItem.className = 'mcp-server-item';
                        
                        let statusBadge;
                        if (server.status === 'ready') {
                            statusBadge = '<span class="status-indicator status-connected">● Ready</span>';
                        } else if (server.status === 'missing_credentials') {
                            statusBadge = '<span class="status-indicator status-warning">⚠ Missing Credentials</span>';
                        } else {
                            statusBadge = '<span class="status-indicator status-disconnected">● Configured</span>';
                        }
                        
                        const missingVars = server.missing_vars ? `<div style="font-size: 0.7rem; color: var(--error); margin-top: 4px;">Missing: ${server.missing_vars.join(', ')}</div>` : '';
                        
                        serverItem.innerHTML = `
                            <div class="mcp-server-info">
                                <div class="mcp-server-name">${server.name}</div>
                                <div class="mcp-server-details">
                                    ${server.type} • ${server.command}
                                    ${statusBadge}
                                    ${missingVars}
                                </div>
                            </div>
                            <div class="toggle-switch ${server.enabled ? 'active' : ''}" onclick="toggleMCPServer('${server.name}', ${!server.enabled})"></div>
                        `;
                        
                        container.appendChild(serverItem);
                    });
                    
                    // Update MCP server count in stats
                    document.getElementById('mcpServers').textContent = data.total;
                }
            } catch (error) {
                console.error('Error loading MCP servers:', error);
            }
        }

        async function toggleMCPServer(serverName, enabled) {
            try {
                const response = await fetch(`${API_BASE}/settings/mcp/${serverName}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ enabled })
                });
                const data = await response.json();
                
                if (data.success) {
                    await loadMCPServers(); // Reload to update UI
                }
            } catch (error) {
                console.error('Error toggling MCP server:', error);
            }
        }

        async function refreshMCPServers() {
            await loadMCPServers();
        }

        async function saveServerSettings() {
            const settings = {
                server: {
                    host: document.getElementById('serverHost').value,
                    backend_port: parseInt(document.getElementById('serverPort').value),
                    frontend_port: parseInt(document.getElementById('frontendPort').value)
                },
                cors: {
                    allowed_origins: document.getElementById('corsOrigins').value.split(',').map(s => s.trim())
                }
            };
            
            try {
                const response = await fetch(`${API_BASE}/settings`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(settings)
                });
                const data = await response.json();
                
                if (data.success) {
                    showStatus('serverSettingsStatus', '✓ Settings saved successfully. Restart server to apply changes.', 'success');
                } else {
                    showStatus('serverSettingsStatus', `✗ Failed to save settings`, 'error');
                }
            } catch (error) {
                console.error('Error saving settings:', error);
                showStatus('serverSettingsStatus', '✗ Failed to save settings', 'error');
            }
        }

        async function loadEnvironmentVariables() {
            try {
                const response = await fetch(`${API_BASE}/settings/env`);
                const data = await response.json();
                
                if (data.success) {
                    const tbody = document.getElementById('envVarTableBody');
                    tbody.innerHTML = '';
                    
                    const vars = data.variables;
                    if (Object.keys(vars).length === 0) {
                        tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: var(--text-muted); padding: 20px;">No environment variables found</td></tr>';
                        return;
                    }
                    
                    Object.entries(vars).forEach(([key, value]) => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td class="env-var-key">${key}</td>
                            <td class="env-var-value">${value || '<span style="color: var(--text-muted);">(empty)</span>'}</td>
                            <td>
                                <button class="settings-btn settings-btn-secondary" style="padding: 4px 10px; font-size: 0.75rem;" onclick="editEnvVar('${key}', '${value}')">
                                    ✏️ Edit
                                </button>
                            </td>
                        `;
                        tbody.appendChild(row);
                    });
                }
            } catch (error) {
                console.error('Error loading environment variables:', error);
            }
        }

        function editEnvVar(key, currentValue) {
            const newValue = prompt(`Edit ${key}:`, currentValue);
            if (newValue !== null) {
                updateEnvVar(key, newValue);
            }
        }

        async function updateEnvVar(key, value) {
            try {
                const response = await fetch(`${API_BASE}/settings/env`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ key, value })
                });
                const data = await response.json();
                
                if (data.success) {
                    await loadEnvironmentVariables();
                } else {
                    alert(`Error: ${data.error}`);
                }
            } catch (error) {
                console.error('Error updating environment variable:', error);
                alert('Failed to update environment variable');
            }
        }

        async function exportConfiguration() {
            try {
                const response = await fetch(`${API_BASE}/settings/export`);
                const data = await response.json();
                
                if (data.success) {
                    const blob = new Blob([JSON.stringify(data.config, null, 2)], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `antigravity-config-${new Date().toISOString().split('T')[0]}.json`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }
            } catch (error) {
                console.error('Error exporting configuration:', error);
                alert('Failed to export configuration');
            }
        }

        function showStatus(elementId, message, type) {
            const element = document.getElementById(elementId);
            const statusClass = type === 'success' ? 'status-connected' : 
                              type === 'error' ? 'status-disconnected' : 
                              'status-warning';
            element.innerHTML = `<div class="status-indicator ${statusClass}">${message}</div>`;
            
            // Clear after 5 seconds
            setTimeout(() => {
                element.innerHTML = '';
            }, 5000);
        }

        // ═══════════════════════════════════════════════════════════════
        // End Settings Functions
        // ═══════════════════════════════════════════════════════════════

        // ═══════════════════════════════════════════════════════════════
        // Performance Dashboard
        // ═══════════════════════════════════════════════════════════════

        // Performance Dashboard State
        let performanceCharts = {};
        let performanceData = {
            cpu: [],
            memory: [],
            cache: { hits: [], misses: [] },
            websocket: [],
            responseTime: []
        };
        let performanceInterval = null;
        let performanceTimeRange = 15; // minutes

        // Initialize Performance Charts
        function initPerformanceCharts() {
            const chartConfig = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { 
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(30, 41, 59, 0.9)',
                        titleColor: '#f8fafc',
                        bodyColor: '#94a3b8',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: { 
                        display: false,
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { 
                            color: '#64748b',
                            callback: function(value) { return value + '%'; }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        }
                    }
                }
            };

            // CPU Chart
            const cpuCtx = document.getElementById('cpuChart');
            if (cpuCtx) {
                performanceCharts.cpu = new Chart(cpuCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'CPU %',
                            data: [],
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: chartConfig
                });
            }

            // Memory Chart
            const memoryCtx = document.getElementById('memoryChart');
            if (memoryCtx) {
                performanceCharts.memory = new Chart(memoryCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Memory %',
                            data: [],
                            borderColor: '#8b5cf6',
                            backgroundColor: 'rgba(139, 92, 246, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: chartConfig
                });
            }

            // Cache Chart
            const cacheCtx = document.getElementById('cacheChart');
            if (cacheCtx) {
                performanceCharts.cache = new Chart(cacheCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Hits', 'Misses'],
                        datasets: [{
                            data: [0, 0],
                            backgroundColor: ['#10b981', '#ef4444'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'bottom',
                                labels: { color: '#94a3b8', font: { size: 11 } }
                            }
                        }
                    }
                });
            }

            // WebSocket Chart
            const wsCtx = document.getElementById('wsChart');
            if (wsCtx) {
                performanceCharts.websocket = new Chart(wsCtx, {
                    type: 'bar',
                    data: {
                        labels: ['Active', 'Total'],
                        datasets: [{
                            label: 'Connections',
                            data: [0, 0],
                            backgroundColor: ['#10b981', '#3b82f6'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { color: '#64748b' },
                                grid: { color: 'rgba(255, 255, 255, 0.05)' }
                            },
                            x: {
                                ticks: { color: '#94a3b8' },
                                grid: { display: false }
                            }
                        }
                    }
                });
            }

            // Response Time Chart
            const rtCtx = document.getElementById('responseTimeChart');
            if (rtCtx) {
                performanceCharts.responseTime = new Chart(rtCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Response Time (ms)',
                            data: [],
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        ...chartConfig,
                        scales: {
                            ...chartConfig.scales,
                            y: {
                                ...chartConfig.scales.y,
                                max: undefined,
                                ticks: {
                                    color: '#64748b',
                                    callback: function(value) { return value + 'ms'; }
                                }
                            }
                        }
                    }
                });
            }
        }

        // Fetch Performance Metrics
        async function fetchPerformanceMetrics() {
            try {
                const response = await fetch(`${API_BASE}/performance/metrics`);
                if (!response.ok) throw new Error('Failed to fetch metrics');
                
                const data = await response.json();
                updatePerformanceDashboard(data);
            } catch (error) {
                console.error('Error fetching performance metrics:', error);
            }
        }

        // Update Performance Dashboard
        function updatePerformanceDashboard(data) {
            if (!data) return;

            // Update System Metrics
            if (data.system) {
                updateSystemMetrics(data.system);
            }

            // Update Cache Stats
            if (data.cache) {
                updateCacheStats(data.cache);
            }

            // Update WebSocket Stats
            if (data.websocket) {
                updateWebSocketStats(data.websocket);
            }

            // Update MCP Stats
            if (data.mcp) {
                updateMCPStats(data.mcp);
            }

            // Update Request Stats
            if (data.requests) {
                updateRequestStats(data.requests);
            }
        }

        // Update System Metrics
        function updateSystemMetrics(system) {
            // Update CPU
            const cpuPercent = system.cpu_percent || 0;
            document.getElementById('cpuCurrent').textContent = `${cpuPercent.toFixed(1)}%`;
            
            performanceData.cpu.push(cpuPercent);
            if (performanceData.cpu.length > 60) performanceData.cpu.shift();
            
            if (performanceCharts.cpu) {
                performanceCharts.cpu.data.labels = performanceData.cpu.map((_, i) => i);
                performanceCharts.cpu.data.datasets[0].data = performanceData.cpu;
                
                const avgCpu = performanceData.cpu.reduce((a, b) => a + b, 0) / performanceData.cpu.length;
                document.getElementById('cpuAverage').textContent = `${avgCpu.toFixed(1)}%`;
                
                performanceCharts.cpu.update('none');
            }

            // Update Memory
            const memoryPercent = system.memory_percent || 0;
            document.getElementById('memoryCurrent').textContent = `${memoryPercent.toFixed(1)}%`;
            
            performanceData.memory.push(memoryPercent);
            if (performanceData.memory.length > 60) performanceData.memory.shift();
            
            if (performanceCharts.memory) {
                performanceCharts.memory.data.labels = performanceData.memory.map((_, i) => i);
                performanceCharts.memory.data.datasets[0].data = performanceData.memory;
                
                const avgMemory = performanceData.memory.reduce((a, b) => a + b, 0) / performanceData.memory.length;
                document.getElementById('memoryAverage').textContent = `${avgMemory.toFixed(1)}%`;
                
                performanceCharts.memory.update('none');
            }

            // Update Disk
            const diskPercent = system.disk_usage_percent || 0;
            document.getElementById('diskValue').textContent = `${diskPercent.toFixed(1)}%`;
            const diskGauge = document.getElementById('diskGauge');
            if (diskGauge) {
                diskGauge.style.setProperty('--percentage', diskPercent);
            }
            
            const diskStatus = diskPercent > 90 ? 'Critical' : diskPercent > 80 ? 'Warning' : 'Normal';
            document.getElementById('diskStatus').textContent = diskStatus;
        }

        // Update Cache Stats
        function updateCacheStats(cache) {
            const hitRate = cache.hit_rate_percent || 0;
            document.getElementById('cacheHitRate').textContent = `${hitRate.toFixed(1)}%`;
            document.getElementById('cacheHits').textContent = cache.hits || 0;
            document.getElementById('cacheMisses').textContent = cache.misses || 0;
            document.getElementById('cacheSize').textContent = `${cache.size || 0} items`;
            document.getElementById('cacheAccesses').textContent = cache.total_accesses || 0;
            
            const hitProgress = document.getElementById('cacheHitProgress');
            if (hitProgress) {
                hitProgress.style.width = `${hitRate}%`;
            }
            
            if (performanceCharts.cache) {
                performanceCharts.cache.data.datasets[0].data = [cache.hits || 0, cache.misses || 0];
                performanceCharts.cache.update('none');
            }
        }

        // Update WebSocket Stats
        function updateWebSocketStats(websocket) {
            document.getElementById('wsActiveCount').textContent = websocket.active_connections || 0;
            document.getElementById('wsTotalCount').textContent = websocket.total_connections || 0;
            document.getElementById('wsAvgDuration').textContent = 
                `${(websocket.average_duration_seconds || 0).toFixed(1)}s`;
            
            if (performanceCharts.websocket) {
                performanceCharts.websocket.data.datasets[0].data = [
                    websocket.active_connections || 0,
                    websocket.total_connections || 0
                ];
                performanceCharts.websocket.update('none');
            }

            // Update active connections list
            const activeList = document.getElementById('wsActiveList');
            if (activeList && websocket.active_connections_list) {
                if (websocket.active_connections_list.length === 0) {
                    activeList.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 20px;">No active connections</div>';
                } else {
                    activeList.innerHTML = websocket.active_connections_list.map(conn => `
                        <div class="perf-metric-row">
                            <span class="perf-metric-label">
                                <span class="perf-status-dot online"></span>
                                ${conn.connection_id.substring(0, 8)}...
                            </span>
                            <span class="perf-metric-value">
                                ${conn.messages_sent} sent / ${conn.messages_received} rcv
                            </span>
                        </div>
                    `).join('');
                }
            }
        }

        // Update MCP Stats
        function updateMCPStats(mcpServers) {
            const tbody = document.getElementById('mcpTableBody');
            if (!tbody) return;

            const servers = Object.entries(mcpServers);
            if (servers.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No MCP server data available</td></tr>';
                return;
            }

            tbody.innerHTML = servers.map(([name, stats]) => {
                const statusClass = stats.success_rate_percent > 90 ? 'online' : 
                                   stats.success_rate_percent > 70 ? 'warning' : 'offline';
                return `
                    <tr>
                        <td>${name}</td>
                        <td><span class="perf-status-dot ${statusClass}"></span></td>
                        <td>${stats.average_response_time_ms.toFixed(2)}ms</td>
                        <td>${stats.success_rate_percent.toFixed(1)}%</td>
                        <td>${stats.total_requests}</td>
                    </tr>
                `;
            }).join('');
        }

        // Update Request Stats
        function updateRequestStats(requests) {
            document.getElementById('reqPerMinute').textContent = requests.requests_per_minute || 0;
            document.getElementById('reqTotal').textContent = requests.total_requests || 0;
            document.getElementById('reqErrorRate').textContent = 
                `${(requests.error_rate_percent || 0).toFixed(1)}%`;
            document.getElementById('reqAvgTime').textContent = 
                `${(requests.average_response_time_ms || 0).toFixed(2)}ms`;

            // Update slowest endpoints
            const slowestDiv = document.getElementById('slowestEndpoints');
            if (slowestDiv && requests.slowest_endpoints) {
                if (requests.slowest_endpoints.length === 0) {
                    slowestDiv.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 20px;">No data available</div>';
                } else {
                    slowestDiv.innerHTML = requests.slowest_endpoints.slice(0, 5).map(ep => `
                        <div class="perf-metric-row">
                            <span class="perf-metric-label">${ep.endpoint}</span>
                            <span class="perf-metric-value">${ep.avg_time_ms.toFixed(2)}ms</span>
                        </div>
                    `).join('');
                }
            }

            // Update response time chart
            if (performanceCharts.responseTime && requests.recent_requests) {
                const times = requests.recent_requests.slice(-30).map(r => r.response_time_ms);
                const labels = times.map((_, i) => i);
                
                performanceCharts.responseTime.data.labels = labels;
                performanceCharts.responseTime.data.datasets[0].data = times;
                performanceCharts.responseTime.update('none');
            }
        }

        // Refresh Performance Dashboard
        function refreshPerformance() {
            fetchPerformanceMetrics();
        }

        // Set Time Range
        function setTimeRange(minutes) {
            performanceTimeRange = minutes;
            
            // Update active button
            document.querySelectorAll('.perf-time-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Fetch history for new time range
            fetchPerformanceHistory(minutes);
        }

        // Fetch Performance History
        async function fetchPerformanceHistory(minutes) {
            try {
                const response = await fetch(`${API_BASE}/performance/metrics/history?minutes=${minutes}`);
                if (!response.ok) throw new Error('Failed to fetch history');
                
                const data = await response.json();
                // Process historical data
                if (data.metrics && data.metrics.length > 0) {
                    performanceData.cpu = data.metrics.map(m => m.cpu_percent);
                    performanceData.memory = data.metrics.map(m => m.memory_percent);
                    
                    // Update charts
                    if (performanceCharts.cpu) {
                        performanceCharts.cpu.data.labels = performanceData.cpu.map((_, i) => i);
                        performanceCharts.cpu.data.datasets[0].data = performanceData.cpu;
                        performanceCharts.cpu.update();
                    }
                    
                    if (performanceCharts.memory) {
                        performanceCharts.memory.data.labels = performanceData.memory.map((_, i) => i);
                        performanceCharts.memory.data.datasets[0].data = performanceData.memory;
                        performanceCharts.memory.update();
                    }
                }
            } catch (error) {
                console.error('Error fetching performance history:', error);
            }
        }

        // Export Metrics
        async function exportMetrics() {
            try {
                const response = await fetch(`${API_BASE}/performance/metrics`);
                if (!response.ok) throw new Error('Failed to fetch metrics');
                
                const data = await response.json();
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `performance-metrics-${new Date().toISOString()}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                showNotification('Metrics exported successfully', 'success');
            } catch (error) {
                console.error('Error exporting metrics:', error);
                showNotification('Failed to export metrics', 'error');
            }
        }

        // Start/Stop Performance Monitoring
        function startPerformanceMonitoring() {
            if (performanceInterval) return;
            
            initPerformanceCharts();
            fetchPerformanceMetrics();
            performanceInterval = setInterval(fetchPerformanceMetrics, 2000); // Update every 2 seconds
        }

        function stopPerformanceMonitoring() {
            if (performanceInterval) {
                clearInterval(performanceInterval);
                performanceInterval = null;
            }
        }

        // Initialize performance monitoring when tab is active
        document.querySelectorAll('.tab').forEach(tab => {
            const originalClick = tab.onclick;
            tab.addEventListener('click', function() {
                const panelId = this.getAttribute('data-panel');
                
                if (panelId === 'performance') {
                    startPerformanceMonitoring();
                } else {
                    stopPerformanceMonitoring();
                }
            });
        });

        // ═══════════════════════════════════════════════════════════════
        // End Performance Dashboard
        // ═══════════════════════════════════════════════════════════════

        // ═══════════════════════════════════════════════════════════════
        // Debug Panel Functionality
        // ═══════════════════════════════════════════════════════════════

        let debugState = {
            logs: [],
            filteredLogs: [],
            currentPage: 1,
            perPage: 50,
            totalPages: 1,
            autoRefreshInterval: null,
            filters: {
                severity: 'ALL',
                model: 'ALL'
            }
        };

        // Initialize debug panel when activated
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', function() {
                const panelId = this.getAttribute('data-panel');
                
                if (panelId === 'debug') {
                    startDebugMonitoring();
                } else if (debugState.autoRefreshInterval) {
                    stopDebugMonitoring();
                }
            });
        });

        function startDebugMonitoring() {
            // Initial load
            refreshLogs();
            
            // Auto-refresh every 3 seconds
            if (debugState.autoRefreshInterval) {
                clearInterval(debugState.autoRefreshInterval);
            }
            debugState.autoRefreshInterval = setInterval(refreshLogs, 3000);
        }

        function stopDebugMonitoring() {
            if (debugState.autoRefreshInterval) {
                clearInterval(debugState.autoRefreshInterval);
                debugState.autoRefreshInterval = null;
            }
        }

        // Refresh logs from API
        async function refreshLogs() {
            try {
                const response = await fetch(`${API_BASE}/debug/logs?page=${debugState.currentPage}&per_page=${debugState.perPage}`);
                if (!response.ok) throw new Error('Failed to fetch logs');
                
                const data = await response.json();
                debugState.logs = data.logs || [];
                debugState.totalPages = data.total_pages || 1;
                
                applyLogFilters();
                updateLogsDisplay();
                updatePaginationButtons();
            } catch (error) {
                console.error('Error fetching logs:', error);
                displayLogsError('Failed to load logs. Make sure the backend is running.');
            }
        }

        // Apply filters to logs
        function applyLogFilters() {
            const severity = document.getElementById('logSeverityFilter').value;
            const model = document.getElementById('logModelFilter').value;
            
            debugState.filters.severity = severity;
            debugState.filters.model = model;
            
            debugState.filteredLogs = debugState.logs.filter(log => {
                // Severity filter
                if (severity !== 'ALL' && log.level !== severity) {
                    return false;
                }
                
                // Model filter
                if (model !== 'ALL' && log.metadata && log.metadata.model !== model) {
                    return false;
                }
                
                return true;
            });
            
            updateLogsDisplay();
        }

        // Update logs display
        function updateLogsDisplay() {
            const container = document.getElementById('debugLogsDisplay');
            
            if (debugState.filteredLogs.length === 0) {
                container.innerHTML = `
                    <div class="debug-empty-state">
                        <div class="debug-empty-icon">📝</div>
                        <div>No logs to display</div>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = debugState.filteredLogs.map(log => {
                const level = (log.level || 'INFO').toLowerCase();
                const timestamp = formatTimestamp(log.timestamp);
                const metadata = log.metadata ? JSON.stringify(log.metadata) : '';
                
                return `
                    <div class="debug-log-entry log-${level}" onclick='showLogDetails(${JSON.stringify(log).replace(/'/g, "\\'")})'}>
                        <div>
                            <span class="debug-log-time">${timestamp}</span>
                            <span class="debug-log-level level-${level}">${log.level || 'INFO'}</span>
                            <span class="debug-log-message">${escapeHtml(log.message || '')}</span>
                        </div>
                        ${log.metadata ? `<div class="debug-log-metadata">${escapeHtml(metadata)}</div>` : ''}
                    </div>
                `;
            }).join('');
            
            // Auto-scroll if enabled
            if (document.getElementById('autoScrollLogs').checked) {
                container.scrollTop = container.scrollHeight;
            }
        }

        // Display error message
        function displayLogsError(message) {
            const container = document.getElementById('debugLogsDisplay');
            container.innerHTML = `
                <div class="debug-empty-state">
                    <div class="debug-empty-icon">⚠️</div>
                    <div style="color: var(--error);">${message}</div>
                </div>
            `;
        }

        // Clear logs display (local only)
        function clearLogsDisplay() {
            debugState.logs = [];
            debugState.filteredLogs = [];
            updateLogsDisplay();
        }

        // Show log details in modal
        function showLogDetails(log) {
            document.getElementById('debugModalTitle').textContent = `Log Entry - ${log.level || 'INFO'}`;
            document.getElementById('debugModalContent').textContent = JSON.stringify(log, null, 2);
            document.getElementById('debugModal').classList.add('active');
        }

        // Close debug modal
        function closeDebugModal() {
            document.getElementById('debugModal').classList.remove('active');
        }

        // Close modal on outside click
        document.getElementById('debugModal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeDebugModal();
            }
        });

        // Export logs
        async function exportLogs() {
            try {
                const response = await fetch(`${API_BASE}/debug/export?format=json`);
                if (!response.ok) throw new Error('Failed to export logs');
                
                const data = await response.blob();
                const url = URL.createObjectURL(data);
                const a = document.createElement('a');
                a.href = url;
                a.download = `debug-logs-${new Date().toISOString()}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            } catch (error) {
                console.error('Error exporting logs:', error);
                alert('Failed to export logs. Make sure the /debug/export endpoint is available.');
            }
        }

        // Load failed requests
        async function loadFailedRequests() {
            try {
                const response = await fetch(`${API_BASE}/debug/failed`);
                if (!response.ok) throw new Error('Failed to fetch failed requests');
                
                const data = await response.json();
                displayFailedRequests(data.failed_requests || []);
                
                // Expand the section
                toggleCollapsible('failedRequests', true);
            } catch (error) {
                console.error('Error loading failed requests:', error);
                displayFailedRequests([]);
            }
        }

        // Display failed requests
        function displayFailedRequests(requests) {
            const container = document.getElementById('failedRequestsList');
            const countElement = document.getElementById('failedRequestsCount');
            
            countElement.textContent = `${requests.length} items`;
            
            if (requests.length === 0) {
                container.innerHTML = `
                    <div class="debug-empty-state">
                        <div class="debug-empty-icon">✓</div>
                        <div>No failed requests</div>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = requests.map(req => `
                <div class="debug-item" onclick='showLogDetails(${JSON.stringify(req).replace(/'/g, "\\'")})'}>
                    <div class="debug-item-header">
                        <span class="debug-item-time">${formatTimestamp(req.timestamp)}</span>
                        <span style="color: var(--text-muted); font-size: 0.75rem;">${req.model || 'N/A'}</span>
                    </div>
                    <div class="debug-item-content">
                        <div><strong>Request:</strong> ${escapeHtml(req.request || '')}</div>
                        <div class="debug-item-error"><strong>Error:</strong> ${escapeHtml(req.error || '')}</div>
                    </div>
                </div>
            `).join('');
        }

        // Load missing data
        async function loadMissingData() {
            try {
                const response = await fetch(`${API_BASE}/debug/missing-data`);
                if (!response.ok) throw new Error('Failed to fetch missing data');
                
                const data = await response.json();
                displayMissingData(data.missing_data || []);
                
                // Expand the section
                toggleCollapsible('missingData', true);
            } catch (error) {
                console.error('Error loading missing data:', error);
                displayMissingData([]);
            }
        }

        // Display missing data
        function displayMissingData(items) {
            const container = document.getElementById('missingDataList');
            const countElement = document.getElementById('missingDataCount');
            
            countElement.textContent = `${items.length} items`;
            
            if (items.length === 0) {
                container.innerHTML = `
                    <div class="debug-empty-state">
                        <div class="debug-empty-icon">✓</div>
                        <div>All requests have proper context</div>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = items.map(item => `
                <div class="debug-item" onclick='showLogDetails(${JSON.stringify(item).replace(/'/g, "\\'")})'}>
                    <div class="debug-item-header">
                        <span class="debug-item-time">${formatTimestamp(item.timestamp)}</span>
                    </div>
                    <div class="debug-item-content">
                        <div><strong>Request:</strong> ${escapeHtml(item.request || '')}</div>
                        <div style="color: var(--warning);"><strong>Missing:</strong> ${escapeHtml(item.missing || '')}</div>
                    </div>
                </div>
            `).join('');
        }

        // Clear logs with confirmation
        function clearLogsConfirm() {
            if (confirm('Are you sure you want to clear all logs? This action cannot be undone.')) {
                clearAllLogs();
            }
        }

        // Clear all logs on backend
        async function clearAllLogs() {
            try {
                const response = await fetch(`${API_BASE}/debug/clear`, {
                    method: 'POST'
                });
                
                if (!response.ok) throw new Error('Failed to clear logs');
                
                const data = await response.json();
                alert(data.message || 'Logs cleared successfully');
                
                // Refresh display
                refreshLogs();
            } catch (error) {
                console.error('Error clearing logs:', error);
                alert('Failed to clear logs. Make sure the /debug/clear endpoint is available.');
            }
        }

        // Toggle collapsible section
        function toggleCollapsible(sectionId, forceExpand = false) {
            const content = document.getElementById(`${sectionId}Content`);
            const icon = document.getElementById(`${sectionId}Icon`);
            
            if (forceExpand || !content.classList.contains('expanded')) {
                content.classList.add('expanded');
                icon.classList.add('expanded');
            } else {
                content.classList.remove('expanded');
                icon.classList.remove('expanded');
            }
        }

        // Pagination
        function loadPreviousLogs() {
            if (debugState.currentPage > 1) {
                debugState.currentPage--;
                refreshLogs();
            }
        }

        function loadNextLogs() {
            if (debugState.currentPage < debugState.totalPages) {
                debugState.currentPage++;
                refreshLogs();
            }
        }

        function updatePaginationButtons() {
            const prevBtn = document.getElementById('prevLogsBtn');
            const nextBtn = document.getElementById('nextLogsBtn');
            const pageInfo = document.getElementById('logsPageInfo');
            
            prevBtn.disabled = debugState.currentPage <= 1;
            nextBtn.disabled = debugState.currentPage >= debugState.totalPages;
            pageInfo.textContent = `Page ${debugState.currentPage} of ${debugState.totalPages}`;
        }

        // Utility functions
        function formatTimestamp(timestamp) {
            if (!timestamp) return 'N/A';
            const date = new Date(timestamp);
            return date.toLocaleTimeString('en-US', { 
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // ═══════════════════════════════════════════════════════════════
        // End Debug Panel
        // ═══════════════════════════════════════════════════════════════

        // ═══════════════════════════════════════════════════════════════
        // Swarm Tab Functions
        // ═══════════════════════════════════════════════════════════════

        let swarmState = {
            executing: false,
            currentTask: null
        };

        // Execute swarm task
        async function executeSwarm() {
            const taskInput = document.getElementById('swarmTaskInput');
            const task = taskInput.value.trim();
            
            if (!task) {
                alert('Please enter a task');
                return;
            }
            
            if (swarmState.executing) {
                alert('A swarm execution is already in progress');
                return;
            }
            
            const executeBtn = document.getElementById('swarmExecuteBtn');
            const verbose = document.getElementById('swarmVerbose').checked;
            
            try {
                swarmState.executing = true;
                executeBtn.disabled = true;
                executeBtn.innerHTML = '<span>⏳</span><span>Executing...</span>';
                
                // Clear previous results
                clearSwarmResults();
                
                const response = await fetch(`${API_BASE}/api/swarm/execute`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ task, verbose })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                displaySwarmResults(data);
                
            } catch (error) {
                console.error('Error executing swarm:', error);
                alert(`Failed to execute swarm: ${error.message}`);
            } finally {
                swarmState.executing = false;
                executeBtn.disabled = false;
                executeBtn.innerHTML = '<span>🚀</span><span>Execute with Swarm</span>';
            }
        }

        // Clear swarm results
        function clearSwarmResults() {
            const planDisplay = document.getElementById('swarmPlanDisplay');
            const resultsDisplay = document.getElementById('swarmResultsDisplay');
            
            planDisplay.classList.remove('active');
            planDisplay.innerHTML = `
                <div style="text-align: center; color: var(--text-muted); padding: 20px;">
                    Execute a task to see the delegation plan
                </div>
            `;
            
            resultsDisplay.classList.remove('active');
            resultsDisplay.innerHTML = `
                <div style="text-align: center; color: var(--text-muted); padding: 20px;">
                    Results will appear here after execution
                </div>
            `;
        }

        // Display swarm results
        function displaySwarmResults(data) {
            const planDisplay = document.getElementById('swarmPlanDisplay');
            const resultsDisplay = document.getElementById('swarmResultsDisplay');
            
            // Display delegation plan if available
            if (data.delegation_plan) {
                planDisplay.classList.add('active');
                const planHTML = Object.entries(data.delegation_plan).map(([agent, task]) => `
                    <div class="swarm-plan-item">
                        <div class="swarm-plan-agent">${agent}</div>
                        <div class="swarm-plan-task">${escapeHtml(task)}</div>
                    </div>
                `).join('');
                planDisplay.innerHTML = planHTML;
            }
            
            // Display agent results
            if (data.agent_results) {
                resultsDisplay.classList.add('active');
                const resultsHTML = Object.entries(data.agent_results).map(([agent, result]) => `
                    <div class="swarm-result-item">
                        <div class="swarm-result-header">
                            <div class="swarm-result-agent">${agent}</div>
                            <div class="swarm-result-status ${result.success !== false ? '' : 'error'}">
                                ${result.success !== false ? '✓ Success' : '✗ Error'}
                            </div>
                        </div>
                        <div class="swarm-result-content">${escapeHtml(JSON.stringify(result, null, 2))}</div>
                    </div>
                `).join('');
                resultsDisplay.innerHTML = resultsHTML;
            }
            
            // Display final result if available
            if (data.final_result) {
                resultsDisplay.classList.add('active');
                const finalHTML = `
                    <div class="swarm-result-item">
                        <div class="swarm-result-header">
                            <div class="swarm-result-agent">Final Synthesized Result</div>
                            <div class="swarm-result-status">✓ Complete</div>
                        </div>
                        <div class="swarm-result-content">${escapeHtml(data.final_result)}</div>
                    </div>
                `;
                resultsDisplay.innerHTML += finalHTML;
            }
        }

        // Load agent capabilities
        async function loadSwarmCapabilities() {
            try {
                const response = await fetch(`${API_BASE}/api/swarm/capabilities`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                displaySwarmCapabilities(data.capabilities);
            } catch (error) {
                console.error('Error loading swarm capabilities:', error);
            }
        }

        // Display swarm capabilities
        function displaySwarmCapabilities(capabilities) {
            const grid = document.getElementById('swarmAgentsGrid');
            if (!capabilities || Object.keys(capabilities).length === 0) {
                return;
            }
            
            const html = Object.entries(capabilities).map(([agent, info]) => `
                <div class="swarm-agent-card active">
                    <div class="swarm-status-indicator active"></div>
                    <div class="swarm-agent-info">
                        <div class="swarm-agent-name">${agent.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
                        <div class="swarm-agent-role">${escapeHtml(info.description || info.expertise || '')}</div>
                    </div>
                </div>
            `).join('');
            
            grid.innerHTML = html;
        }

        // ═══════════════════════════════════════════════════════════════
        // Sandbox Tab Functions
        // ═══════════════════════════════════════════════════════════════

        let sandboxState = {
            executing: false
        };

        // Run sandbox code
        async function runSandbox() {
            const codeInput = document.getElementById('sandboxCode');
            const code = codeInput.value.trim();
            
            if (!code) {
                alert('Please enter code to execute');
                return;
            }
            
            if (sandboxState.executing) {
                alert('Code is already executing');
                return;
            }
            
            const language = document.getElementById('sandboxLanguage').value;
            const sandboxType = document.getElementById('sandboxType').value;
            const timeout = parseInt(document.getElementById('sandboxTimeout').value) || 30;
            const runBtn = document.getElementById('sandboxRunBtn');
            const outputContainer = document.getElementById('sandboxOutputContainer');
            
            try {
                sandboxState.executing = true;
                runBtn.disabled = true;
                runBtn.innerHTML = '⏳ Running...';
                
                outputContainer.innerHTML = `
                    <div class="sandbox-empty-state">
                        <div class="tools-loading-spinner"></div>
                        <div style="margin-top: 12px;">Executing code...</div>
                    </div>
                `;
                
                const response = await fetch(`${API_BASE}/api/sandbox/run`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        code,
                        language,
                        sandbox_type: sandboxType,
                        timeout
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                displaySandboxResults(data);
                
            } catch (error) {
                console.error('Error running sandbox:', error);
                outputContainer.innerHTML = `
                    <div class="sandbox-output-section">
                        <span class="sandbox-output-label">Error</span>
                        <div class="sandbox-output-content stderr">${escapeHtml(error.message)}</div>
                    </div>
                `;
            } finally {
                sandboxState.executing = false;
                runBtn.disabled = false;
                runBtn.innerHTML = '▶️ Run Code';
            }
        }

        // Display sandbox results
        function displaySandboxResults(data) {
            const container = document.getElementById('sandboxOutputContainer');
            
            const exitStatus = data.exit_code === 0 ? 'success' : 'error';
            const exitText = data.exit_code === 0 ? 'Success' : 'Failed';
            
            const html = `
                <div class="sandbox-output-section">
                    <span class="sandbox-output-label">Standard Output</span>
                    <div class="sandbox-output-content stdout">${escapeHtml(data.stdout || '(empty)')}</div>
                </div>
                
                ${data.stderr ? `
                <div class="sandbox-output-section">
                    <span class="sandbox-output-label">Standard Error</span>
                    <div class="sandbox-output-content stderr">${escapeHtml(data.stderr)}</div>
                </div>
                ` : ''}
                
                <div class="sandbox-output-meta">
                    <div class="sandbox-meta-item">
                        <span class="sandbox-meta-label">Exit Code:</span>
                        <span class="sandbox-meta-value ${exitStatus}">${data.exit_code}</span>
                    </div>
                    <div class="sandbox-meta-item">
                        <span class="sandbox-meta-label">Status:</span>
                        <span class="sandbox-meta-value ${exitStatus}">${exitText}</span>
                    </div>
                    <div class="sandbox-meta-item">
                        <span class="sandbox-meta-label">Execution Time:</span>
                        <span class="sandbox-meta-value">${data.execution_time?.toFixed(3) || '0.000'}s</span>
                    </div>
                    ${data.sandbox_type ? `
                    <div class="sandbox-meta-item">
                        <span class="sandbox-meta-label">Sandbox:</span>
                        <span class="sandbox-meta-value">${data.sandbox_type}</span>
                    </div>
                    ` : ''}
                </div>
            `;
            
            container.innerHTML = html;
        }

        // Clear sandbox
        function clearSandbox() {
            document.getElementById('sandboxCode').value = '';
            document.getElementById('sandboxOutputContainer').innerHTML = `
                <div class="sandbox-empty-state">
                    Run code to see output
                </div>
            `;
        }

        // Load sandbox status
        async function loadSandboxStatus() {
            try {
                const response = await fetch(`${API_BASE}/api/sandbox/status`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('Sandbox status:', data);
            } catch (error) {
                console.error('Error loading sandbox status:', error);
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // Tools Tab Functions
        // ═══════════════════════════════════════════════════════════════

        let toolsState = {
            mcpServers: [],
            tools: [],
            allTools: [],
            selectedTool: null
        };

        // Load MCP servers
        async function loadMCPServers() {
            const grid = document.getElementById('toolsMCPServersGrid');
            
            try {
                grid.innerHTML = `
                    <div class="tools-loading">
                        <div class="tools-loading-spinner"></div>
                        <div>Loading MCP servers...</div>
                    </div>
                `;
                
                const response = await fetch(`${API_BASE}/mcp/status`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                toolsState.mcpServers = data.servers || [];
                displayMCPServers(data.servers || []);
                
            } catch (error) {
                console.error('Error loading MCP servers:', error);
                grid.innerHTML = `
                    <div class="tools-empty-state">
                        Failed to load MCP servers<br>
                        <small>${escapeHtml(error.message)}</small>
                    </div>
                `;
            }
        }

        // Display MCP servers
        function displayMCPServers(servers) {
            const grid = document.getElementById('toolsMCPServersGrid');
            
            if (servers.length === 0) {
                grid.innerHTML = `
                    <div class="tools-empty-state">
                        No MCP servers configured
                    </div>
                `;
                return;
            }
            
            const html = servers.map(server => {
                const isRunning = server.status === 'running' || server.running === true;
                const statusClass = isRunning ? 'running' : 'stopped';
                const statusText = isRunning ? '● Running' : '○ Stopped';
                const toolCount = server.tool_count || server.tools?.length || 0;
                
                return `
                    <div class="tools-mcp-server-card">
                        <div class="tools-mcp-server-header">
                            <div class="tools-mcp-server-name">${escapeHtml(server.name || server.server || 'Unknown')}</div>
                            <div class="tools-mcp-server-status ${statusClass}">${statusText}</div>
                        </div>
                        <div class="tools-mcp-server-info">
                            ${toolCount} tool${toolCount !== 1 ? 's' : ''} available
                        </div>
                    </div>
                `;
            }).join('');
            
            grid.innerHTML = html;
        }

        // Load tools list
        async function loadToolsList() {
            const list = document.getElementById('toolsList');
            
            try {
                list.innerHTML = `
                    <div class="tools-loading">
                        <div class="tools-loading-spinner"></div>
                        <div>Discovering tools...</div>
                    </div>
                `;
                
                const response = await fetch(`${API_BASE}/mcp/tools`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                toolsState.allTools = data.tools || [];
                toolsState.tools = data.tools || [];
                displayToolsList(toolsState.tools);
                
            } catch (error) {
                console.error('Error loading tools:', error);
                list.innerHTML = `
                    <div class="tools-empty-state">
                        Failed to load tools<br>
                        <small>${escapeHtml(error.message)}</small>
                    </div>
                `;
            }
        }

        // Display tools list
        function displayToolsList(tools) {
            const list = document.getElementById('toolsList');
            
            if (tools.length === 0) {
                list.innerHTML = `
                    <div class="tools-empty-state">
                        No tools discovered
                    </div>
                `;
                return;
            }
            
            const html = tools.map(tool => `
                <div class="tools-item" onclick="selectTool('${escapeHtml(tool.name)}', '${escapeHtml(tool.server || '')}')">
                    <div class="tools-item-header">
                        <div class="tools-item-name">${escapeHtml(tool.name)}</div>
                        ${tool.server ? `<div class="tools-item-server">${escapeHtml(tool.server)}</div>` : ''}
                    </div>
                    ${tool.description ? `<div class="tools-item-description">${escapeHtml(tool.description)}</div>` : ''}
                </div>
            `).join('');
            
            list.innerHTML = html;
        }

        // Filter tools
        function filterTools() {
            const searchInput = document.getElementById('toolsSearchInput');
            const query = searchInput.value.toLowerCase().trim();
            
            if (!query) {
                toolsState.tools = toolsState.allTools;
            } else {
                toolsState.tools = toolsState.allTools.filter(tool => {
                    return tool.name.toLowerCase().includes(query) ||
                           (tool.description && tool.description.toLowerCase().includes(query)) ||
                           (tool.server && tool.server.toLowerCase().includes(query));
                });
            }
            
            displayToolsList(toolsState.tools);
        }

        // Select tool
        async function selectTool(toolName, serverName) {
            try {
                // Remove quotes if present
                toolName = toolName.replace(/['"]/g, '');
                serverName = serverName.replace(/['"]/g, '');
                
                // Highlight selected tool
                document.querySelectorAll('.tools-item').forEach(item => {
                    item.classList.remove('selected');
                });
                event.currentTarget.classList.add('selected');
                
                // Load tool details
                const response = await fetch(`${API_BASE}/mcp/tools/${encodeURIComponent(toolName)}?server=${encodeURIComponent(serverName)}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                toolsState.selectedTool = { ...data, name: toolName, server: serverName };
                displayToolDetails(toolsState.selectedTool);
                
            } catch (error) {
                console.error('Error loading tool details:', error);
                alert(`Failed to load tool details: ${error.message}`);
            }
        }

        // Display tool details
        function displayToolDetails(tool) {
            const detailsSection = document.getElementById('toolDetailsSection');
            const testSection = document.getElementById('toolTestSection');
            const detailsPanel = document.getElementById('toolDetailsPanel');
            
            detailsSection.style.display = 'block';
            testSection.style.display = 'block';
            
            const html = `
                <div class="tools-details-name">
                    🔧 ${escapeHtml(tool.name)}
                    ${tool.server ? `<span class="tools-item-server">${escapeHtml(tool.server)}</span>` : ''}
                </div>
                
                ${tool.description ? `
                <div class="tools-details-section">
                    <span class="tools-details-label">Description</span>
                    <div class="tools-details-value">${escapeHtml(tool.description)}</div>
                </div>
                ` : ''}
                
                ${tool.inputSchema || tool.input_schema ? `
                <div class="tools-details-section">
                    <span class="tools-details-label">Input Schema</span>
                    <div class="tools-schema-display">${escapeHtml(JSON.stringify(tool.inputSchema || tool.input_schema, null, 2))}</div>
                </div>
                ` : ''}
                
                ${tool.parameters ? `
                <div class="tools-details-section">
                    <span class="tools-details-label">Parameters</span>
                    <div class="tools-schema-display">${escapeHtml(JSON.stringify(tool.parameters, null, 2))}</div>
                </div>
                ` : ''}
            `;
            
            detailsPanel.innerHTML = html;
            
            // Populate test input with example
            const testInput = document.getElementById('toolTestInput');
            if (tool.inputSchema || tool.input_schema || tool.parameters) {
                const schema = tool.inputSchema || tool.input_schema || tool.parameters;
                const example = generateExampleFromSchema(schema);
                testInput.value = JSON.stringify(example, null, 2);
            } else {
                testInput.value = '{}';
            }
        }

        // Generate example from schema
        function generateExampleFromSchema(schema) {
            const example = {};
            
            if (schema.properties) {
                for (const [key, prop] of Object.entries(schema.properties)) {
                    if (prop.type === 'string') {
                        example[key] = prop.default || `example_${key}`;
                    } else if (prop.type === 'number' || prop.type === 'integer') {
                        example[key] = prop.default || 0;
                    } else if (prop.type === 'boolean') {
                        example[key] = prop.default || false;
                    } else if (prop.type === 'array') {
                        example[key] = [];
                    } else if (prop.type === 'object') {
                        example[key] = {};
                    } else {
                        example[key] = null;
                    }
                }
            }
            
            return example;
        }

        // Test tool
        async function testTool() {
            if (!toolsState.selectedTool) {
                alert('Please select a tool first');
                return;
            }
            
            const testInput = document.getElementById('toolTestInput');
            const testBtn = document.getElementById('toolTestBtn');
            const resultContainer = document.getElementById('toolTestResultContainer');
            const resultDisplay = document.getElementById('toolTestResult');
            
            let args;
            try {
                args = JSON.parse(testInput.value);
            } catch (error) {
                alert('Invalid JSON in arguments');
                return;
            }
            
            try {
                testBtn.disabled = true;
                testBtn.innerHTML = '⏳ Executing...';
                
                resultContainer.style.display = 'block';
                resultDisplay.textContent = 'Executing tool...';
                
                const response = await fetch(`${API_BASE}/mcp/tools/${encodeURIComponent(toolsState.selectedTool.name)}/execute`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        server: toolsState.selectedTool.server,
                        arguments: args
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                resultDisplay.textContent = JSON.stringify(data, null, 2);
                
            } catch (error) {
                console.error('Error testing tool:', error);
                resultDisplay.textContent = `Error: ${error.message}`;
            } finally {
                testBtn.disabled = false;
                testBtn.innerHTML = '🚀 Execute Tool';
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // Model Rotator Functions
        // ═══════════════════════════════════════════════════════════════
        
        // State for rotator
        const rotatorState = {
            keys: [],
            stats: {},
            refreshInterval: null
        };

        // Show toast notification
        function showRotatorToast(message, type = 'success') {
            const toast = document.createElement('div');
            toast.className = `rotator-toast ${type}`;
            toast.textContent = message;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.style.animation = 'slideInRight 0.3s ease reverse';
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }

        // Add new API key
        async function addRotatorKey() {
            const service = document.getElementById('rotatorService').value;
            const apiKey = document.getElementById('rotatorApiKey').value;
            const keyName = document.getElementById('rotatorKeyName').value;
            
            if (!apiKey) {
                showRotatorToast('Please enter an API key', 'error');
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/api/rotator/keys`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        service: service,
                        api_key: apiKey,
                        name: keyName || `${service.charAt(0).toUpperCase() + service.slice(1)} Key`
                    })
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to add key');
                }
                
                showRotatorToast('API key added successfully', 'success');
                
                // Clear form
                document.getElementById('rotatorApiKey').value = '';
                document.getElementById('rotatorKeyName').value = '';
                
                // Refresh keys list
                await loadRotatorKeys();
                
            } catch (error) {
                console.error('Error adding key:', error);
                showRotatorToast(error.message, 'error');
            }
        }

        // Load all keys
        async function loadRotatorKeys() {
            try {
                const response = await fetch(`${API_BASE}/api/rotator/stats`);
                
                if (!response.ok) {
                    throw new Error('Failed to load keys');
                }
                
                const data = await response.json();
                rotatorState.keys = data.keys || [];
                rotatorState.stats = data.stats || {};
                
                displayRotatorKeys();
                displayRotatorStats(data);
                displayRotatorMonitor(data);
                
            } catch (error) {
                console.error('Error loading keys:', error);
                const grid = document.getElementById('rotatorKeysGrid');
                grid.innerHTML = '<div class="rotator-empty">Failed to load keys. Please try again.</div>';
            }
        }

        // Display keys in grid
        function displayRotatorKeys() {
            const grid = document.getElementById('rotatorKeysGrid');
            
            if (rotatorState.keys.length === 0) {
                grid.innerHTML = '<div class="rotator-empty">No API keys configured. Add your first key above!</div>';
                return;
            }
            
            const html = rotatorState.keys.map(key => {
                const healthScore = key.health_score || 0;
                const healthClass = healthScore >= 90 ? 'excellent' : 
                                   healthScore >= 70 ? 'good' : 
                                   healthScore >= 50 ? 'fair' : 'poor';
                
                const successRate = key.success_rate || 0;
                const requests = key.total_requests || 0;
                
                return `
                    <div class="rotator-key-card ${key.status === 'disabled' ? 'disabled' : ''}">
                        <div class="rotator-key-header">
                            <div>
                                <div class="rotator-key-name">${escapeHtml(key.name)}</div>
                                <div class="rotator-key-service">${escapeHtml(key.service)}</div>
                            </div>
                            <div class="rotator-key-status ${escapeHtml(key.status)}"></div>
                        </div>
                        
                        <div class="rotator-key-metrics">
                            <div class="rotator-metric">
                                <span class="rotator-metric-value">${successRate.toFixed(1)}%</span>
                                <span class="rotator-metric-label">Success Rate</span>
                            </div>
                            <div class="rotator-metric">
                                <span class="rotator-metric-value">${requests}</span>
                                <span class="rotator-metric-label">Requests</span>
                            </div>
                        </div>
                        
                        <div class="rotator-health-bar">
                            <div class="rotator-health-fill ${healthClass}" style="width: ${healthScore}%"></div>
                        </div>
                        
                        <div class="rotator-key-actions">
                            ${key.status === 'disabled' ? 
                                `<button class="rotator-btn rotator-btn-secondary" onclick="enableRotatorKey('${escapeHtml(key.key_hash)}')">
                                    ✓ Enable
                                </button>` :
                                `<button class="rotator-btn rotator-btn-secondary" onclick="disableRotatorKey('${escapeHtml(key.key_hash)}')">
                                    ⏸ Disable
                                </button>`
                            }
                            <button class="rotator-btn rotator-btn-danger" onclick="removeRotatorKey('${escapeHtml(key.key_hash)}', '${escapeHtml(key.name)}')">
                                🗑️ Remove
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
            
            grid.innerHTML = html;
        }

        // Display statistics dashboard
        function displayRotatorStats(data) {
            const statsGrid = document.getElementById('rotatorStatsGrid');
            const stats = data.stats || {};
            
            const totalRequests = Object.values(stats).reduce((sum, s) => sum + (s.total_requests || 0), 0);
            const totalSuccess = Object.values(stats).reduce((sum, s) => sum + (s.successful_requests || 0), 0);
            const totalTokens = Object.values(stats).reduce((sum, s) => sum + (s.total_tokens || 0), 0);
            const avgSuccessRate = totalRequests > 0 ? (totalSuccess / totalRequests * 100) : 0;
            
            const html = `
                <div class="rotator-stat-card">
                    <span class="rotator-stat-value">${totalRequests}</span>
                    <span class="rotator-stat-label">Total Requests</span>
                </div>
                <div class="rotator-stat-card">
                    <span class="rotator-stat-value">${avgSuccessRate.toFixed(1)}%</span>
                    <span class="rotator-stat-label">Success Rate</span>
                </div>
                <div class="rotator-stat-card">
                    <span class="rotator-stat-value">${totalTokens.toLocaleString()}</span>
                    <span class="rotator-stat-label">Tokens Used</span>
                </div>
                <div class="rotator-stat-card">
                    <span class="rotator-stat-value">${rotatorState.keys.length}</span>
                    <span class="rotator-stat-label">Active Keys</span>
                </div>
            `;
            
            statsGrid.innerHTML = html;
            
            // Update usage chart
            displayRotatorUsageChart(data.keys || []);
        }

        // Display usage chart
        function displayRotatorUsageChart(keys) {
            const chartContainer = document.getElementById('rotatorUsageChart');
            
            if (keys.length === 0) {
                chartContainer.innerHTML = '<div class="rotator-empty" style="padding: 20px;">No data available</div>';
                return;
            }
            
            const maxRequests = Math.max(...keys.map(k => k.total_requests || 0), 1);
            
            const html = keys.map(key => {
                const requests = key.total_requests || 0;
                const percentage = (requests / maxRequests) * 100;
                
                return `
                    <div class="rotator-chart-bar">
                        <div class="rotator-chart-label">${escapeHtml(key.name)}</div>
                        <div class="rotator-chart-track">
                            <div class="rotator-chart-fill" style="width: ${percentage}%"></div>
                        </div>
                        <div class="rotator-chart-value">${requests}</div>
                    </div>
                `;
            }).join('');
            
            chartContainer.innerHTML = html;
        }

        // Display monitoring panel
        function displayRotatorMonitor(data) {
            const monitorGrid = document.getElementById('rotatorMonitorGrid');
            const keys = data.keys || [];
            
            if (keys.length === 0) {
                monitorGrid.innerHTML = '<div class="rotator-empty">No keys to monitor</div>';
                return;
            }
            
            const html = keys.map(key => {
                const status = key.status || 'unknown';
                const statusText = status.replace('_', ' ').toUpperCase();
                const errorCount = key.error_count || 0;
                const lastUsed = key.last_used ? new Date(key.last_used).toLocaleString() : 'Never';
                
                return `
                    <div class="rotator-monitor-item">
                        <div class="rotator-monitor-label">${escapeHtml(key.name)}</div>
                        <div class="rotator-monitor-value">${statusText}</div>
                    </div>
                    <div class="rotator-monitor-item">
                        <div class="rotator-monitor-label">Errors</div>
                        <div class="rotator-monitor-value" style="color: ${errorCount > 0 ? 'var(--error)' : 'var(--success)'}">
                            ${errorCount}
                        </div>
                    </div>
                    <div class="rotator-monitor-item">
                        <div class="rotator-monitor-label">Last Used</div>
                        <div class="rotator-monitor-value">${lastUsed}</div>
                    </div>
                `;
            }).join('');
            
            monitorGrid.innerHTML = html;
        }

        // Enable key
        async function enableRotatorKey(keyHash) {
            try {
                const response = await fetch(`${API_BASE}/api/rotator/keys/enable`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key_hash: keyHash })
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to enable key');
                }
                
                showRotatorToast('Key enabled successfully', 'success');
                await loadRotatorKeys();
                
            } catch (error) {
                console.error('Error enabling key:', error);
                showRotatorToast(error.message, 'error');
            }
        }

        // Disable key
        async function disableRotatorKey(keyHash) {
            try {
                const response = await fetch(`${API_BASE}/api/rotator/keys/disable`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key_hash: keyHash })
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to disable key');
                }
                
                showRotatorToast('Key disabled successfully', 'success');
                await loadRotatorKeys();
                
            } catch (error) {
                console.error('Error disabling key:', error);
                showRotatorToast(error.message, 'error');
            }
        }

        // Remove key
        async function removeRotatorKey(keyHash, keyName) {
            if (!confirm(`Are you sure you want to remove "${keyName}"?\n\nThis action cannot be undone.`)) {
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/api/rotator/keys`, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key_hash: keyHash })
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to remove key');
                }
                
                showRotatorToast('Key removed successfully', 'success');
                await loadRotatorKeys();
                
            } catch (error) {
                console.error('Error removing key:', error);
                showRotatorToast(error.message, 'error');
            }
        }

        // Refresh stats
        async function refreshRotatorStats() {
            showRotatorToast('Refreshing statistics...', 'success');
            await loadRotatorKeys();
        }

        // Reset stats
        async function resetRotatorStats() {
            if (!confirm('Are you sure you want to reset all statistics?\n\nThis will clear all counters but keep your API keys.')) {
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/api/rotator/stats/reset`, {
                    method: 'POST'
                });
                
                if (!response.ok) {
                    throw new Error('Failed to reset statistics');
                }
                
                showRotatorToast('Statistics reset successfully', 'success');
                await loadRotatorKeys();
                
            } catch (error) {
                console.error('Error resetting stats:', error);
                showRotatorToast(error.message, 'error');
            }
        }

        // Export stats
        function exportRotatorStats() {
            const exportData = {
                timestamp: new Date().toISOString(),
                keys: rotatorState.keys,
                stats: rotatorState.stats
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `rotator-stats-${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showRotatorToast('Statistics exported successfully', 'success');
        }

        // Start auto-refresh for monitoring
        function startRotatorAutoRefresh() {
            if (rotatorState.refreshInterval) {
                clearInterval(rotatorState.refreshInterval);
            }
            
            rotatorState.refreshInterval = setInterval(() => {
                const panel = document.getElementById('rotator-panel');
                if (panel && panel.classList.contains('active')) {
                    loadRotatorKeys();
                }
            }, 5000); // Refresh every 5 seconds
        }

        // Stop auto-refresh
        function stopRotatorAutoRefresh() {
            if (rotatorState.refreshInterval) {
                clearInterval(rotatorState.refreshInterval);
                rotatorState.refreshInterval = null;
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // Initialize New Tabs
        // ═══════════════════════════════════════════════════════════════

        // Add initialization for new tabs
        function initializeNewTabs() {
            // Initialize when tabs are switched
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.attributeName === 'class') {
                        const target = mutation.target;
                        if (target.id === 'swarm-panel' && target.classList.contains('active')) {
                            loadSwarmCapabilities();
                        } else if (target.id === 'sandbox-panel' && target.classList.contains('active')) {
                            loadSandboxStatus();
                        } else if (target.id === 'tools-panel' && target.classList.contains('active')) {
                            if (toolsState.tools.length === 0) {
                                loadMCPServers();
                                loadToolsList();
                            }
                        } else if (target.id === 'rotator-panel' && target.classList.contains('active')) {
                            if (rotatorState.keys.length === 0) {
                                loadRotatorKeys();
                            }
                            startRotatorAutoRefresh();
                        } else if (target.id !== 'rotator-panel' && !target.classList.contains('active')) {
                            // Stop auto-refresh when leaving rotator panel
                            stopRotatorAutoRefresh();
                        }
                    }
                });
            });
            
            // Observe all content panels
            document.querySelectorAll('.content-panel').forEach(panel => {
                observer.observe(panel, { attributes: true, attributeFilter: ['class'] });
            });
        }

        // Call initialization after DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initializeNewTabs);
        } else {
            initializeNewTabs();
        }

        // ═══════════════════════════════════════════════════════════════
        // End Debug Panel
        // ═══════════════════════════════════════════════════════════════

        // Periodic file refresh
        setInterval(fetchFiles, 10000);