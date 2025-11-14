#!/bin/bash
# Quick setup script for daily stock analysis cron job

echo "=========================================="
echo "Daily Stock Analyzer - Cron Setup"
echo "=========================================="
echo ""

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)

echo "Script directory: $SCRIPT_DIR"
echo "Python path: $PYTHON_PATH"
echo ""

# Check if config exists
if [ ! -f "$SCRIPT_DIR/daily_config.json" ]; then
    echo "Creating daily_config.json from example..."
    cp "$SCRIPT_DIR/daily_config.json.example" "$SCRIPT_DIR/daily_config.json"
    echo "✓ Config file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit daily_config.json with your settings:"
    echo "   - Set email_enabled to true if you want email reports"
    echo "   - Add your email credentials"
    echo "   - Adjust universe and max_stocks as needed"
    echo ""
    read -p "Press Enter to continue after editing config..."
fi

# Create daily_reports directory
mkdir -p "$SCRIPT_DIR/daily_reports"

# Test the script
echo "Testing daily runner..."
cd "$SCRIPT_DIR"
$PYTHON_PATH daily_runner.py --config daily_config.json &
TEST_PID=$!

echo "Test started (PID: $TEST_PID)"
echo "This will take 30-60 minutes for full S&P 500 analysis"
echo ""
echo "You can:"
echo "  1. Wait for it to complete"
echo "  2. Press Ctrl+C to cancel and continue with cron setup anyway"
echo "  3. Monitor in another terminal: tail -f $SCRIPT_DIR/daily_reports/daily_summary_*.txt"
echo ""

# Wait a bit to see if it starts successfully
sleep 5

if ps -p $TEST_PID > /dev/null; then
    echo "✓ Script is running successfully"
    echo ""
    read -p "Continue with cron setup? (it will run in background) [y/N]: " CONTINUE

    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        echo "Setup cancelled. Test is still running in background."
        echo "Check progress: tail -f daily_reports/daily_summary_*.txt"
        exit 0
    fi
else
    echo "✗ Script failed to start. Check your configuration."
    exit 1
fi

echo ""
echo "=========================================="
echo "Setting up Cron Job"
echo "=========================================="
echo ""

# Ask for time
echo "When should the analysis run?"
read -p "Hour (0-23, default 9 for 9am): " HOUR
HOUR=${HOUR:-9}

read -p "Minute (0-59, default 0): " MINUTE
MINUTE=${MINUTE:-0}

echo ""
echo "Run on which days?"
echo "  1) Every day"
echo "  2) Weekdays only (Mon-Fri)"
echo "  3) Custom"
read -p "Choice [1]: " DAY_CHOICE
DAY_CHOICE=${DAY_CHOICE:-1}

case $DAY_CHOICE in
    1)
        DAY_SPEC="* * *"
        DAY_DESC="every day"
        ;;
    2)
        DAY_SPEC="* * 1-5"
        DAY_DESC="weekdays only"
        ;;
    3)
        read -p "Enter day specification (e.g., '* * 1,3,5' for Mon/Wed/Fri): " CUSTOM_DAYS
        DAY_SPEC="$CUSTOM_DAYS"
        DAY_DESC="custom schedule"
        ;;
    *)
        echo "Invalid choice, using every day"
        DAY_SPEC="* * *"
        DAY_DESC="every day"
        ;;
esac

# Create cron entry
CRON_ENTRY="$MINUTE $HOUR $DAY_SPEC cd $SCRIPT_DIR && $PYTHON_PATH daily_runner.py >> daily_reports/cron.log 2>&1"

echo ""
echo "Cron entry to be added:"
echo "----------------------------------------"
echo "$CRON_ENTRY"
echo "----------------------------------------"
echo "This will run at $HOUR:$(printf "%02d" $MINUTE) $DAY_DESC"
echo ""

read -p "Add this cron job? [y/N]: " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Setup cancelled"
    exit 0
fi

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo ""
echo "✓ Cron job added successfully!"
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Your daily stock analysis will run:"
echo "  Time: $HOUR:$(printf "%02d" $MINUTE)"
echo "  Days: $DAY_DESC"
echo "  Output: $SCRIPT_DIR/daily_reports/"
echo ""
echo "Verify cron job:"
echo "  crontab -l"
echo ""
echo "View logs:"
echo "  tail -f $SCRIPT_DIR/daily_reports/cron.log"
echo ""
echo "Check results:"
echo "  ls -lt $SCRIPT_DIR/daily_reports/"
echo ""
echo "Remove cron job (if needed):"
echo "  crontab -e"
echo "  # Delete the line with 'daily_runner.py'"
echo ""
