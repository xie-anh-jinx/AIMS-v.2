"""
AIMS Telegram Bot — Main Entry Point
Bot dengan menu interaktif berbasis role: Mahasiswa, Dosen PA, Admin.
Gunakan: python -m apps.telegram_bot.bot
"""
import logging
import os
from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters, ContextTypes
)
from apps.telegram_bot.keyboards import (
    login_keyboard, student_main_menu, student_back,
    advisor_main_menu, advisor_back, admin_main_menu, admin_back,
    confirm_keyboard
)
from apps.telegram_bot.api_client import (
    login, get_students, get_student_records,
    get_admin_overview, get_agent_logs, trigger_agent_evaluation
)

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("AIMS_TG_Bot")

BOT_TOKEN = "8947130178:AAG8Kn3p-BwvN0AQdOz3qIq_h0AAyX68tHk"

# ConversationHandler states
AWAIT_USERNAME, AWAIT_PASSWORD = range(2)

# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def _get_session(context: ContextTypes.DEFAULT_TYPE) -> dict:
    return context.user_data.setdefault("session", {})

def _role(context: ContextTypes.DEFAULT_TYPE) -> str:
    return _get_session(context).get("role", "")

def _token(context: ContextTypes.DEFAULT_TYPE) -> str:
    return _get_session(context).get("token", "")

def _nim(context: ContextTypes.DEFAULT_TYPE) -> str:
    return _get_session(context).get("nim", "")

# ══════════════════════════════════════════════════════════════════
# /start — Welcome & Role Selector
# ══════════════════════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess = _get_session(context)
    if sess.get("token"):
        role = sess.get("role", "")
        name = sess.get("name", "Pengguna")
        await update.message.reply_text(
            f"👋 Selamat datang kembali, *{name}*!\nAnda login sebagai *{role}*.",
            parse_mode="Markdown",
            reply_markup=_get_menu(role)
        )
        return

    await update.message.reply_text(
        "🎓 *AIMS — Academic Intelligence Management System*\n\n"
        "Selamat datang! Pilih peran Anda untuk login:",
        parse_mode="Markdown",
        reply_markup=login_keyboard()
    )

def _get_menu(role: str):
    if role == "STUDENT":
        return student_main_menu()
    elif role == "ADVISOR":
        return advisor_main_menu()
    elif role == "ADMIN":
        return admin_main_menu()
    return login_keyboard()

# ══════════════════════════════════════════════════════════════════
# LOGIN CONVERSATION
# ══════════════════════════════════════════════════════════════════

async def role_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    role_map = {"role_student": "STUDENT", "role_advisor": "ADVISOR", "role_admin": "ADMIN"}
    context.user_data["pending_role"] = role_map.get(query.data, "STUDENT")
    await query.edit_message_text("📋 Masukkan *username* / NIM Anda:", parse_mode="Markdown")
    return AWAIT_USERNAME

async def got_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pending_username"] = update.message.text.strip()
    await update.message.reply_text("🔐 Masukkan *password* Anda:", parse_mode="Markdown")
    return AWAIT_PASSWORD

