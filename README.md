# Pantopix assesment

## how to run

Fur runnint the project there are two options

1) within dev container by running:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2) by creating container:
```bash
#use podman or docker
podman build -f .devcontainer/Dockerfile -t pantopix_image .
podman run -it --env-file .env -p 8000:8000 pantopix_image
```

## Accessing app

access by: `http://localhost:8000/static/index.html`

docs: `http://localhost:8000/docs`

redoc: `http://localhost:8000/redoc`

openapi: `http://localhost:8000/openapi.json`

## Overview

Application utilizes the python FastAPI framework with use of:
pydantic for models
precommit hook - later pylint disabled as I got tired of constant nagging 😅
isort, pylint, pytest, autoflake, black

### Core functionality
- launch tracking
```bash
# e.g.
curl "http://localhost:8000/launches/filter?success=true&rocket=5e9d0d95eda69955f709d1eb"
```
```json
[{"id":"5eb87cdbffd86e000604b32d","name":"RatSat","date_utc":"2008-09-28T23:15:00.000Z","date_unix":1222643700,"rocket":"5e9d0d95eda69955f709d1eb","launchpad":"5e9e4502f5090995de566f86","success":true,"details":"Ratsat was carried to orbit on the first successful orbital launch of any privately funded and developed, liquid-propelled carrier rocket, the SpaceX Falcon 1","links":{"patch":{"small":"https://images2.imgbox.com/95/39/sRqN7rsv_o.png","large":"https://images2.imgbox.com/a3/99/qswRYzE8_o.png"},"reddit":{"campaign":null,"launch":null,"media":null,"recovery":null},"flickr":{"small":[],"original":[]},"presskit":null,"webcast":"https://www.youtube.com/watch?v=dLQ2tZEH6G0","youtube_id":"dLQ2tZEH6G0","article":"https://en.wikipedia.org/wiki/Ratsat","wikipedia":"https://en.wikipedia.org/wiki/Ratsat"},"failures":[]},{"id":"5eb87cdcffd86e000604b32e","name":"RazakSat","date_utc":"2009-07-13T03:35:00.000Z","date_unix":1247456100,"rocket":"5e9d0d95eda69955f709d1eb","launchpad":"5e9e4502f5090995de566f86","success":true,"details":null,"links":{"patch":{"small":"https://images2.imgbox.com/ab/5a/Pequxd5d_o.png","large":"https://images2.imgbox.com/92/e4/7Cf6MLY0_o.png"},"reddit":{"campaign":null,"launch":null,"media":null,"recovery":null},"flickr":{"small":[],"original":[]},"presskit":"http://www.spacex.com/press/2012/12/19/spacexs-falcon-1-successfully-delivers-razaksat-satellite-orbit","webcast":"https://www.youtube.com/watch?v=yTaIDooc8Og","youtube_id":"yTaIDooc8Og","article":"http://www.spacex.com/news/2013/02/12/falcon-1-flight-5","wikipedia":"https://en.wikipedia.org/wiki/RazakSAT"},"failures":[]}]
```
- Statistic generation
```bash
curl "http://localhost:8000/stats/data"
```
```json
{
  "successByRocket": {
    "labels": ["Falcon 1", "Falcon 9", "Falcon Heavy"],
    "values": [0.4, 0.98, 1.0]
  },
  "launchesBySite": {
    "labels": ["VAFB", "CCAFS", "KSC"],
    "values": [45, 120, 35]
  },
  "frequencyByYear": {
    "labels": [2020, 2021, 2022], # years
    "values": [[2, 3, 1, ...], [5, 4, 6, ...], ...] # months for specific year
  }
}
```
### Optional
YES - A simple web-based interface to view launch details and statistics.

YES - Export data to CSV/JSON

NO  - Webhook notifications for new launches
- While I technically understand the mechanics of webhooks and could easily implement it with use of AI I have decided to not to include it.
The reason is this: as there is no scheduler to load new data so there is no point to notify anybody, data are not streamed, the older data are the same and new data are refreshed quite often (every 10 minutes)

YES - Implement a cache invalidation strategy for outdated or stale data.
- I have  implemented very simple cache for data retention and expiration_ttl strategy for refresh, set for 10 minutes.
Otherwise, I would probably use something more robust, maybe with use of decorators, but didnt want to over engineer the soludion. But simpler solution means less code, and less code means less bugs.

### Tests

