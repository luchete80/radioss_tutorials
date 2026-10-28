# Auditoría estática de la malla de model 4

No se ejecutaron Starter ni Engine. El cambio se hizo solo sobre `model_4/model_0000.rad`; el original inmediato se conserva como `model_0000.rad.before_xy_refine`. `model_3` y `model_4/model_0001.rad` permanecen intactos. El procedimiento reproducible está en `refine_workpiece.py`.

## Reconstrucción y conteos

| Medida | Antes | Después |
|---|---:|---:|
| Nodos de `/BRICK/1` | 64,256 | 127,254 |
| Elementos de `/BRICK/1` | 47,250 | 63,000 |
| Celdas XY en cada piel z extrema | 15,750 | 63,000 |
| Capas de elementos a través de Z | 3 | 1 |
| Coordenadas Z de la pieza | interiores entre 0 y 0.0002 m | solo 0 y 0.0002 m |
| Nodos totales del deck | 64,616 | 127,614 |

Las 15,750 caras externas en `z=0` y las 15,750 en `z=0.0002 m` tenían correspondencia XY exacta al comparar coordenadas redondeadas a 12 decimales. Cada celda de superficie se subdividió en cuatro, compartiendo nodos medios por arista y por cara a partir de las IDs de sus padres. La nueva capa conecta las dos pieles coincidentes y conserva el espesor total de `0.2 mm`.

El conteo de caras exteriores del resultado es 63,000 en cada piel Z, 500 en cada cara Y y 126 en cada cara X. Las caras internas tienen incidencia dos; no se encontraron huecos internos ni caras interiores expuestas. Todos los nodos generados pertenecen a elementos y no quedan referencias a los nodos internos Z retirados.

## Jacobianos, volumen y tamaño XY

- Todos los Jacobianos evaluados en los ocho puntos de integración por brick son positivos. El mínimo en la malla nueva es `3.8059e-14 m^3` por unidad de cubo natural. El mínimo volumen integrado es `3.0557e-13 m^3`.
- Volumen total de `/BRICK/1`: `2.000000000000001e-8 m^3` antes y después.
- Las aristas XY refinadas en la región de corte (`y >= 0.004 m`) miden `0.0387–0.0423 mm`, mediana `0.0399 mm`. La malla queda más fina que antes, pero no alcanza exactamente el objetivo de `~0.03 mm`.

## Grupos, restricciones y contacto

| Grupo | Antes | Después | Uso auditado |
|---|---:|---:|---|
| 1 | 1,004 | 1,002 | `/BCS/1`, desplazamientos XYZ fijados en `y=0`; cubre toda la nueva cara de apoyo. |
| 4 | 32,131 | 127,257 | `/BCS/4`, componente Z fijada sobre las dos pieles Z; incluye 3 nodos ajenos a la pieza que se conservaron. |
| 5 | 358 | 358 | `/BCS/5`, restricciones Y/Z de herramienta; sin cambios. |
| 101 | 196 | 196 | Grupo de herramienta/contacto; sin cambios. |
| 102 | 15,060 | 29,058 | Nodos esclavos de la pieza para `/INTER/TYPE7/1`; sin nodos ajenos a la pieza. |
| 103 | 196 | 196 | Grupo de `/IMPVEL/1`; nodos de herramienta sin cambios. |
| 6 | 64,418 | 127,416 | Grupo de nodos generales; los 162 miembros externos a la pieza se conservaron. |

Las definiciones `/BCS/1`, `/BCS/4`, `/BCS/5`, `/IMPVEL/1`, `/INTER/TYPE7/1`, `/SURF/PART/EXT/2`, `/FUNCT/1` y `material.rad` no se alteraron por el refinamiento. El contacto mantiene el grupo 102 como slave y la superficie externa de part 2 (herramienta) como master. La velocidad en X sigue siendo `13.3333333333 m/s` mediante group 103.

La condición `/BCS/4` restringe Z en ambas pieles externas. Con una sola capa, todos los nodos de la pieza pertenecen a esas pieles; por eso el resultado tiene respuesta cinemática tipo plane strain en Z. La restricción existente se conservó literalmente, pero esta consecuencia de la topología debe tenerse presente al interpretar el modelo.

Se conservaron los 196 nodos y los 79 bricks de la herramienta con coordenadas y conectividad idénticas al deck previo al refinamiento. Todos los bricks de ambas partes y todos los IDs de grupo hacen referencia a nodos presentes; los IDs de elemento permanecen únicos.
