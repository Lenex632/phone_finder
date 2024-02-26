import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException, ElementClickInterceptedException

# регулярка для телефонных масок
phone_mask = re.compile(r'(?<!\d)((\+?[7-8] ?\(?[0-9]+\)? ?[0-9]{3}[- ]?[0-9]{2}[- ]?[0-9]{2})|([0-9]{2}[- ]?[0-9]{2}[- ]?[0-9]{2}))')
# регулярка для поиска на странице нужных class и id
tag_mask = re.compile(r'phone|number|tel')


def phone_finder(url: str) -> list[str]:
    phones = []
    clickable = []

    # открываем страницу, парсим в BeautifulSoup
    browser = webdriver.Chrome()
    browser.get(url)
    page = browser.page_source
    soup = BeautifulSoup(page, "html.parser")

    # находим теги с id и class в которых могут содержаться телефоны
    tags = soup.find_all(class_=tag_mask)
    tags += soup.find_all(id=tag_mask)
    # ищем среди найденных тегов кликаемые, что бы увидеть скрытые телефоны
    for tag in tags:
        tag_class = tag.get('class')
        if tag_class:
            tag_class = [s for s in tag_class if tag_mask.search(s)]

        tag_id = tag.get('id')
        if tag_id:
            tag_id = [s for s in tag_id if tag_mask.search(s)]

        # отсекаем хотя бы те, которые точно являются ссылками
        link = tag.get('href')
        if not link:
            clickable.append((tag_class, tag_id))

    # кликаем на все кликаемые элементы
    for tag_class, tag_id in clickable:
        if tag_id:
            elements = browser.find_elements(By.ID, tag_id[0])
        else:
            elements = browser.find_elements(By.CLASS_NAME, tag_class[0])

        for e in elements:
            try:
                e.click()
            # если элемент некликабельный - пропускаем его
            except ElementNotInteractableException:
                continue
            # если клик на какой-то элемент ограничил доступ к клику на другой - прерываем, что бы не возникла каша
            except ElementClickInterceptedException:
                break

    # загружаем обновлённую страничку в BeautifulSoup, и ищем там номера по маске в обычных строках
    page = browser.page_source
    soup = BeautifulSoup(page, "html.parser")
    phones += soup.find_all(string=phone_mask)

    browser.quit()

    return phones


def worker(phone: str) -> str:
    # приводим номер к формату 8KKKNNNNNNN
    phone = re.sub(r' |-|\(|\)|\n', '', phone)
    phone = re.sub(r'\+7', '8', phone)
    if len(phone) == 6:
        phone = '8495' + phone
    return phone


def find_phones(urls: list[str]) -> dict[str: list[str]]:
    results = {}
    for url in urls:
        phones = phone_finder(url)
        phones = list(map(worker, phones))
        phones = list(filter(lambda x: len(x) <= 11, phones))
        results[url] = phones

    return results


if __name__ == '__main__':
    urls = ['https://hands.ru/company/about/', 'https://repetitors.info/']
    print(find_phones(urls))
    # nums = ['8 (495) 540-56-76', '8 (495) 540-56-76', '8 495 540 56 76', '+74955405676', '84955405676',
    #         '44 50 40', '445040', '44-50-40', '4450 40', '44 5040', '44 50-40']
    # print(list(map(worker, nums)))

