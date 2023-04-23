from telebot import types
import time
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from telebot.types import Update
import telebot
from .models import User
from django.shortcuts import render, redirect
from .forms import UserForm



bot = telebot.TeleBot(settings.TOKEN)



def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Дополнительные действия после успешной регистрации
            return redirect('registration')
    else:
        form = UserForm()

    return render(request, 'chatbot/registration.html', {'form': form})


def restricted_access(func):
    'Декор, для проверки пользователя'
    def wrapper(message):
        user_id = message.from_user.id
        if not User.objects.filter(telegram_id=user_id).exists():
            bot.send_message(chat_id=message.chat.id, text='Доступ запрещен')
            return
        return func(message)
    return wrapper


@csrf_exempt
def index(request):
    if request.method == "POST":
        update = Update.de_json(request.body.decode('utf-8'))
        bot.process_new_updates([update])
    return render(request, 'chatbot/registration.html', {'title':'Registration form'})

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not hasattr(bot, 'user_context'):
        bot.user_context = {}
    if user_id not in bot.user_context:
        bot.user_context[user_id] = {
            'index': 0
        }
    print(bot.user_context)
    bot.send_message(message.chat.id, 'Привет! Я бот. Как я могу тебе помочь?')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('💊 ОС')
    item2 = types.KeyboardButton('🖇 МЦ')
    item3 = types.KeyboardButton('🗿 АРЕНДА')
    item4 = types.KeyboardButton('🔎 Поиск по названию')
    item5 = types.KeyboardButton('🤔 FAQ')
    item6 = types.KeyboardButton('🖥 Компьютерная техника')

    markup.add(item1, item2, item3, item4, item5, item6, row_width=2)

    bot.send_message(message.chat.id, f'Приветствую вас, {message.from_user.first_name}')
    time.sleep(1)
    bot.send_message(message.chat.id, 'Буду рад помочь вам разобраться в вашем отчете МОЛ')
    time.sleep(1)
    bot.send_message(message.chat.id, 'После добавления вашего id в базу данных вы сможете использовать бот')
    time.sleep(1)
    bot.send_message(message.chat.id, 'У вас появились кнопки меню, где вы сможете выбирать интересующую вас категорию',reply_markup=markup)

user_id = [740586983,975863525,211600094]

text = 'Тестовое приветствие'


@bot.message_handler(content_types=['text'])
@restricted_access
def bot_messege(message):
    if message.chat.type == 'private':
        if message.text in buttons_constants:
            add_buttons(message.text, message.chat.id)
        elif message.text in constants:
            bot.send_message(message.chat.id, 'Сейчас появится список фотографий с наименованиями:')
            yyy(message.text, message, True)
        elif message.text == '🤔 FAQ':
            yyy("DOCUMENT", message, True)
        elif message.text == 'message':
            for kot in user_id:
                bot.send_message(chat_id=kot,text=text)

        else:
            matchFound = False
            for x in searchByNameDictionary:
                if message.text.lower() in x:
                    bot.send_photo(message.chat.id, open(searchByNameDictionary[x]['photo'], 'rb'))
                    bot.send_message(message.chat.id, searchByNameDictionary[x]['name'])
                    matchFound = True
            if not matchFound:
                bot.send_message(message.chat.id, 'По вашему запросу ничего не найдено')

