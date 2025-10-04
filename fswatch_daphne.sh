#!/bin/bash

# Daphne Auto-Reloader using fswatch (macOS)
# Watches for file changes and automatically restarts Daphne server

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DAPHNE_CMD="daphne dkp.asgi:application --port 8000 --bind 127.0.0.1 --verbosity 2"
WATCH_DIR="./dkp"
PID_FILE="/tmp/daphne.pid"

# Patterns to ignore
IGNORE_PATTERNS=(
    ".*\.pyc$"
    ".*__pycache__.*"
    ".*\.git.*"
    ".*\.idea.*"
    ".*\.log$"
    ".*\.sqlite3$"
    ".*staticfiles.*"
    ".*media.*"
    ".*node_modules.*"
    ".*\.DS_Store$"
    ".*\.swp$"
    ".*\.swo$"
    ".*~$"
)

# Build fswatch exclude arguments
EXCLUDE_ARGS=""
for pattern in "${IGNORE_PATTERNS[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude '$pattern'"
done

# Function to start Daphne
start_daphne() {
    echo -e "${GREEN}🚀 Starting Daphne...${NC}"
    cd dkp && $DAPHNE_CMD &
    DAPHNE_PID=$!
    echo $DAPHNE_PID > $PID_FILE
    echo -e "${GREEN}✅ Daphne started with PID: $DAPHNE_PID${NC}"
}

# Function to stop Daphne
stop_daphne() {
    if [ -f $PID_FILE ]; then
        DAPHNE_PID=$(cat $PID_FILE)
        if ps -p $DAPHNE_PID > /dev/null; then
            echo -e "${YELLOW}🛑 Stopping Daphne (PID: $DAPHNE_PID)...${NC}"
            kill -TERM $DAPHNE_PID 2>/dev/null

            # Wait for graceful shutdown (max 5 seconds)
            for i in {1..5}; do
                if ! ps -p $DAPHNE_PID > /dev/null; then
                    echo -e "${GREEN}✅ Daphne stopped gracefully${NC}"
                    rm -f $PID_FILE
                    return
                fi
                sleep 1
            done

            # Force kill if still running
            kill -KILL $DAPHNE_PID 2>/dev/null
            echo -e "${YELLOW}⚠️ Daphne force stopped${NC}"
        fi
        rm -f $PID_FILE
    fi
}

# Function to restart Daphne
restart_daphne() {
    echo -e "${BLUE}🔄 Restarting Daphne...${NC}"
    stop_daphne
    sleep 0.5
    start_daphne
}

# Function to handle file changes
handle_change() {
    local file=$1

    # Check if it's a relevant file type
    if [[ $file == *.py ]] || [[ $file == *.html ]] || [[ $file == *.css ]] || [[ $file == *.js ]] || [[ $file == *.json ]]; then
        echo -e "${YELLOW}🔄 Detected change in: $file${NC}"
        restart_daphne
    fi
}

# Cleanup on exit
cleanup() {
    echo -e "\n${RED}🛑 Shutting down...${NC}"
    stop_daphne
    echo -e "${GREEN}👋 Goodbye!${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if fswatch is installed
if ! command -v fswatch &> /dev/null; then
    echo -e "${RED}❌ fswatch is not installed!${NC}"
    echo "Please install it with: brew install fswatch"
    exit 1
fi

# Start Daphne initially
start_daphne

# Start watching for changes
echo -e "${BLUE}👀 Watching for file changes in $WATCH_DIR${NC}"
echo -e "${BLUE}Press Ctrl+C to stop${NC}\n"

# Use fswatch to monitor file changes
fswatch -r -0 \
    --event Created \
    --event Updated \
    --event Removed \
    --event Renamed \
    --event MovedFrom \
    --event MovedTo \
    --exclude "\.pyc$" \
    --exclude "__pycache__" \
    --exclude "\.git" \
    --exclude "\.idea" \
    --exclude "\.log$" \
    --exclude "\.sqlite3$" \
    --exclude "staticfiles" \
    --exclude "media" \
    --exclude "node_modules" \
    --exclude "\.DS_Store$" \
    --exclude "\.swp$" \
    --exclude "\.swo$" \
    --exclude "~$" \
    $WATCH_DIR | while read -d "" file; do
    handle_change "$file"
done