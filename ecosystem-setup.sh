#!/bin/bash

################################################################################
# Antigravity Ecosystem Setup
# Clones/links sister repositories into the ecosystem/ directory so
# Antigravitys can act as the central orchestrator for the full AI stack.
#
# Repos bootstrapped:
#   oh-my-opencode  – Sisyphus agent harness
#   opencode        – Core agent engine
#   openclaw        – Personal AI assistant / message-routing gateway
#   swarm-tools     – Multi-agent coordination utilities
#
# Usage:
#   ./ecosystem-setup.sh              # clone all repos
#   ./ecosystem-setup.sh --update     # git pull in every existing repo
#   ./ecosystem-setup.sh --link <dir> # symlink a local checkout instead
################################################################################

set -euo pipefail

# ── colours ────────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ECOSYSTEM_DIR="$SCRIPT_DIR/ecosystem"

print_status()  { echo -e "${BLUE}[*]${NC} $1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error()   { echo -e "${RED}[✗]${NC} $1"; }

# ── ecosystem repo definitions ─────────────────────────────────────────────────
# Format: "local_dirname|github_org/repo|description"
ECOSYSTEM_REPOS=(
    "oh-my-opencode|AloSantana/oh-my-opencode|Sisyphus agent harness"
    "opencode|AloSantana/opencode|Core OpenCode agent engine"
    "openclaw|AloSantana/openclaw|Personal AI assistant / message-routing gateway"
    "swarm-tools|AloSantana/swarm-tools|Multi-agent coordination utilities"
)

# ── helpers ────────────────────────────────────────────────────────────────────
check_git() {
    if ! command -v git &>/dev/null; then
        print_error "git is not installed. Please install git and try again."
        exit 1
    fi
}

clone_or_update_repo() {
    local dir_name="$1"
    local gh_repo="$2"
    local description="$3"
    local target="$ECOSYSTEM_DIR/$dir_name"
    local url="https://github.com/${gh_repo}.git"

    if [ -L "$target" ]; then
        print_warning "$dir_name is a symlink – skipping (use --update to pull inside symlinked repos)"
        return 0
    fi

    if [ -d "$target/.git" ]; then
        if [ "${UPDATE_MODE:-false}" = "true" ]; then
            print_status "Updating $dir_name ($description)…"
            git -C "$target" pull --ff-only 2>/dev/null || \
                print_warning "Could not fast-forward $dir_name – run 'git pull' manually"
            print_success "$dir_name updated"
        else
            print_success "$dir_name already present – skipping (use --update to refresh)"
        fi
    else
        print_status "Cloning $dir_name ($description)…"
        if git clone --depth 1 "$url" "$target"; then
            print_success "$dir_name cloned"
        else
            print_warning "Could not clone $gh_repo (repo may be private or unavailable) – skipping"
            rm -rf "$target"  # clean up partial clone
        fi
    fi
}

link_repo() {
    local source_dir="$1"
    if [ ! -d "$source_dir" ]; then
        print_error "Directory does not exist: $source_dir"
        exit 1
    fi
    local dir_name
    dir_name="$(basename "$source_dir")"
    local target="$ECOSYSTEM_DIR/$dir_name"

    if [ -e "$target" ] || [ -L "$target" ]; then
        print_warning "$target already exists – removing old entry"
        rm -rf "$target"
    fi

    ln -s "$(realpath "$source_dir")" "$target"
    print_success "Linked $dir_name → $source_dir"
}

write_ecosystem_env() {
    local env_file="$ECOSYSTEM_DIR/.env.ecosystem"
    if [ -f "$env_file" ]; then
        return 0  # already written
    fi

    cat > "$env_file" << 'EOF'
# Ecosystem environment configuration
# Sourced by start.sh when --ecosystem flag is used.

# OpenCode Agent Hub
OPENCODE_HUB_PORT=9100
OPENCODE_HUB_HOST=0.0.0.0

# OpenClaw message-routing gateway
OPENCLAW_GATEWAY_PORT=9200
OPENCLAW_GATEWAY_HOST=0.0.0.0

# Swarm-Tools SQLite database
SWARM_DB_PATH=~/.config/swarm-tools/swarm.db

# oh-my-opencode harness
OH_MY_OPENCODE_PORT=9300
EOF
    print_success "Created $env_file – edit as needed"
}

show_summary() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         Antigravity Ecosystem Setup Complete!                ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Ecosystem directory: $ECOSYSTEM_DIR"
    echo ""
    echo "Cloned / linked repos:"
    for entry in "${ECOSYSTEM_REPOS[@]}"; do
        local dir_name="${entry%%|*}"
        local target="$ECOSYSTEM_DIR/$dir_name"
        if [ -d "$target" ] || [ -L "$target" ]; then
            echo -e "  ${GREEN}✓${NC} $dir_name"
        else
            echo -e "  ${YELLOW}–${NC} $dir_name (not available)"
        fi
    done
    echo ""
    echo "To start the full ecosystem:"
    echo "  ./start.sh --ecosystem"
    echo ""
    echo "To start with Docker:"
    echo "  docker compose --profile ecosystem up -d"
    echo ""
}

# ── main ───────────────────────────────────────────────────────────────────────
main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║       Antigravity Ecosystem Setup                          ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    check_git
    mkdir -p "$ECOSYSTEM_DIR"

    # Parse arguments
    UPDATE_MODE=false
    LINK_DIR=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --update)
                UPDATE_MODE=true
                shift
                ;;
            --link)
                LINK_DIR="${2:-}"
                shift 2
                ;;
            *)
                print_error "Unknown argument: $1"
                echo "Usage: $0 [--update] [--link <local_dir>]"
                exit 1
                ;;
        esac
    done

    export UPDATE_MODE

    if [ -n "$LINK_DIR" ]; then
        link_repo "$LINK_DIR"
    else
        for entry in "${ECOSYSTEM_REPOS[@]}"; do
            IFS='|' read -r dir_name gh_repo description <<< "$entry"
            clone_or_update_repo "$dir_name" "$gh_repo" "$description"
        done
    fi

    write_ecosystem_env
    show_summary
}

main "$@"
