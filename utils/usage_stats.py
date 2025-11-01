from typing import Dict, Any
import json
from pathlib import Path
from datetime import datetime, timedelta
import threading
import logging

logger = logging.getLogger(__name__)

class UsageStats:
    def __init__(self):
        """Initialize usage statistics tracker."""
        self.data_file = Path("data/reports/usage_stats.json")
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.stats = self._load_stats()

    def _load_stats(self) -> Dict[str, Any]:
        """Load statistics from file."""
        if not self.data_file.exists():
            return {
                "total_messages": 0,
                "web_messages": 0,
                "widget_messages": 0,
                "daily_counts": {},
                "common_queries": {}
            }
            
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading usage stats: {e}")
            return {
                "total_messages": 0,
                "web_messages": 0,
                "widget_messages": 0,
                "daily_counts": {},
                "common_queries": {}
            }

    def _save_stats(self):
        """Save statistics to file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving usage stats: {e}")

    def record_message(self, message: str, source: str = "web"):
        """Record a new message."""
        with self.lock:
            # Update total counts
            self.stats["total_messages"] += 1
            if source == "web":
                self.stats["web_messages"] += 1
            else:
                self.stats["widget_messages"] += 1

            # Update daily counts
            today = datetime.now().strftime("%Y-%m-%d")
            daily = self.stats.setdefault("daily_counts", {})
            daily_entry = daily.setdefault(today, {"total": 0, "web": 0, "widget": 0})
            daily_entry["total"] += 1
            daily_entry[source] += 1

            # Update common queries (keep simple versions of queries)
            query = message.lower().strip()
            queries = self.stats.setdefault("common_queries", {})
            queries[query] = queries.get(query, 0) + 1

            # Keep only last 30 days of daily stats
            cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            self.stats["daily_counts"] = {
                k: v for k, v in daily.items() 
                if k >= cutoff_date
            }

            # Keep only top 100 common queries
            if len(queries) > 100:
                sorted_queries = sorted(queries.items(), key=lambda x: x[1], reverse=True)
                self.stats["common_queries"] = dict(sorted_queries[:100])

            self._save_stats()

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of usage statistics."""
        with self.lock:
            daily = self.stats.get("daily_counts", {})
            today = datetime.now().strftime("%Y-%m-%d")
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            return {
                "total_messages": self.stats["total_messages"],
                "web_messages": self.stats["web_messages"],
                "widget_messages": self.stats["widget_messages"],
                "today": daily.get(today, {"total": 0, "web": 0, "widget": 0}),
                "yesterday": daily.get(yesterday, {"total": 0, "web": 0, "widget": 0}),
                "top_queries": dict(
                    sorted(
                        self.stats.get("common_queries", {}).items(), 
                        key=lambda x: x[1], 
                        reverse=True
                    )[:10]
                )
            }

# Global instance for usage tracking
usage_tracker = UsageStats()