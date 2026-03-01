import { useMcp } from 'use-mcp/react';
import { useState } from 'react';

/**
 * Advanced MCP Dashboard with Tool Invocation
 * 
 * Features:
 * - Tool execution with parameter input
 * - Execution history
 * - Auto-retry on connection failure
 * - Custom gateway URL configuration
 */
export function AdvancedMCPDashboard() {
  const [gatewayUrl, setGatewayUrl] = useState(
    process.env.REACT_APP_MCP_GATEWAY_URL || 'http://localhost:15000/mcp'
  );
  const [isEnabled, setIsEnabled] = useState(true);
  const [executionHistory, setExecutionHistory] = useState<Array<{
    toolName: string;
    params: any;
    result: any;
    timestamp: Date;
    success: boolean;
  }>>([]);
  const [selectedTool, setSelectedTool] = useState<string | null>(null);
  const [toolParams, setToolParams] = useState<Record<string, any>>({});

  const {
    state,
    tools,
    error,
    callTool,
    retry
  } = useMcp({
    url: gatewayUrl,
    enabled: isEnabled,
    logLevel: 'normal'
  });

  // Auto-retry on failure
  useState(() => {
    if (state === 'failed') {
      const timer = setTimeout(() => {
        console.log('Auto-retrying connection in 5 seconds...');
        retry();
      }, 5000);
      return () => clearTimeout(timer);
    }
  });

  const handleToolExecution = async () => {
    if (!selectedTool) return;

    try {
      const result = await callTool(selectedTool, toolParams);
      
      setExecutionHistory(prev => [{
        toolName: selectedTool,
        params: toolParams,
        result,
        timestamp: new Date(),
        success: true
      }, ...prev]);

      // Clear params
      setToolParams({});
      alert('Tool executed successfully!');
    } catch (err: any) {
      setExecutionHistory(prev => [{
        toolName: selectedTool,
        params: toolParams,
        result: err.message,
        timestamp: new Date(),
        success: false
      }, ...prev]);

      alert(`Tool execution failed: ${err.message}`);
    }
  };

  const getStatusColor = () => {
    switch (state) {
      case 'ready': return '#28a745';
      case 'failed': return '#dc3545';
      case 'connecting': return '#ffc107';
      case 'loading': return '#17a2b8';
      default: return '#6c757d';
    }
  };

  const currentTool = tools.find(t => t.name === selectedTool);

  return (
    <div className="advanced-mcp-dashboard">
      {/* Header with connection controls */}
      <header className="dashboard-header">
        <h1>MCP Tools Dashboard</h1>
        
        <div className="connection-controls">
          <div className="status-badge" style={{ backgroundColor: getStatusColor() }}>
            {state}
          </div>
          
          <input
            type="text"
            value={gatewayUrl}
            onChange={(e) => setGatewayUrl(e.target.value)}
            placeholder="Gateway URL"
            className="gateway-url-input"
            disabled={isEnabled}
          />
          
          <button
            onClick={() => setIsEnabled(!isEnabled)}
            className={`connection-toggle ${isEnabled ? 'connected' : 'disconnected'}`}
          >
            {isEnabled ? 'Disconnect' : 'Connect'}
          </button>

          {state === 'failed' && (
            <button onClick={retry} className="retry-button">
              Retry
            </button>
          )}
        </div>
      </header>

      {error && (
        <div className="error-banner">
          <strong>Error:</strong> {error}
        </div>
      )}

      {state === 'ready' && (
        <div className="dashboard-content">
          {/* Left panel: Tool list */}
          <aside className="tools-panel">
            <h2>Available Tools ({tools.length})</h2>
            
            <div className="tools-list">
              {tools.map((tool) => (
                <div
                  key={tool.name}
                  className={`tool-item ${selectedTool === tool.name ? 'selected' : ''}`}
                  onClick={() => setSelectedTool(tool.name)}
                >
                  <h3>{tool.name}</h3>
                  <p>{tool.description}</p>
                </div>
              ))}
            </div>
          </aside>

          {/* Center panel: Tool execution */}
          <main className="execution-panel">
            {currentTool ? (
              <>
                <h2>Execute: {currentTool.name}</h2>
                <p className="tool-description">{currentTool.description}</p>

                {currentTool.inputSchema && (
                  <div className="parameter-inputs">
                    <h3>Parameters</h3>
                    
                    {Object.entries(currentTool.inputSchema.properties || {}).map(([key, schema]: [string, any]) => (
                      <div key={key} className="parameter-field">
                        <label>
                          {key}
                          {currentTool.inputSchema.required?.includes(key) && (
                            <span className="required">*</span>
                          )}
                        </label>
                        
                        <input
                          type={schema.type === 'number' ? 'number' : 'text'}
                          value={toolParams[key] || ''}
                          onChange={(e) => setToolParams(prev => ({
                            ...prev,
                            [key]: schema.type === 'number' ? Number(e.target.value) : e.target.value
                          }))}
                          placeholder={schema.description}
                          className="parameter-input"
                        />
                        
                        <small className="parameter-hint">{schema.description}</small>
                      </div>
                    ))}

                    <button
                      onClick={handleToolExecution}
                      className="execute-button"
                    >
                      Execute Tool
                    </button>
                  </div>
                )}

                <details className="schema-details">
                  <summary>View Full Schema</summary>
                  <pre>{JSON.stringify(currentTool.inputSchema, null, 2)}</pre>
                </details>
              </>
            ) : (
              <div className="no-selection">
                <p>Select a tool from the list to execute it</p>
              </div>
            )}
          </main>

          {/* Right panel: Execution history */}
          <aside className="history-panel">
            <h2>Execution History</h2>
            
            <div className="history-list">
              {executionHistory.length === 0 ? (
                <p className="no-history">No executions yet</p>
              ) : (
                executionHistory.map((item, idx) => (
                  <div
                    key={idx}
                    className={`history-item ${item.success ? 'success' : 'error'}`}
                  >
                    <div className="history-header">
                      <strong>{item.toolName}</strong>
                      <span className="timestamp">
                        {item.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    
                    <details>
                      <summary>View Details</summary>
                      <div className="history-details">
                        <div>
                          <strong>Parameters:</strong>
                          <pre>{JSON.stringify(item.params, null, 2)}</pre>
                        </div>
                        <div>
                          <strong>Result:</strong>
                          <pre>{JSON.stringify(item.result, null, 2)}</pre>
                        </div>
                      </div>
                    </details>
                  </div>
                ))
              )}
            </div>

            {executionHistory.length > 0 && (
              <button
                onClick={() => setExecutionHistory([])}
                className="clear-history-button"
              >
                Clear History
              </button>
            )}
          </aside>
        </div>
      )}

      {state !== 'ready' && state !== 'failed' && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Connecting to gateway...</p>
        </div>
      )}
    </div>
  );
}