async def got_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.user_data.pop("pending_username", "")
    password = update.message.text.strip()

    await update.message.reply_text("⏳ Memverifikasi...")
    data = await login(username, password)

    if not data or "access_token" not in data:
        await update.message.reply_text(
            "❌ Login gagal. Username atau password salah.\n\nCoba lagi:",
            reply_markup=login_keyboard()
        )
        return ConversationHandler.END

    pending_role = context.user_data.pop("pending_role", "ANY")
    actual_role = data.get("role", "")
    if pending_role != "ANY" and actual_role != pending_role:
        await update.message.reply_text(
            f"🚫 Akun ini bukan *{pending_role}*.\nAnda login sebagai *{actual_role}*.",
            parse_mode="Markdown",
            reply_markup=login_keyboard()
        )
        return ConversationHandler.END

    # Save session
    sess = _get_session(context)
    sess["token"] = data["access_token"]
    sess["role"] = actual_role
    sess["user_id"] = data.get("user_id")
    sess["username"] = username
    sess["name"] = username

    # If student, fetch NIM
    if actual_role == "STUDENT":
        students = await get_students(data["access_token"])
        if students:
            sess["nim"] = students[0]["nim"]
            sess["name"] = students[0]["nama"]

    role_emoji = {"STUDENT": "🎓", "ADVISOR": "👨‍🏫", "ADMIN": "🛡️"}.get(actual_role, "👤")
    await update.message.reply_text(
        f"{role_emoji} *Login berhasil!*\n\n"
        f"Selamat datang, *{sess['name']}*\n"
        f"Peran: *{actual_role}*\n\n"
        f"Pilih menu di bawah:",
        parse_mode="Markdown",
        reply_markup=_get_menu(actual_role)
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Login dibatalkan.", reply_markup=login_keyboard())
    return ConversationHandler.END

# ══════════════════════════════════════════════════════════════════
# LOGOUT
# ══════════════════════════════════════════════════════════════════

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text(
        "🚪 Anda telah *logout*.\n\nSampai jumpa! 👋",
        parse_mode="Markdown",
        reply_markup=login_keyboard()
    )

# ══════════════════════════════════════════════════════════════════
# STUDENT HANDLERS
# ══════════════════════════════════════════════════════════════════

async def student_ipk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    nim = _nim(context)
    token = _token(context)
    if not nim:
        await query.edit_message_text("❌ NIM tidak ditemukan. Silakan login ulang.")
        return
    records = await get_student_records(nim, token)
    if not records:
        await query.edit_message_text("📂 Belum ada data akademik.", reply_markup=student_back())
        return
    latest = records[0]
    status_icon = {"Aman": "✅", "Warning": "⚠️", "HIGH_RISK": "🚨"}.get(latest.get("status"), "📊")
    text = (
        f"📊 *Data Akademik Terkini*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎓 NIM: `{nim}`\n"
        f"📅 Semester: *{latest.get('semester')}*\n\n"
        f"📈 IPK: *{latest.get('ipk', 0):.2f}*\n"
        f"📉 IPS: *{latest.get('ips', 0):.2f}*\n"
        f"📚 Total SKS: *{latest.get('sks', 0)}* / 144\n\n"
        f"{status_icon} Status: *{latest.get('status')}*"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=student_back())

async def student_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    nim = _nim(context)
    token = _token(context)
    records = await get_student_records(nim, token)
    if not records:
        await query.edit_message_text("📂 Belum ada riwayat nilai.", reply_markup=student_back())
        return
    lines = ["📚 *Riwayat Akademik*\n━━━━━━━━━━━━━━━━━━━━"]
    for r in sorted(records, key=lambda x: x.get("semester", 0)):
        icon = "✅" if r.get("status") == "Aman" else "⚠️" if r.get("status") == "Warning" else "🚨"
        lines.append(
            f"{icon} Sem {r.get('semester')}: IPK *{r.get('ipk', 0):.2f}* | IPS *{r.get('ips', 0):.2f}* | SKS *{r.get('sks')}*"
        )
    await query.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=student_back())

async def student_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    nim = _nim(context)
    token = _token(context)
    records = await get_student_records(nim, token)
    if not records:
        await query.edit_message_text("📂 Belum ada data.", reply_markup=student_back())
        return
    latest = records[0]
    sks = latest.get("sks", 0)
    target = 144
    pct = min(100, int(sks / target * 100))
    bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
    text = (
        f"🎯 *Progress Kelulusan*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📚 SKS Tempuh: *{sks}* / {target}\n"
        f"📊 Progress: [{bar}] *{pct}%*\n\n"
        f"{'✅ Sudah mencapai target SKS!' if sks >= target else f'📌 Sisa: *{target - sks} SKS* lagi'}"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=student_back())

async def student_notif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    nim = _nim(context)
    token = _token(context)
    records = await get_student_records(nim, token)
    notifs = []
    if records:
        latest = records[0]
        if latest.get("status") == "HIGH_RISK":
            notifs.append("🚨 *PERINGATAN*: IPK Anda berisiko DO. Segera konsultasi dengan Dosen PA!")
        elif latest.get("status") == "Warning":
            notifs.append("⚠️ IPK Anda perlu perhatian. Tingkatkan prestasi di semester ini.")
        if latest.get("ipk", 4) < 2.0:
            notifs.append("📉 IPK di bawah standar minimum (2.00).")
    notifs.append("📅 Pastikan pengisian KRS sebelum tenggat waktu.")
    text = "🔔 *Notifikasi & Peringatan*\n━━━━━━━━━━━━━━━━━━━━\n" + "\n\n".join(notifs)
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=student_back())

