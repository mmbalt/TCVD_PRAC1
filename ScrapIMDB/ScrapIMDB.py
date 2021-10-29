import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime as dt


def getTitle(store):
    try:
        title = store.h3.a.text
    except Exception as e:
        print(e)
        title = None
    finally:
        return title


def getRanking(store):
    try:
        r_class = 'lister-item-index unbold text-primary'
        x_ranking = store.h3.find('span', class_=r_class) \
            .text.replace('(', '').replace(')', '').replace(".", '').strip()
    except Exception as e:
        print(e)
        x_ranking = None
    finally:
        return x_ranking


def getYear(store):
    try:
        m_class = 'lister-item-year text-muted unbold'
        movie_year = store.h3.find('span', class_=m_class) \
            .text.replace('(', '').replace(')', '').strip()
    except Exception as e:
        print(e)
        movie_year = None
    finally:
        return movie_year


def getTime(store):
    try:
        runtime = store.p.find('span', class_='runtime') \
            .text.replace(' min', '').strip()
    except Exception as e:
        print(e)
        runtime = None
    finally:
        return runtime


def getGenre(store):
    try:
        x_genre = store.p.find('span', class_='genre') \
            .text.replace('\n', '').strip()
    except Exception as e:
        print(e)
        x_genre = None
    finally:
        return x_genre


def getMetascore(store):
    try:
        meta = store.find('span', class_='metascore') \
            .text.replace(' ', '').strip()
    except Exception as e:
        print(e)
        meta = None
    finally:
        return meta


def getRate(store):
    try:
        rate = store.find('div', class_='inline-block ratings-imdb-rating') \
            .text.replace('\n', '')
    except Exception as e:
        print(e)
        rate = None
    finally:
        return rate


def getSinopsis(store):
    try:
        sin_x = store.find('div', class_='inline-block ratings-imdb-rating') \
            .text.replace('\n', '')
    except Exception as e:
        print(e)
        sin_x = None
    finally:
        return sin_x


def getDirectors(store):
    try:
        directors = store.find("p", {"class": ""}).text.replace('\n', '') \
            .strip().split("|")[0]
    except Exception as e:
        print(e)
        directors = None
    finally:
        return directors


def getStars(store):
    try:
        stars = store.find("p", {"class": ""}).text.replace('\n', '') \
            .strip().split("|")[1]
    except Exception as e:
        print(e)
        stars = None
    finally:
        return stars


def appendVotesAndGross(store, votes, gross):
    value = store.find_all('span', attrs={'name': 'nv'})
    vote = value[0].text
    votes.append(vote)
    grosses = value[1].text if len(value) > 1 else '*****'
    gross.append(grosses)

    return (votes, gross)


def scrapPage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # creating an empty list, so that we can append the values
    ranking = []
    movie_title = []
    year = []
    time = []
    genre = []
    rating = []
    metascore = []
    sinopsis = []
    # cast=[]
    directors = []
    stars = []
    votes = []
    gross = []

    # storing the meaningfull required data in the variable
    movie_data = soup.findAll('div', attrs={'class': 'lister-item-content'})

    for store in movie_data:
        movie_title.append(getTitle(store))

        ranking.append(getRanking(store))

        year.append(getYear(store))

        time.append(getTime(store))

        genre.append(getGenre(store))

        metascore.append(getMetascore(store))

        rating.append(getRate(store))

        sinopsis.append(getSinopsis(store))

        directors.append(getDirectors(store))

        stars.append(getStars(store))

        appendVotesAndGross(store, votes, gross)

    df_page = pd.DataFrame({'Title': movie_title,
                            'Release Year': year,
                            'Watchtime': time,
                            'Genre': genre,
                            'Movie Rating': rating,
                            'Metascore': metascore,
                            'Votes': votes,
                            'Gross collection': gross,
                            'Sinopsis': sinopsis,
                            "Director": directors,
                            'Star': stars})

    return df_page


def getNextUrl(actual_url):
    response = requests.get(actual_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    url = 'https://www.imdb.com' \
          + soup.find('a', attrs={'class': "lister-page-next next-page"})['href']

    return url


def getMoviesDataframe():
    finish = False
    url = 'https://www.imdb.com/search/title/'\
          + '?title_type=feature&num_votes=1000,&genres=sci-fi&sort=boxoffice_gross_us,desc'

    df = scrapPage(url)

    while not (finish):
        # Try to get next url:
        try:
            url = getNextUrl(url)
        except Exception as e:
            print(e)
            finish = True
            break

        print(url)
        df = pd.concat([df, scrapPage(url)])

    return df.copy()


def correctGross(value):
    value = value.replace('$', '')
    if value.find('M') != -1:
        value = value.replace('M', '')
        return float(value)*1000000
    elif value.find('K') != -1:
        value = value.replace('K', '')
        return float(value)*1000
    else:
        return float(value)

