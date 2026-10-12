# Guion Cronometrado de Defensa (10 Minutos) — StreamView Analytics

**Asignatura:** Visualización de Datos (ADY1104) — Duoc UC  
**Modalidad:** Exposición grupal con defensa individual (10 minutos presentación + 5 minutos preguntas)  
**Storytelling Central:** Metáfora de la película *"La Niebla"* (*The Mist*, Stephen King / Frank Darabont)  
**Audiencia Evaluadora:** Mesa Ejecutiva Integral (Directorio, Gerencia de Contenidos y Gerencia de Marketing)

---

## Estructura Temporal del Guion

| Bloque | Minutos | Qué se Proyecta | Contenido / Objetivo |
| :---: | :---: | :--- | :--- |
| **Bloque 1** | 00:00 - 01:30 | **PPT: Slides 1 y 2** | El Gancho Cinematográfico: Atrapados en la Niebla frente a Netflix y HBO Max. |
| **Bloque 2** | 01:30 - 02:30 | **PPT: Slides 3 y 4** | Rigor Metodológico (31.991 títulos, clave UID) y pase a la solución. |
| **Bloque 3** | 02:30 - 07:00 | **Dashboard en Vivo** | Demostración práctica en `http://127.0.0.1:8050`: Filtros (IE19), UX (IE21), Pestañas (IE20) y Exportación (IE23). |
| **Bloque 4** | 07:00 - 08:30 | **PPT: Slides 5 y 6** | Los Grandes Hallazgos: Series duplican popularidad y cruda realidad financiera del cine (58% recupera costo). |
| **Bloque 5** | 08:30 - 09:30 | **PPT: Slide 7** | Plan de Acción Estratégico H-E-I-R (Directorio, Contenidos, Marketing). |
| **Bloque 6** | 09:30 - 10:00 | **PPT: Slide 8** | Justificación Tecnológica (IE15) y Cierre: *"La niebla se ha disipado"*. |

---

## Bloque 1 (00:00 - 01:30): El Gancho Inicial — "Atrapados en La Niebla"
*(Proyectando Slide 1 y Slide 2 en pantalla completa)*

> *"Buenos días, profesor y miembros de la comisión directiva.  
> 
> ¿Alguno de ustedes ha visto la película **'La Niebla'** (*The Mist*), basada en la obra de Stephen King?  
> En esa película, un pueblo entero queda envuelto en una niebla espesa y sobrenatural. Un grupo de personas queda atrapado dentro de un supermercado: no pueden ver a tres metros de distancia hacia afuera, pero escuchan los rugidos aterradores de monstruos gigantescos acechándolos en la oscuridad. Adentro, cunde el pánico porque nadie sabe qué camino tomar sin ser devorado.  
> 
> Bueno... hasta hace muy poco, a **StreamView Analytics** le estaba pasando exactamente lo mismo.  
> 
> Nuestra plataforma creció desde 2018 hasta superar los **31.000 títulos**. Pero estábamos atrapados en nuestra propia niebla: reportes de Excel fragmentados, datos en silos y decisiones de compra tomadas a ciegas... mientras afuera, en el mercado real de Latinoamérica, gigantes como **Netflix, HBO Max y Prime Video** acechan invirtiendo miles de millones de dólares armados con analítica de punta.  
> 
> Nuestra pregunta de negocio no admitía más corazonadas: **¿Qué contenidos debería adquirir, renovar o promocionar StreamView para fidelizar a su audiencia y rentabilizar su capital?**  
> 
> Hoy no venimos a mostrarles tablas aburridas: venimos a encender los reflectores y disipar la niebla con **StreamView Analytics**."*

---

## Bloque 2 (01:30 - 02:30): Rigor Metodológico y Gobernanza de Datos
*(Proyectando Slide 3 y Slide 4)*

