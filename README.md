# Monolit

![alt text](logo.png "Logo")

##### Структура проекта:


- docker - директория с докер образами для сервисов
- service_aggregator - сервис, реализующего поиск трендов новостей по переданному корпусу текста
- service_api - API сервис, реализующий доступ к поиску трендов новостей
- service_filterer - сервис, реализующий фильтрацию на "не новости"
- service_insights - сервис, выделяющий инсайты из текста новости
- service_scraper - сервис пауков, выполняющих парсинг новостных сайтов


##### Локальный запуск API


Необходимо скачать бинарный файл обученных эмбеддингов на новостях - https://drive.google.com/u/0/uc?id=11K3T8uHspn7nK21m3be5hM6hYKl5igPC&export=download и положить его по пути `monolit/service_aggregator/models/ru_vectors_v3.bin`

Запуск сервиса API:

```bash
docker compose up -d api
```

- При старе api предварительно запускается сервис db базы данных, который создает таблицы из `monolit/sql/init.sql`
- API доступно локально по адресу: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Endpoint, реализующий поиск новостей: `http://localhost:8000/api/v1/trands/`
- В момент запроса в endpoint выполняется выгрузка данных из БД за выбранный период
- Для обработки новостей вызываются модули сервисов `service_aggregator` и `service_insights`


Запуск пауков:
```bash
docker compose up -d scraper
```

- Пауки работают в фоне, опрашивая новостные сайты каждые `SPIDER_WAIT_TIMEOUT_SEC` секунд за период `SPIDER_PERIOD_DAYS` дней.

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
