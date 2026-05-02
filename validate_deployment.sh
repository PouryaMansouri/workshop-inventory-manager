#!/bin/bash
# Deployment Validation Script

echo "=== Workshop Tool Inventory System - Deployment Validation ==="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $1 missing"
        ((FAIL++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 directory exists"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $1 directory missing"
        ((FAIL++))
    fi
}

echo "1. Checking Docker Configuration..."
check_file "Dockerfile"
check_file "docker-compose.yml"
check_file ".dockerignore"
check_file "docker-entrypoint.sh"
check_file ".env.example"
echo ""

echo "2. Checking Documentation..."
check_file "docs/deployment.md"
check_file "docs/operations.md"
check_file "docs/architecture.md"
check_file "docs/database.md"
check_file "docs/development_guide.md"
check_file "SECURITY_CHECKLIST.md"
check_file "RISK_REGISTER.md"
echo ""

echo "3. Checking Test Structure..."
check_dir "tests/core"
check_dir "tests/admin"
check_dir "tests/integration"
check_dir "tests/performance"
check_file "tests/core/test_transaction_service.py"
check_file "tests/core/test_stock_service.py"
check_file "tests/core/test_barcode_service.py"
check_file "tests/core/test_csv_import_service.py"
check_file "tests/core/test_transaction_validators.py"
check_file "tests/core/test_inventory_validators.py"
check_file "tests/transactions/test_transaction_model.py"
check_file "tests/admin/test_admin_actions.py"
check_file "tests/integration/test_workflows.py"
check_file "tests/performance/test_queries.py"
echo ""

echo "4. Checking Application Structure..."
check_dir "apps/inventory"
check_dir "apps/transactions"
check_dir "apps/maintenance"
check_dir "apps/dashboard"
check_dir "core/services"
check_dir "core/selectors"
check_dir "core/validators"
echo ""

echo "5. Checking Configuration..."
check_file "config/settings/base.py"
check_file "config/settings/dev.py"
check_file "config/settings/prod.py"
check_file "requirements.txt"
echo ""

echo "=== Validation Summary ==="
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ System is ready for deployment!${NC}"
    exit 0
else
    echo -e "${RED}✗ System has missing components. Please review.${NC}"
    exit 1
fi
