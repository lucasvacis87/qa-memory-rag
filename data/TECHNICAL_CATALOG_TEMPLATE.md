# Convención de la plantilla técnica

[`technical_catalog_template.json`](technical_catalog_template.json) es un
esquema vacío y versionable. No contiene bugs, test cases, servicios, APIs,
endpoints, equipos ni smoke checks reales o ficticios.

## Campos

Cada campo técnico —`functional_domain`, `service_or_api`,
`endpoint_or_operation` y `owner_team`— usa la misma forma:

```json
{
  "state": "desconocido",
  "value": null,
  "source": null,
  "validity": null
}
```

- `value`: el texto que la fuente declara explícitamente.
- `source`: de dónde se recuperó ese texto.
- `validity`: la vigencia declarada por la fuente o el período al que aplica.

No se completa ningún campo por semejanza, suposición ni conocimiento externo.

## Estados de evidencia

| Estado | Cuándo usarlo | Regla |
| --- | --- | --- |
| `confirmado` | Hay valor, fuente y vigencia explícitos. | Los tres campos deben estar presentes. |
| `parcial` | La fuente sólo aporta una parte del dato. | Se conserva sólo esa parte; el resto sigue ausente. |
| `desconocido` | La fuente no aporta el dato. | `value`, `source` y `validity` permanecen en `null`. |

## Smoke sugerido

`suggested_smoke` mantiene la misma evidencia dentro de `evidence`, pero
siempre debe llevar `label: "sugerido"` e
`is_historical_evidence: false`. Es una propuesta respaldada por la evidencia
disponible; no es un antecedente histórico ni un test case existente.

## Ejemplo abstracto

Cuando una futura fuente declare un dato completo, una sola celda podría verse
así:

```json
{
  "state": "confirmado",
  "value": "texto explícito de la fuente",
  "source": "referencia de la fuente ficticia",
  "validity": "vigencia declarada por esa fuente"
}
```

El ejemplo muestra la forma, no un registro técnico. Antes de cargar datos QA,
cada valor deberá tener respaldo trazable en la fuente correspondiente.