async def student_contact_advisor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📞 *Hubungi Dosen PA*\n━━━━━━━━━━━━━━━━━━━━\n"
        "Silakan kirim permintaan konsultasi melalui portal akademik atau hubungi langsung:\n\n"
        "🏛️ Gedung Akademik Lt. 2\n"
        "📧 advisor@kampus.ac.id\n"
        "🕐 Jam kerja: Senin–Jumat, 08.00–16.00"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=student_back())

async def student_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    name = _get_session(context).get("name", "Mahasiswa")
    await query.edit_message_text(
        f"🎓 *Dashboard Mahasiswa*\nHalo, *{name}*! Pilih menu:", 
        parse_mode="Markdown", reply_markup=student_main_menu()
    )

# ══════════════════════════════════════════════════════════════════
# ADVISOR HANDLERS
# ══════════════════════════════════════════════════════════════════

async def advisor_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    token = _token(context)
    students = await get_students(token)
    if not students:
        await query.edit_message_text("📂 Tidak ada data mahasiswa.", reply_markup=advisor_back())
        return
    lines = [f"👥 *Mahasiswa Bimbingan* ({len(students)} orang)\n━━━━━━━━━━━━━━━━━━━━"]
    for s in students[:10]:
        icon = "✅" if s.get("status") == "Aktif" else "⏸️"
        lines.append(f"{icon} `{s['nim']}` — *{s['nama']}* (Sem {s['semester']})")
    if len(students) > 10:
        lines.append(f"_...dan {len(students) - 10} mahasiswa lainnya_")
    await query.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=advisor_back())

async def advisor_risky(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    token = _token(context)
    students = await get_students(token)
    risky = []
    for s in students:
        recs = await get_student_records(s["nim"], token)
        if recs and recs[0].get("status") in ["HIGH_RISK", "Warning"]:
            risky.append((s, recs[0]))

    if not risky:
        text = "✅ *Tidak ada mahasiswa berisiko saat ini.*\nSemua dalam status Aman."
    else:
        lines = [f"🚨 *Mahasiswa Berisiko* ({len(risky)} orang)\n━━━━━━━━━━━━━━━━━━━━"]
        for s, rec in risky:
            icon = "🚨" if rec.get("status") == "HIGH_RISK" else "⚠️"
            lines.append(
                f"{icon} *{s['nama']}* (`{s['nim']}`)\n"
                f"   IPK: *{rec.get('ipk', 0):.2f}* | Sem: *{s['semester']}* | Status: _{rec.get('status')}_"
            )
        text = "\n\n".join(lines)
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=advisor_back())

async def advisor_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    token = _token(context)
    students = await get_students(token)
    aktif = sum(1 for s in students if s.get("status") == "Aktif")
    text = (
        f"📊 *Statistik Bimbingan*\n━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total Mahasiswa: *{len(students)}*\n"
        f"✅ Aktif: *{aktif}*\n"
        f"⏸️ Non-Aktif: *{len(students) - aktif}*"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=advisor_back())

async def advisor_do_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    token = _token(context)
    students = await get_students(token)
    do_risk = []
    for s in students:
        recs = await get_student_records(s["nim"], token)
        if recs and recs[0].get("status") == "HIGH_RISK":
            do_risk.append((s, recs[0]))
    if not do_risk:
        text = "✅ Tidak ada mahasiswa dalam kategori HIGH RISK D.O."
    else:
        lines = ["⛔ *Mahasiswa HIGH RISK D.O.*\n━━━━━━━━━━━━━━━━━━━━"]
        for s, rec in do_risk:
            lines.append(
                f"⛔ *{s['nama']}*\n"
                f"   NIM: `{s['nim']}` | Semester: *{s['semester']}*\n"
                f"   IPK: *{rec.get('ipk', 0):.2f}* | SKS: *{rec.get('sks')}*"
            )
        text = "\n\n".join(lines)
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=advisor_back())

