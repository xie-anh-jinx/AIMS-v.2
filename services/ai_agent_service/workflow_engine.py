"""
Workflow Engine — Orchestrates the full agent pipeline.
Receives triggered actions from RuleEngine and executes them in sequence.
"""
import logging
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from typing import List
from packages.database.models import AgentLog, Student, AcademicRecord
from packages.database.connection import SessionLocal
from services.ai_agent_service.rule_engine import RuleEngine, RuleAction
from services.notification_service.notification_engine import NotificationEngine

logger = logging.getLogger("WorkflowEngine")

class WorkflowEngine:
    def __init__(self):
        self.rule_engine = RuleEngine()

    def run_full_evaluation(self) -> dict:
        """Evaluate ALL students and trigger appropriate actions."""
        db = SessionLocal()
        try:
            students = db.query(Student).filter(Student.status == "Aktif").all()
            total_actions = 0
            total_notifications = 0

            logger.info(f"[WorkflowEngine] Starting full evaluation for {len(students)} active students...")

            for student in students:
                records = (
                    db.query(AcademicRecord)
                    .filter(AcademicRecord.student_id == student.id)
                    .order_by(AcademicRecord.semester.desc())
                    .all()
                )
                student_dict = {
                    "id": student.id,
                    "nim": student.nim,
                    "nama": student.nama,
                    "semester": student.semester,
                    "nomor_whatsapp": student.nomor_whatsapp,
                }
                records_list = [
                    {"semester": r.semester, "ips": r.ips, "ipk": r.ipk, "sks": r.sks, "status": r.status}
                    for r in records
                ]

                actions = self.rule_engine.evaluate_student(student_dict, records_list)
                total_actions += len(actions)

                notifier = NotificationEngine(db)
                for action in actions:
                    self._execute_action(action, notifier, db)
                    total_notifications += 1

            summary = {
                "students_evaluated": len(students),
                "rules_triggered": total_actions,
                "notifications_sent": total_notifications,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Log the scheduler run
            db.add(AgentLog(
                event_type="WORKFLOW_RUN",
                action="FULL_EVALUATION",
                status="SUCCESS",
                message=f"Evaluated {len(students)} students. {total_actions} rules triggered. {total_notifications} notifications.",
            ))
            db.commit()
            logger.info(f"[WorkflowEngine] Completed: {summary}")
            return summary

        except Exception as e:
            logger.error(f"[WorkflowEngine] Error: {e}")
            db.add(AgentLog(
                event_type="WORKFLOW_RUN", action="FULL_EVALUATION",
                status="FAILED", message=str(e),
            ))
            db.commit()
            return {"error": str(e)}
        finally:
            db.close()

    def evaluate_single_student(self, student_id: int) -> List[dict]:
        """Evaluate rules for a single student (called on grade update event)."""
        db = SessionLocal()
        try:
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                return []

            records = (
                db.query(AcademicRecord)
                .filter(AcademicRecord.student_id == student_id)
                .order_by(AcademicRecord.semester.desc())
                .all()
            )
            student_dict = {
                "id": student.id, "nim": student.nim, "nama": student.nama,
                "semester": student.semester, "nomor_whatsapp": student.nomor_whatsapp,
            }
            records_list = [
                {"semester": r.semester, "ips": r.ips, "ipk": r.ipk, "sks": r.sks, "status": r.status}
                for r in records
            ]
            actions = self.rule_engine.evaluate_student(student_dict, records_list)

            notifier = NotificationEngine(db)
            results = []
            for action in actions:
                self._execute_action(action, notifier, db)
                results.append({"rule": action.rule_name, "action": action.action, "severity": action.severity})

            db.commit()
            return results
        finally:
            db.close()

    def _execute_action(self, action: RuleAction, notifier: NotificationEngine, db):
        """Execute a single rule action: log it and send notifications."""
        # Log the rule trigger
        db.add(AgentLog(
            event_type="RULE_TRIGGERED",
            student_id=action.student_id,
            rule_name=action.rule_name,
            action=action.action,
            status="SUCCESS",
            message=f"[{action.severity}] {action.rule_name} for {action.student_nim}",
        ))

        # Send WhatsApp notification to student
        if action.student_whatsapp:
            notifier.send("WHATSAPP", action.student_whatsapp, action.message, action.student_id)

        # Also notify advisor via Telegram for HIGH severity
        if action.notify_advisor:
            # SYSTEM log (always)
            notifier.send("SYSTEM", "advisor-channel",
                          f"[ALERT] {action.rule_name}\n" + action.message, action.student_id)
            # Telegram to advisor (requires advisor's Telegram chat_id to be stored)
            # For now, broadcast to the configured Telegram bot so advisors can see it
            notifier.send("TELEGRAM", "advisor-broadcast",
                          f"🚨 *AIMS ALERT*\n" + action.message, action.student_id)

        logger.info(f"Action executed: {action.rule_name} → {action.action} for {action.student_nim}")
