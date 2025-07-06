#!/bin/bash

# setup_timezone.sh - Auto-detect and configure timezone for POP API

echo "🕐 Detecting system timezone..."

# Detect timezone based on the operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    DETECTED_TZ=$(readlink /etc/localtime | sed 's|.*/zoneinfo/||')
    echo "📍 Detected macOS timezone: $DETECTED_TZ"
elif [[ -f /etc/timezone ]]; then
    # Linux with /etc/timezone
    DETECTED_TZ=$(cat /etc/timezone)
    echo "📍 Detected Linux timezone: $DETECTED_TZ"
elif [[ -f /etc/localtime ]]; then
    # Linux with symlink
    DETECTED_TZ=$(readlink /etc/localtime | sed 's|.*/zoneinfo/||')
    echo "📍 Detected Linux timezone: $DETECTED_TZ"
else
    # Fallback
    DETECTED_TZ="UTC"
    echo "⚠️  Could not detect timezone, using UTC"
fi

# Calculate timezone offset
if command -v python3 &> /dev/null; then
    TZ_OFFSET=$(python3 -c "
import time
import datetime
now = datetime.datetime.now()
utc_now = datetime.datetime.utcnow()
offset = now - utc_now
total_seconds = int(offset.total_seconds())
hours = total_seconds // 3600
minutes = (abs(total_seconds) % 3600) // 60
print(f'{hours:+03d}{minutes:02d}')
")
    echo "📊 Calculated timezone offset: $TZ_OFFSET"
else
    TZ_OFFSET="+0000"
    echo "⚠️  Python3 not found, using +0000 offset"
fi

# Export environment variables
export TZ="$DETECTED_TZ"
export TZ_OFFSET="$TZ_OFFSET"

echo "✅ Timezone configuration:"
echo "   TZ=$TZ"
echo "   TZ_OFFSET=$TZ_OFFSET"

# Update .env file if it exists
if [[ -f .env ]]; then
    echo "📝 Updating .env file with timezone settings..."
    
    # Remove existing timezone settings
    sed -i.bak '/^TZ=/d' .env 2>/dev/null || true
    sed -i.bak '/^TZ_OFFSET=/d' .env 2>/dev/null || true
    
    # Add new timezone settings
    echo "" >> .env
    echo "# Auto-detected timezone settings" >> .env
    echo "TZ=$TZ" >> .env
    echo "TZ_OFFSET=$TZ_OFFSET" >> .env
    
    echo "✅ Updated .env with timezone settings"
fi

echo "🚀 Ready to start Docker containers with correct timezone!"
echo "   Run: docker-compose up -d"
