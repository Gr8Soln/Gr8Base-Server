from kombu import Queue

# Queues
task_queues = (
    Queue("default"),
    Queue("resume"),
    Queue("scoring"),
    Queue("generation"),
    Queue("embedding"),
    Queue("analytics"),
    Queue("rendering"),
)

task_default_queue = "default"

# Routing
task_routes = {
    "app.adapters.queue.tasks.resume_tasks.*": {"queue": "resume"},
    "app.adapters.queue.tasks.scoring_tasks.*": {"queue": "scoring"},
    "app.adapters.queue.tasks.generation_tasks.*": {"queue": "generation"},
    "app.adapters.queue.tasks.embedding_tasks.*": {"queue": "embedding"},
    "app.adapters.queue.tasks.analytics_tasks.*": {"queue": "analytics"},
    "app.adapters.queue.tasks.render_tasks.*": {"queue": "rendering"},
}

# Serialization
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

# Reliability
task_acks_late = True
task_reject_on_worker_lost = True
task_track_started = True

# Retries
task_max_retries = 3
task_default_retry_delay = 60

# Result expiry (24h)
result_expires = 86400

# Beat schedule (analytics aggregation)
beat_schedule = {
    "aggregate-analytics-daily": {
        "task": "app.adapters.queue.tasks.analytics_tasks.aggregate_daily_analytics",
        "schedule": 86400.0,
    },
}

timezone = "UTC"
