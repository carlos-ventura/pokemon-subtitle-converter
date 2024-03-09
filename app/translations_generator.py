import json

import pandas as pd
import requests
from constants import TRANSLATION_FILENAME


class TranslationsGenerator():

    def __init__(self):
        self.translated_data = {}

    def load(self):
        self.translated_data = self._load_json()

    def upsert(self, update: bool = False):
        scraped_dfs = self._scraper()
        self._gather_all_data(dfs=scraped_dfs, update=update)

    def add_entries(self, entries: dict):
        self._load_json()
        self.translated_data = self.translated_data | entries
        self._save_json()

    def _load_json(self):
        with open(f'data/{TRANSLATION_FILENAME}.json', 'r') as input_json:
            return json.load(input_json)

    def _save_json(self):
        with open(f'data/{TRANSLATION_FILENAME}.json', 'w') as output_json:
            json.dump(self.translated_data, output_json, indent=4)

    def _scraper(self):
        url = r'https://bulbapedia.bulbagarden.net/wiki/List_of_Japanese_Pok%C3%A9mon_names'
        html = requests.get(url).content
        df_list = pd.read_html(html)
        pokemon_dfs = []
        for df in df_list:
            if 'Ndex' in df:
                df = self._clean_dataframes(df)
                pokemon_dfs.append(df)
            elif 'English' in df:
                df = self._clean_dataframes(df, False)
                pokemon_dfs.append(df)
        return pokemon_dfs

    def _clean_dataframes(self, df: pd.DataFrame, pokemons=True):
        df = df.droplevel(0, axis=1).drop('Kana', axis=1)
        if pokemons:
            df.drop(['Ndex', 'MS'], axis=1, inplace=True)
            df.replace(to_replace="\*", value="", regex=True, inplace=True)
        else:
            df.drop('Unnamed: 0_level_1', axis=1, inplace=True)
        return df

    def _gather_all_data(self, dfs: list[pd.DataFrame], update: bool):
        self._load_json() if update else {}
        all_dict_data = [self._convert_to_dictionary(df) for df in dfs]
        for dict_ in all_dict_data:
            self.translated_data |= dict_
        self._save_json()

    def _convert_to_dictionary(self, df: pd.DataFrame):
        pokemon_hepburn = dict(zip(df['Hepburn'], df['English']))
        pokemon_trademark = dict(zip(df['Trademarked'], df['English']))
        return pokemon_hepburn | pokemon_trademark
