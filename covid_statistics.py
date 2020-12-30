
#!/usr/bin/env python3
#Description: Provide the covid  worlwide statistics and country wise.
"""
Provide the current worldwide COVID-19 statistics.
This data is being scrapped from 'https://www.worldometers.info/coronavirus/countries'.
"""
import logging as logger
import requests
import texttable as tt
from bs4 import BeautifulSoup


def world_covid_status(url: str = "https://www.worldometers.info/coronavirus") -> dict:
    """
    Return a dict of current worldwide COVID-19 statistics
    """
    try:
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        keys = soup.findAll("h1")
        values = soup.findAll("div", {"class": "maincounter-number"})
        keys += soup.findAll("span", {"class": "panel-title"})
        values += soup.findAll("div", {"class": "number-table-main"})
        return {key.text.strip(): value.text.strip() for key, value in zip(keys, values)}
    except Exception as error:
        logger.error(error)

def create_table(data):
    try:
        table = tt.Texttable()
        # Add an empty row at the beginning for the headers
        table.add_rows([(None, None, None, None)] + data) 
        # 'l' denotes left, 'c' denotes center,
        # and 'r' denotes right
        table.set_cols_align(('c', 'c', 'c', 'c'))  
        table.header((' Country ', ' Number of cases ', ' Deaths ', ' Continent '))
        print(table.draw())
    except Exception as error:
        logger.error(error)


def world_covid_table():
    try:
        # URL for scrapping data
        url = 'https://www.worldometers.info/coronavirus/countries-where-coronavirus-has-spread/'
        # get URL html
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        data = []
        # soup.find_all('td') will scrape every
        # element in the url's table
        data_iterator = iter(soup.find_all('td')) 
         
        # data_iterator is the iterator of the table
        # This loop will keep repeating till there is
        # data available in the iterator
        while True:
            try:
                country = next(data_iterator).text
                confirmed = next(data_iterator).text
                deaths = next(data_iterator).text
                continent = next(data_iterator).text
                # For 'confirmed' and 'deaths',
                # make sure to remove the commas 
                # and convert to int
                data.append((
                    country,
                    int(confirmed.replace(',', '')),
                    int(deaths.replace(',', '')),
                    continent
                ))
         
            # StopIteration error is raised when
            # there are no more elements left to
            # iterate through
            except StopIteration:
                break
         
        # Sort the data by the number of confirmed cases
        data.sort(key = lambda row: row[1], reverse = True)
        create_table(data) 
    except Exception as error:
        logger.error(error)    

def main():
    try:
        print("\033[1m" + "COVID-19 Status of the World" + "\033[0m\n")
        for key, value in world_covid_status().items():
            print(f"{key}\n{value}\n")
        world_covid_table()
    except Exception as error:
        logger.error(error)

if __name__ == "__main__":
    main()
    
   