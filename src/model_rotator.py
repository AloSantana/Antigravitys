"""
AI Model Rotator - Intelligent API key rotation with rate limit management.

This module provides intelligent rotation of API keys across multiple services
(Gemini, OpenAI, Vertex, OpenRouter, etc.) with automatic rate limit detection, 
health monitoring, and load balancing for concurrent swarm operations.
"""

import os
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class KeyStatus(Enum):
    """Status of an API key."""
    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class APIKey:
    """Represents a single API key with its status and usage metrics."""
    key: str
    service: str  # gemini, openai, vertex, openrouter, etc.
    name: str  # User-friendly identifier
    model: Optional[str] = None  # Specific model to use with this key
    status: KeyStatus = KeyStatus.AVAILABLE
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limit_hits: int = 0
    last_used: Optional[float] = None
    last_rate_limit: Optional[float] = None
    backoff_until: Optional[float] = None
    error_count: int = 0
    consecutive_errors: int = 0
    tags: List[str] = field(default_factory=list)
    
    def is_available(self) -> bool:
        """Check if the key is currently available for use."""
        if self.status == KeyStatus.DISABLED:
            return False
        
        if self.backoff_until:
            if time.time() < self.backoff_until:
                return False
            else:
                # Backoff period expired, reset status
                self.backoff_until = None
                if self.status == KeyStatus.RATE_LIMITED:
                    self.status = KeyStatus.AVAILABLE
        
        return self.status == KeyStatus.AVAILABLE
    
    def get_health_score(self) -> float:
        """Calculate health score (0-100) based on success rate and errors."""
        if self.total_requests == 0:
            return 100.0
        
        success_rate = self.successful_requests / self.total_requests
        error_penalty = min(self.consecutive_errors * 10, 50)
        rate_limit_penalty = min(self.rate_limit_hits * 5, 30)
        
        score = (success_rate * 100) - error_penalty - rate_limit_penalty
        return max(0.0, min(100.0, score))


@dataclass
class ServiceConfig:
    """Configuration for a specific AI service."""
    service_name: str
    default_model: str
    available_models: List[str] = field(default_factory=list)
    rate_limit_rpm: int = 60  # Requests per minute
    rate_limit_tpd: int = 1500  # Tokens per day (in thousands)
    backoff_seconds: int = 60  # Initial backoff duration
    max_backoff_seconds: int = 3600  # Maximum backoff (1 hour)
    retry_attempts: int = 3
    supports_streaming: bool = True


