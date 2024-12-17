import random
import string
import logging
from social_core.pipeline.user import create_user  # Импорт только необходимой функции

logger = logging.getLogger(__name__)  # Исправлено: logger корректно определён

def pipeline_debug_step(*args, **kwargs):
    """
    Отладочный шаг pipeline для логирования аргументов и параметров
    """
    logger.debug(f"Pipeline debug step: args={args}, kwargs={kwargs}")
    return {}

def early_test_pipeline_step(*args, **kwargs):
    """
    Тестовый шаг pipeline
    """
    logger.debug("Early test step executed")
    return {}

def test_pipeline_step(*args, **kwargs):
    """
    Ещё один тестовый шаг pipeline
    """
    logger.debug(f"Test step called with args={args}, kwargs={kwargs}")

def generate_fake_email(strategy, details, user=None, *args, **kwargs):
    """
    Генерация поддельного email, если он отсутствует
    """
    logger.debug("generate_fake_email called with details: %s", details)
    if not details.get('email'):
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        details['email'] = f"generated_user_{random_part}@example.com"
        logger.debug("Generated fake email: %s", details['email'])
    return {'details': details}

def log_pipeline_step(*args, **kwargs):
    """
    Логирование шагов pipeline
    """
    logger.debug(f"Pipeline step called with args={args}, kwargs={kwargs}")

def create_user_with_logging(strategy, details, backend, user=None, *args, **kwargs):
    """
    Создаёт пользователя с использованием стандартного pipeline
    """
    logger.debug(f"Creating user with details: {details}")
    return create_user(strategy, details, backend, user, *args, **kwargs)

def log_access_token(strategy, *args, **kwargs):
    import logging
    logger = logging.getLogger(__name__)
    response = kwargs.get('response', {})
    logger.info(f"VK Response: {response}")  # Логирование полного ответа VK
    token = response.get('access_token')
    logger.info(f"Access Token: {token}")
    # Логируем любые ошибки
    if 'error' in response:
        logger.error(f"VK Error: {response['error']}")
    return {}

def debug_state(strategy, backend, *args, **kwargs):
    import logging
    logger = logging.getLogger(__name__)
    # Попытка получить state из kwargs или из сессии, если это актуально
    state = kwargs.get('state') or strategy.session_get('state')
    logger.debug(f"Current state value: {state}")
    return {}

def log_state(strategy, *args, **kwargs):
    """
    Логирование параметра state для отладки.
    """
    state = kwargs.get('state') or strategy.session_get('state')
    if not state:
        logger.error("Параметр OAuth state отсутствует или некорректен.")
    else:
        logger.debug(f"OAuth state: {state}")
    return {}
