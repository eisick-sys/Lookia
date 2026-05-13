# CONTEXTO PROYECTO LOOKIA
> Pegar este archivo al inicio de cada sesión con Claude para retomar sin repetir contexto.

---

## ¿Qué es Lookia?
App de recomendación de outfits basada en personalidad, ocasión, mood, actividad y clima.
Desarrollada en Python + Streamlit. La usuaria no es programadora, aprendió con IA.

---

## Estructura de archivos

```
proyecto app/
├── app.py                  # UI principal (4 tabs)
├── models.py               # Clases: Garment, OutfitFeedback, UsedOutfit
├── constants.py            # Listas: categorías, colores, estilos, etc.
├── storage.py              # (legacy) Guardar/cargar JSON local — ya no se usa en producción
├── storage_cloud.py        # Operaciones CRUD contra Supabase (prendas, feedback, outfits, imágenes)
├── supabase_client.py      # Cliente Supabase + get_supabase_for_user(access_token)
├── auth_ui.py              # Pantalla de login/registro con Supabase Auth
├── weather.py              # Conexión OpenWeather (actual + pronóstico semanal)
├── migrate_local_data.py   # Script one-shot: sube JSON locales a Supabase (no va a producción)
├── test_outfit_coverage.py # Script de pruebas automatizadas del motor
├── requirements.txt
├── closet.json             # (legacy)
├── feedback.json           # (legacy)
├── used_outfits.json       # (legacy)
├── .env
├── .gitignore
├── engine/
│   ├── recommender.py      # Motor principal + explain_outfit_score
│   ├── generation/
│   │   ├── outfit_generation.py          # generate_outfits
│   │   ├── outfit_generation_selected.py # generate_outfits_from_selected_garment
│   │   └── week_plan.py                  # generate_week_plan
│   ├── occasion_rules.py
│   ├── category_rules.py
│   ├── scoring_components.py
│   ├── compatibility.py
│   ├── history_utils.py
│   ├── user_profile.py
│   └── selection_utils.py
└── utils/
    ├── garment_utils.py
    └── attribute_inference.py
```

---

## Variables de entorno (.env)
```
OPENWEATHER_API_KEY=tu_clave_aqui
LOOKIA_CITY=Punta Arenas
SUPABASE_URL=https://pkojtqwatctncuerilub.supabase.co
SUPABASE_KEY=sb_publishable_...          # anon/publishable key
SUPABASE_SERVICE_KEY=eyJ...              # service_role key (solo para scripts locales)
```
En Streamlit Cloud (rama version-sana) agregar también en Secrets:
```
LOOKIA_ENV = "production"
```

---

## Tabs de la app
1. **🌤️ Hoy** — Recomendador principal con clima real, ajustes manuales y prenda forzada
2. **👕 Mi clóset** — Galería de prendas con edición y análisis de inconsistencias
3. **➕ Agregar prenda** — Subida múltiple (hasta 5 fotos) + formulario individual
4. **📅 Planificador semanal** — Outfits para la semana evitando repetir prendas

---

## Orden de prioridad del motor
1. Ocasión
2. Clima
3. Mood
4. Actividad
5. Ajustes manuales

## Filosofía del motor
- El motor sugiere y advierte, pero la usuaria decide (botón "Mostrar de todos modos")
- Las recomendaciones son tan buenas como el clóset que las alimenta
- Flexibilidad sobre rigidez — nunca bloquear sin dar opción de forzar
- El motor no impone criterios estéticos — si la usuaria tiene una prenda, es porque la usa
- El feedback entrena el motor para personalizar según el estilo real de la usuaria
- Cada cambio en su lugar — las reglas van en el archivo que corresponde según arquitectura

---

## Estado del repositorio
- Rama activa de desarrollo: **main** (local, debug visible)
- Rama testers: **version-sana** (Streamlit Cloud, `LOOKIA_ENV=production`, debug oculto)
- Ambas ramas deben estar siempre sincronizadas (idénticas en código)
- Flujo correcto: desarrollar en main → push → mergear a version-sana → push
- Comando para correr la app: `python -m streamlit run app.py`
- Retomar Claude Code: `claude --resume [session_id]` o simplemente `claude` en la carpeta
- **SIEMPRE verificar que .env no esté en el commit antes de hacer push**

## Infraestructura Supabase
- **Proyecto:** `pkojtqwatctncuerilub` (Supabase)
- **Auth:** Supabase Auth (email/password). `auth_ui.py` maneja login/registro/logout.
- **Base de datos:** PostgreSQL en Supabase. Tablas: `garments`, `outfit_feedback`, `used_outfits`. Todas con RLS habilitado por `user_id`.
- **Storage:** Bucket `garment-images`. Ruta: `{user_id}/{image_name}`. Imágenes públicas, subida autenticada con `access_token`.
- **Cliente:** `supabase_client.py` — `get_supabase()` para operaciones de DB, `get_supabase_for_user(access_token)` para uploads de Storage.
- **Tabla `ignored_badges`:** `(id, user_id, garment_id, created_at)` con RLS.

---

## Notas técnicas importantes
- La app ya usa Supabase — JSON locales son legacy, no se leen en producción
- `wardrobe_images/` y `__pycache__/` no van al repositorio
- Claude Code tiende a incluir .env en commits — siempre verificar antes del push
- `supabase-py 2.3.5` instalado localmente (versiones más nuevas fallan en Python 3.14)

## ⚠️ Pendiente urgente
- **Moderación de fotos en subida:** no hay filtro de contenido en imágenes subidas. Implementar moderación (AWS Rekognition, Google Vision, o Anthropic) antes de guardar en Supabase Storage.

---

## Script de pruebas automatizado

`test_outfit_coverage.py` — itera ocasiones × moods × temps × lluvia y reporta combinaciones con < 3 outfits. Usa `SUPABASE_SERVICE_KEY` para bypassear RLS. Baseline actual: **48 fallos totales, 38 reales** (10 son early returns intencionales de `deporte+formal`). Los 38 restantes son todos limitación de clóset, no bugs del motor.

---

## Tabla de bugs y mejoras pendientes — v1.0.1

### 🔴 Crítico
| # | Ítem | Archivo(s) | Estado |
|---|------|-----------|--------|
| 1 | Moderación de fotos en subidas | `storage_cloud.py`, `app.py` | ⏳ Pendiente estratégico |

### 🟠 Alta prioridad / Motor
| # | Ítem | Archivo(s) | Estado |
|---|------|-----------|--------|
| 7 | Midlayer repetido a temp baja | `outfit_generation.py` | ✅ Resuelto |

### 🟡 Media prioridad / Motor
| # | Ítem | Archivo(s) | Estado |
|---|------|-----------|--------|
| 11 | Knitwear con vestidos elegantes | `compatibility.py` | ✅ Resuelto |
| 12 | Calzado plano trabajo+calor | `category_rules.py` | ✅ Resuelto |
| 13 | `taco_bajo` penalizado leve en cómodo (+20) | `scoring_components.py` | ✅ Resuelto |
| 14 | `taco_alto` penalizado cómodo (+50), bloqueado casi en relajado (+80) | `scoring_components.py` | ✅ Resuelto |
| 15 | Mayor diversidad de tops en mood urbano | `outfit_generation.py` | ✅ Dado por superado |
| 16 | Compatibilidad colores — 4+ cromáticos sin eje | `compatibility.py`, `scoring_components.py` | ✅ Resuelto |
| 17 | Frío extremo sin capa — forzar midlayer/outerwear temp ≤ 8° | `outfit_generation.py`, `outfit_generation_selected.py` | ✅ Resuelto |
| 35 | Chaleco cuello V — lógica de compatibilidad y scoring no implementada | `compatibility.py`, `scoring_components.py` | ⬜ Pendiente |
| 18 | Inconsistencia 2 vs 3 outfits entre tandas | ambos generation | ✅ Resuelto |
| 32 | Prenda forzada one_piece — 1 solo outfit | `outfit_generation_selected.py` | ✅ Resuelto |
| 33 | Vestido forzado gala/salida nocturna mood relajado → [] | ambos generation | ✅ Resuelto |
| 34 | Prenda forzada limita a 1 outfit — condición residual | `outfit_generation_selected.py` | ✅ Resuelto |

### 🟢 Baja prioridad / UI y clóset
| # | Ítem | Archivo(s) | Estado |
|---|------|-----------|--------|
| 19 | Ocasiones frecuentes del perfil ordenadas primero | `app.py` | ⬜ Post-React |
| 20 | Tip de pantys — máximo una vez por tanda | `app.py` | ⬜ Post-React |
| 21 | Formulario editar prenda — scroll automático | `app.py` | ⬜ Post-React |
| 22 | Destacar botones "Mi perfil" y "Qué es Lookia" | `app.py` | ⬜ Post-React |
| 23 | Verificar top leopardo (id 63) — tag urbano | Supabase | ⬜ Pendiente |
| 24 | Agregar sandalias, ballerinas, chalas | Supabase | ⬜ Pendiente |

### ⚙️ Técnico / Deuda
| # | Ítem | Archivo(s) | Estado |
|---|------|-----------|--------|
| 25 | Integración IA Anthropic — moderación + inferencia fotos | `storage_cloud.py`, `attribute_inference.py` | ⬜ Pendiente |
| 26 | Refactor `outfit_generation_selected.py` — duplicación | `outfit_generation_selected.py` | ⬜ Pendiente |
| 27 | Import `outfit_score` dentro de loop en `_generate_matrimonio_elegante` | `outfit_generation.py` | ⬜ Pendiente |
| 28 | Extraer `is_too_similar` a función standalone | ambos generation | ✅ Resuelto |
| 29 | Dividir `app.py` en módulos por tab | `app.py` | ⬜ Pendiente pre-React |
| 30 | Nueva subcategoría `chaleco_vestir` | `constants.py` | ⬜ Postergado a React |
| 31 | Migración React — UI definitiva | Proyecto nuevo | ⬜ Largo plazo |

---

## Historial de cambios por sesión

## Historial de cambios por sesión

### Sesión 1 — abril 2026
**Seguridad**
- ✅ API key movida de `app.py` a `.env`
- ✅ `.gitignore` creado con `.env`
- ✅ Ciudad hardcodeada movida a `.env` como `LOOKIA_CITY`

