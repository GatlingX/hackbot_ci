#!/bin/bash

# Color definitions
BOLD_RED='\033[1;31m'
BOLD_GREEN='\033[1;32m'
BOLD_YELLOW='\033[1;33m'
RESET='\033[0m'

# Function to print error and exit
function error_exit() {
    echo -e "${BOLD_RED}❌ ERROR${RESET}: $1" >&2
    exit 1
}

# Function to print success
function success() {
    echo -e "${BOLD_GREEN}✅ SUCCESS${RESET}: $1"
}

# Function to print warning
function warning() {
    echo -e "${BOLD_YELLOW}⚠️ WARNING${RESET}: $1"
}

##########################################################
# Starting installation
##########################################################

# Step 1: Check if API key is provided
if [ -z "$1" ]; then
    error_exit "Please provide your Hackbot API key as an argument. Usage: ./install.sh <HACKBOT_API_KEY>"
fi

HACKBOT_API_KEY="$1"

# Step 2: Check if we're in a git repository for hackbot target
if [ ! -d .git ]; then
    error_exit "This script must be run from the root of a git repository that you want the hackbot to scan."
fi

# Step 3: Check for scope.txt file
if [ ! -f "scope.txt" ]; then
    error_exit "scope.txt file not found in the root directory. Please create a scope.txt file with your target Contract relative paths."
fi

# Step 4: Check if git is installed
if ! command -v git &> /dev/null; then
    error_exit "git is not installed. Please install git first"
fi

# Step 5: Extract repository information from git remote URL
REMOTE_URL=$(git remote get-url origin)
if [ $? -ne 0 ]; then
    error_exit "Failed to get git remote URL. Make sure you run this script in the root of your git repository you want the hackbot to scan your code."
fi

# Step 6: Parse GitHub repository information
if [[ $REMOTE_URL =~ github\.com[:/]([^/]+)/([^/]+)(\.git)?$ ]]; then
    GITHUB_ORG="${BASH_REMATCH[1]}"
    GITHUB_REPO="${BASH_REMATCH[2]%.git}"
else
    error_exit "Could not parse GitHub organization and repository from remote URL: $REMOTE_URL"
fi

# Step 7: Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    warning "GitHub CLI (gh) is not installed. Installing now..."
    
    # Install gh CLI based on OS
    if [[ "$(uname 2>/dev/null)" == "Darwin" ]]; then
        # macOS installation
        if command -v brew &> /dev/null; then
            brew install gh
        else
            error_exit "Homebrew is not installed. Please install Homebrew first: https://brew.sh"
        fi
    elif [[ "$(uname 2>/dev/null)" == "Linux" ]]; then
        # Linux installation
        if command -v apt-get &> /dev/null; then
            # Debian/Ubuntu
            curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
            sudo apt update
            sudo apt install gh
        elif command -v dnf &> /dev/null; then
            # Fedora/RHEL
            sudo dnf install 'dnf-command(config-manager)'
            sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
            sudo dnf install gh
        elif command -v pacman &> /dev/null; then
            # Arch Linux
            sudo pacman -S github-cli
        else
            error_exit "Unsupported Linux distribution. Please install GitHub CLI manually: https://cli.github.com/manual/installation"
        fi
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$(uname 2>/dev/null)" == *"MINGW"* ]]; then
        # Windows installation
        if command -v winget &> /dev/null; then
            # Using winget (Windows Package Manager)
            winget install --id GitHub.cli
        elif command -v choco &> /dev/null; then
            # Using Chocolatey
            choco install gh
        elif command -v scoop &> /dev/null; then
            # Using Scoop
            scoop install gh
        else
            warning "No package manager found. Installing using PowerShell..."
            # PowerShell installation
            powershell.exe -Command "Set-ExecutionPolicy RemoteSigned -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://github.com/cli/cli/releases/latest/download/install.ps1'))"
        fi
    else
        error_exit "Unsupported operating system. Please install GitHub CLI manually: https://cli.github.com/manual/installation"
    fi
fi

# Step 8: Verify gh CLI installation
if ! command -v gh &> /dev/null; then
    error_exit "Failed to install GitHub CLI"
fi

# Step 9: Check if logged in to GitHub CLI
if ! gh auth status &> /dev/null; then
    warning "Not logged in to GitHub CLI. Please login:"
    gh auth login
    if [ $? -ne 0 ]; then
        error_exit "Failed to login to GitHub CLI"
    fi
fi

# Step 10: Set HACKBOT_API_KEY as a GitHub secret
echo "Setting up HACKBOT_API_KEY as a GitHub secret..."
if ! gh secret set HACKBOT_API_KEY -b"$HACKBOT_API_KEY" -R "$GITHUB_ORG/$GITHUB_REPO"; then
    error_exit "Failed to set HACKBOT_API_KEY secret in GitHub repository"
fi

# Step 11: Create GitHub Actions workflow directory if it doesn't exist
WORKFLOW_DIR=".github/workflows"
mkdir -p "$WORKFLOW_DIR"

# Step 12: Check if workflow file already exists
WORKFLOW_FILE="$WORKFLOW_DIR/hackbot-scan.yaml"
if [ -f "$WORKFLOW_FILE" ]; then
    read -p "⚠️  Workflow file already exists. Do you want to overwrite it? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        warning "Skipping workflow file creation of $WORKFLOW_FILE. Using existing yaml file."
    else
        # Fetch and create the workflow file
        curl -s https://raw.githubusercontent.com/GatlingX/hackbot_ci/main/example.yaml > "$WORKFLOW_FILE"
        if [ $? -ne 0 ]; then
            error_exit "Failed to download workflow file template"
        fi
        success "Created GitHub Actions workflow file at $WORKFLOW_FILE"
    fi
else
    # Fetch and create the workflow file
    curl -s https://raw.githubusercontent.com/GatlingX/hackbot_ci/main/example.yaml > "$WORKFLOW_FILE"
    if [ $? -ne 0 ]; then
        error_exit "Failed to download workflow file template"
    fi
    success "Created GitHub Actions workflow file at $WORKFLOW_FILE"
fi

# Step 13: Stage the workflow file and inform about pushing
git add "$WORKFLOW_FILE"
if [ $? -ne 0 ]; then
    error_exit "Failed to stage workflow file"
fi
success "Staged workflow file for commit"
warning "Don't forget to commit and push the changes. Run the following commands:"
echo -e "  git commit -m \"Add Hackbot workflow\""
echo -e "  git push origin main"

success "Installed hackbot for repository: https://github.com/$GITHUB_ORG/$GITHUB_REPO"
