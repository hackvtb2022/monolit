# monolit


##### Зависимости:
```bash
pip install -r requirements_aggregator.txt
pip install -r requirements_api.txt
pip install -r requirements_scraper.txt
```

##### `pre-commit hooks`:
```bash
pip install pre-commit
pre-commit install
pre-commit autoupdate
pre-commit install-hooks
```

Запуск pre-commit:

```bash
pre-commit run --all-files -v
```

##### Локальный запуск

```bash
docker compose up -d app
```
