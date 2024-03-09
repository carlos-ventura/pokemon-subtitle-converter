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
        pattern = re.compile('|'.join(r'\b' + key + r'\b' for key in self._translated_data.keys()), flags=re.IGNORECASE)
        return pattern.sub(lambda match: self._translated_data[match.group(0).title()], content)

    def _write_subtitles(self, path: str, content: str):
        with open(path, 'w', encoding="utf-8") as output_file:
            output_file.write(content)
