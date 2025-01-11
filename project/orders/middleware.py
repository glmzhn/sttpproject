from collections import defaultdict
from threading import Lock


# Class for Processing Metrics
class MetricsMiddleware:
    metrics = defaultdict(lambda: {"total_calls": 0, "success": 0, "errors": 0})
    lock = Lock()

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        endpoint = request.path
        status_code = response.status_code

        # Writing Metrics
        with self.lock:
            self.metrics[endpoint]["total_calls"] += 1
            if 200 <= status_code < 400:
                self.metrics[endpoint]["success"] += 1
            else:
                self.metrics[endpoint]["errors"] += 1

        return response

    @classmethod
    def get_metrics(cls):
        with cls.lock:
            return dict(cls.metrics)