**Motor**
- ✅ Ajustes manuales de clima activados
- ✅ Interior + frío: fuerza al menos 1 outfit sin outerwear
- ✅ 24-25°C: mantiene opción de midlayer liviana
- ✅ `generate_outfits_from_selected_garment` reescrita para igualar lógica de `generate_outfits`
- ✅ Filtro `is_too_similar` relajado
- ✅ Gorro/beanie bloqueado en gala y matrimonio

**UI**
- ✅ Score eliminado de la UI (reemplazado por modo debug con toggle)
- ✅ Explicaciones con más variedad de lenguaje
- ✅ Tip de pantys con falda + frío/lluvia

---

### Sesión 2 — abril 2026
**Motor**
- ✅ Tacos penalizados con lluvia (+35) y mood cómodo (+50) en `practicality_penalty`
- ✅ `practicality_penalty` recibe `mood` como parámetro
- ✅ Vestido elegante bloqueado en trabajo + mood cómodo
- ✅ Pantalón buzo bloqueado en cita (salvo mood urbano)
- ✅ Zapatillas deporte bloqueadas en cita (salvo mood urbano)
- ✅ Mini/short bloqueados con temp <= 9°
- ✅ `garment_allowed_for_occasion` recibe `mood` y `temp`
- ✅ `occasion_rules.py` reordenado por ocasión

**UI**
- ✅ Tip de pantys extendido a short con frío/lluvia

---

### Sesiones 3–13 — abril 2026
*(ver historial completo en versiones anteriores del archivo)*

---

### Sesión 14 — abril 2026

**Inferencia de atributos**
- ✅ `infer_attributes_from_subcategory` — nueva función en `utils/attribute_inference.py` que aplica reglas deterministas por subcategoría para warmth, dress_level, sexiness y style
- ✅ Inferencia cruzada integrada en `infer_attributes_from_name` — complementa atributos None con reglas por subcategoría
- ✅ Keywords de jockey/gorra/cap/visera agregados a inferencia de categoría accessory y subcategoría gorro
- ✅ dress_level "relajado" agregado para subcategoría gorro en inferencia cruzada
- ✅ Re-inferencia de categoría y subcategoría al escribir nombre en formulario (`on_change=_reinfer_category_from_name`)
- ✅ dress_level, sexiness y waterproof ahora se aplican desde inferred en formulario individual
- ✅ sexiness se lee de inferred en bulk upload (antes hardcodeado a 0)
- ✅ warmth visible para one_piece en formulario de edición
- ✅ `infer_from_filename` eliminada (era código muerto)
- ✅ `wardrobe_images/` agregado a .gitignore y removido del tracking

**UI**
- ✅ "sport" → "Deporte" en toda la UI visible (STYLE_LABELS_ES en constants.py, format_func en selectboxes, mensajes de advertencia)

---

### Sesión 15 — abril 2026

**Motor — ocasión matrimonio (mejora mayor)**

Contexto: para matrimonio "relajado" el motor mostraba poleras y mocasines como primera opción. Se rediseñó la lógica para que los vestidos elegantes/cóctel dominen siempre los primeros 2 slots, con top+bottom arreglado como tercera opción.

**`engine/occasion_rules.py`**
- ✅ Hard block botines y botas para matrimonio/gala (a nivel de prenda individual)
- ✅ Hard block mocasines para matrimonio/gala

**`engine/scoring_components.py`**
- ✅ Penalty 999 para botas con vestido elegante/cóctel (irrompible)
- ✅ Boost -160 para vestidos elegante/cóctel en matrimonio
- ✅ Boost -60 para vestido casual en matrimonio

**`engine/outfit_generation.py`** (aplicado en `generate_outfits` y `generate_outfits_from_selected_garment`)
- ✅ one_piece candidatos ordenados por elegancia: vestido_elegante/cóctel primero, casual después
- ✅ Tops filtrados a `style: elegante/formal` + `dress_level: arreglado/elegante` cuando hay vestidos disponibles
- ✅ Bottoms filtrados a `style: elegante/formal` + `dress_level: arreglado/elegante`, excluyendo buzo/jogger/legging/short_casual/jeans
- ✅ Shoes filtrados: excluye mocasín, botín, bota, zapatilla_urbana, zapatilla_deporte
- ✅ `is_too_similar` relajado para one_piece en matrimonio/gala (permite 2 vestidos distintos)
- ✅ Reordenamiento `final_outfits`: vestidos al frente, 2 slots reservados para vestidos si hay ≥2 disponibles
- ✅ Loop de diversidad forzado: primeros 2 slots reservados para vestidos cuando hay ≥2 disponibles

**Supabase — datos**
- ✅ `aros` y `collar corazon dorado` actualizados: `dress_level: arreglado`, `style: elegante`

---

### Sesión 16 — abril 2026

**Motor — matrimonio mood urbano**

- ✅ Excepciones de calzado para matrimonio mood urbano en occasion_rules.py: botines y botas permitidos si dress_level in ["flexible", "arreglado", "elegante"]; mocasines permitidos sin restricción de dress_level; zapatilla_urbana permitida si dress_level in ["arreglado", "elegante"]
- ✅ Filtros de candidatos en outfit_generation.py (generate_outfits y generate_outfits_from_selected_garment): tops y bottoms aceptan estilo urbano además de elegante/formal en matrimonio mood urbano
- ✅ Filtros de candidatos: shoes en matrimonio mood urbano excluye solo zapatilla_deporte y zapatilla_urbana sin dress_level alto; permite zapatilla_urbana con dress_level arreglado/elegante
- ✅ Reordenamiento final desactivado para matrimonio mood urbano — outfits ordenados por score natural sin forzar vestidos al frente
- ✅ scoring_components.py: taco_alto penalizado +50 en matrimonio mood urbano; botin/zapato/mocasin bonificados -40; zapatilla_urbana arreglada/elegante bonificada -40
- ✅ Filtros de tops en matrimonio mood urbano exigen dress_level in ["arreglado", "elegante"] — tops flexible excluidos aunque tengan estilo urbano
- ✅ Loop inline de tops también actualizado con dress_level

**Prendas agregadas al clóset para pruebas**
- Camisa formal oscura (navy/negro) con secondary_styles urbano
- Pantalón vestir negro con secondary_styles urbano y elegante
- Zapato derby negro con secondary_styles urbano y elegante
- Zapatilla elegante crema con dress_level arreglado y style urbano
- Pantalón crema urbano con secondary_styles elegante y urbano

---

### Sesión 17 — abril 2026

**Motor — matrimonio mood urbano (continuación)**

- ✅ Pool de candidatos one_piece para matrimonio mood urbano ampliado: incluye prendas con style == "urbano" o "urbano" in secondary_styles, independiente de su subcategoría — en generate_outfits y generate_outfits_from_selected_garment
- ✅ Vestido urbano elegante agregado al clóset como one_piece vestido_casual, style urbano, secondary_styles [casual, elegante, formal], dress_level arreglado, warmth caluroso

**Pruebas completadas matrimonio + normal**

- ✅ URBANO 8°C sin lluvia — OK
- ✅ URBANO 8°C con lluvia — OK
- ✅ URBANO 33°C calor — OK

---

### Sesión 18 — abril 2026

**Motor — matrimonio mood urbano 24-25°C (fix midlayer)**

Problema: a 24-25°C el bloque `if temp >= 24` filtraba midlayer a `warmth == "caluroso"` únicamente, y todos los blazers del clóset tienen `warmth: medio`. Además, el branch `outerwear_required` consume el flujo con un `continue` sin iterar midlayer cuando el pool de outerwear está vacío (como ocurre a esa temperatura).

**`engine/outfit_generation.py`** (aplicado en `generate_outfits` y `generate_outfits_from_selected_garment`)
- ✅ Bloque `if temp >= 24`: para `matrimonio+urbano` filtra midlayer a `subcategory == "blazer"` con `[:1]`; resto de ocasiones mantiene `warmth == "caluroso"` con `[:2]`
- ✅ Dentro del branch `if outerwear_required:`, antes del `continue`: agrega iteración de midlayer (blazer) sin outerwear cuando `occasion == "matrimonio" and mood == "urbano" and temp >= 24` — necesario porque outerwear está en `optional` (no `required`) pero el pool queda vacío a esa temperatura, y el `continue` cortaba el flujo antes de llegar al bloque normal de midlayer

**`engine/scoring_components.py`**
- ✅ En `practicality_penalty`: blazer como midlayer en `matrimonio` a 24°+ recibe penalty 999 si hay `one_piece` con `warmth != "caluroso"` — bloquea vestido+blazer salvo que el vestido sea ligero

**Prendas agregadas al clóset**
- ✅ `blazer manga corta morado urbano` — subcategory: blazer, warmth: caluroso, style: urbano, dress_level: arreglado, secondary_styles: [elegante, formal]

**Pruebas completadas**
- ✅ URBANO 24-25°C — blazer aparece en outfit 1 con top+bottom, bloqueado con one_piece de warmth medio

**Deuda técnica registrada**
- ⬜ `generate_outfits_from_selected_garment` — equiparar TODAS las reglas de `generate_outfits` en una pasada dedicada (incluye fix matrimonio+urbano+calor y cualquier otra divergencia acumulada)

---

### Sesión 19 — abril 2026