async def advisor_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    name = _get_session(context).get("name", "Dosen PA")
    await query.edit_message_text(
        f"👨‍🏫 *Dashboard Dosen PA*\nHalo, *{name}*! Pilih menu:",
        parse_mode="Markdown", reply_markup=advisor_main_menu()
    )

# ══════════════════════════════════════════════════════════════════
# ADMIN HANDLERS
# ══════════════════════════════════════════════════════════════════

async def admin_overview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    token = _token(context)
    ov = await get_admin_overview(token)
    text = (
        f"📊 *Overview Sistem AIMS*\n━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total Mahasiswa: *{ov.get('total_students', '—')}*\n"
        f"✅ Aktif: *{ov.get('total_active_students', '—')}*\n"
        f"🚨 Risiko D.O.: *{ov.get('high_risk_students', '—')}*\n"
        f"📩 Reminder Terkirim: *{ov.get('total_reminders_sent', '—')}*"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_back())

async def admin_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    token = _token(context)
    students = await get_students(token)
    lines = [f"👥 *Semua Mahasiswa* ({len(students)} terdaftar)\n━━━━━━━━━━━━━━━━━━━━"]
    for s in students[:15]:
        icon = "✅" if s.get("status") == "Aktif" else "⏸️"
        lines.append(f"{icon} `{s['nim']}` {s['nama']} — Sem {s['semester']}")
    if len(students) > 15:
        lines.append(f"_...dan {len(students)-15} lainnya. Lihat selengkapnya di portal._")
    await query.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=admin_back())

async def admin_trigger_agent_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🤖 *Jalankan Evaluasi Agent?*\n\n"
        "Agent akan mengevaluasi semua mahasiswa aktif dan mengirimkan notifikasi jika ditemukan risiko.",
        parse_mode="Markdown",
        reply_markup=confirm_keyboard("agent")
    )

async def admin_trigger_agent_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⏳ Menjalankan evaluasi agent...")
    token = _token(context)
    success = await trigger_agent_evaluation(token)
    if success:
        text = "✅ *Agent berhasil dijalankan!*\nEvaluasi berjalan di background. Cek Agent Logs untuk hasilnya."
    else:
        text = "❌ Gagal menjalankan agent. Pastikan backend aktif."
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_back())

async def admin_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    token = _token(context)
    logs = await get_agent_logs(token, limit=8)
    if not logs:
        await query.edit_message_text("📋 Belum ada activity log.", reply_markup=admin_back())
        return
    lines = ["📋 *Agent Activity Logs* (8 terbaru)\n━━━━━━━━━━━━━━━━━━━━"]
    for lg in logs:
        icon = "✅" if lg.get("status") == "SUCCESS" else "❌"
        lines.append(f"{icon} `{lg.get('event_type')}` → {lg.get('action')}\n   _{lg.get('message', '')[:60]}_")
    await query.edit_message_text("\n\n".join(lines), parse_mode="Markdown", reply_markup=admin_back())

async def admin_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    token = _token(context)
    ov = await get_admin_overview(token)
    students = await get_students(token)
    do_count = ov.get("high_risk_students", "—")
    text = (
        f"🚨 *Analisis Risiko D.O.*\n━━━━━━━━━━━━━━━━━━━━\n"
        f"⛔ Mahasiswa HIGH RISK: *{do_count}*\n"
        f"📊 Total Mahasiswa: *{len(students)}*\n\n"
        f"💡 Jalankan Agent Evaluation untuk memperbarui status risiko."
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_back())

async def admin_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "⚙️ *Status Sistem AIMS*\n━━━━━━━━━━━━━━━━━━━━\n"
        "🟢 Backend API: *Online* (port 8000)\n"
        "🟢 Database: *Connected* (PostgreSQL)\n"
        "🟢 Telegram Bot: *Active* (@AIMS_FIB_bot)\n"
        "🟡 WhatsApp: Menunggu scan QR\n"
        "🟢 Agent Engine: *Standby*\n"
        "🟢 Scheduler: *Running*"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_back())

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🛡️ *Dashboard Administrator*\nPilih menu:",
        parse_mode="Markdown", reply_markup=admin_main_menu()
    )

