import requests
import re
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime as dt


def get_ipc_table(url,
                  table_class="table tabledat table-striped table-condensed table-hover"):

    """
    The function gets the 'ipc_table' from the url.
    The url must be:
    f"https://datosmacro.expansion.com/ipc-paises/usa?sector=IPC+General&sc=IPC-IG&anio={i}"
    Where i is the year we are consulting.
    """

    soup = BeautifulSoup(requests.get(url).content)
    return soup.find('table', {'class': table_class})


def get_ipc_tbl_header(ipc_table):
    """
    Get the header of the ipc_table.
    """

    headers = ipc_table.thead.find_all('th')
    pattern = r"[a-zA-Z0-9]+"

    table_header = ['Empty' if not (re.findall(pattern, h.contents[0].replace(u'\xa0', u' ')))
                    else h.contents[0].replace(u'\xa0', u' ')
                    for h in headers]

    return table_header


def get_ipc_tbl_body(ipc_table, table_body):
    """
    Get body content of the ipc_table. This function gets the rows
    of the resulting dataset and adds them into table_body list.
    """

    for row in ipc_table.tbody.find_all('tr'):
        row_arr = []
        for cell in row.contents:
            if cell['class'][0] in {'fecha', 'numero'}:
                row_arr.append(cell.contents[0])
        table_body.append(row_arr)

    return table_body


def get_ipc_data(first_yr=1961, last_yr=2021):
    """
    Main function which scraps the web table in order to build the dataset.
    :param first_yr: first ipc info year.
    :param last_yr: last ipc info year.
    :return: (table_header, table_body).
    """

    # URL to get the table header:
    ipc_usa = "https://datosmacro.expansion.com/ipc-paises/usa?sector=IPC+General&sc=IPC-IG"

    ipc_table = get_ipc_table(ipc_usa)               # Get first table.
    table_header = get_ipc_tbl_header(ipc_table)     # Get table header.

    table_body = []

    for i in range(first_yr, last_yr + 1):
        print('Year: ', i)
        try:
            # Get the url:
            ipc_usa = f"https://datosmacro.expansion.com/ipc-paises/usa?sector=IPC+General&sc=IPC-IG&anio={i}"
            ipc_table = get_ipc_table(ipc_usa)            # Get table from year i.
            get_ipc_tbl_body(ipc_table, table_body)       # Get rows from table.

            # print(ipc_usa)
        except Exception as e:
            print("Error:", e)
            continue

    print("--Finished--")
    return table_header, table_body


def correct_date(adate):
    """
    The function does preprocessing over date objects of the dataset.
    :param adate: raw object with date.
    :return: date object.
    """
    m_names_num = {'Enero': 1, 'Febrero': 2, 'Marzo': 3,
                   'Abril': 4, 'Mayo': 5, 'Junio': 6,
                   'Julio': 7, 'Agosto': 8, 'Septiembre': 9,
                   'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12}

    month, year = (m_names_num[adate.split(' ')[0]], int(adate.split(' ')[1]))

    return dt(year, month, 1)


def fill_missed_years(ipc_dict, min_yr, max_yr):

    expected = set(range(min_yr, max_yr + 1))
    had = set(ipc_dict.keys())
    missed = expected - had
    missed_ls = sorted(list(missed), reverse=True)
    years = list(ipc_dict.keys())
    ipcs = list(ipc_dict.values())

    for missed_yr in missed_ls:
        ipc_dict[missed_yr] = np.interp(missed_yr, years, ipcs)

    return ipc_dict


def get_year_factor_dict(first_year, last_year):
    """
    Calculates the gross correction factors according to the year.
    :param first_year:
    :param last_year:
    :return: year_factor_dict
    """
    (table_header, table_body) = get_ipc_data(first_year, last_year)

    # get dataframe:
    df = pd.DataFrame(table_body, columns=table_header)

    # Drop duplicates:
    df.drop_duplicates(inplace=True)

    # Date columns:
    df['date'] = df['Empty'].apply(lambda x: correct_date(x))
    df['anho'] = df['date'].dt.year
    df['mes'] = df['date'].dt.month

    # Rename columns:
    df.columns = ['fecha', 'interanual', 'acum_anho', 'var_mes%', 'date', 'anho', 'mes']

    # Change var_mes% type:
    df['var_mes%'] = df['var_mes%'].apply(
        lambda x: float(str(x).replace('%', '').replace(',', '.')))

    # Drop unused columns:
    df.drop(['fecha', 'interanual', 'acum_anho'], axis=1, inplace=True)

    # get data frame with year vs ipc variation by year:
    da = df.groupby('anho').sum().reset_index()[['anho', 'var_mes%']]
    da['var_mes_acu'] = da['var_mes%'].cumsum()

    # get IPC variation since first year scrapen until now:
    acu_actual = float(da[da['anho'] == max(da['anho'])]['var_mes_acu'])

    # get 'inverse' IPC variation:
    da['var_mes_acu_inv'] = acu_actual - da['var_mes_acu']

    # get factor to shift old grosses to equivalent value today
    da["factor"] = (da['var_mes_acu_inv'] / 100 + 1)

    # get year vs factor dictionary:
    year_factor_dict = da[['anho', 'factor']].set_index('anho').to_dict()['factor']

    year_factor_dict = fill_missed_years(year_factor_dict, first_year, last_year)

    return year_factor_dict
