# Consignas Proyecto 2: RAG

> Transcripción estructurada de `Consignas Proyecto 2 RAG.docx`. Esta es la consigna académica original; el alcance específico de QA Memory RAG se define en [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md).

## Contexto y objetivos

Sos un/a ingeniero/a de IA en una empresa de HR SaaS con mucha documentación. El equipo de soporte al cliente recibe más de 200 preguntas repetitivas por día sobre políticas, funcionalidades y procedimientos que ya están documentados en FAQs internas y guías. El equipo necesita un chatbot inteligente de soporte para FAQs que responda al instante recuperando información relevante de la documentación de la empresa, sin requerir búsquedas manuales ni intervención de agentes.

### Objetivos

- Implementar un sistema de FAQs basado en RAG que procese un documento de texto plano, lo divida en chunks de forma inteligente —mínimo 20—, genere embeddings y los almacene para una recuperación eficiente. Esto crea una base de conocimiento consultable a partir de documentación no estructurada.
- Construir un pipeline de consulta que acepte preguntas de usuarios, realice búsqueda vectorial usando métodos k-NN, ANN, rango o híbridos, recupere los chunks relevantes y genere respuestas precisas con un LLM.
- Devolver JSON estructurado con `user_question`, `system_answer` y `chunks_related`, para asegurar transparencia y auditabilidad.
- Opcional: implementar un agente evaluador que puntúe la calidad de la respuesta de 0 a 10 según la relevancia de los chunks, la precisión y la completitud.

### Por qué es importante

Los sistemas RAG permiten que los LLM respondan con precisión usando conocimiento privado, actualizado y específico del dominio, sin fine-tuning costoso. Dominar embeddings, búsqueda vectorial y generación aumentada por recuperación prepara para casos como automatización de soporte, bases de conocimiento internas, análisis de documentos legales y asistentes para documentación técnica.

## Consigna

Creá un chatbot de soporte para FAQs usando RAG que responda preguntas basándose en un documento del sistema. Debe:

1. Procesar un documento de texto plano.
2. Dividirlo en al menos 20 chunks.
3. Generar embeddings.
4. Para cada pregunta del usuario, devolver una salida JSON que contenga `user_question`, `system_answer` y `chunks_related` usados para generar la respuesta.
5. Utilizar búsqueda vectorial —por ejemplo, k-NN, ANN, rango o híbrida— para encontrar eficientemente los chunks relevantes.

### Bonus opcional

Implementar un agente evaluador que reciba `user_question`, `system_answer` y `chunks_related`, y devuelva un puntaje de 0 a 10 con una justificación.

## Entrega

Enviar un enlace público al repositorio Git. El repositorio debe ser autocontenido y ejecutable sin depender de elementos externos no documentados.

La solución debe tener código limpio y mantenible, funciones modulares, documentación completa —README con instalación y uso—, gestión de dependencias y manejo de errores.

## Estructura esperada y entregables

| Entregable | Archivo o formato | Contenido mínimo |
| --- | --- | --- |
| Documento fuente | `data/faq_document.txt` | Documento de texto plano con al menos 1000 palabras sobre temas de FAQ —políticas, procedimientos, funcionalidades, entre otros—. Debe ser suficientemente sustancial para generar más de 20 chunks significativos. |
| Pipeline de datos | `src/build_index.py`, `notebook.ipynb` o secciones con código | Código ejecutable que carga el documento, lo divide en más de 20 chunks, genera embeddings para todos y guarda embeddings y chunks en un almacenamiento —archivo, base de datos o memoria—. |
| Pipeline de consultas | `src/query.py`, `notebook.ipynb` o secciones con código | Código que recibe una pregunta, la convierte en embedding, realiza búsqueda vectorial, recupera chunks relevantes, genera una respuesta con un LLM y devuelve JSON con `user_question`, `system_answer` y `chunks_related`. |
| Salidas de ejemplo | `outputs/sample_queries.json` | Al menos tres pares consulta-respuesta que muestren el formato JSON completo y demuestren el flujo de punta a punta. |
| README | `README.md` | Versión de Python, instalación con `pip install -r requirements.txt`, configuración de API key, cómo ejecutar indexación y consultas, ejemplo de uso, estructura del proyecto y decisiones de chunking y búsqueda. |
| Configuración | `.env.example` | Plantilla de variables requeridas, por ejemplo `OPENAI_API_KEY=your-key-here` y `EMBEDDING_MODEL=text-embedding-3-small`. |

Tener en cuenta lo aprendido en el módulo 2: estrategias de chunking, generación de embeddings —OpenAI o Sentence-Transformers—, búsqueda por similitud vectorial y arquitectura RAG de recuperación más generación. Documentar las decisiones técnicas: por qué se eligió la estrategia de chunking y el enfoque de búsqueda.

## Rúbrica de evaluación

### Análisis y segmentación del documento

**Requerimiento:** analizar y segmentar eficientemente el documento, preservando contexto semántico y usando fragmentos de tamaño óptimo.

**Indicadores:**

- Se procesa el 100 % del contenido.
- Se generan 20 o más chunks distintos.
- Cada chunk tiene entre 50 y 500 tokens.
- La estrategia queda documentada explícitamente: tamaño fijo con solapamiento, por oraciones, semántica o por párrafos.
- El código incluye `chunk_size` y `overlap` si utiliza tamaño fijo, o la definición de límites si usa otra estrategia.

