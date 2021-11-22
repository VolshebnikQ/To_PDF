#  Это было нужно для того чтобы импользовать внутреннею память приложеня (Оставил рудимент)
#import json
#from django.core.files import storage
#from django.http import JsonResponse
#from requests.exceptions import URLRequired
#from django.core.files.storage import FileSystemStorage
#from .models import *
#import json


from django.shortcuts import render
from django.views.generic import View
import requests
import pathlib

from random import randint
import random
import yadisk


#  Токен Яндекс.Диска, для того чтобы работать с файлами облачного серфиса, что на мой взгляд интереснее
yandexTOKEN = "AQAAAAATFRfsAAeDdPOX1KePGEz3h2JOmPtD2MI"

#  Словарь для генерации идентификационного ключа файла на сервере onlyoffice
keys_alphabet = '''
        1,2,3,4,5,6,7,8,9,0,
        q,w,e,r,t,y,u,i,o,p,
        a,s,d,f,g,h,j,k,l,z,
        x,c,v,b,n,m,Q,W,E,R,
        T,Y,U,I,O,P,A,S,D,F,
        G,H,J,K,L,Z,X,C,V,B,
        N,M
        '''
typesd = 'doc.docm.docx.dot.dotm.dotx.epub.fb2.fodt.html.mht.odt.ott.oxps.rtf.txt.xps.xml'
typess = 'csv.fods.ods.ots.xls.xlsm.xlsx.xlt.xltm.xltx'
typesp = 'fodp.odp.otp.pot.potm.potx.pps.ppsm.ppsx.ppt.pptm.pptx'


#  Класс загружающий страницу
class Index(View):

    #  Загрузка страницы при обычной загрузки
    def get(self, request, *args, **kwargs):
        return render(request, 'index/index.html')

    #  Загрузка страницы при отправки на сервер файла для конвертации
    def post(self, request, *args, **kwargs):
        if request.method == 'POST' and request.FILES:
            #  Активация Яндекс.Диск
            y = yadisk.YaDisk(token=yandexTOKEN)
            #  Удаление всех фалов в дириктории приложения
            clear_YaDisk(list(y.listdir("/topdf/")))

            #  Получения файла со стриницы index.html
            file = request.FILES['myfile']

            #  Создание пути файла в дириктории и загрузка файла в облако
            path = "/topdf/" + file.name
            y.upload(file, path)

            #  Повторная активация Яндекс.Диск, чтобы обновить содержание облака
            y = yadisk.YaDisk(token=yandexTOKEN)
            storagelist = list(y.listdir("/topdf/"))

            filename = storagelist[0].name
            fileurl = storagelist[0].file
            filetype = pathlib.Path(filename).suffix[1:]
            format = get_formatfile(filetype)
            key = key_gen()

            #  Проверка на подходящее расширение файл
            if format == 0:
                return render(
                    request,
                    'index/index.html',
                    {
                        'file_url': "#", 'api': "#", 'url_pdffile': "#",
                        'text': 'Расширение файла не подходит'
                    })

            #  Создание json запроса
            apitopdf = Api(format, fileurl, filename, filetype, key)
            #  Выполнение json запроса
            api = requests.get(apitopdf)

            #  Получение ссылки на конвертированный файл
            url_pdffile = geturl(api)

            return render(
                request,
                'index/index.html',
                {
                    'fileurl': fileurl, 'api': apitopdf,
                    'url_pdffile': url_pdffile, 'text': ''
                })


#  Генерация json запроса
def Api(format, file_url, title, filetype, key):

    #  Адрес сервера
    url = 'http://localhost/ConvertService.ashx/'

    #  API для получения pdf файла из файлов формата текста или презентации
    if format == "text" or format == "presentation":
        payload = {
            'async': 'false',
            'filetype': filetype,
            "key": key,
            'outputtype': 'pdf',
            'title': title,
            'url': file_url
        }
    #  API для получения pdf файла из файлов формата таблицы
    elif format == "spreadsheet":
        payload = {
            "filetype": filetype,
            "key": key,
            "outputtype": "pdf",
            "region": "en-US",
            "spreadsheetLayout": {
                "ignorePrintArea": "true",
                "orientation": "portrait",
                "fitToWidth": 0,
                "fitToHeight": 0,
                "scale": 100,
                "headings": "false",
                "gridLines": "false",
                "pageSize": {
                    "width": "210mm",
                    "height": "297mm"
                },
                "margins": {
                    "left": "17.8mm",
                    "right": "17.8mm",
                    "top": "19.1mm",
                    "bottom": "19.1mm"
                }
            },
            "title": title,
            "url": file_url
        }
    else:
        return 0

    response = requests.post(url, params=payload)

    return response.url


#  Почему-то эта конструкция "requests.get" добавляет 'amp;' в ссылку,
#  после чего ссылку не принемает сервер
#  Так что эта функция выделяет ссылку из всего файла,
#  полученного с сервера onlyoffice и удаляет не нужные подстроки
def geturl(api):
    start_url = api.text.find('<FileUrl>')
    end_url = api.text.find('</FileUrl>')
    link = api.text[start_url+9:end_url]
    clear_link = ''
    for s in link.split('amp;'):
        clear_link = clear_link + s
    return clear_link


#  Очистка дириктории Яндекс.Диск
def clear_YaDisk(storagelist):
    y = yadisk.YaDisk(token=yandexTOKEN)
    if len(storagelist) > 0:
        for elemetn in storagelist:
            path = "/topdf/" + elemetn.name
            y.remove(path, permanently=True)


#  Генератор идентификационных ключей для файлов
def key_gen():
    key = ""
    for e in range(randint(8, 16)):
        s = random.choice(keys_alphabet.replace("\n        ", "").split(","))
        key = key + s
    return key


#  Функция определения формата файла
#  Если файл не соответсвует ни одному расширению, то выводится сообщение об этом
def get_formatfile(filetype):
    if typesd.find(filetype) != -1:
        format = "text"
    elif typess.find(filetype) != -1:
        format = "spreadsheet"
    elif typesp.find(filetype) != -1:
        format = "presentation"
    else:
        format = 0
    return format
