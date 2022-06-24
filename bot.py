import smtplib
from email.message import EmailMessage
from time import sleep

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By

# ebay link that includes search results already by item name / type
ebay_item_link = 'https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2334524.m570.l1311&_nkw=msi+rtx+3090+gaming+x+trio&_sacat=0&LH_TitleDesc=0&_odkw=rtx+3090s&_osacat=0&LH_PrefLoc=2'
# set price range
price_range = range(0, 1000)
# for better item accuracy
product_name_val = 'rtx 3090'
# key words to avoid particular items
product_description_filters = ['broken', 'parts', 'used', 'missing', 'damaged']

# dont remove these / change
potential_products = []
filter_to_apply = ['Buy It Now', 'US Only']
page_navigator = [ebay_item_link]
page_count = 'pagination__items'
product_returned = 's-item__pl-on-bottom'
title_class = 's-item__title'
price_class = 's-item__price'
product_emb_link = 's-item__link'


def email_notify(subject, body):
    msg = EmailMessage()
    msg.set_content(body)

    msg['subject'] = subject
    
    # your email for alerts 
    msg['to'] = ''
    
    # your sending Gmail
    user = ''
    msg['from'] = user
    
    # Gmail app password
    password = ''

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)

    server.quit()


def filter_results(title, price):
    if not any(word in title for word in product_description_filters) and product_name_val in title:

        for character in "$to,":
            price = price.replace(character, "")

        if price:
            price_list = price.split()
            price_list = [float(i) for i in price_list]
            price_list = [int(i) for i in price_list]

            if len(price_list) == 1:
                price_list = price_list[0]

                if price_list in price_range:
                    return True
            else:
                if min(price_list) and max(price_list) in price_range:
                    return True


def main():
    for pages in page_navigator:

        driver.get(pages)

        # index starts at 0
        if page_navigator.index(pages) == 0:

            sleep(5)

            # filters to apply
            for filters in filter_to_apply:
                current_filter = f"""[aria-label='{filters}']"""

                filter_type = driver.find_element(by=By.CSS_SELECTOR, value=current_filter)
                filter_type.click()
                sleep(3)

            # count page(s)
            pages_found = driver.find_element(by=By.CLASS_NAME, value=page_count)
            element = pages_found.find_elements(by=By.TAG_NAME, value="a")

            for counter, page in enumerate(element):

                if counter != 0:
                    page_link = page.get_attribute("href")
                    page_navigator.append(page_link)

        results = driver.find_elements(by=By.CLASS_NAME, value=product_returned)
        sleep(5)

        for i in results:
            item_title = i.find_elements(by=By.CLASS_NAME, value=title_class)
            title_string = item_title[0].text
            title_string_formatted = title_string.lower()

            item_price = i.find_elements(by=By.CLASS_NAME, value=price_class)
            price_string = item_price[0].text

            if filter_results(title_string_formatted, price_string):

                product_href = i.find_elements(by=By.CLASS_NAME, value=product_emb_link)
                for link in product_href:
                    product_link = link.get_attribute("href")

                    product_details = ['\n', title_string, '\n', price_string, '\n', product_link, '\n']

                    for item in product_details:
                        potential_products.append(item)

            sleep(1)

    # if we did find items
    if len(potential_products) != 0:
        alert_to_string = ' '.join([str(elem) for elem in potential_products])
        sleep(1)
        email_notify('Ebay Item Update(s)', alert_to_string)


if __name__ == '__main__':
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=1920,1080')
    driver = uc.Chrome(options=chrome_options)

    main()
