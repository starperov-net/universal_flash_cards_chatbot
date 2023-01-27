from piccolo.conf.apps import AppRegistry

from app.settings import settings
from piccolo_conf import PostgresEngine

DB = PostgresEngine(config={"database": settings.POSTGRES_TEST_DATABASE_NAME})


APP_REGISTRY = AppRegistry(apps=["app.piccolo_app"])
