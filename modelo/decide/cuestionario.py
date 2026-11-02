"""Cuestionario «decide» — borrador 3 (1 nov 2026).

Cada pregunta = un asunto concreto dentro de un problema de la lista del barómetro del CIS.
Cada respuesta = UNA medida. Se pueden elegir varias respuestas por pregunta.
Para cada partido y respuesta: 'p' (lo propone como prioridad), 't' (también lo recoge) o 'c' (en contra, a mano),
con los índices de las frases del corpus que lo justifican (columna `i` de datos/decide/frases.csv).
Los «en contra» por respuesta opuesta y los automáticos del Manifesto Project los añade exportar.py (direccion.py).
"""

TEMAS = {
    'vivienda': 'Vivienda',
    'economia': 'Precios y coste de la vida',
    'empleo': 'Empleo y salarios',
    'inmigracion': 'Inmigración',
    'sanidad': 'Sanidad',
    'educacion': 'Educación',
    'corrupcion': 'Corrupción y funcionamiento de la política',
    'juventud': 'Jóvenes',
    'impuestos': 'Impuestos',
    'seguridad': 'Seguridad ciudadana',
    'clima': 'Clima, energía y agua',
    'pensiones': 'Pensiones',
    'desigualdad': 'Pobreza e igualdad',
    'territorio': 'Modelo territorial y lenguas',
    'exterior': 'Defensa y política exterior',
}

def O(k, t, **p):
    return dict(k=k, t=t, p=p)

