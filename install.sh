#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  AuditCaddie OSS — One-Click Installer
#  Usage: curl -sSL https://raw.githubusercontent.com/Blodgic/AuditCaddie/main/install.sh | bash
#  Docs:  https://github.com/Blodgic/AuditCaddie
# ─────────────────────────────────────────────────────────────────────────────
set -e

REPO="https://raw.githubusercontent.com/Blodgic/AuditCaddie/main"
INSTALL_DIR="${AUDITCADDIE_DIR:-$HOME/auditcaddie}"
PORT="${AUDITCADDIE_PORT:-8080}"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'

echo ""
echo -e "${BOLD}  AuditCaddie OSS${NC} — Self-Hosted Compliance Engine"
echo -e "  ${BLUE}github.com/Blodgic/AuditCaddie${NC}"
echo ""

# ── Check Docker ──────────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
  echo -e "${RED}✗ Docker is required but not installed.${NC}"
  echo "  Install Docker Desktop: https://www.docker.com/products/docker-desktop"
  echo "  Then re-run this script."
  exit 1
fi

if ! docker compose version &>/dev/null 2>&1 && ! docker-compose version &>/dev/null 2>&1; then
  echo -e "${RED}✗ Docker Compose is required. Please update Docker Desktop.${NC}"
  exit 1
fi

echo -e "${GREEN}✓${NC} Docker found: $(docker --version | cut -d' ' -f3 | tr -d ',')"

# ── Create install directory ──────────────────────────────────────────────────
mkdir -p "$INSTALL_DIR"/{data,templates}
cd "$INSTALL_DIR"
echo -e "${GREEN}✓${NC} Install directory: $INSTALL_DIR"

# ── Download core files ───────────────────────────────────────────────────────
echo -e "\n${BOLD}Downloading AuditCaddie OSS...${NC}"

curl -sSfL "$REPO/docker-compose.yml" -o docker-compose.yml
echo -e "  ${GREEN}✓${NC} docker-compose.yml"

for tmpl in soc2-startup nist-csf-smb iso27001-saas hipaa-healthtech vendor-assessment; do
  curl -sSfL "$REPO/templates/${tmpl}.yaml" -o "templates/${tmpl}.yaml"
  echo -e "  ${GREEN}✓${NC} templates/${tmpl}.yaml"
done

# ── Configure .env ────────────────────────────────────────────────────────────
if [ ! -f .env ]; then
  curl -sSfL "$REPO/.env.example" -o .env

  echo ""
  echo -e "${BOLD}Configuration${NC}"
  echo -e "${YELLOW}You'll need at least one AI API key. You can also set these later in the UI.${NC}"
  echo ""

  read -p "  OpenAI API key (sk-...): " OPENAI_KEY
  read -p "  Anthropic API key (sk-ant-...) [optional]: " ANTHROPIC_KEY
  read -p "  AWS Access Key ID [optional]: " AWS_KEY
  read -p "  AWS Secret Access Key [optional]: " AWS_SECRET
  read -p "  GitHub Token (ghp_...) [optional]: " GH_TOKEN
  read -p "  GitHub Org name [optional]: " GH_ORG
  read -p "  Port (default: 8080): " CUSTOM_PORT
  PORT="${CUSTOM_PORT:-8080}"

  # Write .env
  cat > .env <<EOF
OPENAI_API_KEY=${OPENAI_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_KEY}
AI_MODEL=$([ -n "$OPENAI_KEY" ] && echo "gpt-4o" || echo "claude-sonnet-4-5")
AWS_ACCESS_KEY_ID=${AWS_KEY}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET}
AWS_DEFAULT_REGION=us-east-1
GITHUB_TOKEN=${GH_TOKEN}
GITHUB_ORG=${GH_ORG}
PORT=${PORT}
EOF
  echo -e "\n${GREEN}✓${NC} .env configured"
else
  echo -e "${YELLOW}→${NC} .env already exists, skipping configuration"
fi

# ── Pull and start ────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}Starting AuditCaddie OSS...${NC}"

COMPOSE_CMD="docker compose"
command -v docker-compose &>/dev/null && COMPOSE_CMD="docker-compose"

$COMPOSE_CMD pull --quiet 2>/dev/null || true
$COMPOSE_CMD up -d

# ── Health check ──────────────────────────────────────────────────────────────
echo -n "  Waiting for startup"
for i in $(seq 1 30); do
  if curl -sf "http://localhost:${PORT}/api/health" &>/dev/null; then
    echo ""
    echo -e "  ${GREEN}✓${NC} AuditCaddie is running!"
    break
  fi
  echo -n "."
  sleep 2
done

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}✓ AuditCaddie OSS is running!${NC}"
echo ""
echo -e "  Open:    ${BLUE}http://localhost:${PORT}${NC}"
echo -e "  Data:    $INSTALL_DIR/data/"
echo -e "  Logs:    docker logs -f audit-caddie-oss"
echo -e "  Stop:    cd $INSTALL_DIR && docker compose down"
echo -e "  Update:  cd $INSTALL_DIR && docker compose pull && docker compose up -d"
echo ""
echo -e "  ${YELLOW}Upgrade to Enterprise for team access, Fieldguide integration,"
echo -e "  and auditor portal: ${BLUE}https://auditcaddie.com/pricing${NC}"
echo ""

# Try to open browser (Mac/Linux)
if command -v open &>/dev/null; then
  open "http://localhost:${PORT}" 2>/dev/null || true
elif command -v xdg-open &>/dev/null; then
  xdg-open "http://localhost:${PORT}" 2>/dev/null || true
fi
