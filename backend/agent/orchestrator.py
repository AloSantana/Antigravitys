import os
import hashlib
import time
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from collections import OrderedDict
from functools import lru_cache
from dataclasses import dataclass, asdict
from .gemini_client import GeminiClient
from .local_client import LocalClient
from .vertex_client import VertexClient
from rag.store import VectorStore
from utils.debug_logger import get_debug_logger


@dataclass
class AgentSession:
    """Represents an active agent session in dual-mode"""
    agent_name: str
    session_id: str
    created_at: float
    context: Dict[str, Any]
    is_primary: bool = True


@dataclass
class AgentHandoff:
    """Represents a handoff between agents"""
    from_agent: str
    to_agent: str
    context: Dict[str, Any]
    timestamp: float
    handoff_reason: str


class Orchestrator:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.vertex_api_key = os.getenv("VERTEX_API_KEY")
        self.gemini = GeminiClient(self.gemini_api_key)
        self.vertex = VertexClient(self.vertex_api_key)
        self.local = LocalClient()
        self.store = VectorStore()
        self.debug_logger = get_debug_logger()
        
        # Active model selection from environment
        self.active_model = os.getenv("ACTIVE_MODEL", "auto").lower()
        
        # Enhanced cache configuration from environment
        self._cache_ttl = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5 minutes default
        self._max_cache_size = int(os.getenv("CACHE_MAX_SIZE", "100"))  # 100 entries default
        # Use OrderedDict for efficient LRU cache implementation
        self._response_cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        # Cache statistics
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_evictions = 0
        self._total_requests = 0
        # Cache warming - common queries
        self._common_queries = [
            "hello", "help", "what can you do", "status"
        ]
        self._last_cleanup = time.time()
        self._cleanup_interval = 60  # Clean up expired entries every minute

        # Dual-agent coordination features
        self._active_sessions: Dict[str, AgentSession] = {}
        self._handoff_history: List[AgentHandoff] = []
        self._shared_context: Dict[str, Any] = {}
        self._agent_priorities: Dict[str, int] = {
            "jules": 10,  # Highest priority for code quality
            "rapid-implementer": 9,
            "architect": 8,
            "debug-detective": 7,
            "testing-stability-expert": 6,
            "code-reviewer": 5,
            "performance-optimizer": 4,
            "full-stack-developer": 3,
            "devops-infrastructure": 2,
            "docs-master": 1,
        }

        self.debug_logger.log_info(
            "orchestrator_init", 
            f"Orchestrator initialized with Hybrid Intelligence, RAG & Dual-Agent Mode (cache: {self._max_cache_size} entries, TTL: {self._cache_ttl}s, active_model: {self.active_model})"
        )
    
    def reinitialize(self):
        """
        Reinitialize the orchestrator by reloading environment variables and recreating clients.
        Used when settings change (e.g., model selection, API keys).
        """
        # Reload environment variables
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        # Update active model
        old_model = self.active_model
        self.active_model = os.getenv("ACTIVE_MODEL", "auto").lower()
        
        # Recreate clients with new API keys
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.vertex_api_key = os.getenv("VERTEX_API_KEY")
        self.gemini = GeminiClient(self.gemini_api_key)
        self.vertex = VertexClient(self.vertex_api_key)
        self.local = LocalClient()
        
        # Clear cache to ensure fresh responses with new configuration
        self._response_cache.clear()
        
        self.debug_logger.log_info(
            "orchestrator_reinit",
            f"Orchestrator reinitialized: model changed from '{old_model}' to '{self.active_model}'",
            {"old_model": old_model, "new_model": self.active_model}
        )
    
    def _get_cache_key(self, request: str) -> str:
        """Generate cache key from request using SHA256 for better distribution."""
        return hashlib.sha256(request.encode()).hexdigest()
    
    def _get_cached_response(self, request: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired."""
        # Periodic cleanup of expired entries
        self._cleanup_expired_cache()
        
        cache_key = self._get_cache_key(request)
        if cache_key in self._response_cache:
            response, timestamp = self._response_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                self._cache_hits += 1
                # Move to end (most recently used)
                self._response_cache.move_to_end(cache_key)
                print(f"Cache hit for request (age: {int(time.time() - timestamp)}s, hit rate: {self.get_cache_hit_rate():.1%})")
                return response
            else:
                # Expired, remove from cache
                del self._response_cache[cache_key]
        self._cache_misses += 1
        return None
    
    def _cache_response(self, request: str, response: Dict[str, Any]) -> None:
        """Cache a response with LRU eviction."""
        cache_key = self._get_cache_key(request)
        
        # Add to cache (or update if exists)
        self._response_cache[cache_key] = (response, time.time())
        self._response_cache.move_to_end(cache_key)
        
        # Evict oldest entries if cache is full
        while len(self._response_cache) > self._max_cache_size:
            # Remove oldest (first) item
            self._response_cache.popitem(last=False)
            self._cache_evictions += 1
    
    def _cleanup_expired_cache(self) -> None:
        """Periodically clean up expired cache entries to free memory."""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        self._last_cleanup = current_time
        expired_keys = []
        
        for key, (_, timestamp) in self._response_cache.items():
            if current_time - timestamp >= self._cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._response_cache[key]
        
        if expired_keys:
            print(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    async def warm_cache(self, queries: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Warm cache with common queries for faster initial responses.
        
        Args:
            queries: List of queries to cache. Uses defaults if None.
            
        Returns:
            Dictionary with warming statistics
        """
        queries_to_warm = queries or self._common_queries
        warmed = 0
        failed = 0
        
        print(f"Warming cache with {len(queries_to_warm)} common queries...")
        
        for query in queries_to_warm:
            try:
                # Check if already cached
                if self._get_cached_response(query):
                    continue
                
                # Process and cache
                await self.process_request(query)
                warmed += 1
            except Exception as e:
                print(f"Failed to warm cache for '{query}': {e}")
                failed += 1
        
        print(f"Cache warming complete: {warmed} warmed, {failed} failed")
        return {
            "warmed": warmed,
            "failed": failed,
            "cache_size": len(self._response_cache)
        }
    
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self._cache_hits + self._cache_misses
        return self._cache_hits / total if total > 0 else 0.0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary with cache metrics
        """
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = self.get_cache_hit_rate()
        
        # Calculate average cache entry age
        current_time = time.time()
        ages = [current_time - timestamp for _, timestamp in self._response_cache.values()]
        avg_age = sum(ages) / len(ages) if ages else 0
        
        return {
            "cache_size": len(self._response_cache),
            "max_cache_size": self._max_cache_size,
            "cache_ttl_seconds": self._cache_ttl,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_evictions": self._cache_evictions,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "hit_rate_percentage": f"{hit_rate * 100:.2f}%",
            "miss_rate": 1 - hit_rate,
            "avg_entry_age_seconds": avg_age,
            "memory_efficiency": f"{(hit_rate * 100):.1f}% of requests served from cache"
        }
    
    def clear_cache(self) -> Dict[str, int]:
        """
        Clear the response cache and return statistics.
        
        Returns:
            Dictionary with cleared cache stats
        """
        cleared_entries = len(self._response_cache)
        stats_before = {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "evictions": self._cache_evictions
        }
        
        self._response_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_evictions = 0
        self._total_requests = 0
        
        return {
            "cleared_entries": cleared_entries,
            "stats_before": stats_before
        }

    async def process_request(self, request: str) -> Dict[str, Any]:
        """
        Decides which model to use based on ACTIVE_MODEL setting or complexity heuristics.
        Includes response caching and optimized context retrieval.
        """
        start_time = time.time()
        self._total_requests += 1
        request_id = f"req_{self._total_requests}_{int(time.time() * 1000)}"
        
        self.debug_logger.log_request_start(
            request, 
            request_id,
            {"request_number": self._total_requests, "active_model": self.active_model}
        )
        
        # Check cache first - fastest path
        cached = self._get_cached_response(request)
        if cached:
            cached_copy = cached.copy()  # Don't modify cached version
            cached_copy['processing_time_ms'] = (time.time() - start_time) * 1000
            cached_copy['from_cache'] = True
            # Ensure model field is present for logging/UI consistency
            if not cached_copy.get("model"):
                cached_copy["model"] = cached_copy.get("source") or self.active_model or "unknown"
            self.debug_logger.log_request_complete(request_id, cached_copy, {"cache_hit": True})
            return cached_copy
        
        # 1. Retrieve Context with optimized embedding
        context = ""
        embedding_start = time.time()
        try:
            # Assess complexity early to decide embedding strategy
            complexity = self._assess_complexity(request)
            
            # For simple requests, skip RAG to save time
            if complexity == "low" and len(request) < 100:
                self.debug_logger.log_info("rag_skip", "Skipping RAG for simple request", {"complexity": complexity})
                query_embedding = None
            elif self.active_model == "ollama":
                # Only try local embeddings when explicitly using Ollama
                query_embedding = await self.local.embed(request)
                if not query_embedding:
                    self.debug_logger.log_warning("embedding_fallback", "Local embedding failed, trying Gemini...")
                    query_embedding = await self.gemini.embed(request)
            else:
                # Use Gemini embeddings directly (Ollama disabled or not selected)
                query_embedding = await self.gemini.embed(request)
            
            if query_embedding:
                # Increase results for better context
                results = self.store.query(query_embeddings=[query_embedding], n_results=5)
                if results and results['documents']:
                    # Use only most relevant chunks (top 3)
                    context = "\n".join(results['documents'][0][:3])
                    embedding_time = (time.time() - embedding_start) * 1000
                    self.debug_logger.log_info(
                        "rag_retrieval", 
                        f"Retrieved {len(results['documents'][0][:3])} context chunks in {embedding_time:.0f}ms",
                        {"chunks": len(results['documents'][0][:3]), "time_ms": embedding_time}
                    )
                else:
                    self.debug_logger.log_warning("rag_no_results", "No context chunks retrieved from RAG")
        except Exception as e:
            self.debug_logger.log_error("rag_error", f"RAG Retrieval Error: {str(e)}", {"error": str(e)})

        # 2. Augment Prompt efficiently
        if context:
            augmented_request = f"Context:\n{context}\n\nUser Request: {request}"
        else:
            augmented_request = request

        # 3. Delegate based on ACTIVE_MODEL setting or complexity
        gen_start = time.time()
        
        # Honor ACTIVE_MODEL setting if explicitly set
        if self.active_model == "gemini":
            self.debug_logger.log_info("model_selection", "Using Gemini (explicit setting)", {"active_model": self.active_model})
            response = await self._delegate_to_gemini(augmented_request)
        elif self.active_model == "vertex":
            self.debug_logger.log_info("model_selection", "Using Vertex AI (explicit setting)", {"active_model": self.active_model})
            response = await self._delegate_to_vertex(augmented_request)
        elif self.active_model == "ollama":
            self.debug_logger.log_info("model_selection", "Using Ollama with cloud fallback (explicit setting)", {"active_model": self.active_model})
            response = await self._delegate_to_local(augmented_request)
            # Fallback to cloud if local fails
            if "Error" in response["response"] or "Could not connect" in response["response"]:
                self.debug_logger.log_warning("llm_fallback", "Local LLM failed, falling back to cloud...")
                if self.vertex.is_available():
                    response = await self._delegate_to_vertex(augmented_request)
                else:
                    response = await self._delegate_to_gemini(augmented_request)
        else:
            # Auto mode: delegate based on complexity heuristics
            self.debug_logger.log_info("model_selection", f"Using auto mode (complexity: {complexity})", {"active_model": "auto", "complexity": complexity})
            complexity = self._assess_complexity(request)
            if complexity == "high":
                # Prefer Vertex AI if available, fallback to Gemini
                if self.vertex.is_available():
                    response = await self._delegate_to_vertex(augmented_request)
                else:
                    response = await self._delegate_to_gemini(augmented_request)
            else:
                # Use Gemini for low-complexity requests (Ollama disabled)
                response = await self._delegate_to_gemini(augmented_request)
        
        # Add performance metrics
        total_time = (time.time() - start_time) * 1000
        response['processing_time_ms'] = total_time
        response['generation_time_ms'] = (time.time() - gen_start) * 1000
        response['from_cache'] = False
        response['model'] = response.get('source', 'Unknown')
        
        self.debug_logger.log_request_complete(
            request_id, 
            response,
            {"total_time_ms": total_time, "generation_time_ms": response['generation_time_ms']}
        )
        
        # Cache the response
        self._cache_response(request, response)
        return response

    @lru_cache(maxsize=256)
    def _assess_complexity(self, request: str) -> str:
        """
        Assess request complexity using enhanced heuristics.
        Cached for performance on repeated similar requests.
        """
        request_lower = request.lower()
        
        # High complexity keywords (requires advanced reasoning)
        high_complexity_keywords = [
            "plan", "design", "architecture", "complex", "strategy", 
            "implement", "refactor", "optimize", "debug", "analyze",
            "deployment", "infrastructure", "scale", "performance",
            "security", "integration", "migration"
        ]
        
        # Additional factors for complexity
        # 1. Keyword matching
        high_keyword_count = sum(1 for k in high_complexity_keywords if k in request_lower)
        
        # 2. Request length (longer requests often more complex)
        is_long = len(request) > 200
        
        # 3. Code patterns (suggests implementation work)
        has_code_patterns = any(pattern in request for pattern in 
            ["```", "function", "class", "def ", "async ", "import "])
        
        # 4. Question complexity
        has_multiple_questions = request.count("?") > 1
        
        # Decision logic
        if high_keyword_count >= 2 or (high_keyword_count >= 1 and (is_long or has_code_patterns)):
            return "high"
        elif has_multiple_questions and is_long:
            return "high"
        
        return "low"

    async def _delegate_to_gemini(self, request: str):
        self.debug_logger.log_info("delegate_gemini", "Delegating to Gemini...")
        response = await self.gemini.generate(request)
        return {"source": "Gemini", "response": response}
    
    async def _delegate_to_vertex(self, request: str):
        """Delegate request to Vertex AI."""
        self.debug_logger.log_info("delegate_vertex", "Delegating to Vertex AI...")
        response = await self.vertex.generate(request)
        return {"source": "Vertex AI", "response": response}

    async def _delegate_to_local(self, request: str):
        self.debug_logger.log_info("delegate_local", "Delegating to Local LLM...")
        response = await self.local.generate(request)
        return {"source": "Local", "response": response}

    # Dual-Agent Coordination Methods

    def create_agent_session(
        self,
        agent_name: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None,
        is_primary: bool = True
    ) -> AgentSession:
        """
        Create a new agent session for dual-agent mode.

        Args:
            agent_name: Name of the agent
            session_id: Unique session identifier
            context: Initial context for the session
            is_primary: Whether this is the primary agent

        Returns:
            AgentSession object
        """
        session = AgentSession(
            agent_name=agent_name,
            session_id=session_id,
            created_at=time.time(),
            context=context or {},
            is_primary=is_primary
        )
        self._active_sessions[session_id] = session
        print(f"Created {'primary' if is_primary else 'secondary'} agent session: {agent_name} ({session_id})")
        return session

    def get_agent_session(self, session_id: str) -> Optional[AgentSession]:
        """Get an active agent session by ID."""
        return self._active_sessions.get(session_id)

    def list_active_sessions(self) -> List[AgentSession]:
        """List all active agent sessions."""
        return list(self._active_sessions.values())

    def end_agent_session(self, session_id: str) -> bool:
        """
        End an agent session.

        Args:
            session_id: Session ID to end

        Returns:
            True if session was ended, False if not found
        """
        if session_id in self._active_sessions:
            session = self._active_sessions.pop(session_id)
            print(f"Ended agent session: {session.agent_name} ({session_id})")
            return True
        return False

    def handoff_agent(
        self,
        from_agent: str,
        to_agent: str,
        context: Dict[str, Any],
        reason: str
    ) -> AgentHandoff:
        """
        Execute a handoff from one agent to another.

        Args:
            from_agent: Source agent name
            to_agent: Target agent name
            context: Context to transfer
            reason: Reason for the handoff

        Returns:
            AgentHandoff object
        """
        handoff = AgentHandoff(
            from_agent=from_agent,
            to_agent=to_agent,
            context=context,
            timestamp=time.time(),
            handoff_reason=reason
        )

        self._handoff_history.append(handoff)

        # Update shared context
        handoff_key = f"handoff_{from_agent}_to_{to_agent}"
        self._shared_context[handoff_key] = {
            "context": context,
            "timestamp": handoff.timestamp,
            "reason": reason
        }

        print(f"Agent handoff: {from_agent} → {to_agent} (reason: {reason})")
        return handoff

    def get_handoff_history(
        self,
        agent_name: Optional[str] = None,
        limit: int = 10
    ) -> List[AgentHandoff]:
        """
        Get handoff history, optionally filtered by agent.

        Args:
            agent_name: Optional agent name to filter by
            limit: Maximum number of results

        Returns:
            List of AgentHandoff objects
        """
        history = self._handoff_history

        if agent_name:
            history = [
                h for h in history
                if h.from_agent == agent_name or h.to_agent == agent_name
            ]

        return history[-limit:]

    def update_shared_context(self, key: str, value: Any) -> None:
        """
        Update the shared context accessible by all agents.

        Args:
            key: Context key
            value: Context value
        """
        self._shared_context[key] = {
            "value": value,
            "updated_at": time.time()
        }
        print(f"Updated shared context: {key}")

    def get_shared_context(self, key: Optional[str] = None) -> Any:
        """
        Get shared context value(s).

        Args:
            key: Optional specific key to retrieve

        Returns:
            Context value or entire context dict
        """
        if key:
            item = self._shared_context.get(key)
            return item["value"] if item else None
        return self._shared_context

    def route_to_best_agent(
        self,
        request: str,
        exclude_agents: Optional[List[str]] = None
    ) -> str:
        """
        Route a request to the best available agent based on capabilities.

        Args:
            request: The request to route
            exclude_agents: Optional list of agents to exclude

        Returns:
            Name of the best agent for the request
        """
        request_lower = request.lower()
        exclude = exclude_agents or []

        # Agent capability patterns
        agent_patterns = {
            "jules": ["review", "refactor", "quality", "analyze", "improve", "collaborate"],
            "rapid-implementer": ["implement", "build", "create", "develop", "code"],
            "architect": ["design", "architecture", "structure", "plan", "system"],
            "debug-detective": ["bug", "debug", "error", "issue", "fix", "investigate"],
            "testing-stability-expert": ["test", "validate", "verify", "coverage"],
            "code-reviewer": ["review", "security", "audit", "check"],
            "performance-optimizer": ["optimize", "performance", "speed", "efficiency"],
            "full-stack-developer": ["frontend", "backend", "full-stack", "web"],
            "devops-infrastructure": ["deploy", "docker", "kubernetes", "ci/cd"],
            "docs-master": ["document", "docs", "readme", "guide"],
        }

        # Score each agent
        scores = {}
        for agent, patterns in agent_patterns.items():
            if agent in exclude:
                continue

            # Count pattern matches
            score = sum(1 for pattern in patterns if pattern in request_lower)

            # Add priority bonus
            priority_bonus = self._agent_priorities.get(agent, 0) * 0.1
            scores[agent] = score + priority_bonus

        # Return agent with highest score, or jules as default
        if scores:
            best_agent = max(scores.items(), key=lambda x: x[1])[0]
            print(f"Routed request to {best_agent} (score: {scores[best_agent]:.1f})")
            return best_agent

        return "jules"  # Default to jules

    async def collaborative_process(
        self,
        request: str,
        agents: List[str],
        mode: str = "sequential"
    ) -> Dict[str, Any]:
        """
        Process a request collaboratively with multiple agents.

        Args:
            request: The request to process
            agents: List of agent names to collaborate
            mode: Collaboration mode ('sequential' or 'parallel')

        Returns:
            Combined response from all agents
        """
        results = {}

        if mode == "sequential":
            # Sequential processing with context passing
            context = {"original_request": request}

            for i, agent in enumerate(agents):
                # Create augmented request with context
                if i == 0:
                    augmented_request = request
                else:
                    prev_agent = agents[i - 1]
                    augmented_request = f"""
Previous agent ({prev_agent}) completed their part.
Context: {results.get(prev_agent, {}).get('response', '')}

Your task as {agent}: {request}
"""

                # Process request
                response = await self.process_request(augmented_request)
                results[agent] = response

                # Update context for next agent
                context[agent] = response

                print(f"Completed {agent} ({i+1}/{len(agents)})")

        elif mode == "parallel":
            # Parallel processing for independent tasks
            tasks = []
            for agent in agents:
                agent_request = f"As {agent}: {request}"
                tasks.append(self.process_request(agent_request))

            responses = await asyncio.gather(*tasks)
            results = dict(zip(agents, responses))

        # Combine results
        combined = {
            "mode": mode,
            "agents": agents,
            "results": results,
            "timestamp": time.time()
        }

        return combined

    def get_agent_stats(self) -> Dict[str, Any]:
        """
        Get statistics about agent usage and coordination.

        Returns:
            Dictionary with agent statistics
        """
        total_handoffs = len(self._handoff_history)
        active_sessions_count = len(self._active_sessions)

        # Agent handoff frequency
        handoff_by_agent = {}
        for handoff in self._handoff_history:
            handoff_by_agent[handoff.from_agent] = handoff_by_agent.get(handoff.from_agent, 0) + 1
            handoff_by_agent[handoff.to_agent] = handoff_by_agent.get(handoff.to_agent, 0) + 1

        return {
            "active_sessions": active_sessions_count,
            "total_handoffs": total_handoffs,
            "handoff_by_agent": handoff_by_agent,
            "shared_context_size": len(self._shared_context),
            "agent_priorities": self._agent_priorities
        }
