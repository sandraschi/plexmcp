"""
Basic monitoring and metrics for PlexMCP.
"""

import json
import logging
import time
import uuid
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """A single metric data point."""
    timestamp: float
    value: float
    tags: Dict[str, str]


@dataclass
class OperationMetrics:
    """Metrics for a specific operation."""
    operation: str
    total_calls: int
    successful_calls: int
    failed_calls: int
    avg_duration: float
    last_called: float
    errors: List[str]


class PlexMonitor:
    """Simple monitoring system for PlexMCP operations."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.operation_metrics: Dict[str, OperationMetrics] = {}
        self.recent_operations: deque = deque(maxlen=max_history)
        self.start_time = time.time()
        self._lock = None  # Simple implementation without threading locks
        
    def record_operation(
        self,
        operation: str,
        success: bool,
        duration: float,
        error: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Record an operation metric."""
        timestamp = time.time()
        
        # Update operation metrics
        if operation not in self.operation_metrics:
            self.operation_metrics[operation] = OperationMetrics(
                operation=operation,
                total_calls=0,
                successful_calls=0,
                failed_calls=0,
                avg_duration=0.0,
                last_called=0.0,
                errors=[]
            )
        
        metrics = self.operation_metrics[operation]
        metrics.total_calls += 1
        metrics.last_called = timestamp
        
        if success:
            metrics.successful_calls += 1
        else:
            metrics.failed_calls += 1
            if error and len(metrics.errors) < 10:
                metrics.errors.append(error)
        
        # Update average duration
        total_duration = metrics.avg_duration * (metrics.total_calls - 1) + duration
        metrics.avg_duration = total_duration / metrics.total_calls
        
        # Add to recent operations
        self.recent_operations.append({
            'timestamp': timestamp,
            'operation': operation,
            'success': success,
            'duration': duration,
            'error': error,
            'context': context
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get monitoring summary."""
        uptime = time.time() - self.start_time
        
        # Calculate overall stats
        total_operations = sum(m.total_calls for m in self.operation_metrics.values())
        total_successful = sum(m.successful_calls for m in self.operation_metrics.values())
        total_failed = sum(m.failed_calls for m in self.operation_metrics.values())
        
        # Get most recent operations
        recent_ops = list(self.recent_operations)[-10:]
        
        return {
            'uptime_seconds': uptime,
            'total_operations': total_operations,
            'successful_operations': total_successful,
            'failed_operations': total_failed,
            'success_rate': total_successful / max(total_operations, 1),
            'operations_by_type': {
                op: asdict(metrics) for op, metrics in self.operation_metrics.items()
            },
            'recent_operations': recent_ops,
            'timestamp': time.time()
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for monitoring systems."""
        summary = self.get_summary()
        
        # Determine health status
        health_status = "healthy"
        issues = []
        
        # Check success rate
        if summary['success_rate'] < 0.9 and summary['total_operations'] > 10:
            health_status = "degraded"
            issues.append(f"Low success rate: {summary['success_rate']:.1%}")
        
        # Check for recent errors
        recent_errors = [op for op in summary['recent_operations'][-20:] if not op['success']]
        if len(recent_errors) > 5:
            health_status = "unhealthy"
            issues.append(f"High error rate: {len(recent_errors)} errors in last 20 operations")
        
        return {
            'status': health_status,
            'uptime': summary['uptime_seconds'],
            'total_operations': summary['total_operations'],
            'success_rate': summary['success_rate'],
            'issues': issues,
            'timestamp': time.time()
        }


# Global monitor instance
_monitor = PlexMonitor()


def get_monitor() -> PlexMonitor:
    """Get the global monitor instance."""
    return _monitor


def record_operation(operation: str, success: bool, duration: float, error: Optional[str] = None):
    """Record an operation in the global monitor."""
    _monitor.record_operation(operation, success, duration, error)


def operation_monitor(operation_name: str):
    """Decorator to monitor operations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            error = None
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                duration = time.time() - start_time
                record_operation(operation_name, success, duration, error)
        
        return wrapper
    return decorator


async def get_monitoring_metrics() -> Dict[str, Any]:
    """Get monitoring metrics for the health endpoint."""
    return get_monitor().get_summary()


async def get_health_metrics() -> Dict[str, Any]:
    """Get health metrics for monitoring systems."""
    return get_monitor().get_health_status()
