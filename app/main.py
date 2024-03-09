import argparse
import glob
import mimetypes
import os
import subprocess
from pathlib import Path

from constants import *
from translations import Translations
from translator import Translator


def convert_str_to_dict(entries: str):
    all_dicts = {}
    for entry in entries.split('|'):
        key, value = entry.split(':')
        all_dicts[key.strip()] = value.strip()
    return all_dicts


def generate_subs(file: str, sub_file: str, track_number: int):
    command_string = f'mkvextract "{file}" tracks {track_number}:"{sub_file}"'
    subprocess.Popen(command_string, stdout=subprocess.PIPE, shell=True)


def translate_subs(translator: Translator, videos_folder: str):
    subs_filenames = get_filenames(videos_folder, video=False)
    for file in subs_filenames:
        print(f"[+] {file}")
        translator.run(path=file)


def get_filenames(videos_folder: str, video: bool = True):
    filenames = glob.glob(os.path.join(videos_folder, "*.*"))
    video_filenames = []
    sub_filenames = []
    for file in filenames:
        mime = mimetypes.guess_type(file)
        if mime[0] is None:
            continue
        if "video" in mime[0]:
            video_filenames.append(file)
        else:
            sub_filenames.append(file)
    return video_filenames if video else sub_filenames


def read_files(videos_folder: str, track_number: int):
    video_filenames = get_filenames(videos_folder)
    for file in video_filenames:
        file_list = file.split(".")
        file_list[-1] = "ass"
        sub_file = ".".join(file_list)
        generate_subs(file, sub_file, track_number)


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
        translations.upsert(update=False)
        print("[+] Create name list")
    if args.update:
        translations.upsert(update=True)
        print("[+] Update name list from the web")
    if add := args.add:
        add_dicts = convert_str_to_dict(add)
        translations.add_entries(add_dicts)
        print(f"[+] Entry {add} added to the name list")
    if path := args.path:
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
    if videos_folder := args.generate_subs:
        print("[+] Extracting subtitles from the video files...")
        read_files(videos_folder, track_number)
