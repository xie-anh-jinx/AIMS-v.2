import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgentEngine")

class RuleEngine:
    def evaluate(self, event):
        logger.info(f"Evaluating rules for event: {event}")
        # Example rule: IF Semester >= 8 AND SKS < 120 -> Risk = HIGH
        if event.get('type') == 'student_update':
            data = event.get('data', {})
            if data.get('semester', 0) >= 8 and data.get('sks', 0) < 120:
                logger.warning(f"HIGH RISK identified for student {data.get('nim')}")
                return {'action': 'notify_advisor', 'risk': 'HIGH', 'student_id': data.get('id')}
        return None

class WorkflowEngine:
    def execute(self, action):
        logger.info(f"Executing workflow action: {action}")
        if action.get('action') == 'notify_advisor':
            # Add to task queue
            logger.info("Adding notification task to Queue")
            self._queue_task(action)

    def _queue_task(self, task):
        # In a real app, this sends to Celery / Redis
        logger.info(f"[Queue] Task added: {task}")

class EventListener:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.workflow_engine = WorkflowEngine()

    def on_event(self, event_payload):
        logger.info(f"Event received: {event_payload}")
        action = self.rule_engine.evaluate(event_payload)
        if action:
            self.workflow_engine.execute(action)

# Singleton initialized engine
agent_engine = EventListener()
