"""
Settings Manager for Antigravity Workspace.

Manages configuration, API keys, MCP servers, and environment variables
with secure storage and validation capabilities.
"""

import os
import json
import logging
from typing import Dict, Any, List, Set
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet
from dotenv import load_dotenv, set_key

logger = logging.getLogger(__name__)


class SettingsManager:
    """
    Centralized settings management for configuration, API keys, MCP servers,
    and environment variables with encryption support.
    """
    
    # Environment variables that should never be exposed
    SENSITIVE_VARS: Set[str] = {
        'GEMINI_API_KEY',
        'ANTHROPIC_API_KEY',
        'OPENAI_API_KEY',
        'OPENROUTER_API_KEY',
        'VERTEX_API_KEY',
        'GOOGLE_APPLICATION_CREDENTIALS',
        'COPILOT_MCP_GITHUB_TOKEN',
        'COPILOT_MCP_BRAVE_API_KEY',
        'COPILOT_MCP_POSTGRES_CONNECTION_STRING',
        'DATABASE_URL',
        'SECRET_KEY',
        'JWT_SECRET',
        'ENCRYPTION_KEY'
    }
    
    # Available AI models
    AVAILABLE_MODELS: List[Dict[str, Any]] = [
        {
            'id': 'gemini',
            'name': 'Google Gemini',
            'description': 'Google\'s Gemini 2.0 Flash model',
            'requires_key': True,
            'key_var': 'GEMINI_API_KEY'
        },
        {
            'id': 'vertex',
            'name': 'Google Vertex AI',
            'description': 'Google Cloud Vertex AI models',
            'requires_key': True,
            'key_var': 'VERTEX_API_KEY'
        },
        {
            'id': 'anthropic',
            'name': 'Anthropic Claude',
            'description': 'Anthropic Claude models (claude-sonnet, claude-opus)',
            'requires_key': True,
            'key_var': 'ANTHROPIC_API_KEY'
        },
        {
            'id': 'openai',
            'name': 'OpenAI',
            'description': 'OpenAI GPT models (GPT-4, GPT-4o)',
            'requires_key': True,
            'key_var': 'OPENAI_API_KEY'
        },
        {
            'id': 'openrouter',
            'name': 'OpenRouter',
            'description': 'OpenRouter — access 200+ models via a single API',
            'requires_key': True,
            'key_var': 'OPENROUTER_API_KEY'
        },
        {
            'id': 'ollama',
            'name': 'Ollama (Local)',
            'description': 'Local LLMs via Ollama',
            'requires_key': False,
            'key_var': None
        }
    ]
    
    def __init__(self, env_file: str = ".env", mcp_config_file: str = ".github/copilot/mcp.json"):
        """
        Initialize the settings manager.
        
        Args:
            env_file: Path to .env file
            mcp_config_file: Path to MCP configuration JSON file
        """
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / env_file
        self.mcp_config_file = self.project_root / mcp_config_file
        self.encryption_key = self._get_or_create_encryption_key()
        
        # Load environment variables
        load_dotenv(self.env_file)
        
        logger.info(f"Settings manager initialized with env file: {self.env_file}")
    
    def _get_or_create_encryption_key(self) -> Fernet:
        """
        Get or create an encryption key for secure storage.
        
        Returns:
            Fernet encryption instance
        """
        key_file = self.project_root / ".encryption_key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            # Only create if directory is writable
            try:
                with open(key_file, 'wb') as f:
                    f.write(key)
                # Make it read-only
                os.chmod(key_file, 0o600)
                logger.info("Created new encryption key")
            except Exception as e:
                logger.warning(f"Could not save encryption key: {e}")
        
        return Fernet(key)
    
    def get_settings(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Get current application settings.
        
        Args:
            include_sensitive: If True, include redacted sensitive values
            
        Returns:
            Dictionary of current settings
        """
        settings = {
            'ai_models': self.get_available_models(),
            'active_model': os.getenv('ACTIVE_MODEL', 'gemini'),
            'server': {
                'host': os.getenv('HOST', '0.0.0.0'),
                'port': int(os.getenv('PORT', '8000')),
                'backend_port': int(os.getenv('BACKEND_PORT', '8000')),
                'frontend_port': int(os.getenv('FRONTEND_PORT', '3000'))
            },
            'cors': {
                'allowed_origins': os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8000').split(',')
            },
            'features': {
                'remote_access': os.getenv('REMOTE_ACCESS', 'false').lower() == 'true',
                'debug_mode': os.getenv('DEBUG_MODE', 'false').lower() == 'true'
            },
            'mcp_servers': self.get_mcp_servers_status()
        }
        
        if include_sensitive:
            # Add redacted sensitive values
            settings['api_keys'] = {}
            for var in self.SENSITIVE_VARS:
                value = os.getenv(var)
                if value:
                    settings['api_keys'][var] = self._redact_key(value)
                else:
                    settings['api_keys'][var] = None
        
        return settings
    
    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update application settings.
        
        Args:
            settings: Dictionary of settings to update
            
        Returns:
            Dictionary with update results
        """
        updated = []
        errors = []
        
        try:
            # Update server settings
            if 'server' in settings:
                server = settings['server']
                if 'host' in server:
                    self._update_env_var('HOST', server['host'])
                    updated.append('HOST')
                if 'port' in server:
                    self._update_env_var('PORT', str(server['port']))
                    updated.append('PORT')
                if 'backend_port' in server:
                    self._update_env_var('BACKEND_PORT', str(server['backend_port']))
                    updated.append('BACKEND_PORT')
                if 'frontend_port' in server:
                    self._update_env_var('FRONTEND_PORT', str(server['frontend_port']))
                    updated.append('FRONTEND_PORT')
            
            # Update CORS settings
            if 'cors' in settings and 'allowed_origins' in settings['cors']:
                origins = ','.join(settings['cors']['allowed_origins'])
                self._update_env_var('ALLOWED_ORIGINS', origins)
                updated.append('ALLOWED_ORIGINS')
            
            # Update feature flags
            if 'features' in settings:
                features = settings['features']
                if 'remote_access' in features:
                    self._update_env_var('REMOTE_ACCESS', str(features['remote_access']).lower())
                    updated.append('REMOTE_ACCESS')
                if 'debug_mode' in features:
                    self._update_env_var('DEBUG_MODE', str(features['debug_mode']).lower())
                    updated.append('DEBUG_MODE')
            
            # Update active model
            if 'active_model' in settings:
                self._update_env_var('ACTIVE_MODEL', settings['active_model'])
                updated.append('ACTIVE_MODEL')
            
            # Reload environment
            load_dotenv(self.env_file, override=True)
            
        except Exception as e:
            logger.error(f"Error updating settings: {e}", exc_info=True)
            errors.append(str(e))
        
        return {
            'success': len(errors) == 0,
            'updated': updated,
            'errors': errors
        }
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available AI models with their configuration status.
        
        Returns:
            List of model configurations
        """
        models = []
        for model in self.AVAILABLE_MODELS:
            model_info = model.copy()
            
            # Check if model is configured
            if model['requires_key'] and model['key_var']:
                api_key = os.getenv(model['key_var'])
                model_info['configured'] = bool(api_key)
                model_info['key_present'] = bool(api_key)
            else:
                model_info['configured'] = True
                model_info['key_present'] = True
            
            models.append(model_info)
        
        return models
    
    def set_active_model(self, model_id: str) -> Dict[str, Any]:
        """
        Set the active AI model.
        
        Args:
            model_id: Model identifier (gemini, vertex, ollama)
            
        Returns:
            Result dictionary
        """
        valid_ids = [m['id'] for m in self.AVAILABLE_MODELS]
        
        if model_id not in valid_ids:
            return {
                'success': False,
                'error': f'Invalid model ID. Must be one of: {", ".join(valid_ids)}'
            }
        
        try:
            self._update_env_var('ACTIVE_MODEL', model_id)
            load_dotenv(self.env_file, override=True)
            
            return {
                'success': True,
                'active_model': model_id
            }
        except Exception as e:
            logger.error(f"Error setting active model: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_api_key(self, service: str, api_key: str) -> Dict[str, Any]:
        """
        Validate an API key for a given service.
        
        Args:
            service: Service name (gemini, vertex, github, etc.)
            api_key: API key to validate
            
        Returns:
            Validation result dictionary
        """
        # Basic validation - check format
        if not api_key or len(api_key) < 10:
            return {
                'valid': False,
                'error': 'API key is too short or empty'
            }
        
        # Service-specific validation
        if service == 'gemini':
            # Gemini keys typically start with 'AI' and are ~40 chars
            if not api_key.startswith('AI') or len(api_key) < 30:
                return {
                    'valid': False,
                    'error': 'Invalid Gemini API key format'
                }
        elif service == 'github':
            # GitHub tokens start with 'ghp_' or 'github_pat_'
            if not (api_key.startswith('ghp_') or api_key.startswith('github_pat_')):
                return {
                    'valid': False,
                    'error': 'Invalid GitHub token format'
                }
        
        return {
            'valid': True,
            'message': f'{service} API key format is valid'
        }
    
    def update_api_key(self, key_var: str, value: str) -> Dict[str, Any]:
        """
        Update an API key securely.
        
        Args:
            key_var: Environment variable name
            value: API key value
            
        Returns:
            Update result
        """
        try:
            # Validate the key variable is known
            if key_var not in self.SENSITIVE_VARS:
                return {
                    'success': False,
                    'error': f'Unknown key variable: {key_var}'
                }
            
            # Update the environment variable
            self._update_env_var(key_var, value)
            load_dotenv(self.env_file, override=True)
            
            return {
                'success': True,
                'message': f'{key_var} updated successfully'
            }
        except Exception as e:
            logger.error(f"Error updating API key: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_mcp_servers_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all MCP servers.
        
        Returns:
            List of MCP server configurations with status
        """
        if not self.mcp_config_file.exists():
            logger.warning(f"MCP config file not found: {self.mcp_config_file}")
            return []
        
        try:
            with open(self.mcp_config_file, 'r') as f:
                mcp_config = json.load(f)
            
            servers = []
            for name, config in mcp_config.get('mcpServers', {}).items():
                server_info = {
                    'name': name,
                    'type': config.get('type', 'unknown'),
                    'command': config.get('command', ''),
                    'enabled': True,  # All servers in config are enabled by default
                    'status': 'configured',
                    'requires_env': bool(config.get('env'))
                }
                
                # Check if required environment variables are set
                if config.get('env'):
                    env_vars = config['env']
                    missing_vars = []
                    for var, value in env_vars.items():
                        # Check if it's a reference to an env var
                        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                            env_var_name = value[2:-1]
                            if not os.getenv(env_var_name):
                                missing_vars.append(env_var_name)
                    
                    if missing_vars:
                        server_info['status'] = 'missing_credentials'
                        server_info['missing_vars'] = missing_vars
                    else:
                        server_info['status'] = 'ready'
                
                servers.append(server_info)
            
            return servers
            
        except Exception as e:
            logger.error(f"Error reading MCP config: {e}")
            return []
    
    def toggle_mcp_server(self, server_name: str, enabled: bool) -> Dict[str, Any]:
        """
        Enable or disable an MCP server.
        
        Args:
            server_name: Name of the MCP server
            enabled: True to enable, False to disable
            
        Returns:
            Result dictionary
        """
        # Note: This is a placeholder. In a full implementation, you would
        # modify the MCP config file or maintain a separate enabled/disabled list
        
        try:
            servers = self.get_mcp_servers_status()
            server_exists = any(s['name'] == server_name for s in servers)
            
            if not server_exists:
                return {
                    'success': False,
                    'error': f'Server {server_name} not found'
                }
            
            # For now, just log the action
            # In production, you'd update the MCP config or a separate state file
            logger.info(f"MCP server {server_name} {'enabled' if enabled else 'disabled'}")
            
            return {
                'success': True,
                'server': server_name,
                'enabled': enabled,
                'message': f'Server {server_name} {"enabled" if enabled else "disabled"}'
            }
            
        except Exception as e:
            logger.error(f"Error toggling MCP server: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_environment_variables(self, include_sensitive: bool = False) -> Dict[str, str]:
        """
        Get environment variables.
        
        Args:
            include_sensitive: If True, include redacted sensitive values
            
        Returns:
            Dictionary of environment variables
        """
        env_vars = {}
        
        if not self.env_file.exists():
            return env_vars
        
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Skip sensitive vars unless requested
                        if key in self.SENSITIVE_VARS:
                            if include_sensitive:
                                env_vars[key] = self._redact_key(value)
                            continue
                        else:
                            env_vars[key] = value
            
            return env_vars
            
        except Exception as e:
            logger.error(f"Error reading environment variables: {e}")
            return {}
    
    def update_environment_variable(self, key: str, value: str) -> Dict[str, Any]:
        """
        Update a single environment variable.
        
        Args:
            key: Variable name
            value: Variable value
            
        Returns:
            Update result
        """
        try:
            # Don't allow updating sensitive vars through this method
            if key in self.SENSITIVE_VARS:
                return {
                    'success': False,
                    'error': 'Use update_api_key() for sensitive variables'
                }
            
            self._update_env_var(key, value)
            load_dotenv(self.env_file, override=True)
            
            return {
                'success': True,
                'key': key,
                'message': f'{key} updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating environment variable: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_env_var(self, key: str, value: str) -> None:
        """
        Update an environment variable in the .env file.
        
        Args:
            key: Variable name
            value: Variable value
        """
        if not self.env_file.exists():
            # Create the file if it doesn't exist
            self.env_file.touch()
        
        set_key(self.env_file, key, value)
        logger.info(f"Updated environment variable: {key}")
    
    def _redact_key(self, key: str) -> str:
        """
        Redact an API key for display.
        
        Args:
            key: API key to redact
            
        Returns:
            Redacted key (shows first 4 and last 4 characters)
        """
        if not key or len(key) < 8:
            return '***'
        
        return f"{key[:4]}...{key[-4:]}"
    
    def test_connection(self, service: str) -> Dict[str, Any]:
        """
        Test connection to a service.
        
        Args:
            service: Service to test (gemini, vertex, ollama)
            
        Returns:
            Test result
        """
        try:
            if service == 'gemini':
                api_key = os.getenv('GEMINI_API_KEY')
                if not api_key:
                    return {
                        'success': False,
                        'error': 'GEMINI_API_KEY not configured'
                    }
                
                # Basic validation - in production, make actual API call
                validation = self.validate_api_key('gemini', api_key)
                if validation['valid']:
                    return {
                        'success': True,
                        'message': 'Gemini API key format is valid',
                        'note': 'Full connection test requires actual API call'
                    }
                else:
                    return {
                        'success': False,
                        'error': validation['error']
                    }
            
            elif service == 'vertex':
                api_key = os.getenv('VERTEX_API_KEY')
                if not api_key:
                    return {
                        'success': False,
                        'error': 'VERTEX_API_KEY not configured'
                    }
                
                return {
                    'success': True,
                    'message': 'Vertex AI key present',
                    'note': 'Full connection test requires actual API call'
                }
            
            elif service == 'ollama':
                # Check if Ollama is accessible on localhost
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('127.0.0.1', 11434))
                sock.close()
                
                if result == 0:
                    return {
                        'success': True,
                        'message': 'Ollama server is accessible on localhost:11434'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Ollama server not accessible on localhost:11434'
                    }
            
            else:
                return {
                    'success': False,
                    'error': f'Unknown service: {service}'
                }
                
        except Exception as e:
            logger.error(f"Error testing connection to {service}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_config(self) -> Dict[str, Any]:
        """
        Export current configuration (sanitized).
        
        Returns:
            Configuration dictionary
        """
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'settings': self.get_settings(include_sensitive=False),
            'mcp_servers': self.get_mcp_servers_status(),
            'environment': self.get_environment_variables(include_sensitive=False)
        }
    
    def reload_environment(self) -> Dict[str, Any]:
        """
        Reload environment variables from .env file and return summary of changes.
        
        This is useful after modifying settings to ensure the application
        picks up the new values without requiring a restart.
        
        Returns:
            Dictionary with reload results and change summary
        """
        try:
            # Get current values before reload
            old_active_model = os.getenv('ACTIVE_MODEL', 'auto')
            old_gemini_key = os.getenv('GEMINI_API_KEY', '')
            old_vertex_key = os.getenv('VERTEX_API_KEY', '')
            
            # Reload environment variables
            load_dotenv(self.env_file, override=True)
            
            # Get new values after reload
            new_active_model = os.getenv('ACTIVE_MODEL', 'auto')
            new_gemini_key = os.getenv('GEMINI_API_KEY', '')
            new_vertex_key = os.getenv('VERTEX_API_KEY', '')
            
            # Track what changed
            changes = []
            if old_active_model != new_active_model:
                changes.append({
                    'variable': 'ACTIVE_MODEL',
                    'old_value': old_active_model,
                    'new_value': new_active_model
                })
            
            if old_gemini_key != new_gemini_key:
                changes.append({
                    'variable': 'GEMINI_API_KEY',
                    'old_value': '***REDACTED***' if old_gemini_key else 'not set',
                    'new_value': '***REDACTED***' if new_gemini_key else 'not set'
                })
            
            if old_vertex_key != new_vertex_key:
                changes.append({
                    'variable': 'VERTEX_API_KEY',
                    'old_value': '***REDACTED***' if old_vertex_key else 'not set',
                    'new_value': '***REDACTED***' if new_vertex_key else 'not set'
                })
            
            logger.info(f"Environment reloaded, {len(changes)} variables changed")
            
            return {
                'success': True,
                'changes': changes,
                'message': f'Environment reloaded successfully with {len(changes)} changes'
            }
            
        except Exception as e:
            logger.error(f"Error reloading environment: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to reload environment'
            }
