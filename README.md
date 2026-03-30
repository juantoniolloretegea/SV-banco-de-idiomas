# Banco de idiomas del Sistema Vectorial SV

## Estatuto

Este repositorio no constituye autoridad semántica soberana ni corpus de entrenamiento estadístico. Su función es estrictamente subordinada al Sistema Vectorial SV.

Sirve para:

- probar la transducción `I_NLP`;
- verificar la cobertura del horizonte `H_NLP`;
- tensionar la clasificación `Γ_H`;
- probar la compuerta `T_NLP`;
- verificar la salida `κ_3`;
- y ensayar la política `cerrar / continuar / fork`.

No sirve para:

- entrenar distribuciones;
- inducir semántica desde frecuencia;
- introducir minería de datos;
- justificar inferencias opacas;
- ni doblegar el contrato algebraico del SV.

## Organización general

- El cascarón general del repositorio se redacta en **español**.
- Cada carpeta de idioma se documentará en su **propio idioma**.
- Los identificadores técnicos, claves JSON y nombres críticos se mantienen en ASCII cuando convenga a la estabilidad operativa.

## Estado inicial

Este arranque fija únicamente el **piloto de español**.  
Los demás idiomas quedan previstos por arquitectura, pero no nacen todavía como frente material.

## Estructura mínima

```text
README.md
/esquema/
/registros/
/idiomas/
  /espanol/
```

## Regla dura de subordinación

El banco no decide. Decide el agente SV.  
Ningún caso crea semántica nueva por acumulación.  
Todo caso debe venir tipado por observables y salida esperada.
