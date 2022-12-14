import asyncio
import logging
from os import getenv
from typing import Any, Dict, List, Tuple
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram_media_group import MediaGroupFilter, media_group_handler
import sqlite3

storage = MemoryStorage()
database = "users.db"

api_token = "5094482535:AAGyFsCLRWYXzutpnvaepjab-pKWDbqTFZ4"
bot = Bot(token=api_token)
dp = Dispatcher(bot, storage=storage)
admin = "452917869"
logging.basicConfig(level=logging.DEBUG)


class Chimchistka(StatesGroup):
	rod_zagryazneniya = State()
	predmet_mebeli = State()
	vopros_divan = State()
	kolichestvo_mest = State()
	vikatnoye = State()
	kolichestvo_podushek = State()
	foto_mebeli = State()
	phone = State()
	proverka = State()
	name = State()
	tip_oplati = State()
	rekviziti = State()
	adres = State()
	komment = State()


class Uborka(StatesGroup):
	tip_pomesheniya = State()
	ploshad = State()
	tip_uborki = State()
	phone = State()
	proverka = State()
	name = State()
	tip_oplati = State()
	rekviziti = State()
	adres = State()
	komment = State()


class Okna(StatesGroup):
	rod_zagryazneniya = State()
	tip_uslugi = State()
	kolichestvo_okon = State()
	sekcii = State()
	tip_ostekleniya = State()
	blok = State()
	foto = State()
	phone = State()
	proverka = State()
	name = State()
	tip_oplati = State()
	rekviziti = State()
	adres = State()
	komment = State()
	
class Rassilka(StatesGroup):
	getmes = State()
	

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals="отмена", ignore_case=True), state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply(
        "Вы остановили оформление заявки.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Вернутся в начало"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )


@dp.message_handler(lambda msg: msg.text.lower() == "вернутся в начало" or msg.text.lower() == "/start", state=None)
async def send_welcome(message: types.Message):
    await message.reply(
        "При заказе двух и более услуг Вы получаете скидку 10%" + '\n' + "Выберите необходимую Вам услугу" + '\n' + 'Для возврата в начало введите "Отмена"',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Химическая чистка мягкой мебели"),
                    KeyboardButton(text="Мытье окон и балконов"),
                    KeyboardButton(text="Уборка помещений"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )

@dp.message_handler(commands='sendall', chat_id=admin, state=None)
async def mass_message(message: types.Message):
	await Rassilka.getmes.set()
	await message.reply('Введите сообщение для рассылки пользователям')


@dp.message_handler(state=Rassilka.getmes)
async def vibor_tipa(message: types.Message, state=Rassilka.getmes):
	async with state.proxy() as data:
		data['getmes'] = message.text
		connect = sqlite3.connect(database)
		cursor = connect.cursor()
		usrs = cursor.execute("SELECT user_id, user_name, user_active FROM main").fetchall()
		for i in usrs:
			try:
				if i[2] == 1:
					cursor.execute(f"UPDATE main SET user_active = {0} WHERE user_id = {i[0]}")
				await bot.send_message(i[0], "Привет, " + i[1] + "!" + " " + data['getmes'])
			except:
				cursor.execute(f"UPDATE main SET user_active = {1} WHERE user_id = {i[0]}")
	await state.finish()
	

@dp.message_handler(lambda msg: msg.text == "Уборка помещений", state=None)
async def cm_start(message: types.Message):
    await Uborka.tip_pomesheniya.set()
    await message.reply('Укажите тип помещения (жилое, офис, производственное...)')


@dp.message_handler(state=Uborka.tip_pomesheniya)
async def vibor_tipa(message: types.Message, state=Uborka.tip_pomesheniya):
    async with state.proxy() as data:
        data['tip_pomesheniya'] = message.text
    await Uborka.next()
    await message.reply('Укажите площадь помещения')


@dp.message_handler(state=Uborka.ploshad)
async def vibor_tipa(message: types.Message, state=Uborka.ploshad):
    async with state.proxy() as data:
        data['ploshad'] = message.text
    await Uborka.next()
    await message.reply(
        "Выберите тип уборки",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Поддерживающая"),
                    KeyboardButton(text="Генеральная"),
                    KeyboardButton(text="После строительных работ"),
                    KeyboardButton(text="После пожара"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )

@dp.message_handler(content_types=["text"], state=Uborka.tip_uborki)
async def vibor_ploshadi(message: types.Message, state=Uborka.tip_uborki):
    async with state.proxy() as data:
        data['tip_uborki'] = message.text
    await Uborka.next()
    await message.reply('Введите Ваш номер телефона(+7...)')
    
	
@dp.message_handler(content_types=["text"], state=Uborka.phone)
async def vibor_ploshadi(message: types.Message, state=Uborka.phone):
    async with state.proxy() as data:
        data['phone'] = message.text
    await Uborka.next()
    await message.reply(
        'Оставляли ли Вы у нас заявку ранее? (Если адрес или тип оплаты с момента последней заявки изменился выберите ответ "Нет")',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Да"),
                    KeyboardButton(text="Нет"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )
	
@dp.message_handler(content_types=["text"], state=Uborka.proverka)
async def vibor_ploshadi(message: types.Message, state=Uborka.proverka):
	async with state.proxy() as data:
		data['proverka'] = message.text
		if data['proverka'].lower() == "да":
			await Uborka.komment.set()
			await message.reply('Если есть какая то дополнительная информация, то укажите ее')
		elif data['proverka'].lower() == "нет":
			await Uborka.next()
			await message.reply('Укажите Ваше имя')

@dp.message_handler(content_types=["text"], state=Uborka.name)
async def vibor_ploshadi(message: types.Message, state=Uborka.name):
	async with state.proxy() as data:
		data['name'] = message.text
	await Uborka.next()
	await message.reply(
		"Выберите тип оплаты",
		reply_markup=ReplyKeyboardMarkup(
			keyboard=[
				[
					KeyboardButton(text="Как физическое лицо"),
					KeyboardButton(text="Как юридическое лицо"),
				]
			],
			resize_keyboard=True,
			one_time_keyboard=True,
		)
	)

@dp.message_handler(content_types=["text"], state=Uborka.tip_oplati)
async def vibor_ploshadi(message: types.Message, state=Uborka.tip_oplati):
    async with state.proxy() as data:
        data['tip_oplati'] = message.text
        if data['tip_oplati'] == "Как юридическое лицо":
            await Uborka.next()
            await message.reply('Укажите реквизиты для выставления счета')
        elif data['tip_oplati'] == "Как физическое лицо":
            await Uborka.adres.set()
            await message.reply('Укажите Ваш адрес')


@dp.message_handler(content_types=["text"], state=Uborka.rekviziti)
async def vibor_ploshadi(message: types.Message, state=Uborka.rekviziti):
    async with state.proxy() as data:
        data['rekviziti'] = message.text
    await Uborka.next()
    await message.reply('Укажите Ваш адрес')
	
@dp.message_handler(content_types=["text"], state=Uborka.adres)
async def vibor_ploshadi(message: types.Message, state=Uborka.adres):
    async with state.proxy() as data:
        data['adres'] = message.text
    await Uborka.next()
    await message.reply('Если есть какая то дополнительная информация, то укажите ее')


@dp.message_handler(content_types=["text"], state=Uborka.komment)
async def adresuborka(message: types.Message, state=Uborka.komment):
	chat = message.chat.id
	async with state.proxy() as data:
		data['komment'] = message.text
	async with state.proxy() as data:
		if data['proverka'].lower() == 'нет':
			if data['tip_oplati'] == "Как юридическое лицо":
				zakaz1 = 'Услуга: Уборка помещений \n' + 'Тип помещения:  ' + data['tip_pomesheniya'] + '\n' + 'Площадь помещения:  ' + data['ploshad'] + '\n' + 'Тип уборки:  ' + data['tip_uborki'] + '\n' + 'Номер телефона:  ' + data['phone'] + '\n' +  'Имя:  ' + data['name'] + '\n' + 'Тип оплаты: ' + data['tip_oplati'] + '\n' + 'Реквизиты: ' + data['rekviziti'] + '\n' + 'Адрес и контакты' + data['adres'] + '\n' + 'Комментарий:  ' + data['komment']
			elif data['tip_oplati'] == "Как физическое лицо":
				zakaz1 = 'Услуга: Уборка помещений \n' + 'Тип помещения:  ' + data['tip_pomesheniya'] + '\n' + 'Площадь помещения:  ' + data['ploshad'] + '\n' + 'Тип уборки:  ' + data['tip_uborki'] + '\n' + 'Номер телефона:  ' + data['phone'] + '\n' +  'Имя:  ' + data['name'] + '\n' + 'Тип оплаты: ' + data['tip_oplati'] + '\n' + 'Адрес и контакты: ' + data['adres'] + '\n' + 'Комментарий:  ' + data['komment']
		elif data['proverka'].lower() == 'да':
			zakaz1 = 'Услуга: Уборка помещений \n' + 'Тип помещения:  ' + data['tip_pomesheniya'] + '\n' + 'Площадь помещения:  ' + data['ploshad'] + '\n' + 'Тип уборки:  ' + data['tip_uborki']  + '\n' +  'Номер телефона:  ' + data['phone']  + '\n' + 'Комментарий:  ' + data['komment']
		await bot.send_message(chat_id=admin, text=zakaz1)
		await message.reply(
			"Ваша заявка принята",
			reply_markup=ReplyKeyboardMarkup(
				keyboard=[
					[
						KeyboardButton(text="Вернутся в начало"),
					]
				],
				resize_keyboard=True,
				one_time_keyboard=True,
			)
		)
	connect = sqlite3.connect(database)
	cursor = connect.cursor()
	people_id = message.chat.id
	cursor.execute(f"SELECT user_id FROM main WHERE user_id = {people_id}")
	info = cursor.fetchone()
	if info is None:
		async with state.proxy() as data:
			user_phone = data['phone']
			user_name = data['name']
			user_id = message.chat.id
			user_active = 0
			cursor.execute("INSERT INTO main(user_id,user_name,user_phone,user_active) VALUES(?,?,?,?)", (user_id, user_name, user_phone, user_active))
			connect.commit()
	await state.finish()


@dp.message_handler(lambda msg: msg.text == "Мытье окон и балконов", state=None)
async def cm_start(message: types.Message):
    await Okna.rod_zagryazneniya.set()
    await message.reply(
        "Укажите тип необходимой мойки",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Сезонная мойка"),
                    KeyboardButton(text="Мойка после строительных работ"),
                    KeyboardButton(text="После пожара"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )


@dp.message_handler(state=Okna.rod_zagryazneniya)
async def cm_start(message: types.Message, state=Okna.rod_zagryazneniya):
    async with state.proxy() as data:
        data['rod_zagryazneniya'] = message.text
    await Okna.next()
    await message.reply(
        "Выберите необходимые услуги",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Мойка окон"),
                    KeyboardButton(text="Мойка балкона"),
                    KeyboardButton(text="Мойка окон и балкона"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )


@dp.message_handler(state=Okna.tip_uslugi)
async def vibor_tipa(message: types.Message, state=Okna.tip_uslugi):
    async with state.proxy() as data:
        data['tip_uslugi'] = message.text
        if data['tip_uslugi'] == "Мойка окон":
            await Okna.next()
            await message.reply('Укажите количество окон')
        elif data['tip_uslugi'] == "Мойка балкона":
            await Okna.sekcii.set()
            await message.reply('Укажите количество секций балкона')
        elif data['tip_uslugi'] == "Мойка окон и балкона":
            await Okna.next()
            await message.reply('Укажите количество окон')


@dp.message_handler(state=Okna.kolichestvo_okon)
async def vibor_tipa(message: types.Message, state=Okna.kolichestvo_okon):
    async with state.proxy() as data:
        data['kolichestvo_okon'] = message.text
        if data['tip_uslugi'] == "Мойка окон":
            await Okna.foto.set()
            await message.reply('Для более точного определения стоимости пришлите пожалуйста фотографии окон')
        else:
            await Okna.next()
            await message.reply('Укажите количество секций балкона')


@dp.message_handler(state=Okna.sekcii)
async def vibor_tipa(message: types.Message, state=Okna.sekcii):
	async with state.proxy() as data:
		data['sekcii'] = message.text
	await Okna.next()
	user_id = message.from_user.id
	await bot.send_photo(chat_id = user_id, photo = "AgACAgIAAxkBAAIVQmKD37gVnQ7oz9DjLNkOhMVQ6JScAAIKvzEbjmAhSOl9yuCFsCHkAQADAgADeQADJAQ")
	await message.reply(
		"Балконное остекление от пола или от пояса? \n Пример слева от пояса, пример справа от пола",
		reply_markup=ReplyKeyboardMarkup(
			keyboard=[
				[
					KeyboardButton(text="От пола"),
					KeyboardButton(text="От пояса"),
				]
			],
			resize_keyboard=True,
			one_time_keyboard=True,
		)
	)


@dp.message_handler(state=Okna.tip_ostekleniya)
async def vibor_tipa(message: types.Message, state=Okna.tip_ostekleniya):
	async with state.proxy() as data:
		data['tip_ostekleniya'] = message.text
	await Okna.next()
	await message.reply(
		"Есть ли балконный блок?",
		reply_markup=ReplyKeyboardMarkup(
			keyboard=[
				[
					KeyboardButton(text="Нет (мыть не требуется)"),
					KeyboardButton(text="Только дверь"),
					KeyboardButton(text="Дверь с окном"),
				]
			],
			resize_keyboard=True,
			one_time_keyboard=True,
		)
	)

		
@dp.message_handler(state=Okna.blok)
async def vibor_tipa(message: types.Message, state=Okna.blok):
    async with state.proxy() as data:
        data['blok'] = message.text
    await Okna.next()
    if data['tip_uslugi'] == "Мойка балкона":
        await message.reply('Для более точного определения стоимости пришлите пожалуйста фотографии секций балкона')
    elif data['tip_uslugi'] == "Мойка окон и балкона":
        await message.reply('Для более точного определения стоимости пришлите пожалуйста фотографии окон и секций балкона')


@dp.message_handler(MediaGroupFilter(), content_types=["photo", "text"], state=Okna.foto)
@media_group_handler
async def album_handler(messages: Tuple[types.Message], state=Okna.foto):
    async with state.proxy() as data:
        data['media'] = types.MediaGroup()
        for message in messages:
            file_id = message.photo[-1].file_id
            data['media'].attach_photo(file_id)
    await Okna.next()
    await message.reply('Введите Ваш номер телефона(+7...)')

@dp.message_handler(content_types=["photo", "text"], state=Okna.foto)	
async def vibor_ploshadi(message: types.Message, state=Okna.foto):
	async with state.proxy() as data:
		data['media'] = types.MediaGroup()
		file_id = message.photo[-1].file_id
		data['media'].attach_photo(file_id)
	await Okna.next()
	await message.reply('Введите Ваш номер телефона(+7...)')
	
@dp.message_handler(content_types=["text"], state=Okna.phone)
async def vibor_ploshadi(message: types.Message, state=Okna.phone):
    async with state.proxy() as data:
        data['phone'] = message.text
    await Okna.next()
    await message.reply(
        'Оставляли ли Вы у нас заявку ранее? (Если адрес или тип оплаты с момента последней заявки изменился выберите ответ "Нет")',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Да"),
                    KeyboardButton(text="Нет"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )
	
@dp.message_handler(content_types=["text"], state=Okna.proverka)
async def vibor_ploshadi(message: types.Message, state=Okna.proverka):
	async with state.proxy() as data:
		data['proverka'] = message.text
		if data['proverka'].lower() == "да":
			await Okna.komment.set()
			await message.reply('Если есть какая то дополнительная информация, то укажите ее')
		elif data['proverka'].lower() == "нет":
			await Okna.next()
			await message.reply('Укажите Ваше имя')

@dp.message_handler(content_types=["text"], state=Okna.name)
async def vibor_ploshadi(message: types.Message, state=Uborka.name):
	async with state.proxy() as data:
		data['name'] = message.text
	await Okna.next()
	await message.reply(
		"Выберите тип оплаты",
		reply_markup=ReplyKeyboardMarkup(
			keyboard=[
				[
					KeyboardButton(text="Как физическое лицо"),
					KeyboardButton(text="Как юридическое лицо"),
				]
			],
			resize_keyboard=True,
			one_time_keyboard=True,
		)
	)

@dp.message_handler(content_types=["text"], state=Okna.tip_oplati)
async def vibor_ploshadi(message: types.Message, state=Okna.tip_oplati):
    async with state.proxy() as data:
        data['tip_oplati'] = message.text
        if data['tip_oplati'] == "Как юридическое лицо":
            await Okna.next()
            await message.reply('Укажите реквизиты для выставления счета')
        elif data['tip_oplati'] == "Как физическое лицо":
            await Okna.adres.set()
            await message.reply('Укажите Ваш адрес')


@dp.message_handler(content_types=["text"], state=Okna.rekviziti)
async def vibor_ploshadi(message: types.Message, state=Okna.rekviziti):
    async with state.proxy() as data:
        data['rekviziti'] = message.text
    await Okna.next()
    await message.reply('Укажите Ваш адрес')
	
@dp.message_handler(content_types=["text"], state=Okna.adres)
async def vibor_ploshadi(message: types.Message, state=Okna.adres):
    async with state.proxy() as data:
        data['adres'] = message.text
    await Okna.next()
    await message.reply('Если есть какая то дополнительная информация, то укажите ее')

@dp.message_handler(content_types=["text"], state=Okna.komment)
async def vibor_ploshadi(message: types.Message, state=Okna.komment):
	chat = message.chat.id
	async with state.proxy() as data:
		data['komment'] = message.text
	async with state.proxy() as data:
		if data['proverka'].lower() == 'нет':
			if data['tip_uslugi'] == "Мойка окон":
				zakaz2 = 'Услуга: ' + data['tip_uslugi'] + '\n' + 'Род загрязнения:  ' + data['rod_zagryazneniya'] + '\n' + 'Количество окон:  ' + data['kolichestvo_okon'] + '\n'
			elif data['tip_uslugi'] == "Мойка балкона":
				zakaz2 = 'Услуга: ' + data['tip_uslugi'] + '\n' + 'Род загрязнения:  ' + data['rod_zagryazneniya'] + '\n' + 'Количество секций балкона:  ' + data['sekcii'] + '\n' + 'Тип остекления балкона:  ' + data['tip_ostekleniya'] + '\n' + 'Балконный блок: ' + data['blok'] + '\n'
			elif data['tip_uslugi'] == "Мойка окон и балкона":
				zakaz2 = 'Услуга: ' + data['tip_uslugi'] + '\n' + 'Род загрязнения:  ' + data['rod_zagryazneniya'] + '\n' + 'Количество окон:  ' + data['kolichestvo_okon'] + '\n' + 'Количество секций балкона:  ' + data['sekcii'] + '\n' + 'Тип остекления балкона:  ' + data['tip_ostekleniya'] + '\n'+ 'Балконный блок: ' + data['blok'] + '\n'
			if data['tip_oplati'] == "Как юридическое лицо":
				zakaz3 = zakaz2 + 'Тип оплаты: ' + data['tip_oplati'] + 'Реквизиты: ' + data['rekviziti'] + '\n' + 'Номер телефона:  ' + data['phone'] + '\n' +  'Имя:  ' + data['name'] + '\n' + 'Тип оплаты: ' + data['tip_oplati'] + '\n' + 'Адрес и контакты: ' + data['adres'] + '\n' + 'Комментарий:  ' + data['komment'] + '\n' + "Фотографии :"
			elif data['tip_oplati'] == "Как физическое лицо":
				zakaz3 = zakaz2 + 'Тип оплаты: ' + data['tip_oplati'] + '\n' + 'Номер телефона:  ' + data['phone'] + '\n' +  'Имя:  ' + data['name'] + '\n' + 'Тип оплаты: ' + data['tip_oplati'] + '\n' + 'Адрес и контакты: ' + data['adres'] + '\n' + 'Комментарий:  ' + data['komment'] + '\n' + "Фотографии :"
		elif data['proverka'].lower() == 'да':
			if data['tip_uslugi'] == "Мойка окон":
				zakaz3 = 'Услуга: ' + data['tip_uslugi'] + '\n' + 'Род загрязнения:  ' + data['rod_zagryazneniya'] + '\n' + 'Количество окон:  ' + data['kolichestvo_okon'] + '\n' + "Фотографии :"
			elif data['tip_uslugi'] == "Мойка балкона":
				zakaz3 = 'Услуга: ' + data['tip_uslugi'] + '\n' + 'Род загрязнения:  ' + data['rod_zagryazneniya'] + '\n' + 'Количество секций балкона:  ' + data['sekcii'] + '\n' + 'Тип остекления балкона:  ' + data['tip_ostekleniya'] + '\n' + 'Балконный блок: ' + data['blok'] + '\n' + "Фотографии :"
			elif data['tip_uslugi'] == "Мойка окон и балкона":
				zakaz3 = 'Услуга: ' + data['tip_uslugi'] + '\n' + 'Род загрязнения:  ' + data['rod_zagryazneniya'] + '\n' + 'Количество окон:  ' + data['kolichestvo_okon'] + '\n' + 'Количество секций балкона:  ' + data['sekcii'] + '\n' + 'Тип остекления балкона:  ' + data['tip_ostekleniya'] + '\n' + 'Балконный блок: ' + data['blok'] + '\n' + "Фотографии :"
		await bot.send_message(chat_id=admin, text=zakaz3)
		await bot.send_media_group(chat_id=admin, media=data['media'])
		await message.reply(
			"Ваша заявка принята",
			reply_markup=ReplyKeyboardMarkup(
				keyboard=[
					[
						KeyboardButton(text="Вернутся в начало"),
					]
				],
				resize_keyboard=True,
				one_time_keyboard=True,
			)
		)
	connect = sqlite3.connect(database)
	cursor = connect.cursor()
	people_id = message.chat.id
	cursor.execute(f"SELECT user_id FROM main WHERE user_id = {people_id}")
	info = cursor.fetchone()
	if info is None:
		async with state.proxy() as data:
			user_phone = data['phone']
			user_name = data['name']
			user_id = message.chat.id
			user_active = 0
			cursor.execute("INSERT INTO main(user_id,user_name,user_phone,user_active) VALUES(?,?,?,?)", (user_id, user_name, user_phone, user_active))
			connect.commit()
	await state.finish()


@dp.message_handler(lambda msg: msg.text == "Химическая чистка мягкой мебели", state=None)
async def cm_start(message: types.Message):
	await Chimchistka.rod_zagryazneniya.set()
	await message.reply(
	'Выберите все типы загрязнения мебели (можно выбрать несколько, после выбора всех типов нажмите "Далее"',
	reply_markup=ReplyKeyboardMarkup(
		keyboard=[
			[
				KeyboardButton(text="Бытовые (напитки, еда, масло, алкоголь)"),
				KeyboardButton(text="Кровь, красное вино"),
				KeyboardButton(text="Строительные (краска, строительная пыль)"),
			],
			[
				KeyboardButton(text="Домашние животные (моча, уличная грязь)"),
				KeyboardButton(text="После пожара"),
			],
			[
				KeyboardButton(text="Далее"),
			]
		],
		resize_keyboard=True,
		)
	)

@dp.message_handler(state=Chimchistka.rod_zagryazneniya)
async def vibor_tipa(message: types.Message, state=Chimchistka.rod_zagryazneniya):
	async with state.proxy() as data:
		if 'rod_zagryazneniya' not in data.keys():
			data['rod_zagryazneniya'] = []
		if message.text.lower() != "далее":
			data['rod_zagryazneniya'].append(message.text)
			await Chimchistka.rod_zagryazneniya.set()
		else:
			await Chimchistka.next()
			await message.reply('Перечислите и укажите количество мебели, которую необходимо почистить', reply_markup=ReplyKeyboardRemove())
		
@dp.message_handler(state=Chimchistka.predmet_mebeli)
async def vibor_tipa(message: types.Message, state=Chimchistka.predmet_mebeli):
    async with state.proxy() as data:
        data['predmet_mebeli'] = message.text
    await Chimchistka.next()
    await message.reply(
        "Нуждается ли диван в чистке?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Да"),
                    KeyboardButton(text="Нет"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )


@dp.message_handler(state=Chimchistka.vopros_divan)
async def vibor_tipa(message: types.Message, state=Chimchistka.vopros_divan):
	async with state.proxy() as data:
		data['vopros_divan'] = message.text
		if data['vopros_divan'] == "Да":
			await Chimchistka.next()
			await message.reply(
	'Выберите все типы загрязнения мебели (можно выбрать несколько, после выбора всех типов нажмите "Далее"',
	reply_markup=ReplyKeyboardMarkup(
		keyboard=[
			[
				KeyboardButton(text="Угловой (три)"),
				KeyboardButton(text="Угловой с выдвижным спальным местом"),
				KeyboardButton(text="Кухоный уголок"),
			],
			[
				KeyboardButton(text="Прямой (2)"),
				KeyboardButton(text="Прямой (3)"),
				KeyboardButton(text="Прямой (4)"),
			],
			[
				KeyboardButton(text="Прямой (4+)"),
				KeyboardButton(text="Прямой-книжка (2)"),
			]
		],
		resize_keyboard=True,
		one_time_keyboard=True,
		)
	)
		elif data['vopros_divan'] == "Нет":
			await Chimchistka.kolichestvo_podushek.set()
			await message.reply('Укажите количество подушек')


@dp.message_handler(state=Chimchistka.kolichestvo_mest)
async def vibor_tipa(message: types.Message, state=Chimchistka.kolichestvo_mest):
    async with state.proxy() as data:
        data['kolichestvo_mest'] = message.text
    await Chimchistka.next()
    await message.reply('Необходимо ли чистить выкатное спальное место?')


@dp.message_handler(state=Chimchistka.vikatnoye)
async def vibor_tipa(message: types.Message, state=Chimchistka.vikatnoye):
    async with state.proxy() as data:
        data['vikatnoye'] = message.text
    await Chimchistka.next()
    await message.reply('Укажите количество подушек (0 если чистка подушек не требуется)')
	
@dp.message_handler(state=Chimchistka.kolichestvo_podushek)
async def vibor_tipa(message: types.Message, state=Chimchistka.kolichestvo_podushek):
    async with state.proxy() as data:
        data['kolichestvo_podushek'] = message.text
    await Chimchistka.foto_mebeli.set()
    await message.reply('Для более точного определения стоимости пришлите пожалуйста фотографии мебели')

@dp.message_handler(MediaGroupFilter(), content_types=["photo", "text"], state=Chimchistka.foto_mebeli)
@media_group_handler
async def album_handler(messages: Tuple[types.Message], state=Chimchistka.foto_mebeli):
    async with state.proxy() as data:
        data['media'] = types.MediaGroup()
        for message in messages:
            file_id = message.photo[-1].file_id
            data['media'].attach_photo(file_id)
    await Chimchistka.next()
    await message.reply(
        "Выберите тип оплаты",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Как физическое лицо"),
                    KeyboardButton(text="Как юридическое лицо"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )

@dp.message_handler(content_types=["photo", "text"], state=Chimchistka.foto_mebeli)	
async def vibor_ploshadi(message: types.Message, state=Chimchistka.foto_mebeli):
	async with state.proxy() as data:
		data['media'] = types.MediaGroup()
		file_id = message.photo[-1].file_id
		data['media'].attach_photo(file_id)
	await Chimchistka.next()
	await message.reply('Введите Ваш номер телефона(+7...)')

@dp.message_handler(content_types=["text"], state=Chimchistka.phone)
async def vibor_ploshadi(message: types.Message, state=Chimchistka.phone):
    async with state.proxy() as data:
        data['phone'] = message.text
    await Chimchistka.next()
    await message.reply(
        'Оставляли ли Вы у нас заявку ранее? (Если адрес или тип оплаты с момента последней заявки изменился выберите ответ "Нет")',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Да"),
                    KeyboardButton(text="Нет"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )
	
@dp.message_handler(content_types=["text"], state=Chimchistka.proverka)
async def vibor_ploshadi(message: types.Message, state=Chimchistka.proverka):
	async with state.proxy() as data:
		data['proverka'] = message.text
		if data['proverka'].lower() == "да":
			await Chimchistka.komment.set()
			await message.reply('Если есть какая то дополнительная информация, то укажите ее')
		elif data['proverka'].lower() == "нет":
			await Chimchistka.next()
			await message.reply('Укажите Ваше имя')

@dp.message_handler(content_types=["text"], state=Chimchistka.name)
async def vibor_ploshadi(message: types.Message, state=Chimchistka.name):
	async with state.proxy() as data:
		data['name'] = message.text
	await Chimchistka.next()
	await message.reply(
		"Выберите тип оплаты",
		reply_markup=ReplyKeyboardMarkup(
			keyboard=[
				[
					KeyboardButton(text="Как физическое лицо"),
					KeyboardButton(text="Как юридическое лицо"),
				]
			],
			resize_keyboard=True,
			one_time_keyboard=True,
		)
	)

@dp.message_handler(content_types=["text"], state=Chimchistka.tip_oplati)
async def vibor_ploshadi(message: types.Message, state=Chimchistka.tip_oplati):
    async with state.proxy() as data:
        data['tip_oplati'] = message.text
        if data['tip_oplati'] == "Как юридическое лицо":
            await Chimchistka.next()
            await message.reply('Укажите реквизиты для выставления счета')
        elif data['tip_oplati'] == "Как физическое лицо":
            await Chimchistka.adres.set()
            await message.reply('Укажите Ваш адрес')


@dp.message_handler(content_types=["text"], state=Chimchistka.rekviziti)
async def vibor_ploshadi(message: types.Message, state=Chimchistka.rekviziti):
    async with state.proxy() as data:
        data['rekviziti'] = message.text
    await Chimchistka.next()
    await message.reply('Укажите Ваш адрес')
	
@dp.message_handler(content_types=["text"], state=Chimchistka.adres)
async def vibor_ploshadi(message: types.Message, state=Chimchistka.adres):
    async with state.proxy() as data:
        data['adres'] = message.text
    await Chimchistka.next()
    await message.reply('Если есть какая то дополнительная информация, то укажите ее')

@dp.message_handler(content_types=["text"], state=Chimchistka.komment)
async def vibor_ploshadi(message: types.Message, state=Chimchistka.komment):
	chat = message.chat.id
	async with state.proxy() as data:
		data['komment'] = message.text
	async with state.proxy() as data:
		if data['proverka'].lower() == 'нет':
			if data['vopros_divan'] == "Да":
				zakaz = 'Услуга: Химическая чистка мягкой мебели \n' + 'Тип загрязнения :' + ', '.join(data['rod_zagryazneniya']) + '\n' + 'Предметы мебели:  ' + data['predmet_mebeli'] + '\n' + 'Количество мест дивана:  ' + data['kolichestvo_mest'] + '\n' + 'Количество подушек:  ' + data['kolichestvo_podushek'] + '\n' + 'Чистить выкатное спально место:  ' + data['vikatnoye'] + '\n'
			elif data['vopros_divan'] == "Нет":
				zakaz = 'Вы выбрали: Химическая чистка мягкой мебели \n' + 'Тип загрязнения :' + ', '.join(data['rod_zagryazneniya']) + '\n' + 'Предметы мебели:  ' + data['predmet_mebeli'] + '\n' + 'Количество подушек:  ' + data['kolichestvo_podushek'] + '\n'
			if data['tip_oplati'] == "Как физическое лицо":
				zakaz2 = zakaz + 'Тип оплаты: ' + data['tip_oplati'] + '\n' + 'Номер телефона:  ' + data['phone'] + '\n' +  'Имя:  ' + data['name'] + '\n' + 'Тип оплаты: ' + data['tip_oplati'] + '\n' + 'Адрес и контакты: ' + data['adres'] + '\n' + 'Комментарий:  ' + data['komment'] + '\n' + "Фотографии :"
			elif data['tip_oplati'] == "Как юридическое лицо":
				zakaz2 = zakaz + 'Тип оплаты: ' + data['tip_oplati'] + '\n' +  'Реквизиты :' + data['rekviziti'] + '\n' + 'Номер телефона:  ' + data['phone'] + '\n' +  'Имя:  ' + data['name'] + '\n' + 'Тип оплаты: ' + data['tip_oplati'] + '\n' + 'Адрес и контакты: ' + data['adres'] + '\n' + 'Комментарий:  ' + data['komment'] + '\n' + "Фотографии :"
		elif data['proverka'].lower() == 'да':
			if data['vopros_divan'] == "Да":
				zakaz2 = 'Услуга: Химическая чистка мягкой мебели \n' + 'Тип загрязнения :' + ', '.join(data['rod_zagryazneniya']) + '\n' + 'Предметы мебели:  ' + data['predmet_mebeli'] + '\n' + 'Количество мест дивана:  ' + data['kolichestvo_mest'] + '\n' + 'Количество подушек:  ' + data['kolichestvo_podushek'] + '\n' + 'Чистить выкатное спально место:  ' + data['vikatnoye'] + '\n' + '\n' + "Фотографии :"
			elif data['vopros_divan'] == "Нет":
				zakaz2 = 'Вы выбрали: Химическая чистка мягкой мебели \n' + 'Тип загрязнения :' + ', '.join(data['rod_zagryazneniya']) + '\n' + 'Предметы мебели:  ' + data['predmet_mebeli'] + '\n' + 'Количество подушек:  ' + data['kolichestvo_podushek'] + '\n' + '\n' + "Фотографии :"
		await bot.send_message(chat_id=admin, text=zakaz2)
		await bot.send_media_group(chat_id=admin, media=data['media'])
		await message.reply(
			"Ваша заявка принята",
			reply_markup=ReplyKeyboardMarkup(
				keyboard=[
					[
						KeyboardButton(text="Вернутся в начало"),
					]
				],
				resize_keyboard=True,
				one_time_keyboard=True,
			)
		)
	connect = sqlite3.connect(database)
	cursor = connect.cursor()
	people_id = message.chat.id
	cursor.execute(f"SELECT user_id FROM main WHERE user_id = {people_id}")
	info = cursor.fetchone()
	if info is None:
		async with state.proxy() as data:
			user_phone = data['phone']
			user_name = data['name']
			user_id = message.chat.id
			user_active = 0
			cursor.execute("INSERT INTO main(user_id,user_name,user_phone,user_active) VALUES(?,?,?,?)", (user_id, user_name, user_phone, user_active))
			connect.commit()
	await state.finish()


@dp.message_handler(state=None)
async def send_welcome(message: types.Message):
    await message.reply("Для начала оформления заявки - введите команду /start")


if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True)  # функция, запускающая прослушку канала на наличие запросов от Telegram, непосредственный запуск бота
