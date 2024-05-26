from asr_evaluation import __main__
import sys,os

# Ruta base y idioma correspondiente
base_route = "test\\langs"
language = 'en'  # Cambia esto al idioma correspondiente: 'en', 'it', 'ru' o 'ja'

sys.argv = ['evaluate.py' ,os.path.join(base_route,language,f'input_{language}.txt'),os.path.join(base_route,language,f'output_{language}.txt')]
__main__.main()

