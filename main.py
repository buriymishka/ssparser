import requests
import json
from bs4 import BeautifulSoup
import threading

def set_interval(func, sec, *args):
    def func_wrapper():
        set_interval(func, sec, *args)
        func(*args)

    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def parse():
    url = "https://m.ss.lv/ru/real-estate/flats/riga/all/sell/"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {"id": "main_mtbl"})
    flats = table.findAll('tr')

    flatObj = dict()
    for flat in flats:
        href = flat.find('a')
        title = ''
        price = ''
        place = ''
        area = ''
        type = ''
        link = ''

        if href:
            link = href['href']

        if not link:
            continue

        link = "https://www.ss.lv/" + link
        rawTitle = flat.find('div', {"class": "dmsg"})
        if rawTitle:
            title = rawTitle.text

        rawInfo = flat.find("td", {"class": "omsg"})
        if rawInfo:
            rawPrice = rawInfo.find("b", {"class": "bp"})
            if (rawPrice):
                price = int(rawPrice.text.replace(',', ''))
            rawInfoText = str(rawInfo.decode_contents())
            if rawInfoText:
                infoArr = rawInfoText.split('<br/>')
                if len(infoArr):
                    place = infoArr[1].replace('<b>', '').replace('</b>', '')
                    area = int(infoArr[2].replace('<b>', '').replace('</b>', '').replace(' m2', ''))
                    type = infoArr[3].replace('<b>', '').replace('</b>', '')
        if area < 30:
            continue
        if price < 25000 or price > 50000:
            continue

        flatObj[link] = {
            "title": title,
            "price": str(price) + ' €',
            "place": place,
            "area": area,
            "priceForArea": str(round(price / area, 2)) + ' €/м²',
            "type": type,
            "link": link
        }
    return flatObj


def saveInFile(data):
    file = open('flats.txt', 'w')
    json.dump(data, file)
    file.close()

def readFromFile():
    file = open('flats.txt')
    data = json.load(file)
    file.close()
    return data

bot_token = '1967603615:AAHlfBlriWwgJXuhaniPytwVFmE2huTS1SE'
bot_chatID = '-1001222794525'
def sendToTelegram(data):
    if len(data):
        print('Sending to telegram: ', len(data))
    else:
        print('Nothing to send')
    for key, flat in data.items():
        msg = f"*Цена:* {flat['price']}\n*Цена за квадрат:* {flat['priceForArea']}\n*Район:* {flat['place']}\n*Площадь:* {flat['area']}\n*Тип Дома:* {flat['type']}\n*Ссылка:* {flat['link']}"
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + msg
        requests.get(send_text)

def main():
    print('Parsing started')
    newData = parse()
    oldData = readFromFile()
    newKeys = list(newData.keys())
    oldKeys = list(oldData.keys())
    uniqueKeys = list(set(newKeys) - set(oldKeys))

    needToSend = dict()
    for key in uniqueKeys:
        needToSend[key] = newData[key]
    sendToTelegram(needToSend)
    saveInFile(newData)
    print('Parsing ended')
    print('')

main()
set_interval(main, 180)
