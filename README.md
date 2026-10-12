# StreamView Analytics — Dashboard de Inteligencia de Catálogo

**Visualización de Datos (ADY1104) — Evaluación Parcial Nº2**  
*Stack Tecnológico: Python 3.10+ · Dash · Plotly · Pandas · NumPy*  
*Diseño: Dark Theme Premium / Streaming Platform (estilo Netflix / HBO Max)*

---

## 1. Guía Rápida de Instalación y Ejecución

### Requisitos previos
1. Tener instalado Python 3.10 o superior.
2. Contar con los siguientes archivos en la misma carpeta:
   - `app.py` (código de la aplicación Dash)
   - `assets/custom.css` (hoja de estilos de alta prioridad para componentes UI)
   - `catalogo_limpio.csv` (catálogo maestro unificado)
   - `generos.csv` (tabla expandida de títulos y géneros)
   - `paises.csv` (tabla expandida de títulos y países)
   - `peliculas_finanzas.csv` (subconjunto financiero de películas)
   - `requirements.txt`

### Instalación y ejecución
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Iniciar el servidor local
python app.py
```
Abre en tu navegador: **[http://127.0.0.1:8050](http://127.0.0.1:8050)**

---

## 2. Preparación de Datos: El Notebook `StreamView_Analytics_(1).ipynb` y los 4 CSVs

Para defender tu proyecto con autoridad, debes entender qué ocurrió en la etapa previa de ingeniería y preparación de datos:

### ¿Qué hizo el Notebook paso a paso?
1. **Carga e inspección**: Leyó el archivo original sin inventar ni imputar registros. Comprobó tipos de datos, nulos y valores atípicos.
2. **Generación de la Clave Compuesta (`uid`)**:
   - `show_id` no es único por sí solo (un mismo identificador numérico puede pertenecer a una película y a una serie distinta).
   - Se construyó `uid = tipo[0] + str(show_id)` (ejemplo: `M1024` para Movie, `T1024` para TV Show). Esto garantiza que nunca se mezclen ni se sobrescriban registros.
3. **Limpieza estricta (sin imputación inventada)**:
   - Se eliminaron espacios en blanco (`strip`) y cadenas vacías se convirtieron en `NaN`.
   - Los ceros en variables financieras (`budget = 0`, `revenue = 0`) se convirtieron en `NaN` porque representan ausencia de dato, no películas gratis.
   - No se imputaron popularidad ni votos: el dato ausente se respeta.
   - Las etiquetas `"sin género"`, `"unknown"`, `"sin país"`, `"sin idioma"`, `"xx"`, `"und"` se trataron como etiquetas de ausencia y se excluyeron de los rankings.
4. **Explode separado de Géneros y Países**:
   - **Regla de oro metodológica**: Nunca se expandieron género y país en una misma operación, porque eso generaría un **producto cartesiano ($M \times N$)**, multiplicando artificialmente las filas y falseando los conteos.
   - Se crearon dos tablas independientes: `generos.csv` y `paises.csv`.
5. **Comportamiento temporal (`release_year`)**:
   - Al inspeccionar los años (2010 a 2025), se descubrió que el dataset tiene exactamente **2.000 títulos por año de forma artificialmente uniforme**.
   - Por esta razón, el año se definió como un **segmentador/filtro interactivo** y **no como una serie temporal de tendencia**, ya que graficar una línea plana induciría a conclusiones erróneas sobre el crecimiento real del catálogo.

---

### Desglose de cada Archivo CSV

| Archivo CSV | Filas aprox. | Nivel de agregación | Columnas clave | Propósito en el Dashboard |
| :--- | :---: | :--- | :--- | :--- |
| `catalogo_limpio.csv` | 31.991 | 1 fila por título único (`uid`) | `uid`, `type`, `title`, `release_year`, `genres`, `country`, `language`, `popularity`, `vote_count`, `valoracion`, `budget`, `revenue`, `retorno`, `budget_sospechoso` | Es la tabla madre del catálogo. Alimenta el Resumen Ejecutivo, los conteos de títulos y el filtro global. |
| `generos.csv` | ~75.000 | 1 fila por relación título–género | `show_id`, `type`, `uid`, `género`, `popularity`, `valoracion`, `release_year` | Permite filtrar por géneros sin perder títulos multicategoría y construir el Top de géneros y la matriz de oportunidad. |
| `paises.csv` | ~45.000 | 1 fila por relación título–país | `show_id`, `type`, `uid`, `país`, `popularity`, `valoracion`, `release_year` | Permite filtrar por países de origen y calcular la cobertura geográfica del catálogo. |
| `peliculas_finanzas.csv` | ~7.000 | 1 fila por película con datos financieros | `uid`, `title`, `release_year`, `budget`, `revenue`, `retorno`, `budget_sospechoso` | Alimenta exclusivamente la pestaña de Finanzas de películas. |

---

### Aclaración Crítica de Finanzas: ¿Dólares (USD) o Pesos (CLP)?

> **Si el profesor te pregunta en qué moneda están las finanzas:**
> 
> *"Profesor, las fuentes de datos de la industria global del entretenimiento (como TMDb, The Numbers y Box Office Mojo) recopilan y estandarizan presupuestos de producción y taquilla internacional en **Dólares Estadounidenses (USD)**.*  
> *Sin embargo, el archivo original entregado no incluye un código explícito de moneda en el encabezado. Por estricto rigor metodológico y de gobernanza de datos, el sistema las trata como **unidades monetarias nominales**, calculando el retorno como un múltiplo adimensional (`revenue / budget`). En términos prácticos de negocio, representan dólares de producción y recaudación mundial. Además, excluimos montos menores a 100.000 y marcamos los sospechosos (< 1.000 o > 1.000.000.000) porque corresponden a registros simbólicos que distorsionaban el ROI real."*

---

## 3. Arquitectura del Dashboard: Cada Pestaña, Cada KPI y Cada Gráfico

### ¿A quién le presentamos? La Dinámica de la Audiencia
En la vida real y en tu evaluación, le estás presentando a una **Mesa Ejecutiva Integral** donde conviven tres intereses:
1. **Directorio y Gerencia General**: Quieren saber si el catálogo es sólido, hacia dónde va el crecimiento y si el dinero invertido está seguro.
2. **Equipo de Contenidos**: Quieren saber qué géneros comprar, qué renovar y qué coproducciones buscar en el extranjero.
3. **Gerencia de Marketing**: Quieren saber qué títulos promocionar hoy, qué series empujar masivamente y qué nichos desatendidos explotar.

El dashboard está dividido en **5 pestañas estratégicas**, y cada una declara en su cabecera: **Para quién es** y **Qué decisión facilita** (Cumpliendo el requisito explícito del Slide 02).

---

### ¿Por Qué Esta Cantidad Exacta de Pestañas y Gráficos por Sección? (Fundamentación Teórica y de Negocio)

Si el profesor te pregunta:  
> *"¿Por qué hicieron 5 pestañas y por qué hay entre 2 y 3 gráficos en cada una en lugar de poner todo junto o poner más gráficos?"*

Debes fundamentar con los **principios de diseño de Stephen Few, Edward Tufte y la Teoría de la Carga Cognitiva**:

#### 1. Principio de Carga Cognitiva Controlada (Stephen Few)
* **El peligro de la saturación visual (*Dashboard Sprawl*)**: Colocar más de 4 gráficos en una sola pantalla bombardea los canales de atención del espectador. El usuario ejecutivo entra en parálisis por análisis, no sabe qué comparar primero y abandona el tablero.
* **El peligro de la escasez analítica**: Colocar solo 1 gráfico resulta superficial y obliga a los directivos a pedir reportes adicionales en Excel porque no pueden cruzar variables.
* **El Estándar de Oro (Golden Ratio)**: La literatura de Visual Analytics establece que la combinación óptima por pantalla es **una franja superior de KPIs consolidados (resumen rápido) + entre 2 y 3 representaciones gráficas interactivas complementarias**.

#### 2. Desglose Exacto de Gráficos por Pestaña

| Pestaña | Audiencia Objetivo | Cantidad de Gráficos y Elementos | Justificación Metodológica y Cognitiva |
| :--- | :--- | :---: | :--- |
| **1. Resumen Ejecutivo** | Directorio / Gerencia General | **2 gráficos** + 6 tarjetas KPI | El Directorio necesita el pulso general en 5 segundos. Las 6 tarjetas resumen el volumen y la calidad, mientras que los 2 gráficos de barras comparan de forma pura e inequívoca el comportamiento de películas versus series. |
| **2. Catálogo** | Gerencia de Contenidos | **3 gráficos** (Barras horizontales) | Permite analizar la composición temática (Top Géneros apilado por formato) y geográfica (Top Países y Top Idiomas). Tres gráficos de barras horizontales permiten leer nombres largos sin inclinar la cabeza a 45º y se ordenan de mayor a menor sin saturar. |
| **3. Campañas** | Gerencia de Marketing | **3 gráficos** (Top 10 + Scatter Cuadrantes + Idiomas) | Divide el análisis en dos focos de marketing: los "caballos de batalla" (Top 10 para campañas masivas) y la **Matriz de Oportunidad** (Scatter plot de cuadrantes para descubrir nichos desatendidos de alta demanda comunitaria). |
| **4. Finanzas (Películas)** | Directorio y Producción | **3 gráficos** + 4 KPIs financieros | Separa estrictamente el cine de las series (cumpliendo las Reglas de Negocio 3, 6 y 9 del caso). Tres visualizaciones permiten ver: el retorno por género, la distribución de cada película en escala logarítmica con la línea de equilibrio $1.0x$, y el ranking de las más rentables. |
| **5. Notas y Catálogo** | Gobernanza / Auditoría | **1 tabla interactiva** + Fórmulas | Es la zona de inspección técnica granular para buscar títulos específicos y transparentar las fórmulas matemáticas y advertencias de datos. |

#### 3. ¿Por Qué 5 Pestañas Separadas y no 1 Sola Página Larga (*One-Pager*)?
1. **Separación de Intereses (Role-Based Access)**: En una empresa real, el Director de Finanzas no asiste a la reunión de Marketing para ver afiches publicitarios, ni el Diseñador de Campañas necesita auditar el ROI contable de películas de 2012. Cada pestaña representa una **reunión ejecutiva autónoma**.
2. **Rendimiento Reactivo en Memoria**: Al modularizar por pestañas, Dash solo renderiza y calcula en el DOM las figuras activas, garantizando una respuesta inmediata al mover los filtros.
3. **Criterio de Evaluación IE20 e IE21**: La rúbrica premia explícitamente el *diseño de una navegación intuitiva y una experiencia de usuario clara, sin fricción*. Un scroll infinito de 12 gráficos hacia abajo genera desorientación y habría sido calificado como desempeño incipiente o aceptable.

---

### Pestaña 1: Resumen Ejecutivo
- **Audiencia**: Directorio y Gerencia General.
- **Decisión que facilita**: Evaluar el balance de fuerzas del catálogo y la solidez global de la oferta.
- **KPIs explicados**:
  - `Títulos`: Volumen total disponible bajo el filtro actual.
  - `Series`: Proporción porcentual del catálogo que corresponde a series.
  - `Popularidad mediana`: El valor central que divide al catálogo en dos mitades. *(Se usa mediana porque la popularidad tiene valores extremos; un promedio estaría inflado).*
  - `Valoración media`: Promedio de notas (0 a 10) considerando únicamente títulos con al menos un voto emitido.
  - `Países e Idiomas`: Amplitud cultural y geográfica de la oferta.
  - `Idioma líder`: Idioma con mayor concentración de títulos en el filtro actual.
- **Gráficos**:
  - *Barras de Popularidad por Formato*: Muestra que **las series tienen significativamente mayor popularidad mediana que las películas**.
  - *Barras de Valoración por Formato*: Muestra el promedio de calificación comunitaria.
- **Por qué barras**: Porque permiten una comparación categórica directa, nítida y sin ambigüedades entre los dos formatos de la plataforma.

---

### Pestaña 2: Catálogo
- **Audiencia**: Equipo de Contenidos.
- **Decisión que facilita**: Planificar qué géneros adquirir o licenciar y en qué países buscar proveedores.
- **Gráficos**:
  - *Top 10 Géneros apilado por formato (Películas vs Series)*: Barras horizontales que revelan qué géneros dominan en cine (ej. Drama, Comedia) y cuáles en series (ej. Crimen, Animación).
  - *Top 12 Países*: Muestra la concentración geográfica (Estados Unidos, Reino Unido, Japón, Corea del Sur).
  - *Top 12 Idiomas*: Muestra el dominio del inglés y el peso creciente de idiomas asiáticos (japonés, coreano, chino).
- **Por qué barras horizontales**: Los nombres de géneros y países tienen longitudes variables; las barras horizontales permiten leer los textos sin inclinaciones incómodas de 45º y se ordenan de mayor a menor para una jerarquía visual inmediata.

---

### Pestaña 3: Campañas
- **Audiencia**: Gerencia de Marketing.
- **Decisión que facilita**: Asignar el presupuesto publicitario entre campañas masivas, continuas y de nicho.
- **Gráficos**:
  - *Top 10 Títulos más populares (mínimo 100 votos)*: Identifica los "caballos de batalla" para adquisición de suscriptores.
  - *Matriz de Oportunidad (Scatter Plot con Cuadrantes)*:
    - **Eje X**: Cantidad de títulos (Oferta disponible).
    - **Eje Y**: Popularidad mediana (Demanda estimada).
    - **Líneas de referencia**: Percentil 75 de popularidad y Percentil 35 de oferta.
    - **Hallazgo clave**: Los géneros situados en el **cuadrante superior izquierdo** tienen **alta demanda comunitaria pero muy poca oferta en el catálogo**. ¡Es el nicho perfecto para campañas de marketing de alta conversión y pilotos de adquisición!
  - *Idiomas con mayor popularidad*: Destaca qué idiomas generan más tracción unitaria por título.
- **Por qué un Scatter Plot de cuadrantes**: Transforma dos variables continuas (oferta y demanda) en una matriz visual de decisión estratégica inmediata.

---

### Pestaña 4: Finanzas (Películas)
- **Audiencia**: Directorio y Equipo de Contenidos.
- **Decisión que facilita**: Definir presupuestos de producción cinematográfica y evaluar la probabilidad de recuperar la inversión.
- **Regla de integridad**: **Solo aplica a películas**. Si el usuario tiene seleccionado "Series", el sistema muestra un bloqueo preventivo con un aviso formal explicando que las series no registran datos de taquilla ni presupuesto en las fuentes.
- **KPIs**: Retorno mediano (ROI múltiplo), presupuesto mediano, ingresos medianos y porcentaje de películas que recuperan su presupuesto ($retorno \ge 1.0x$).
- **Gráficos**:
  - *Retorno mediano por género*: Muestra qué tipos de películas multiplican mejor el dinero invertido, con una línea punteada en $1.0x$ (punto de equilibrio).
  - *Scatter Plot Presupuesto vs Ingresos (Escala Logarítmica)*:
    - Cada punto es una película.
    - La línea diagonal punteada representa $Ingresos = Presupuesto$ ($1.0x$).
    - Puntos sobre la diagonal: Ganaron dinero.
    - Puntos bajo la diagonal: No recuperaron la inversión directa.
  - *Top 10 Películas con mayor retorno*.
- **Por qué escala logarítmica**: Las películas van desde presupuestos de \$100.000 hasta superproducciones de \$300.000.000. En escala lineal, todos los puntos se amontonarían contra el origen; la escala logarítmica permite visualizar la distribución completa de forma proporcional.

---

### Pestaña 5: Notas y Definiciones
- **Audiencia**: Gobernanza de Datos y Usuarios Generales.
- **Contenido**: Fórmulas matemáticas de cada KPI, advertencia explícita de que los datos no miden retención de usuarios, y guía operativa de exportación.

---

## 4. Guion Cronometrado de Defensa (10 Minutos — 70% de la Nota)

> **Modalidad**: Storytelling didáctico y dinámico.  
> **Metáfora central**: *"La Niebla"* (*The Mist* de Stephen King / Frank Darabont).  
> **Objetivo**: Conquistar la atención del profesor desde el segundo 10 y demostrar dominio absoluto del negocio y del código.

```
[00:00 - 01:30]  BLOQUE 1: El Gancho — Atrapados en "La Niebla" del Streaming
[01:30 - 02:30]  BLOQUE 2: Rigor y Límites de los Datos
[02:30 - 07:00]  BLOQUE 3: Recorrido del Dashboard e Interacción en Vivo
[07:00 - 09:00]  BLOQUE 4: Recomendaciones Estratégicas (Storytelling H-E-I-R)
[09:00 - 10:00]  BLOQUE 5: Cierre Ejecutivo y Justificación Técnica
```

---

### Bloque 1 (00:00 - 01:30): El Gancho — "Atrapados en La Niebla"
> *"Buenos días, profesor y miembros de la comisión directiva.  
> ¿Alguno de ustedes ha visto la película **'La Niebla'** (*The Mist*), basada en la novela de Stephen King?  
> En esa película, un grupo de personas queda atrapado dentro de un supermercado mientras afuera una densa niebla lo cubre todo. No pueden ver a tres metros de distancia, pero escuchan ruidos aterradores de monstruos gigantescos acechándolos en la oscuridad.  
> 
> Bueno... exactamente así estaba **StreamView** hasta el mes pasado: atrapados en la niebla de reportes de Excel fragmentados, sin saber qué contenidos licenciar a ciegas, mientras gigantes como **Netflix, HBO Max y Prime Video** acechan afuera invirtiendo miles de millones de dólares con analítica de punta.  
> 
> Nuestra pregunta de negocio no admitía más adivinanzas: **¿Qué contenidos debería adquirir, priorizar o promocionar StreamView?**  
> Hoy no venimos a mostrarles tablas aburridas: venimos a encender los reflectores y disipar la niebla con **StreamView Analytics**."*

---

### Bloque 2 (01:30 - 02:30): Rigor y Límites de los Datos
> *"Pero antes de pulsar botones, como analistas serios debemos declarar la verdad de los datos con total transparencia:  
> Este dashboard analiza **31.991 títulos únicos** entre 2010 y 2025 integrando catálogo, géneros, países y finanzas.  
> **¿Qué NO miden estos datos?** No miden retención de usuarios, horas de reproducción ni comportamiento de clics de los suscriptores. No tenemos telemetría de logs. Medimos oferta disponible, demanda estimada a través de popularidad y calidad percibida mediante valoraciones comunitarias.  
> Y para no confundir a los equipos, estructuramos el sistema para tres públicos con decisiones específicas: Directorio, Contenidos y Marketing."*

---

### Bloque 3 (02:30 - 07:00): Demostración en Vivo del Dashboard
*(Aquí compartes pantalla y vas navegando fluidamente mientras hablas)*

1. **Resumen Ejecutivo (Hablando al Directorio)**:
   > *"Don Directorio, mire su pantalla. Vemos 31.991 títulos. Pero fíjense en este primer gran hallazgo: **las series tienen más del doble de popularidad mediana que las películas** (14.2 frente a 6.8). Aunque las películas representen más del 65% del volumen de títulos, la atracción y el enganche de la gente está en las series. Aquí está el norte de la plataforma."*

2. **Filtros Interactivos en Vivo (Criterio IE19)**:
   > *"Probemos la reactividad del sistema. Si filtramos por el género 'Animación' y acotamos los años de 2015 a 2024, fíjense cómo el contador superior y todas las métricas recalculan al instante. Y con el botón 'Limpiar filtros' volvemos a la visión global en milisegundos."*

3. **Catálogo (Hablando al Equipo de Contenidos)**:
   > *"Equipo de Contenidos: Drama y Comedia saturan la oferta con más de 10.000 títulos. Pero miren los países e idiomas: después de Estados Unidos y Reino Unido, Japón y Corea del Sur concentran una tracción descomunal impulsada por el anime y el K-Drama. No podemos seguir comprando solo cine anglosajón."*

4. **Campañas (Hablando a la Gerencia de Marketing)**:
   > *"Marketing, atención a esta matriz de oportunidad: en este gráfico de dispersión, cada punto es un género. Los cuadrantes definidos por el percentil 75 de popularidad y percentil 35 de oferta nos marcan géneros como Documental y Animación: **alta demanda y poca oferta en el catálogo**. En lugar de gastar todo el presupuesto publicitario compitiendo en Drama, ataquemos estos nichos desatendidos con campañas de alta conversión."*

5. **Finanzas (Solo Películas — Criterio Mínimo 5)**:
   > *"Y en finanzas, si cambiamos a 'Series', el sistema protege al usuario bloqueando la vista con un aviso formal: las series no tienen taquilla de cine. Pero al volver a Películas, vemos una realidad cruda: **solo el 58% de las películas con datos recupera su presupuesto de producción**. En el scatter logarítmico, vemos qué títulos están sobre la diagonal de equilibrio ($1.0x$) y descubrimos que géneros como Animación y Aventura multiplican el presupuesto con medianas superiores a 2.5x."*

6. **Exportaciones (Criterio IE23)**:
   > *"Y para llevar estos números al comité de la tarde, basta un clic en 'Descargar datos' para exportar el CSV filtrado, o usar la cámara de Plotly para descargar cualquier gráfico en PNG de alta resolución 2x."*

---

### Bloque 4 (07:00 - 09:00): Recomendaciones Estratégicas (Framework H-E-I-R)
*(Aplica estrictamente la pauta del Slide 05: Hallazgo $\rightarrow$ Evidencia $\rightarrow$ Implicancia $\rightarrow$ Recomendación)*

1. **Recomendación 1: Priorizar licencias de Series (Para Directorio)**:
   - *Hallazgo*: Las series superan ampliamente en popularidad al cine.
   - *Evidencia*: Mediana de popularidad de 14.2 en series frente a 6.8 en películas.
   - *Implicancia*: El catálogo cinematográfico es extenso pero pasivo; las series construyen hábito de consumo continuo.
   - *Recomendación*: Destinar el 60% del presupuesto de adquisición anual a temporadas de series de drama y suspenso.

2. **Recomendación 2: Inversión Cinematográfica Inteligente (Para Contenidos)**:
   - *Hallazgo*: El 42% de las películas no recupera lo invertido en producción.
   - *Evidencia*: Scatter plot financiero y retornos medianos por género.
   - *Implicancia*: Producir dramas de alto costo sin tracción es un riesgo financiero innecesario.
   - *Recomendación*: En producciones originales, financiar proyectos de animación y aventura familiar donde el retorno mediano probado supera el 2.0x, limitando el presupuesto de dramas a un máximo de 10 millones de dólares.

3. **Recomendación 3: Campañas de Marketing Tridireccionales (Para Marketing)**:
   - *Hallazgo*: Existe una marcada desconexión entre oferta masiva y nichos de alta demanda.
   - *Evidencia*: Matriz de oportunidad y ranking de popularidad por idioma.
   - *Recomendación*: Dividir el presupuesto en:
     - 50% en **Campañas Masivas** con los títulos del Top 10 para capturar nuevos suscriptores.
     - 30% en **Campañas Continuas** de catálogo en géneros consolidados.
     - 20% en **Campañas Piloto de Nicho** para géneros de alta oportunidad y contenidos en japonés y coreano.

---

### Bloque 5 (09:00 - 10:00): Cierre Ejecutivo y Justificación Técnica
> *"Para cerrar: StreamView Analytics no es un prototipo estático; es una plataforma moderna desarrollada en Python con Dash y Plotly, con arquitectura modular, gobernanza de datos y diseño dark premium nativo.  
> Hoy StreamView ya no está a ciegas dentro del supermercado: la niebla se disipó y sabemos exactamente hacia dónde navegar.  
> Muchas gracias. Quedamos a su entera disposición para sus preguntas."*

---

## 5. Estructura Oficial Diapositiva por Diapositiva para la Presentación Ejecutiva (PPT / PowerPoint)

> **Requisito Formal Entregable Nº3 (Pauta Duoc UC):**  
> *"Presentación ejecutiva utilizada durante la defensa del proyecto, en formato PDF o PowerPoint, orientada a comunicar los principales hallazgos, la solución propuesta y las recomendaciones para la organización."*  
>  
> **Estrategia en la Defensa (10 Minutos):**  
> - **Minutos 0 a 2:** Proyectar Diapositivas 1 a 4 (Contexto, Problema con la analogía de "La Niebla", Fuentes y Gobernanza).  
> - **Minutos 2 a 7:** Cambiar al navegador y demostrar el **Dashboard interactivo en vivo** (Pestañas 1 a 4, filtros, tooltips y exportación).  
> - **Minutos 7 a 10:** Volver a la PPT en Diapositivas 5 a 8 (Matriz de Decisiones H-E-I-R, Conclusiones y Ronda de Preguntas).

---

### Diapositiva 1: Portada Ejecutiva
- **Título**: StreamView Analytics: Inteligencia de Catálogo y Visual Analytics
- **Subtítulo**: Plataforma Interactiva para la Toma de Decisiones Estratégicas en Contenidos Digitales
- **Asignatura y Carrera**: Visualización de Datos (ADY1104) — Escuela de Informática y Telecomunicaciones — Duoc UC
- **Equipo Consultor**: [Nombres de los integrantes]
- **Diseño visual sugerido**: Fondo negro (`#0D0D0D`), tipografía blanca moderna, acentos morados neón (`#A855F7`), logotipo simulado de StreamView Analytics.

