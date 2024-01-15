## To run the application:

go to the directory containing dash_app.py and run:

```
celery -A dash_app:celery_app worker --loglevel=INFO --concurrency=2
```

go to the directory containing dash_app.py and run:

```
python dash_app.py
```
