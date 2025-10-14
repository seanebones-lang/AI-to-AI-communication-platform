"""
Real-time AI Streaming System
Implements streaming AI responses with Server-Sent Events and WebSocket enhancements
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, AsyncGenerator, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class StreamEventType(Enum):
    START = "start"
    CHUNK = "chunk"
    THINKING = "thinking"
    PROGRESS = "progress"
    ERROR = "error"
    COMPLETE = "complete"
    METADATA = "metadata"

@dataclass
class StreamEvent:
    event_type: StreamEventType
    data: Dict[str, Any]
    timestamp: datetime
    stream_id: str
    sequence_number: int

@dataclass
class StreamingConfig:
    chunk_size: int = 100
    max_chunk_delay: float = 0.1  # seconds
    buffer_size: int = 1024
    compression_enabled: bool = True
    backpressure_threshold: float = 0.8

class AIStreamingManager:
    """
    AI Streaming Manager for real-time AI response streaming
    """
    
    def __init__(self, config: StreamingConfig = None):
        self.config = config or StreamingConfig()
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.stream_handlers: Dict[str, Callable] = {}
        self.backpressure_queues: Dict[str, asyncio.Queue] = {}
        
        # Performance tracking
        self.stream_stats = {
            "total_streams": 0,
            "active_streams": 0,
            "total_chunks": 0,
            "average_latency": 0.0,
            "backpressure_events": 0
        }
    
    async def start_stream(self, stream_id: str, initial_data: Dict[str, Any]) -> str:
        """Start a new AI streaming session"""
        try:
            stream_info = {
                "id": stream_id,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "status": "active",
                "chunks_sent": 0,
                "total_size": 0,
                "subscribers": [],
                "backpressure_detected": False
            }
            
            self.active_streams[stream_id] = stream_info
            self.backpressure_queues[stream_id] = asyncio.Queue(maxsize=100)
            
            self.stream_stats["total_streams"] += 1
            self.stream_stats["active_streams"] += 1
            
            # Send start event
            await self._send_stream_event(stream_id, StreamEventType.START, {
                "stream_id": stream_id,
                "config": asdict(self.config),
                "initial_data": initial_data
            })
            
            logger.info(f"Started AI stream: {stream_id}")
            return stream_id
            
        except Exception as e:
            logger.error(f"Failed to start stream {stream_id}: {e}")
            raise
    
    async def stream_ai_response(self, stream_id: str, query: str, 
                               ai_provider, context: Dict[str, Any] = None) -> AsyncGenerator[StreamEvent, None]:
        """
        Stream AI response with real-time chunking and backpressure handling
        """
        try:
            # Start thinking phase
            await self._send_stream_event(stream_id, StreamEventType.THINKING, {
                "message": "AI is processing your request...",
                "progress": 0
            })
            
            # Generate streaming response
            async for chunk in self._generate_streaming_response(query, ai_provider, context):
                # Check for backpressure
                if await self._check_backpressure(stream_id):
                    await self._handle_backpressure(stream_id)
                
                # Send chunk
                await self._send_stream_event(stream_id, StreamEventType.CHUNK, {
                    "content": chunk["content"],
                    "metadata": chunk.get("metadata", {}),
                    "progress": chunk.get("progress", 0)
                })
                
                # Update stream statistics
                await self._update_stream_stats(stream_id, chunk)
            
            # Send completion event
            await self._send_stream_event(stream_id, StreamEventType.COMPLETE, {
                "message": "Response completed successfully",
                "total_chunks": self.active_streams[stream_id]["chunks_sent"]
            })
            
        except Exception as e:
            # Send error event
            await self._send_stream_event(stream_id, StreamEventType.ERROR, {
                "error": str(e),
                "error_type": type(e).__name__
            })
            logger.error(f"Stream error for {stream_id}: {e}")
        
        finally:
            await self._cleanup_stream(stream_id)
    
    async def _generate_streaming_response(self, query: str, ai_provider, 
                                         context: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate streaming response from AI provider
        """
        try:
            # Simulate streaming response (in real implementation, this would
            # integrate with actual streaming AI providers like OpenAI's streaming API)
            
            # Mock streaming response for demonstration
            response_parts = [
                "Based on your request, I'll help you with the following:",
                "\n\n1. First, let's analyze the requirements...",
                "\n2. Next, I'll process the data...",
                "\n3. Finally, I'll provide the solution.",
                "\n\nHere's the detailed response you requested."
            ]
            
            total_parts = len(response_parts)
            
            for i, part in enumerate(response_parts):
                # Simulate processing delay
                await asyncio.sleep(0.1)
                
                # Calculate progress
                progress = (i + 1) / total_parts
                
                yield {
                    "content": part,
                    "metadata": {
                        "part": i + 1,
                        "total_parts": total_parts,
                        "timestamp": datetime.now().isoformat()
                    },
                    "progress": progress
                }
        
        except Exception as e:
            logger.error(f"Error generating streaming response: {e}")
            yield {
                "content": f"Error: {str(e)}",
                "metadata": {"error": True},
                "progress": 1.0
            }
    
    async def _send_stream_event(self, stream_id: str, event_type: StreamEventType, 
                               data: Dict[str, Any]):
        """Send stream event to all subscribers"""
        if stream_id not in self.active_streams:
            return
        
        stream_info = self.active_streams[stream_id]
        
        # Create stream event
        event = StreamEvent(
            event_type=event_type,
            data=data,
            timestamp=datetime.now(),
            stream_id=stream_id,
            sequence_number=stream_info["chunks_sent"]
        )
        
        # Add to backpressure queue
        try:
            await asyncio.wait_for(
                self.backpressure_queues[stream_id].put(event),
                timeout=1.0
            )
        except asyncio.TimeoutError:
            # Handle backpressure
            await self._handle_backpressure(stream_id)
        
        # Notify subscribers
        await self._notify_subscribers(stream_id, event)
    
    async def _notify_subscribers(self, stream_id: str, event: StreamEvent):
        """Notify all subscribers of stream event"""
        if stream_id not in self.active_streams:
            return
        
        stream_info = self.active_streams[stream_id]
        
        # Send to all subscribers
        for subscriber in stream_info["subscribers"]:
            try:
                await subscriber(event)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
    
    async def subscribe_to_stream(self, stream_id: str, 
                                callback: Callable[[StreamEvent], None]) -> str:
        """Subscribe to stream events"""
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream {stream_id} not found")
        
        subscriber_id = f"sub_{len(self.active_streams[stream_id]['subscribers'])}"
        self.active_streams[stream_id]["subscribers"].append(callback)
        
        logger.info(f"Subscribed {subscriber_id} to stream {stream_id}")
        return subscriber_id
    
    async def unsubscribe_from_stream(self, stream_id: str, subscriber_id: str):
        """Unsubscribe from stream events"""
        if stream_id not in self.active_streams:
            return
        
        # Remove subscriber (simplified implementation)
        stream_info = self.active_streams[stream_id]
        if stream_info["subscribers"]:
            stream_info["subscribers"].pop()
        
        logger.info(f"Unsubscribed {subscriber_id} from stream {stream_id}")
    
    async def _check_backpressure(self, stream_id: str) -> bool:
        """Check if stream is experiencing backpressure"""
        if stream_id not in self.backpressure_queues:
            return False
        
        queue = self.backpressure_queues[stream_id]
        queue_size = queue.qsize()
        max_size = queue.maxsize
        
        backpressure_ratio = queue_size / max_size
        return backpressure_ratio > self.config.backpressure_threshold
    
    async def _handle_backpressure(self, stream_id: str):
        """Handle backpressure by slowing down or buffering"""
        if stream_id not in self.active_streams:
            return
        
        stream_info = self.active_streams[stream_id]
        stream_info["backpressure_detected"] = True
        self.stream_stats["backpressure_events"] += 1
        
        # Slow down stream
        await asyncio.sleep(0.1)
        
        # Send backpressure event
        await self._send_stream_event(stream_id, StreamEventType.METADATA, {
            "type": "backpressure",
            "message": "Stream experiencing high load, slowing down...",
            "timestamp": datetime.now().isoformat()
        })
        
        logger.warning(f"Backpressure detected for stream {stream_id}")
    
    async def _update_stream_stats(self, stream_id: str, chunk: Dict[str, Any]):
        """Update stream statistics"""
        if stream_id not in self.active_streams:
            return
        
        stream_info = self.active_streams[stream_id]
        stream_info["chunks_sent"] += 1
        stream_info["total_size"] += len(chunk.get("content", ""))
        stream_info["last_activity"] = datetime.now()
        
        self.stream_stats["total_chunks"] += 1
    
    async def _cleanup_stream(self, stream_id: str):
        """Clean up stream resources"""
        if stream_id in self.active_streams:
            del self.active_streams[stream_id]
            self.stream_stats["active_streams"] -= 1
        
        if stream_id in self.backpressure_queues:
            del self.backpressure_queues[stream_id]
        
        logger.info(f"Cleaned up stream: {stream_id}")
    
    async def get_stream_status(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of stream"""
        if stream_id not in self.active_streams:
            return None
        
        stream_info = self.active_streams[stream_id]
        
        return {
            "stream_id": stream_id,
            "status": stream_info["status"],
            "created_at": stream_info["created_at"].isoformat(),
            "last_activity": stream_info["last_activity"].isoformat(),
            "chunks_sent": stream_info["chunks_sent"],
            "total_size": stream_info["total_size"],
            "subscriber_count": len(stream_info["subscribers"]),
            "backpressure_detected": stream_info["backpressure_detected"]
        }
    
    async def get_streaming_stats(self) -> Dict[str, Any]:
        """Get overall streaming statistics"""
        return {
            "total_streams": self.stream_stats["total_streams"],
            "active_streams": self.stream_stats["active_streams"],
            "total_chunks": self.stream_stats["total_chunks"],
            "average_latency": self.stream_stats["average_latency"],
            "backpressure_events": self.stream_stats["backpressure_events"],
            "streams": list(self.active_streams.keys())
        }

class ServerSentEventsHandler:
    """
    Server-Sent Events handler for real-time AI streaming
    """
    
    def __init__(self, streaming_manager: AIStreamingManager):
        self.streaming_manager = streaming_manager
    
    async def handle_sse_connection(self, stream_id: str, 
                                  response_callback: Callable[[str], None]):
        """
        Handle Server-Sent Events connection for streaming
        """
        try:
            # Subscribe to stream events
            subscriber_id = await self.streaming_manager.subscribe_to_stream(
                stream_id, 
                lambda event: self._format_sse_event(event, response_callback)
            )
            
            # Send initial connection event
            await response_callback(f"data: {json.dumps({'type': 'connected', 'stream_id': stream_id})}\n\n")
            
            # Keep connection alive
            while True:
                await asyncio.sleep(1)
                
                # Check if stream is still active
                status = await self.streaming_manager.get_stream_status(stream_id)
                if not status or status["status"] != "active":
                    break
            
        except Exception as e:
            logger.error(f"SSE connection error for stream {stream_id}: {e}")
            await response_callback(f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n")
        
        finally:
            # Cleanup subscription
            await self.streaming_manager.unsubscribe_from_stream(stream_id, subscriber_id)
    
    async def _format_sse_event(self, event: StreamEvent, 
                              response_callback: Callable[[str], None]):
        """Format stream event for SSE"""
        sse_data = {
            "type": event.event_type.value,
            "data": event.data,
            "timestamp": event.timestamp.isoformat(),
            "sequence": event.sequence_number
        }
        
        sse_message = f"data: {json.dumps(sse_data)}\n\n"
        await response_callback(sse_message)

class WebSocketStreamingHandler:
    """
    WebSocket handler for bidirectional streaming
    """
    
    def __init__(self, streaming_manager: AIStreamingManager):
        self.streaming_manager = streaming_manager
        self.websocket_connections: Dict[str, Any] = {}
    
    async def handle_websocket_connection(self, websocket, stream_id: str):
        """
        Handle WebSocket connection for bidirectional streaming
        """
        try:
            self.websocket_connections[stream_id] = websocket
            
            # Subscribe to stream events
            subscriber_id = await self.streaming_manager.subscribe_to_stream(
                stream_id,
                lambda event: self._send_websocket_event(websocket, event)
            )
            
            # Send connection confirmation
            await websocket.send(json.dumps({
                "type": "connected",
                "stream_id": stream_id,
                "timestamp": datetime.now().isoformat()
            }))
            
            # Handle incoming messages
            async for message in websocket:
                await self._handle_websocket_message(websocket, stream_id, message)
            
        except Exception as e:
            logger.error(f"WebSocket connection error for stream {stream_id}: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }))
        
        finally:
            # Cleanup
            if stream_id in self.websocket_connections:
                del self.websocket_connections[stream_id]
            
            await self.streaming_manager.unsubscribe_from_stream(stream_id, subscriber_id)
    
    async def _send_websocket_event(self, websocket, event: StreamEvent):
        """Send stream event via WebSocket"""
        try:
            websocket_data = {
                "type": event.event_type.value,
                "data": event.data,
                "timestamp": event.timestamp.isoformat(),
                "sequence": event.sequence_number
            }
            
            await websocket.send(json.dumps(websocket_data))
        
        except Exception as e:
            logger.error(f"Error sending WebSocket event: {e}")
    
    async def _handle_websocket_message(self, websocket, stream_id: str, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "ping":
                await websocket.send(json.dumps({"type": "pong"}))
            
            elif message_type == "control":
                await self._handle_stream_control(stream_id, data.get("action"), data.get("params", {}))
            
            else:
                logger.warning(f"Unknown WebSocket message type: {message_type}")
        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in WebSocket message: {message}")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def _handle_stream_control(self, stream_id: str, action: str, params: Dict[str, Any]):
        """Handle stream control commands"""
        if action == "pause":
            # Implement stream pausing
            pass
        elif action == "resume":
            # Implement stream resuming
            pass
        elif action == "cancel":
            # Implement stream cancellation
            await self.streaming_manager._cleanup_stream(stream_id)
        
        logger.info(f"Stream control action '{action}' for stream {stream_id}")

class ProgressiveLoadingManager:
    """
    Progressive loading manager for large AI responses
    """
    
    def __init__(self, streaming_manager: AIStreamingManager):
        self.streaming_manager = streaming_manager
        self.loading_strategies = {}
    
    async def load_progressively(self, stream_id: str, content: str, 
                               chunk_size: int = 100) -> AsyncGenerator[str, None]:
        """
        Load content progressively with intelligent chunking
        """
        try:
            # Analyze content for optimal chunking
            chunks = self._intelligent_chunk(content, chunk_size)
            
            total_chunks = len(chunks)
            
            for i, chunk in enumerate(chunks):
                # Send progress update
                progress = (i + 1) / total_chunks
                
                await self.streaming_manager._send_stream_event(
                    stream_id, 
                    StreamEventType.PROGRESS, 
                    {
                        "chunk": chunk,
                        "progress": progress,
                        "chunk_number": i + 1,
                        "total_chunks": total_chunks
                    }
                )
                
                yield chunk
                
                # Adaptive delay based on content complexity
                delay = self._calculate_adaptive_delay(chunk)
                await asyncio.sleep(delay)
        
        except Exception as e:
            logger.error(f"Progressive loading error for stream {stream_id}: {e}")
            yield f"Error: {str(e)}"
    
    def _intelligent_chunk(self, content: str, target_size: int) -> List[str]:
        """Intelligently chunk content based on structure"""
        # Simple implementation - can be enhanced with NLP
        words = content.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) + 1 > target_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                current_size += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _calculate_adaptive_delay(self, chunk: str) -> float:
        """Calculate adaptive delay based on chunk complexity"""
        # Simple implementation - can be enhanced with complexity analysis
        base_delay = 0.05  # 50ms base delay
        
        # Increase delay for longer chunks
        length_factor = min(2.0, len(chunk) / 100)
        
        # Increase delay for complex content (more punctuation, numbers, etc.)
        complexity_factor = 1.0
        if any(char in chunk for char in ".,!?;:"):
            complexity_factor += 0.2
        if any(char.isdigit() for char in chunk):
            complexity_factor += 0.1
        
        return base_delay * length_factor * complexity_factor
