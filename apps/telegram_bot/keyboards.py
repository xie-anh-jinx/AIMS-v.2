"""
AIMS Telegram Bot — Keyboards (InlineKeyboardMarkup)
Menu disesuaikan dengan role masing-masing pengguna.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ────────────────────────── LOGIN KEYBOARD ──────────────────────────
def login_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎓 Login Mahasiswa", callback_data="role_student")],
        [InlineKeyboardButton("👨‍🏫 Login Dosen PA", callback_data="role_advisor")],
        [InlineKeyboardButton("🛡️ Login Admin", callback_data="role_admin")],
    ])

# ────────────────────────── STUDENT MENU ────────────────────────────
def student_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 IPK & IPS Terkini", callback_data="s_ipk"),
         InlineKeyboardButton("📚 Riwayat Nilai", callback_data="s_history")],
        [InlineKeyboardButton("📈 Grafik Perkembangan", callback_data="s_chart"),
         InlineKeyboardButton("🎯 Progress Kelulusan", callback_data="s_progress")],
        [InlineKeyboardButton("🔔 Notifikasi & Peringatan", callback_data="s_notif")],
        [InlineKeyboardButton("📞 Hubungi Dosen PA", callback_data="s_contact_advisor")],
        [InlineKeyboardButton("🔄 Refresh Data", callback_data="s_refresh"),
         InlineKeyboardButton("🚪 Logout", callback_data="logout")],
    ])

def student_back() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="s_menu")]
    ])

# ────────────────────────── ADVISOR MENU ────────────────────────────
def advisor_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Mahasiswa Bimbingan", callback_data="a_students"),
         InlineKeyboardButton("🚨 Mahasiswa Berisiko", callback_data="a_risky")],
        [InlineKeyboardButton("📊 Statistik Bimbingan", callback_data="a_stats"),
         InlineKeyboardButton("📋 Laporan IPK", callback_data="a_report")],
        [InlineKeyboardButton("⚠️ High Risk DO", callback_data="a_do_risk")],
        [InlineKeyboardButton("📢 Broadcast Pesan", callback_data="a_broadcast")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="a_refresh"),
         InlineKeyboardButton("🚪 Logout", callback_data="logout")],
    ])

def advisor_back() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="a_menu")]
    ])

# ────────────────────────── ADMIN MENU ──────────────────────────────
def admin_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Overview Sistem", callback_data="ad_overview"),
         InlineKeyboardButton("👥 Data Mahasiswa", callback_data="ad_students")],
        [InlineKeyboardButton("🤖 Jalankan Agent", callback_data="ad_trigger_agent"),
         InlineKeyboardButton("📋 Agent Logs", callback_data="ad_logs")],
        [InlineKeyboardButton("🚨 Risiko D.O.", callback_data="ad_risk"),
         InlineKeyboardButton("📩 Notif Massal", callback_data="ad_broadcast")],
        [InlineKeyboardButton("⚙️ Status Sistem", callback_data="ad_status")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="ad_refresh"),
         InlineKeyboardButton("🚪 Logout", callback_data="logout")],
    ])

def admin_back() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="ad_menu")]
    ])

def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Ya, Jalankan", callback_data=f"confirm_{action}"),
         InlineKeyboardButton("❌ Batal", callback_data="ad_menu")],
    ])