def yyy (category_name, message, reset):
    object = constants[category_name]
    items = object["items"]
    if reset:
        bot.user_context[message.chat.id]["index"] = 0
    idx = bot.user_context[message.chat.id]["index"]
    item = items[idx]
    msg = item["name"]
    if "photos" in item:
        photos = item["photos"]
        for photo in photos:
             bot.send_photo(message.chat.id, open(photo, 'rb'))
        bot.send_message(message.chat.id, msg)
    if "documents" in item:
        documents = item["documents"]
        for document in documents:
             bot.send_message(message.chat.id, msg)
        bot.send_document(message.chat.id, open(document, 'rb'))
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('◄ ', callback_data='previous')
    item2 = types.InlineKeyboardButton('► ', callback_data='next')
    listic = []
    if idx != 0:
        listic.append(item1)
    if idx != len(items)-1:
        listic.append(item2)
    markup.add(*listic)

    bot.send_message(message.chat.id, 'OIOS', reply_markup=markup)
    bot.user_context[message.chat.id]["index"] = items.index(item)
    bot.user_context[message.chat.id]["category"] = category_name

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "previous":
        bot.user_context[call.message.chat.id]["index"] = bot.user_context[call.message.chat.id]["index"] - 1
        yyy(bot.user_context[call.message.chat.id]["category"], call.message, False)
    elif call.data == "next":
        bot.user_context[call.message.chat.id]["index"] = bot.user_context[call.message.chat.id]["index"]+ 1
        yyy(bot.user_context[call.message.chat.id]["category"] , call.message, False)

