# Conclusiones: DESIGN.md como fuente de verdad del diseño

<!-- Local copy of the Claude Doc with the same title
     (https://claude.ai/code/artifact/b7ae0fb3-bc86-4e5f-8cee-5a437ba01caf).
     This file is the version the skill reads. Keep both in sync when either changes. -->

DESIGN.md es la fuente de verdad del diseño: se extrae del código en un proyecto existente o se genera desde cero en uno nuevo, y a partir de ahí el código se genera desde él. No depende de ningún software de diseño; las únicas entradas son el código y las decisiones del usuario. Aplica a cualquier proyecto frontend; son conclusiones razonadas, todavía no medidas.

## Alcance

- **Entradas:** el código del proyecto y las respuestas del usuario. Sin Figma, Stitch ni otra herramienta de diseño.
- **Salida:** un DESIGN.md con el formato del spec de Google, validado con su CLI, y los tokens de código generados desde él.
- **Herramientas de diseño:** si un equipo usa una, es un consumidor más de DESIGN.md, nunca su fuente.

## Idea central

DESIGN.md tiene dos capas y cada una responde una pregunta distinta.

| Capa                    | Pregunta que responde                                                                                           |
| ----------------------- | --------------------------------------------------------------------------------------------------------------- |
| Front matter (tokens)   | ¿Qué valores existen? Colores, tipografía, espaciado, radios.                                                   |
| Prosa                   | ¿Cómo y por qué se usan? ¿Qué hacer cuando **ningún token** cubre el caso? (hover, error, vacío, breakpoints, jerarquía) |

Por encima de ambas pesa un tercer eje: **cuánto de la UI gobiernan realmente los tokens en el código**. Sin DESIGN.md y sin capa de tokens, el agente recurre a sus valores por defecto (paleta Tailwind, estética shadcn) y cada pantalla diverge.

## Escenarios

El estado del proyecto define el modo de trabajo.

|                                | Sin DESIGN.md                                                                                                   | Con DESIGN.md                                                                                                    |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Proyecto con UI existente**  | **Extraer:** auditar el código, consolidar valores, escribir DESIGN.md. Desde ese momento es la fuente de verdad. | **Usar**, si los tokens gobiernan la UI. Si dominan los literales, **reconciliar** antes de confiar en él.        |
| **Proyecto desde cero**        | **Seed:** entrevista al usuario, DESIGN.md mínimo y tokens generados antes del primer componente.               | **Usar:** el agente construye la UI solo con los tokens generados.                                               |

Tener DESIGN.md no es binario. Un DESIGN.md que documenta fielmente una capa de tokens minoritaria es engañoso, porque el agente lo toma como verdad.

## Ciclo de vida

1. **Crear:** Extract (desde el código) o Seed (desde cero).
2. **Generar:** exportar los tokens a todos los consumidores de estilo del proyecto.
3. **Unificar:** reemplazar los literales por tokens generados (en Extract y Reconcile).
4. **Conectar:** un puntero en AGENTS.md o CLAUDE.md para que todo agente lea DESIGN.md antes de tocar UI.
5. **Usar:** el agente construye UI solo con tokens generados; la prosa resuelve los casos no cubiertos.
6. **Evolucionar:** un cambio de diseño se hace en DESIGN.md, se lintea y se regenera. Nunca en los archivos generados ni re-extrayendo del código.

## Señales de diagnóstico

Para elegir el modo no alcanza con saber si existe DESIGN.md: hay que medir cuánto de la UI gobiernan los tokens.

| Señal                     | Cómo se mide                                                                           | Qué indica                                                                                              |
| ------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Cobertura de tokens       | Valores literales vs. referencias a tokens en estilos, componentes y assets            | Si los literales dominan, DESIGN.md describe una minoría de la UI y el agente lo toma igual como verdad. |
| Colores sin token cercano | Colores literales a ΔE ≥ 10 del token más cercano                                      | Vocabulario faltante: requiere decisión de diseño, no refactor.                                         |
| Colores consolidables     | Colores literales exactos o a ΔE < 2 de un token                                       | Reemplazo mecánico, sin riesgo visual.                                                                  |
| Paletas ajenas            | Valores que coinciden con defaults de frameworks (Tailwind, Material, Bootstrap)       | La UI se construyó contra otro sistema, típicamente copiado de un template o generado sin contexto.     |
| Duplicación de fuentes    | El mismo token definido en más de un lugar (variables CSS y tema de la librería de UI) | Dos dueños para el mismo dato: garantiza drift.                                                         |

Distancia de color: CIE76 ΔE en espacio Lab. Menos de 2 es imperceptible; 10 o más es otro color. En un caso real auditado, los valores literales superaban a las referencias a tokens y una sección entera usaba la paleta por defecto de Tailwind sin que Tailwind fuera dependencia.

## Principios de Google sobre DESIGN.md

El spec oficial declara a DESIGN.md fuente de verdad y a sus tokens valores normativos; la herramienta solo genera en sentido DESIGN.md → código.

| Principio               | Qué dice el spec                                                                                                                             | Implicancia                                                             |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Fuente de verdad        | "it serves as a living source of truth that both humans and AI can understand and refine"                                                    | Respalda que DESIGN.md sea dueño de los estilos.                        |
| Tokens normativos       | "The tokens are the normative values; the prose provides context for how to apply them."                                                     | Los valores viven en el front matter; la prosa explica cómo aplicarlos. |
| Dirección de generación | El texto admite convertir "from or to tokens.json, Figma variables, and Tailwind". El CLI solo tiene lint, diff, export y spec: no hay import. | El soporte real es DESIGN.md → otros formatos.                          |
| Prosa como fallback     | Overview guía al agente "when a specific rule or token isn't explicitly defined".                                                            | Cubre los casos que ningún token resuelve.                              |

**Alcance del front matter:** `colors` (`primary` obligatorio), `typography`, `spacing`, `rounded` y `components` (sub-tokens y variantes como `button-primary-hover`; el spec lo marca como "actively evolving"). Sombras, breakpoints, z-index y motion no tienen grupo.

**Formatos de export:** DTCG (`tokens.json`), CSS de Tailwind v4 (`@theme`) y JSON de Tailwind v3. No genera SCSS ni temas de librerías de UI.

**Tolerancia a lo desconocido:**

| Caso                                | Comportamiento                                                                                    |
| ----------------------------------- | ------------------------------------------------------------------------------------------------- |
| Propiedad de componente desconocida | Se acepta con warning                                                                             |
| Referencia {colors.x} que no existe | Error broken-ref                                                                                  |
| Clave top-level propia              | Silenciosa, salvo que parezca un typo (unknown-key) o tenga valores de token (token-like-ignored) |
| Sección desconocida                 | Se preserva                                                                                       |

El linter también valida contraste WCAG AA en pares backgroundColor/textColor de componentes y detecta tokens de color huérfanos.

## Decisión: DESIGN.md es dueño de los estilos principales

Los valores de los tokens principales (`colors`, `typography`, `spacing`, `rounded`) se definen en el front matter de DESIGN.md y las variables del código se generan a partir de él. Está alineada con el spec de Google y aplica tanto a proyectos nuevos como a proyectos con tokens existentes, que se migran al front matter una vez.

**Queda fuera:** sombras, breakpoints, z-index y motion, porque el spec no los cubre; y los valores de implementación propios de cada componente. Siguen en código.

**Condiciones para que funcione:**

1. Los archivos generados no se editan a mano y llevan un header que lo indica.
2. Un check en CI ejecuta la generación y falla si la salida difiere de lo commiteado.
3. Se generan **todos** los consumidores de estilo del proyecto: variables CSS o SCSS, configuración de Tailwind, tema de la librería de UI (MUI, Chakra, Mantine) o de CSS-in-JS. Generar solo uno deja dos fuentes.
4. La unificación cubre todos los lugares donde aparecen valores literales: hojas de estilo, JS/TS/JSX, estilos inline y SVG.
5. Al construir UI, el agente no introduce literales. Si ningún token sirve, propone un cambio en DESIGN.md.

**Riesgo:** DESIGN.md pasa a cumplir dos funciones, valores y reglas. Si crece sin control, absorbe detalles de componentes que corresponden al código; la skill debe sostener ese límite.

## Conclusiones

Cada dato necesita un único dueño, y la generación va en un solo sentido: DESIGN.md → código.

1. **Proyecto existente:** auditoría → consolidar valores → DESIGN.md → generar tokens → reemplazar literales. Escribir DESIGN.md sin auditar primero solo documenta el desorden existente.
2. **Proyecto desde cero:** DESIGN.md antes del primer componente. Sin él, el agente usa los defaults de su framework favorito.
3. **Después de creado,** DESIGN.md se refina editándolo, nunca re-extrayendo del código: re-extraer devolvería la fuente de verdad al código.
4. **El agente tiene que saber que existe:** sin un puntero en AGENTS.md o CLAUDE.md, un DESIGN.md perfecto puede ignorarse.

| Dato                                           | Fuente de verdad          |
| ---------------------------------------------- | ------------------------- |
| Tokens principales                             | DESIGN.md (front matter)  |
| Principios y reglas                            | DESIGN.md (prosa)         |
| Variables de estilo y temas de librerías de UI | Generados desde DESIGN.md |
| Sombras, breakpoints, motion                   | Código                    |
| API de componentes                             | Código (tipos)            |
| Ejemplos de uso                                | Storybook, si existe      |
| Procesos                                       | Skills                    |

## Implicaciones para las skills

El trabajo se reparte en cuatro skills con responsabilidades separadas: `spec-design-plan` recibe el requerimiento, desglosa y deriva; `spec-design-establish` deja DESIGN.md fiel a la UI real (Extract, Reconcile, Seed, Unify); `spec-design-apply` hace que el código siga a DESIGN.md (Use, Evolve, Generate); `spec-design-stories` decide qué componentes y estados llevan story en Storybook. Los cinco modos de abajo se eligen según el estado del proyecto. Extract y Reconcile arrancan con un script de auditoría compartido (`../../_shared/spec-design/audit.py`), para que cada corrida mida igual.

| Modo    | Cuándo                                     | Qué hace                                                                                                          |
| ------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| Extract | Hay UI y no hay DESIGN.md                  | Audita con las guías por framework, agrupa por ΔE, propone tokens, escribe DESIGN.md, genera y unifica.           |
| Reconcile | Hay DESIGN.md pero dominan los literales | Audita contra DESIGN.md, lista tokens definidos en código que faltan en él, propone solo el diff de tokens nuevos o renombrados, genera y unifica. |
| Seed    | No hay UI                                  | Entrevista (producto, personalidad, color, tipografía, densidad, esquinas), DESIGN.md mínimo marcado SEED, genera. |
| Use     | Hay DESIGN.md y la tarea construye UI      | Lee DESIGN.md, usa solo tokens generados, aplica la prosa a lo no cubierto, no agrega literales.                  |
| Evolve  | Hay que cambiar un token                   | Edita DESIGN.md, lintea, regenera, revisa el diff de los generados.                                               |

Límites: no mover a DESIGN.md lo que el spec no cubre, y no corregir colores de marca por contraste, porque es una decisión de producto.

## Skills existentes para crear DESIGN.md

Google publica skills para DESIGN.md en [stitch-skills](https://github.com/google-labs-code/stitch-skills), pero casi todas dependen de Stitch y quedan fuera del alcance. La excepción es **extract-design-md**, que trabaja sobre el código.

| Skill / comando                                     | Qué hace                                                                                                                                  | Rol en esta skill                                  |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| Google `extract-design-md`                          | Extrae el diseño del código con guías por framework (React, Vue, Svelte, Angular, CSS plano) y deduplica colores casi iguales             | Sus guías por framework se usan en Extract         |
| Google `design-md`, `manage-design-system`, `code-to-design`, `upload-to-stitch`, `generate-design` | Trabajan con Stitch                                                                                   | Descartadas: dependen de Stitch                    |
| impeccable `document --seed`                        | Entrevista y DESIGN.md mínimo marcado SEED                                                                                                | Base del modo Seed                                 |
| impeccable `extract`                                | Consolida en tokens valores repetidos (3+ usos con la misma intención)                                                                    | Criterio de consolidación en Extract               |
| `@google/design.md` CLI                             | lint, diff y export                                                                                                                       | Validación y generación                            |

**Lo que ninguna cubre:**

- Estructura: `extract-design-md` usa 6 secciones propias de Stitch y su propio ejemplo no pasa el lint oficial; impeccable usa 6 y prohíbe Layout. El spec del CLI define 8.
- Dirección: todas van del código hacia DESIGN.md. Ninguna genera tokens de código desde DESIGN.md ni reemplaza valores hardcodeados.
- Uso: ninguna define cómo debe construir UI un agente una vez que DESIGN.md existe.

## Qué falta verificar

Ninguna de estas conclusiones está medida todavía.

- [ ] Medir un baseline antes de atribuir cualquier mejora.
- [ ] Validar que DESIGN.md reduce decisiones visuales inconsistentes.
- [ ] Validar que el agente consulta DESIGN.md en tareas de UI sin que se lo pidan, con el puntero en AGENTS.md o CLAUDE.md.
- [ ] Definir el generador DTCG → consumidores que el CLI no emite (propio o Style Dictionary).
- [ ] Definir el criterio de escalamiento para colores sin token cercano (ΔE ≥ 10).
- [ ] Probar el modo Seed de punta a punta en un proyecto vacío.
- [ ] Verificar el comportamiento del lint con propiedades de componente desconocidas: el spec dice warning, impeccable asume que no se soportan.

## Fuentes

- [Especificación DESIGN.md (docs/spec.md)](https://github.com/google-labs-code/design.md/blob/main/docs/spec.md)
- [README del CLI @google/design.md](https://github.com/google-labs-code/design.md)
- [Google stitch-skills](https://github.com/google-labs-code/stitch-skills)
- Skills de este repositorio: `skills/spec-design-plan/`, `spec-design-establish/`, `spec-design-apply/` y `spec-design-stories/`; lo compartido vive en `skills/_shared/spec-design/`
- Skill impeccable: `reference/document.md` y `reference/extract.md`
