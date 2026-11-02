"""«En contra» positions, two sources:

1. OPUESTAS — answers that exclude each other. A party marked 'p' (priority) on one answer is 'c' (against) on its
   opposite, with the same quotes. Comes from our own hand-picked assignments.

2. DIR — Manifesto Project direction, only where MARPOR has a plus/minus pair that maps onto the answer.
   (question, answer) -> (codes for, codes against, topical regex).
   Sentences are counted inside the question's topic (column `temas` of datos/decide/frases.csv).
   Automatic 'contra': party not assigned to the answer, ≥ MIN_CONTRA sentences against, ≥ RATIO × more against
   than for, and at least one of those sentences matches the topical regex (it is about this, not just the same code).
   The quotes shown are the matching sentences.
   Also used to check hand-picked quotes: a quote coded against its own answer is flagged.

Left out on purpose: answers sharing one code (504 welfare: housing, health, pensions), 605.1/605.2 (mixes prison
policy with gender violence, terrorism and police resources), 701/702 (no 702 in any programme).
"""
MIN_CONTRA = 3
RATIO = 2

OPUESTAS = [
    ('viv_alquiler', 'tope', 'derogar'),
    ('viv_desahucio', 'alternativa', 'plazos'),
    ('inm_irregular', 'regularizar', 'expulsar'),
    ('inm_irregular', 'regularizar', 'arraigo'),
    ('inm_nacionalidad', 'endurecer', 'cinco'),
    ('inm_menores', 'papeles', 'repatriar'),
    ('inm_ayudas', 'legal', 'imv'),
    ('inm_ayudas', 'legal', 'padron'),
    ('san_gestion', 'estado', 'comunidades'),
    ('edu_centro', 'eleccion', 'publica'),
    ('edu_centro', 'cheque', 'publica'),
    ('edu_contenidos', 'ebau', 'propio'),
    ('dem_jueces', 'jueces', 'cortes'),
    ('dem_indultos', 'sedicion', 'amnistia'),
    ('imp_fortunas', 'subir', 'quitar'),
    ('imp_sucesiones', 'suprimir', 'minimo'),
    ('seg_penas', 'ampliar', 'eliminar'),
    ('seg_protesta', 'mordaza', 'autoridad'),
    ('seg_policias', 'autonomica', 'suprimir'),
    ('cli_nuclear', 'alargar', 'cerrar'),
    ('cli_ritmo', 'acelerar', 'pacto'),
    ('cli_ritmo', 'acelerar', 'combustion'),
    ('des_genero', 'reforzar', 'derogar'),
    ('des_aborto', 'publica', 'derogar'),
    ('ter_modelo', 'recentralizar', 'autonomias'),
    ('ter_modelo', 'recentralizar', 'plurinacional'),
    ('ter_referendum', 'si', 'no'),
    ('ter_financiacion', 'foral', 'suprimir'),
    ('ter_financiacion', 'propia', 'suprimir'),
    ('ter_lenguas', 'castellano', 'inmersion'),
    ('ter_lenguas_estado', 'uso', 'requisito'),
    ('ext_defensa', 'reforzar', 'menos'),
    ('ext_sahara', 'autodeterminacion', 'actual'),
]

RX_VIV = r'alquiler|lloguer|aluguer|vivienda|habitatge|vivenda'
RX_INM = (r'inmigr|immigr|migra|extranjer|estranger|estranxeir|frontera|fronter|asilo|\basil\b|nacionalidad|nacionalitat|'
          r'arraigo|arrelament|regulariz|regularitz|expuls|devoluci|devolu|retorno|repatri')
RX_SAN = r'sanit|salud|salut|saúde|hospital|\bMIR\b|médic|metge'
RX_COMP = r'competencia|competència|autonom|estatut|traspas|traspàs|transfer|descentraliz|centraliz|autogob|autogovern|autogoberno'
RX_NAC = (r'naci[oó]n|nació\b|naciones|plurinacion|refer[eè]ndum|referend|autodetermin|decidir|independ|soberan|sobiran|'
          r'unidad de España|separatis|secesion')
RX_FIN = r'financ|finança|concierto|concert|convenio|cupo|hacienda|hisenda|facenda|tribut|impuest|impost|foral|derechos hist'
RX_LEN = (r'lengua|llengua|lingua|idioma|castellano|español|català|catalán|euskera|euskara|galego|gallego|valencià|'
          r'vehicular|inmersi|immersi|plurilingü')
RX_DEF = r'defensa|militar|Fuerzas Armadas|ejército|exèrcit|exército|OTAN|NATO|armament|armas|armes|bèl·lic|belicis'

