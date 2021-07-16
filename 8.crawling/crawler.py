from flask import Flask, render_template, request, jsonify
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import warnings
from dao import es_dao
from mpl_finance import candlestick2_ohlc
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from datetime import datetime
from IPython.display import display
from wordcloud import WordCloud

class Crawling():

    def crawl_stock(stock_num):

        warnings.filterwarnings('ignore')

        main_url = "https://m.stock.naver.com/index.html#/domestic/stock/"+ stock_num +"/price"
        driver = webdriver.Chrome("C:/driver/chromedriver")
        driver.get(main_url)
        time.sleep(2)  
        driver.implicitly_wait(1) 
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        driver.implicitly_wait(1) 
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        driver.implicitly_wait(1) 
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

        try:
            data = []
            columns = ['날짜','종가','전일대비','등락률','시가','고가','저가','거래량']
            soup = BeautifulSoup(driver.page_source, "lxml" )
            boxItems = soup.select("#content > div:nth-child(4) > div:nth-child(3) > div:nth-child(2) > div > div.VTablePrice_article__DfdmT > table > tbody")[0].select('tr')
            for boxItem in boxItems:
                a = boxItem.select('td')
                row = dict()
                row = {"등록번호":stock_num}
                for k,v in list(zip(columns,a)):
                    row[k] = v.text
                
                data.append(row)

            data = data[::-1]
            df_stock = pd.DataFrame(data)

            # 데이터 타입 변환
            for k,v in list(zip(range(0,9),df_stock)):
                if not k in [0,1,3,4]:
                    df_stock[v] = df_stock[v].apply(lambda x : int(int(x.replace(',', ''))))

            # 인덱스 재설정 밀 이동평균 칼럼 추가
            df_stock.reset_index(drop = True,inplace = True)
            df_stock.set_index('날짜',inplace=True)
            df_stock['MA3'] = df_stock['종가'].rolling(3).mean()
            df_stock['MA5'] = df_stock['종가'].rolling(5).mean()
            df_stock['MA10'] = df_stock['종가'].rolling(10).mean()

            fig = plt.figure(figsize=(20,10))
            ax = fig.add_subplot(111)
            index = df_stock.index.astype('str') # 캔들스틱 x축이 str로 들어감

            # 이동평균선 그리기
            ax.plot(index, df_stock['MA3'], label='MA3', linewidth=0.7)
            ax.plot(index, df_stock['MA5'], label='MA5', linewidth=0.7)
            ax.plot(index, df_stock['MA10'], label='MA10', linewidth=0.7)

            # X축 티커 숫자 20개로 제한
            ax.xaxis.set_major_locator(ticker.MaxNLocator(20))

            # 그래프 title과 축 이름 지정
            ax.set_title('Stock Chart', fontsize=22)
            ax.set_xlabel('Date')

            # 캔들차트 그리기
            candlestick2_ohlc(ax, df_stock['시가'], df_stock['고가'], 
                            df_stock['저가'], df_stock['종가'],
                            width=0.5, colorup='r', colordown='b')
            ax.legend()
            plt.grid()
            plt.show()
            # 이후 es에 저장할지 차트를 저장할지 결정

        except Exception as e:
            print("페이지 파싱 에러", e)
        finally:
            time.sleep(2)
            driver.close()

    def crawl_news(stock_num):

        warnings.filterwarnings('ignore')

        main_url = "https://m.stock.naver.com/index.html#/domestic/stock/"+ stock_num + "/news/title"
        driver = webdriver.Chrome("C:/driver/chromedriver")
        driver.get(main_url)
        time.sleep(2)  
        news_data = []
        try:
            for page_num in range(1,11):
                print(page_num,"번째 뉴스 크롤링---------------------")
                time.sleep(1)
                try:
                    boxItem = driver.find_element_by_css_selector(f"#content > div:nth-child(4) > div:nth-child(3) > div:nth-child(2) > div > div.VNewsList_article__1gx6H > ul > li:nth-child({page_num}) > a")
                except:
                    print("Pass")
                    continue
                boxItem.click()
                time.sleep(2)
                
                a = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[4]/div[3]/div[2]/div/div[1]/div[1]/strong").text
                b = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[4]/div[3]/div[2]/div/div[1]/div[2]/div[1]").text
                row = dict()
                row = {"등록번호" : stock_num}
                row['title'] = a
                row['content'] = b.replace("\n", "")
                news_data.append(row)
                
                time.sleep(1)
                driver.back()
            
            # 워드 클라우드 생성
            content = ""
            for i in news_data:
                content += i["content"]
            wordcloud = WordCloud(font_path='font/HMKMMAG.TTF', background_color='white').generate(content)
            plt.figure(figsize=(22,22)) #이미지 사이즈 지정
            plt.imshow(wordcloud, interpolation='lanczos') #이미지의 부드럽기 정도
            plt.axis('off') #x y 축 숫자 제거
            # plt.show() 

        except Exception as e:
            print("페이지 파싱 에러", e)
        finally:
            time.sleep(2)
            driver.close()
            # es_dao.save_news(news_data)


if __name__ == '__main__':
    # Crawling.crawl_stock('005930')
    Crawling.crawl_news('005930')