class ModelRotator:
    """
    Intelligent AI model rotator with multi-key support and rate limit management.
    
    Features:
    - Multiple API keys per service
    - Automatic key rotation
    - Rate limit detection and backoff
    - Health monitoring
    - Load balancing for concurrent operations
    - Usage statistics and analytics
    """
    
    def __init__(self):
        """Initialize the model rotator."""
        self.keys: Dict[str, List[APIKey]] = defaultdict(list)
        self.service_configs: Dict[str, ServiceConfig] = {}
        self.usage_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "keys_used": set()
        })
        self.last_used_key: Dict[str, str] = {}  # service -> key_name
        self._lock = asyncio.Lock()
        
        # Initialize from environment
        self._load_from_environment()
        
        logger.info(f"ModelRotator initialized with {sum(len(keys) for keys in self.keys.values())} keys across {len(self.keys)} services")
    
    def _load_from_environment(self):
        """Load API keys from environment variables."""
        # Gemini keys
        self._load_service_keys("gemini", "GEMINI_API_KEY", "GEMINI_API_KEYS")
        
        # OpenAI keys
        self._load_service_keys("openai", "OPENAI_API_KEY", "OPENAI_API_KEYS")
        
        # Vertex keys
        self._load_service_keys("vertex", "VERTEX_API_KEY", "VERTEX_API_KEYS")
        
        # OpenRouter keys
        self._load_service_keys("openrouter", "OPENROUTER_API_KEY", "OPENROUTER_API_KEYS")
        
        # Initialize service configurations
        self.service_configs["gemini"] = ServiceConfig(
            service_name="gemini",
            default_model="gemini-2.0-flash-exp",
            available_models=[
                "gemini-2.0-flash-exp",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-pro"
            ],
            rate_limit_rpm=60,
            rate_limit_tpd=1500
        )
        
        self.service_configs["openai"] = ServiceConfig(
            service_name="openai",
            default_model="gpt-4",
            available_models=[
                "gpt-4",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "gpt-4o",
                "gpt-4o-mini"
            ],
            rate_limit_rpm=60,
            rate_limit_tpd=10000
        )
        
        self.service_configs["vertex"] = ServiceConfig(
            service_name="vertex",
            default_model="gemini-pro",
            available_models=[
                "gemini-pro",
                "gemini-1.5-pro",
                "gemini-1.5-flash"
            ],
            rate_limit_rpm=60,
            rate_limit_tpd=1500
        )
        
        self.service_configs["openrouter"] = ServiceConfig(
            service_name="openrouter",
            default_model="anthropic/claude-3.5-sonnet",
            available_models=[
                "anthropic/claude-3.5-sonnet",
                "anthropic/claude-3-opus",
                "openai/gpt-4-turbo",
                "google/gemini-pro-1.5",
                "meta-llama/llama-3.1-70b-instruct",
                "mistralai/mixtral-8x7b-instruct"
            ],
            rate_limit_rpm=200,  # OpenRouter has higher limits
            rate_limit_tpd=50000,
            supports_streaming=True
        )
    
    def _load_service_keys(self, service: str, single_key_var: str, multi_key_var: str):
        """Load API keys for a service from environment variables."""
        # Load single key
        single_key = os.getenv(single_key_var)
        if single_key:
            self.add_key(service, single_key, f"{service}_default")
        
        # Load multiple keys (comma-separated)
        multi_keys = os.getenv(multi_key_var, "")
        if multi_keys:
            for idx, key in enumerate(multi_keys.split(","), start=1):
                key = key.strip()
                if key:
                    self.add_key(service, key, f"{service}_key_{idx}")
    
    def add_key(self, service: str, key: str, name: str, model: Optional[str] = None, tags: Optional[List[str]] = None) -> bool:
        """
        Add a new API key to the rotator.
        
        Args:
            service: Service name (gemini, openai, vertex, openrouter)
            key: API key
            name: User-friendly identifier
            model: Optional specific model to use with this key
            tags: Optional tags for categorization
            
        Returns:
            True if key was added, False if it already exists
        """
        # Check if key already exists
        for existing_key in self.keys[service]:
            if existing_key.key == key:
                logger.warning(f"Key {name} for {service} already exists")
                return False
        
        # Use default model if not specified
        if not model and service in self.service_configs:
            model = self.service_configs[service].default_model
        
        api_key = APIKey(
            key=key,
            service=service,
            name=name,
            model=model,
            tags=tags or []
        )
        
        self.keys[service].append(api_key)
        logger.info(f"Added key {name} for service {service} (model: {model})")
        return True
    
    def remove_key(self, service: str, name: str) -> bool:
        """Remove a key by name."""
        for idx, key in enumerate(self.keys[service]):
            if key.name == name:
                self.keys[service].pop(idx)
                logger.info(f"Removed key {name} from service {service}")
                return True
        return False
    
    def disable_key(self, service: str, name: str) -> bool:
        """Disable a key temporarily."""
        for key in self.keys[service]:
            if key.name == name:
                key.status = KeyStatus.DISABLED
                logger.info(f"Disabled key {name} for service {service}")
                return True
        return False
    
    def enable_key(self, service: str, name: str) -> bool:
        """Enable a previously disabled key."""
        for key in self.keys[service]:
            if key.name == name:
                if key.status == KeyStatus.DISABLED:
                    key.status = KeyStatus.AVAILABLE
                    key.consecutive_errors = 0
                    logger.info(f"Enabled key {name} for service {service}")
                    return True
        return False
    
    async def get_next_key(self, service: str, preferred_model: Optional[str] = None) -> Optional[APIKey]:
        """
        Get the next available API key for a service using intelligent rotation.
        
        Strategy:
        1. Filter available keys
        2. If preferred_model specified, prioritize keys with that model
        3. Sort by health score and last used time
        4. Return best key
        
        Args:
            service: Service name
            preferred_model: Optional preferred model to use
            
        Returns:
            APIKey if available, None if all keys are unavailable
        """
        async with self._lock:
            service_keys = self.keys.get(service, [])
            
            if not service_keys:
                logger.warning(f"No keys configured for service {service}")
                return None
            
            # Filter available keys
            available_keys = [k for k in service_keys if k.is_available()]
            
            if not available_keys:
                logger.warning(f"All keys for {service} are currently unavailable")
                return None
            
            # If preferred model specified, prioritize matching keys
            if preferred_model:
                model_matched_keys = [k for k in available_keys if k.model == preferred_model]
                if model_matched_keys:
                    available_keys = model_matched_keys
            
            # Sort by health score (desc) and last used time (asc)
            available_keys.sort(
                key=lambda k: (k.get_health_score(), -(k.last_used or 0)),
                reverse=True
            )
            
            selected_key = available_keys[0]
            selected_key.last_used = time.time()
            
            self.last_used_key[service] = selected_key.name
            
            logger.debug(
                f"Selected key {selected_key.name} for {service} "
                f"(model: {selected_key.model}, health: {selected_key.get_health_score():.1f})"
            )
            
            return selected_key
    
    async def mark_success(self, service: str, key_name: str, tokens_used: int = 0):
        """Mark a successful API call."""
        async with self._lock:
            for key in self.keys.get(service, []):
                if key.name == key_name:
                    key.total_requests += 1
                    key.successful_requests += 1
                    key.consecutive_errors = 0
                    
                    # Update service stats
                    self.usage_stats[service]["total_requests"] += 1
                    self.usage_stats[service]["successful_requests"] += 1
                    self.usage_stats[service]["total_tokens"] += tokens_used
                    self.usage_stats[service]["keys_used"].add(key_name)
                    break
    
    async def mark_failure(self, service: str, key_name: str, is_rate_limit: bool = False, auto_handoff: bool = True):
        """
        Mark a failed API call and apply backoff if needed.
        Smart handoff: automatically tries to get next available key.
        
        Args:
            service: Service name
            key_name: Key identifier
            is_rate_limit: Whether failure was due to rate limiting
            auto_handoff: Whether to automatically suggest handoff to another key
        
        Returns:
            Tuple of (handoff_recommended, suggested_key_name)
        """
        async with self._lock:
            handoff_recommended = False
            suggested_key = None
            
            for key in self.keys.get(service, []):
                if key.name == key_name:
                    key.total_requests += 1
                    key.failed_requests += 1
                    key.error_count += 1
                    key.consecutive_errors += 1
                    
                    # Update service stats
                    self.usage_stats[service]["total_requests"] += 1
                    self.usage_stats[service]["failed_requests"] += 1
                    
                    if is_rate_limit:
                        key.rate_limit_hits += 1
                        key.last_rate_limit = time.time()
                        key.status = KeyStatus.RATE_LIMITED
                        
                        # Calculate exponential backoff
                        config = self.service_configs.get(service)
                        if config:
                            backoff = min(
                                config.backoff_seconds * (2 ** (key.rate_limit_hits - 1)),
                                config.max_backoff_seconds
                            )
                            key.backoff_until = time.time() + backoff
                            
                            logger.warning(
                                f"⚠️  Key {key_name} for {service} rate limited. "
                                f"Backing off for {backoff}s (attempt {key.rate_limit_hits})"
                            )
                        
                        # Smart handoff: recommend another key if available
                        if auto_handoff:
                            available_keys = [k for k in self.keys.get(service, []) 
                                            if k.name != key_name and k.is_available()]
                            if available_keys:
                                # Find healthiest available key
                                available_keys.sort(key=lambda k: k.get_health_score(), reverse=True)
                                suggested_key = available_keys[0].name
                                handoff_recommended = True
                                logger.info(
                                    f"🔄 Smart handoff: Recommending switch from {key_name} to {suggested_key} "
                                    f"(health: {available_keys[0].get_health_score():.1f})"
                                )
                    else:
                        key.status = KeyStatus.ERROR
                        
                        # Disable key after too many consecutive errors
                        if key.consecutive_errors >= 5:
                            key.status = KeyStatus.DISABLED
                            logger.error(
                                f"❌ Key {key_name} for {service} disabled after "
                                f"{key.consecutive_errors} consecutive errors"
                            )
                    
                    break
            
            return handoff_recommended, suggested_key
    
    def get_service_stats(self, service: str) -> Dict[str, Any]:
        """Get usage statistics for a service."""
        stats = self.usage_stats[service].copy()
        stats["keys_used"] = len(stats.get("keys_used", set()))
        
        # Add per-key statistics
        service_keys = self.keys.get(service, [])
        stats["keys"] = [
            {
                "name": k.name,
                "model": k.model,
                "status": k.status.value,
                "total_requests": k.total_requests,
                "success_rate": (k.successful_requests / k.total_requests * 100) if k.total_requests > 0 else 0,
                "health_score": k.get_health_score(),
                "rate_limit_hits": k.rate_limit_hits,
                "last_used": datetime.fromtimestamp(k.last_used).isoformat() if k.last_used else None,
                "is_available": k.is_available(),
                "backoff_remaining": max(0, int(k.backoff_until - time.time())) if k.backoff_until else 0
            }
            for k in service_keys
        ]
        
        # Add service configuration
        if service in self.service_configs:
            config = self.service_configs[service]
            stats["config"] = {
                "default_model": config.default_model,
                "available_models": config.available_models,
                "rate_limit_rpm": config.rate_limit_rpm,
                "supports_streaming": config.supports_streaming
            }
        
        return stats
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all services."""
        return {
            service: self.get_service_stats(service)
            for service in self.keys.keys()
        }
    
    def get_available_key_count(self, service: str) -> int:
        """Get count of currently available keys for a service."""
        return sum(1 for k in self.keys.get(service, []) if k.is_available())
    
    def reset_stats(self, service: Optional[str] = None):
        """Reset usage statistics."""
        if service:
            self.usage_stats[service] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_tokens": 0,
                "keys_used": set()
            }
        else:
            self.usage_stats.clear()
        
        logger.info(f"Reset stats for {service if service else 'all services'}")


# Global rotator instance
_rotator_instance: Optional[ModelRotator] = None


def get_rotator() -> ModelRotator:
    """Get or create the global model rotator instance."""
    global _rotator_instance
    
    if _rotator_instance is None:
        _rotator_instance = ModelRotator()
    
    return _rotator_instance


# Convenience functions
async def get_api_key(service: str) -> Optional[Tuple[str, str]]:
    """
    Get an available API key for a service.
    
    Returns:
        Tuple of (key, key_name) if available, None otherwise
    """
    rotator = get_rotator()
    api_key = await rotator.get_next_key(service)
    
    if api_key:
        return (api_key.key, api_key.name)
    return None


async def mark_api_success(service: str, key_name: str, tokens_used: int = 0):
    """Mark a successful API call."""
    rotator = get_rotator()
    await rotator.mark_success(service, key_name, tokens_used)


async def mark_api_failure(service: str, key_name: str, is_rate_limit: bool = False):
    """Mark a failed API call."""
    rotator = get_rotator()
    await rotator.mark_failure(service, key_name, is_rate_limit)