**UI — tab3 Agregar prenda**
- ✅ Sección "Agregar fotos" renombrada a "Subida rápida" con caption descriptivo
- ✅ Sección "Agregar prenda manualmente" renombrada a "Agregar con formulario" con caption
- ✅ Orden del formulario: foto → nombre → caption inferencia → categoría → resto de campos
- ✅ Campo "Nombre de la prenda" destacado con fondo rosado (#fff0f3) y caption de inferencia arriba del input
- ✅ Mensaje de confirmación "Tu prenda quedó guardada" movido al final del formulario (via session_state + st.success post-rerun)
- ✅ Validación: impedir guardar prenda sin foto ni nombre, mostrar warning inline
- ✅ Inferencia de estilo principal desde nombre (infer_style_from_name en attribute_inference.py)

**UI — tab2 Mi clóset**
- ✅ Botón eliminar con confirmación via st.popover en formulario de editar prenda
- ✅ Botón eliminar directo en tarjeta de galería — descartado, pendiente migración a React
- ✅ Sección de estadísticas agregada al final del tab: título con fondo rosado, métricas (prendas, outfits registrados, estilo dominante), prendas más usadas y ocasiones más frecuentes

**Motor — matrimonio elegante**
- ✅ Fix diversidad de vestidos: matrimonio_forced ahora fuerza vestidos distintos en slots 1 y 2
- ✅ Fix vestidos elegantes/cóctel con calor: exentos de penalización warmth en matrimonio a temp >= 26 si warmth != "frio"
- ✅ Penalización zapato derby en matrimonio mood no urbano (+80)
- ✅ midlayer (blazer) agregado a optional de matrimonio en occasion_rules.py
- ✅ Filtro de midlayer en matrimonio: solo blazers elegantes/formales con dress_level arreglado/elegante, pool [:3]
- ✅ Fix blazer a 24°+: excepción para blazer caluroso aunque vestido sea warmth medio
- ✅ Fix flujo midlayer con one_piece en matrimonio elegante a todas las temperaturas
- ✅ max_same_midlayer = 1 cuando 24 <= temp <= 25, top_n en el resto — con tracking en matrimonio_forced
- ✅ midlayer vaciado cuando temp > 25 en matrimonio elegante

**Pruebas matrimonio elegante completadas**
- ✅ 5° sin lluvia — OK
- ✅ 5° con lluvia — OK (tip paraguas correcto)
- ✅ 31° calor — OK (vestidos dominan, fix warmth funcionando)
- ✅ 24-25° — OK (1 blazer caluroso aparece en 1 slot)
- ⬜ 16° — PENDIENTE: blazer negro y blazer gris tienen dress_level: flexible, no pasan filtro → corregir a arreglado en Supabase, luego verificar que los 3 outfits tengan blazer

### Sesión 20 — abril 2026

**Motor — matrimonio mood elegante**

- ✅ Blazers elegantes/formales filtrados en pool de midlayer para todos los rangos de temperatura (16°, 13°, <13°)
- ✅ max_same_shoes = 1 para matrimonio elegante
- ✅ max_same_midlayer = 1 cuando hay más de 1 blazer disponible en matrimonio elegante
- ✅ Boost -350 a vestidos elegantes/cóctel en matrimonio mood elegante (scoring_components.py)
- ✅ matrimonio_forced desactivado para mood elegante — vestidos dominan por scoring
- ✅ _max_forced_vestidos = 2 solo para moods que no sean urbano ni elegante
- ✅ Rotación de blazers y tacos funcionando a 16°C

**Pendiente matrimonio elegante (retomar desde cero próxima sesión)**
- ⬜ 3 vestidos en los 3 slots — el forzado rompe la rotación, el boost solo no es suficiente en todos los escenarios. Buscar enfoque distinto.
- ⬜ 1 abrigo elegante rotando en umbral 15-18°C — el trench domina scoring y aparece en todos los combos. Requiere penalización específica en scoring_components.py + lógica de pool.
- ⬜ Compatibilidad de colores — penalizar outfits con 4+ colores sin eje cromático claro (ej. vestido azul + tacos rojos + blazer blanco + abrigo café + pañuelo negro)
- ⬜ Continuar matriz de pruebas: 22-23°C, mood sexy, mood cómodo

---

### Sesión 21 — abril 2026

**Motor — matrimonio elegante (refactor completo)**

Problema raíz identificado: el motor genérico no podía garantizar vestidos en todos los slots 
para matrimonio elegante porque blusa+falda con buenos scores individuales superaban el boost 
de vestidos a temperaturas templadas. Después de múltiples intentos de parches, se decidió 
crear una función dedicada y separada.

**`engine/outfit_generation.py`**
- ✅ Nueva función `_generate_matrimonio_elegante` — maneja exclusivamente 
  `occasion == "matrimonio" and mood == "elegante"` con lógica propia y simple
- ✅ Base fija: vestido elegante/cóctel + taco alto/bajo o sandalia elegante. Siempre.
- ✅ Capas según temperatura:
  - `> 25°C` → vestido + tacos, sin capas
  - `24-25°C` → 1 blazer caluroso/medio en slot 0, resto sin blazer
  - `20-23°C` → 2 outfits con blazer, 1 sin blazer (slot 2 omite)
  - `13-19°C` → blazer elegante en todos los slots, sin abrigo
  - `< 13°C` → blazer elegante + abrigo elegante/formal en todos los slots
- ✅ Pool de abrigos filtrado: solo subcategory abrigo/trench con style no sport/urbano/casual
- ✅ Sin impermeable casual en matrimonio elegante (lluvia → mismo abrigo elegante + tip paraguas)
- ✅ Rotación por índice `i % len(pool)` — vestido distinto, taco distinto, blazer distinto por slot
- ✅ `random.shuffle(vestidos)` para variar orden entre tandas
- ✅ Llama a `outfit_score` real para scoring final
- ✅ Integrada en `generate_outfits` y `generate_outfits_from_selected_garment`
- ✅ `selected_garment` compatible (vestido/tacos/blazer/abrigo/accesorio) → úsarlo como base
- ✅ `selected_garment` incompatible (pantalón, etc.) → retorna `[], []` → UI muestra warning
- ✅ Limpieza de toda la lógica matrimonio elegante del motor genérico (bloques continue 
  en fallbacks, bloque vestido+blazer 13-23°C, ramas de temperatura específicas, 
  matrimonio_forced restaurado a `mood not in ["urbano", "elegante"]`)
- ✅ Sin vestidos elegantes en clóset → fallback automático al motor genérico en lugar de 
  retornar vacío (filosofía: nunca dejar a la usuaria sin opciones)
- ✅ Sin calzado elegante → retorna [], [] con mensaje de categoría faltante

**`engine/scoring_components.py`**
- ✅ Boost vestidos elegantes/cóctel en matrimonio restaurado a -160 (era -350 para elegante)
- ✅ Penalización zapato derby en matrimonio no urbano subida a 999 (hard block)

**`app.py`**
- ✅ Verificación de compatibilidad para matrimonio elegante con selected_garment:
  si la prenda no es vestido/tacos/blazer/abrigo/accesorio → warning "no es la elección 
  típica" + activa botón "Mostrar de todos modos"
- ✅ Al presionar "Mostrar de todos modos" con prenda incompatible → bypasea 
  `_generate_matrimonio_elegante` y usa motor genérico completo

**Matriz de pruebas completada y aprobada**
- ✅ 5°C sin lluvia
- ✅ 8°C sin lluvia  
- ✅ 10°C sin lluvia
- ✅ 9°C con lluvia
- ✅ 12°C sin lluvia
- ✅ 14°C sin lluvia
- ✅ 16°C sin lluvia
- ✅ 14°C con lluvia
- ✅ 17°C sin lluvia
- ✅ 18°C sin lluvia
- ✅ 20°C sin lluvia
- ✅ 22°C sin lluvia
- ✅ 23°C sin lluvia
- ✅ 24°C sin lluvia
- ✅ 25°C sin lluvia
- ✅ 28°C sin lluvia
- ✅ 31°C sin lluvia

---

### Sesión 22 — abril 2026

**UI — app.py**
- ✅ Emoji 💪 agregado al botón "Mostrar de todos modos"
- ✅ Emoji 📅 y `type="primary"` agregado al botón "Generar semana"
- ✅ Label `"Nombre de la prenda"` en `st.text_input` que tenía string vacío (eliminaba warning de accesibilidad)

**Motor — diagnóstico y refactor engine/outfit_generation.py**

Diagnóstico completo realizado sobre `generate_outfits` y `generate_outfits_from_selected_garment`: código muerto por dispatch matrimonio+elegante, ramas elif duplicadas, edge case lluvia+calor sin manejar, `is_too_similar` divergente entre funciones, y varias inconsistencias de mood.

- ✅ `mood in ["urbano", "elegante"]` reemplazado por `mood in ["urbano", "sexy"]` en 5 ocurrencias (L341, L650, L669, L1170, L1376) — matrimonio+sexy ahora tiene acceso a midlayer con lógica equivalente a urbano
- ✅ Rama `elif temp >= 22 and not rain` duplicada eliminada en ambas funciones — rango 16–23°C sin lluvia unificado en una sola rama
- ✅ Rama `elif rain and temp >= 16` agregada antes del `else` final en ambas funciones — corrige edge case donde lluvia con calor caía al pool de frío extremo (midlayer[:1] no frío + outerwear[:2])
- ✅ `is_too_similar` en `generate_outfits_from_selected_garment` sincronizada con versión de `generate_outfits`: agregadas regla fuerte `same_bottom_type + same_shoes_type`, regla suave `same_top + same_shoes`, y declaración de `same_one_piece`
- ✅ En **ambas** versiones de `is_too_similar`: agregadas reglas `same_top and same_one_piece` y `same_one_piece and same_shoes` (antes `same_one_piece` estaba declarado pero nunca usado)
- ✅ Rama muerta `mood == "elegante"` eliminada de `max_same_midlayer` — colapsado a expresión simple
- ✅ `mood not in ["urbano", "elegante"]` corregido a `mood != "urbano"` (L864)

**Pendientes anotados (no tocar aún)**
- ⚠️ Sort+shuffle inconsistente en `_generate_matrimonio_elegante` (sort de vestidos destruido por shuffle inmediato)
- ⚠️ Riesgo de recursión infinita si no hay vestidos en `_generate_matrimonio_elegante` (fallback llama a `generate_outfits` con mood="elegante" que volvería a llamar a `_generate_matrimonio_elegante`)
- ⚠️ Cardigan/midlayer repetido en múltiples outfits — problema de rotación

**Próxima sesión**
- Rondas de pruebas: matrimonio+sexy, matrimonio+cómodo, gala y deporte (todos los moods, todas las temperaturas)
- Post-pruebas: merge main → version-sana
- Post-merge: refactor `generate_outfits_from_selected_garment` (lógica duplicada con `generate_outfits`)

---

### Sesión 23 — abril 2026

**Motor — matrimonio mood cómodo (implementación completa)**

Contexto: el motor no tenía lógica propia para matrimonio+cómodo. Las prendas caían en el `else` genérico de elegante/sexy/relajado, el scoring con `mood_bonus` penalizaba prendas formales/elegantes, y no había filtros específicos de calzado ni one_piece para este mood.

**`engine/outfit_generation.py`** (aplicado en `generate_outfits` y `generate_outfits_from_selected_garment`)
- ✅ Bloque `elif mood == "comodo":` propio para one_piece en matrimonio: lista blanca `["vestido_casual", "enterito"]` — excluye vestido_elegante y vestido_coctel del pool
- ✅ Bloque `elif mood == "comodo":` propio para top/bottom en matrimonio: solo elegante/formal (sin urbano), dress_level arreglado/elegante/flexible
- ✅ Bloque `elif mood == "comodo":` propio para shoes en matrimonio: bloquea taco_alto y zapatilla_deporte; pool tomado del ranking completo `ranked["shoes"]` (no del slice); un representante por subcategoría via `_seen_subs`; `random.shuffle` para variar entre tandas
- ✅ `max_same_shoes = 1` para matrimonio+cómodo (forzar variedad de calzado por outfit)
- ✅ Bloques inline de tops y bottoms en loops: condición ampliada a `mood in ["urbano", "comodo"]` para el `else` permisivo; ambos moods aceptan dress_level flexible en el `else`
- ✅ Forzado de vestidos desactivado para cómodo: `mood not in ["urbano", "comodo"]` en bloques de reordenamiento final y matrimonio_forced

**`engine/occasion_rules.py`**
- ✅ Zapatilla_urbana arreglada/elegante permitida para `mood in ["urbano", "comodo"]`
- ✅ Botín y bota permitidos para `mood in ["urbano", "comodo"]` con cualquier dress_level (relajado a elegante)
- ✅ Mocasín permitido para `mood in ["urbano", "comodo"]`
- ✅ Excepción en `blocked_by_occasion`: dress_level "relajado" no bloquea shoes botin/bota/zapato/mocasin cuando `occasion == "matrimonio" and mood == "comodo"`

**`engine/scoring_components.py`**
- ✅ `mood_bonus` recibe `occasion: str = ""` como parámetro
- ✅ Branch `if mood == "comodo" and occasion == "matrimonio":` en mood_bonus: strong = ["formal", "elegante"], soft = dress_level arreglado/flexible
- ✅ `practicality_penalty`: bloque matrimonio+comodo penaliza taco_alto (+80) y vestido_elegante/vestido_coctel (+70)
- ✅ Hard block zapato derby (`penalty += 999`) ampliado a `mood not in ["urbano", "comodo"]` — zapato derby permitido en matrimonio+cómodo

**`engine/recommender.py`**
- ✅ Las 5 llamadas a `mood_bonus` actualizadas a `mood_bonus(g, mood, occasion=occasion)`

**Estado WIP**
- ⚠️ PENDIENTE: resultados aún pueden mostrar demasiado zapato derby y zapatilla elegante en algunos clósets — ajuste fino de scores pendiente
---

### Sesión 24 — abril 2026

**Motor — matrimonio mood cómodo (fixes y validación completa)**

- ✅ occasion_rules.py: matrimonio ya no está exento de outerwear obligatorio con lluvia (solo gala queda exento)
- ✅ outfit_generation.py: filtro de impermeables para matrimonio+lluvia — excluye style sport y dress_level relajado
- ✅ outfit_generation.py: midlayer permitido en loop one_piece para matrimonio+cómodo (agregado "comodo" a la excepción)
- ✅ outfit_generation.py: bloque else de temperatura no corta midlayer pool cuando occasion == "matrimonio"
- ✅ outfit_generation.py: _force_mid_outer generalizado a todos los moods de matrimonio a temp ≤ 12° (antes solo cómodo)
- ✅ outfit_generation.py: _force_mid_outer aplicado también en bloques outer+acc y mid+acc para evitar escapes
- ✅ scoring_components.py: impermeables no penalizados en matrimonio cuando llueve
- ✅ category_rules.py: boost +35 a blazer en matrimonio+cómodo con temp ≤ 15°
- ✅ _generate_matrimonio_elegante: filtra outfits con score <= -999 antes de retornar
- ✅ max_same_midlayer = 1 para matrimonio+cómodo cuando hay 2+ blazers disponibles

**Diagnóstico completo ejecutado post-fixes**
- ✅ Blazer consistente en todos los moods a temp ≤ 15° (relajado sin forzado — esperado)
- ✅ Blazer+abrigo en todos los moods a temp ≤ 12°
- ✅ Outerwear consistente en todos a temp ≤ 10°
- ✅ Variedad de calzado y outerwear en los 3 slots
- ✅ Impermeable elegante con lluvia (no sport/relajado)
- ✅ Cómodo 3°/7° produce 2 outfits con armario sintético — esperado, en producción hay más prendas


---

### Sesión 25 — abril 2026 — Fixes matrimonio + preparación gala

**Fixes aplicados y mergeados a main:**
- Fix B1: shuffle antes de sort en `_generate_matrimonio_elegante` para variar vestidos entre tandas
- Fix B2: fallback cuando `result` queda vacío (no solo cuando no hay vestidos) → usa `mood="sexy"` como fallback
- Fix C1: `max_same_midlayer` escalonado para matrimonio (1 con 3+ blazers, 2 con 2 blazers, top_n con 1)
- Fix C2: pool de midlayer ampliado a `[:4]` para matrimonio a 16°+ (antes `[:1]` bloqueaba variedad)
- Fix C3: `max_same_one_piece=1` para evitar repetir vestidos entre outfits
- Fix C4: threshold permisivo 0.20 para matrimonio (vs 0.35 general)
- Fix C5: hard block zapato derby y mocasín en matrimonio+sexy (`occasion_rules.py` y `scoring_components.py`)
- Fix C6: corregir doble conteo de shoes/midlayer/outerwear_usage en bloque matrimonio_forced
- Fix C7: relajar `_outerwear_limit` en tercera pasada para matrimonio
- Fix C8: `_outerwear_limit` relajado permite enterito aparecer con tacos en sexy+5°

**Estado matrimonio:** todos los moods generan 3 outfits en temperaturas normales. Limitación aceptada: urbano+5° repite vestido casual (solo hay uno en el clóset para ese mood/temp).

**Próxima ocasión: GALA**

Diseño acordado:
- Moods permitidos: elegante, sexy, cómodo (con restricciones), urbano (excepción especial)
- Moods bloqueados: relajado
- Solo one_piece: vestido_elegante y vestido_coctel (sin enterito, sin vestido_casual)
- Excepción urbano: permite vestido_coctel + zapatilla_urbana con dress_level arreglado/elegante + blazer elegante obligatorio. Sin top+bottom.
- Calzado: solo tacos y sandalias elegantes (sin derby, sin mocasín, sin zapatilla_deporte)
- Abrigo: solo elegante (abrigo de gala, trench) — sin parka, sin impermeable
- Sin fallback a top+bottom — si no hay vestido elegante/cóctel, mostrar mensaje directo

---

### Sesión actual (abril 2026) — Gala implementada y validada

**`engine/outfit_generation.py`**
- ✅ `_generate_gala` — función dedicada para `occasion == "gala"`, análoga a `_generate_matrimonio_elegante`
- ✅ Pools: `vestido_elegante` / `vestido_coctel` obligatorio. Sin top+bottom, sin enterito, sin midlayer
- ✅ Calzado por mood: elegante/sexy → taco_alto, taco_bajo, sandalia; cómodo → taco_bajo, sandalia; urbano → tacos + zapatilla_urbana arreglada/elegante
- ✅ Outerwear por mood: elegante/sexy/cómodo → `abrigo/chaqueta/bolero` con estilo elegante o formal, sin impermeable; urbano → además permite `trench` sin restricción de estilo
- ✅ Sandalia pre-filtrada del pool cuando `temp <= 10` (evita que consuma un slot con score -999)
- ✅ Loop `for i in range(top_n)` — siempre intenta 3 outfits ciclando vestidos disponibles (fix: antes usaba `range(min(top_n, len(vestidos)))`)
- ✅ `abrigos_todos` reinsertado después del sort cuando hay `selected_garment` outerwear — garantiza que aparezca en primer slot (bug pendiente: solo outfit 1, no los 3; ver pendientes)
- ✅ `selected_garment` trench rechazado si `mood != "urbano"` → retorna `[], []`
- ✅ mood `relajado` bloqueado al inicio de la función
- ✅ Dispatched desde `generate_outfits` cuando `occasion == "gala"`
- ✅ Boost vestido_coctel primero en `sexy` y `urbano` mediante sort estable

**`engine/occasion_rules.py`**
- ✅ Excepción `zapatilla_urbana` extendida de `occasion == "matrimonio"` a `occasion in ["matrimonio", "gala"]`
- ✅ Bloque `zapato` (subcategory) agregado: bloqueado en matrimonio/gala salvo `mood in ["urbano", "comodo"]`

**`engine/scoring_components.py`**
- ✅ Boost gala para vestido_elegante/coctel (`penalty -= 180`)
- ✅ Boost `sexy` extendido a gala, salida nocturna y cita

**`app.py`**
- ✅ Bloque compatibilidad `selected_garment` para gala: acepta vestido/calzado/abrigo+chaqueta+bolero/accesorio; trench solo en urbano
- ✅ Warning específico para trench forzado en mood no-urbano: `"no va con gala {mood}"`
- ✅ Warning gala sin vestidos distingue mood relajado vs. sin prenda elegante en clóset
- ✅ "Mostrar de todos modos" visible en gala incluso sin `selected_garment`

**`constants.py`**
- ✅ `bolero` agregado a `SUBCATEGORY_OPTIONS["outerwear"]` y `SUBCATEGORY_LABELS_ES`
- ✅ Aliases de color femeninos: blanca, negra, roja, rosada, morada, amarilla

**`utils/attribute_inference.py`**
- ✅ `"bolero": ["bolero"]` agregado a `subcategory_keywords["outerwear"]`

**Matriz de validación gala completada (37 casos)**
- ✅ Casos 1–9: relajado bloqueado, elegante/sexy/cómodo/urbano a distintas temperaturas y lluvia
- ✅ Casos 10–28: temperaturas extremas, lluvia, calzado específico, outerwear bolero/chaqueta, accesorios, prenda forzada
- ✅ Casos 29–37: trench excluido en elegante/sexy/cómodo, permitido en urbano; prenda forzada trench; bolero; clima extremo
- ✅ False positive #21 identificado: chaqueta de cuero (style=casual) detectada por check sin filtro de estilo → no hay fix de producción

**⚠️ Bug pendiente — prenda forzada outerwear en gala**
Cuando `selected_garment` es un outerwear (abrigo, chaqueta, bolero), la lógica actual lo reinserta al frente del pool después del sort, pero el loop `abrigos[i % len(abrigos)]` cicla por todo el pool. Resultado: solo aparece en outfit 1. Fix requerido: cuando hay `selected_garment` outerwear, restringir `abrigos = [selected_garment]` o forzar en cada iteración del loop.

---

### Sesión 26 — abril 2026 — mood formal + fixes outerwear trabajo + mejoras inferencia

**`constants.py`**
- ✅ `"formal"` agregado a `MOOD_OPTIONS`; `"formal"` eliminado de `ACTIVITY_OPTIONS` → ahora `["normal", "caminar", "entrenar"]`
- ✅ `"lunares"` agregado a `PATTERN_OPTIONS`

**`engine/scoring_components.py`**
- ✅ `mood_map["formal"]` agregado en `mood_bonus()`: strong → elegante/formal, soft → urbano
- ✅ Jeans penalty extendido a `mood in ["elegante", "sexy", "formal"]`
- ✅ Falda boost extendido a `mood in ["elegante", "sexy", "formal"]`
- ✅ Taco boost `-40` para `mood == "formal"` en `practicality_penalty()`
- ✅ `activity_bonus()`: bloque `activity == "formal"` eliminado de `activity_bonus()`

**`engine/occasion_rules.py`**
- ✅ Firma extendida con `activity: str = ""`
- ✅ Regla global: `mood == "formal"` bloquea prendas con estilo sport (excepto shoes/accessory)
- ✅ Regla global: `activity == "caminar"` bloquea sandalia
- ✅ `work+comodo`: `one_piece` con `dress_level in ["elegante", "arreglado"]` bloqueado

**`engine/category_rules.py`**
- ✅ `shoe_context_penalty()`: condición +14 extendida a `mood in ["elegante", "formal"]` para tacos en trabajo

**`engine/outfit_generation.py`**
- ✅ Filtro formal shoes: bloquea converse y zapatilla_deporte; bloquea zapatilla_urbana sin estilo elegante/formal salvo `occasion in ["casual", "deporte"]`
- ✅ `max_same_shoes_heel`: escape condition (opción B) para formal — limita a 1 heel outfit solo si hay ≥2 non-heel
- ✅ `max_same_outerwear`: escape condition para no-rain — limita a 1 solo si hay ≥2 outerwear candidatas
- ✅ Filtro outerwear 13–15°: `_allow_cold` extendido a `mood in ["elegante", "formal", "comodo"]`; filtro trabajo abrigos elegantes sin secondary "formal" aplicado antes del `[:4]`
- ✅ Filtro outerwear frío extremo (else): mismo filtro de trabajo abrigos elegantes sin secondary "formal"
- ✅ Pool inicial outerwear ampliado a `[:8]` antes del filtro de temperatura

**`engine/recommender.py`**
- ✅ `explain_outfit_score()`: eliminado texto "Funciona bien para la actividad 'normal'" del random.choice

**`app.py`**
- ✅ Actividades disponibles condicionales: `caminar` solo en moods relajado/urbano/cómodo o casual/deporte; `entrenar` solo en deporte — aplicado en recomendador principal y planificador
- ✅ `_reinfer_from_edit_name()`: re-inferencia completa al editar nombre (categoría, subcategoría, color, patrón, warmth, dress_level, sexiness) con on_change
- ✅ Widgets del formulario de edición leen desde `st.session_state` con fallback a `garment.*`

**`utils/attribute_inference.py`**
- ✅ Keywords `"lunares"` agregados: ["lunares", "lunar", "puntos", "polka", "polka dot", "dots"]
- ✅ `"poncho"` confirmado en `subcategory_keywords["outerwear"]`; agregado a `cold_keywords` y `warmth_map["poncho"] = "frio"`

**Bloque 7 completado:**
- ✅ 7.1 matrimonio + elegante — OK
- ✅ 7.2 gala + sexy — OK
- ✅ 7.3 trabajo + cómodo — OK (deuda menor: rotación de bottoms)
- ✅ 7.4 actividad "formal" nunca aparece en UI — OK
- ✅ 7.5 sin errores/crashes — OK

**⚠️ Deuda técnica prioritaria próxima sesión (primera parte)**
- 🎯 Rotación de bottoms — pantalón vestir negro y falda negra larga dominan en moods formales/elegantes, generando 1–2 outfits en lugar de 3

**Fixes adicionales sesión 26 (continuación)**

**`app.py`**
- ✅ `default_wardrobe()` eliminada — era código muerto legacy de antes de Supabase (160 líneas)
- ✅ Nombre de prenda capitalizado al guardar (`.strip().capitalize()`) en formulario agregar y editar
- ✅ `_reinfer_from_edit_name` actualiza también `edit_style_{garment.id}` — gap corregido
- ✅ Selectbox de estilo en edición lee desde `st.session_state` con fallback a `garment.style`

**`utils/attribute_inference.py`**
- ✅ Inferencia cruzada `dress_level` ← estilo — cuando `dress_level` queda `None` o `flexible` con estilo elegante/formal, se sube a `arreglado`
- ✅ Aliases de color ampliados — femeninos (dorada, plateada), chilenismos (naranjo, camel, arena, tostado, nude, palo de rosa, terracota→café, salmón→naranja, coral→rosado, turquesa→celeste, granate→burdeo, etc.)
- ✅ `"poncho"` agregado a `cold_keywords` y `warmth_map`

**`engine/occasion_rules.py`**
- ✅ Bloqueo prendas sport en mood formal implementado

**Supabase**
- ✅ Script `capitalize_garment_names.py` ejecutado — 156 nombres de prendas existentes capitalizados

**Limpieza de código muerto**
- ✅ `from unicodedata import category` eliminado de `recommender.py`
- ✅ `is_shoe_high_heel()` e `is_shoe_low_heel()` eliminadas de `garment_utils.py`
- ✅ Condiciones redundantes simplificadas en `occasion_rules.py` y `category_rules.py`
- ✅ Prints de debug eliminados de `outfit_generation.py` y `recommender.py`

---

## Sesión 27 — abril 2026

### Ocasión deporte — mejoras de calzado
- ✅ `occasion_rules.py`: bloqueo de calzado por actividad en deporte — entrenar solo `zapatilla_deporte`, caminar `zapatilla_deporte` + `zapatilla_urbana`, normal `zapatilla_deporte` + `zapatilla_urbana` básica (sin converse, sin elegante, sin `dress_level` arreglado/elegante)
- ✅ `recommender.py` (`rank_garments`): excepción en filtro sport para zapatilla urbana básica en deporte+normal — permite entrada al ranking sin style sport

### Gala — capa ligera 16–22°
- ✅ `outfit_generation.py` (`_generate_gala`): nuevo pool `capas_ligeras` para rango 16–22° — bolero (`midlayer`) o chaqueta (`outerwear`) con `style elegante` sin secondary casual/sport/urbano; `usar_abrigo` ajustado a `temp ≤ 15°`
- ✅ `constants.py`: `"bolero"` movido de `SUBCATEGORY_OPTIONS["outerwear"]` a `SUBCATEGORY_OPTIONS["midlayer"]`; label agregado en `SUBCATEGORY_LABELS_ES`

**⚠️ Deuda técnica prioritaria próxima sesión**
- 🎯 Rotación de categorías — implementar `bottom_usage` y mecanismo de diversidad forzada genérica para todas las categorías (bottom, midlayer, outerwear). Causa raíz de outfits con 1–2 resultados y prendas que nunca aparecen
- ⬜ Refactor `generate_outfits_from_selected_garment` — ~430 líneas duplicadas con `generate_outfits`. Sesión dedicada con batería de pruebas completa
- ⬜ Extraer `is_too_similar` a función standalone (cambio seguro, pendiente)
- ⬜ Extraer filtro accesorios duplicado en `_generate_matrimonio_elegante` y `_generate_gala` (cambio seguro, pendiente)
- ⬜ Rotación de bottoms — pantalón vestir negro y falda negra larga dominan en moods formales/elegantes
- ⬜ Outerwear faltante a temperaturas bajas con actividad caminar

---

### Sesión 28 — abril 2026

**Versión**
- ✅ `APP_VERSION = "1.0.0"` agregado en `app.py`; `st.caption(f"v{APP_VERSION}")` al final del sidebar

**Fix lluvia + calor (`engine/outfit_generation.py`)**
- ✅ Bug: cuando `rain=True` y `temp >= 24`, el bloque `elif temp >= 24` vaciaba outerwear sin considerar lluvia, dejando al usuario sin abrigo impermeable
- ✅ Fix: nuevo branch `if temp >= 24 and rain:` antes del `if temp >= 24:` — mantiene solo impermeables livianos (waterproof + warmth caluroso/medio), vacía midlayer; aplicado en `generate_outfits` y `generate_outfits_from_selected_garment`
- ✅ Tip en `app.py`: "Con este calor no necesitas abrigo, pero no olvides llevar paraguas" cuando `temp >= 24 and not has_any_outer`
- ✅ Umbral tip de falda/short cambiado de `temp <= 16` a `temp <= 20`

**Fixes accesorios (`engine/category_rules.py`)**
- ✅ `should_include_accessory`: bufanda bloqueada a `temp >= 18`; gorro de invierno bloqueado a `temp >= 18`; jockey bloqueado a `temp >= 22` (antes `>= 20 and not rain`)
- ✅ `accessory_relevance_penalty`: jockey bloqueado a `temp >= 22` (incondicionalmente); gorro invierno bloqueado a `temp >= 18` (incondicionalmente, antes incluía `and not rain`)
- ✅ `outerwear_context_penalty`: bloque `is_formal_coat` agregado — penaliza abrigo elegante/formal en deporte, casual relajado y ocasiones sin formalidad

**Nuevas subcategorías**
- ✅ `jardinera` (bottom): constants, labels, inferencia, attribute_inference, occasion_rules
- ✅ `camisón` (midlayer): constants, labels, inferencia, attribute_inference
- ✅ `ballarina` (shoes): constants, labels, inferencia, `is_shoe_ballet_flat()` en garment_utils, occasion_rules
- ✅ `polera_deporte` (top): constants, labels, inferencia, category_rules (bonus +12 en deporte, penalty +20 fuera de deporte/casual), occasion_rules (bloqueada fuera de deporte/casual)
- ✅ `impermeable_deporte` (outerwear): constants, labels, inferencia, category_rules (bonus en deporte/lluvia, penalty en elegante/formal), occasion_rules (bloqueado en matrimonio/gala/cita elegante/nocturna elegante)

**`engine/compatibility.py`**
- ✅ Vestido elegante/cóctel penaliza calzado que no sea elegante/formal: zapato/botín sin estilo elegante → -22; bota sin estilo elegante → -28

**`engine/category_rules.py` — `one_piece_context_bonus`**
- ✅ Boost vestido_elegante/coctel cambiado de incondicional (+25) a condicional: `occasion_match AND mood_match → +25`; `occasion_match AND mood not in ["comodo","relajado"] → +12`

**`engine/occasion_rules.py`**
- ✅ Trabajo + enterito: bloqueado salvo `mood == "sexy"`
- ✅ Trabajo + short/falda corta: umbral temperatura según mood — `24°` si relajado/cómodo, `27°` si otros
- ✅ Salida nocturna + polar: bloqueado cuando `mood == "elegante"`
- ✅ `impermeable_deporte`: bloqueado en matrimonio/gala; bloqueado en cita/nocturna/trabajo con mood elegante/formal/sexy
- ✅ `polera_deporte`: bloqueada fuera de deporte/casual
- ✅ `jardinera`: bloqueada con lluvia y temp ≤ 13°; bloqueada en matrimonio/gala si dress_level relajado/flexible
- ✅ `ballarina`: bloqueada en deporte y actividad entrenar; bloqueada con temp ≤ 8° (advertencia suave)
- ✅ `zapatilla_deporte` + `mood == "elegante"`: bloqueada fuera de deporte

**`utils/garment_utils.py`**
- ✅ `is_shoe_ballet_flat(garment)` nueva función — detecta ballarina por subcategoría y keywords en nombre

**`app.py` — Galería de prendas**
- ✅ Filtro "☔ Solo impermeables" (`filter_waterproof`) en galería
- ✅ Filtro "⚠️ Con alertas" (`filter_issues`) en galería — muestra solo prendas con inconsistencias no ignoradas
- ✅ Ignored badges migrados de `st.session_state[f"issue_ignored_{g.id}"]` (efímero) a `st.session_state.ignored_badges` (set cargado desde Supabase)
- ✅ 7 widgets del formulario de edición corregidos (style, pattern, category, subcategory, warmth, dress_level, sexiness): removidos parámetros `index=`/`value=` conflictivos con session_state; inicialización con `if key not in st.session_state`

**`storage_cloud.py`**
- ✅ `load_ignored_badges_cloud(user_id)` y `add_ignored_badge_cloud(user_id, garment_id)` agregadas — persisten badges ignorados en tabla Supabase `ignored_badges`

---

### Sesión 29 — 01-May-2026 — Equiparación from_selected + fixes de diversidad

**Refactorización**
- ✅ `outfit_generation.py` dividido en `engine/generation/outfit_generation.py`, `engine/generation/outfit_generation_selected.py` y `engine/generation/week_plan.py`
- ✅ `recommender.py` y `app.py` actualizados para apuntar a los nuevos paths
- ✅ Versión bumpeada a `1.0.1`

**Fixes aplicados a `generate_outfits_from_selected_garment`**
- ✅ Fix A: Pool de accesorios ampliado a `max(accessory_limit+3, 5)` con `random.shuffle`
- ✅ Fix B: Matrimonio+sexy — inyección de enteritos al pool one_piece + corte dinámico (5 vs 4)
- ✅ Fix C: Reordenamiento de `final_outfits` en matrimonio para forzar vestidos primero
- ✅ Fix D: Sistema de selección completo (3 fases + contadores `max_same_*` + fallbacks) reemplaza el loop simple de 6 líneas

**Fixes de diversidad y estabilidad (ambos archivos generation)**
- ✅ Fix 1: Eliminada regla `same_one_piece → always True` en `is_too_similar` — redundante con `max_same_one_piece`
- ✅ Fix 2: `same_top + same_shoes → True` relajado a `same_top + same_shoes + same_bottom → True`
- ✅ Fix 3: `same_bottom_type + same_shoes_type → True` relajado a requerir además `same_top`
- ✅ Fix 4: `max_same_midlayer` ahora basado en total de midlayers post-filtro de clima, no solo blazers
- ✅ Fix 5: `max_same_outerwear` sin lluvia cambiado de 1 a 2 cuando hay 2+ outerwears
- ✅ Fix 6: Pool de midlayer a 16-23°C ampliado de `[:1]` a `[:3]` para ocasiones no-matrimonio
- ✅ Fix 7: Fallbacks relajan `max_same_midlayer`, `max_same_shoes` y `max_same_outerwear` progresivamente en segunda y tercera pasada
- ✅ Fix 8: `bottom_usage` + `max_same_bottom` agregado a las 3 pasadas del loop de selección — guard solo en primera pasada, conteo en todas

**Outfit sorpresa mejorado**
- ✅ Selección ponderada por sexiness, uso reciente y color no neutro (`random.choices` con weights)
- ✅ Fallback de hasta 3 intentos con prendas distintas si `from_selected` devuelve vacío
- ✅ Fallback final a `generate_outfits` normal si ninguna prenda forzada produce resultados

**Bugs resueltos**
- ✅ Bug 2: Enterito + polar — bloqueo duro en `occasion_rules.py` cuando midlayer sport/polar está con one_piece formal/sexy
- ✅ Bug 3: Lluvia+calor → impermeable elegante en casual — resuelto por regla prendas elegantes en moods relajados
- ✅ Bug 4: Casual + abrigo elegante en mood relajado — resuelto por la misma regla
- ✅ Bug 5: Recursión infinita matrimonio elegante — ya estaba resuelto (fallbacks usan `mood="sexy"`)

**Nueva regla `occasion_rules.py` — prendas elegantes/formales en moods relajados**
- ✅ Prenda con `style in ["elegante","formal"]`, sin secondary casual/urbano, y `dress_level in ["arreglado","elegante"]` queda bloqueada en `mood in ["relajado","comodo"]` cuando `occasion in ["casual","deporte"]`

**Formularios agregar/editar prenda sincronizados**
- ✅ `PATTERN_OPTIONS` usado en ambos tabs (incluye `"lunares"`)
- ✅ Colores secundarios con `st.multiselect` en ambos tabs
- ✅ Orden dress_level antes que sexiness en ambos tabs
- ✅ Labels `"Nivel térmico"` e `"Impermeable"` consistentes

**Deporte+entrenar — fix parcial**
- ✅ `occasion_rules.py`: excepciones if/elif/elif — tops `polera`/`polera_deporte` con `warmth == "caluroso"` pueden usarse para entrenar aunque no tengan style sport
- ✅ `occasion_rules.py`: bottom `short_casual` con `warmth == "caluroso"`, `dress_level in ["relajado","flexible"]` y sin denim en el nombre puede usarse para entrenar
- ✅ `utils/attribute_inference.py`: `"fitness"` agregado a keywords de style sport en `infer_style_from_name` y a keywords de `polera_deporte` en `infer_subcategory_from_name`
- ⚠️ Sigue dando resultados limitados en algunos escenarios de calor extremo — diagnóstico pendiente

---

### Sesión 30 — 02-May-2026 — Bugs motor + diversidad + deporte

**Bugs resueltos esta sesión**
- ✅ Bug 8 parcial: Deporte+entrenar+calor — diagnóstico completo ejecutado sobre clóset real (Supabase). Causa raíz: `max_same_shoes = 2` limitaba la única `zapatilla_deporte` disponible a aparecer solo en 2 outfits. Fix: principio "pool de 1" para shoes. Adicionalmente se confirmaron las excepciones de sesión 29 (short_casual caluroso + polera calurosa sin style sport).

**Principio "pool de 1" implementado (ambos archivos generation)**

Cuando el pool de candidatos de una categoría tiene exactamente 1 prenda, su `max_same_*` sube a `top_n` — el motor usa esa prenda en todos los outfits en lugar de cortarse. Aplica a: `shoes`, `top`, `bottom`, `outerwear`, `one_piece`. Midlayer no necesita ajuste (ya tenía su propia lógica con `_n_midlayers`).

Casos más impactantes:
- `shoes` en cualquier ocasión con 1 calzado disponible (incluye matrimonio/cita/nocturna donde antes el cap era 1 o 2)
- `outerwear` en lluvia con 1 impermeable disponible (antes cap = 3, ahora = top_n)

Implementación en dos capas:
1. La lógica de `max_same_shoes` para matrimonio/cita/nocturna se integró en un único bloque `if/elif/elif/else` (antes era un `if` separado que sobreescribía al final)
2. Bloque genérico de override "pool de 1" insertado después de todos los `max_same_*` individuales y antes del loop de selección — evalúa `_n_tops`, `_n_bottoms`, `_n_outerwear`, `_n_shoes`, `_n_one_pieces`

**⚠️ Inconsistencia observada (pendiente)**
En algunas tandas el motor muestra 2 outfits + mensaje "pocas combinaciones", en la siguiente recarga muestra 3. Causa probable: `random.shuffle` en pools de accesorios y outerwear genera variación en qué combos se registran primero en `unique{}`, afectando cuántos sobreviven los filtros de diversidad. No crítico pero debe investigarse.

---

### Sesión 31 — 02-May-2026 (continuación) — Bug #10 gala/matrimonio prenda forzada

**`engine/occasion_rules.py`**
- ✅ Nueva función `validate_selected_for_occasion(garment, occasion, mood, temp, rain, activity)` — fuente de verdad única para validación de prenda forzada. Retorna `(allowed, reason, severity)` donde severity es `"block"`, `"warn"` u `"ok"`
- ✅ Elimina las 5 contradicciones entre `app.py`, `garment_allowed_for_occasion` y `_generate_gala`

**`app.py`**
- ✅ Bloque de validación de `selected_garment` reemplazado por llamada a `validate_selected_for_occasion` — elimina lógica duplicada inline para gala y matrimonio+elegante
- ✅ Doble warning eliminado para casos como botín en gala
- ✅ Nombre de prenda aparece primero en formulario de edición (antes aparecía después de colores secundarios)

**`engine/generation/outfit_generation.py`**
- ✅ Accesorios forzados aparecen en todos los outfits de `_generate_gala` y `_generate_matrimonio_elegante` — antes solo aparecían en outfit 1

**`engine/generation/outfit_generation_selected.py`**
- ✅ `ranked` por categoría: la categoría de la prenda forzada rankea con `"casual"` cuando `ignore_occasion_for_selected=True`, las categorías companion rankean con la ocasión real — tacos y sandalias entran al pool correcto para matrimonio+elegante
- ✅ Filtro de matrimonio omitido para categoría forzada cuando `ignore_occasion_for_selected=True`: excepción explícita al final del bloque matrimonio que resetea `top_candidates[sel_cat]` al pool completo sin filtros de ocasión
- ✅ `add_combo` usa `check_occasion = "casual"` para companions cuando `ignore_occasion_for_selected=True` — evita que `garment_allowed_for_occasion` rechace companions válidos

**`engine/recommender.py`**
- ✅ `garment_base_score` usa `check_occasion` en vez de `occasion` cuando `ignore_occasion_for_forced=True` — scoring consistente con el ranking, sin penalizaciones de matrimonio para companions en modo ignore; evita que el diversity loop (`score < 0`) descarte outfits válidos

**`is_too_similar` (ambos archivos generation)**
- ✅ Regla fuerte `same_bottom_type + same_shoes_type` requiere además `same_bottom` exacto — dos jeans distintos con mismo top ya no se bloquean entre sí

**Causa raíz del Bug #10 documentada (3 capas)**
1. `ranked["shoes"]` usaba `"casual"` para todos los companions → tacos/sandalias rankeaban bajo → no entraban al top 5 → filtro matrimonio+elegante quedaba sin candidatos
2. `add_combo` usaba `occasion="matrimonio"` para `garment_allowed_for_occasion` → bloqueaba companions válidos como botines aunque el usuario hubiera presionado "Mostrar de todos modos"
3. `outfit_score` usaba `occasion="matrimonio"` para `garment_base_score` → scores muy negativos (-697) → `score < 0` del diversity loop descartaba todos los outfits

### Sesión 32 — 03-May-2026 — Fixes motor + matrimonio relajado/formal

**Fixes aplicados (pendientes de commit):**

**`engine/occasion_rules.py`**
- ✅ Prendas con `style == "sport"` como estilo principal bloqueadas en `occasion == "casual"` salvo `mood == "urbano"`
- ✅ Excepción calzado `dress_level` relajado para matrimonio + `mood == "relajado"` (cualquier calzado pasa, no solo subcategorías específicas)
- ✅ `validate_selected_for_occasion` — fuente de verdad única para validación de prenda forzada

**`engine/generation/outfit_generation.py`**
- ✅ matrimonio + relajado — nuevo bloque con reglas propias: tops/bottoms con `dress_level flexible+`, vestido casual incluido, calzado sin `zapatilla_deporte`, blazer flexible permitido como midlayer
- ✅ matrimonio + formal — hereda automáticamente las reglas estrictas del `else` (vestidos elegantes, tacos, blazer elegante)
- ✅ Reordenamiento y forzado de vestidos excluyen `mood relajado`
- ✅ `_force_mid` y `matrimonio_midlayer_allowed` incluyen `mood relajado`

**`engine/generation/outfit_generation_selected.py`**
- ✅ Mismos 9 cambios aplicados para equiparar con `outfit_generation.py`
- ✅ Loops de tops/bottoms en `selected_category == "shoes"` actualizados para relajado
- ✅ `ranked` por categoría: categoría forzada con `"casual"`, companions con ocasión real cuando `ignore_occasion_for_selected=True`
- ✅ `garment_base_score` usa `check_occasion` cuando `ignore_occasion_for_forced=True`

**`engine/recommender.py`**
- ✅ `garment_base_score` con `check_occasion` para scoring consistente en modo ignore

**`engine/generation/outfit_generation.py` + `outfit_generation_selected.py`**
- ✅ `is_too_similar` regla fuerte requiere `same_bottom_exact` — jeans distintos con mismo top no se bloquean
- ✅ Accesorios forzados aparecen en todos los outfits de gala y matrimonio

**⚠️ Pendiente de pruebas antes de commit:**

| # | Prueba | Esperado |
|---|--------|----------|
| T1 | Matrimonio + relajado temp 18° | Outfits más casuales — vestido casual, tops flexibles, calzado variado |
| T2 | Matrimonio + relajado temp 5° | Blazer flexible (no sweater/cardigan), abrigo elegante |
| T3 | Matrimonio + formal temp 18° | Vestidos elegantes priorizados, tacos, blazer elegante |
| T4 | Matrimonio + elegante temp 18° | Sin cambios vs antes |
| T5 | Matrimonio + sexy temp 18° | Sin cambios vs antes |
| T6 | Prenda forzada matrimonio + relajado | Funciona correctamente con motor permisivo |
| T7 | Prenda forzada matrimonio + formal "Mostrar de todos modos" | Outfits con companions formales |

---

## Tabla de bugs y mejoras pendientes — v1.0.1

### 🔴 Crítico
| # | Ítem | Archivo(s) | Estado |
|---|------|-----------|--------|
| 1 | Moderación de fotos en subidas | `storage_cloud.py`, `app.py` | ⏳ Pendiente estratégico |

### 🟠 Alta prioridad / Motor
| # | Ítem | Archivo(s) | Estado |
|---|------|-----------|--------|
| 7 | Midlayer repetido a temp baja | `outfit_generation.py` | ✅ Resuelto |
| 9 | Matrimonio relajado/formal — reglas invertidas | `outfit_generation.py`, `outfit_generation_selected.py` | ✅ Resuelto |
| 10 | Prenda forzada atípica en gala/matrimonio | múltiples | ✅ Resuelto |

### 🟡 Media prioridad / Motor
| # | Ítem | Archivo(s) | Estado |
|---|------|-----------|--------|
| 11 | Knitwear con vestidos elegantes | `compatibility.py` | ✅ Resuelto |
| 12 | Calzado plano trabajo+calor | `category_rules.py` | ✅ Resuelto |
| 13 | `taco_bajo` tolerado en mood cómodo (penalty 0) | `scoring_components.py` | ✅ Resuelto |
| 14 | `taco_alto` penalizado mood relajado (+80), `taco_bajo` penalizado leve (+30) | `scoring_components.py` | ✅ Resuelto |
| 15 | Mayor diversidad de tops en mood urbano | `outfit_generation.py` | ⬜ Pendiente |
| 16 | Compatibilidad de colores — 4+ colores sin eje cromático | `compatibility.py` | ⬜ Pendiente |
| 17 | Frío extremo sin capa — penalty +60 cuando temp ≤ 8 y no hay midlayer/outerwear | `scoring_components.py` | ✅ Resuelto |
| 18 | Inconsistencia 2 vs 3 outfits entre tandas — `is_too_similar` prenda forzada one_piece | `outfit_generation.py`, `outfit_generation_selected.py` | ✅ Resuelto |
| 32 | Prenda forzada one_piece — dedup key alineada con `core_ids` (excluye outerwear) | `outfit_generation_selected.py` | ✅ Resuelto |
| 33 | Vestido forzado en gala/salida nocturna mood relajado — no genera outfits | `outfit_generation.py`, `outfit_generation_selected.py` | ⬜ Pendiente |
| 34 | Prenda forzada limita a 1 outfit en algunos escenarios — condición residual a investigar | `outfit_generation_selected.py` | ⬜ Pendiente |
| 35 | Chaleco cuello V — lógica de compatibilidad y scoring no implementada | `compatibility.py`, `scoring_components.py` | ⬜ Pendiente |

### 🟢 Baja prioridad / UI y clóset
| # | Ítem | Archivo(s) | Estado |
|---|------|-----------|--------|
| 19 | Ocasiones frecuentes del perfil ordenadas primero | `app.py` | ⬜ Pendiente |
| 20 | Tip de pantys — máximo una vez por tanda | `app.py` | ⬜ Pendiente |
| 21 | Formulario editar prenda — scroll automático | `app.py` | ⬜ Pendiente |
| 22 | Destacar botones "Mi perfil" y "Qué es Lookia" | `app.py` | ⬜ Pendiente |
| 23 | Verificar top leopardo (id 63) — tag urbano | Supabase | ⬜ Pendiente |
| 24 | Agregar sandalias, ballerinas, chalas | Supabase | ⬜ Pendiente |

### ⚙️ Técnico / Deuda
| # | Ítem | Archivo(s) | Estado |
|---|------|-----------|--------|
| 25 | Integración IA Anthropic — moderación + inferencia desde fotos | `storage_cloud.py`, `attribute_inference.py` | ⬜ Pendiente |
| 26 | Refactor `outfit_generation_selected.py` — duplicación | `outfit_generation_selected.py` | ⬜ Pendiente |
| 27 | Import `outfit_score` dentro de loop en `_generate_matrimonio_elegante` | `outfit_generation.py` | ⬜ Pendiente |
| 28 | Extraer `is_too_similar` a función standalone | ambos generation | ✅ Resuelto |
| 29 | Dividir `app.py` en módulos por tab | `app.py` | ⬜ Pendiente |
| 30 | Nueva subcategoría `chaleco_vestir` | `constants.py` | ⬜ Pendiente |
| 31 | Migración React — UI definitiva | Proyecto nuevo | ⬜ Largo plazo |

---

## Sesión 33 — 10-May-2026 — Pruebas T1-T7, fixes scoring, bugs #11 y #12, code review

**Pruebas matrimonio completadas (sesión 32 cerrada)**

| Prueba | Estado |
|---|---|
| T1 matrimonio+relajado 18° | ✅ Aprobado con nota rotación |
| T2 matrimonio+relajado 5° | ✅ Aprobado con nota rotación |
| T3 matrimonio+formal 18° | ✅ Aprobado |
| T4 matrimonio+elegante 18° | ✅ Aprobado — regresión limpia |
| T5 matrimonio+sexy 18° | ✅ Aprobado — regresión limpia |
| T6 Prenda forzada matrimonio+relajado | ✅ Aprobado |
| T7 Prenda forzada matrimonio+formal bypass | ✅ Aprobado |

**Fixes de scoring aplicados**

`engine/scoring_components.py`
- ✅ `dress_score`: nueva entrada `"matrimonio_relajado"` con valores flexibles (flexible: 16, arreglado: 14, elegante: 8) — favorece prendas casuales en matrimonio+relajado sin afectar otros moods
- ✅ `practicality_penalty`: vestido_elegante/coctel en matrimonio+relajado recibe +60 en vez de -160 — diferencia al mood relajado del elegante
- ✅ Shuffle de blazers en pool de midlayer para matrimonio+relajado — mejora rotación entre tandas
- ✅ Blazer penalty (+15 flexible, -10 arreglado/elegante) ahora con guard `occasion == "matrimonio"` — no aplica en trabajo ni otras ocasiones
- ✅ Double penalty vestido_elegante corregido: bloque genérico +80 de mood relajado excluye matrimonio con `occasion != "matrimonio"` — neto real ahora es +60 como se diseñó

`engine/recommender.py`
- ✅ `garment_base_score`: usa `_dress_occasion = "matrimonio_relajado"` cuando `occasion == "matrimonio" and mood == "relajado"`
- ✅ `explain_outfit_score`: misma sustitución `_dress_occ` para consistencia en explicaciones

`engine/generation/outfit_generation.py`
- ✅ Fix blazer forzado en `_generate_matrimonio_elegante`: variable `_blazer_forzado` garantiza que el blazer seleccionado aparezca en los 3 outfits sin ser sobreescrito por el ciclo `i % len(blazers)`

`engine/generation/outfit_generation_selected.py`
- ✅ Fix `midlayer_usage` para prenda forzada: la condición `max_same_midlayer` no aplica cuando `midlayer_id == selected_garment.id` — prenda forzada aparece en los 3 slots

**Bug #11 — Knitwear con vestidos elegantes**
`engine/compatibility.py`
- ✅ Bloque `{midlayer, one_piece}` refactorizado con diferenciación por subcategoría:
  - `chaleco` (sin mangas): 0 penalty con vestido elegante — es un look válido
  - `cardigan`: -6 con vestido elegante — penalización leve
  - `sweater`: -12 con vestido elegante — penalización moderada
  - Midlayers casual/urbano (no knitwear): -18 con vestido elegante — sin cambios
- ✅ Decisión: subcategoría `chaleco_vestir` (#30) y atributo `neckline` postergados para React — no hay chalecos de vestir en el clóset femenino típico de Lookia

**Bug #12 — Calzado plano trabajo+calor**
`engine/category_rules.py`
- ✅ `shoe_context_bonus`: nuevo bloque `occasion == "trabajo" and temp >= 24` — sandalia elegante +20, taco_bajo +12, ballarina flexible/arreglada +10, taco_alto -15
- ✅ Fix datos Supabase: "Sandalias elegantes" (id 152) actualizado a style `elegante`, dress_level `arreglado`

**Code review automático (plugin code-review)**
- ✅ Plugin instalado y configurado — requiere PR abierto para funcionar (no push directo)
- ✅ Review manual detectó 3 bugs reales, todos resueltos en commit f73523a
- ✅ Plugins instalados en CC: code-review, security-guidance, supabase, github

**Commits de sesión**
- `4e0f62c` — Sesiones 32-33: matrimonio relajado/formal, fixes scoring dress_level, penalización vestido elegante mood relajado, shuffle blazers
- `f73523a` — fix: code review — blazer penalty solo matrimonio, double-penalty vestido relajado, explain_outfit_score usa dress_occasion

**Próxima sesión**
- Bugs #13, #14 (taco_bajo/taco_alto por mood)
- Bug #17 (planificador + frío)
- Revisión final pre-React (rotación, refactor, limpieza)

---

### Sesión 34 — 10-May-2026 — Bugs motor + plan migración React

**Bugs resueltos**
- ✅ Bug #13 — `taco_bajo` tolerado en mood cómodo (penalty 0)
- ✅ Bug #14 — `taco_alto` penalizado mood relajado (penalty 80), `taco_bajo` penalizado leve (penalty 30)
  - Archivo: `engine/scoring_components.py`, función `practicality_penalty`
  - Commit: cc02f5c
- ✅ Bug #17 — Planificador + frío extremo sin capa: penalty +60 cuando temp <= 8 y no hay midlayer/outerwear
  - Archivo: `engine/scoring_components.py`, función `practicality_penalty`
  - Commit: cc02f5c
- ✅ Bug #18 — Inconsistencia 2 vs 3 outfits entre tandas: `is_too_similar` ahora ignora `one_piece` compartido cuando no hay top compartido (caso prenda forzada vestido)
  - Archivos: `engine/generation/outfit_generation.py`, `engine/generation/outfit_generation_selected.py`
  - Commit: da28682
- ✅ Bug #32 — Prenda forzada one_piece genera 1 solo outfit: alineada key de deduplicación con `core_ids` (excluye outerwear) igual que `outfit_generation.py`
  - Archivos: `engine/generation/outfit_generation_selected.py`
  - Commit: da28682


---

### Sesión 35 — 11-May-2026 — Bugs motor + calidad cromática + combinaciones absurdas

**Bug #13/#14 — Calzado por mood**
`engine/scoring_components.py`, función `practicality_penalty`
- ✅ Reemplazado bloque `is_shoe_heel → +50` genérico por penalizaciones granulares por subcategoría
- ✅ `mood == "comodo"`: `taco_alto` +50, `taco_bajo` +20
- ✅ `mood == "relajado"`: `taco_alto` +80, `taco_bajo` +40

**Bug #17 — Frío extremo fuerza capa**
`engine/generation/outfit_generation.py` + `outfit_generation_selected.py`
- ✅ `_force_mid`, `_force_mid_outer`, `_force_outer_only` generalizados: condición `temp <= 8 and occasion != "deporte"` aplica a todas las ocasiones, no solo matrimonio
- ✅ Aplica en ambos bloques del loop (top+bottom y one_piece)

**Bug #16 — Compatibilidad cromática**
`engine/compatibility.py`
- ✅ Nueva función `count_chromatic_colors(items)` — cuenta colores únicos no neutros excluyendo outerwear
- ✅ `NEUTRAL_COLORS = {"negro", "blanco", "gris", "beige", "café", "crema", "gris claro"}`

`engine/scoring_components.py`, función `coherence_penalty`
- ✅ Reemplazado conteo de colores totales por `count_chromatic_colors`
- ✅ 4+ cromáticos: penalty 999 (bloqueo duro)
- ✅ 3 cromáticos: +45 en ocasiones formales, +25 en casual

**Combinaciones inválidas bloqueadas**
`engine/generation/outfit_generation.py`
- ✅ Early return `[], []` para `deporte + formal`
- ✅ Early return `[], []` para `gala + relajado`

`app.py`
- ✅ Selector de mood filtra opciones según ocasión: `deporte` excluye `formal`; `gala` excluye `relajado`
- ✅ Warning de gala+relajado eliminado (ya no puede llegar)

**Buzo como bottom — reglas nuevas**
`engine/category_rules.py`, `bottom_context_penalty`
- ✅ `subcategory == "buzo"` fuera de `deporte` o `mood != "urbano"` → penalty +60

`engine/scoring_components.py`, `practicality_penalty`
- ✅ Buzo + calzado no-zapatilla → penalty +120 (bloqueo efectivo de buzo+ballerina, buzo+taco, etc.)

**Polar como midlayer — reglas nuevas**
`engine/scoring_components.py`, `practicality_penalty`
- ✅ Polar bloqueado (penalty 999) en `salida nocturna` + `mood in ["sexy", "elegante"]`
- ✅ Polar bloqueado (penalty 999) en `trabajo` + `mood in ["elegante", "formal"]`

**Tip de pantys en deporte eliminado**
`app.py`
- ✅ Condición `has_short and temp <= 20` incluye `and occasion != "deporte"`

**Script de pruebas**
- ✅ `test_outfit_coverage.py` creado y validado con clóset real (107 prendas, service role key)
- ✅ Baseline post-sesión: 48 fallos totales, 38 reales

---

## Sesión 36 — 13-May-2026 — Sincronización generation + reglas deporte + subcategoría polerón

**Sincronización `outfit_generation_selected.py`**
- ✅ Early returns `deporte+formal` y `gala+relajado` agregados al inicio de `generate_outfits_from_selected_garment`
- ✅ `_force_mid`, `_force_mid_outer`, `_force_outer_only` sincronizados con `outfit_generation.py`: condición `or (temp <= 8 and occasion != "deporte")` agregada

**Inferencia — fix `"formal"` en style**
- ✅ `attribute_inference.py`, `infer_style_from_name`: keyword `"formal"` eliminado de lista de `"elegante"` — nombres con "formal" ahora infieren `style == "formal"` correctamente

**Reglas deporte — midlayer**
- ✅ `occasion_rules.py`: en `occasion == "deporte"`, midlayers bloqueados salvo `style == "sport"` o `subcategory in ["hoodie", "poleron"]`

**Nueva subcategoría `poleron`**
- ✅ `constants.py`: `"poleron"` agregado a `SUBCATEGORY_OPTIONS["midlayer"]` y `SUBCATEGORY_LABELS_ES`
- ✅ `attribute_inference.py`: keywords `["poleron", "polerón", "sudadera"]`; `style_map["poleron"] = "casual"`; `warmth_map["poleron"] = "medio"`

---

## Sesión 36 — 13-May-2026 — Bug #7 midlayer repetido a temp baja

**Bug #7 — Midlayer repetido a temp baja**
`engine/generation/outfit_generation.py`
- ✅ `max_same_midlayer` para ocasiones no-matrimonio: cambiado de `2` (cuando `_n_midlayers == 2`) a `1` cuando hay 2+ midlayers — evita que el mismo midlayer aparezca dos veces en una tanda
- ✅ `mid_limit` subido de `2` a `4` — el pool de midlayers ya no se trunca antes de llegar a la selección de diversidad
- ✅ Pool de midlayers `ranked["midlayer"][:4]` subido a `[:6]` — permite que más blazers entren al pool para matrimonio+relajado antes del filtro por subcategoría
- ✅ Filtro matrimonio+relajado: `dress_level` incluye `"relajado"` además de `["flexible", "arreglado", "elegante"]`

**Próxima sesión**
- Deuda técnica #29 — dividir `app.py` en módulos por tab
- Bug #35 — implementar lógica chaleco cuello V (compatibilidad, scoring, subcategorías)
- Limpieza `occasion_rules`/`scoring_components`
- Migración React — FastAPI + React, deadline fin de mayo 2026

---

### Sesión 36 (continuación) — 13-May-2026 — Deuda #28

**Deuda #28 — Extraer is_too_similar a función standalone**
`engine/compatibility.py`, `engine/generation/outfit_generation.py`, `engine/generation/outfit_generation_selected.py`
- ✅ Función `is_too_similar` extraída a `engine/compatibility.py` como función standalone
- ✅ Definiciones locales eliminadas de ambos archivos de generación
- ✅ Imports actualizados en ambos archivos
- ✅ App corre sin errores tras el cambio
- Nota: CC detectó discrepancia en bloque `same_one_piece and same_shoes` — se usó la versión correcta de los archivos locales, no la simplificada
