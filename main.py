# This is a sample Python script.

import re
# import pandas as pd
from ScrapIMDB.ScrapIMDB import get_movies_dataframe, correct_gross
from ScrapIPC.ScrapIPC import get_year_factor_dict
from os import makedirs


def apply_factor(year, gross, years_dict):
    return years_dict[year] * gross


# get movies raw dataframe:
df = get_movies_dataframe()

# Impute missed values on 'Gross collection'
df['Gross collection'].replace({'*****': '0'}, inplace=True)

# Apply correction function to gross:
df['Gross collection'] = df['Gross collection'].apply(correct_gross)

# Erase spaces from columns:
df.columns = [c.replace(' ', '_') for c in df.columns.tolist()]

# Fix date values:
pattern = r"[0-9]{4}"
df['Release_Year'] = df['Release_Year'].apply(lambda x: int(re.findall(pattern, x)[0]))

# Get years range:
last_year = max(df['Release_Year'])
first_year = min(df['Release_Year'])

# Get IPC factor:
year_factor_dict = get_year_factor_dict(first_year, last_year)

# Get revised gross:
df['Gross_equivalent'] = df.apply(lambda x: apply_factor(x.Release_Year, x.Gross_collection, year_factor_dict),
                                  axis=1)

# Create data folder:
makedirs("./data/", exist_ok=True)

# Create .csv:
df.to_csv('./data/sciFiMovies_dataset.csv', sep=';')
