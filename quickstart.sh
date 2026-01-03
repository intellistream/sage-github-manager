#!/usr/bin/env bash

# SAGE GitHub Manager - Quick Start Installation Script
# This script helps you quickly set up sage-github-manager on your system

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main installation process
main() {
    print_header "SAGE GitHub Manager Quick Start"
    echo ""
    echo "This script will install sage-github-manager and set up your environment."
    echo ""

    # Step 1: Check prerequisites
    print_header "Step 1: Checking Prerequisites"

    # Check Python version
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
            print_success "Python $PYTHON_VERSION found (required: 3.10+)"
        else
            print_error "Python 3.10+ required, found $PYTHON_VERSION"
            echo "Please install Python 3.10 or higher: https://www.python.org/downloads/"
            exit 1
        fi
    else
        print_error "Python 3 not found"
        echo "Please install Python 3.10+: https://www.python.org/downloads/"
        exit 1
    fi

    # Check pip
    if command_exists pip3; then
        print_success "pip3 found"
    else
        print_error "pip3 not found"
        echo "Please install pip3: https://pip.pypa.io/en/stable/installation/"
        exit 1
    fi

    # Check git (optional but recommended)
    if command_exists git; then
        print_success "git found"
    else
        print_warning "git not found (optional, but recommended for updates)"
    fi

    echo ""

    # Step 2: Install package
    print_header "Step 2: Installing sage-github-manager"

    # Check if already in project directory
    if [ -f "pyproject.toml" ] && grep -q "sage-github" "pyproject.toml" 2>/dev/null; then
        print_info "Already in sage-github-manager directory"
        PROJECT_DIR="$(pwd)"
    else
        print_error "Not in sage-github-manager directory"
        echo "Please run this script from the project root directory:"
        echo "  cd /path/to/sage-github-manager"
        echo "  bash quickstart.sh"
        exit 1
    fi

    # Check if already in a virtual environment
    if [ -n "$VIRTUAL_ENV" ]; then
        print_success "Already in virtual environment: $(basename $VIRTUAL_ENV)"
    elif [ -n "$CONDA_DEFAULT_ENV" ]; then
        print_success "Already in conda environment: $CONDA_DEFAULT_ENV"
    else
        # Not in a virtual environment, ask if they want to create one
        read -p "$(echo -e ${YELLOW}Not in a virtual environment. Create a new venv? [Y/n]: ${NC})" CREATE_VENV
        CREATE_VENV=${CREATE_VENV:-Y}

        if [[ "$CREATE_VENV" =~ ^[Yy]$ ]]; then
            if [ -d "venv" ]; then
                print_info "Virtual environment already exists, using existing one"
            else
                print_info "Creating virtual environment..."
                python3 -m venv venv
                print_success "Virtual environment created"
            fi

            print_info "Activating virtual environment..."
            source venv/bin/activate
            print_success "Virtual environment activated"
        else
            print_warning "Installing without virtual environment (not recommended)"
        fi
    fi

    # Install package with dependencies
    print_info "Installing package and dependencies (this may take a minute)..."
    pip3 install -e ".[dev]" --quiet
    print_success "Package installed successfully"

    # Install pre-commit hooks
    if command_exists pre-commit; then
        print_info "Installing pre-commit hooks..."
        pre-commit install > /dev/null 2>&1
        print_success "Pre-commit hooks installed"
    else
        print_warning "pre-commit not found, skipping hooks installation"
    fi

    echo ""

    # Step 3: Configure environment
    print_header "Step 3: Configuring Environment"

    # Check for existing .env file
    if [ -f ".env" ]; then
        print_info ".env file already exists"
        read -p "$(echo -e ${YELLOW}Do you want to update it? [y/N]: ${NC})" UPDATE_ENV
        UPDATE_ENV=${UPDATE_ENV:-N}

        if [[ ! "$UPDATE_ENV" =~ ^[Yy]$ ]]; then
            print_info "Skipping .env configuration"
            SKIP_ENV=true
        fi
    fi

    if [ "$SKIP_ENV" != "true" ]; then
        print_info "Setting up GitHub configuration..."
        echo ""
        echo "You need a GitHub Personal Access Token (PAT) with 'repo' scope."
        echo "Create one at: https://github.com/settings/tokens/new"
        echo ""

        read -p "Enter your GitHub Token (or press Enter to skip): " GITHUB_TOKEN
        read -p "Enter GitHub Owner (default: intellistream): " GITHUB_OWNER
        GITHUB_OWNER=${GITHUB_OWNER:-intellistream}
        read -p "Enter GitHub Repo (default: SAGE): " GITHUB_REPO
        GITHUB_REPO=${GITHUB_REPO:-SAGE}

        # Create .env file
        cat > .env << EOF
# GitHub Configuration
GITHUB_TOKEN=${GITHUB_TOKEN}
GITHUB_OWNER=${GITHUB_OWNER}
GITHUB_REPO=${GITHUB_REPO}

# Optional: OpenAI API Key for AI features
# OPENAI_API_KEY=sk-...

# Optional: Anthropic API Key for Claude
# ANTHROPIC_API_KEY=sk-ant-...
EOF

        print_success ".env file created"

        if [ -z "$GITHUB_TOKEN" ]; then
            print_warning "No GitHub token provided. You'll need to set it later:"
            echo "  export GITHUB_TOKEN=your_token_here"
            echo "  or edit .env file"
        fi
    fi

    echo ""

    # Step 4: Verify installation
    print_header "Step 4: Verifying Installation"

    if command_exists github-manager; then
        print_success "github-manager command available"
        VERSION=$(github-manager --version 2>/dev/null || echo "unknown")
        print_info "Version: $VERSION"
    else
        print_error "github-manager command not found"
        echo "Try running: pip3 install -e '.[dev]'"
        exit 1
    fi

    # Test basic functionality
    if [ -n "$GITHUB_TOKEN" ]; then
        print_info "Testing GitHub connection..."
        export GITHUB_TOKEN
        export GITHUB_OWNER
        export GITHUB_REPO

        if github-manager download --help >/dev/null 2>&1; then
            print_success "Basic command test passed"
        else
            print_warning "Command test failed, but installation completed"
        fi
    fi

    echo ""

    # Step 5: Success message and next steps
    print_header "Installation Complete! 🎉"
    echo ""
    print_success "sage-github-manager is ready to use!"
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    QUICK START GUIDE                           ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    print_info "Configuration (Required):"
    echo ""

    # Show environment activation if needed
    if [[ "$CREATE_VENV" =~ ^[Yy]$ ]] && [ -z "$CONDA_DEFAULT_ENV" ]; then
        echo -e "  ${YELLOW}▶${NC} Activate virtual environment:"
        echo "    source venv/bin/activate"
        echo ""
    fi

    if [ -z "$GITHUB_TOKEN" ]; then
        echo -e "  ${YELLOW}▶${NC} Set your GitHub token:"
        echo "    export GITHUB_TOKEN=ghp_xxxxxxxxxxxxx"
        echo "    export GITHUB_OWNER=intellistream"
        echo "    export GITHUB_REPO=SAGE"
        echo ""
        echo -e "    ${BLUE}Or create .env file:${NC}"
        echo "    cat > .env << EOF"
        echo "GITHUB_TOKEN=ghp_xxxxxxxxxxxxx"
        echo "GITHUB_OWNER=intellistream"
        echo "GITHUB_REPO=SAGE"
        echo "EOF"
        echo ""
    fi

    print_info "Basic Commands:"
    echo ""
    echo -e "  ${GREEN}1.${NC} Download SAGE issues:"
    echo -e "     ${BLUE}github-manager download${NC}"
    echo ""
    echo -e "  ${GREEN}2.${NC} List open issues:"
    echo -e "     ${BLUE}github-manager list --state open${NC}"
    echo -e "     ${BLUE}github-manager list --label bug --assignee yourname${NC}"
    echo ""
    echo -e "  ${GREEN}3.${NC} View analytics:"
    echo -e "     ${BLUE}github-manager analytics${NC}"
    echo ""
    echo -e "  ${GREEN}4.${NC} Export data:"
    echo -e "     ${BLUE}github-manager export issues.csv${NC}"
    echo -e "     ${BLUE}github-manager export report.md -f markdown${NC}"
    echo ""
    echo -e "  ${GREEN}5.${NC} Batch operations:"
    echo -e "     ${BLUE}github-manager batch-close --label wontfix --dry-run${NC}"
    echo -e "     ${BLUE}github-manager batch-label --add reviewed --label bug${NC}"
    echo ""
    echo -e "  ${GREEN}6.${NC} AI features (requires API key):"
    echo -e "     ${BLUE}github-manager summarize --issue 123${NC}"
    echo -e "     ${BLUE}github-manager detect-duplicates${NC}"
    echo -e "     ${BLUE}github-manager suggest-labels --issue 456${NC}"
    echo ""

    print_info "Documentation:"
    echo "  - Quick Start: docs/QUICK_START.md"
    echo "  - FAQ: docs/FAQ.md"
    echo "  - Examples: examples/"
    echo ""

    print_info "Development:"
    echo "  - Run tests: pytest"
    echo "  - Format code: ruff format ."
    echo "  - Lint code: ruff check ."
    echo ""

    if [ -f ".env" ]; then
        print_warning "Remember: .env file contains sensitive data (not committed to git)"
    fi

    echo ""
    print_header "Happy Issue Managing! 🚀"
}

# Run main function
main "$@"