def add_buttons(text, chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    for i in buttons_constants[text]['buttons']:
        buttons.append(types.KeyboardButton(i))
    markup.add(*buttons)
    bot.send_message(chat_id, buttons_constants[text]['message_text'], reply_markup=markup)

searchByNameDictionary = {
    'тумба, тумбы, подиум для выкладки товаров, тумба 4 доски, тумба четыре доски, тумба 1260*880*590, 4 доски)': {
        'photo': 'D:\бот\ЗАЛ\тумбае.jpg',
        'name': 'Подиум для выкладки и демонстрации товаров 4, "1260мм*880мм*590мм" (тумба 4 доски)'
    },
    'тумба металлическая, тумба, тумба под весы, весы': {
            'photo': 'D:\бот\ЗАЛ\тумбаб.jpg',
            'name': 'ТУМБА МЕТАЛИЧЕСКАЯ ДЛЯ СЕНСОРНЫХ ВЕСОВ (С РОЛИКОВЫМИ НАПРАВЛЯЮЩИМИ)'
    },
    'тумба 2 доски, тумба, тумба 1200*880*340, тумба две доски, Подиум': {
            'photo': 'D:\бот\ЗАЛ\тумбаг.jpg',
            'name': 'Подиум для выкладки и демонстрации товаров 2, "1260мм*880мм*340мм'
    },
    'тумба 6 досок, тумба, тумба 1260*880*850, тумба шесть досок, ящик 1260*880*850, подиум 1260*880*850, тумба соф, соф': {
            'photo': 'D:\бот\ЗАЛ\тумбад.jpg',
            'name': 'Подиум для выкладки и демонстрации товаров 1, "1260мм*880мм*850мм" (СОФ)'
    },
    'тумба из ЛДСП, конфетница, тумба, тумба прилавок из ЛДСП,тумба 1200*800*860  ': {
            'photo': 'D:\бот\ЗАЛ\тумбаа.jpg',
            'name': 'Тумба-прилавок из ЛДСП с раздел.ячеек из оргстекла 1200*800*860)'
    },
    'тумба профильная, тумба, тумба 1200*800*570, поддон профильный 1200*800*570, ящик 1200*800*570   ': {
            'photo': 'D:\бот\ЗАЛ\тумбах.jpg',
            'name': 'БЛ ПДН ПД КЦ 1200 800 570 ФП Тумба профильная деревянная'
    },
    'тумба под весы, тумба, весы, фасад, с фасадом, тумба с фасадом,тумба 535*700*890 ': {
            'photo': 'D:\бот\ЗАЛ\тумбав.jpg',
            'name': 'ТУМБА 535*700*890 ОРЕХ ЭККО/ДУБ МОЛОЧНЫЙ/ТУМБА ПОД ВЕСЫ С ФАСАДОМ'
    },
    'камера хранения, камера, кхс, сейф для покупателя, шкаф для сумок, сумки ': {
        'photo': 'D:\бот\ЗАЛ\камерс.jpg',
        'name': 'КАМЕРА ХРАНЕНИЯ КХС9,С КРУГЛЫМИ ВСТАВКАМИ'

    },
    'стеллаж для овощей италия, италия, овощи, стеллаж, ': {
        'photo': 'D:\бот\ЗАЛ\камерк.jpg',
        'name': 'СТЕЛЛАЖ ДЛЯ ОВОЩЕЙ, ИТАЛИЯ:'

    },
    'касса самообслуживания, ксо, касса, самообслуживания, кассы ': {
        'photo': 'D:\бот\кассы\касск.jpg',
        'name': 'КАССА САМООБСЛУЖИВАНИЯ Z2 21.5 СО СТОЙКОЙ ZJ28 И КОНТРОЛЬНЫМИ ВЕСАМИ:'

    },
    'касса, касса самообслуживания, ксо, самообслуживания, кассы ': {
        'photo': 'D:\бот\кассы\касскт.jpg',
        'name': 'КАССА САМООБСЛУЖИВАНИЯ НА БАЗЕ ТЕРМИНАЛА  "ТУССОН SST-300R"(КОМПЛЕКТ)'

    },
    'касса, экспресс-касса,экспресс, экспресс касса, кассы  ': {
        'photo': 'D:\бот\кассы\кассн.jpg',
        'name': 'ЭКСПРЕСС-КАССА (7024 ш.п), метал., 9967-533-04 Х5 ЕК 001 00.'

    },
    'касса, кассовый прилавок, прилавок, 750*500*1000, кассы ': {
        'photo': 'D:\бот\кассы\кассе.jpg',
        'name': 'Кассовый прилавок 750 500 1000 (7024 ш.п), метал.'

    },
    'пэвм, системный блок, системный, авакадо, авакадо 100, системник, компьютер ': {
        'photo': 'D:\бот\орг техника\корп.jpg',
        'name': 'СИСТЕМНЫЙ БЛОК АВОКАДО 100'
    },
    ' системный блок,пэвм, системный, атом, системник, компьютер ': {
        'photo': 'D:\бот\орг техника\атом1.jpg',
        'name': 'ПЭВМ "ENERGY" INTEL ATOM 230'

    },
    ' пэвм,системный блок, системный, jet, системник, компьютер,джет ': {
        'photo': 'D:\бот\орг техника\компб.jpg',
        'name': 'ПЭВМ "JET I" CELERON J4105/BIOSTAR J4105NHU/DDR4 2666MHz/КОРПУС MI-207-M300'

    },
    ' максим, пэвм,системный блок, системный, maxima, системник, компьютер, ': {
        'photo': 'D:\бот\орг техника\максим.jpg',
        'name': 'ПЭВМ HAFF МОДЕЛЬ "MAXIMA"'

    },
    'факс, аппарат, факсимальный аппарат, panasonic KX-FT982RU-B, KX-FT982RU-B': {
        'photo': 'D:\бот\орг техника\компт.jpg',
        'name': 'ФАКСИМИЛЬНЫЙ АППАРАТ PANASONIC KX-FT982RU-B'

    },
    'холодильник, холодильники, витрина холодильная, витрина, свитязь, 120П': {
        'photo': 'D:\бот\kaskas.jpg',
        'name': 'ВИТРИНА ХОЛОДИЛЬНАЯ "СВИТЯЗЬ 120 П" ВС-0,67-2,6-1-4Х.'
    },
    'холодильники, холодильник, витрина холодильная, горка холодильная, горка, euro bali': {
        'photo': 'D:\бот\holod1.jpg',
        'name': 'ГОРКА ХОЛОД.EURO BALI D890 H2210 L1250 2 ГЛУХ БОКОВИНЫ'
    },
    'ларь, холодильник, морозильный ларь млп-250, млп,морозильный ': {
        'photo': 'D:\бот\лари бонеты\лар.jpg',
        'name': 'МОРОЗИЛЬНЫЙ ЛАРЬ МЛП-250'
    },
    'холодильник, шкаф, шкаф холодильный, капри, капри 1,5ум': {
        'photo': 'D:\бот\капри1.jpg',
        'name': 'ШКАФ ХОЛОДИЛЬНЫЙ КАПРИ 1,5 УМ'
    },
    'сейф, сейф 65т, 65т, шкаф сейф 65Т': {
        'photo': 'D:\бот\складская мебель\сейфс.jpg',
        'name': 'ШКАФ SL-65T (СЕЙФ)'
    },
    'принтер, зебра, zebra, тлп, tlp2824, принтер штрих-кодов, штрих, 2824': {
        'photo': 'D:\бот\орг техника\принтера\зебра1.jpg',
        'name': 'ПРИНТЕР ШТРИХ-КОДОВ ZEBRA TLP2824'
    },
}
constants = {
         'Холодильные шкафы': {
            "name": "Холодильные шкафы",
            "items": [
                {
                    "name": 'ВИТРИНА ХОЛОДИЛЬНАЯ "СВИТЯЗЬ 120 П" ВС-0,67-2,6-1-4Х.',
                    "photos": [
                        'D:\бот\kaskas.jpg', 'D:\бот\kuskus.jpg'
                    ]
                },
                {
                    "name": 'ГОРКА ХОЛОД.EURO BALI D890 H2210 L1250 2 ГЛУХ БОКОВИНЫ',
                    "photos": [
                        'D:\бот\holod1.jpg', 'D:\бот\holod2.jpg'
                    ]
                },
                {
                    "name": 'ГОРКА ВСТРОЕННЫЙ ХОЛОД ГАСТРОНОМИЧЕСКАЯ Berg 125',
                    "photos": [
                        'D:\бот\holod3.jpg', 'D:\бот\holod4.jpg'
                    ]
                },
                {
                    "name": 'ШКАФ ХОЛОДИЛЬНЫЙ КАПРИ 1,5 УМ',
                    "photos": [
                        'D:\бот\капри1.jpg', 'D:\бот\капри2.jpg'
                    ]
                },
            ]
        },
        'Лари/бонеты': {
            "name": "Лари/бонеты",
            "items": [
                {
                    "index": 0,
                    "name": 'ЛАРЬ-БОНЕТА LEVIN ARCTICA 250 НТ/СТ.',
                    "photos": [
                        'D:\бот\лари бонеты\harctica.jpg', 'D:\бот\лари бонеты\hmb.jpg'
                    ]
                },
                {
                    "index": 1,
                    "name": 'ЛАРЬ-БОНЕТА КОРСИКА ЛХН-2100.',
                    "photos": [
                        'D:\бот\лари бонеты\хар.jpg', 'D:\бот\лари бонеты\хар2.jpg'
                    ]
                },
                {
                    "index": 2,
                    "name": 'МОРОЗИЛЬНЫЙ ЛАРЬ МЛП-250.',
                    "photos": [
                        'D:\бот\лари бонеты\лар.jpg',
                    ]
                },

            ]
        },
        '💶 Кассовое оборудование': {
            "name": "💶 Кассовое оборудование",
            "items": [
                {
                    "name": 'КАССА САМООБСЛУЖИВАНИЯ Z2 21.5 СО СТОЙКОЙ ZJ28 И КОНТРОЛЬНЫМИ ВЕСАМИ.',
                    "photos": [
                        'D:\бот\кассы\касск.jpg',
                    ]
                },
                {
                    "name": 'КАССА САМООБСЛУЖИВАНИЯ НА БАЗЕ ТЕРМИНАЛА  "ТУССОН SST-300R"(КОМПЛЕКТ).',
                    "photos": [
                        'D:\бот\кассы\касскт.jpg',
                    ]
                },
                {
                    "name": 'ЭКСПРЕСС-КАССА (7024 ш.п), метал., 9967-533-04 Х5 ЕК 001 00.',
                    "photos": [
                        'D:\бот\кассы\кассш.jpg', 'D:\бот\кассы\кассн.jpg',
                    ]
                },
                {
                    "name": 'Кассовый прилавок 750 500 1000 (7024 ш.п), метал.',
                    "photos": [
                        'D:\бот\кассы\касси.jpg', 'D:\бот\кассы\кассе.jpg',
                    ]
                },

            ]
        },
        '📦 Торговый зал': {
            "name": "📦 Торговый зал",
            "items": [
                {
                    "name": 'Тумба-прилавок из ЛДСП с раздел.ячеек из оргстекла 1200*800*860)',
                    "photos": [
                        'D:\бот\ЗАЛ\тумбаа.jpg'
                    ]
                },
                {
                    "name": 'Подиум для выкладки и демонстрации товаров 2, "1260мм*880мм*590мм" (тумба четыре доски)',
                    "photos": [
                        'D:\бот\ЗАЛ\тумбае.jpg'
                    ]
                },
                {
                    "name": 'Подиум для выкладки и демонстрации товаров 4, "1260мм*880мм*340мм" (тумба две доски)',
                    "photos": [
                        'D:\бот\ЗАЛ\тумбаг.jpg'
                    ]
                },
                {
                    "name": 'Подиум для выкладки и демонстрации товаров 1, "1260мм*880мм*850мм" (СОФ)',
                    "photos": [
                        'D:\бот\ЗАЛ\тумбад.jpg'
                    ]
                },
                {
                    "name": 'ТУМБА 535*700*890 ОРЕХ ЭККО/ДУБ МОЛОЧНЫЙ/ТУМБА ПОД ВЕСЫ С ФАСАДОМ',
                    "photos": [
                        'D:\бот\ЗАЛ\тумбав.jpg'
                    ]
                },
                {
                    "name": 'ТУМБА МЕТАЛИЧЕСКАЯ ДЛЯ СЕНСОРНЫХ ВЕСОВ (С РОЛИКОВЫМИ НАПРАВЛЯЮЩИМИ)',
                    "photos": [
                        'D:\бот\ЗАЛ\тумбаб.jpg'
                    ]
                },
                {
                    "name": 'БЛ ПДН ПД КЦ 1200 800 570 ФП Тумба профильная деревянная',
                    "photos": [
                        'D:\бот\ЗАЛ\тумбах.jpg', 'D:\бот\ЗАЛ\тумбас.jpg'
                    ]
                },
                {
                    "name": 'КАМЕРА ХРАНЕНИЯ КХС9,С КРУГЛЫМИ ВСТАВКАМИ',
                    "photos": [
                        'D:\бот\ЗАЛ\камерр.jpg', 'D:\бот\ЗАЛ\камерс.jpg'
                    ]
                },
                {
                    "name": 'СТЕЛЛАЖ ДЛЯ ОВОЩЕЙ, ИТАЛИЯ '
                            '\nВыставочный экспонент для фруктов и овощей 1200х1200хН1250мм в стальной краске RAL 7024 '
                            '\nРеклинирующий верхний этаж ЕВЕ120 1000Х650ХН240 мм в стальной краске RAL 7024'
                            '\nРеклинирующий верхний этаж ЕВЕ120 1200Х400ХН210 мм в стальной краске RAL 7024:',
                    "photos": [
                        'D:\бот\ЗАЛ\камерт.jpg', 'D:\бот\ЗАЛ\камерк.jpg'
                    ]
                },

            ]
        },
        'Компьютеры/posbox': {
            "name": "Компьютеры/posbox",
            "items": [
                {
                    "name": 'ПЭВМ "ENERGY" INTEL ATOM 230',
                    "photos": [
                        'D:\бот\орг техника\атом1.jpg', 'D:\бот\орг техника\атом2.jpg',
                    ]
                },
                {
                    "name": 'ПЭВМ "BVK" TY BY 191647183002-2019',
                    "photos": [
                        'D:\бот\орг техника\комр.jpg'
                    ]
                },
                {
                    "name": 'ПЭВМ "JET I" CELERON J4105/BIOSTAR J4105NHU/DDR4 2666MHz/КОРПУС MI-207-M300',
                    "photos": [
                        'D:\бот\орг техника\компб.jpg','D:\бот\орг техника\компз.jpg', 'D:\бот\орг техника\компн.jpg'
                    ]
                },
                {
                    "name": 'СИСТЕМНЫЙ БЛОК АВОКАДО 100',
                    "photos": [
                        'D:\бот\орг техника\корп.jpg','D:\бот\орг техника\корпд.jpg',
                    ]
                },
                {
                    "name": 'ПЭВМ HAFF МОДЕЛЬ "MAXIMA"',
                    "photos": [
                        'D:\бот\орг техника\максим.jpg','D:\бот\орг техника\максим1.jpg',
                    ]
                },
            ]
        },
        '🗜 Мебель (Склад)': {
            "name": "🗜 Мебель (Склад)",
            "items": [
                {
                    "name": 'ФАКСИМИЛЬНЫЙ АППАРАТ PANASONIC KX-FT982RU-B',
                    "photos": [
                        'D:\бот\орг техника\компт.jpg',
                    ]
                },
                {
                    "name": 'ШКАФ SL-65T (СЕЙФ)',
                    "photos": [
                        'D:\бот\складская мебель\сейфс.jpg',
                    ]
                },
            ]
        },
        'Принтеры/МФУ': {
            "name": "Принтеры/МФУ)",
            "items": [
                {
                    "name": 'ПРИНТЕР ШТРИХ-КОДОВ ZEBRA TLP2824',
                    "photos": [
                        'D:\бот\орг техника\принтера\зебра1.jpg','D:\бот\орг техника\принтера\зебра.jpg'
                    ]
                },
            ]
        },
        "DOCUMENT": {
            "name": "🤔 FAQ",
            "items": [
                {
                    "name": 'Примеры служебных записок на списание',
                    "documents": [
                        'D:\работа\списание.xlsx'
                    ]
                }
            ]
        },
        'Сканеры': {
            "name": "Сканеры",
            "items": [
                {
                    "name": 'СКАНЕР ШТРИХ-КОДА NEWLAND FR2780-B-20',
                    "photos": [
                        'D:\бот\орг техника\компс.jpg'
                    ]
                }
            ]
        },

}
buttons_constants = {
    '💊 ОС': {
        'buttons': ['❄ Холодильное оборудование ', '💶 Кассовое оборудование ', '🐄Оборудование СП ', '⬅ Назад'],
        'message_text': 'ОС - Пожалуйста, выберите категорию основных средств'
    },
    '❄ Холодильное оборудование': {
        'buttons': ['Лари/бонеты ', 'Холодильные витрины (пристенные) ', 'Холодильные витрины (прилавки)', '⬅ Назад'],
        'message_text': 'Пожалуйста, выберите категорию Холодильного оборудования'
    },
    '🖇 МЦ':{
        'buttons': ['📦 Торговый зал ', '🗜 Мебель (Склад)', '⬅ Назад'],
        'message_text': 'Пожалуйста, выберите категорию МЦ'
    },
    '🖥Компьютерная техника': {
        'buttons': ['Сканеры ', 'Компьютеры/posbox ', 'Прин-сервера ', 'Принтеры/МФУ ', 'Маршрутезаторы ', '⬅ Назад'],
        'message_text': 'Пожалуйста, выберите категорию МЦ'
    },
    '🗿 АРЕНДА': {
        'buttons': ['Поставщики ', '⬅ Назад'],
        'message_text': 'Осуществлять поиск по поставщику'
    },
    '🔎Поиск по названию': {
        'message_text': 'Введите интересующую вас позицию'
    },
    '⬅ Назад': {
        'buttons': ['💊 ОС ', '🖇 МЦ ', '🗿 АРЕНДА ', '🔎Поиск по названию ', '🤔 FAQ ',  '🖥Компьютерная техника '],
        'message_text': '⬅ Назад'
    }
}

bot.polling(none_stop=True)




