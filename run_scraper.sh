#!/bin/bash
# سكريبت التحديث اليومي — Linux
# يمكن جدولته عبر cron: 0 2 * * * /path/to/run_scraper.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/log.txt"

echo "=============================" >> "$LOG_FILE"
echo "بدء التحديث: $(date)" >> "$LOG_FILE"

cd "$SCRIPT_DIR"

# جلب المنتجات من المتاجر
python3 scraper.py >> "$LOG_FILE" 2>&1
SCRAPER_EXIT=$?

if [ $SCRAPER_EXIT -ne 0 ]; then
    echo "خطأ في السكريبر (exit code: $SCRAPER_EXIT)" >> "$LOG_FILE"
fi

# تشغيل عميل المطابقة
python3 matcher.py >> "$LOG_FILE" 2>&1
MATCHER_EXIT=$?

if [ $MATCHER_EXIT -ne 0 ]; then
    echo "خطأ في عميل المطابقة (exit code: $MATCHER_EXIT)" >> "$LOG_FILE"
fi

# تشغيل عميل الذكاء الاصطناعي
python3 ai_agent.py >> "$LOG_FILE" 2>&1
AI_EXIT=$?

if [ $AI_EXIT -ne 0 ]; then
    echo "خطأ في عميل الذكاء الاصطناعي (exit code: $AI_EXIT)" >> "$LOG_FILE"
fi

echo "انتهى التحديث: $(date)" >> "$LOG_FILE"
echo "=============================" >> "$LOG_FILE"
