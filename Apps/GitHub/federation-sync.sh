#!/bin/bash

# Federation Git Sync Script
# One-stop shop for saving, committing, and pushing Federation updates
# Created by CC for Sam

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Federation root directory
FEDERATION_ROOT="/Users/samuelatagana/Documents/Federation"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[Federation Sync]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

# Navigate to Federation directory
cd "$FEDERATION_ROOT" || { print_error "Failed to navigate to Federation directory"; exit 1; }

print_status "Starting Federation Git sync..."
echo ""

# Show current branch
BRANCH=$(git branch --show-current)
print_status "Current branch: ${GREEN}$BRANCH${NC}"
echo ""

# Show git status
print_status "Current status:"
git status --short
echo ""

# Check if there are changes to commit
if [ -z "$(git status --porcelain)" ]; then
    print_success "Everything is up to date! No changes to commit."
    exit 0
fi

# Stage all changes
print_status "Staging all changes..."
git add -A
print_success "All changes staged"
echo ""

# Show what's being committed
print_status "Changes to be committed:"
git diff --cached --stat
echo ""

# Get commit message from user
read -p "$(echo -e ${BLUE}Enter commit message:${NC} ) " commit_message

# If no message provided, use default
if [ -z "$commit_message" ]; then
    commit_message="Federation update $(date '+%Y-%m-%d %H:%M:%S')"
    print_warning "Using default message: $commit_message"
fi

# Create commit
print_status "Creating commit..."
git commit -m "$commit_message" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Commit created successfully"
else
    print_error "Failed to create commit"
    exit 1
fi
echo ""

# Push to remote
print_status "Pushing to GitHub..."
git push origin "$BRANCH" 2>&1 | grep -E "(up-to-date|->|Total|Writing|Counting)" | sed 's/^/  /'

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    print_success "Successfully pushed to GitHub!"
    echo ""
    
    # Show latest commit
    print_status "Latest commit:"
    git log -1 --oneline --decorate
else
    print_error "Failed to push to GitHub"
    print_warning "You may need to pull changes first with: git pull origin $BRANCH"
    exit 1
fi

echo ""
print_success "Federation sync complete!"