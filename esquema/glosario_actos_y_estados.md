# Glosario mínimo de actos y estados

## Actos esperados

- `consulta`: petición de orientación estructural sobre un frame.
- `clasificacion`: petición de encuadre o tipado del material aportado.
- `resumen`: petición de compactación fiel del contenido.
- `clarificacion`: petición de cierre de ambigüedad o hueco abierto.
- `derivacion`: preparación del frame para ser transferido a un agente posterior.

## Salidas globales

- `APTO`: el frame queda cerrado sin conflicto y puede darse por estructuralmente suficiente.
- `INDETERMINADO`: el frame sigue siendo gobernable, pero todavía no está cerrado.
- `NO_APTO`: existe conflicto material o insuficiencia no salvable en el estado actual.

## Política esperada

- `CERRAR_FRAME`
- `CONTINUAR_EN_W(T,k)`
- `PROPONER_FORK`