> *"Pero como consultores serios en analítica, antes de pulsar botones garantizamos la pureza y veracidad de los datos:  
> 
> 1. **Preservamos 31.991 títulos únicos** (16.000 películas y 15.991 series), con una tasa de pérdida de datos del cero por ciento.  
> 2. **Resolvimos una colisión crítica de 397 identificadores repetidos** entre películas y series creando la clave unívoca UID (`tipo[0] + show_id`), asegurando que jamás se sobreescribiera un registro.  
> 3. **Evitamos el error del producto cartesiano (M × N):** separamos la expansión de géneros y países en tablas independientes para no inflar artificialmente las estadísticas.  
> 4. **Adoptamos la Mediana sobre el Promedio:** porque las variables de popularidad y presupuesto tienen una asimetría extrema con éxitos virales aislados que distorsionarían la media.  
> 5. **Y declaramos la verdad con honestidad analítica:** estos datos miden oferta de catálogo, demanda comunitaria y valoración percibida; no miden telemetría de clics ni retención de usuarios.  
> 
> Y para que cada líder de la organización encuentre respuestas directas, estructuramos la plataforma en módulos orientados por rol: Directorio, Contenidos, Marketing y Finanzas.  
> 
> A continuación, pasamos a nuestro navegador para demostrar la solución interactiva en vivo."*

---

## Bloque 3 (02:30 - 07:00): Demostración en Vivo del Dashboard
*(Minimizar PPT o cambiar al navegador en `http://127.0.0.1:8050`)*

### 1. Interacción y Filtros Reactivos (Criterio IE19)
> *"Observen la interfaz: implementamos un diseño Dark Theme cinematográfico premium inspirado en plataformas como Netflix o HBO, con contraste visual cuidado para no cansar la vista.  
> En el panel superior tenemos filtros reactivos sincronizados: Formato, Rango de Años en un slider continuo, Género múltiple y País múltiple. Al mover el slider o filtrar por un género, observen cómo las métricas y los gráficos recalculan al instante en memoria sin latencia. Y con el botón 'Limpiar filtros' volvemos a la visión global en milisegundos."*

### 2. Pestaña 1: Resumen Ejecutivo (Hablando al Directorio)
> *"Don Directorio, mire su pantalla: tenemos 31.991 títulos. Pero fíjese en el primer gran descubrimiento: **las series duplican en popularidad mediana a las películas** (14.2 frente a 6.8). Aunque el cine represente más del 65% de los títulos del catálogo, la tracción y el enganche de los suscriptores está en las series. Las películas construyen volumen de catálogo, pero las series construyen el hábito de pago mensual."*

### 3. Pestaña 2: Catálogo (Hablando a Contenidos y Adquisición)
> *"Equipo de Contenidos: miren las barras horizontales. Drama y Comedia saturan la oferta con más de 10.000 títulos disponibles. Pero si miramos países e idiomas, después de Estados Unidos y Reino Unido, **Japón y Corea del Sur concentran una demanda unitaria descomunal** impulsada por el fenómeno global del Anime y los K-Dramas. Seguir comprando cine anglosajón genérico es saturar un mercado que ya tiene demasiada oferta."*

### 4. Pestaña 3: Campañas (Hablando a la Gerencia de Marketing)
> *"Marketing, atención a esta **Matriz de Oportunidad**: cada punto es un género graficado entre la oferta disponible y la demanda comunitaria. Los cuadrantes superiores nos marcan categorías como **Documental y Animación: alta demanda del público pero muy poca oferta en catálogo**. En lugar de gastar todo el presupuesto publicitario compitiendo en Drama, ataquemos estos nichos desatendidos con campañas de alta conversión. Y para captación masiva, usamos el ranking del Top 10 con al menos 100 votos auditados."*

### 5. Pestaña 4: Finanzas de Películas (Reglas de Negocio 3, 6 y 9)
> *"En finanzas, si filtramos por 'Series', el sistema protege la integridad con un bloqueo formal: las series no reportan taquilla. Pero al volver a Películas comerciales (presupuestos mayores a 100.000 dólares), descubrimos una realidad contundente: **solo el 58% de las películas recupera su costo de producción**. En el scatter logarítmico, vemos qué títulos están sobre la línea de equilibrio de 1.0x. Géneros como Animación y Aventura multiplican el capital con medianas superiores a 2.5x, mientras los dramas costosos operan a pérdida."*

