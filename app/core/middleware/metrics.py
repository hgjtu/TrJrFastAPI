from prometheus_client import Counter, Histogram, start_http_server
from fastapi import Request
import time
from typing import Callable

# Метрики для HTTP запросов
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Метрики для ошибок
http_errors_total = Counter(
    'http_errors_total',
    'Total number of HTTP errors',
    ['method', 'endpoint', 'error_type']
)

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app
        # Запускаем сервер метрик на порту 8001
        start_http_server(8001)

    async def __call__(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Записываем метрики
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=status_code
            ).inc()
            
            # Записываем длительность запроса
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            # Если статус код указывает на ошибку, записываем в метрики ошибок
            if status_code >= 400:
                http_errors_total.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    error_type=str(status_code)
                ).inc()
                
            return response
            
        except Exception as e:
            # Записываем метрики для необработанных исключений
            http_errors_total.labels(
                method=request.method,
                endpoint=request.url.path,
                error_type=type(e).__name__
            ).inc()
            raise 