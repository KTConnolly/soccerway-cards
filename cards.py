import argparse
import csv

import requests
from bs4 import BeautifulSoup
from unidecode import unidecode


def create_soup(url):
    headers = {'User Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/73.0.3683.103 Safari/537.36'}

    r = requests.get(url, headers=headers)
    return BeautifulSoup(r.text, 'html.parser')


def mins_played(soup):
    mins_elem = soup.find_all(
        'td', class_='number statistic game-minutes available'
    )
    return int(mins_elem[-1].text)


def yellow_cards(soup):
    cards_elem = soup.find_all(
        'td', class_='number statistic yellow-cards available'
    )
    return int(cards_elem[-1].text)


def squad(soup):
    player_elems = soup.find_all(
        'td', class_='name large-link'
    )

    players_data = [(unidecode(player.text), player.a.get('href'))
                    for player in player_elems][:-1]  # Remove coach
    return players_data


def card_dict(squad_list):
    card_data = {}
    for name, url_path in squad_list:
        s = create_soup('https://us.soccerway.com' + url_path)
        card_data[name] = (mins_played(s), yellow_cards(s))
        print(name)
    return card_data


def write_csv(team_name, player_dict):
    with open(f'{team_name}.csv', mode='w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)

        for player, (mins, cards) in player_dict.items():
            csv_writer.writerow(
                [
                    player,
                    mins,
                    cards,
                ]
            )


def available_teams():
    s = create_soup('https://us.soccerway.com/national/italy/serie-a')

    team_elems = s.find_all(
        'td', class_='text team large-link'
    )
    team_names = []
    for team in team_elems:
        if 'italy' in team.a.get('href'):
            team_names.append(team.a.get('href').split('/')[-3])
    return team_names


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('team', help='Serie A team name')
    args = parser.parse_args()

    options = available_teams()

    if args.team not in options:
        print(f'Available teams are:')
        print('\n'.join(options))
        return

    s = create_soup(f'https://us.soccerway.com/teams/italy/{args.team}/squad/')
    squad_soup = squad(s)
    data = card_dict(squad_soup)
    write_csv(args.team, data)


if __name__ == '__main__':
    main()
