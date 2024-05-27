'''from asr_evaluation import __main__
import sys,os

# Ruta base y idioma correspondiente
base_route = "test\\langs"
language = 'en'  # Cambia esto al idioma correspondiente: 'en', 'it', 'ru' o 'ja'

sys.argv = ['evaluate.py' ,os.path.join(base_route,language,f'input_{language}.txt'),os.path.join(base_route,language,f'output_{language}.txt')]
#__main__.main()
'''

from typing import List

import datasets,os
import jiwer
import jiwer.transforms as tr
from datasets.config import PY_VERSION
from packaging import version

import evaluate


if PY_VERSION < version.parse("3.8"):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata


SENTENCE_DELIMITER = ""


if version.parse(importlib_metadata.version("jiwer")) < version.parse("2.3.0"):

    class SentencesToListOfCharacters(tr.AbstractTransform):
        def __init__(self, sentence_delimiter: str = " "):
            self.sentence_delimiter = sentence_delimiter

        def process_string(self, s: str):
            return list(s)

        def process_list(self, inp: List[str]):
            chars = []
            for sent_idx, sentence in enumerate(inp):
                chars.extend(self.process_string(sentence))
                if self.sentence_delimiter is not None and self.sentence_delimiter != "" and sent_idx < len(inp) - 1:
                    chars.append(self.sentence_delimiter)
            return chars

    cer_transform = tr.Compose(
        [tr.RemoveMultipleSpaces(), tr.Strip(), SentencesToListOfCharacters(SENTENCE_DELIMITER)]
    )
else:
    cer_transform = tr.Compose(
        [
            tr.RemoveMultipleSpaces(),
            tr.Strip(),
            tr.ReduceToSingleSentence(SENTENCE_DELIMITER),
            tr.ReduceToListOfListOfChars(),
        ]
    )
base_dir= "test\\langs"
lan="en"
input_file = os.path.join(base_dir, lan, f"input_{lan}.txt")
output_file = os.path.join(base_dir, lan, f"output_{lan}.txt")

# Leer el contenido de input_file
with open(input_file, 'r', encoding='utf-8') as file:
    references = [line.strip() for line in file.readlines()]

# Leer el contenido de output_file
with open(output_file, 'r', encoding='utf-8') as file:
     predictions= [line.strip() for line in file.readlines()]


cer = evaluate.load("cer")
cer_score = cer.compute(predictions=predictions, references=references)
print(cer_score)
