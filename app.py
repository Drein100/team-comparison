import requests
import pandas as pd
import json
import os

# League information
league_info = {
    'Bundesliga': {'id': 54, 'season': 23794},
    'La Liga': {'id': 87, 'season': 23686},
    'Premier League': {'id': 47, 'season': 23685},
    'Serie A': {'id': 55, 'season': 23819},
    'Ligue 1': {'id': 53, 'season': 23724},
    'Super Lig': {'id': 71, 'season': 23864},
    'Champions League': {'id': 42, 'season': 24110},
    'Europa League': {'id': 73, 'season': 24112}
}

# Statistics mapping
team_stats = {
    "FotMob Rating": 'rating_team',
    "Goals (per match)": 'goals_team_match',
    "Expected Goals (xG)": 'expected_goals_team',
    "Goals Conceded (per match)": 'goals_conceded_team_match',
    "xG Conceded": 'expected_goals_conceded_team',
    "Touches in Opposition Box": 'touches_in_opp_box_team',
    "Shots on Target (per match)": 'ontarget_scoring_att_team',
    "Big Chances": 'big_chance_team',
    "Big Chances Missed": 'big_chance_missed_team',
    "Possession Won Final 3rd (per match)": 'poss_won_att_3rd_team',
    "Average Possession": 'possession_percentage_team',
    "Corners": 'corner_taken_team',
    "Accurate Crosses (per match)": 'accurate_cross_team',
    "Accurate Long Balls (per match)": 'accurate_long_balls_team',
    "Accurate Passes (per match)": 'accurate_pass_team',
    "Penalties Awarded": 'penalty_won_team',
    "Penalties Conceded": 'penalty_conceded_team',
    "Interceptions (per match)": 'interception_team',
    "Successful Tackles (per match)": 'won_tackle_team',
    "Clearences (per match)": 'effective_clearance_team',
    "Fouls (per match)": 'fk_foul_lost_team',
    "Saves (per match)": 'saves_team',
    "Clean Sheets": 'clean_sheet_team',
    "Yellow Cards": 'total_yel_card_team',
    "Red Cards": 'total_red_card_team'
}

def fetch_team_data(league_name, stat_name):
    league_name = capitalize_words(league_name)

    headers = {
        'Referer': 'https://www.fotmob.com',
        'Accept': '*/*',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0',
    }

    league = league_info.get(league_name)
    stat = team_stats.get(stat_name)

    if league is None or stat is None:
        raise ValueError("Geçersiz lig adı veya istatistik adı.")

    params = {
        'id': league['id'],
        'season': league['season'],
        'type': 'players',
        'stat': stat,
    }

    response = requests.get('https://www.fotmob.com/api/leagueseasondeepstats', params=params, headers=headers)
    data = response.json()

    # İstatistik verilerini al
    stats_data = data['statsData']
    names = [item['name'] for item in stats_data]
    stat_values = [item['statValue']['value'] for item in stats_data]

    team_ids = [item['teamId'] for item in stats_data]
    team_images = [f'https://images.fotmob.com/image_resources/logo/teamlogo/{team_id}.png' for team_id in team_ids]

    # DataFrame oluştur
    df = pd.DataFrame({
        'Takım': names,
        stat_name: stat_values,
        'Takım Resmi': team_images
    })

    return df

def compare_teams(league_name, stat_names):
    combined_stats = {}

    for stat_name in stat_names:
        df_team = fetch_team_data(league_name, stat_name)

        # İstatistikleri sözlükte sakla
        for index, row in df_team.iterrows():
            if row['Takım'] not in combined_stats:
                combined_stats[row['Takım']] = {'Takım Resmi': row['Takım Resmi']}  # Oyuncu resmini ekle
            # Değerleri yuvarlayarak ekle
            combined_stats[row['Takım']][stat_name] = round(row[stat_name], 1)

    # DataFrame oluştur
    final_df = pd.DataFrame(combined_stats).T
    final_df.reset_index(inplace=True)
    final_df.rename(columns={'index': 'Takım'}, inplace=True)

    # NaN değerlerini 0.0 ile doldur
    final_df.fillna(0.0, inplace=True)

    return final_df

def capitalize_words(text):
    return ' '.join(word.capitalize() for word in text.split())

# Örnek kullanım
stat_names = list(team_stats.keys())  # Tüm istatistik isimlerini al

# JSON dosyalarını kaydedeceğimiz klasörün adı
output_dir = 'jsons'

# Klasörün var olup olmadığını kontrol et, yoksa oluştur
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Tüm ligler için verileri oluştur ve JSON dosyalarına kaydet
for league in league_info.keys():
    team_stats_df = compare_teams(league, stat_names)

    # JSON verisini bir dosyaya yaz
    team_stats_json = team_stats_df.set_index('Takım').T.to_json(orient='index')
    file_name = f"{league}.json"
    file_path = os.path.join(output_dir, file_name)
    
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(json.loads(team_stats_json), json_file, indent=4, ensure_ascii=False)


