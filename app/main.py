import argparse
from translator import Translator
from data_parser import DataParser
from pathlib import Path
import constants as c
import shlex
import glob
import os
import subprocess
import mimetypes

#TODO Generations kinda
#TODO Fix bug of "-" bigger character 

def add_argument(add):
    all_entries = shlex.split(add)
    all_dicts = {}
    for entry in all_entries:
        new_entry = entry.split(":")
        all_dicts |= { new_entry[0]: new_entry[1] }
    return all_dicts

def generate_subs(file:str, sub_file: str, track_number:int):
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
        else : sub_filenames.append(file)
    return video_filenames if video else sub_filenames

def read_files(videos_folder: str, track_number: int):
    video_filenames = get_filenames(videos_folder)
    for file in video_filenames:
        file_list = file.split(".")
        file_list[-1] = "ass"
        sub_file = ".".join(file_list)
        generate_subs(file, sub_file, track_number)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Returns subtitle file with translated Pokemons and more")
    parser.add_argument('-p', '--path', type=str, metavar='', help="Full path of the subtitle target file or folder")
    parser.add_argument('-a', '--add', type=str, metavar='', help="Adds new entry to the translated json. 'Japonese_name:English_name'. If multiple separate by space")
    parser.add_argument('-gs', '--generate-subs', type=str, metavar='', help="Folder with mkv files. Generates all sub files for a folder outside called subs")
    parser.add_argument("-t", '--track', type=int, metavar='', help="Track number to get subs")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-u', '--update', action='store_true', help="Update the translation list from Bulbapedia")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    track_number = args.track or c.DEFAULT_TRACK_NUMBER
    print(f"[+] Track number is {track_number}")
    data_parser = DataParser()
    path_exists = Path(f'data/{c.TRANSLATION_DATA}.json').exists()
    if not path_exists:
        data_parser.create()
        print("[+] Create name list")
    if args.update:
        data_parser.update()
        print("[+] Update name list from the web")
    if add := args.add:
        add_dicts = add_argument(add)
        data_parser.add_entries(add_dicts)
        print(f"[+] Entry {add} added to the name list")
    if path := args.path:
        if not args.update and path_exists:
            data_parser.load_file(c.TRANSLATION_DATA)
        translated_data = data_parser.translated_data
        translator = Translator(translated_data, path)
        if os.path.isdir(path):
            print("[+] Folder input")
            translate_subs(translator, path)
        else:
            print("[+] Single file input")
            translator.run()
            print(path)
    if videos_folder:= args.generate_subs:
        print("[+] Extracting subtitles from the video files...")
        read_files(videos_folder, track_number)
        
    

