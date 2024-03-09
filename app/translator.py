import re


class Translator():
    def __init__(self, translated_data: dict, path: str):
        self._translated_data = translated_data
        self._path = path

    def run(self, path: str = None):
        if path:
            self._path = path

        old_subtitles = self._read_subtitles()
        new_subtitles = self._translate(old_subtitles)
        self._write_subtitles(self._path, new_subtitles)

    def _read_subtitles(self):
        with open(self._path, 'r', encoding="utf-8") as input_file:
            return input_file.read()

    def _translate(self, content: str):
        for key, value in self._translated_data.items():
            content = re.sub(pattern=r'\b' + key + r'\b', repl=value, string=content, flags=re.IGNORECASE)
        return content

    def _write_subtitles(self, path: str, content: str):
        with open(path, 'w', encoding="utf-8") as output_file:
            output_file.write(content)
