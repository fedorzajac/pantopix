run app
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```




```bash
autoflake --remove-all-unused-imports --in-place --recursive .
pylint .
pytest tests/
black .
isort .
```
