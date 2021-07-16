from flask import Flask, render_template, request, jsonify
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


app = Flask(import_name=__name__)
app.config['JSON_AS_ASCII'] = False

# index
@app.route('/', methods=['get'])
def index():
    return render_template('00.index.html')

# 무신사 Search
@app.route('/search', methods=['post'])
def search_data():
    c_name = request.form.get("name") # 검색명 저장
    # data = '{'
    data = []
    print(c_name)

    main_url = "https://m.stock.naver.com/index.html#/domestic/stock/005930/total"
    driver = webdriver.Chrome("C:/driver/chromedriver")
    driver.get(main_url)
    time.sleep(2)  # 절대적 : 무조건 정해진 시간(초) 쉬기
    driver.implicitly_wait(2) # seconds
    
    input_search = driver.find_element_by_id("search_query")
    input_search.click() 
    input_search.clear()
    input_search.send_keys(c_name)

    btn_search = driver.find_element_by_id("search_button")
    btn_search.click()

    driver.implicitly_wait(5) # seconds
    driver.execute_script("searchTab('goods')")

    try:

        # 자바스크립트 실행 -> 해당 함수를 직접 실행!!
        soup = BeautifulSoup(driver.page_source, "lxml" )
        boxItems = soup.select("#searchList > .li_box")
        cnt = 0
        for boxItem in boxItems:
            print("*"*50)
            link = boxItem.find("p", class_="item_title").find('a')['href'] # 사이트 링크
            print(link)
            brand = boxItem.find("p", class_="item_title").find('a').string # 브랜드명
            print(brand)
            proTitle = boxItem.find("p", class_="list_info").find('a')['title'] # 옷 이름
            print(proTitle)
            proPrice = boxItem.find("p", class_="price").string
            if proPrice == None:
                proPrice = boxItem.find("p",class_="price").find('del').next_sibling.string
            proPrice = proPrice.replace(" ", "")
            proPrice = proPrice.replace("\n", "")
            print(proPrice)

            data.append({"link":link,"brand":brand,"proTitle":proTitle,"proPrice":proPrice})
        #     data += str(cnt)+':{"link":"' + link + '", "brand":' + brand + '", "proTitle":' + proTitle +'", "proPrice":' + str(proPrice) +'},'
        # data = data[0:-1]+"}"
        # data = literal_eval(data) # dict
        print(data)
        return jsonify(data)

    except Exception as e:
        print("페이지 파싱 에러", e)
    finally:
        time.sleep(3)
        driver.close()


if __name__ == '__main__':
    app.run(host="127.0.0.1", 
            port="5000",
            debug=True)
