# TCVD_PRAC1

The code of this repository has been made to meet the objectives of <Practice 1> of the TCVD subject, within the Master of Data Science (Universitat Oberta de Catalunya).

The code is divided in three files:
* main.py : main file which calls the functions to scrap the webpages and generate the dataset.
* ScrapIPC.py : file which contains the functions to get the USA IPC data from [datosmacro](https://datosmacro.expansion.com/) site.
* ScrapIMDB.py : file which contains the functions to get the Sci-Fi movie data from [IMDB](https://www.imdb.com/) site.


## Usage:
Once the repository is pulled the code can be executed in a terminal running on the project folder with `python main.py`.

The program will start scrapping the webpages for a few minutes. After that it will build the dataset with the scrapped data into a folder `./data/` and print --Finished-- on the console when its done. The name of the data file will be `sciFiMovies_dataset.csv` which is a csv file using ';' as separator.


## Issues:
The code may stop working because changes on the structure of the sracpped webpages and it will not be maintained after 2021/11/7.


## License
* The lincese of the code is indicated on the LICENSE.md file of the repository.
* The license of the dataset is indicated [here](https://zenodo.org/record/5650109#.YYZ6OrqCF1I). You can also find the obtained dataset there.

