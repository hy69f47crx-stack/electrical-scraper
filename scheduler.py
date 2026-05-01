import logging
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

KUWAIT_TZ = pytz.timezone("Asia/Kuwait")


def run_daily_update():
    """يشغّل السكريبر، ثم عميل المطابقة، ثم عميل الذكاء الاصطناعي."""
    logger.info("بدء التحديث اليومي ...")

    try:
        from scraper import scrape_all
        scrape_all()
        logger.info("تم الانتهاء من جلب البيانات.")
    except Exception as e:
        logger.error(f"خطأ في السكريبر: {e}")

    try:
        from matcher import build_comparison_groups
        build_comparison_groups()
        logger.info("تم الانتهاء من المطابقة.")
    except Exception as e:
        logger.error(f"خطأ في المطابق: {e}")

    try:
        from ai_agent import run_ai_agent
        run_ai_agent()
        logger.info("تم الانتهاء من توصيف الأعمال بواسطة الذكاء الاصطناعي.")
    except Exception as e:
        logger.error(f"خطأ في عميل الذكاء الاصطناعي: {e}")

    logger.info("تم التحديث اليومي بنجاح.")


def start_scheduler() -> BackgroundScheduler:
    """يبدأ الجدول الزمني للتحديث اليومي الساعة 2 فجراً بتوقيت الكويت."""
    scheduler = BackgroundScheduler(timezone=KUWAIT_TZ)
    scheduler.add_job(
        run_daily_update,
        trigger="cron",
        hour=2,
        minute=0,
        id="daily_update",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("تم بدء الجدول الزمني — التحديث اليومي الساعة 2:00 صباحاً (توقيت الكويت).")
    return scheduler


if __name__ == "__main__":
    import time
    scheduler = start_scheduler()
    print("الجدول الزمني يعمل ... اضغط Ctrl+C للإيقاف.")
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("تم إيقاف الجدول الزمني.")
