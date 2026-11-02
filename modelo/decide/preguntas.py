"""Draft questionnaire. Each option has a retrieval regex (matched on original text + text_en) used to find
candidate evidence; party assignments are decided by hand in posiciones.py after reading the evidence."""
Q = [
 # ---------- VIVIENDA ----------
 dict(id='viv_precio', tema='vivienda', q='¿Qué debería hacer el Estado con el precio del alquiler?', opts=[
   ('tope', 'Ponerle límite en las zonas donde más ha subido', r'(limit|tope|topar|contener|congel|regula|control).{0,40}(alquiler|lloguer|aluguer|\brent)|zonas? tensionad|zones tensionades|índice de (precios|referencia)|ley (estatal )?de vivienda|llei d.habitatge|lei de vivenda'),
   ('mercado', 'No tocar los precios: más oferta, más seguridad jurídica e incentivos a quien alquila', r'seguridad jur[ií]dica|(incentiv|bonific|deduc|ventaja).{0,60}(propietari|arrendador|alquil|lloguer)|derog.{0,40}(ley|norma).{0,20}vivienda|intervenci[oó]n de (los )?precios|control de precios|liberaliz.{0,30}suelo'),
 ]),
 dict(id='viv_dinero', tema='vivienda', q='¿En qué debería gastar más dinero público la política de vivienda?', opts=[
   ('parque', 'Un gran parque de vivienda pública de alquiler', r'parque (público|de vivienda|p[uú]blic)|vivienda (pública|social|protegida)|habitatge (públic|social|protegit)|vivenda (pública|social|protexida)|alquiler social|lloguer social|aluguer social|VPO'),
   ('compra', 'Ayudar a comprar: avales para la hipoteca y menos impuestos a la compra', r'\baval|garant[ií]a.{0,40}hipotec|primera vivienda|primer habitatge|primeira vivenda|transmisiones patrimoniales|\bITP\b|acceso a la propiedad|vivienda en propiedad|comprar (una|su) vivienda'),
   ('ayuda', 'Ayudas directas para pagar el alquiler', r'bono.{0,15}alquiler|ayuda.{0,25}alquiler|ajut.{0,25}lloguer|axuda.{0,25}aluguer|bo lloguer|bono joven'),
 ]),
 dict(id='viv_okupa', tema='vivienda', q='Ocupaciones ilegales y desahucios: ¿qué te preocupa más?', opts=[
   ('desalojo', 'Que se pueda desalojar en horas a quien ocupa una vivienda, con penas más duras', r'okupa|ocupaci[oó]n ilegal|ocupación de (la |su )?vivienda|ocupaci[oó] il|allanamiento|usurpaci|desalojo|desokup|24 horas|48 horas'),
   ('desahucio', 'Que no se desahucie a familias vulnerables sin una alternativa de vivienda', r'desahuc|desnonament|desnonaments|despexo|alternativa habitacional|alternativa residencial|lanzamiento'),
 ]),
 # ---------- INMIGRACIÓN ----------
 dict(id='inm_irregular', tema='inmigracion', q='¿Qué hacer con las personas que viven en España sin papeles?', opts=[
   ('regularizar', 'Regularizarlas y abrir vías estables para tener papeles', r'regulariz|regularitz|arraigo|arrelament|\bILP\b'),
   ('expulsar', 'Expulsarlas y endurecer el acceso a la residencia y la nacionalidad', r'deport|expuls|repatri|devoluci|inmigraci[oó]n ilegal|ilegales|nacionalidad'),
 ]),
 dict(id='inm_modelo', tema='inmigracion', q='¿Qué inmigración necesita España?', opts=[
   ('laboral', 'La que pida el mercado de trabajo, contratada en el país de origen', r'en origen|contrataci[oó]n en origen|gesti[oó]n colectiva|necesidades.{0,40}(laboral|mercado|econom)|migraci[oó]n (laboral|ordenada|legal)|talento'),
   ('afin', 'Prioridad a quien comparte idioma y cultura, con cupos por origen', r'hispanoam|iberoam|afinidad|cupo|asimilaci|integraci[oó]n.{0,40}(cultura|valores)|identidad'),
   ('derechos', 'Vías legales y seguras, acogida y cierre de los CIE', r'\bCIE\b|centros de internamiento|v[ií]as (legales|seguras)|acogida|acollida|racis|xenof|derechos de las personas migrantes'),
 ]),
 dict(id='inm_frontera', tema='inmigracion', q='¿Y en la frontera sur (Ceuta, Melilla, Canarias)?', opts=[
   ('control', 'Más control: vallas, devoluciones y vigilancia naval', r'frontera|valla|\bmuro|armada|devoluci|rechazo en frontera|blindar|control de fronteras|mafias'),
   ('reparto', 'Reparto obligatorio de los menores que llegan solos y más apoyo a Canarias, Ceuta y Melilla', r'menores (migrantes|no acompañados|extranjeros)|\bMENA|reparto|corresponsab|solidaridad.{0,40}(comunidades|territor|Estado)|contingencia migratoria'),
   ('cooperacion', 'Acuerdos con los países de origen y de tránsito', r'cooperaci[oó]n.{0,60}(origen|tránsito|África|Marruecos|terceros países)|pa[ií]ses de (origen|tránsito)|acuerdos de readmisi'),
 ]),
 # ---------- ECONOMÍA / COSTE DE LA VIDA ----------
 dict(id='eco_bolsillo', tema='economia', q='¿Qué haría más para que el sueldo llegue a fin de mes?', opts=[
   ('iva', 'Bajar el IVA de los alimentos y la energía', r'\bIVA\b.{0,60}(aliment|energ|luz|gas|electric|cesta|básic|higiene|carne|pescado)|\bIVE\b|tipo superreducido'),
   ('irpf', 'Bajar el IRPF a rentas medias y bajas y ajustarlo a la inflación', r'deflact|\bIRPF\b|tramos|rebaja fiscal|clases? medias?|mínimo personal|impuesto sobre la renta'),
   ('beneficios', 'Gravar los beneficios extraordinarios de energéticas, bancos y distribuidoras', r'beneficios (extraordinarios|caídos)|windfall|gravamen.{0,30}(banca|energ|entidades)|impuesto.{0,30}(banca|energ|distribu)|márgenes empresariales|márgenes de beneficio'),
 ]),
 # ---------- EMPLEO ----------
 dict(id='emp_cambio', tema='empleo', q='¿Qué cambio en el trabajo te importa más?', opts=[
   ('jornada', 'Trabajar menos horas por el mismo sueldo', r'reducci[oó]n de (la )?jornada|semana laboral|32 horas|37[,.]5|cuatro d[ií]as|4 d[ií]as|reducci[oó] de la jornada|jornada (laboral )?de'),
   ('smi', 'Subir el salario mínimo al 60 % del salario medio', r'salario m[ií]nimo|\bSMI\b|salari m[ií]nim|soldo m[ií]nimo|60 ?% del salario'),
   ('cotiz', 'Bajar las cotizaciones y los costes de contratar', r'cotizaci|cotitzaci|cargas sociales|costes laborales|cuña fiscal|coste de (la )?contrataci|bonificaci[oó]n.{0,30}contrat'),
   ('despido', 'Que despedir cueste más y vuelvan los salarios de tramitación', r'despid|acomiad|indemnizaci[oó]n por despido|salarios de tramitaci|causalidad del despido'),
 ]),
 dict(id='emp_autonomos', tema='empleo', q='Si trabajas por tu cuenta, ¿qué te ayudaría más?', opts=[
   ('cuota0', 'No pagar cuota si ganas menos del salario mínimo', r'aut[oó]nom.{0,80}(salario m[ií]nimo|SMI|exenci|cuota cero|no pagar)|cuota cero'),
   ('ingresos', 'Cotizar según lo que ingresas de verdad y tener mejor protección (paro, bajas)', r'ingresos reales|rendimientos reales|cese de actividad|protecci[oó]n social.{0,30}aut[oó]nom|incapacidad temporal.{0,30}aut[oó]nom'),
   ('burocracia', 'Menos papeleo, IVA de caja y no adelantar impuestos de facturas no cobradas', r'IVA de caja|criterio de caja|facturas no cobradas|morosidad|burocracia|cargas administrativas|declaraci[oó]n responsable|ventanilla única'),
 ]),
 # ---------- SANIDAD ----------
 dict(id='san_prioridad', tema='sanidad', q='¿Qué es lo primero que habría que hacer en la sanidad?', opts=[
   ('publica', 'Más dinero y personal para la sanidad pública, sin privatizar', r'atenci[oó]n primaria|atenci[oó] prim|privatiz|gesti[oó]n p[uú]blica|blindaje|sanidad p[uú]blica|sanitat p[uú]blica|sanidade p[uú]blica|% del PIB'),
   ('privada', 'Apoyarse en la sanidad privada para acortar las listas de espera', r'colaboraci[oó]n p[uú]blico.privada|concierto|sanidad privada|mutualismo|MUFACE|listas? de espera|llista d.espera|libre elecci[oó]n'),
   ('competencias', 'Dar a las comunidades más competencias y dinero para gestionar su sanidad', r'competencias? sanitari|transferencia.{0,40}(sanidad|MIR|salud|sanitat)|\bMIR\b|formaci[oó]n sanitaria especializada|traspàs.{0,30}(MIR|salut)'),
   ('estatal', 'Una sanidad coordinada por el Estado, con tarjeta única para toda España', r'tarjeta sanitaria [uú]nica|recentraliz|cartera (b[aá]sica|com[uú]n)|igualdad.{0,40}(sanitari|todos los españoles)|historia cl[ií]nica (digital )?(única|compartida)'),
 ]),
 # ---------- EDUCACIÓN ----------
 dict(id='edu_prioridad', tema='educacion', q='¿Qué debería priorizar la política educativa?', opts=[
   ('eleccion', 'Que las familias elijan centro, incluida la escuela concertada', r'libertad.{0,40}(elegir|elecci[oó]n)|elecci[oó]n de centro|concertad|cheque escolar|pin parental|derecho de los padres'),
   ('publica', 'Más inversión en la escuela pública y escuelas infantiles gratuitas de 0 a 3 años', r'\b0[ -]?(a )?3\b|cero a tres|escuela p[uú]blica|escola p[uú]blica|ensino p[uú]blico|educaci[oó]n p[uú]blica|5 ?% del PIB|gratuidad|gratu[iï]tat'),
   ('becas', 'Becas más altas y universidad sin tasas', r'\bbecas?\b|beques|bolsas? de estudo|matr[ií]cula|tasas universitarias|taxes universit'),
   ('exigencia', 'Más exigencia: evaluaciones comunes, esfuerzo y autoridad del profesor', r'esfuerzo|m[eé]rito|evaluaci[oó]n (externa|nacional|común)|pruebas? (externas?|nacionales?)|autoridad del profesor|excelencia|EBAU [uú]nica|selectividad [uú]nica'),
 ]),
 # ---------- JUVENTUD ----------
 dict(id='jov_ayuda', tema='juventud', q='¿Qué ayuda pública daría más oportunidades a los jóvenes?', opts=[
   ('herencia', 'Una cantidad de dinero al cumplir los 18 para estudiar o emprender', r'herencia universal|20[.]?000 euros|18 años.{0,60}(euros|ayuda|capital)|dote'),
   ('casa', 'Ayudas para la entrada de una casa o para el alquiler', r'(j[oó]venes|joves|mozos|xente nova).{0,80}(vivienda|alquiler|hipotec|habitatge|vivenda|lloguer)|(vivienda|alquiler|hipotec|habitatge|vivenda).{0,80}(j[oó]venes|joves|menores de 35)'),
   ('impuestos', 'Pagar menos impuestos los primeros años de trabajo', r'(j[oó]venes|joves|menores de (30|35)).{0,80}(IRPF|impuesto|fiscal|cotizaci)|(IRPF|impuesto|fiscal|cotizaci).{0,80}(j[oó]venes|menores de (30|35))'),
   ('empleo', 'Primer empleo con contrato estable y prácticas pagadas', r'primer empleo|primera experiencia|pr[aà]ctiques|pr[aá]cticas|becari|estatuto del becario|garant[ií]a juvenil'),
 ]),
 # ---------- PENSIONES ----------
 dict(id='pen_futuro', tema='pensiones', q='¿Cómo asegurar las pensiones?', opts=[
   ('ipc', 'Subirlas con el IPC y pagarlas con más ingresos públicos', r'\bIPC\b|revaloriz|destop|base m[aá]xima|cotizaci[oó]n m[aá]xima|\bMEI\b|mecanismo de equidad|poder adquisitivo de (las )?pensi'),
   ('privado', 'Completarlas con planes de empresa o ahorro privado', r'planes? de pensiones|capitalizaci|mochila|complementari|segundo pilar|pensi[oó]n privada|ahorro (para la )?jubilaci'),
   ('minimas', 'Subir las pensiones mínimas y de viudedad hasta un nivel digno', r'pensi[oó]n(es)? m[ií]nim|no contributiv|viudedad|viudez|umbral de (la )?pobreza|pensi[oó] m[ií]nim'),
   ('propia', 'Que mi comunidad gestione su propia Seguridad Social', r'caja [uú]nica|caixa [uú]nica|unidad de caja|transferencia.{0,40}(Seguridad Social|sistema de pensiones)|r[eé]gimen econ[oó]mico de la Seguridad Social|Seguretat Social (pròpia|catalana)'),
 ]),
 # ---------- IMPUESTOS ----------
 dict(id='imp_quien', tema='impuestos', q='¿Quién debería pagar más, o menos, impuestos?', opts=[
   ('ricos', 'Más las grandes fortunas, la banca y las grandes empresas', r'grandes fortunas|grans fortunes|grandes patrimonios|impuesto.{0,20}(patrimonio|riqueza)|tipo m[ií]nimo|grandes empresas|grans empreses|banca|multinacional|fiscalidad progresiva|progresividad'),
   ('todos', 'Menos todo el mundo: bajar el IRPF y quitar Patrimonio y Sucesiones', r'(suprim|elimin|bonific|rebaj|bajar|reducir|deflact).{0,40}(impuesto|IRPF|patrimonio|sucesiones|donaciones|presi[oó]n fiscal|tributos)|sucesiones|donaciones|infierno fiscal|presi[oó]n fiscal'),
   ('territorio', 'Que cada territorio recaude y decida sus impuestos', r'concierto|concert|cupo|hacienda propia|hisenda pròpia|facenda propia|agència tributària|agencia tributaria (propia|catalana|vasca)|axencia tributaria|soberan[ií]a fiscal|sobirania fiscal|recaptar.{0,30}tots els impostos'),
 ]),
 # ---------- CORRUPCIÓN Y DEMOCRACIA ----------
 dict(id='dem_corrupcion', tema='corrupcion', q='¿Qué haría más contra la corrupción y el mal funcionamiento de la política?', opts=[
   ('jueces', 'Que los jueces elijan a su órgano de gobierno y una Fiscalía más independiente', r'\bCGPJ\b|Consejo General del Poder Judicial|Consell General del Poder Judicial|jueces elijan|fiscal general|Fiscal[ií]a.{0,40}independ|independencia judicial|separaci[oó]n de poderes'),
   ('control', 'Más control: registro de lobbies, fin de los aforamientos y de las puertas giratorias', r'lobby|lobbies|grupos de inter[eé]s|aforament|aforamient|anticorrup|puertas giratorias|portes giratòries|denunciantes|alertadores|transparencia|transpar[eè]ncia'),
   ('electoral', 'Cambiar la ley electoral para que el voto valga lo mismo y con listas abiertas', r'ley electoral|llei electoral|lei electoral|sistema electoral|LOREG|proporcional|listas (abiertas|desbloqueadas)|circunscripci'),
   ('lawfare', 'Acabar con la persecución judicial a cargos políticos (amnistía, fin del lawfare)', r'amnist|lawfare|repressi[oó]|persecuci[oó].{0,30}(pol[ií]tic|judicial)|presos pol[ií]tics|exili|desjudicialitz'),
 ]),
 # ---------- SEGURIDAD ----------
 dict(id='seg_prioridad', tema='seguridad', q='¿Qué haría más por la seguridad en tu barrio o tu pueblo?', opts=[
   ('penas', 'Penas más duras, sobre todo para los multirreincidentes, y más agentes', r'multirreincid|reincid|prisi[oó]n permanente|endurec|cumplimiento [ií]ntegro|m[aá]s (agentes|polic[ií]as|efectivos)|plantillas?'),
   ('mordaza', 'Derogar la «ley mordaza» y apostar por la prevención', r'mordaza|mordassa|Ley Org[aá]nica 4/2015|LO 4/2015|seguridad ciudadana|seguretat ciutadana|seguridade cidad'),
   ('autonomica', 'Que las policías autonómicas asuman más competencias', r'\bMossos|Ertzaintza|Polic[ií]a Foral|Policia Canaria|Polic[ií]a Canaria|polic[ií]a (auton[oó]mica|integral|galega)|competencias.{0,40}seguridad|seguretat.{0,40}compet'),
   ('equiparacion', 'Equiparar el sueldo de Policía Nacional y Guardia Civil y reconocerla como profesión de riesgo', r'equipara|profesi[oó]n de riesgo|Guardia Civil|Polic[ií]a Nacional|Fuerzas y Cuerpos de Seguridad del Estado'),
 ]),
 # ---------- CLIMA Y ENERGÍA ----------
 dict(id='cli_nuclear', tema='clima', q='¿Qué hacer con las centrales nucleares?', opts=[
   ('alargar', 'Alargar su vida para tener energía estable y más barata', r'nuclear'),
   ('cerrar', 'Cerrarlas según el calendario previsto y sustituirlas por renovables', r'nuclear'),
 ]),
 dict(id='cli_ritmo', tema='clima', q='¿A qué ritmo hacer la transición ecológica?', opts=[
   ('acelerar', 'Más deprisa: más renovables y adelantar el fin de los combustibles fósiles', r'renovab|f[oó]sil|descarboni|neutralidad clim[aá]tica|emergencia clim[aá]tica|emerg[eè]ncia clim|autoconsum|comunidades energ|comunitats energ'),
   ('frenar', 'Más despacio: revisar la Agenda 2030 y el Pacto Verde, que perjudican al campo y a la industria', r'Agenda 2030|Pacto Verde|fanatismo|alarmis|ideolog[ií]a clim|religi[oó]n clim|globalis'),
   ('agua', 'Lo urgente es el agua: trasvases y grandes obras hidráulicas', r'trasvase|transvasament|Plan Hidrol[oó]gico|infraestructuras hidr[aá]ulicas|embalse|pantano|regad[ií]o|desaladora|interconexi[oó]n de cuencas'),
 ]),
 # ---------- DESIGUALDAD ----------
 dict(id='des_pobreza', tema='desigualdad', q='¿Cómo reducir la pobreza?', opts=[
   ('renta', 'Reforzar el Ingreso Mínimo Vital y dar una ayuda por cada hijo', r'Ingreso M[ií]nimo Vital|\bIMV\b|renta (b[aá]sica|garantizada|m[ií]nima)|renda (b[aá]sica|garantida|m[ií]nima)|prestaci[oó]n (universal )?por crianza|crianza|por hijo'),
   ('empleo', 'Crear empleo y ligar las ayudas a buscar trabajo', r'(condicion|vincul|lig).{0,40}(empleo|trabajo|inserci[oó]n)|paguitas|subsidi.{0,30}(trabaj|empleo)|la mejor pol[ií]tica social es el empleo|incentiv.{0,30}trabaj|compatib.{0,30}(empleo|salario)'),
   ('familia', 'Apoyar a las familias y la natalidad', r'natalidad|natalitat|cheque|familias numerosas|maternidad|demogr[aá]f|invierno demogr'),
 ]),
 dict(id='des_genero', tema='desigualdad', q='Sobre la violencia contra las mujeres, ¿con qué estás más de acuerdo?', opts=[
   ('reforzar', 'Mantener y reforzar las leyes contra la violencia de género', r'violencia (de g[eé]nero|machista|contra las mujeres)|viol[eè]ncia masclista|violencia machista|Pacto de Estado|violencias machistas'),
   ('intrafamiliar', 'Cambiarlas por una ley de violencia intrafamiliar que proteja a todos por igual', r'intrafamiliar|ideolog[ií]a de g[eé]nero|derog.{0,40}(violencia|igualdad|g[eé]nero)|presunci[oó]n de inocencia|denuncias falsas'),
 ]),
 # ---------- TERRITORIO ----------
 dict(id='ter_modelo', tema='territorio', q='¿Cómo debería organizarse España?', opts=[
   ('recentralizar', 'Devolver al Estado competencias como educación, sanidad o seguridad', r'recentraliz|devolver al Estado|devoluci[oó]n de (las )?competencias|Estado auton[oó]mico.{0,40}(fracas|insostenible)|ilegaliz|\b155\b|unidad de España'),
   ('autonomias', 'Mantener las autonomías y cumplir los estatutos y traspasos pendientes', r'Estado auton[oó]mico|estatut|traspas|transferencias pendientes|competencias pendientes|desarrollo estatutario|cogobernanza'),
   ('plurinacional', 'Reconocer que España es plurinacional y avanzar hacia un Estado federal', r'plurinacion|federal|naciones|reconocimiento nacional|realidad nacional|naci[oó]n vasca'),
   ('referendum', 'Que cada nación pueda decidir su futuro en un referéndum', r'autodetermin|refer[eè]ndum|referéndum|dret a decidir|derecho a decidir|independ[eè]ncia|independencia|sobiran'),
 ]),
 dict(id='ter_financiacion', tema='territorio', q='¿Cómo deberían financiarse las comunidades autónomas?', opts=[
   ('comun', 'Un nuevo sistema común para todas, con más recursos y sin privilegios', r'financiaci[oó]n auton[oó]mica|nivelaci[oó]n|igualdad entre (los )?españoles|privilegio|solidaridad interterritorial|infrafinanciaci|fondo de nivelaci'),
   ('singular', 'Que mi territorio recaude sus impuestos, como el País Vasco y Navarra', r'financiaci[oó] singular|finançament singular|concert econ[oò]mic|concierto (econ[oó]mico )?para|consorcio tributario|hisenda|facenda|agència tributària|recaptar|recadar|d[eè]ficit fiscal'),
   ('foral', 'Defender el Concierto vasco y el Convenio navarro tal como están', r'Concierto Econ[oó]mico|Convenio Econ[oó]mico|r[eé]gimen foral|derechos hist[oó]ricos|fueros|foralidad|Amejoramiento'),
 ]),
 dict(id='ter_lenguas', tema='territorio', q='¿Qué hacer con las lenguas en la escuela y las instituciones?', opts=[
   ('castellano', 'Garantizar que se pueda estudiar en castellano en toda España', r'castellano|lengua vehicular|25 ?%|lengua com[uú]n|español.{0,30}(escuela|vehicular|ense)'),
   ('propias', 'Proteger y reforzar el catalán, el euskera y el gallego (inmersión, oficialidad en Europa)', r'immersi|inmersi|catal[aà]\b|llengua catalana|galego|lingua galega|euskera|euskara|lengua propia|llengua pròpia|lingua propia|oficialitat|oficialidad|cooficial|plurilingüismo'),
 ]),
 # ---------- EXTERIOR ----------
 dict(id='ext_defensa', tema='exterior', q='¿Cuánto debería gastar España en defensa?', opts=[
   ('otan', 'Llegar al 2 % del PIB que pide la OTAN', r'2 ?%.{0,40}(PIB|defensa)|gasto (en )?defensa|despesa militar|presupuesto de defensa|inversi[oó]n en defensa|capacidades militares|Fuerzas Armadas'),
   ('paz', 'Gastar menos en armas y más en paz y cooperación', r'gasto militar|despesa militar|gasto en armamento|desarme|desarmament|cultura de paz|cultura de pau|pacifis|bases militares|antimilitar|salida de la OTAN|sortida de l.OTAN'),
 ]),
 dict(id='ext_marruecos', tema='exterior', q='Marruecos, el Sáhara Occidental, Ceuta y Melilla: ¿qué debería hacer España?', opts=[
   ('sahara', 'Volver a defender un referéndum de autodeterminación para el Sáhara', r'S[aá]hara|saharaui|Polisario|autodeterminaci[oó]n del pueblo saharaui'),
   ('firmeza', 'Firmeza con Marruecos: proteger Ceuta y Melilla e incluirlas bajo el paraguas de la OTAN', r'Ceuta|Melilla|soberan[ií]a.{0,30}(Ceuta|Melilla)|integridad territorial'),
   ('socio', 'Buena relación con Marruecos como socio clave en inmigración y comercio', r'Marruecos|Marroc|Magreb|socio estrat[eé]gico|relaci[oó]n.{0,30}Marruecos|vecino del sur'),
 ]),
]
