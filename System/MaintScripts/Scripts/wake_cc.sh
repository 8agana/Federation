#!/bin/bash
# Wake script for CC - Updated for iTerm2
# Ported from Claude_Home to Federation

echo "🔔 Waking CC in iTerm2..."

MESSAGE="${1:-DT TEST WAKE MESSAGE - $(date)}"

# iTerm2 activation and message sending
osascript <<EOF
tell application "iTerm2"
    activate
    delay 0.5
    tell application "System Events"
        tell process "iTerm2"
            set frontmost to true
            delay 0.3
            keystroke "$MESSAGE"
            delay 0.1
            key code 36
        end tell
    end tell
end tell
EOF

echo "✅ Wake signal sent to iTerm2!"