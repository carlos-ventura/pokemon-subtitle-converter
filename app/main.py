import argparse
from translator import Translator
from data_parser import DataParser
from pathlib import Path
import constants as c
import shlex

#TODO Generations kinda
#TODO Extracts subtitle from mkv file

def add_argument(add):
    all_entries = shlex.split(add)
    all_dicts = {}
    for entry in all_entries:
        new_entry = entry.split(":")
        all_dicts |= { new_entry[0]: new_entry[1] }
    return all_dicts

def parse_arguments():
    parser = argparse.ArgumentParser(description="Returns subtitle file with translated Pokemons and more")
    parser.add_argument('-p', '--path', type=str, metavar='', help="Full path of the subtitle target file")
    parser.add_argument('-a', '--add', type=str, metavar='', help="Adds new entry to the translated json. 'Japonese_name:English_name'. If multiple separate by space")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-u', '--update', action='store_true', help="Update the translation list from Bulbapedia")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    data_parser = DataParser()
    path_exists = Path(f'data/{c.TRANSLATION_DATA}.json').exists()
    if not path_exists:
        data_parser.create()
    if args.update:
        data_parser.update()
    if add := args.add:
        add_dicts = add_argument(add)
        data_parser.add_entries(add_dicts)
    if path := args.path:
        if not args.update and path_exists:
            data_parser.load_file(c.TRANSLATION_DATA)
        translated_data = data_parser.translated_data
        translator = Translator(translated_data, path)
        translator.run()

