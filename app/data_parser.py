import json

import pandas as pd
import requests
from constants import TRANSLATION_FILENAME


class DataParser():

    def __init__(self):
        self.translated_data = {}

    def _clean_dataframes(self, df: pd.DataFrame, pokemons=True):
        df = df.droplevel(0, axis=1).drop('Kana', axis=1)
        if pokemons:
            df.drop(['Ndex', 'MS'], axis=1, inplace=True)
            df.replace(to_replace="\*", value="", regex=True, inplace=True)
        else:
            df.drop('Unnamed: 0_level_1', axis=1, inplace=True)
        return df

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

    def _convert_to_dictionary(self, df: pd.DataFrame):
        pokemon_hepburn = dict(zip(df['Hepburn'], df['English']))
        pokemon_trademark = dict(zip(df['Trademarked'], df['English']))
        return pokemon_hepburn | pokemon_trademark

    def _save_json(self, filename: str):
        with open(f'data/{filename}.json', 'w') as handle:
            json.dump(self.translated_data, handle, indent=4)

    def load_file(self, filename: str):
        self.translated_data = self._load_json(filename)

    def _load_json(self, filename: str):
        with open(f'data/{filename}.json', 'r') as handle:
            return json.load(handle)

    def add_entries(self, entry: dict):
        self.load_file(TRANSLATION_FILENAME)
        self.translated_data = self.translated_data | entry
        self._save_json(TRANSLATION_FILENAME)

    def _gather_all_data(self, dfs: list[pd.DataFrame], update: bool = False):
        self.load_file(TRANSLATION_FILENAME) if update else {}
        all_dict_data = [self._convert_to_dictionary(df) for df in dfs]
        for poke_dict in all_dict_data:
            self.translated_data |= poke_dict
        self._save_json(filename=TRANSLATION_FILENAME)

    def create(self):
        poke_dfs = self._scraper()
        self._gather_all_data(dfs=poke_dfs)

    def update(self):
        poke_dfs = self._scraper()
        self._gather_all_data(dfs=poke_dfs, update=True)