# ══════════════════════════════════════════════════════════════════
# REFRESH (per-role)
# ══════════════════════════════════════════════════════════════════

async def handle_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🔄 Data diperbarui!")
    role = _role(context)
    name = _get_session(context).get("name", "Pengguna")
    ts = "Data diperbarui ✓"
    menus = {"STUDENT": student_main_menu, "ADVISOR": advisor_main_menu, "ADMIN": admin_main_menu}
    menu_fn = menus.get(role, login_keyboard)
    await query.edit_message_text(
        f"🔄 *{ts}*\n\nHalo, *{name}*! Pilih menu:",
        parse_mode="Markdown",
        reply_markup=menu_fn()
    )

# ══════════════════════════════════════════════════════════════════
# /help
# ══════════════════════════════════════════════════════════════════

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Perintah yang Tersedia*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "/start — Mulai & Login\n"
        "/menu — Tampilkan menu utama\n"
        "/logout — Keluar dari akun\n"
        "/help — Bantuan",
        parse_mode="Markdown"
    )

async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess = _get_session(context)
    role = sess.get("role", "")
    name = sess.get("name", "Pengguna")
    if not role:
        await update.message.reply_text("❌ Belum login.", reply_markup=login_keyboard())
        return
    await update.message.reply_text(
        f"📋 Menu *{role}* — {name}:", parse_mode="Markdown", reply_markup=_get_menu(role)
    )

async def logout_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("🚪 Logout berhasil. Sampai jumpa! 👋", reply_markup=login_keyboard())

# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Login conversation
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(role_selected, pattern="^role_")],
        states={
            AWAIT_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_username)],
            AWAIT_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(CommandHandler("logout", logout_cmd))

    # Login flow
    app.add_handler(conv)

    # Logout button
    app.add_handler(CallbackQueryHandler(logout, pattern="^logout$"))

    # Student callbacks
    app.add_handler(CallbackQueryHandler(student_ipk, pattern="^s_ipk$"))
    app.add_handler(CallbackQueryHandler(student_history, pattern="^s_history$"))
    app.add_handler(CallbackQueryHandler(student_progress, pattern="^s_progress$"))
    app.add_handler(CallbackQueryHandler(student_notif, pattern="^s_notif$"))
    app.add_handler(CallbackQueryHandler(student_contact_advisor, pattern="^s_contact_advisor$"))
    app.add_handler(CallbackQueryHandler(student_menu, pattern="^s_menu$"))

    # Advisor callbacks
    app.add_handler(CallbackQueryHandler(advisor_students, pattern="^a_students$"))
    app.add_handler(CallbackQueryHandler(advisor_risky, pattern="^a_risky$"))
    app.add_handler(CallbackQueryHandler(advisor_stats, pattern="^a_stats$"))
    app.add_handler(CallbackQueryHandler(advisor_do_risk, pattern="^a_do_risk$"))
    app.add_handler(CallbackQueryHandler(advisor_menu, pattern="^a_menu$"))

    # Admin callbacks
    app.add_handler(CallbackQueryHandler(admin_overview, pattern="^ad_overview$"))
    app.add_handler(CallbackQueryHandler(admin_students, pattern="^ad_students$"))
    app.add_handler(CallbackQueryHandler(admin_trigger_agent_confirm, pattern="^ad_trigger_agent$"))
    app.add_handler(CallbackQueryHandler(admin_trigger_agent_execute, pattern="^confirm_agent$"))
    app.add_handler(CallbackQueryHandler(admin_logs, pattern="^ad_logs$"))
    app.add_handler(CallbackQueryHandler(admin_risk, pattern="^ad_risk$"))
    app.add_handler(CallbackQueryHandler(admin_status, pattern="^ad_status$"))
    app.add_handler(CallbackQueryHandler(admin_menu, pattern="^ad_menu$"))

    # Refresh (all roles)
    app.add_handler(CallbackQueryHandler(handle_refresh, pattern="^(s|a|ad)_refresh$"))

    logger.info("🎓 AIMS Telegram Bot dimulai...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
