#!/bin/bash
# Wake Desktop Claude by typing in their window
# Ported from Claude_Home to Federation

echo "🔔 Waking Desktop Claude..."

# Get message parameter or use default
MESSAGE="${1:-🔔 CC MESSAGE WAITING! Use dt_check_cc_messages() to see latest updates!}"

# Activate Claude app
osascript -e 'tell application "Claude" to activate'
sleep 0.5

# Type the wake signal with custom message
osascript -e "tell application \"System Events\" to keystroke \"$MESSAGE\""
sleep 0.2

# Hit Enter to send
osascript -e 'tell application "System Events" to key code 36'

echo "✅ Wake signal sent to Desktop Claude!"