# DESC: Scrapes NFL AV stat, combine data, and college data for given players in a draft year
# DATE: June 3, 2020
# NOTE: CHANGE FILE DESTINATION ON LINE 16 SO CSV FILE SAVES TO YOUR LOCAL MACHINE

# Import Libraries
from bs4 import BeautifulSoup, Comment
import requests
import re
import pandas as pd
import csv

#**********************************************************
#*          CHANGE THE FILE DESTINATION HERE              *
#**********************************************************
# Opens csv files to write into
csv_export_file = open('C:\\Users\Jaxon\Desktop\sports_analytics_project_data.csv', 'w', newline='')

# Creates the csv writer objects
csv_export_file_writer = csv.writer(csv_export_file)

# fixes 'Rushing & Receiving' table order
def fix_table_order(table_list, table_type):
    if table_type == 'rushing':
        order = [4, 5, 6, 7, 0, 1, 2, 3, 8, 9, 10, 11]
    elif table_type == 'punt_ret':
        order = [4, 5, 6, 7, 0, 1, 2, 3]
    
    try:
        table_list = [table_list[i] for i in order]
        return table_list
    except:
        return table_list

# Less-magical parsing class
def parse_table(table_data):
    # Creates variable to return
    parsed_table = []

    try:
        # Gets the table ID
        parsed_table.append(table_data.get('id'))

        # Grabs all the rows
        table_body = table_data.find('tfoot')
        rows = table_body.find_all('tr')

        # Grabs data from row
        for row in rows:
            if row.th.get_text() == 'Career':
                data_list = []
                cols = row.find_all('td')
                for data in cols:
                    if data.find('a') is not None:
                        data_list.append(data.find('a').get_text())
                    else:
                        data_list.append(data.get_text())

                # Removes values that are always empty
                for i in range(5):
                    data_list.pop(0)

                # Adds player info to list
                parsed_table.append(data_list)

        # Reformats list if necessary
        if parsed_table[0] == 'rushing' or parsed_table[0] == 'punt_ret':
            parsed_table[1] = fix_table_order(parsed_table[1], parsed_table[0])

        # Returns complete list of rows
        return parsed_table

    except:
        pass

def get_av(av_table):
    # Declares variable
    av = ''

    # Grabs all the rows
    table_body = av_table.find('tfoot')
    rows = table_body.find_all('tr')

    # Grabs data from row
    for row in rows:
        if row.th.get_text() == 'Career':
            av = row.find("td", attrs={"data-stat": "av"}).get_text()
    
    # Returns av value
    return av

# Set Headers
headers = requests.utils.default_headers()
headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linus x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})

# Base url for web scraping
url = 'https://www.pro-football-reference.com'

# Table header list
csv_headers = [
    'Key', 'Name', 'Draft_Year', 'Position', 'AV', 'Height', 'Weight', 'Forty_Yd', 'Bench', 'Broad_Jump', 'Shuttle', 'Cone', 
    'Vertical', 'T_Solo', 'T_Ast', 'T_Tot', 'T_Loss', 'T_Sk', 'Def_Int', 'Def_Yds', 'Def_Avg', 'Def_TD', 'Def_PD', 'F_FR', 
    'F_Yds', 'F_TD', 'F_FF', 'K_Ret', 'K_Yds', 'K_Avg', 'K_TD', 'P_Ret', 'P_Yds', 'P_Avg', 'P_TD', 'Rush_Att', 'Rush_Yds', 
    'Rush_Avg', 'Rush_TD', 'Rec_Rec', 'Rec_Yds', 'Rec_Avg', 'Rec_TD', 'Scim_Plays', 'Scrim_Yds', 'Scrim_Avg', 'Scrim_TD', 
    'Pass_Cmp', 'Pass_Att', 'Pass_Pct', 'Pass_Yds', 'Pass_YA', 'Pass_AYA', 'Pass_TD', 'Pass_Int', 'Pass_Rate', 'TD_Rush', 
    'TD_Rec', 'TD_Int', 'TD_FR', 'TD_PR', 'TD_KR', 'TD_Oth', 'TD_Tot', 'K_XPM', 'K_FGM', '2PM', 'Sfty', 'Pts'
]
csv_export_file_writer.writerow(csv_headers)

