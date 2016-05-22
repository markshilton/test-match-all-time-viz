from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import json

summary_url = "http://stats.espncricinfo.com/ci/engine/stats/index.html?class=1;orderby=runs;template=results;type=batting"

summary_r = requests.get(summary_url)
summary_soup = BeautifulSoup(summary_r.content, 'html5lib')
summary_table = summary_soup.find_all("table", class_="engineTable")[2].tbody

player_list = []

for row in summary_table.find_all('tr'):
    name_team = row.find_all('td')[0].get_text()
    link = row.find_all('td')[0].find('a')
    
    player_name = link.contents[0]
    player_id = re.search('player\/(.+?)\.html', link['href']).group(1)
    player_nationality = re.search('\((.+?)\)', name_team).group(1)

    innings_list_url = "http://stats.espncricinfo.com/ci/engine/player/" + player_id + ".html?class=1;orderby=runs;template=results;type=batting;view=innings"

    player_r = requests.get(innings_list_url)
    player_soup = BeautifulSoup(player_r.content, 'html5lib')
    player_table = player_soup.find_all("table", class_="engineTable")[3].tbody

    innings_list = []
    cumulative_runs = 0
    innings_count = 1

    for row in player_table.findAll('tr'):
        cells = row.find_all('td')
        innings = {}
        print(player_name, cells[12].string, cells[11].find('a').contents[0], cells[10].find('a').contents[0])

        if cells[0].string.strip() != 'DNB' and cells[0].string.strip() != 'TDNB' and cells[0].string.strip() != 'absent':
            cumulative_runs += int(re.sub('\*', '', cells[0].string))
            
            innings['cum_runs'] = cumulative_runs
            innings['runs'] = int(re.sub('\*', '', cells[0].string))
#            innings['mins'] = int(cells[1].string)
#            innings['balls'] = int(cells[2].string)
#            innings['fours'] = int(cells[3].string)
#            innings['sixes'] = int(cells[4].string)
#            innings['strike_rate'] = cells[5].string
#            innings['position'] = cells[6].string
#            innings['how_out'] = cells[7].string
#            innings['innings'] = cells[8].string
            innings['opponent'] = cells[10].find('a').contents[0]
            innings['venue'] = cells[11].find('a').contents[0]
            innings['date'] = cells[12].string
            innings['innings_count'] = innings_count

            innings_list.append(innings)

            innings_count += 1

    player_details = {}
    player_details['name'] = player_name
    player_details['innings'] = innings_list
    player_details['career runs'] = cumulative_runs
    player_list.append(player_details)

    print("Scraped " + player_name + ", " + player_nationality + ": " + str(cumulative_runs) + " runs")

with open('battingData.json', 'w', encoding='utf-8') as outfile:
    json.dump(player_list, outfile)
print("Scraping complete!")  