### 6. Exportación de Calidad (Criterio IE23)
> *"Y para llevar estos hallazgos a los comités ejecutivos, basta un clic para descargar los datos filtrados en CSV, o usar la cámara nativa de Plotly para exportar cualquier gráfico en imagen PNG de alta definición."*

---

## Bloque 4 (07:00 - 08:30): Hallazgos Clave de Catálogo y Finanzas
*(Volver a la PPT en Slide 5 y Slide 6)*

> *"Al regresar de la demostración interactiva, consolidamos los dos grandes pilares de hallazgos:  
> 
> **Pilar 1: Composición de Catálogo y Engagement:**  
> - Las series superan por más del doble en atracción al cine (14.2 frente a 6.8 de popularidad mediana), manteniendo calificaciones idénticas de calidad (6.0 vs 5.8).  
> - La oferta está hiperconcentrada en producciones anglosajonas, mientras los contenidos asiáticos presentan comunidades con un engagement unitario mucho más apasionado.  
> 
> **Pilar 2: Realidad Financiera Cinematográfica:**  
> - El 42% de las películas no alcanza el punto de equilibrio en taquilla.  
> - Producir dramas prestigiosos con presupuestos superiores a 30 millones de dólares presenta una tasa de fracaso de taquilla superior al 55%.  
> - En contraste, la Animación y Aventura familiar lideran el retorno mediano sobre costo superando 2.5x de ROI."*

---

## Bloque 5 (08:30 - 09:30): Recomendaciones Estratégicas H-E-I-R
*(Proyectando Slide 7)*

> *"Siguiendo la metodología H-E-I-R exigida por la pauta (Hallazgo → Evidencia → Implicancia → Recomendación), dejamos acciones concretas por audiencia:  
> 
> 1. **Para el Directorio (Inversión Patrimonial):**  
>    *Recomendación:* **Destinar el 60% del presupuesto de licencias anual a temporadas de series**, ya que son las que retienen suscriptores y reducen el churn mensual.  
> 
> 2. **Para Contenidos (Gestión de Catálogo):**  
>    *Recomendación:* **Priorizar coproducciones en Animación y Aventura familiar** con retornos probados superiores a 2.5x, y **establecer un tope presupuestario de 10 millones de dólares para películas dramáticas** para mitigar el riesgo de pérdida.  
> 
> 3. **Para Marketing (Estrategia 50/30/20):**  
>    *Recomendación:* Dividir el presupuesto publicitario en:  
>    - **50% en Campañas Masivas:** apoyadas en el Top 10 para capturar nuevos suscriptores.  
>    - **30% en Campañas de Retención:** aprovechando el volumen de catálogo de Drama y Comedia.  
>    - **20% en Campañas de Nicho de Alta Conversión:** en Documentales y comunidades de Anime y K-Drama."*

---

## Bloque 6 (09:30 - 10:00): Cierre y Justificación Tecnológica (IE15)
*(Proyectando Slide 8)*

> *"Para cerrar y defendiendo el criterio IE15 de la rúbrica:  
> Seleccionamos **Python, Dash y Plotly** porque nos otorgó tres ventajas imbatibles frente a herramientas cerradas como Power BI o Tableau:  
> 1. **Control de Experiencia de Usuario:** un Dark Theme cinematográfico premium que respeta la identidad de streaming sin plantillas corporativas rígidas.  
> 2. **Procesamiento Analítico en Memoria:** cálculo instantáneo con Pandas de matrices de oportunidad, percentiles y exclusiones por clave compuesta.  
> 3. **Soberanía y Costo Cero:** una solución de código abierto sin licencias mensuales por visualizador, lista para producción con Gunicorn.  
> 
> Señores del Directorio: StreamView Analytics ya no está atrapada dentro del supermercado de 'La Niebla'.  
> Hoy los reflectores están encendidos, el camino está despejado y la compañía está lista para liderar con evidencia.  
> 
> Muchas gracias. Quedamos a su entera disposición para sus preguntas."*