for x in range (2000, 2019): #Set year range
    try:
        r = requests.get(url + '/years/' + str(x) + '/draft.htm') #get HTML request data
        soup = BeautifulSoup(r.content, 'html.parser') #create beautifulSoup object
        parsed_table = soup.find_all('table')[0] #parse text for table
        
        #Set values to "" in case of missing data
        print(x)
        
        for i,row in enumerate(parsed_table.find_all('tr')[2:]): #Loop through each player in draft year
            try:
                av = ''
                dat = row.find('td', attrs={'data-stat': 'player'})  #find player stat row      
                name = dat.a.get_text() #extract player name
                key = dat.get('data-append-csv') #extract player ID
                stub = dat.a.get('href') #extract player URL stub`
                
                #Nav to player page to get stats
                playerRequest = requests.get(url + stub)
                playerSoup = BeautifulSoup(playerRequest.content, 'html.parser')
                
                #Grab AV
                try:
                    #AVdiv = playerSoup.find_all("td", {"data-stat": "av"})
                    #y=-1
                    #for tag in AVdiv:
                    #    y = y + 1

                    #av = AVdiv[y].text
                    av_table = playerSoup.find_all("table")[0]
                    av = get_av(av_table)
                except:
                    av='NONE'
                    continue
                
                #Grab college stats url
                college_link = ''
                try:
                    college_link = playerSoup.find("a", text="College Stats").get("href")
                except:
                    college_link = 'NONE'
                    continue
                
                div = playerSoup.find('div', id='all_combine').find(string=lambda tag: isinstance(tag, Comment))
                div = BeautifulSoup(div, 'html.parser')
                table = div.find('table', id='combine')
                for i,row in enumerate(table.find_all('tr')[1:]):
                    try:
                        #Position
                        dat = row.find('td', attrs={'data-stat': 'pos'})
                        pos = dat.get_text()
                        #Height
                        dat = row.find('td', attrs={'data-stat': 'height'})
                        height = dat.get_text()
                        #Weight
                        dat = row.find('td', attrs={'data-stat': 'weight'})
                        weight = dat.get_text()
                        #40yd
                        dat = row.find('td', attrs={'data-stat': 'forty_yd'})
                        forty_yd = dat.get_text()
                        #Bench
                        dat = row.find('td', attrs={'data-stat': 'bench_reps'})
                        bench_reps = dat.get_text()
                        #Broad Jump
                        dat = row.find('td', attrs={'data-stat': 'broad_jump'})
                        broad_jump = dat.get_text()
                        #Shuttle
                        dat = row.find('td', attrs={'data-stat': 'shuttle'})
                        shuttle = dat.get_text()
                        #3Cone
                        dat = row.find('td', attrs={'data-stat': 'cone'})
                        cone = dat.get_text()
                        #Vertical
                        dat = row.find('td', attrs={'data-stat': 'vertical'})
                        vertical = dat.get_text()

                    except:
                        pass

                # Gets college data
                req_player_page = requests.get(college_link)
                player_page = BeautifulSoup(req_player_page.content, 'html.parser')

                # Creates list of each table for players
                combined_data_list = [
                    ['defense', ['', '', '', '', '', '', '', '', '', '', '', '', '', '']],
                    ['kick_ret', ['', '', '', '', '', '', '', '']],
                    ['receiving', ['', '', '', '', '', '', '', '', '', '', '', '']],
                    ['passing', ['', '', '', '', '', '', '', '', '']],
                    ['scoring', ['', '', '', '', '', '', '', '', '', '', '', '', '']]
                ]

                # list to hold comments found in html
                comment_list = []

                # list to hold all table data for player
                final_data_list = []

                # List to read into csv
                csv_ready_list = []

                # Finds all commented tables and saves them to comment_list
                for comments in player_page.findAll(text=lambda text:isinstance(text, Comment)):
                    if comments.extract().find("table") != -1:
                        comment_list.append(comments.extract())

                # Parses each table in list
                for table in comment_list:
                    formatted_table = BeautifulSoup(table, 'html.parser').find("table")
                    if formatted_table is not None:
                        parsed_table = parse_table(formatted_table)
                        if parsed_table is not None:
                            final_data_list.append(parsed_table)

                # Adds last data table to list
                if player_page.find("table") is not None:
                    data_table = parse_table(player_page.find("table"))
                    final_data_list.append(data_table)

                # Adds all lists to master list
                for table in final_data_list:
                    if table[0] == 'defense':
                        combined_data_list.pop(0)
                        combined_data_list.insert(0, table)
                    elif table[0] == 'kick_ret':
                        combined_data_list.pop(1)
                        combined_data_list.insert(1, table)
                    elif table[0] == 'receiving':
                        combined_data_list.pop(2)
                        combined_data_list.insert(2, table)
                    elif table[0] == 'passing':
                        combined_data_list.pop(3)
                        combined_data_list.insert(3, table)   
                    elif table[0] == 'scoring':
                        combined_data_list.pop(4)
                        combined_data_list.insert(4, table)

                # Combines master list into one list to read into csv
                for table in combined_data_list:
                    csv_ready_list = csv_ready_list + table[1]

                #TODO: REMOVE DEBUGGING CODE
                print(name)

                #Add player data to table
                finalized_player_data = [key, name, x, pos, av, height, weight, forty_yd, bench_reps, broad_jump, shuttle, cone, vertical] + csv_ready_list

                # Writes row into csv file
                csv_export_file_writer.writerow(finalized_player_data)

            except:
                pass
    except:
        pass

# Closes csv files
csv_export_file.close()