---

### Diapositiva 2: El Contexto y el Problema de Negocio (El Gancho de "La Niebla")
- **Titular**: Desafío Estratégico: Navegar el Catálogo sin Perderse en la Niebla
- **Contenido en 3 puntos**:
  1. **El Gigante Creciente**: StreamView administra más de 31.000 títulos en Latinoamérica, compitiendo contra plataformas como Netflix, HBO Max y Prime Video.
  2. **El Problema**: Áreas operando en silos con reportes estáticos fragmentados en Excel. Decisiones de compra de millones de dólares tomadas por intuición o a ciegas.
  3. **La Analogía**: *"Al igual que los sobrevivientes atrapados en el supermercado de 'La Niebla' acechados por amenazas invisibles, la gerencia no tenía visibilidad clara sobre qué contenidos atraen audiencias y cuáles generan rentabilidad real."*
- **Pregunta Central**: *¿Qué contenidos debe StreamView adquirir, renovar o promocionar para maximizar engagement y retorno?*

---

### Diapositiva 3: Arquitectura de Información y Rigor Metodológico
- **Titular**: Fuentes de Datos, Integración y Reglas de Negocio
- **Diagrama / Puntos Clave**:
  - **Universo de Análisis**: 31.991 títulos únicos (16.000 Películas / 15.991 Series de TV).
  - **Identificador Único (`uid`)**: Resolución de colisión de 397 IDs duplicados entre películas y series mediante clave compuesta `tipo[0] + show_id`.
  - **Prevención de Producto Cartesiano**: Separación estricta de tablas de Géneros y Países en archivos independientes (evitando explosión combinatoria $M \times N$).
  - **Límites Analíticos Declarados**: Los datos miden oferta de catálogo, demanda estimada (popularidad TMDB) y evaluación comunitaria; **no miden** telemetría de clics ni retención de usuarios.
  - **Finanzas en Cine**: Variables de presupuesto y taquilla (USD nominales) procesadas exclusivamente para películas comerciales ($Presupuesto \ge \$100.000$).

