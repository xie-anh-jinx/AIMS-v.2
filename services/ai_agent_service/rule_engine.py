"""
Rule Engine — Evaluates all academic business rules.
Returns a list of actions to be performed by the Workflow Engine.
"""
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger("RuleEngine")

@dataclass
class RuleAction:
    rule_name: str
    action: str
    severity: str  # HIGH, MEDIUM, LOW
    student_id: int
    student_nim: str
    student_nama: str
    student_whatsapp: str
    message: str
    notify_advisor: bool = False

class RuleEngine:
    """
    Stateless rule evaluator. Given a student's full academic profile,
    returns a list of triggered RuleActions.
    """

    def evaluate_student(self, student: dict, records: List[dict]) -> List[RuleAction]:
        actions = []
        if not records:
            return actions

        latest = records[0]  # Most recent semester
        sem = student.get("semester", 0)
        sks = latest.get("sks", 0)
        ipk = latest.get("ipk", 0.0)
        ips = latest.get("ips", 0.0)

        base = dict(
            student_id=student["id"],
            student_nim=student["nim"],
            student_nama=student["nama"],
            student_whatsapp=student.get("nomor_whatsapp", ""),
        )

        # ── Rule 1: HIGH RISK — Long Study + Low SKS ─────────────────────────
        if sem >= 8 and sks < 120:
            actions.append(RuleAction(
                **base,
                rule_name="LONG_STUDY_LOW_SKS",
                action="NOTIFY_ADVISOR",
                severity="HIGH",
                message=(
                    f"⚠️ *PERINGATAN RISIKO DO*\n\n"
                    f"Mahasiswa: *{student['nama']}* ({student['nim']})\n"
                    f"Semester: {sem} | Total SKS: {sks} (min. 120)\n\n"
                    f"Mahasiswa berisiko tidak lulus tepat waktu. "
                    f"Segera lakukan konsultasi dengan PA."
                ),
                notify_advisor=True
            ))

        # ── Rule 2: IPK Below Minimum ────────────────────────────────────────
        if ipk < 2.0:
            actions.append(RuleAction(
                **base,
                rule_name="LOW_IPK",
                action="NOTIFY_ADVISOR",
                severity="HIGH",
                message=(
                    f"📉 *IPK DI BAWAH STANDAR*\n\n"
                    f"Mahasiswa: *{student['nama']}* ({student['nim']})\n"
                    f"IPK Saat Ini: *{ipk:.2f}* (standar minimum: 2.00)\n\n"
                    f"Harap segera konsultasi dengan Dosen PA."
                ),
                notify_advisor=True
            ))

        # ── Rule 3: IPS Warning ───────────────────────────────────────────────
        elif ips < 2.0 and ipk >= 2.0:
            actions.append(RuleAction(
                **base,
                rule_name="LOW_IPS_WARNING",
                action="SEND_REMINDER",
                severity="MEDIUM",
                message=(
                    f"📊 *PERINGATAN IPS RENDAH*\n\n"
                    f"Halo {student['nama']}, IPS Anda semester ini *{ips:.2f}*.\n"
                    f"Tingkatkan prestasi belajar Anda untuk menjaga IPK. Semangat! 💪"
                ),
                notify_advisor=False
            ))

        # ── Rule 4: Consecutive IPK Drop ─────────────────────────────────────
        if len(records) >= 2:
            prev_ipk = records[1].get("ipk", 0.0)
            if ipk < prev_ipk - 0.3:  # Dropped more than 0.3 points
                actions.append(RuleAction(
                    **base,
                    rule_name="CONSECUTIVE_IPK_DROP",
                    action="NOTIFY_ADVISOR",
                    severity="MEDIUM",
                    message=(
                        f"📉 *PENURUNAN IPK SIGNIFIKAN*\n\n"
                        f"Mahasiswa: *{student['nama']}* ({student['nim']})\n"
                        f"IPK sebelumnya: {prev_ipk:.2f} → sekarang: {ipk:.2f}\n\n"
                        f"Penurunan IPK terdeteksi. Pertimbangkan sesi konsultasi."
                    ),
                    notify_advisor=True
                ))

        logger.info(f"Evaluated {student['nim']}: {len(actions)} rule(s) triggered.")
        return actions
