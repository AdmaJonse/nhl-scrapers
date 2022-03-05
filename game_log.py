#
#  Description:
#    This script will attempt to parse game log data for a given player from
#    hockey-reference.com. An input file provides basic player data like
#    their name, ID on the website and career start and end year. The script
#    will use this data to navigate to the different game log pages, parse
#    the tables within and compile a single .csv file with the player's 
#    complete career game log (regular season only).
#

from bs4 import BeautifulSoup
from urllib.request import urlopen
from lxml import html
import csv
import os
import pandas

in_file = 'input\\players.csv'
out_dir = 'output'
headers = []

with open(in_file, newline='') as csv_in:

    # read the input files to determine which players and years we will attempt to parse
    reader = csv.reader(csv_in, delimiter=',', quotechar='\"')

    for row in reader:

        gamelog=[]

        try:
            # read the input file to determine the player name, starting year and ending year
            player = row[2]
            letter = row[3]
            id = row[4]        
            start = int(row[6])
            end = int(row[7])

            # set the output file name based on the player id
            out_file = out_dir + "\\" + id + ".csv"

        except:
            print("unable to parse row: " + row)
            break
        
        for year in range(start, end+1):
            
            # determine the url to parse
            url = "https://www.hockey-reference.com/players/" + letter + "/" + id + "/gamelog/" + str(year)

            # remove the output file if it already exists
            if os.path.isfile(out_file):
                os.remove(out_file)
                        
            print("parsing: " + url)

            # retrieve the page and parse it
            html = urlopen(url)

            # ensure the page was found before proceeding
            if html.getcode() == 404:
                print("url is not valid: " + url)
                continue

            soup = BeautifulSoup(html, features="lxml")

            # the headers are all the same, we just need to parse this once
            if headers == []:
                headers = [th.getText() for th in soup.findAll('tr', limit=2)[1].findAll('th')]

            # get rows from table
            rows = soup.findAll('tr')[2:]
            rows_data = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]

            gamelog += rows_data

        # write the complete game log to a .csv file
        df = pandas.DataFrame(gamelog, columns = headers[1:])
        df.dropna(inplace=True)
        df.to_csv(out_file, index=False)
