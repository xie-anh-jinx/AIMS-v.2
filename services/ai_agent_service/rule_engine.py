"""
Rule Engine — Evaluates all academic business rules.
Returns a list of actions to be performed by the Workflow Engine.
"""
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

from packages.shared.degree_rules import get_degree_level, get_degree_rules

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
    advisor_id: Optional[int] = None
    advisor_nama: Optional[str] = None
    advisor_whatsapp: Optional[str] = None

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

        prodi_name = student.get("prodi", "")
        level = get_degree_level(prodi_name)
        rules = get_degree_rules(prodi_name)

        min_sks = rules["min_sks"]
        max_sem = rules["max_semesters"]
        warn_sem = rules["warning_semesters"]

        base = dict(
            student_id=student["id"],
            student_nim=student["nim"],
            student_nama=student["nama"],
            student_whatsapp=student.get("nomor_whatsapp", ""),
            advisor_id=student.get("advisor_id"),
            advisor_nama=student.get("advisor_nama"),
            advisor_whatsapp=student.get("advisor_whatsapp"),
        )

        from packages.shared.degree_rules import evaluate_academic_risk
        calculated_risk = evaluate_academic_risk(prodi_name, sem, sks, ipk)
        
        # ── Rule 1: HIGH RISK (Zona Merah Terpadu) ──
        if calculated_risk == "HIGH_RISK":
            # Tentukan alasan spesifik untuk pesan WhatsApp
            if ipk < 2.0:
                reason = f"IPK Anda sangat rendah ({ipk:.2f})."
            elif sem >= max_sem:
                reason = f"Anda telah mencapai/melewati batas maksimal masa studi ({sem}/{max_sem} Semester)."
            else:
                reason = f"Performa akademik Anda berada di Zona Merah (SKS: {sks}, IPK: {ipk:.2f})."
                
            actions.append(RuleAction(
                **base,
                rule_name="ACADEMIC_HIGH_RISK",
                action="NOTIFY_ADVISOR",
                severity="HIGH",
                message=(
                    f"🚨 *PERINGATAN ZONA MERAH (DO)*\n\n"
                    f"Mahasiswa: *{student['nama']}* ({student['nim']})\n"
                    f"Prodi: {prodi_name} ({level})\n"
                    f"Semester: {sem} | Total SKS: {sks} | IPK: {ipk:.2f}\n\n"
                    f"Alasan: {reason}\n"
                    f"Segera lakukan konsultasi wajib dengan Dosen PA."
                ),
                notify_advisor=True
            ))
            
        # ── Rule 2: WARNING (Zona Kuning) ──
        elif calculated_risk == "Warning":
            actions.append(RuleAction(
                **base,
                rule_name="ACADEMIC_WARNING",
                action="SEND_REMINDER",
                severity="MEDIUM",
                message=(
                    f"⚠️ *PERINGATAN ZONA KUNING*\n\n"
                    f"Halo {student['nama']}, performa akademik Anda berada di ambang batas peringatan.\n"
                    f"Semester: {sem} | Total SKS: {sks} | IPK: {ipk:.2f}\n\n"
                    f"Tingkatkan prestasi Anda dan jangan ragu berdiskusi dengan Dosen PA."
                ),
                notify_advisor=True
            ))

        # ── Rule 3: IPS Warning ───────────────────────────────────────────────
        if ips < 2.0 and calculated_risk != "HIGH_RISK":
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
