import re

import selenium.common.exceptions
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


results = {}
urls = ['https://hands.ru/company/about/', 'https://repetitors.info/', 'https://webim.ru/about/']
# urls = ['https://pizzafabrika.ru/tolyatti/company/about.html']
phone_mask = re.compile(r'(?<!\d)((\+?[7-8] ?\(?[0-9]+\)? ?[0-9]{3}[- ]?[0-9]{2}[- ]?[0-9]{2})|([0-9]{2}[- ]?[0-9]{2}[- ]?[0-9]{2}))')
tag_mask = re.compile(r'phone|number|tel')


def phone_finder(url: str) -> list[str]:
    phones = []
    clickable = []

    browser = webdriver.Chrome()
    browser.get(url)
    page = browser.page_source
    soup = BeautifulSoup(page, "html.parser")

    soup = soup.find_all(class_=tag_mask)
    for tag in soup:
        tag_class = tag.get('class')
        if tag_class:
            tag_class = [s for s in tag_class if tag_mask.search(s)]

        tag_id = tag.get('id')
        if tag_id:
            tag_id = [s for s in tag_id if tag_mask.search(s)]

        link = tag.get('href')
        if not link:
            clickable.append((tag_class, tag_id))

    for tag_class, tag_id in clickable:
        if tag_id:
            elements = browser.find_elements(By.ID, tag_id[0])
        else:
            elements = browser.find_elements(By.CLASS_NAME, tag_class[0])

        for e in elements:
            try:
                e.click()
            except selenium.common.exceptions.ElementNotInteractableException:
                continue

    page = browser.page_source
    soup = BeautifulSoup(page, "html.parser")
    phones += soup.find_all(string=phone_mask)

    browser.quit()

    return phones


def worker(phone: str) -> str:
    phone = re.sub(r' |-|\(|\)', '', phone)
    phone = re.sub(r'\+7', '8', phone)
    if len(phone) == 6:
        phone = '8495' + phone
    return phone


def main():
    for url in urls:
        phones = phone_finder(url)
        phones = list(map(worker, phones))
        phones = list(filter(lambda x: len(x) <= 11, phones))
        results[url] = phones

    print(results)


if __name__ == '__main__':
    main()
    # nums = ['8 (495) 540-56-76', '8 (495) 540-56-76', '8 495 540 56 76', '+74955405676', '84955405676',
    #         '44 50 40', '445040', '44-50-40', '4450 40', '44 5040', '44 50-40']
    # print(list(map(worker, nums)))