### Generación de embeddings

**Requerimiento:** generar automáticamente embeddings de alta calidad para permitir recuperación precisa y veloz.

**Indicadores:**

- Se genera un embedding por cada chunk: ambas cantidades coinciden.
- Se utiliza la API de OpenAI o un modelo de Sentence-Transformers.
- Los embeddings se guardan en una variable, archivo —JSON, pickle o CSV— o base/vector store.

### Salida JSON estructurada

**Requerimiento:** entregar los datos procesados y recuperados con una arquitectura de objetos clara.

**Indicadores:**

- El JSON valida en todas las consultas de prueba.
- Tiene exactamente tres claves: `user_question`, `system_answer` y `chunks_related`.

### Búsqueda vectorial

**Requerimiento:** implementar una base de datos vectorial que permita consultas de similitud de alta velocidad.

**Indicadores:**

- Se implementa al menos una técnica: k-Nearest Neighbors (k-NN), Approximate Nearest Neighbors (ANN), Range Query o búsqueda híbrida.
- El código calcula similitud explícitamente —coseno, producto punto o distancia euclidiana— mediante fórmula o función de librería.
- La documentación indica qué método se usa y por qué.

### Calidad y relevancia de la recuperación

**Requerimiento:** ajustar `top-k` y aplicar filtros para obtener resultados precisos, contextuales y con poco ruido.

**Indicadores:**

- Con tres o más preguntas de ejemplo, al menos 80 % de los chunks recuperados contienen palabras clave de la consulta o la responden directamente.
- Para preguntas de sí/no, se recuperan chunks con hechos relevantes.
- Para preguntas de “cómo hacer”, se recuperan chunks con pasos o procedimientos.
- Se devuelven de dos a cinco chunks por consulta.

### Data Pipeline de indexación

**Requerimiento:** automatizar la ingesta, limpieza y almacenamiento de la base de conocimiento en un motor vectorial.

**Indicadores:**

- Etapa 1: carga del documento, contemplando manejo de codificación.
- Etapa 2: segmentación del texto y generación de 20 o más chunks.
- Etapa 3: generación de embeddings para todos los chunks.
- Etapa 4: almacenamiento de embeddings y texto de chunks en base de datos, archivo o estructura en memoria.
- El pipeline es modular: funciones separadas por etapa o bloques claramente diferenciados.
- Se puede comprobar el flujo completo: documento de entrada → vectores almacenados con el texto de cada chunk.

### Query Pipeline de recuperación y generación

**Requerimiento:** conectar consulta, recuperación, contexto y LLM para producir respuestas fundamentadas.

**Indicadores:**

- Etapa 1: embedding de la consulta con la misma dimensionalidad que los embeddings de los chunks.
- Etapa 2: búsqueda vectorial de los chunks más similares.
- Etapa 3: ensamblado de contexto incorporado al prompt.
- Etapa 4: generación con un LLM —API de OpenAI o modelo local— usando ese contexto.

### Comprensión de la arquitectura RAG

**Requerimiento:** implementar los componentes de forma lógica para resolver límites de tokens y brindar conocimiento actualizable sin reentrenamiento.

**Indicadores:**

- El código deja visible el flujo de dos pasos: primero recuperación y después generación.
- El README o los comentarios explican por qué usa RAG y que primero se recuperan chunks relevantes antes de generar.
- La documentación menciona al menos un beneficio de RAG: conocimiento actualizable, transparencia o atribución de fuentes.

### Organización modular

**Requerimiento:** separar claramente procesamiento, embeddings y orquestación RAG.

**Indicadores:**

- Hay cuatro o más funciones con nombres descriptivos, por ejemplo `load_and_chunk_document()`, `generate_embeddings()`, `search_similar_chunks()` y `generate_answer()`.
- Cada función tiene un propósito claro y no supera 30 líneas.
- Los imports aparecen arriba, luego las funciones y, al final, `main`.

### Documentación técnica

**Requerimiento:** documentar pipelines, fuentes de datos e instrucciones de ejecución.

**Indicadores:**

- El README tiene una descripción de al menos 50 palabras sobre el propósito del chatbot de FAQs.
- Incluye tres o más pasos de instalación y configuración: dependencias, API key y ejecución.
- Muestra una pregunta de entrada y el formato JSON esperado.
- Justifica en una o dos oraciones la estrategia de chunking y la búsqueda vectorial.

### Dependencias y entorno

**Requerimiento:** garantizar reproducibilidad mediante dependencias y variables de entorno documentadas.

**Indicadores:**

- Incluye `requirements.txt` o equivalente con las dependencias.
- Especifica versiones, por ejemplo `openai==1.12.0` y `numpy==1.24.0`.
- La API key se carga mediante `os.getenv()` o un archivo de configuración.
- El README explica cómo definir las variables de entorno.

### Agente evaluador — bonus

**Requerimiento:** implementar un flujo de supervisión que evalúe fidelidad, relevancia y posibles alucinaciones antes de entregar la respuesta.

**Indicadores:**

- Devuelve un objeto con `score`, entero de 0 a 10, y `reason`, texto de 50 o más caracteres.
- Evalúa al menos dos dimensiones: relevancia de los chunks, calidad de la respuesta y/o completitud.
- `reason` justifica el puntaje con observaciones específicas, por ejemplo: “Puntaje 8: responde usando 3 chunks relevantes, pero podría incorporar más detalle del chunk 2”.
