"""
AI Observability and Monitoring System
Implements comprehensive monitoring for AI workflows, model performance, and business metrics
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import statistics

logger = logging.getLogger(__name__)

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Metric:
    name: str
    value: Union[int, float]
    metric_type: MetricType
    labels: Dict[str, str]
    timestamp: datetime
    description: Optional[str] = None

@dataclass
class AITrace:
    trace_id: str
    span_id: str
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: str = "pending"
    tags: Dict[str, str] = None
    logs: List[Dict[str, Any]] = None
    parent_span_id: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
        if self.logs is None:
            self.logs = []
        if self.end_time and self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()

@dataclass
class ModelPerformanceMetrics:
    model_name: str
    timestamp: datetime
    response_time: float
    token_count: int
    cost: float
    accuracy_score: Optional[float] = None
    hallucination_score: Optional[float] = None
    relevance_score: Optional[float] = None
    error_rate: float = 0.0
    throughput: float = 0.0

@dataclass
class BusinessMetric:
    metric_name: str
    value: float
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

class AIObservabilityManager:
    """
    Comprehensive AI Observability Manager
    Tracks AI workflows, model performance, and business metrics
    """
    
    def __init__(self):
        self.metrics_store = []
        self.traces_store = []
        self.model_performance = []
        self.business_metrics = []
        self.alerts = []
        
        # Performance tracking
        self.response_times = {}
        self.error_rates = {}
        self.throughput_stats = {}
        
        # Configuration
        self.alert_thresholds = {
            'response_time': 5.0,  # seconds
            'error_rate': 0.05,    # 5%
            'hallucination_rate': 0.1,  # 10%
            'cost_threshold': 100.0  # dollars per hour
        }
    
    async def start_trace(self, operation_name: str, parent_span_id: Optional[str] = None,
                         tags: Dict[str, str] = None) -> AITrace:
        """Start a new AI operation trace"""
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        
        trace = AITrace(
            trace_id=trace_id,
            span_id=span_id,
            operation_name=operation_name,
            start_time=datetime.now(),
            parent_span_id=parent_span_id,
            tags=tags or {}
        )
        
        self.traces_store.append(trace)
        
        logger.info(f"Started trace {trace_id} for operation {operation_name}")
        return trace
    
    async def end_trace(self, trace: AITrace, status: str = "success", 
                       error_message: Optional[str] = None):
        """End an AI operation trace"""
        trace.end_time = datetime.now()
        trace.status = status
        
        if error_message:
            trace.logs.append({
                "timestamp": datetime.now().isoformat(),
                "level": "error",
                "message": error_message
            })
        
        # Calculate duration
        if trace.end_time and trace.start_time:
            trace.duration = (trace.end_time - trace.start_time).total_seconds()
        
        # Update performance metrics
        await self._update_performance_metrics(trace)
        
        # Check for alerts
        await self._check_alerts(trace)
        
        logger.info(f"Ended trace {trace.trace_id} with status {status}")
    
    async def log_metric(self, name: str, value: Union[int, float], 
                        metric_type: MetricType, labels: Dict[str, str] = None,
                        description: str = None):
        """Log a metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            labels=labels or {},
            timestamp=datetime.now(),
            description=description
        )
        
        self.metrics_store.append(metric)
        
        # Update real-time statistics
        await self._update_real_time_stats(metric)
    
    async def log_model_performance(self, model_name: str, response_time: float,
                                  token_count: int, cost: float,
                                  accuracy_score: Optional[float] = None,
                                  hallucination_score: Optional[float] = None,
                                  relevance_score: Optional[float] = None):
        """Log model performance metrics"""
        performance = ModelPerformanceMetrics(
            model_name=model_name,
            timestamp=datetime.now(),
            response_time=response_time,
            token_count=token_count,
            cost=cost,
            accuracy_score=accuracy_score,
            hallucination_score=hallucination_score,
            relevance_score=relevance_score
        )
        
        self.model_performance.append(performance)
        
        # Calculate error rate and throughput
        await self._calculate_model_stats(model_name)
        
        # Check for model performance alerts
        await self._check_model_alerts(performance)
    
    async def log_business_metric(self, metric_name: str, value: float,
                                user_id: Optional[str] = None,
                                session_id: Optional[str] = None,
                                context: Dict[str, Any] = None):
        """Log business metric"""
        business_metric = BusinessMetric(
            metric_name=metric_name,
            value=value,
            timestamp=datetime.now(),
            user_id=user_id,
            session_id=session_id,
            context=context or {}
        )
        
        self.business_metrics.append(business_metric)
        
        # Check for business metric alerts
        await self._check_business_alerts(business_metric)
    
    async def _update_performance_metrics(self, trace: AITrace):
        """Update performance metrics based on trace"""
        if trace.duration is not None:
            await self.log_metric(
                name=f"ai_operation_duration",
                value=trace.duration,
                metric_type=MetricType.HISTOGRAM,
                labels={
                    "operation": trace.operation_name,
                    "status": trace.status
                }
            )
    
    async def _update_real_time_stats(self, metric: Metric):
        """Update real-time statistics"""
        if metric.name not in self.response_times:
            self.response_times[metric.name] = []
        
        if metric.metric_type == MetricType.HISTOGRAM:
            self.response_times[metric.name].append(metric.value)
            
            # Keep only last 1000 measurements
            if len(self.response_times[metric.name]) > 1000:
                self.response_times[metric.name] = self.response_times[metric.name][-1000:]
    
    async def _calculate_model_stats(self, model_name: str):
        """Calculate error rate and throughput for model"""
        recent_performance = [
            p for p in self.model_performance 
            if p.model_name == model_name and 
            p.timestamp > datetime.now() - timedelta(hours=1)
        ]
        
        if not recent_performance:
            return
        
        # Calculate error rate
        total_requests = len(recent_performance)
        error_requests = len([p for p in recent_performance if p.error_rate > 0])
        error_rate = error_requests / total_requests if total_requests > 0 else 0
        
        # Calculate throughput (requests per minute)
        if recent_performance:
            time_span = (recent_performance[-1].timestamp - recent_performance[0].timestamp).total_seconds() / 60
            throughput = total_requests / time_span if time_span > 0 else 0
        else:
            throughput = 0
        
        # Update model performance records
        for perf in recent_performance:
            perf.error_rate = error_rate
            perf.throughput = throughput
    
    async def _check_alerts(self, trace: AITrace):
        """Check for alerts based on trace"""
        if trace.duration and trace.duration > self.alert_thresholds['response_time']:
            await self._create_alert(
                severity=Severity.WARNING,
                message=f"High response time for {trace.operation_name}: {trace.duration:.2f}s",
                context={"trace_id": trace.trace_id, "operation": trace.operation_name}
            )
        
        if trace.status == "error":
            await self._create_alert(
                severity=Severity.ERROR,
                message=f"Error in {trace.operation_name}",
                context={"trace_id": trace.trace_id, "operation": trace.operation_name}
            )
    
    async def _check_model_alerts(self, performance: ModelPerformanceMetrics):
        """Check for model performance alerts"""
        if performance.error_rate > self.alert_thresholds['error_rate']:
            await self._create_alert(
                severity=Severity.WARNING,
                message=f"High error rate for {performance.model_name}: {performance.error_rate:.2%}",
                context={"model": performance.model_name, "error_rate": performance.error_rate}
            )
        
        if performance.hallucination_score and performance.hallucination_score > self.alert_thresholds['hallucination_rate']:
            await self._create_alert(
                severity=Severity.WARNING,
                message=f"High hallucination rate for {performance.model_name}: {performance.hallucination_score:.2%}",
                context={"model": performance.model_name, "hallucination_rate": performance.hallucination_score}
            )
        
        # Check cost threshold
        recent_cost = sum(
            p.cost for p in self.model_performance 
            if p.model_name == performance.model_name and 
            p.timestamp > datetime.now() - timedelta(hours=1)
        )
        
        if recent_cost > self.alert_thresholds['cost_threshold']:
            await self._create_alert(
                severity=Severity.WARNING,
                message=f"High cost for {performance.model_name}: ${recent_cost:.2f} in last hour",
                context={"model": performance.model_name, "cost": recent_cost}
            )
    
    async def _check_business_alerts(self, business_metric: BusinessMetric):
        """Check for business metric alerts"""
        # Implement business-specific alert logic
        pass
    
    async def _create_alert(self, severity: Severity, message: str, context: Dict[str, Any]):
        """Create an alert"""
        alert = {
            "id": str(uuid.uuid4()),
            "severity": severity.value,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "acknowledged": False
        }
        
        self.alerts.append(alert)
        
        # Log alert
        log_level = {
            Severity.INFO: logging.INFO,
            Severity.WARNING: logging.WARNING,
            Severity.ERROR: logging.ERROR,
            Severity.CRITICAL: logging.CRITICAL
        }
        
        logger.log(log_level[severity], f"ALERT [{severity.value}]: {message}")
        
        # Send notifications for critical alerts
        if severity in [Severity.ERROR, Severity.CRITICAL]:
            await self._send_notification(alert)
    
    async def _send_notification(self, alert: Dict[str, Any]):
        """Send notification for critical alerts"""
        # Implement notification system (email, Slack, SMS, etc.)
        logger.critical(f"CRITICAL ALERT NOTIFICATION: {alert['message']}")
    
    async def get_performance_summary(self, model_name: Optional[str] = None,
                                    time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Get performance summary for specified model and time window"""
        cutoff_time = datetime.now() - time_window
        
        # Filter performance data
        if model_name:
            filtered_performance = [
                p for p in self.model_performance 
                if p.model_name == model_name and p.timestamp > cutoff_time
            ]
        else:
            filtered_performance = [
                p for p in self.model_performance 
                if p.timestamp > cutoff_time
            ]
        
        if not filtered_performance:
            return {
                "total_requests": 0,
                "average_response_time": 0,
                "total_cost": 0,
                "error_rate": 0,
                "throughput": 0
            }
        
        # Calculate summary statistics
        total_requests = len(filtered_performance)
        average_response_time = statistics.mean([p.response_time for p in filtered_performance])
        total_cost = sum([p.cost for p in filtered_performance])
        error_rate = statistics.mean([p.error_rate for p in filtered_performance])
        throughput = statistics.mean([p.throughput for p in filtered_performance])
        
        return {
            "total_requests": total_requests,
            "average_response_time": round(average_response_time, 3),
            "total_cost": round(total_cost, 2),
            "error_rate": round(error_rate, 3),
            "throughput": round(throughput, 2),
            "time_window_hours": time_window.total_seconds() / 3600
        }
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active (unacknowledged) alerts"""
        return [alert for alert in self.alerts if not alert["acknowledged"]]
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.now().isoformat()
                return True
        return False
    
    async def get_trace_details(self, trace_id: str) -> Optional[AITrace]:
        """Get detailed trace information"""
        for trace in self.traces_store:
            if trace.trace_id == trace_id:
                return trace
        return None
    
    async def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format"""
        if format == "json":
            return json.dumps({
                "metrics": [asdict(m) for m in self.metrics_store],
                "traces": [asdict(t) for t in self.traces_store],
                "model_performance": [asdict(m) for m in self.model_performance],
                "business_metrics": [asdict(b) for b in self.business_metrics],
                "alerts": self.alerts
            }, indent=2, default=str)
        
        # Add support for other formats (Prometheus, InfluxDB, etc.)
        return ""

class LangSmithIntegration:
    """Integration with LangSmith for advanced AI observability"""
    
    def __init__(self, api_key: str, project_name: str):
        self.api_key = api_key
        self.project_name = project_name
        self.base_url = "https://api.smith.langchain.com"
    
    async def log_run(self, run_data: Dict[str, Any]):
        """Log a run to LangSmith"""
        # Implement LangSmith API integration
        logger.info(f"Logging run to LangSmith: {run_data}")
    
    async def log_feedback(self, run_id: str, feedback: Dict[str, Any]):
        """Log feedback for a run"""
        # Implement feedback logging
        logger.info(f"Logging feedback for run {run_id}: {feedback}")

class WeightsBiasesIntegration:
    """Integration with Weights & Biases for experiment tracking"""
    
    def __init__(self, api_key: str, project_name: str):
        self.api_key = api_key
        self.project_name = project_name
    
    async def log_experiment(self, experiment_data: Dict[str, Any]):
        """Log experiment data to W&B"""
        # Implement W&B API integration
        logger.info(f"Logging experiment to W&B: {experiment_data}")
    
    async def log_metrics(self, metrics: Dict[str, float], step: int = None):
        """Log metrics to W&B"""
        # Implement metrics logging
        logger.info(f"Logging metrics to W&B: {metrics}")
