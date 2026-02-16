#lab №1
from bs4 import BeautifulSoup
import requests

def parse_omgtu_news():
    url = 'https://omgtu.ru/news/'
    # https://www.omgtu.ru/news/?SHOWALL_1=1 - если все новости
    
    try:
        page = requests.get(url)
        print(f"Статус код: {page.status_code}")
        
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, "html.parser")

            news_titles = soup.find_all('h3', class_='news-card__title')
            
            headlines = []
            for title in news_titles:
                headline = title.text.strip()
                if headline:
                    headlines.append(headline)


            with open('omgtu_news_titles.txt', 'w', encoding='utf-8') as file:
                if headlines:
                    file.write("ЗАГОЛОВКИ НОВОСТЕЙ ОмГТУ:\n")
                    file.write("=" * 50 + "\n\n")
                    
                    for i, headline in enumerate(headlines, 1):
                        file.write(f"{i}. {headline}\n")
                        print(f"{i}. {headline}")
                    
                    print(f"\nВсего найдено новостей: {len(headlines)}")
                    print("Результаты сохранены в файл 'omgtu_news_titles.txt'")
                else:
                    file.write("Новости не найдены или структура сайта изменилась.")
                    print("Новости не найдены. Возможно, структура сайта изменилась.")
        
        else:
            print(f"Ошибка доступа к сайту. Статус код: {page.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("Ошибка подключения. Проверьте интернет-соединение.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == '__main__':
    parse_omgtu_news()
    
#button
#<a href="/news/?SHOWALL_1=1" 
#    onclick="BX.ajax.insertToNode('/news/?SHOWALL_1=1&amp;bxajaxid=f7fc60d6333aad8d37afe7a7a378359c',
#    'comp_f7fc60d6333aad8d37afe7a7a378359c'); return false;" rel="nofollow">Все</a>

#title
##<a href="/news/?eid=100251"
##onclick="BX.ajax.insertToNode('/news/?eid=100251&amp;bxajaxid=f7fc60d6333aad8d37afe7a7a378359c',
##'comp_f7fc60d6333aad8d37afe7a7a378359c'); return false;" class="news-card__link">
##                                    <h3 class="news-card__title">
##                                        Сформированы новые пакетные решения для повышения производительности труда в российских университетах </h3>
##                                </a>