```bash
# run within devcontainer
root@63d120b1d30a:/workspace# bash run_tests.sh
rm: cannot remove 'app/__pycache__': No such file or directory
rm: cannot remove 'tests/__pycache__': No such file or directory
rm: cannot remove '__pycache__': No such file or directory
reformatted /workspace/tests/analytics_test.py

All done! ✨ 🍰 ✨
1 file reformatted, 15 files left unchanged.
Fixing /workspace/tests/analytics_test.py
Skipped 1 files
==================================================================================================== test session starts ====================================================================================================
platform linux -- Python 3.13.11, pytest-9.0.2, pluggy-1.6.0 -- /usr/local/bin/python3.13
cachedir: .pytest_cache
rootdir: /workspace
configfile: pytest.ini
plugins: anyio-4.12.1, asyncio-1.3.0, dotenv-0.5.2, respx-0.22.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 21 items

tests/analytics_test.py::test_rocket_success_rate_basic PASSED                                                                                                                                                        [  4%]
tests/analytics_test.py::test_launches_by_site_counts PASSED                                                                                                                                                          [  9%]
tests/analytics_test.py::test_launch_frequency_by_month_and_year PASSED                                                                                                                                               [ 14%]
tests/analytics_test.py::test_rocket_success_rate_empty_list PASSED                                                                                                                                                   [ 19%]
tests/analytics_test.py::test_rocket_success_rate_none_success PASSED                                                                                                                                                 [ 23%]
tests/error_handling_test.py::test_get_data_timeout PASSED                                                                                                                                                            [ 28%]
tests/error_handling_test.py::test_get_data_http_error PASSED                                                                                                                                                         [ 33%]
tests/error_handling_test.py::test_cache_with_invalid_data PASSED                                                                                                                                                     [ 38%]
tests/export_test.py::test_export_csv_all_launches PASSED                                                                                                                                                             [ 42%]
tests/export_test.py::test_export_csv_filtered_by_success PASSED                                                                                                                                                      [ 47%]
tests/export_test.py::test_export_csv_filtered_by_date_range PASSED                                                                                                                                                   [ 52%]
tests/export_test.py::test_export_csv_with_none_details PASSED                                                                                                                                                        [ 57%]
tests/export_test.py::test_export_json_all_launches PASSED                                                                                                                                                            [ 61%]
tests/export_test.py::test_export_json_filtered_by_rocket PASSED                                                                                                                                                      [ 66%]
tests/export_test.py::test_export_json_empty_result PASSED                                                                                                                                                            [ 71%]
tests/export_test.py::test_export_json_structure PASSED                                                                                                                                                               [ 76%]
tests/filter_launches_test.py::test_filter_launches_date_range PASSED                                                                                                                                                 [ 80%]
tests/filter_launches_test.py::test_filter_launches_success PASSED                                                                                                                                                    [ 85%]
tests/load_launches_test.py::test_load_cached_data_cache_miss PASSED                                                                                                                                                  [ 90%]
tests/load_launches_test.py::test_load_cached_data_cache_hit PASSED                                                                                                                                                   [ 95%]
tests/main_test.py::test_health_endpoint PASSED                                                                                                                                                                       [100%]

===================================================================================================== warnings summary ======================================================================================================
tests/analytics_test.py::test_launch_frequency_by_month_and_year
tests/analytics_test.py::test_launch_frequency_by_month_and_year
tests/analytics_test.py::test_launch_frequency_by_month_and_year
  /workspace/app/analytics.py:42: DeprecationWarning: datetime.datetime.utcfromtimestamp() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.fromtimestamp(timestamp, datetime.UTC).
    dt = datetime.utcfromtimestamp(t)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============================================================================================== 21 passed, 3 warnings in 0.32s ===============================================================================================

```

### Disclaimer:

I have Used 'AI' the way I would have used Stackoverflow.

I Used 'AI' code generation for optional FE task, as I am not a Frontend developer, but I can still explain every line of code to you. Also its faster.

### Env File:
.env & .env.testing
```bash
# DEBUG
# DEBUG_LEVEL=10
# INFO
DEBUG_LEVEL=20
# DEBUG_LEVEL=30  # WARNING
# DEBUG_LEVEL=40  # ERROR
# DEBUG_LEVEL=50  # CRITICAL

```

---------------------------

Personal underline notes

```bash
autoflake --remove-all-unused-imports --in-place --recursive .
pylint .
pytest tests/
black .
isort .
```
