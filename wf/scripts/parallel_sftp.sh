#!/bin/bash

# Default configuration
MAX_PARALLEL=8
HOST="usftp23.novogene.com"
PORT="3022"
USER="user"
PASS="password"
REMOTE_PATH="/"
LOCAL_PATH="."

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -u, --user USER       SFTP username"
    echo "  -p, --pass PASS       SFTP password"
    echo "  -h, --host HOST       SFTP host (default: $HOST)"
    echo "  -P, --port PORT       SFTP port (default: $PORT)"
    echo "  -j, --jobs JOBS       Maximum parallel downloads (default: $MAX_PARALLEL)"
    echo "  -r, --remote PATH     Remote path (default: $REMOTE_PATH)"
    echo "  -l, --local PATH      Local path (default: $LOCAL_PATH)"
    echo "  --help               Show this help message"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--user)
            USER="$2"
            shift 2
            ;;
        -p|--pass)
            PASS="$2"
            shift 2
            ;;
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -P|--port)
            PORT="$2"
            shift 2
            ;;
        -j|--jobs)
            MAX_PARALLEL="$2"
            shift 2
            ;;
        -r|--remote)
            REMOTE_PATH="$2"
            shift 2
            ;;
        -l|--local)
            LOCAL_PATH="$2"
            shift 2
            ;;
        --help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

# Validate required parameters
if [ -z "$USER" ] || [ -z "$PASS" ]; then
    echo "Error: Username and password are required"
    show_help
fi
# this works: sshpass -p sj3carka sftp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r -P 3022 X202SC24122716-Z01-F010@usftp23.novogene.com:01.RawData ./

# SFTP options to disable host key checking
SFTP_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

# Create temporary file for process tracking
temp_file=$(mktemp)
trap 'rm -f $temp_file' EXIT

# Function to download a single file
download_file() {
    local file="$1"
    sshpass -p "$PASS" sftp $SFTP_OPTS -P "$PORT" "$USER@$HOST:$file" "$LOCAL_PATH/" 2>> "$temp_file"
    echo "$?" >> "$temp_file"
}

# Function to download a directory recursively
download_dirs() {
    local file="$1"
    local dire="$2"
    echo "d_d: $file to $dire"
    sshpass -p "$PASS" sftp $SFTP_OPTS -r -P "$PORT" "$USER@$HOST:$file" "$LOCAL_PATH/$dire" 2>> "$temp_file"
    echo "$?" >> "$temp_file"
}

# Get list of files
files=$(sshpass -p "$PASS" sftp $SFTP_OPTS -P "$PORT" "$USER@$HOST:$REMOTE_PATH" <<< "ls -1" | grep -v '^sftp>' | awk '{print $NF}')

# Get list of directories
directories=$(sshpass -p "$PASS" sftp $SFTP_OPTS -P "$PORT" "$USER@$HOST:$REMOTE_PATH" <<< "ls -la" | grep -v '^sftp>' | grep 'drw' | grep -v 'Undetermined' | awk '{print $NF}' | grep -v '^\.')
echo "Directories found: $directories"

# Download files in parallel with controlled concurrency
active_jobs=0
for direct in $directories; do
    # Wait if we've reached max parallel jobs
    while [ $active_jobs -ge $MAX_PARALLEL ]; do
        active_jobs=$(jobs -p | wc -l)
        sleep 1
    done
    
    # Start new download in background
    download_dirs "$REMOTE_PATH/$direct" "$direct" &
    
    # Update active job count
    active_jobs=$(jobs -p | wc -l)
    echo "Starting download of $direct (Active jobs: $active_jobs)"
done

# Wait for all downloads to complete
wait

# Check for errors
if grep -q "^[1-9]" "$temp_file"; then
    echo "Some downloads failed. Check $temp_file for details."
    exit 1
else
    echo "All downloads completed successfully!"
    exit 0
fi
