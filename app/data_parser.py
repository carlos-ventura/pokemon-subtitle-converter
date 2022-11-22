import requests
import pandas as pd
import json
import pickle
import constants as c

class DataParser():

    def __init__(self):
        self.translated_data = {}

    def __clean_dataframes(self, df: pd.DataFrame, pokemons=True):
        df = df.droplevel(0, axis=1).drop('Kana', axis=1)
        if pokemons:
            df.drop(['Ndex', 'MS'], axis=1, inplace=True)
            df.replace(to_replace="\*", value="", regex=True, inplace=True)
        else:
            df.drop('Unnamed: 0_level_1', axis=1, inplace=True)
        return df

    def __scraper(self):
        url = r'https://bulbapedia.bulbagarden.net/wiki/List_of_Japanese_Pok%C3%A9mon_names'
        html = requests.get(url).content
        df_list = pd.read_html(html)
        pokemon_dfs = []
        for df in df_list:
            if 'Ndex' in df:
                df = self.__clean_dataframes(df)
                pokemon_dfs.append(df)
            elif 'English' in df:
                df = self.__clean_dataframes(df, False)
                pokemon_dfs.append(df)
        return pokemon_dfs
        
    def __convert_to_dictionary(self, df: pd.DataFrame):
        pokemon_hepburn = dict(zip(df['Hepburn'], df['English']))
        pokemon_trademark = dict(zip(df['Trademarked'], df['English']))
        return pokemon_hepburn | pokemon_trademark

    def __save_file(self, filename: str, pickle: bool = False):
        self.__save_pickle(filename) if pickle else self.__save_json(filename)

    def __save_json(self, filename: str):
        with open(f'data/{filename}.json', 'w') as handle:
            json.dump(self.translated_data, handle, indent=4)

    def __save_pickle(self, filename: str):
        with open(f'data/{filename}.pickle', 'wb') as handle:
            pickle.dump(self.translated_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_file(self, filename: str, pickle: bool = False):
        self.translated_data = self.__load_pickle(filename) if pickle else self.__load_json(filename)

    def __load_json(self, filename: str):
        with open(f'data/{filename}.json', 'r') as handle:
            return json.load(handle)

    def __load_pickle(self, filename: str):
        with open(f'data/{filename}.pickle', 'rb') as handle:
            return pickle.load(handle)

    def add_entries(self, entry:dict):
        self.load_file(c.TRANSLATION_DATA)
        self.translated_data = self.translated_data | entry
        self.__save_file(c.TRANSLATION_DATA)

    def __gather_all_data(self, dfs: list[pd.DataFrame], update: bool = False):
        self.load_file(c.TRANSLATION_DATA) if update else {}
        all_dict_data = [self.__convert_to_dictionary(df) for df in dfs]
        for poke_dict in all_dict_data:
            self.translated_data |= poke_dict
        self.__save_file(filename=c.TRANSLATION_DATA)

    def create(self):
        poke_dfs = self.__scraper()
        self.__gather_all_data(dfs=poke_dfs)

    def update(self):
        poke_dfs = self.__scraper()
        self.__gather_all_data(dfs=poke_dfs, update=True)


