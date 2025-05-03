from typing import Dict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class Metrics:
    def __init__(self):
        self.requests = 0
        self.durations = []
        self.errors = 0

    def record_request(self):
        self.requests += 1

    def record_duration(self, duration: float):
        self.durations.append(duration)

    def record_error(self):
        self.errors += 1

    def get_metrics(self) -> Dict:
        return {
            "requests": self.requests,
            "avg_duration": sum(self.durations) / len(self.durations) if self.durations else 0,
            "errors": self.errors
        }

metrics = Metrics()

class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        metrics.record_request()
        
        try:
            response = await call_next(request)
            duration = response.headers.get("X-Response-Time", 0)
            metrics.record_duration(float(duration))
            return response
        except Exception as e:
            metrics.record_error()
            raise e 