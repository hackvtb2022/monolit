# monolit

##### Структура проекта:

docker - директория с докер образами для сервисов
service_aggregator - сервис, реализующего поиск трендов новостей по переданному корпусу текста
service_api - API сервис, ерализующий доступ к поиску трендов новостей
service_filterer - сервис, реализующий фильтрацию на "не новости"
service_insights - сервис, выделяющие инсайты из текста новост
service_scraper - сервисы пауков, выполняющих парсинг новостных сайтов


##### Локальный запуск API

```bash
docker compose up -d api
```

- При старе api предварительно запускается сервис db базы данных, который создает таблицы из `monolit/sql/init.sql`
- API доступно локально по адресу: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Endpoint, реализующий поиск новостей: `http://localhost:8000/api/v1/trands/`

##### Зависимости:
```bash
pip install -r requirements_aggregator.txt
pip install -r requirements_api.txt
pip install -r requirements_filterer.txt
pip install -r requirements_scraper.txt
pip install -r requirements_insights
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
