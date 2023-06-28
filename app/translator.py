import re

class Translator():
    def __init__(self, translated_data: str, path: str = None):
        self._translated_data = translated_data
        self._path = path

    def read_subtitles(self):
        with open(self._path, 'r', encoding="utf-8") as handle:
            return handle.read()

    def write_subtitles(self, path: str, content: str):
        with open(path, 'w', encoding="utf-8") as handle:
            handle.write(content)

    def translate_pokemon_names(self, content: str, translated_pokemons: dict):
        for key, value in translated_pokemons.items():
            content = re.sub(pattern=r'\b' + key + r'\b', repl=value, string=content, flags=re.IGNORECASE)
        return content
    
    def run(self, path: str = None):
        if path:
            self._path = path
        old_subtitles = self.read_subtitles()
        new_subtitles = self.translate_pokemon_names(old_subtitles, self._translated_data)
        self.write_subtitles(self._path, new_subtitles)
    