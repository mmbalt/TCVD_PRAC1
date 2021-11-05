import requests
# import re
import pandas as pd
from bs4 import BeautifulSoup
# from datetime import datetime as dt


def get_title(store):
    """
    Gets the title of the movie
    :param store: bs4 tag object which contents the movie data.
    :return: title of the movie
    """
    try:
        title = store.h3.a.text
    except Exception as e:
        print(e)
        title = None
    finally:
        return title


def get_ranking(store):
    """
    Gets movie ranking.
    :param store: bs4 tag object which contents the movie data.
    :return: x_ranking.
    """
    try:
        r_class = 'lister-item-index unbold text-primary'
        x_ranking = store.h3.find('span', class_=r_class) \
            .text.replace('(', '').replace(')', '').replace(".", '').strip()
    except Exception as e:
        print(e)
        x_ranking = None
    finally:
        return x_ranking


def get_year(store):
    """
    Gets movie year.
    :param store: bs4 tag object which contents the movie data.
    :return: movie_year.
    """
    try:
        m_class = 'lister-item-year text-muted unbold'
        movie_year = store.h3.find('span', class_=m_class) \
            .text.replace('(', '').replace(')', '').strip()
    except Exception as e:
        print(e)
        movie_year = None
    finally:
        return movie_year


def get_time(store):
    """
    Gets movie runtime.
    :param store: bs4 tag object which contents the movie data.
    :return: runtime.
    """
    try:
        runtime = store.p.find('span', class_='runtime') \
            .text.replace(' min', '').strip()
    except Exception as e:
        print(e)
        runtime = None
    finally:
        return runtime


def get_genre(store):
    """
    Gets movie genre.
    :param store: bs4 tag object which contents the movie data.
    :return: x_genre.
    """
    try:
        x_genre = store.p.find('span', class_='genre') \
            .text.replace('\n', '').strip()
    except Exception as e:
        print(e)
        x_genre = None
    finally:
        return x_genre


def get_metascore(store):
    """
    Gets movie metascore.
    :param store: bs4 tag object which contents the movie data.
    :return: meta
    """
    try:
        meta = store.find('span', class_='metascore') \
            .text.replace(' ', '').strip()
    except Exception as e:
        print(e)
        meta = None
    finally:
        return meta


def get_rate(store):
    """
    Gets movie rate
    :param store: bs4 tag object which contents the movie data.
    :return: rate.
    """
    try:
        rate = store.find('div', class_='inline-block ratings-imdb-rating') \
            .text.replace('\n', '')
    except Exception as e:
        print(e)
        rate = None
    finally:
        return rate


def get_sinopsis(store):
    """
    Gets movie sinopsis.
    :param store: bs4 tag object which contents the movie data.
    :return: sin_x
    """
    try:
        sin_x = store.find('div', class_='inline-block ratings-imdb-rating') \
            .text.replace('\n', '')
    except Exception as e:
        print(e)
        sin_x = None
    finally:
        return sin_x


def get_directors(store):
    """
    Gets the movie directors.
    :param store: bs4 tag object which contents the movie data.
    :return: directors.
    """
    try:
        directors = store.find("p", {"class": ""}).text.replace('\n', '') \
            .strip().split("|")[0]
    except Exception as e:
        print(e)
        directors = None
    finally:
        return directors


def get_stars(store):
    """
    Gets the movie main actors.
    :param store: bs4 tag object which contents the movie data.
    :return: stars.
    """
    try:
        stars = store.find("p", {"class": ""}).text.replace('\n', '') \
            .strip().split("|")[1]
    except Exception as e:
        print(e)
        stars = None
    finally:
        return stars


def append_votes_and_gross(store, votes, gross):
    """
    Gets the votes and gross.
    :param store: bs4 tag object which contents the movie data.
    :param votes: votes list.
    :param gross: gross list.
    :return: (votes, gross)
    """
    value = store.find_all('span', attrs={'name': 'nv'})
    vote = value[0].text
    votes.append(vote)
    grosses = value[1].text if len(value) > 1 else '*****'
    gross.append(grosses)

    return (votes, gross)


def scrap_page(url):
    """
    This function scraps the page indicated in the url. It must be the url of an IMDB list.
    :param url: bs4 tag object which contents the movie data.
    :return df_page: scraped page data in a dataframe.
    """
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
    directors = []
    stars = []
    votes = []
    gross = []

    # storing the meaningfull required data in the variable
    movie_data = soup.findAll('div', attrs={'class': 'lister-item-content'})

    for store in movie_data:
        movie_title.append(get_title(store))

        ranking.append(get_ranking(store))

        year.append(get_year(store))

        time.append(get_time(store))

        genre.append(get_genre(store))

        metascore.append(get_metascore(store))

        rating.append(get_rate(store))

        sinopsis.append(get_sinopsis(store))

        directors.append(get_directors(store))

        stars.append(get_stars(store))

        append_votes_and_gross(store, votes, gross)

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


def get_next_url(actual_url):
    """
    The function gets the url of the next page to scrap.
    :param actual_url: bs4 tag object which contents the movie data.
    :return:
    """
    response = requests.get(actual_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    url = 'https://www.imdb.com' \
          + soup.find('a', attrs={'class': "lister-page-next next-page"})['href']

    return url


def get_movies_dataframe():
    """
    The function scraps the IMDB website  in order to get data from sci-fi movies.
    :return: dataframe with the movies data.
    """
    finish = False
    url = 'https://www.imdb.com/search/title/'\
          + '?title_type=feature&num_votes=1000,&genres=sci-fi&sort=boxoffice_gross_us,desc'

    df = scrap_page(url)

    while not finish:
        # Try to get next url:
        try:
            url = get_next_url(url)
        except Exception as e:
            print(e)
            finish = True
            break

        print(url)
        df = pd.concat([df, scrap_page(url)])

    return df.copy()


def correct_gross(value):
    """
    The function does preprocessing on movie gross data.
    :param value:
    :return:
    """
    value = value.replace('$', '')
    if value.find('M') != -1:
        value = value.replace('M', '')
        return float(value)*1000000
    elif value.find('K') != -1:
        value = value.replace('K', '')
        return float(value)*1000
    else:
        return float(value)

