import requests
from bs4 import BeautifulSoup
import csv
from fake_useragent import UserAgent  # импортируем все нужные библиотеки
from colorama import *
init()

# пишем все важные константы
UA = UserAgent()
URL = 'https://far-aerf.ru/chleny-associacii-2'
HEADERS = {
    'user-agent':str(UA.chrome),    # здесь мы будем пробрасывать случайный юзер-агент, чтобы сайт нас не заблочил
    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'    # тоже нужно, чтобы сайт нас не заблочил
}


def get_html(url):    # создаём функцию, чтобы вызывать запросы
    r = requests.get(url, headers=HEADERS)   # как раз здесь прокидываем всё что нам нужно через параметры функции get
    return r   # возвращаем ответ от сервера

def get_info(html):    # создаём функцию, которая делают всю основную работу : собирает теги и из тегов то что нам надо для дальнейшего занесения в таблицу
    soup = BeautifulSoup(html, 'html.parser')
    infoes = soup.find_all('div', class_='list-names-item')    # находим теги все теги, которые будут нам нужны
    data = []   # создаю список в который потом будем складывать все значения
    n = 0    # переменная для счёта визиток, которые мы спарсили

# Сразу напишу, это функция сортирует данные, мы вкладываем в неё тег, а она оринтируясь по этому тегу
# забирает из него информацию. Эта функция нединамическая, и предназаначена только для этого
# сайта. Вот.

    def sort_data(div):
        # проверка на тип: список это или нет
        if type(div) != list:
            # проверяет нашла ли тег библиотека, если нет выводит 'Not Data'
            if (div == None) or (div.get_text() == ''):
                return 'Not data'
            else:
                # тут тоже только специально с тегом a, так как структура сайта, очень коварная
                # и приходилось изворачивоться и писать много условий
                if div.find('a') != None:
                    return div.find('a').get_text()
                else:
                    # тут мы уже выводи результат
                    return div.get_text()
        else:
            # если всё таки это был список, проверяет не пустой ли он
            # срез тут нужен так как больше двух тегов на сайте нету
            if div[0:2] == []:
                return 'Not Data'
            # проверят сайт ли это или же нет, проверка идёт через поиск в строке,
            # но тут уж ничего не подлеаешь, повторюсь сайт неординаре в этом плане
            elif div[0].get_text().find('www') != -1:
                return div[0].get_text()
            else:
                # тут он проверяет длину, для того чтобы вывести "Not Data"
                # Почему? Потому что в этом теге всего два тега a, и поэтому
                # если прошлое условие проверило, что этот тег нам не подходит
                # то сейчас мы его просто выкидываем
                if len(div) == 1:
                    return 'Not Data'
                # а если же длина не одна то тогда мы выводим второй, потому что
                # первый мы уже проверили в elif
                else:
                    return div[1].get_text()

    # та же фунцкия только для чисел
    def sort_number(num, mobile=None):
        # проверяем существует ли вообще тег
        if num == None:
            return 'Not Data'
        else:
            # дальше делаем из внтуриклассового списка библиотеки bs4, нормальный питоновский список
            num_list = list(num.find_all('a'))
            # проверяем есть ли вообще в этом списке что-то
            if num_list == []:
                return "Not Data"
            else:
                # тут мы ложим хороший номер в виде строки, обработанный так сказать
                number = num_list[0].get_text().replace(' ', '')
                if mobile:
                    # тут длинное условие, но суть, что надо было сделать так, чтобы в одну колонку были
                    # вложены только номера начинающиеся не на 89,79,+79
                    if (number[:2].find('89') != -1) or (number[:2].find('79') != -1) or (number[:3].find('+79') != -1):
                        return number
                    else:
                        return 'Not Data'
                else:
                    # а вот здесь как раз данные в колонку в которой нужны номера начинающиеся на 89,79,+79
                    if (number[:2].find('89') == -1) or (number[:2].find('79') == -1) or (number[:3].find('+79') == -1):
                        return number
                    else:
                        return 'Not Data'


    for info in infoes: # проходимся итирируемым циклом
        n += 1 # счётчик
        print(Fore.GREEN + Style.BRIGHT + 'Спаршено визиток ' + str(n))
        # данные которые мы будем ложить в data
        one = {
            'Name of Company': sort_data(info.find('a', class_='bl_titl')),
            'Entity type': sort_data(info.find('div', class_='bl_desc')),
            'Address': sort_data(info.find('div', class_='bl_addr')),
            'Email': sort_data(info.find('div', class_='bl_email')),
            'Site': sort_data(list(info.find_all('a', target='_blank'))),
            'phone_1': sort_number((info.find('div', class_='bl_phones')), mobile=False),
            'mobile_1': sort_number((info.find('div', class_='bl_phones')), mobile=True),
        }

        data.append(one)
    return data

# создание csv-файла
def save_info_to_csv(htmls, save_how, name_of_file):
    # специальные условия для сохранения
    if save_how == 1:
        delim = ';'
    elif save_how == 2:
        delim = ','
    else:
        print(Fore.RED + Style.BRIGHT + "Вы ввели не ту цифру, презапустите программу, и попробуйте снова :)")
    # сохранение файла
    with open(name_of_file+".CSV", 'w', newline='') as file:
        writer = csv.writer(file, delimiter=delim)
        # создание первой заглавной колонки
        writer.writerow(['Name of Company', 'Entity type', 'Address', 'Email',
                         'Site', 'phone_1', 'mobile_1'])
        # проходимся циклом и содзаём много строк
        for html in htmls:
            writer.writerow([ html['Name of Company'], html['Entity type'],
                             html['Address'], html['Email'], html['Site'],
                             html['phone_1'], html['mobile_1'] ])

# функция, которая вызывает все функции
def general_call(url, save=None, name_of_file_saved=None):
    text = get_html(url)
    # если ответ запроса хороший, то выводим дальше, а так вывыодит "Ошибка!!!!!!"
    if text.ok:
        global_data = get_info(text.text)
        save_info_to_csv(global_data, save, name_of_file_saved)
    else:
        print('\033[31m {}'.format('Ошибка!!!!!!'))

# ну и стаднартное условие
if __name__ == '__main__':
    # чутка марафета
    print(Fore.MAGENTA + Style.BRIGHT + "Как вы хотите сохранить файл: 1 - Excel; 2 - Другое")
    name = int(input())
    print(Fore.CYAN + Style.BRIGHT + "Как вы хотите назвать файл:")
    name_saved = str(input())
    # вызов главной функции
    general_call(URL, save=name, name_of_file_saved=name_saved)