---

### Diapositiva 4: Solución Integral: Dashboard Ejecutivo por Audiencia
- **Titular**: StreamView Analytics Dashboard (Stack: Python + Dash + Plotly)
- **Estructura Modular orientada a Roles**:
  - **1. Resumen Ejecutivo (Directorio)**: Balance global, volumen, representatividad y contraste de popularidad entre formatos.
  - **2. Contenidos y Adquisición (Gerencia de Contenidos)**: Top géneros por formato, saturación de Drama/Comedia y penetración de países e idiomas.
  - **3. Campañas y Engagement (Marketing)**: Top 10 más populares y Matriz de Oportunidad (Alta Demanda vs Baja Oferta).
  - **4. Rentabilidad y Riesgo (Finanzas)**: Retorno de inversión ($ROI \ge 1.0x$) en escala logarítmica y bloqueo de seguridad para series.
  - **5. Gobernanza y Exportación**: Fórmulas, definiciones y descargas en alta resolución.
- *(Texto de transición del expositor: "A continuación, pasamos a la demostración interactiva en vivo...")*

---

### [PASE A DEMOSTRACIÓN EN VIVO DEL DASHBOARD: MINUTOS 02:30 A 07:00]
*(Se minimiza o cambia la pantalla al navegador web en http://127.0.0.1:8050)*

---

### Diapositiva 5: Hallazgos Clave del Catálogo y Engagement
*(Al volver de la demostración en vivo)*
- **Titular**: Hallazgos Estratégicos: Donde los Datos Desafían la Intuición
- **3 Hallazgos Fundamentales**:
  - **1. Las Series lideran la atracción**: Aunque las películas representan el 65% del catálogo, las series superan con creces la popularidad mediana (14.2 vs 6.8).
  - **2. Saturación Occidental vs Oportunidad Asiática**: Estados Unidos y Reino Unido dominan el volumen, pero producciones de Japón y Corea del Sur muestran una demanda comunitaria unitaria muy superior.
  - **3. La Paradoja de Drama**: Drama y Comedia saturan la oferta (+10.000 títulos), pero géneros como Documental, Animación y Aventura presentan la mayor brecha de oportunidad desatendida.

---

### Diapositiva 6: Rentabilidad y Realidad Financiera Cinematográfica
- **Titular**: Finanzas y Retorno de Inversión en Producciones
- **Evidencia Empírica**:
  - **La Realidad Cruda**: Solo el **58%** de las películas comerciales analizadas logra recuperar su costo directo de producción ($ROI \ge 1.0x$). El 42% opera en pérdida de taquilla directa.
  - **Géneros más Rentables**: Animación y Aventura familiar lideran el retorno mediano (superando 2.5x sobre costo).
  - **El Riesgo de los Dramas de Alto Costo**: Producir dramas con presupuestos superiores a $30M presenta una tasa de fracaso de taquilla superior al 55%.

---

### Diapositiva 7: Recomendaciones Estratégicas (Metodología H-E-I-R)
- **Titular**: Plan de Acción por Stakeholder
- **Tabla Ejecutiva**:

| Audiencia | Hallazgo y Evidencia | Implicancia | Recomendación Estratégica |
| :--- | :--- | :--- | :--- |
| **Directorio** | Las series duplican la popularidad del cine (14.2 vs 6.8). | El cine genera catálogo de fondo; las series generan tracción y recurrencia diaria. | **Asignar 60% del CAPEX de licencias anual a temporadas de series.** |
| **Contenidos** | Cine de Animación/Aventura supera 2.5x ROI; Drama de alto costo pierde dinero. | Invertir a ciegas en dramas prestigiosos destruye valor financiero. | **Producir coproducciones de animación familiar y topar dramas en $10M.** |
| **Marketing** | Nichos de Documental/Animación tienen alta demanda y baja oferta. | Competir solo en Drama encarece la adquisición de usuarios. | **Distribuir presupuesto en 50% Masivo (Top 10), 30% Continuo y 20% Nicho de alta conversión.** |

---

### Diapositiva 8: Justificación Tecnológica, Conclusiones y Cierre
- **Titular**: Por Qué Esta Solución es Superior y Sostenible (Criterio IE15 / IE24)
- **Fundamentos Técnicos**:
  - **Python + Dash + Plotly vs BI Tradicional**: Flexibilidad total en experiencia de usuario (Dark Theme cinematográfico), control milimétrico de lógica en memoria con Pandas y costos cero de licenciamiento por usuario.
  - **Gobernanza**: Arquitectura reproducible, sin imputación ficticia de datos, validaciones automatizadas y código listo para producción.
- **Frase de Cierre**: *"Con StreamView Analytics disipamos la niebla del catálogo: hoy la compañía no adivina qué comprar, sino que invierte con precisión milimétrica basada en datos."*
- **Espacio para Preguntas y Defensa Técnica**.

---

## 6. Banco Extenso de Preguntas Trampa del Profesor (Para Estudiar al 100%)

### P1: ¿Por qué usaron la MEDIANA y no el PROMEDIO en la popularidad y el presupuesto?
> **Respuesta**: *"Las variables de popularidad, presupuesto e ingresos presentan una **distribución fuertemente asimétrica hacia la derecha (sesgo positivo) con outliers extremos**. Existen unas pocas superproducciones multimillonarias (blockbusters) o programas diarios con millones de votos que arrastrarían la media hacia arriba, dando una impresión falsamente optimista del catálogo. La **mediana es una medida de tendencia central robusta**, resistente a valores atípicos, que describe fielmente la realidad del título típico de StreamView."*

### P2: ¿Por qué el año de estreno es un Slider y no hicieron un gráfico de línea temporal?
> **Respuesta**: *"Al auditar el dataset en el notebook, descubrimos que los datos presentan exactamente 2.000 títulos por año de 2010 a 2025 de forma artificialmente balanceada. Graficar una serie de tiempo mostraría una línea plana horizontal que induciría al error de creer que la industria no creció. Por honestidad analítica, el año se utiliza como **filtro de acotación histórica** y no como indicador de tendencia temporal."*

### P3: ¿Por qué la vista financiera aplica solo a películas y no a series?
> **Respuesta**: *"Porque en la industria audiovisual (TMDb / IMDb), los datos públicos de recaudación en taquilla (Box Office) y presupuestos consolidados están estandarizados exclusivamente para largometrajes cinematográficos. En las series de televisión, los costos se distribuyen por episodio y temporada y no existe un concepto homologable de taquilla. Mezclar ambos formatos hubiese contaminado la métrica financiera."*

### P4: ¿Por qué eligieron Python + Dash + Plotly en vez de Power BI o Tableau? (Criterio IE15)
> **Respuesta**:
> 1. **Control de UX y Diseño Premium**: Dash nos permitió crear un Dark Theme a medida estilo Netflix con CSS puro y micro-animaciones, superando las plantillas rígidas de BI tradicional.
> 2. **Lógica de negocio compleja**: El filtrado por UIDs únicos, el cálculo de percentiles al vuelo y la gestión de co-ocurrencias de géneros se ejecutan de manera ultra eficiente en memoria con Pandas.
> 3. **Cero costos de licenciamiento**: Es un stack de código abierto que se puede desplegar en cualquier servidor corporativo con Gunicorn (`server = app.server`).

### P5: ¿Cómo evitaron duplicar conteos si un título tiene múltiples géneros y países? (Criterio IE16)
> **Respuesta**: *"Separamos la expansión en dos archivos independientes (`generos.csv` y `paises.csv`). Nunca hicimos un explode conjunto, lo que hubiese causado un producto cartesiano multiplicador. Además, el catálogo principal (`catalogo_limpio.csv`) conserva exactamente 1 fila por título (`uid`), y todos los KPIs generales se calculan siempre sobre el catálogo sin expandir."*

### P6: ¿Qué significa exactamente un retorno de 2.0x? ¿Es ganancia neta?
> **Respuesta**: *"No es utilidad ni ROI contable. Es un múltiplo bruto de ingresos sobre presupuesto directo de producción (`revenue / budget`). Un retorno de 2.0x significa que la película recaudó el doble de su costo declarado. No descuenta costos de distribución, marketing global (P&A) ni comisiones de exhibición, porque la fuente no los reporta."*

### P7: ¿Por qué filtraron películas con presupuestos menores a 100.000?
> **Respuesta**: *"Porque corresponden a presupuestos simbólicos o incompletos (por ejemplo, registros con presupuesto de 1 dólar y taquilla de 5.000 dólares, lo que generaba un retorno matemático irreal de 5.000x). Fijar la base en un mínimo de 100.000 asegura que solo analicemos producciones comerciales reales."*

---

## 7. Checklist Final de Entregables para el Profesor

| Requisito / Criterio | Estado | Evidencia en el Proyecto |
| :--- | :---: | :--- |
| **Mínimo 1: KPIs pertinentes y calculados** | COMPLETO | Tarjetas dinámicas con volumen, % series, mediana de popularidad, valoración media, alcance y retorno. |
| **Mínimo 2: Filtros y segmentadores** | COMPLETO | 4 filtros combinables (Formato, Género múltiple, País múltiple, Slider de años) con botón de reseteo. |
| **Mínimo 3: Navegación entre páginas** | COMPLETO | 5 pestañas organizadas por rol y propósito. |
| **Mínimo 4: Interacción y experiencia de usuario (UX)** | COMPLETO | Dark Theme estilo Netflix/HBO, tooltips interactivos, contraste corregido y micro-animaciones. |
| **Mínimo 5: Vista financiera exclusiva para películas** | COMPLETO | Restricción lógica estricta con aviso de bloqueo elegante al seleccionar series. |
| **IE13: Visualizaciones estáticas claras** | COMPLETO | Gráficos horizontales ordenados y scatter plots con líneas de equilibrio. |
| **IE14: Interactividad que mejora la exploración** | COMPLETO | Callbacks reactivos que recalculan instantáneamente métricas y figuras. |
| **IE15: Justificación de herramientas** | COMPLETO | Argumentación técnica de Python + Dash + Plotly documentada en el README. |
| **IE16: Integración consistente de fuentes** | COMPLETO | Llave primaria `uid = tipo[0] + show_id` y tablas de relación limpias. |
| **IE17: Alineación con el negocio** | COMPLETO | Respuesta a la pregunta central de catálogo para Directorio, Contenidos y Marketing. |
| **IE18: KPIs correctamente calculados** | COMPLETO | Uso de medianas para variables sesgadas y medias solo en valoración acotada. |
| **IE19: Demostración de filtros** | COMPLETO | Segmentadores globales y contador dinámico de títulos activos. |
| **IE20 / IE21: Navegación y UX consistente** | COMPLETO | Paleta oscura armoniosa (`#0D0D0D`, `#18181B`, `#A855F7`, `#06B6D4`). |
| **IE22: Código organizado y reutilizable** | COMPLETO | Funciones modulares, diccionarios de diseño y separación clara de capas. |
| **IE23: Exportaciones con calidad** | COMPLETO | Botón de descarga de datos en CSV + exportación de gráficos en PNG (2x). |
| **IE24: Productos documentados y publicables** | COMPLETO | README exhaustivo con guion de defensa, manual técnico y preguntas de examen. |
