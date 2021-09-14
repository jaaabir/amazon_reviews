from selenium import webdriver
import selenium
from time import sleep


def f_pg_num(driver):
    num = int(driver.find_elements_by_class_name('s-pagination-disabled')[-1].text)
    return num

def get_prod_links(driver):
    links = []
    prods = driver.find_elements_by_class_name('s-expand-height.s-include-content-margin.s-latency-cf-section.s-border-bottom')
    for ind,prod in enumerate(prods):
        try:
            rnum = prod.find_element_by_class_name('a-section.a-spacing-none.a-spacing-top-micro').find_element_by_class_name('a-size-base').text.replace(',','')
            review = int(rnum)
        except selenium.common.exceptions.NoSuchElementException as err:
            review = 0
        except ValueError as err:
            review = 0

        if review >= 5:
            # href = prod.find_element_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "a-color-base", " " )) and contains(concat( " ", @class, " " ), concat( " ", "a-text-normal", " " ))]').get_attribute('href')
            href = prod.find_element_by_class_name('a-section.a-spacing-none').find_element_by_class_name('a-link-normal.s-no-outline').get_attribute('href')
            print(href)
            if 'gp/slredirect' not in href:
                links.append(href)
            

    return links

def get_products(pname, driver):
    url = f'https://www.amazon.in/s?k={pname}&page=1'
    # url = f'https://www.amazon.in/s?k={pname}&page=1&qid=1631469987&ref=sr_pg_1'
    print('scraping all product links...')
    all_links = []
    curr_pg_num = 1
    final_pg_num = 20

    driver.get(url)
    sleep(5)
    try:
        final_pg_num = f_pg_num(driver)
    except selenium.common.exceptions.NoSuchElementException as err:
        print('pagination error reloading the page ...')
    #     driver.get(url)
    #     sleep(3)
    #     final_pg_num = f_pg_num(driver)

    print(f'Total number of pages for {pname} : {final_pg_num}')

    while curr_pg_num < final_pg_num: 
        curr_pg_num += 1
        new_url = url.replace('page=1', f'page={curr_pg_num}')
        driver.get(new_url)
        sleep(5)
        all_links += get_prod_links(driver)

    print('finished scraping all product links...')
    return all_links


def get_next_pg(driver):
    try:
        next_pg = driver.find_element_by_class_name('a-pagination').find_element_by_class_name('a-last').find_element_by_tag_name('a').get_attribute('href')
    except selenium.common.exceptions.NoSuchElementException as err:
        next_pg = None
        
    return next_pg

def all_reviews(driver):
    reviews = driver.find_elements_by_class_name('a-size-base.review-text.review-text-content')
    reviews = [r.text for r in reviews]
    return reviews

def get_reviews(prods, pcate, driver):
    all_details = {}
    for prod in prods:  
        print(prod)
        pname = prod.split('/')[3]
        pid = prod.split('/')[5]
        nxt_url = f'https://www.amazon.in/{pname}/product-reviews/{pid}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'
        reviwes = []
        while nxt_url:
            driver.get(nxt_url)
            sleep(3)
            reviwes += all_reviews(driver)
            nxt_url = get_next_pg(driver)

        all_details[pid] = {
            'product_name': pname,
            'product_category': pcate,
            'reviews': reviwes
        } 

    return all_details

        