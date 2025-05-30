# telegram_bot/bot/handlers/commands.py

from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from telegram_bot.bot.utils.api_client import APIClient, get_user_api_token
from telegram_bot.bot.keyboards.inline import navigation_kb

import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    """
    Обработчик команды /start — приветствует пользователя.
    """
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name
    logger.info(f"Пользователь {telegram_id} начал работу с ботом.")

    welcome_message = (
        f"Привет, {full_name}! Я бот FlowerDelivery.\n"
        "Используй кнопки ниже для взаимодействия."
    )

    await message.answer(
        welcome_message,
        reply_markup=navigation_kb,  # Убедитесь, что navigation_kb импортирован и настроен
        parse_mode="HTML"  # Явно указываем parse_mode
    )


@router.message(Command(commands=["help"]))
async def cmd_help(message: Message, state: FSMContext):
    """
    Обработчик команды /help — показывает список доступных команд.
    """
    telegram_id = message.from_user.id
    logger.info(f"Пользователь {telegram_id} запросил помощь.")
    help_text = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/link &lt;username&gt; - Связать Telegram аккаунт с учётной записью на сайте\n"
        "/order - Создать новый заказ\n"
        "/status &lt;order_id&gt; - Узнать статус заказа\n"
        "/clear - Сбросить текущее состояние"
    )
    await message.answer(
        help_text,
        parse_mode="HTML"  # Явно указываем parse_mode
    )


@router.message(Command(commands=["link"]))
async def cmd_link(message: Message, state: FSMContext):
    """
    Обработчик команды /link — связывает Telegram аккаунт с учётной записью на сайте.
    """
    telegram_id = message.from_user.id
    logger.info(f"Пользователь {telegram_id} инициировал связывание аккаунта.")

    # Извлечение username из команды
    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.answer("Пожалуйста, используйте команду в формате: /link &lt;username&gt;", parse_mode="HTML")
        return

    username = parts[1]

    # Сохранение username в состоянии для дальнейшей обработки через callback
    await state.update_data(username=username)
    await state.set_state("linking_account")  # Предполагаем, что у вас есть состояние для связывания

    # Отправка сообщения с подтверждением связывания
    confirm_link_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Связать", callback_data="confirm_link"),
                InlineKeyboardButton(text="Отмена", callback_data="cancel_link")
            ]
        ],
        row_width=2
    )

    await message.answer(
        f"Вы хотите связать ваш Telegram аккаунт с учётной записью '{username}'?",
        reply_markup=confirm_link_kb,
        parse_mode="HTML"
    )


@router.message(Command(commands=["order"]))
async def cmd_order(message: Message, state: FSMContext):
    """
    Обработчик команды /order — инициирует процесс создания заказа.
    """
    telegram_id = message.from_user.id
    logger.info(f"Пользователь {telegram_id} инициирует создание заказа через команду /order.")

    # Здесь можно вызвать функцию инициирования заказа, например, через callback или напрямую
    # Например, можно отправить пользователю список товаров или перейти в состояние создания заказа
    await message.answer(
        "Процесс создания заказа начат. Пожалуйста, выберите товар или используйте кнопку 'Создать заказ' в меню.",
        reply_markup=navigation_kb,
        parse_mode="HTML"
    )


@router.message(Command(commands=["status"]))
async def cmd_status(message: Message, state: FSMContext):
    """
    Обработчик команды /status — узнаёт статус заказа по order_id.
    """
    telegram_id = message.from_user.id
    logger.info(f"Пользователь {telegram_id} запросил статус заказа.")

    # Разделение команды и параметра
    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.answer("Пожалуйста, используйте команду в формате: /status &lt;order_id&gt;", parse_mode="HTML")
        return

    order_id = parts[1]

    if not order_id.isdigit():
        await message.answer("Пожалуйста, введите корректный идентификатор заказа (целое число).", parse_mode="HTML")
        return

    api_token = await get_user_api_token(telegram_id)
    if not api_token:
        logger.warning(f"Пользователь {telegram_id} не связан с учётной записью.")
        await message.answer(
            "Ваш Telegram аккаунт не связан с учётной записью на сайте. Используйте /link для связывания.",
            parse_mode="HTML")
        return

    api_client = APIClient(token=api_token)
    logger.debug(f"APIClient инициализирован для пользователя {telegram_id}")

    try:
        status_response = await api_client.get_order_status(order_id)
        status_display = status_response.get('status_display', 'Неизвестен')
        await message.answer(
            f"Статус вашего заказа №{order_id}: {status_display}",
            parse_mode="HTML"
        )
        logger.info(f"Пользователь {telegram_id} получил статус заказа №{order_id}: {status_display}")
    except Exception as e:
        logger.error(f"Ошибка при получении статуса заказа для пользователя {telegram_id}: {e}")
        await message.answer("Произошла ошибка при получении статуса заказа. Пожалуйста, попробуйте позже.",
                             parse_mode="HTML")
    finally:
        await api_client.close()
        logger.debug(f"APIClient для пользователя {telegram_id} закрыт")


@router.message(Command(commands=["clear"]))
async def cmd_clear(message: Message, state: FSMContext):
    """
    Обработчик команды /clear — сбрасывает состояние пользователя.
    """
    telegram_id = message.from_user.id
    logger.info(f"Пользователь {telegram_id} инициирует сброс состояния.")

    # Сброс состояния пользователя
    await state.clear()

    # Отправка подтверждающего сообщения
    await message.answer(
        "Ваше состояние было успешно сброшено.",
        parse_mode="HTML"
    )


@router.message(F.text.startswith('/'))
async def unknown_command(message: Message):
    """
    Обработчик неизвестных команд.
    """
    telegram_id = message.from_user.id
    logger.info(f"Пользователь {telegram_id} ввёл неизвестную команду: {message.text}")
    await message.answer(
        "Извините, я не понимаю эту команду. Используйте /help для списка доступных команд.",
        parse_mode="HTML"
    )
