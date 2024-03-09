import argparse
import os
from pathlib import Path

from action_handlers import convert_str_to_dict, generate_subs, translate_subs
from constants import *
from translations import Translations
from translator import Translator


def parse_arguments():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-p', '--path', type=str, metavar='', help=PATH_HELP)
    parser.add_argument('-e', '--entries', type=str, metavar='', help=ENTRIES_HELP)
    parser.add_argument('-gs', '--generate-subs', type=str, metavar='', help=GENERATE_SUBS_HELP)
    parser.add_argument("-t", '--track', type=int, metavar='', help=TRACK_HELP)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-u', '--update', action='store_true', help=UPDATE_HELP)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()

    track_number = args.track or DEFAULT_TRACK_NUMBER
    print(f"[+] Track number is {track_number}")

    translations = Translations()

    path_exists = Path(f'data/{TRANSLATION_FILENAME}.json').exists()

    if not path_exists:
        print("[+] Creating translations...")
        translations.upsert(update=False)

    if args.update:
        print("[+] Updating translations...")
        translations.upsert(update=True)

    if entries := args.entries:
        entry_dicts = convert_str_to_dict(entries)
        for key, value in entry_dicts:
            print(f"[+] Adding entry {key}:{value} translations...")
        translations.add_entries(entry_dicts)

    if videos_folder := args.generate_subs:
        print("[+] Extracting subtitles from the video files...")
        generate_subs(videos_folder, track_number)

    if path := args.path:
        print("Translating...")
        if not args.update and path_exists:
            translations.load()

        translated_data = translations.translated_data
        translator = Translator(translated_data, path)
        if os.path.isdir(path):
            print("[+] Folder input")
            translate_subs(translator, path)
        else:
            print("[+] Single file input")
            translator.run()
            print(path)