INM_POS, INM_NEG = {'607.2', '602.2'}, {'608.2', '601.2'}
DIR = {
 ('viv_alquiler', 'tope'):            ({'412'}, {'401'}, RX_VIV),
 ('viv_alquiler', 'derogar'):         ({'401'}, {'412'}, RX_VIV),
 ('inm_irregular', 'regularizar'):    (INM_POS, INM_NEG, RX_INM),
 ('inm_irregular', 'expulsar'):       (INM_NEG, INM_POS, RX_INM),
 ('inm_irregular', 'arraigo'):        (INM_NEG, INM_POS, RX_INM),
 ('inm_nacionalidad', 'endurecer'):   ({'608.2'}, {'607.2'}, RX_INM),
 ('inm_nacionalidad', 'cinco'):       ({'607.2'}, {'608.2'}, RX_INM),
 ('inm_ayudas', 'legal'):             (INM_NEG, INM_POS, RX_INM),
 ('inm_ayudas', 'imv'):               (INM_POS, INM_NEG, RX_INM),
 ('inm_frontera', 'bloqueo'):         ({'601.2'}, {'602.2'}, RX_INM),
 ('inm_frontera', 'medios'):          ({'601.2'}, {'602.2'}, RX_INM),
 ('inm_frontera', 'caliente'):        ({'602.2'}, {'601.2'}, RX_INM),
 ('inm_frontera', 'seguras'):         ({'602.2'}, {'601.2'}, RX_INM),
 ('inm_laboral', 'afin'):             ({'608.2'}, {'607.2'}, RX_INM),
 ('san_gestion', 'estado'):           ({'302'}, {'301'}, RX_SAN),
 ('san_gestion', 'comunidades'):      ({'301'}, {'302'}, RX_SAN),
 ('pen_futuro', 'propia'):            ({'301'}, {'302'}, r'Seguridad Social|Seguretat Social|Seguridade Social|pensi'),
 ('seg_policias', 'autonomica'):      ({'301'}, {'302'}, r'polic|Mossos|Ertzaintza|Guardia Civil|seguridad|seguretat|seguranza'),
 ('seg_policias', 'suprimir'):        ({'302'}, {'301'}, r'polic|Mossos|Ertzaintza|Guardia Civil|seguridad|seguretat|seguranza'),
 ('ter_modelo', 'recentralizar'):     ({'302'}, {'301'}, RX_COMP),
 ('ter_modelo', 'autonomias'):        ({'301'}, {'302'}, RX_COMP),
 ('ter_modelo', 'plurinacional'):     ({'602.1'}, {'601.1'}, RX_NAC),
 ('ter_referendum', 'si'):            ({'602.1'}, {'601.1'}, RX_NAC),
 ('ter_referendum', 'no'):            ({'601.1'}, {'602.1'}, RX_NAC),
 ('ter_financiacion', 'propia'):      ({'301'}, {'302'}, RX_FIN),
 ('ter_financiacion', 'foral'):       ({'301'}, {'302'}, RX_FIN),
 ('ter_financiacion', 'suprimir'):    ({'302'}, {'301'}, r'concierto|concert econ|convenio econ|r[eé]gimen foral|foralidad|\bcupo\b|derechos hist|fueros|Amejoramiento'),
 ('ter_lenguas', 'castellano'):       ({'601.1'}, {'602.1'}, RX_LEN),
 ('ter_lenguas', 'inmersion'):        ({'602.1'}, {'601.1'}, RX_LEN),
 ('ter_lenguas_estado', 'uso'):       ({'602.1'}, {'601.1'}, RX_LEN),
 ('ter_lenguas_estado', 'requisito'): ({'601.1'}, {'602.1'}, RX_LEN),
 ('ext_defensa', 'reforzar'):         ({'104'}, {'105'}, RX_DEF),
 ('ext_defensa', 'menos'):            ({'105'}, {'104'}, RX_DEF),
}

# Answers that are one precise measure: the code direction is too broad to say a party opposes *that* measure, so
# they are only checked (flags), never given automatic «en contra».
SOLO_COMPROBAR = {
    ('inm_irregular', 'arraigo'), ('inm_nacionalidad', 'endurecer'), ('inm_nacionalidad', 'cinco'),
    ('inm_frontera', 'bloqueo'), ('inm_frontera', 'medios'), ('inm_ayudas', 'legal'), ('inm_ayudas', 'imv'),
    ('inm_laboral', 'afin'), ('ter_referendum', 'no'), ('viv_alquiler', 'derogar'), ('viv_alquiler', 'tope'),
}
