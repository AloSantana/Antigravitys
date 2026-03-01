import { useMcp } from 'use-mcp/react';

/**
 * Basic MCP Dashboard Component
 * 
 * Connects to an MCP gateway and displays available tools
 */
export function BasicMCPDashboard() {
  const {
    state,
    tools,
    error,
    retry
  } = useMcp({
    url: process.env.REACT_APP_MCP_GATEWAY_URL || 'http://localhost:15000/mcp',
    enabled: true,
    logLevel: 'normal'
  });

  // Loading state
  if (state === 'discovering' || state === 'connecting' || state === 'loading') {
    return (
      <div className="mcp-dashboard loading">
        <div className="spinner"></div>
        <p>Connecting to MCP gateway...</p>
        <p className="status">Status: {state}</p>
      </div>
    );
  }

  // Error state
  if (state === 'failed') {
    return (
      <div className="mcp-dashboard error">
        <h2>Connection Failed</h2>
        <p className="error-message">{error}</p>
        <button onClick={retry} className="retry-button">
          Retry Connection
        </button>
      </div>
    );
  }

  // Connected state
  return (
    <div className="mcp-dashboard ready">
      <header>
        <h1>MCP Tools Dashboard</h1>
        <div className="status-indicator connected">
          <span className="dot"></span>
          Connected
        </div>
      </header>

      <section className="tools-section">
        <h2>Available Tools ({tools.length})</h2>
        
        {tools.length === 0 ? (
          <p className="no-tools">No tools available from gateway</p>
        ) : (
          <div className="tools-grid">
            {tools.map((tool) => (
              <div key={tool.name} className="tool-card">
                <h3>{tool.name}</h3>
                <p className="tool-description">{tool.description}</p>
                {tool.inputSchema && (
                  <details>
                    <summary>View Schema</summary>
                    <pre>{JSON.stringify(tool.inputSchema, null, 2)}</pre>
                  </details>
                )}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

// CSS Module (basic-mcp-dashboard.module.css)
const styles = `
.mcp-dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.mcp-dashboard.loading {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.status {
  color: #666;
  font-size: 14px;
  margin-top: 10px;
}

.mcp-dashboard.error {
  text-align: center;
  padding: 60px 20px;
}

.error-message {
  color: #e74c3c;
  background: #fadbd8;
  padding: 15px;
  border-radius: 4px;
  margin: 20px 0;
}

.retry-button {
  background: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.retry-button:hover {
  background: #2980b9;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  border-bottom: 2px solid #eee;
  padding-bottom: 15px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.status-indicator.connected {
  background: #d4edda;
  color: #155724;
}

.status-indicator .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #28a745;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.tools-section h2 {
  margin-bottom: 20px;
}

.no-tools {
  text-align: center;
  color: #999;
  padding: 40px;
  background: #f9f9f9;
  border-radius: 4px;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.tool-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: white;
  transition: box-shadow 0.2s;
}

.tool-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.tool-card h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.tool-description {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.tool-card details {
  margin-top: 15px;
}

.tool-card summary {
  cursor: pointer;
  color: #3498db;
  font-size: 13px;
}

.tool-card pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  margin-top: 10px;
}
`;

export default BasicMCPDashboard;
