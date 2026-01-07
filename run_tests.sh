rm -r app/__pycache__
rm -r tests/__pycache__
rm -r .pytest_cache
rm -r __pycache__

black . && isort .

set -a  # Auto-export all variables
    source .env.testing
    set +a
pytest tests/ -v
