import json
import os
from typing import List, Dict, Any, Optional, Callable
from src.config import settings


class MemoryManager:
    """Enhanced JSON-file based memory manager with summarization support."""

    def __init__(self, memory_file: Optional[str] = None):
        self.memory_file = memory_file or str(settings.memory_file_path)
        self._memory: Dict[str, Any] = {"summary": "", "history": []}
        self._load_memory()

    def _load_memory(self):
        """Loads memory from the JSON file if it exists with backward compatibility."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Handle legacy format (list of entries)
                if isinstance(data, list):
                    self._memory = {"summary": "", "history": data}
                # Handle new format (dict with summary and history)
                elif isinstance(data, dict):
                    self._memory = {
                        "summary": data.get("summary", ""),
                        "history": data.get("history", [])
                    }
                else:
                    print(f"Warning: Unknown memory format in {self.memory_file}. Starting fresh.")
                    self._memory = {"summary": "", "history": []}
                    
            except json.JSONDecodeError:
                print(f"Warning: Could not decode memory file {self.memory_file}. Starting fresh.")
                self._memory = {"summary": "", "history": []}
        else:
            self._memory = {"summary": "", "history": []}

    def save_memory(self):
        """Saves the current memory state to the JSON file."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.memory_file) or ".", exist_ok=True)
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self._memory, f, indent=2, ensure_ascii=False)

    def add_entry(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Adds a new interaction to memory."""
        entry = {
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": None  # Could add timestamp if needed
        }
        self._memory["history"].append(entry)
        self.save_memory()

    def get_history(self) -> List[Dict[str, Any]]:
        """Returns the full conversation history."""
        return self._memory["history"]
    
    def get_summary(self) -> str:
        """Returns the current memory summary."""
        return self._memory.get("summary", "")
    
    def update_summary(self, summary: str):
        """Updates the memory summary."""
        self._memory["summary"] = summary
        self.save_memory()

    def _default_summarizer(self, messages: List[Dict[str, Any]]) -> str:
        """Default fallback summarizer that concatenates messages."""
        summary_parts = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            summary_parts.append(f"{role}: {content[:100]}")
        return " | ".join(summary_parts[:5])  # First 5 messages
    
    def get_context_window(
        self,
        system_prompt: str = "",
        max_messages: int = 20,
        summarizer: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Returns a bounded context window with optional summarization.
        
        Args:
            system_prompt: System prompt to include
            max_messages: Maximum number of recent messages to include
            summarizer: Optional function to summarize older messages
            
        Returns:
            List of messages with system prompt and bounded history
        """
        history = self.get_history()
        context = []
        
        # Add system prompt if provided
        if system_prompt:
            context.append({"role": "system", "content": system_prompt})
        
        # If history is within limit, return all
        if len(history) <= max_messages:
            return context + history
        
        # Split history into old and recent
        old_messages = history[:-max_messages]
        recent_messages = history[-max_messages:]
        
        # Create summary of old messages
        if old_messages:
            current_summary = self.get_summary()
            if summarizer:
                # Use provided summarizer
                new_summary = summarizer(old_messages)
            else:
                # Use default summarizer
                new_summary = self._default_summarizer(old_messages)
            
            # Combine with existing summary if present
            if current_summary:
                combined_summary = f"{current_summary}\n\n[Recent interactions]: {new_summary}"
            else:
                combined_summary = new_summary
            
            # Update stored summary
            self.update_summary(combined_summary)
            
            # Add summary as system message
            context.append({
                "role": "system",
                "content": f"[Previous conversation summary]: {combined_summary}"
            })
        
        # Add recent messages
        context.extend(recent_messages)
        
        return context

    def clear_memory(self):
        """Clears the agent's memory."""
        self._memory = {"summary": "", "history": []}
        self.save_memory()
