# Lista de reglas gramaticales basadas en el apartado otras consideraciones, separacion ideal, de esta pagina -> https://www.inesem.es/revistadigital/idiomas/normas-subtitulacion/
'''   
    Artículo + sintagma nominal
    Preposición + sintagma nominal
    Conjunción + frase
    Pronombre + verbo
    Partes de una forma verbal
    Adverbios de negación + verbo
    Preposición + sintagma verbal'''

grammatical_rules_v1 = [
    {"label": "component", "pattern": [{"pos": {"in": ["DET"]}, "dep": {"in": ["nsubj", "obj"]}}]},
    {"label": "component", "pattern": [{"pos": {"in": ["ADP"]}, "dep": {"in": ["nsubj", "obj"]}}]},
    {"label": "component", "pattern": [{"pos": {"in": ["CONJ"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["PRON"]}, "dep": {"in": ["nsubj", "obj"]}}]},
    {"label": "component", "pattern": [{"pos": {"in": ["VERB"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["ADV"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["ADP"]}, "dep": "ROOT"}]}
]

grammatical_rules_v2 = [
    {"label": "component", "pattern": [{"pos":"CCONJ"}]},
    {"label": "component", "pattern": [{"pos": "ADP"}]}
]

#https://applied-language-technology.mooc.fi/html/notebooks/part_iii/03_pattern_matching.html#matching-syntactic-dependencies
grammatical_patterns_v2 = [
  {
    "nombre": "Artículo + Sintagma Nominal",
    "patron": [
      {
        "RIGHT_ID": "det",
        "RIGHT_ATTRS": {"POS": "DET"}
      },
      {
        "LEFT_ID": "det",
        "REL_OP": ">",
        "RIGHT_ID": "noun",
        "RIGHT_ATTRS": {"POS": "NOUN"}
      },
      {
        "LEFT_ID": "det",
        "REL_OP": ">",
        "RIGHT_ID": "pron",
        "RIGHT_ATTRS": {"POS": "PRON"}
      },

    ]
  },
  {
    "nombre": "Preposición + Sintagma Nominal",
    "patron": [
      {
        "RIGHT_ID": "prep",
        "RIGHT_ATTRS": {"POS": "ADP"}
      },
      {
        "LEFT_ID": "prep",
        "REL_OP": ">",
        "RIGHT_ID": "noun",
        "RIGHT_ATTRS": {"POS": "NOUN"}
      }
    ]
  },
  {
    "nombre": "Conjunción + Frase",
    "patron": [
      {
        "RIGHT_ID": "conj",
        "RIGHT_ATTRS": {"POS": "CONJ"}
      },
      {
        "LEFT_ID": "conj",
        "REL_OP": ">",
        "RIGHT_ID": "phrase",
        "RIGHT_ATTRS": {"DEP": "conj"}
      }
    ]
  },
  {
    "nombre": "Pronombre + Verbo",
    "patron": [
      {
        "RIGHT_ID": "pron",
        "RIGHT_ATTRS": {"POS": "PRON"}
      },
      {
        "LEFT_ID": "pron",
        "REL_OP": ">",
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"POS": "VERB"}
      }
    ]
  },
  {
    "nombre": "Partes de una forma verbal",
    "patron": [
      {
        "RIGHT_ID": "aux",
        "RIGHT_ATTRS": {"POS": "AUX"}
      },
      {
        "LEFT_ID": "aux",
        "REL_OP": ">",
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"POS": "VERB"}
      },
      {
        "LEFT_ID": "verb",
        "REL_OP": ">",
        "RIGHT_ID": "particle",
        "RIGHT_ATTRS": {"POS": "PART"}
      }
    ]
  },
  {
    "nombre": "Adverbios de negación + Verbo",
    "patron": [
      {
        "RIGHT_ID": "neg",
        "RIGHT_ATTRS": {"POS": "ADV"} # "no", "nunca", etc.
      },
      {
        "LEFT_ID": "neg",
        "REL_OP": ">",
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"POS": "VERB"}
      }
    ]
  },
  {
    "nombre": "Preposición + Sintagma Verbal",
    "patron": [
      {
        "RIGHT_ID": "prep",
        "RIGHT_ATTRS": {"POS": "ADP"}
      },
      {
        "LEFT_ID": "prep",
        "REL_OP": ">",
        "RIGHT_ID": "verb",
        "RIGHT_ATTRS": {"POS": "VERB"}
      }
    ]
  },
  # ... (puedes agregar más reglas aquí)
]


puntuation_rules_left=[
    {"label": "component", "pattern": [{"ORTH": "¡"}]},#signos lado izquierdo
    {"label": "component", "pattern": [{"ORTH": "¿"}]}
]
puntuation_rules_right=[
    {"label": "component", "pattern": [{"ORTH": ","}]},  # Match para coma
    {"label": "component", "pattern": [{"ORTH": "."}]},  # Match para punto
    {"label": "component", "pattern": [{"ORTH": "!"}]}, #signos lado derecho
    {"label": "component", "pattern": [{"ORTH": "?"}]},
    {"label": "component", "pattern": [{"ORTH": ";"}]},
    {"label": "component", "pattern": [{"ORTH": ":"}]}
]