from enum import Enum

class TaskType(str, Enum):
    EMAIL_CAMPAIGNS = "email_campaigns"
    DATA_SYNCING = "data_syncing"
    SEND_COMIC = "send_comic"

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED =  "completed"