// Styles can be extracted to a separate CSS file
const styles = `
.advanced-mcp-dashboard {
  min-height: 100vh;
  background: #f5f5f5;
}

.dashboard-header {
  background: white;
  padding: 20px 30px;
  border-bottom: 2px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.connection-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  color: white;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.gateway-url-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 300px;
}

.connection-toggle {
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.connection-toggle.connected {
  background: #dc3545;
  color: white;
}

.connection-toggle.disconnected {
  background: #28a745;
  color: white;
}

.error-banner {
  background: #f8d7da;
  color: #721c24;
  padding: 15px 30px;
  border-bottom: 1px solid #f5c6cb;
}

.dashboard-content {
  display: grid;
  grid-template-columns: 300px 1fr 350px;
  gap: 20px;
  padding: 20px;
  min-height: calc(100vh - 100px);
}

.tools-panel, .execution-panel, .history-panel {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.tools-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.tool-item {
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.tool-item:hover {
  background: #f8f9fa;
  border-color: #3498db;
}

.tool-item.selected {
  background: #e3f2fd;
  border-color: #2196f3;
}

.tool-item h3 {
  margin: 0 0 5px 0;
  font-size: 14px;
  color: #2c3e50;
}

.tool-item p {
  margin: 0;
  font-size: 12px;
  color: #666;
}

.parameter-inputs {
  margin: 20px 0;
}

.parameter-field {
  margin-bottom: 15px;
}

.parameter-field label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #333;
}

.required {
  color: #dc3545;
  margin-left: 3px;
}

.parameter-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.parameter-hint {
  display: block;
  margin-top: 3px;
  color: #666;
  font-size: 12px;
}

.execute-button {
  background: #2196f3;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  margin-top: 10px;
}

.execute-button:hover {
  background: #1976d2;
}

.history-list {
  max-height: calc(100vh - 250px);
  overflow-y: auto;
}

.history-item {
  padding: 12px;
  margin-bottom: 10px;
  border-left: 4px solid;
  background: #f9f9f9;
  border-radius: 4px;
}

.history-item.success {
  border-left-color: #28a745;
}

.history-item.error {
  border-left-color: #dc3545;
}

.history-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.timestamp {
  font-size: 12px;
  color: #666;
}

.clear-history-button {
  width: 100%;
  padding: 10px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
`;

export default AdvancedMCPDashboard;
