"""
scheduler.py — جدولة يدوية شهرية فقط (Admin Triggered)
--------------------------------------------------------
⚠️ تنبيه قانوني:
  - لا يوجد جدولة تلقائية يومية بعد الآن.
  - التحديث يتم مرّة واحدة بالشهر فقط، ويُشغَّل من قِبَل الأدمن يدوياً
    عبر لوحة التحكم بعد التحقق من كلمة سر الأدمن.
  - السكريبر نفسه (scraper.py) يفرض الحد الشهري عبر check_monthly_limit().
  - هذا يضمن الامتثال لأنظمة المتاجر، ويتفادى أي ادعاء بـ
    "automated daily scraping / server load abuse".
--------------------------------------------------------
"""
import logging
from datetime import datetime
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
LAST_RUN_FILE = BASE_DIR / "last_run.json"


def can_run_this_month() -> tuple[bool, str]:
    """يتحقق هل يجوز التشغيل هذا الشهر. يُعيد (مسموح, رسالة)."""
    now = datetime.now()
    current_month = f"{now.year}-{str(now.month).zfill(2)}"
    if LAST_RUN_FILE.exists():
        try:
            data = json.loads(LAST_RUN_FILE.read_text(encoding="utf-8"))
            if data.get("month") == current_month:
                return False, f"تم التشغيل بالفعل هذا الشهر بتاريخ {data.get('timestamp')}"
        except Exception:
            pass
    return True, "مسموح بالتشغيل"


def run_monthly_update() -> dict:
    """يشغّل التحديث الشهري الكامل: scraper → matcher → ai_agent.
    يُستدعى يدوياً فقط من لوحة الأدمن. يُعيد قاموس بالنتيجة.
    """
    result = {"ok": False, "scraper": None, "matcher": None, "ai": None, "msg": ""}

    allowed, msg = can_run_this_month()
    if not allowed:
        result["msg"] = msg
        logger.warning(f"[رفض] {msg}")
        return result

    logger.info("بدء التحديث الشهري (يدوي - admin) ...")

    try:
        from scraper import scrape_all
        scrape_all()
        result["scraper"] = "ok"
        logger.info("تم الانتهاء من جلب البيانات.")
    except Exception as e:
        result["scraper"] = f"error: {e}"
        logger.error(f"خطأ في السكريبر: {e}")

    try:
        from matcher import build_comparison_groups
        build_comparison_groups()
        result["matcher"] = "ok"
        logger.info("تم الانتهاء من المطابقة.")
    except Exception as e:
        result["matcher"] = f"error: {e}"
        logger.error(f"خطأ في المطابق: {e}")

    try:
        from ai_agent import run_ai_agent
        run_ai_agent()
        result["ai"] = "ok"
        logger.info("تم الانتهاء من توصيف الأعمال.")
    except Exception as e:
        result["ai"] = f"error: {e}"
        logger.error(f"خطأ في عميل الذكاء الاصطناعي: {e}")

    result["ok"] = result["scraper"] == "ok"
    result["msg"] = "تم التحديث الشهري بنجاح" if result["ok"] else "فشل التحديث الشهري"
    logger.info(result["msg"])
    return result


# ⚠️ تم إلغاء start_scheduler() القديم بشكل متعمد.
# لا يوجد تشغيل تلقائي يومي / أسبوعي / شهري.
# التحديث الوحيد المسموح: يدوي عبر run_monthly_update() من لوحة الأدمن.

if __name__ == "__main__":
    print("⚠️ هذا الملف لم يعد يدعم الجدولة التلقائية.")
    print("لتشغيل التحديث الشهري يدوياً (مرة واحدة بالشهر):")
    print("   python -c 'from scheduler import run_monthly_update; run_monthly_update()'")
    print("أو من لوحة Streamlit عبر زر 'تحديث شهري (Admin)'.")
