from piccolo.conf.apps import AppRegistry

from piccolo_conf import PostgresEngine
from app.settings import settings


DB = PostgresEngine(config={"database": settings.POSTGRES_TEST_DATABASE_NAME})


APP_REGISTRY = AppRegistry(apps=["app.piccolo_app"])