Q = [
 # ═══════════════ VIVIENDA ═══════════════
 dict(id='viv_alquiler', tema='vivienda', q='¿Qué hacer con el precio del alquiler?', opts=[
   O('tope', 'Limitar el precio en las zonas donde más ha subido',
     FA=('p', [303]), ERC=('p', [252, 1174]), BILDU=('p', [10]), PSOE=('t', [3813])),
   O('prorroga', 'Prorrogar automáticamente los contratos con la misma renta', BILDU=('p', [48])),
   O('deduccion', 'Que quien vive de alquiler pueda desgravarlo en el IRPF',
     VOX=('p', [530]), ERC=('p', [2487]), JUNTS=('p', [1538])),
   O('derogar', 'Derogar la ley de vivienda', PP=('p', [602]), VOX=('p', [299, 323]), UPN=('p', [103])),
 ]),
 dict(id='viv_oferta', tema='vivienda', q='¿Cómo conseguir más vivienda a un precio asequible?', opts=[
   O('publica', 'Construir vivienda pública de alquiler',
     PSOE=('p', [1655, 1709]), FA=('p', [394]), ERC=('p', [2467]), JUNTS=('p', [1501]), PNV=('p', [846]),
     BNG=('p', [245]), COMP=('p', [22]), VOX=('t', [296])),
   O('sareb', 'Pasar los pisos de la Sareb a comunidades y ayuntamientos',
     COMP=('p', [23]), BNG=('p', [246]), JUNTS=('p', [1503]), ERC=('p', [1321]), PSOE=('t', [3830]), VOX=('t', [297])),
   O('suelo', 'Liberar suelo para construir', VOX=('p', [286])),
   O('turisticos', 'Regular los pisos turísticos', FA=('p', [2144]), VOX=('t', [303])),
 ]),
 dict(id='viv_compra', tema='vivienda', q='¿Cómo ayudar a comprar la primera vivienda?', opts=[
   O('avales', 'Avales públicos para que la hipoteca cubra casi todo el precio',
     PP=('p', [604]), PSOE=('p', [2249]), JUNTS=('p', [1537])),
   O('iva', 'Quitar o rebajar el IVA de la primera vivienda', VOX=('p', [288, 318])),
   O('itp', 'Que el impuesto de compra suba con el precio de la casa', COMP=('p', [190])),
 ]),
 dict(id='viv_okupa', tema='vivienda', q='¿Qué hacer con la ocupación ilegal de viviendas?', opts=[
   O('desalojo', 'Que se pueda desalojar en 24 horas',
     PP=('p', [1406, 1410]), VOX=('t', [280]), JUNTS=('t', [1930]), UPN=('t', [102])),
   O('mafias', 'Perseguir a las mafias que ocupan viviendas', PSOE=('p', [4303]), VOX=('t', [280])),
 ]),
 dict(id='viv_desahucio', tema='vivienda', q='¿Qué hacer con los desahucios de familias vulnerables?', opts=[
   O('alternativa', 'Que no se desahucie a nadie sin una alternativa de vivienda',
     FA=('p', [2136]), ERC=('p', [1219, 1273]), PSOE=('t', [4296]), JUNTS=('t', [1495])),
   O('plazos', 'Acortar los plazos del desahucio cuando no se paga el alquiler', VOX=('p', [314])),
 ]),
 # ═══════════════ PRECIOS ═══════════════
 dict(id='eco_precios', tema='economia', q='¿Qué haría más contra la subida de precios?', opts=[
   O('iva', 'Bajar el IVA de los alimentos y productos básicos',
     PP=('p', [360]), VOX=('p', [537]), BNG=('p', [519]), BILDU=('t', [74])),
   O('energia', 'Bajar el IVA de la luz y el gas', BNG=('p', [520]), FA=('t', [1302])),
   O('deflactar', 'Ajustar el IRPF a la inflación para no pagar más por la subida de precios',
     PP=('p', [359]), JUNTS=('p', [938]), BNG=('p', [507]), UPN=('p', [24])),
   O('beneficios', 'Un impuesto a los beneficios extraordinarios de energéticas y bancos',
     COMP=('p', [194]), BILDU=('p', [91]), BNG=('p', [99])),
   O('mercado', 'Cambiar el mercado eléctrico para que el gas no fije el precio de la luz', FA=('p', [430])),
   O('pacto', 'Un pacto de rentas entre empresas y sindicatos', FA=('p', [278, 281])),
 ]),
 # ═══════════════ EMPLEO ═══════════════
 dict(id='emp_jornada', tema='empleo', q='¿Hay que reducir la jornada laboral?', opts=[
   O('h375', 'Sí, a 37,5 horas por ley, sin bajar el sueldo', FA=('p', [260])),
   O('h35', 'Sí, a 35 horas, sin bajar el sueldo', BNG=('p', [265])),
   O('h32', 'Sí, hasta 32 horas o cuatro días a la semana',
     BILDU=('p', [36]), COMP=('p', [108]), ERC=('p', [1184]), FA=('t', [261])),
   O('pilotos', 'Probarlo primero en empresas voluntarias', PSOE=('p', [926])),
 ]),
 dict(id='emp_smi', tema='empleo', q='¿Cómo debería fijarse el salario mínimo?', opts=[
   O('s60', 'Que llegue al 60 % del salario medio', BNG=('p', [266]), COMP=('p', [105]), BILDU=('p', [40])),
   O('ipc', 'Que suba siempre por encima de la inflación', FA=('p', [270])),
   O('dialogo', 'Que lo acuerden Gobierno, sindicatos y empresarios', PP=('p', [275, 276])),
   O('propio', 'Que cada comunidad pueda fijar el suyo', BILDU=('t', [40])),
 ]),
 dict(id='emp_despido', tema='empleo', q='¿Qué cambiar en el despido?', opts=[
   O('d45', 'Volver a 45 días de indemnización y a los salarios de tramitación',
     BILDU=('p', [32, 33]), BNG=('p', [257]), COMP=('t', [107])),
   O('readmision', 'Más protección frente al despido injustificado, incluida la readmisión', FA=('p', [823, 825])),
   O('mochila', 'Una cuenta por trabajador que le acompañe de empresa en empresa', PP=('p', [291]), JUNTS=('p', [1039])),
 ]),
 dict(id='emp_crear', tema='empleo', q='¿Cómo crear más empleo?', opts=[
   O('cotizaciones', 'Bajar las cotizaciones a las empresas que contraten', VOX=('p', [149]), JUNTS=('p', [936, 1085])),
   O('activas', 'Mejores políticas de empleo y formación para quien busca trabajo',
     PP=('p', [268]), FA=('p', [273]), PNV=('t', [523])),
 ]),
 dict(id='emp_autonomos', tema='empleo', q='Si trabajas por tu cuenta, ¿qué te ayudaría más?', opts=[
   O('cuota0', 'No pagar cuota si ganas menos del salario mínimo', VOX=('p', [159]), ERC=('t', [2002])),
   O('tarifa0', 'Cuota cero el primer año', PP=('p', [296]), JUNTS=('t', [1114])),
   O('ingresos', 'Cotizar según lo que ingresas de verdad', JUNTS=('p', [1124]), BNG=('p', [287])),
   O('derechos', 'Los mismos derechos que un asalariado (paro, pensión)', ERC=('p', [2014, 2004])),
   O('aplazar', 'Poder aplazar la cuota en los meses malos', PP=('p', [297])),
   O('cobrar', 'Que las grandes empresas te paguen en 30 días como máximo', ERC=('p', [2003]), JUNTS=('t', [1152]), PSOE=('t', [615])),
 ]),
 # ═══════════════ INMIGRACIÓN ═══════════════
 dict(id='inm_irregular', tema='inmigracion', q='¿Qué hacer con las personas que viven en España sin papeles?', opts=[
   O('regularizar', 'Una regularización extraordinaria',
     ERC=('p', [943]), FA=('p', [2767]), BNG=('p', [304]), JUNTS=('t', [1663])),
   O('contrato', 'Que tener un contrato de trabajo baste para conseguir papeles', PNV=('p', [623]), PSOE=('t', [4382])),
   O('expulsar', 'Expulsarlas', VOX=('p', [690, 731]), PP=('t', [1398])),
   O('arraigo', 'Que nunca puedan regularizarse quienes entraron de forma irregular', VOX=('p', [698, 719])),
 ]),
 dict(id='inm_nacionalidad', tema='inmigracion', q='¿Cómo debería conseguirse la nacionalidad española?', opts=[
   O('endurecer', 'Con más requisitos, y que pueda perderse por delitos', VOX=('p', [720, 722, 723])),
   O('cinco', 'Con cinco años de residencia como máximo', ERC=('p', [857])),
   O('agilizar', 'Igual que ahora, pero con trámites más rápidos', PSOE=('p', [4291])),
 ]),
 dict(id='inm_frontera', tema='inmigracion', q='¿Qué hacer en la frontera sur (Ceuta, Melilla, Canarias)?', opts=[
   O('bloqueo', 'Un bloqueo naval', VOX=('p', [704, 705])),
   O('medios', 'Más agentes y medios de control en la frontera', PP=('p', [1390, 1393]), PSOE=('t', [3920])),
   O('caliente', 'Acabar con las devoluciones en caliente',
     BILDU=('p', [134]), BNG=('p', [379]), JUNTS=('p', [1665]), ERC=('p', [635]), FA=('p', [3869]), COMP=('p', [255]), PNV=('t', [194])),
   O('seguras', 'Abrir vías legales y seguras para llegar',
     BILDU=('p', [132]), JUNTS=('p', [1662]), ERC=('p', [856]), PSOE=('t', [4379])),
   O('origen', 'Acuerdos con los países de origen y de tránsito', CC=('p', [188]), PP=('p', [1395, 1398]), PSOE=('t', [4112])),
 ]),
 dict(id='inm_menores', tema='inmigracion', q='¿Qué hacer con los menores que llegan solos?', opts=[
   O('reparto', 'Repartirlos entre todas las comunidades', PNV=('p', [192]), CC=('p', [189]), PP=('t', [988, 989])),
   O('papeles', 'Que tengan permiso de residencia y de trabajo al cumplir los 18', FA=('p', [2587]), COMP=('p', [88])),
   O('repatriar', 'Devolverlos con sus familias a su país', VOX=('p', [473, 700])),
 ]),
 dict(id='inm_ayudas', tema='inmigracion', q='¿Quién debería recibir ayudas sociales?', opts=[
   O('legal', 'Solo quien reside legalmente, con prioridad para los españoles', VOX=('p', [462, 694, 709])),
   O('imv', 'También las familias en situación irregular con hijos', FA=('p', [2345])),
   O('padron', 'Que todo el mundo pueda empadronarse, tenga o no papeles', ERC=('p', [946, 948])),
 ]),
 dict(id='inm_laboral', tema='inmigracion', q='¿Cómo debería elegirse la inmigración que viene a trabajar?', opts=[
   O('puntos', 'Con un sistema de puntos por formación e idioma', PP=('p', [204, 205])),
   O('origen', 'Contratando en el país de origen, con convenios', PSOE=('p', [4393])),
   O('mercado', 'Según los puestos que no se cubren', PNV=('p', [561]), VOX=('t', [155, 685])),
   O('afin', 'Con prioridad para quien comparte idioma y cultura', VOX=('p', [703, 981])),
 ]),
 # ═══════════════ SANIDAD ═══════════════
 dict(id='san_espera', tema='sanidad', q='¿Cómo acortar las esperas en la sanidad?', opts=[
   O('ley', 'Una ley con tiempos máximos de espera', FA=('p', [2427])),
   O('primaria', 'Un plan de choque en atención primaria', PP=('p', [767]), VOX=('p', [404])),
   O('mir', 'Más plazas para formar médicos especialistas (MIR)',
     BILDU=('p', [68]), JUNTS=('p', [1697]), COMP=('p', [145])),
   O('privada', 'Derivar pacientes a la sanidad privada', VOX=('p', [409])),
 ]),
 dict(id='san_gestion', tema='sanidad', q='¿Quién debería gestionar la sanidad?', opts=[
   O('publica', 'Solo lo público: prohibir la gestión privada por ley',
     COMP=('p', [130]), BILDU=('p', [69]), FA=('p', [2418]), BNG=('p', [475])),
   O('estado', 'El Estado, recuperando las competencias de las comunidades', VOX=('p', [391])),
   O('comunidades', 'Las comunidades, también la formación de médicos', ERC=('p', [1376]), BNG=('p', [483]), PNV=('p', [860])),
 ]),
 dict(id='san_cartera', tema='sanidad', q='¿Qué debería añadirse a la sanidad pública?', opts=[
   O('dental', 'El dentista y la óptica', VOX=('p', [419]), BILDU=('p', [72])),
   O('mental', 'Más atención a la salud mental', BILDU=('p', [70]), COMP=('p', [138]), VOX=('t', [413]), PSOE=('t', [1713]), BNG=('t', [775])),
 ]),
 # ═══════════════ EDUCACIÓN ═══════════════
 dict(id='edu_centro', tema='educacion', q='¿Qué red escolar debería tener prioridad?', opts=[
   O('eleccion', 'Que las familias elijan centro, incluida la concertada', PP=('p', [887]), UPN=('p', [56])),
   O('cheque', 'Un cheque escolar para elegir colegio', VOX=('p', [236])),
   O('publica', 'La escuela pública, con la concertada solo como complemento',
     PSOE=('p', [1767]), BNG=('p', [428]), COMP=('p', [7]), FA=('p', [3989]), JUNTS=('t', [1767])),
 ]),
 dict(id='edu_inversion', tema='educacion', q='¿Dónde invertir en educación?', opts=[
   O('infantil', 'Escuelas infantiles gratuitas de 0 a 3 años',
     PP=('p', [874]), PSOE=('p', [651]), FA=('p', [326]), CC=('p', [88]), JUNTS=('t', [1769]), BNG=('t', [346])),
   O('becas', 'Más becas', FA=('p', [2739]), PP=('p', [912, 913]), VOX=('t', [242]), CC=('t', [93])),
   O('tasas', 'Una matrícula universitaria más barata para quien menos tiene', COMP=('p', [17])),
 ]),
 dict(id='edu_contenidos', tema='educacion', q='¿Quién debería decidir qué se enseña?', opts=[
   O('ebau', 'El Estado: la misma prueba de acceso a la universidad en toda España', PP=('p', [925])),
   O('aulas', 'Sacar de las aulas a asociaciones y activistas que den charlas ideológicas', VOX=('p', [235])),
   O('propio', 'Cada comunidad, con su propio sistema educativo', BNG=('p', [437, 442])),
 ]),
 # ═══════════════ CORRUPCIÓN Y POLÍTICA ═══════════════
 dict(id='dem_corrupcion', tema='corrupcion', q='¿Cómo prevenir la corrupción?', opts=[
   O('lobbies', 'Un registro público de lobbies y de con quién se reúnen', PSOE=('p', [4169]), PP=('p', [1253]), FA=('p', [3806])),
   O('puertas', 'Prohibir las puertas giratorias', ERC=('p', [599]), BNG=('p', [408]), PSOE=('p', [4170])),
   O('denunciantes', 'Proteger a quien denuncia la corrupción', FA=('p', [3129]), COMP=('p', [82])),
   O('aforados', 'Acabar con los aforamientos', PNV=('p', [260, 261]), PSOE=('p', [4227]), COMP=('t', [81])),
 ]),
 dict(id='dem_jueces', tema='corrupcion', q='¿Quién debería elegir al órgano de gobierno de los jueces (CGPJ)?', opts=[
   O('jueces', 'Los propios jueces', VOX=('p', [864])),
   O('cortes', 'Las Cortes, como ahora, y renovarlo ya', PSOE=('p', [4256]), JUNTS=('t', [438])),
   O('popular', 'Con más participación de la ciudadanía', COMP=('p', [215])),
 ]),
 dict(id='dem_indultos', tema='corrupcion', q='Indultos, amnistía y delitos del procés: ¿qué hacer?', opts=[
   O('limitar', 'Limitar los indultos del Gobierno', PP=('p', [1264]), FA=('t', [3373])),
   O('sedicion', 'Recuperar el delito de sedición y castigar los referéndums ilegales', PP=('p', [1201]), VOX=('p', [102])),
   O('amnistia', 'Una amnistía para los encausados por el procés', ERC=('p', [248]), JUNTS=('p', [253])),
 ]),
 dict(id='dem_electoral', tema='corrupcion', q='¿Qué cambiar en las elecciones?', opts=[
   O('voto16', 'Votar desde los 16 años', ERC=('p', [1153]), JUNTS=('p', [1549])),
   O('circ', 'Elegir los diputados por comunidades y no por provincias', COMP=('p', [69]), PNV=('t', [657])),
   O('exterior', 'Diputados propios para quienes viven en el extranjero', FA=('p', [3899])),
 ]),
 # ═══════════════ JÓVENES ═══════════════
 dict(id='jov_ayuda', tema='juventud', q='¿Qué ayuda daría más oportunidades a los jóvenes?', opts=[
   O('herencia', 'Una cantidad de dinero al llegar a la edad adulta', FA=('p', [495, 498])),
   O('avales', 'Avales para la hipoteca de la primera vivienda', PP=('p', [604]), PSOE=('p', [2249]), JUNTS=('p', [1537])),
   O('alquiler', 'Una ayuda mensual para el alquiler', PSOE=('p', [2247]), JUNTS=('p', [1536]), FA=('t', [2163])),
   O('becario', 'Prácticas pagadas: un estatuto del becario', PSOE=('p', [2218]), ERC=('p', [2772]), VOX=('t', [180])),
   O('primer', 'Programas para conseguir el primer empleo', FA=('p', [274]), COMP=('p', [109]), CC=('t', [80])),
 ]),
 # ═══════════════ IMPUESTOS ═══════════════
 dict(id='imp_fortunas', tema='impuestos', q='¿Qué hacer con los impuestos a las grandes fortunas?', opts=[
   O('subir', 'Un impuesto permanente a las grandes fortunas',
     FA=('p', [498]), ERC=('p', [277]), BILDU=('p', [91]), BNG=('p', [99]), COMP=('t', [194])),
   O('quitar', 'Suprimirlos, también el de Patrimonio', PP=('p', [365]), VOX=('p', [546])),
 ]),
 dict(id='imp_sucesiones', tema='impuestos', q='¿Qué hacer con el impuesto de herencias (Sucesiones)?', opts=[
   O('suprimir', 'Suprimirlo en toda España', VOX=('p', [546])),
   O('minimo', 'Un mínimo común para que las comunidades no lo rebajen a cero', FA=('p', [530]), COMP=('p', [192])),
 ]),
 dict(id='imp_renta', tema='impuestos', q='¿Qué hacer con el IRPF?', opts=[
   O('bajar', 'Bajarlo para todos', VOX=('p', [527, 528]), UPN=('p', [19])),
   O('familias', 'Rebajas por cada hijo', VOX=('p', [528])),
   O('progresivo', 'Que paguen más las rentas altas y menos las medias y bajas', COMP=('p', [137]), BNG=('p', [506]), PSOE=('t', [709])),
 ]),
 # ═══════════════ SEGURIDAD ═══════════════
 dict(id='seg_penas', tema='seguridad', q='¿Qué hacer con las penas de cárcel?', opts=[
   O('reincidencia', 'Penas más duras para los multirreincidentes en hurtos', PP=('p', [1379]), JUNTS=('p', [1927])),
   O('ampliar', 'Ampliar la prisión permanente revisable', PP=('p', [1381])),
   O('eliminar', 'Eliminar la prisión permanente revisable', FA=('p', [3501]), PNV=('p', [186]), BNG=('p', [381])),
   O('reinsercion', 'Más programas de reinserción', PSOE=('p', [4085]), FA=('p', [3499])),
 ]),
 dict(id='seg_protesta', tema='seguridad', q='Policía y derecho a la protesta: ¿qué cambiar?', opts=[
   O('mordaza', 'Derogar la «ley mordaza»',
     FA=('p', [3457]), ERC=('p', [449]), BILDU=('p', [138]), BNG=('p', [96]), COMP=('p', [64]), PNV=('t', [132]), JUNTS=('t', [427])),
   O('autoridad', 'Reforzar la autoridad de los agentes y castigar más la resistencia', PP=('p', [1354]), VOX=('p', [636])),
 ]),
 dict(id='seg_policias', tema='seguridad', q='¿Qué policía debería haber?', opts=[
   O('autonomica', 'Que las policías autonómicas asuman todas las competencias',
     BNG=('p', [212]), PNV=('p', [160]), JUNTS=('p', [361]), CC=('p', [192]), ERC=('t', [625])),
   O('suprimir', 'Suprimir las policías autonómicas', VOX=('p', [68])),
   O('equiparar', 'Igualar el sueldo de Policía Nacional y Guardia Civil con el de las autonómicas', PP=('p', [1351]), VOX=('p', [69])),
 ]),
 # ═══════════════ CLIMA, ENERGÍA Y AGUA ═══════════════
 dict(id='cli_nuclear', tema='clima', q='¿Qué hacer con las centrales nucleares?', opts=[
   O('alargar', 'Alargar su vida', PP=('p', [692]), VOX=('p', [811])),
   O('cerrar', 'Cerrarlas según el calendario previsto', FA=('p', [1360]), PSOE=('t', [1310])),
 ]),
 dict(id='cli_ritmo', tema='clima', q='¿A qué ritmo hacer la transición ecológica?', opts=[
   O('acelerar', 'Más deprisa: emisiones netas cero antes de 2050',
     BILDU=('p', [103]), FA=('p', [1160, 1164]), ERC=('t', [273]), BNG=('t', [602])),
   O('autoconsumo', 'Con autoconsumo y comunidades energéticas en cada pueblo y barrio', COMP=('p', [153]), FA=('t', [366])),
   O('pacto', 'Más despacio: flexibilizar el Pacto Verde europeo', PP=('p', [453])),
   O('combustion', 'No prohibir los coches de combustión', VOX=('p', [359])),
 ]),
 dict(id='cli_agua', tema='clima', q='¿Cómo asegurar el agua?', opts=[
   O('trasvases', 'Conectar las cuencas con trasvases', VOX=('p', [754, 1003]), PP=('t', [649]), COMP=('t', [164])),
   O('desalar', 'Desalar y reutilizar el agua', PSOE=('p', [1283, 1228])),
   O('caudales', 'Respetar el caudal ecológico de los ríos', ERC=('p', [2160]), JUNTS=('p', [2187, 1192])),
 ]),
 # ═══════════════ PENSIONES ═══════════════
 dict(id='pen_futuro', tema='pensiones', q='¿Qué es lo más importante en las pensiones?', opts=[
   O('ipc', 'Que suban siempre con el IPC',
     PSOE=('p', [2873]), FA=('p', [502]), BNG=('p', [282]), PNV=('p', [607]), JUNTS=('p', [1600]), CC=('p', [97]), PP=('t', [286])),
   O('minimas', 'Subir las pensiones mínimas y no contributivas',
     FA=('p', [503]), BILDU=('p', [54]), COMP=('p', [115]), BNG=('p', [117])),
   O('viudedad', 'Subir las pensiones de viudedad', BILDU=('p', [9]), PNV=('p', [593])),
   O('edad', 'No retrasar la edad de jubilación', BILDU=('p', [57]), BNG=('p', [283])),
   O('irpf', 'Que las pensiones no paguen IRPF', VOX=('p', [532])),
   O('empresa', 'Completarlas con planes de pensiones de empresa', PSOE=('p', [535])),
   O('propia', 'Que mi comunidad gestione su propia Seguridad Social', PNV=('p', [84]), BILDU=('p', [58]), BNG=('p', [278])),
 ]),
 # ═══════════════ POBREZA E IGUALDAD ═══════════════
 dict(id='des_pobreza', tema='desigualdad', q='¿Cómo reducir la pobreza?', opts=[
   O('imv', 'Que el Ingreso Mínimo Vital llegue a más personas', BILDU=('p', [84]), COMP=('p', [89]), JUNTS=('t', [1074])),
   O('crianza', 'Una ayuda por cada hijo hasta los 18 años', FA=('p', [499, 500]), ERC=('p', [1310])),
   O('empleo', 'Que las ayudas sirvan sobre todo para encontrar trabajo', PP=('p', [261, 279])),
   O('natalidad', 'Fomentar la natalidad', VOX=('p', [182]), JUNTS=('t', [1565])),
 ]),
 dict(id='des_genero', tema='desigualdad', q='¿Qué hacer con la ley de violencia de género?', opts=[
   O('reforzar', 'Mantenerla y reforzarla',
     PP=('p', [753]), PSOE=('p', [286]), JUNTS=('p', [1706]), BILDU=('p', [117]), PNV=('p', [94]),
     BNG=('p', [313]), CC=('p', [113]), COMP=('p', [229]), FA=('p', [2786]), ERC=('p', [1054, 1068])),
   O('derogar', 'Derogarla y aprobar una ley que proteja a todos por igual', VOX=('p', [74, 872])),
 ]),
 dict(id='des_aborto', tema='desigualdad', q='¿Qué hacer con el aborto?', opts=[
   O('publica', 'Garantizarlo en los hospitales públicos de todas las comunidades',
     FA=('p', [2910]), ERC=('p', [1002]), COMP=('p', [141]), PSOE=('t', [2355])),
   O('menores', 'Exigir el consentimiento de los padres a las menores de 16 y 17 años', PP=('p', [804])),
   O('derogar', 'Derogar la ley del aborto', VOX=('p', [418])),
 ]),
 # ═══════════════ TERRITORIO ═══════════════
 dict(id='ter_modelo', tema='territorio', q='¿Cómo debería organizarse España?', opts=[
   O('recentralizar', 'Devolver al Estado educación, sanidad, seguridad y justicia', VOX=('p', [52, 89])),
   O('autonomias', 'Mantener las autonomías y que colaboren más con el Estado',
     PSOE=('p', [3952]), CC=('p', [53]), UPN=('p', [11]), PP=('t', [1143])),
   O('plurinacional', 'Reconocer que España es un Estado plurinacional', FA=('p', [3182]), BILDU=('p', [153]), PNV=('p', [108])),
 ]),
 dict(id='ter_referendum', tema='territorio', q='¿Debería poder votar Cataluña, Euskadi o Galicia sobre su independencia?', opts=[
   O('si', 'Sí, en un referéndum de autodeterminación',
     ERC=('p', [223, 231]), JUNTS=('p', [212, 258]), BILDU=('p', [155]), BNG=('p', [182]), PNV=('t', [28])),
   O('no', 'No: castigar como delito convocar un referéndum así', VOX=('p', [102, 125]), PP=('t', [1201])),
 ]),
 dict(id='ter_financiacion', tema='territorio', q='¿Cómo deberían financiarse las comunidades autónomas?', opts=[
   O('comun', 'Un nuevo sistema común, negociado con todas', PP=('p', [1333]), CC=('p', [55]), COMP=('p', [183]), FA=('p', [597])),
   O('propia', 'Que cada comunidad recaude todos sus impuestos', JUNTS=('p', [927]), BNG=('p', [201, 504]), ERC=('t', [1436])),
   O('foral', 'Mantener el Concierto vasco y el Convenio navarro', PNV=('p', [44, 98]), UPN=('p', [9])),
   O('suprimir', 'Acabar con los regímenes forales', VOX=('p', [58])),
 ]),
 dict(id='ter_lenguas', tema='territorio', q='¿En qué lengua se debería estudiar en las comunidades con lengua propia?', opts=[
   O('castellano', 'Garantizar el castellano como lengua vehicular', VOX=('p', [217]), UPN=('t', [32])),
   O('ambas', 'Las dos lenguas oficiales como vehiculares', PP=('p', [892])),
   O('inmersion', 'Proteger la inmersión en la lengua propia', COMP=('p', [6]), ERC=('t', [267])),
 ]),
 dict(id='ter_lenguas_estado', tema='territorio', q='¿Qué papel deberían tener el catalán, el euskera y el gallego en el Estado?', opts=[
   O('uso', 'Que se puedan usar en toda la administración del Estado', BILDU=('p', [160]), PNV=('p', [147]), FA=('p', [3207, 3208])),
   O('medios', 'Más presencia en RTVE y los medios públicos', BNG=('p', [729, 730]), COMP=('p', [54])),
   O('requisito', 'Que no se exijan para trabajar en la administración', VOX=('p', [90]), UPN=('t', [32])),
 ]),
 # ═══════════════ EXTERIOR ═══════════════
 dict(id='ext_defensa', tema='exterior', q='¿Qué hacer con la defensa?', opts=[
   O('reforzar', 'Más soldados y más medios para las Fuerzas Armadas', PP=('p', [1593, 1729]), VOX=('t', [628])),
   O('industria', 'Impulsar la industria de defensa', PSOE=('p', [680]), PP=('t', [421])),
   O('menos', 'Menos gasto militar', BNG=('p', [119]), ERC=('p', [677, 678])),
   O('europa', 'Una defensa europea que dependa menos de la OTAN', FA=('p', [3659])),
 ]),
 dict(id='ext_sahara', tema='exterior', q='¿Qué posición debería tener España sobre el Sáhara Occidental?', opts=[
   O('autodeterminacion', 'Volver a defender un referéndum de autodeterminación',
     FA=('p', [3705, 3706]), ERC=('p', [707]), PNV=('p', [219, 220]), BNG=('p', [798]), COMP=('p', [252]), PP=('t', [1571])),
   O('actual', 'Mantener la posición actual y la nueva relación con Marruecos', PSOE=('p', [4505, 4510])),
 ]),
 dict(id='ext_ceuta', tema='exterior', q='¿Cómo proteger Ceuta y Melilla?', opts=[
   O('otan', 'Que queden bajo la protección de la OTAN', VOX=('p', [649])),
   O('militar', 'Desplegar el ejército en la frontera', VOX=('p', [638])),
   O('apoyo', 'Más apoyo del Estado a las dos ciudades', PP=('p', [1340])),
 ]),
]
