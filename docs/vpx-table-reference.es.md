# Super Star (Recreativos Franco, 1986) — referencia para autores de mesas de Visual Pinball

*Traduccion del documento vpx-table-reference.md; la version inglesa es la de referencia.*

Driver de PinMAME: `src/wpc/rfranco.c` / `rfranco.h` / `rfrancogames.c`
ROM sets: `supstarf1` — «Super Star (rev. 1)» (9 zonas de ajuste de operador; la
revisión que documenta el manual de fábrica) y `supstarf4` — «Super Star
(rev. 4)» (firmware más nuevo: 19 zonas, más correcciones reales como la
condición de carrera en el despertar entre CPUs y el watchdog de contactos
pegados). En este documento «set 1» y «set 2» se refieren a estos dos — los
nombres que tenían cuando se escribió. El set 2 es `supstarf4`, **no**
`supstarf2`.

> Desde entonces se han volcado dos revisiones más, `supstarf2` y `supstarf3`.
> Se sitúan **entre** estas dos en la cadena — el set 1 es la rev. 1 y el set 2
> es la rev. **4** de cuatro — y el driver ya tiene entradas para ellas, así que
> una mesa puede seleccionarlas. Nada de este documento cambia: todo lo que
> sigue describe las revs. 1 y 4. Las dos revisiones nuevas se diferencian de la
> rev. 1 únicamente en correcciones internas (véase `rom-revision-chain.md`);
> conservan las nueve zonas de operador de la rev. 1 y su comportamiento de
> juego, así que una mesa escrita para la rev. 1 les sirve sin cambios.

Placas: CPU 53/3291 (8085A + 8035 de sonido + 2 x AY-3-8910), driver 53/3308,
display 53/3307, fuente de alimentación 53/3309, interconexión 53/3310,
bumper/slingshot 53/3311.

Todo lo que sigue se deriva del código fuente del driver, del manual de fábrica
(`../super-star-pinball-manual.md`, incluida su *Fe de erratas*) y de un
desensamblado de la ROM del juego. Donde los tres discrepan, manda la ROM y la
discrepancia se señala. Las afirmaciones inferidas en lugar de medidas están
marcadas.

> **Lea el §6 antes de cablear nada.** Dos cosas dejarán la máquina con aspecto
> de estar viva pero sin entregar nunca una bola: *caída de bolas* (switch 27)
> debe leerse **cerrado** siempre que haya una bola en el foso, y los contactos
> de monedero deben recibir **pulsos**, nunca mantenerse cerrados. El §6.1
> también explica quién gobierna el switch 27 — por defecto el driver modela el
> foso, y `Controller.HandleMechanics = 0` lo cede por completo a la mesa.


---

## 0. Orientación rápida

| Elemento | Cantidad | Números en VPX |
|---|---|---|
| Contactos de tablero / mueble | 4 bytes de hardware, 27 contactos reales | `11`–`18`, `21`–`28`, `31`–`38`, `41`–`48` |
| Interruptores de puerta del operador | 2 | `1` (*ajuste*), `2` (*test*) — una pseudocolumna, véase §1.6 |
| Falta (tilt) | 1 | **no es un switch de la matriz** — es una línea de interrupción, accesible cerrando el switch 21, véase §1.5 |
| Lámparas | 8 columnas de matriz, 44 que pueden encenderse | `1`–`8`, `11`–`18`, … `71`–`74` (véase §2) |
| Solenoides gobernados por la CPU | 8 de las 10 salidas del decodificador realmente usadas | `2`–`5`, `7`–`10` |
| Solenoides sintetizados por el driver | 4 (bumpers y slingshots) | `17`–`20` |
| Flippers | 2, no controlados por la CPU | botones `112` / `114` de entrada, solenoides `45`–`48` de salida |
| Dígitos del display | 30 dígitos HDSP-3400 | índices de LED `0`–`33` (véase §4) |
| Interruptores DIP | ninguno | la máquina no tiene; los ajustes del operador viven en NVRAM, véase §5.1 |

Ausencias que harán tropezar al autor de una mesa:

* **No hay display de bola en juego.** El número de bola se muestra con las
  lámparas de tablero *BOLA 1*…*BOLA 5* (lámparas 31–35).
* **No hay match ni carrete de fin de partida.** *FIN DE JUEGO* es una
  lámpara (36).
* **No hay contactos de flipper ni control de flippers por la CPU.** Los
  botones de flipper alimentan las bobinas directamente a través de la placa de
  interconexión.
* **No hay contacto de golpe (slam) en la puerta ni contacto en el lanzador de
  bolas.**
* **Los dos bumpers y los dos slingshots disparan en su propia placa**
  (53/3311), directamente desde sus contactos de tablero. La CPU nunca los
  gobierna; el driver sintetiza los solenoides 17–20 para tener de dónde colgar
  un sonido y un flasher — véase §3.2.

### 0.1 Carga desde el script de la mesa

```vbscript
Const cGameName = "supstarf1"     ' rev. 1 - or "supstarf4" for rev. 4
With Controller
    .GameName = cGameName
    .SplashInfoLine = "Super Star (Recreativos Franco 1986)"
    ' .HandleMechanics = 0        ' only if your table owns the trough - see 6.1
    .Run
End With
```

No hay ningún `.vbs` auxiliar específico de la máquina; el driver no necesita
nada más allá del objeto controlador estándar. Elija el set con `cGameName`. La
rev. 2 es la mejor opción por defecto para jugar (es la que llevaban las
máquinas tardías); la rev. 1 es el original exacto según el manual.

### 0.2 Sonido

**Todo el audio del juego sale de la emulación** — dos AY-3-8910 detrás de un
8035, emitido por el audio de VPinMAME como en cualquier otra máquina de estado
sólido. Los carillones, las melodías, la cascada de los bumpers: no recree nada
de eso en la mesa.

Lo que la máquina no puede producir es ruido *mecánico*. Añada muestras solo
para: los flippers, los bumpers y los slingshots (los solenoides 17-20 existen
exactamente para esto), los reset de las bancadas de dianas (solenoides 7/9),
el disparo de salida de bola (solenoide 10), los contadores de monedas (4/5) y
el knocker (2). Los sonidos de inicio de bola, de tanteo y de especial son
trabajo de la ROM.

### 0.3 Iluminación general

No hay ninguna bajo control de la CPU. La iluminación general del tablero y del
frontón va cableada directamente al transformador — está encendida siempre que
la máquina lo está. Modélela como siempre encendida; no hay relé de iluminación
general que seguir ni atenuación.

---

## 1. Switches

El driver declara su propia numeración con
`MDRV_SWITCH_CONV(rfranco_sw2m, rfranco_m2sw)`, dando la convencional
`column*10 + row + 1`. En VPX: `Controller.Switch(nn) = True/False`.

**Polaridad.** Se aplica en todo el documento la convención normal de PinMAME:
`True` = contacto cerrado. El driver gestiona internamente todas las
inversiones activo-bajo del hardware.

### 1.1 Columna 1 — conector JG, leída directamente en `0x4000`

Ocho contactos de tablero llegan del tablero a la placa de CPU por el conector
JG y se leen como un único byte en `0x4000` (selección de chip CS1 del 74S138).
Son los contactos *de tanteo* — y cuatro de ellos disparan además una bobina
localmente.

Corroborado por partida doble: la tabla del conector JG de la placa de CPU da
el bit de bus de cada contacto, y la tabla del test de contactos de la propia
ROM en `0x34A2` lista el mismo orden.

| # | Bus | Nombre en el manual | Descripción | Ubicación en el tablero | Notas |
|---|---|---|---|---|---|
| 11 | AD0 | 10 PUNTOS | Contactos de los slingshots (*rechazador*) | abajo a la izquierda y abajo a la derecha | **Par en paralelo**: contactos 24 + 25 del manual, uno dentro de cada cuerpo de slingshot. Cualquiera de los dos cierra el 11 y la CPU no puede distinguir cuál. Dispara además los solenoides sintéticos **19 y 20** — véase §3.2. Momentáneo. |
| 12 | AD1 | BUMPER DERECHO | Bumper derecho | arriba a la derecha | Dispara además el solenoide sintético **18**. Momentáneo. |
| 13 | AD2 | DIANA IZQUIERDA | Bancada de dianas izquierda, «cualquier diana» | bancada izquierda | Contacto a nivel de bancada. Las dianas individuales son 33–37. **Pulse este además de cerrar la diana individual.** |
| 14 | AD3 | RAMPA ESPECIAL IZQUIERDA | Pasillo del especial izquierdo | pasillo exterior superior izquierdo | Un rollover, **no** un agujero y **no** una bobina. Cobra el especial cuando la lámpara 52 está encendida. |
| 15 | AD4 | DIANA DERECHA | Bancada de dianas derecha, «cualquier diana» | bancada derecha | Contacto a nivel de bancada. Dianas individuales 38, 41–44. |
| 16 | AD5 | RAMPA ESPECIAL DERECHA | Pasillo del especial derecho | pasillo exterior superior derecho | Un rollover, **no** un agujero y **no** una bobina. Cobra el especial cuando la lámpara 42 está encendida. |
| 17 | AD6 | 100 PUNTOS | Rollover de 100 puntos | centro del tablero | **Par en paralelo**: contactos 10 + 21 del manual. Momentáneo. |
| 18 | AD7 | BUMPER IZQUIERDO | Bumper izquierdo | arriba a la izquierda | Dispara además el solenoide sintético **17**. Momentáneo. |

### 1.2 Columna 2 — entradas del mueble, leídas a través de la CPU de sonido

El 8085 no puede leerlas directamente. Se lo pide al 8035 con el comando de
sonido `0x99`; el 8035 selecciona PSG2 (IC2) y lee el registro AY `0x0E`, y la
respuesta vuelve a través del latch 8212. Conector JO de la placa driver;
conector JC de la placa de CPU.

| # | Bit del puerto | Nombre en el manual | Descripción | Ubicación | Notas |
|---|---|---|---|---|---|
| 21 | PA0 | — | *(prestado)* FALTA (tilt) | mueble | No es un contacto real — el juego nunca lee este bit. El driver lo toma prestado para activar RST 6.5, que es como el péndulo de la falta llega a la CPU. Véase §1.5. |
| 22 | PA1 | — | — | — | **Sin cablear, nunca se lee.** Libre. |
| 23 | PA2 | — | — | — | **Sin cablear, nunca se lee.** Libre. |
| 24 | PA3 | — | — | — | **Sin cablear, nunca se lee.** Libre. |
| 25 | PA4 | MONEDERO 25 PTS. | Monedero de 25 pta | puerta de monedas | **Obligatorio.** Debe ser un pulso corto — véase §6.1. |
| 26 | PA5 | MONEDERO 100 PTS. | Monedero de 100 pta | puerta de monedas | **Obligatorio.** Debe ser un pulso corto — véase §6.1. |
| 27 | PA6 | CAIDA DE BOLAS | Caída de bola / foso | foso | **Obligatorio, y debe leerse CERRADO en reposo** — véase §6.1. Contacto 28 del manual; la placa driver también rotula esta red como *contacto final partidas*. |
| 28 | PA7 | PULSADOR PARTIDAS | Botón de partida | frente del mueble | **Obligatorio.** Contacto 29 del manual. Es también el botón de «avance» dentro de todos los menús de operador. |

El programa del juego solo comprueba los bits 4–7 (verificado por búsqueda
exhaustiva de las lecturas de `C027`), y por eso el driver puede tomar
prestados los cuatro bajos. El 21 es la *falta* (§1.5), el 23 y el 24 son los
interruptores de la puerta (§5.1), y el 22 no hace nada.

### 1.3 Columna 3 — la cadena serie de 74165, mitad izquierda (IC6 de la placa driver, conector JM)

IC6 e IC5 de la placa driver son dos registros de desplazamiento 74165 en
cascada cuyo contenido sale bit a bit hacia el pin SID del 8085. El contenido
de IC6 sale primero, y su entrada H (JM3) queda desplazada y perdida antes del
primer `RIM` del firmware, así que es invisible para el juego — que es
exactamente el motivo por el que la fe de erratas del manual mueve el contacto
del *picabolas* de JM3 a JN2.

| # | Entrada 74165 | Con. | Nombre en el manual | Descripción | Ubicación | Notas |
|---|---|---|---|---|---|---|
| 31 | IC6 G | JM4 | PASILLO INFERIOR DERECHO | Pasillo inferior derecho | abajo a la derecha | **Par en paralelo**: contactos 23 + 27 del manual |
| 32 | IC6 F | JM5 | PASILLO INFERIOR IZQUIERDO | Pasillo inferior izquierdo | abajo a la izquierda | **Par en paralelo**: contactos 22 + 26 del manual |
| 33 | IC6 E | JM6 | DIANA IZQUIERDA 1ª | Diana izquierda 1 | bancada izquierda | cerrado = diana **abatida** |
| 34 | IC6 D | JM7 | DIANA IZQUIERDA 3ª | Diana izquierda 3 | bancada izquierda | véase la nota de discrepancia más abajo |
| 35 | IC6 C | JM8 | DIANA IZQUIERDA 2ª | Diana izquierda 2 | bancada izquierda | véase la nota de discrepancia más abajo |
| 36 | IC6 B | JM1 | DIANA IZQUIERDA 4ª | Diana izquierda 4 | bancada izquierda | |
| 37 | IC6 A | JM2 | DIANA IZQUIERDA 5ª | Diana izquierda 5 | bancada izquierda | |
| 38 | IC5 H | JN3 | DIANA DERECHA 5ª | Diana derecha 5 | bancada derecha | primer bit de la mitad de IC5 |

> **Discrepancia en los switches 34 / 35.** La tabla de cableado de IC6 del
> manual rotula JM7 como *diana izquierda 2* y JM8 como *diana izquierda 3*. La
> tabla del test de contactos de la propia ROM del juego (idéntica byte a byte
> en ambas revisiones de la ROM) informa del contacto **13** para la posición
> JM7 y del contacto **12** para JM8 — es decir, dianas 3 y 2, al revés. Quince
> de las dieciséis posiciones serie coinciden entre las dos fuentes; esta es la
> única que no. La ROM es lo que la máquina muestra realmente en la zona 9, así
> que aquí se trata como autoritativa. En la práctica solo importa si los
> premios de la bancada difieren según la posición de la diana.

### 1.4 Columna 4 — la cadena serie, mitad derecha (IC5 de la placa driver, conector JN)

| # | Entrada 74165 | Con. | Nombre en el manual | Descripción | Ubicación | Notas |
|---|---|---|---|---|---|---|
| 41 | IC5 G | JN4 | DIANA DERECHA 4ª | Diana derecha 4 | bancada derecha | |
| 42 | IC5 F | JN5 | DIANA DERECHA 3ª | Diana derecha 3 | bancada derecha | |
| 43 | IC5 E | JN6 | DIANA DERECHA 2ª | Diana derecha 2 | bancada derecha | |
| 44 | IC5 D | JN9 | DIANA DERECHA 1ª | Diana derecha 1 | bancada derecha | |
| 45 | IC5 C | JN8 | PASILLO SUPERIOR DERECHO | Pasillo superior derecho | arriba a la derecha | contacto 2 del manual |
| 46 | IC5 B | JN7 | PASILLO SUPERIOR IZQUIERDO | Pasillo superior izquierdo | arriba a la izquierda | contacto 1 del manual |
| 47 | IC5 A | JN2 | PICABOLAS | Picabolas (spinner) | centro del tablero | Movido aquí por la *Fe de erratas* (JM3 → JN2). Otorga el *especial picabolas*. |
| 48 | IC5 SER | JN1 | — | — | — | **Sin uso.** La entrada serie flotante de IC5. El driver la enmascara fuera de la cadena de desplazamiento, así que escribirla no hace nada. Déjela abierta. |

**Dianas.** Contacto cerrado = diana **abatida**. Una bancada completada es
«las cinco cerradas». Los contactos a nivel de bancada (13 / 15) son hilos
separados de los contactos individuales de las dianas, así que una diana (drop
target) de VPX debe cerrar su propio switch *y* pulsar el switch de bancada. Al
comienzo de cada bola el juego dispara la bobina de reset de cualquier bancada
que no esté completamente levantada.

### 1.5 La falta (tilt) — no es un switch de la matriz

El péndulo de la falta llega a la CPU por JD1 y pulsa **RST 6.5** (vector
`0x0034` → manejador en `0x0286` en el set 1). No tiene número de switch.

En PinMAME independiente es el bit `0x0100` del puerto de entrada común
(«Falta (Tilt)», tecla por defecto `INSERT`).

**Desde un front end, cierre el switch 21.** La ROM nunca lee ese bit del byte
de mueble, así que el driver lo toma prestado: cerrar el 21 activa RST 6.5 y
abrirlo libera la línea. Es un nivel, no un pulso — la ROM deja RST 6.5
enmascarada salvo una instrucción por pasada de TRAP, así que un pulso más
corto que un fotograma se arma y desaparece antes de que la CPU pueda mirar.
Manténgalo cerrado mientras el péndulo esté oscilando.

Medido, desde el modo attract en el set 1: cerrar el switch 21 dejó `C01C`
en `0xFF`, encendió la **lámpara 11** (*luz falta*, que es el pin 3 de IC1 en
FASE B según la fe de erratas) y llenó los treinta dígitos con el patrón del
7447 para 14; abrirlo borró `C01C` y la máquina volvió a esperar una bola en el
foso con la lámpara de falta aún encendida. Ese es el aspecto de una falta — y
también el del manejador de averías por cualquier otra causa, y por eso el §6.1
dice que se lea `C01C` antes de sospechar del display.

### 1.6 Interruptores de puerta del operador — switches 1 y 2

Los dos interruptores de la puerta (*interruptor de ajuste*, *interruptor de
test*) tampoco están en ninguno de los cuatro bytes de hardware. Llegan como los
bits 7/6 del puerto B de PSG2, y el driver les da una pseudocolumna propia: el
mismo sitio donde los Williams System 4–11 tienen su puerta de monedas.

| # | Bit | Nombre | Notas |
|---|---|---|---|
| 1 | PB7 | INTERRUPTOR DE AJUSTE | **Cerrado = subido.** Abierto en reposo. |
| 2 | PB6 | INTERRUPTOR DE TEST | **Cerrado = subido.** Abierto en reposo. |

En VPX: `Controller.Switch(1)` y `Controller.Switch(2)`, como cualquier otro
switch. No hay ningún DIP de por medio — esta máquina no tiene ninguno.

| Switch 1 (ajuste) | Switch 2 (test) | Modo al que se entra al encender |
|---|---|---|
| abierto | abierto | **JUEGO** (juego normal) |
| abierto | cerrado | **TEST DE LUCES Y VISUALIZACION DE RAM** |
| cerrado | abierto | **BORRADO DE DISPLAY Y CREDITOS** |
| cerrado | cerrado | **AJUSTES DE TANTEO Y TEST DE CONTACTOS** |

Ambos abiertos es la posición de reposo, así que una mesa que no los toque
obtiene juego normal. La ROM elige el modo en el arranque (despacho en
`0x00BB`), así que entrar en un menú requiere un **reset** con los interruptores
ya puestos; su estado sobrevive a un reset suave, porque core solo limpia la
matriz en un arranque en frío. Una vez dentro de un menú la pareja se relee en
vivo, que es lo que hace funcionar la navegación de «baje el interruptor de
ajuste, pulse partida».

---

## 2. Lámparas

Tres decodificadores BCD-a-decimal CD4028 en la placa driver (IC1, IC2, IC3)
gobiernan cada uno un tiristor BT106 por salida. Un tiristor disparado conduce
hasta el final del semiciclo de red, así que **cada salida del decodificador
sirve a dos lámparas** — una en **FASE A** y otra en **FASE B** — seleccionadas
según el semiciclo en que se disparó. La CPU de sonido informa del semiciclo
actual por su pin T1 y el 8085 lo usa para elegir entre dos copias de las
tablas de lámparas.

El driver da a cada par (decodificador, fase) una columna de matriz propia:

| Col | Decodificador | Fase | Códigos del decodificador | Conector | Lámparas VPX |
|---|---|---|---|---|---|
| 0 | IC1 | FASE A | 0–7 | JA → placa de display | 1–8 |
| 1 | IC1 | FASE B | 0–7 | JA → placa de display | 11–18 |
| 2 | IC2 | FASE A | 0–7 | JQ pines impares | 21–28 |
| 3 | IC2 | FASE B | 0–7 | JQ pines pares | 31–38 |
| 4 | IC3 | FASE A | 0–7 | JP pines impares | 41–48 |
| 5 | IC3 | FASE B | 0–7 | JP pines pares | 51–58 |
| 6 | IC1 e IC2 | ambas | 8–9 | JQ | 61–68 |
| 7 | IC3 | ambas | 8–9 | — | 71–74 |

Dentro de las columnas 0–5, **el bit *n* es el código de decodificador *n***,
así que el número de lámpara es `col*10 + code + 1`.

**Números de lámpara.** El driver instala `MDRV_LAMP_CONV(rfranco_lamp2m,
rfranco_m2lamp)`, así que las lámparas se numeran `column*10 + row + 1` — el
mismo esquema que los switches, y los mismos números que informa la interfaz de
depuración. Comprobado por muestreo en la máquina en marcha: la lámpara 11 es
*luz falta*, la 12 *jugador 1º*, la 21 *avance 10000*, la 31 *bola 1ª*, la 36
*fin de juego*, la 45 *pulsador partidas* y la 52 *especial izquierda*, cada
una encendiéndose exactamente cuando debe.

`Controller.ChangedLamps` y `vp_getLamp` informan ambos de estos números —
verificados uno contra otro en la máquina en marcha.

El juego hace sus propios parpadeos (mantiene tablas de superposición
separadas de «forzar encendido» y «forzar apagado» y las mezcla en fotogramas
alternos), así que la mesa debe seguir el estado de las lámparas y no añadir
lógica de parpadeo.

### 2.1 Columna 0 — IC1, FASE A (lámparas 1–8): frontón

| Lámpara | Código | Pin | Nombre en el manual | Descripción |
|---|---|---|---|---|
| 1 | 0 | JA8 | LUZ FALTA | Falta (tilt) — **nunca se enciende**, véase §2.9 |
| 2 | 1 | JA20/21 | JUGADOR 3º | Jugador 3 en juego |
| 3 | 2 | JA7 | JUGADOR 4º | Jugador 4 en juego |
| 4 | 3 | JA9 | LOTERIA 90 | Lotería 90 |
| 5 | 4 | JA10 | LOTERIA 80 | Lotería 80 |
| 6 | 5 | JA11 | LOTERIA 70 | Lotería 70 |
| 7 | 6 | JA12 | LOTERIA 60 | Lotería 60 |
| 8 | 7 | JA13 | LOTERIA 50 | Lotería 50 |

### 2.2 Columna 1 — IC1, FASE B (lámparas 11–18): frontón

| Lámpara | Código | Pin | Nombre en el manual | Descripción |
|---|---|---|---|---|
| **11** | 0 | JA8 | LUZ FALTA | **Falta (tilt) — esta es la que se enciende** |
| 12 | 1 | JA20/21 | JUGADOR 1º | Jugador 1 en juego |
| 13 | 2 | JA7 | JUGADOR 2º | Jugador 2 en juego |
| 14 | 3 | JA9 | LOTERIA 00 | Lotería 00 |
| 15 | 4 | JA10 | LOTERIA 10 | Lotería 10 |
| 16 | 5 | JA11 | LOTERIA 20 | Lotería 20 |
| 17 | 6 | JA12 | LOTERIA 30 | Lotería 30 |
| 18 | 7 | JA13 | LOTERIA 40 | Lotería 40 |

Las lámparas de la *lotería* son la rueda de lotería 0…90 del frontón. Cada pin
de JA lleva dos bombillas, una por fase: `JA9` = 00/90, `JA10` = 10/80,
`JA11` = 20/70, `JA12` = 30/60, `JA13` = 40/50. (A la lista de piezas del
manual le falta la pieza `01-2339 Pantallas Luces Loteria`, señalado en su
propia fe de erratas.)

### 2.3 Columna 2 — IC2, FASE A (lámparas 21–28): la escalera de *avance*

| Lámpara | Código | Pin | Nombre en el manual | Descripción | Luz nº del manual |
|---|---|---|---|---|---|
| 21 | 0 | JQ11 | LUZ 10000 PUNTOS | Avance 10,000 | 19 |
| 22 | 1 | JQ19 | LUZ 20000 PUNTOS | Avance 20,000 | 18 |
| 23 | 2 | JQ13 | LUZ 30000 PUNTOS | Avance 30,000 | 17 |
| 24 | 3 | JQ17 | LUZ 40000 PUNTOS | Avance 40,000 | 16 |
| 25 | 4 | JQ15 | LUZ 50000 PUNTOS | Avance 50,000 | 15 |
| 26 | 5 | JQ5 | LUZ 60000 PUNTOS | Avance 60,000 | 14 |
| 27 | 6 | JQ3 | LUZ 70000 PUNTOS | Avance 70,000 | 13 |
| 28 | 7 | JQ9 | LUZ 80000 PUNTOS | Avance 80,000 | 12 |

Los peldaños de 90,000 y 100,000 están en los códigos 8 y 9 — lámparas 65
y 66, §2.7.

### 2.4 Columna 3 — IC2, FASE B (lámparas 31–38)

| Lámpara | Código | Pin | Nombre en el manual | Descripción | Luz nº del manual |
|---|---|---|---|---|---|
| 31 | 0 | JQ12 | LUZ BOLA 1ª | Bola 1 | 27 |
| 32 | 1 | JQ20 | LUZ BOLA 2ª | Bola 2 | 28 |
| 33 | 2 | JQ14 | LUZ BOLA 3ª | Bola 3 | 29 |
| 34 | 3 | JQ18 | LUZ BOLA 4ª | Bola 4 | 30 |
| 35 | 4 | JQ16 | LUZ BOLA 5ª | Bola 5 | 31 |
| 36 | 5 | JQ6 | LUZ FINAL PARTIDA | Fin de partida | 32 |
| 37 | 6 | JQ4 | LUZ BOLA EXTRA (CONSEGUIDA) | Bola extra conseguida | 26 |
| 38 | 7 | JQ10 | LUZ ESPECIAL PICABOLAS | Especial del picabolas | 3 |

**Las lámparas 31–35 son la única indicación de bola en juego que tiene la
máquina.**

### 2.5 Columna 4 — IC3, FASE A (lámparas 41–48)

| Lámpara | Código | Pin | Nombre en el manual | Descripción | Luz nº del manual |
|---|---|---|---|---|---|
| 41 | 0 | JP1 | BUMPER DERECHO | Bumper derecho | 5 |
| 42 | 1 | JP9 | ESPECIAL DERECHA | Especial derecho | 9 |
| 43 | 2 | JP3 | BOLA EXTRA DIANA DERECHA | Bola extra, bancada de dianas derecha | 8 |
| 44 | 3 | JP7 | PASILLO DERECHO INF. Y SUPERIOR | Pasillos derechos | 2, 23, 25 — **tres bombillas en una salida** |
| 45 | 4 | JP5 | PULSADOR PARTIDAS | Lámpara del pulsador de partidas | 33 |
| 46–48 | 5–7 | — | — | *(códigos 5–7 del decodificador sin cablear)* | — |

### 2.6 Columna 5 — IC3, FASE B (lámparas 51–58)

| Lámpara | Código | Pin | Nombre en el manual | Descripción | Luz nº del manual |
|---|---|---|---|---|---|
| 51 | 0 | JP2 | BUMPER IZQUIERDO | Bumper izquierdo | 4 |
| 52 | 1 | JP10 | ESPECIAL IZQUIERDA | Especial izquierdo | 6 |
| 53 | 2 | JP4 | BOLA EXTRA DIANA IZQUIERDA | Bola extra, bancada de dianas izquierda | 7 |
| 54 | 3 | JP8 | PASILLO IZQUIERDO INF. Y SUPERIOR | Pasillos izquierdos | 1, 22, 24 — **tres bombillas en una salida** |
| 55 | 4 | JP6 | — | *(N.C. en el conector)* | — |
| 56–58 | 5–7 | — | — | *(sin cablear)* | — |

### 2.7 Columna 6 — códigos 8 y 9 del decodificador para IC1 e IC2 (lámparas 61–68)

| Lámpara | Decodificador | Fase | Código | Pin | Nombre en el manual | Descripción | Luz nº del manual |
|---|---|---|---|---|---|---|---|
| 61–64 | IC1 | A, A, B, B | 8, 9, 8, 9 | — | — | *(N.U. en el esquema — nunca se encienden)* | — |
| 65 | IC2 | A | 8 | JQ1 | LUZ 90000 PUNTOS | Avance 90,000 | 11 |
| 66 | IC2 | A | 9 | JQ7 | LUZ 100000 PUNTOS | Avance 100,000 | 10 |
| 67 | IC2 | B | 8 | JQ2 | LUZ AVANZE DOBLE | Avance doble | 20 |
| 68 | IC2 | B | 9 | JQ8 | LUZ AVANZE TRIPLE | Avance triple | 21 |

El *doble* se enciende cuando se completa una bancada de dianas mientras la
otra aún tiene dianas levantadas; el *triple*, cuando ambas bancadas están
abatidas.

### 2.8 Columna 7 — códigos 8 y 9 del decodificador para IC3 (lámparas 71–74)

Nada está cableado a los códigos 8 y 9 de IC3, así que las lámparas 71–74 nunca
se encienden. La columna existe solo para mantener regular la disposición.

### 2.9 La lámpara de la falta

La fe de erratas sitúa la lámpara de la *falta* en el pin 3 de IC1, que es la
salida 0 del decodificador, con el pin de conector JA8. No dice en cuál de las
dos fases de red está — pero la ROM sí: todas las escrituras que activan o
preservan el código 0 apuntan a la copia de **FASE B** de la tabla de IC1
(`C21C`), y la copia de FASE A (`C219`) se enmascara repetidamente con
`ANI 0x1F`, que borra el código 0 incondicionalmente. El manejador de fallo de
alimentación en `0x0244` la enciende de la misma manera.

**Asocie la lámpara 11. La lámpara 1 no se encenderá nunca.** Confirmado en la
máquina: cerrar el switch 21 enciende la lámpara 11 y nada más de la
columna 0 — véase §1.5.

### 2.10 Comprobación de cobertura contra el manual

La lista *LUCES DE TABLERO* del manual recoge 33 bombillas de tablero; la placa
driver tiene 29 salidas de tablero (9 utilizables en IC3, 20 en IC2). La
diferencia son los dos grupos de pasillos — el pasillo izquierdo (luces 1, 22,
24 del manual) son tres bombillas en `JP8` y el derecho (2, 23, 25) tres
bombillas en `JP7`. Las 33 quedan contabilizadas arriba. IC1 añade 15 bombillas
de frontón (falta ×1, jugador ×4, lotería ×10).

29 + 15 = **44 números de lámpara que pueden encenderse**, uno por salida
física.

Los números de pin del conector JA se dan tal como están impresos en la hoja de
la placa driver. La fe de erratas invierte el conector JA completo y la hoja de
la placa de display lo numera al revés; los nombres de señal son fiables, los
números de pin de JA no.

---

## 3. Solenoides

### 3.1 Bobinas gobernadas por la CPU — IC7 de la placa driver (un cuarto CD4028), conector JL

El 8035 escribe un byte en el registro `0x0F` de PSG1; su **nibble alto** es un
código de selección del 4028. Los códigos 0–9 eligen una salida, los 10–15 no
seleccionan ninguna. **Número de solenoide en VPX = código del decodificador
+ 1.**

En VPX: `SolCallback(n) = "SubName"`.

| # | Código | Pin | Nombre en el manual | Descripción | Función | ¿Lo usa la ROM? |
|---|---|---|---|---|---|---|
| 1 | 0 | JL10 | — | *(sin cablear)* | El pin del conector es N.C. — pero véase la salvedad más abajo: el manual pone aquí la TACA y el N.C. en la salida 1, y la ROM discrepa. | nunca se activa |
| 2 | 1 | JL6 | TACA / PARTIDA ESPECIAL | Knocker | Golpea en cada premio de *especial* (partida gratis) — **observado**, en ambos sets. Dispara incluso cuando el propio crédito se rechaza porque la máquina ya está en el máximo de la zona 16. Véase la salvedad más abajo. | sí |
| 3 | 2 | JL7 | BOBINA MONEDERO | Bobina del monedero | Actuador de bloqueo/desvío de monedas | sí |
| 4 | 3 | JL9 | CONTADOR 25 PTS. | Contador de monedas de 25 pta | Contador mecánico de auditoría, pulsado con cada moneda de 25 pta | sí |
| 5 | 4 | JL8 | CONTADOR 100 PTS. | Contador de monedas de 100 pta | Contador mecánico de auditoría, pulsado con cada moneda de 100 pta | sí |
| 6 | 5 | JL3 | FLIPPER | Relé de alimentación de bobinas (RL1 en la placa de interconexión, rotulado *relé alimentación bobinas*) | **El programa del juego no lo energiza nunca.** Los flippers están activos siempre que la máquina está encendida. Ignórelo. | nunca se activa |
| 7 | 6 | JL2 | BANCADA IZQUIERDA | Reset de la bancada izquierda | Levanta las 5 dianas izquierdas | sí |
| 8 | 7 | JL5 | PICA-BOLAS | Bobina del picabolas (spinner) | Acciona el mecanismo del picabolas | sí |
| 9 | 8 | JL1 | BANCADA DERECHA | Reset de la bancada derecha | Levanta las 5 dianas derechas | sí |
| 10 | 9 | JL4 | SALIDA BOLAS | Expulsión de bola / kicker del foso | **Obligatorio** — sirve la bola al carril de lanzamiento | sí |

La columna «lo usa la ROM» no es una conjetura: cada escritura al campo de bits
de bobinas es un `MVI A,<bit>` inmediato y hay exactamente ocho en el set 1.
Los códigos 0 y 5 no se activan nunca.

> **Salvedad sobre el solenoide 2 — lo único de aquí que el manual contradice.**
> Lo *medido* es que la ROM dispara la salida **1** del 4028 cuando otorga una
> partida gratis: otorgue un especial y la selección de bobina leída en el
> puerto B de PSG1 es la salida 1, en ambos ROM sets. Nada en ninguna parte
> dispara la salida 0.
> Lo *inferido* es que la salida 1 es el knocker. El esquema de la placa driver
> (página 17 del manual = `manual-images/page-23.jpg`) imprime el número de pin
> de salida del 4028 en cada fila — 3, 14, 2, 15, 1, 6, 7, 4, 9, 5 de abajo
> arriba, que es exactamente Q0…Q9 — y según esos números de pin **Q0 va a JL6
> TACA y Q1 a JL10 N.C.** La tabla del conector JL de la hoja anterior
> (`manual-images/page-22.jpg`) respalda la segunda mitad: JL10 no tiene color
> de hilo asignado donde todos los demás pines sí.
> Tomado al pie de la letra, la máquina no golpearía nunca, y la única salida
> que el programa sí gobierna no iría a ninguna parte. El driver asume en
> cambio que las dos filas inferiores de la hoja tienen sus destinos JL
> transpuestos — la propia *fe de erratas* del mismo manual ya corrige dos
> transposiciones exactamente de este tipo (conector JA invertido; pines 10
> y 11 de IC5 intercambiados) — y mantiene la TACA en el solenoide 2. **Solo
> una placa real lo zanja.** Si está cableando una mesa y le importa, trate el
> solenoide 2 como «partida gratis otorgada» y no como una bobina concreta.
> La propia lectura del esquema se ha calibrado contra los tres decodificadores
> de lámparas de la misma hoja, cuyos mapeos están verificados por la ROM: las
> veinticinco filas verificables coinciden con los números de pin impresos, así
> que las dos filas de IC7 son los únicos valores atípicos de la hoja y no se
> trata de una simple lectura errónea. Lo que el dueño de una máquina podría
> comprobar está recogido en `questions-for-a-real-machine.md` Q1/Q2.

Dos datos de hardware que conviene conocer:

* **Solo se sostiene una bobina a la vez.** El firmware emite diez ranuras de
  tiempo de selección del decodificador por semiciclo; antes de enviarlas busca
  el primer código de bobina activo y lo copia en la *última* ranura, de modo
  que el 4028 queda seleccionando esa bobina el resto del semiciclo. Si se
  pidieran dos bobinas a la vez, la de número más bajo se lleva la ranura
  sostenida.
* Las bobinas se redisparan en cada semiciclo de red (los tiristores lo
  necesitan). El driver acumula todo lo disparado desde el fotograma de vídeo
  anterior, así que es normal que una bobina se informe durante fotogramas
  completos.

### 3.2 Bobinas sintetizadas — los bumpers y los slingshots

La placa 53/3311, «CONTROL BUMPER Y EXPULSOR», acciona cuatro bobinas
directamente desde cuatro contactos de tablero a través de un monoestable RC y
un BDX53C, **sin intervención alguna de la CPU**. El 8085 solo llega a saber
que el contacto se cerró. Su conector de 15 vías (`manual-images/page-29.jpg`)
los nombra: ENTRADA/SALIDA BUMPER IZQUIERDO en los pines 1/2, BUMPER DERECHO
en 4/5, EXPULSOR IZQUIERDO en 6/7 y EXPULSOR DERECHO en 10/11.

**Los «expulsores» son los slingshots, no agujeros de expulsión.** Este tablero
no tiene agujeros. El plano de contactos (página 3 del manual =
`manual-images/page-07.jpg`) sitúa los contactos **24 y 25**, ambos llamados
*10 PUNTOS*, dentro de los dos cuerpos triangulares de las esquinas inferiores,
y la lista de piezas llama a ese mecanismo el *RECHAZADOR* (slingshot) — el
único mecanismo con bobina de todo el manual que el conector JL de la placa
driver no contabiliza, y hay exactamente dos. Los contactos 3 y 7, *rampa
especial izquierda/derecha*, son simples hilos de rollover en los pasillos
exteriores con las lámparas ESPECIAL al lado; no accionan nada.

Los contactos 24 y 25 están cableados en paralelo a AD0, que es el switch
**11** — lo dice la propia tabla del test de contactos de la ROM, que marca AD0
como par en paralelo. Así que la CPU ve un contacto para dos bobinas y no puede
distinguir la izquierda de la derecha.

| # | Disparado por el switch | Nombre en el manual | Descripción |
|---|---|---|---|
| 17 | 18 (BUMPER IZQUIERDO) | BOBINA BUMPER IZQUIERDO | Bobina del bumper izquierdo |
| 18 | 12 (BUMPER DERECHO) | BOBINA BUMPER DERECHO | Bobina del bumper derecho |
| 19 | 11 (10 PUNTOS, contactos 24+25) | EXPULSOR IZQUIERDO | Bobina del slingshot izquierdo |
| 20 | 11 (10 PUNTOS, contactos 24+25) | EXPULSOR DERECHO | Bobina del slingshot derecho |

El 19 y el 20, por tanto, disparan siempre juntos. Más que una decisión de
modelado, es una afirmación sobre el cableado: no hay en la máquina información
que los separe.

Son útiles para sonido e iluminación, pero **no los use para mover la bola**:
se generan *a partir de* su switch, un fotograma o más después de él, así que
no pueden decir nada que no se supiera ya. Haga la física de bumpers y
slingshots en la mesa, en el golpe del contacto, y use el callback para los
efectos — la mesa sabe qué slingshot golpeó la bola y la máquina no.

### 3.3 Flippers

No los controla la CPU. Los botones llegan a las bobinas a través de la placa
de interconexión (J1-18 / J1-19), y el programa del juego ni siquiera los ve.
No hay contacto EOS ni contacto de botón de flipper en ninguna parte de la
matriz propia de esta máquina.

El núcleo de PinMAME sintetiza de todos modos los solenoides de flipper
estándar, desde su propia columna de flippers de mueble (columna interna de
switches 11). Bajo VPX — donde PinMAME no gestiona el teclado — esa columna es
la que la mesa debe accionar:

| Entrada | Número | Significado |
|---|---|---|
| switch | **112** | Botón del flipper inferior **derecho** |
| switch | **114** | Botón del flipper inferior **izquierdo** |

| Salida | Constante | Significado |
|---|---|---|
| 45 | `sLRFlipPow` | Flipper inferior derecho, bobinado de potencia |
| 46 | `sLRFlip` | Flipper inferior derecho, bobinado de retención |
| 47 | `sLLFlipPow` | Flipper inferior izquierdo, bobinado de potencia |
| 48 | `sLLFlip` | Flipper inferior izquierdo, bobinado de retención |

112 y 114 son los mismos números que usan las mesas WPC Fliptronic, porque la
numeración `column*10 + row + 1` del driver cae justamente en ellos para la
columna 11. Si prefiere no pasar los flippers por PinMAME en absoluto,
acciónelos directamente desde la mesa — al juego le da igual.

---

## 4. Display

La placa de display 53/3307 lleva **30 dígitos HDSP-3400** detrás de un Intel
8279, un selector de dígitos 74159 y dos decodificadores BCD-a-siete-segmentos
7447. No hay display de bola ni display de match: 4 jugadores × 7 dígitos + 2
dígitos de créditos = exactamente 30.

El 8279 tiene 16 direcciones de RAM de display y cada byte contiene **dos**
dígitos. El nibble alto va al 7447 que gobierna D15–D30, el bajo al que
gobierna D1–D14. Los dígitos son BCD en bruto; `0x0F` apaga un dígito.

En VPX se leen con `Controller.ChangedLEDs(&HFFFFFFFF, &HFFFFFFFF)` y se
indexan con los números de segmento («LED») de abajo. El driver refresca
`coreGlobals.segments` cada dos VBLANK.

### 4.1 Mapa de índices de segmento

| Jugador | Índices de segmento | Orden |
|---|---|---|
| Jugador 1 | 0–6 | `0` = millones … `6` = el cero final |
| Jugador 2 | 8–14 | `8` = millones … `14` = el cero final |
| Jugador 3 | 16–22 | `16` = millones … `22` = el cero final |
| Jugador 4 | 24–30 | `24` = millones … `30` = el cero final |
| Créditos | 32–33 | `32` = decenas, `33` = unidades |

Los índices 7, 15, 23 y 31 no están cableados; existen solo para mantener a
cada jugador en un límite de 8 índices.

**El dígito menos significativo de cada tanteo es un cero fijo al final** — el
premio más pequeño del tablero son 10 puntos. `0123450` en el display significa
123,450 puntos y el tanteo máximo mostrable es 9,999,990. *(Inferido de la
estructura de premios; el dígito es una posición real del 8279 y la ROM escribe
un 0 en él.)*

### 4.2 Dirección de RAM del 8279 → índice de segmento

Solo necesario si se está depurando el driver.

| Dir. 8279 | Nibble alto → | Nibble bajo → | Posición del dígito |
|---|---|---|---|
| 0 | 14 (J2) | 6 (J1) | menos significativo (0 final) |
| 1 | 30 (J4) | 22 (J3) | menos significativo (0 final) |
| 2 | 13 (J2) | 5 (J1) | decenas |
| 3 | 29 (J4) | 21 (J3) | decenas |
| 4 | 12 (J2) | 4 (J1) | centenas |
| 5 | 28 (J4) | 20 (J3) | centenas |
| 6 | 11 (J2) | 3 (J1) | millares |
| 7 | 27 (J4) | 19 (J3) | millares |
| 8 | 10 (J2) | 2 (J1) | decenas de millar |
| 9 | 26 (J4) | 18 (J3) | decenas de millar |
| 10 | 9 (J2) | 1 (J1) | centenas de millar |
| 11 | 25 (J4) | 17 (J3) | centenas de millar |
| 12 | 8 (J2) | 0 (J1) | millones |
| 13 | 24 (J4) | 16 (J3) | millones |
| 14 | 33 | — | unidades de créditos |
| 15 | 32 | — | decenas de créditos |

Los jugadores 1 y 3 toman el nibble bajo, los jugadores 2 y 4 el alto; los
jugadores 1–2 usan las direcciones de RAM pares, los 3–4 las impares. El juego
usa el comando de *inhibición de escritura de display* del 8279 (`0xA8` para
los jugadores impares, `0xA4` para los pares) para poder escribir de forma
independiente a los dos jugadores que comparten dirección, y su modo de
autoincremento para los rellenos del bloque de 16 bytes.

### 4.3 Disposición en pantalla que usa el driver

```
player 1 (0-6)                       player 3 (16-22)
player 2 (8-14)   credits (32-33)    player 4 (24-30)
```

---

## 5. Ajustes de operador, tests y auditorías

Se accede con los dos interruptores de la puerta (§1.6 — switches 1 y 2). El **botón
de partida (switch 28)** es el único control dentro de todos los menús.

### 5.1 AJUSTES DE TANTEO Y TEST DE CONTACTOS (ambos switches cerrados)

Nueve zonas en `supstarf1`. **El número de zona se muestra en el dígito de
unidades del display de créditos** (índice de segmento 33).

Procedimiento según el manual:

1. Apague la máquina.
2. Suba ambos interruptores de puerta y encienda — se aterriza en la zona 1
   con su valor actual.
3. Para pasar a otra zona: baje el interruptor de *ajuste* (abra el switch 1) y pulse
   partida; cada pulsación avanza una zona.
4. Para cambiar el valor de la zona actual: suba el interruptor de *ajuste*
   (cierre otra vez el switch 1) y pulse partida; cada pulsación incrementa el valor.

| Zona | Nombre en el manual | Descripción | Rango |
|---|---|---|---|
| 1 | NUMERO DE BOLAS POR PARTIDA | Bolas por partida | 1–5 |
| 2 | AJUSTE DE TANTEO BOLA EXTRA | Umbral de tanteo para la bola extra | 10,000–100,000 |
| 3 | NUMERO DE PARTIDAS POR MONEDA DE 25 PTAS. | Partidas por moneda de 25 pta | — |
| 4 | NUMERO DE PARTIDAS POR MONEDA DE 100 PTAS. | Partidas por moneda de 100 pta | — |
| 5 | NUMERO DE ESPECIALES POR TANTEO | Número de especiales por tanteo | 1–3 |
| 6 | TANTEO PRIMER ESPECIAL | Tanteo del primer especial | — |
| 7 | TANTEO SEGUNDO ESPECIAL | Tanteo del segundo especial | — |
| 8 | TANTEO TERCER ESPECIAL | Tanteo del tercer especial | — |
| 9 | TEST DE CONTACTOS | Test de contactos | véase abajo |

**Zona 9 — test de contactos.** El **extremo de las unidades del display del
jugador 1** muestra *cuántos* contactos hay cerrados en ese momento; el
**display del jugador 3** muestra *cuáles*, usando los números de contacto del
manual (1–29 de *CONTACTOS DE TABLERO*, no los números de switch de PinMAME).
Es la manera más rápida de validar el cableado de switches de una mesa: cierre
un contacto cada vez y compruebe que se informa exactamente de un contacto.

El test cubre solo los 23 contactos de tablero leídos por `0x4000` y la cadena
de 74165. Las cuatro entradas de mueble (25–28) no forman parte de él, y
tampoco los cuatro contactos cableados en paralelo con otro — cerrar cualquiera
de las dos mitades de un par informa del número más alto del par (véase el
apéndice).

### 5.1.1 Las diez zonas extra de `supstarf4`

El firmware más nuevo amplía el menú a **diecinueve** zonas: las nueve del
set 1 sin cambios, y después diez más mostradas como 10–19. (Su tabla de saltos
en `0x349D` tiene 25 entradas, de donde salió la cifra de «25 zonas» de notas
anteriores, pero el contador de zona en `C01D` es BCD y `0x33DD` avanza
`0x09 → 0x0A → 0x10`, así que las entradas 9–14 son inalcanzables y están
rellenas con la dirección del manejador de la zona 9.) También reserva `0x30`
bytes extra de NVRAM — su base de pila baja de `C7FF` a `C7CF` — y los ajustes
nuevos viven en `C7F1`–`C7FD`.

Nada de esto está en el manual, que describe el set 1. Todo lo de abajo se leyó
de la ROM y luego se comprobó en la máquina en marcha, ya fuera recorriendo el
menú (`tools/rfranco_zones.py`) o cambiando el ajuste y midiendo qué hacía el
juego de forma diferente.

| Zona | NVRAM | Rango mostrado | Por defecto | Qué cambia |
|---|---|---|---|---|
| 10 | `C7F1` | 0 / 1 | 1 | **Cobrar el especial IZQUIERDO resetea la bancada izquierda.** Con 1, golpear la *rampa especial izquierda* (switch 14) con la lámpara 52 encendida dispara BANCADA IZQUIERDA (solenoide 7) y apaga la lámpara 52, además de otorgar la partida gratis. Con 0 la lámpara sigue encendida y la bancada no se resetea. El set 1 no tiene equivalente — se comporta como 0. |
| 11 | `C7F2` | 0 / 1 | 1 | Lo mismo para el especial **DERECHO**: switch 16, lámpara 42, BANCADA DERECHA (solenoide 9). Medido en ambos sentidos — con 1 el reset de la bancada dispara y la lámpara 42 se apaga, con 0 solo el knocker y el crédito. |
| 12 | `C7F3` | 0 / 1 | 1 | **Cobrar el especial del PICABOLAS resetea la escalera de avance.** Con 1 cae de vuelta a 10 000, las lámparas de *avance doble/triple* se apagan y ESPECIAL PICABOLAS se extingue. Con 0 los tres sobreviven. |
| 13 | `C7F4` | 1–9 | 1 | **Máximo de bolas extra consecutivas en una misma bola en juego** — medido. La bola extra se ofrece cuando la escalera de avance entra en el peldaño guardado en `C1F9` (el umbral de bola extra de la zona 2, por defecto 6 = 60 000), no con cada *diana* completada: `0x0CBC` compara entonces `C7F4 - 1` con `C7F7`, las bolas extra ya cobradas en este turno, y el `RC` de `0x0CC4` abandona la oferta una vez que la cuenta ha alcanzado el límite. Medido en cada frontera forzando `C1F9`, la escalera y `C7F7` con el depurador y completando una *diana*: (`C7F4`,`C7F7`) = (1,0), (3,1) y (3,2) armaron una lámpara BOLA EXTRA DIANA, (1,1) y (3,3) se rechazaron con el contador de golpes posterior al `RC` sin moverse. La lectura de `C006` que le sigue *no* es una segunda puerta — su signo solo elige el lado, lámpara 53 (izquierda) o lámpara 43 (derecha); en cada pasada se armó una lámpara. Completar la bancada bajo la lámpara encendida la cobra — `C7F7` se incrementa en `0x0C4A`, LUZ BOLA EXTRA (lámpara 37) se enciende — y el drenaje repite entonces el mismo número de bola. No es por partida: `0x123D` pone `C7F7` a cero en cada fin de bola que no sea una repetición por bola extra (medido 3 → 0), así que con el valor por defecto de 1 el jugador puede ganar una bola extra en cada bola. |
| 14 | `C7F5` | 30000–90000 | 30000 | **Tanteo por completar una *diana*** (cualquiera de las dos bancadas). El set 1 otorga 30 000 fijos desde la misma instrucción. |
| 15 | `C7F6` | 100–9800 | 1000 | **Tanteo del pasillo de 100 PUNTOS** (switch 17). BCD × 100. El set 1 paga 100 por el mismo contacto, así que esta es la diferencia más visible entre los dos sets en el juego normal. |
| 16 | `C7F8` | 10–20 | 15 | **Máximo de créditos hasta el que una partida gratis puede llevar la máquina.** El set 1 lo tiene fijo en 20. El knocker golpea igualmente cuando el crédito se rechaza. La ruta de *moneda* tiene su propio límite separado de 10 y no consulta este. |
| 17 | `C7F9` | 0 / 1 | 1 | **Completar una diana enciende los bumpers.** Con 1, las lámparas 41 y 51 se encienden y cada bumper pasa a puntuar 10 000 en lugar de 1 000. Con 0 no se encienden. |
| 18 | `C7FA` | 0 / 1 | 1 | **Watchdog de contactos pegados.** Habilita la rutina en `0x3ABF` que pone la máquina en avería cuando el switch 11, 12, 18 o 47 se mantiene cerrado durante unas 128 pasadas consecutivas del bucle de juego, y las comprobaciones correspondientes en la ruta de recuperación de averías. Es el que parece una avería del display — véase §6.1. Desactívelo si una mesa tiene un contacto que no puede evitar mantener cerrado. |
| 19 | `C7FD` | 0 / 1 | 1 | **Cobro del bonus al final de la bola.** Con 1, cada drenaje — incluida la última bola — paga la escalera de avance: la puerta en `0x11E6` ejecuta la cuenta atrás en `0x0F70`/`0x0F9E`, el peldaño encendido baja hasta 10 000 y desaparece, y cada paso puntúa 10 000 (doblado o triplicado bajo *avance doble/triple*). Con 0 la llamada se omite y el valor de la escalera simplemente se pierde. Medido en ambos sentidos: +10 000 y +30 000 desde los peldaños correspondientes con 1, +0 con 0. En cualquier caso la siguiente bola vuelve a abrirse en el peldaño de 10 000 — ese reset pertenece a la ruta de servicio de la bola, no a esta zona. Véase `hardware-findings.md` §15.10. |

Dos de ellas cambian el juego tal como salía de fábrica y no solo cuando un
operador las mueve: la zona 15 hace que el pasillo de 100 puntos pague 1 000
donde el set 1 paga 100, y la zona 17 está activada por defecto, así que los
bumpers pasan a 10 000 tras la primera diana completada.

### 5.2 TEST DE LUCES Y VISUALIZACION DE RAM (switch 2 cerrado)

Encienda con el interruptor de *test* subido y la máquina entra directamente en
el test de luces: todas las bombillas de tablero y de frontón se encienden
alternativamente. Esto ejercita ambas fases de red, así que es una buena
comprobación de extremo a extremo de que una mesa tiene cableados los 44
números de lámpara utilizables.

Pulsar **partida** desde dentro del test de luces recorre las zonas de
visualización de RAM (auditorías). Cada zona muestra cuatro contadores, uno por
display de jugador.

**ZONA 1**

| Display | Nombre en el manual | Descripción |
|---|---|---|
| Jugador 1 | TOTAL PARTIDAS | Total de partidas jugadas |
| Jugador 2 | TOTAL ESPECIALES PRIMER TANTEO | Especiales otorgados en el umbral 1 |
| Jugador 3 | TOTAL ESPECIALES SEGUNDO TANTEO | Especiales otorgados en el umbral 2 |
| Jugador 4 | TOTAL ESPECIAL TERCER TANTEO | Especiales otorgados en el umbral 3 |

**ZONA 2**

| Display | Nombre en el manual | Descripción |
|---|---|---|
| Jugador 1 | TOTAL ESPECIAL POR LOTERIA | Especiales otorgados por la lotería |
| Jugador 2 | TOTAL ESPECIALES POR PICABOLAS | Especiales otorgados por el picabolas |
| Jugador 3 | TOTAL ESPECIALES POR RAMPAS | Especiales otorgados por las rampas |
| Jugador 4 | TOTAL BOLAS EXTRAS | Bolas extra otorgadas |

**ZONA 3**

| Display | Nombre en el manual | Descripción |
|---|---|---|
| Jugador 1 | TOTAL MONEDAS DE 25 PTS. | Monedas de 25 pta aceptadas |
| Jugador 2 | TOTAL MONEDAS DE 100 PTS. | Monedas de 100 pta aceptadas |
| Jugador 3 | TOTAL PARTIDAS GRATIS MONEDAS DE 25 PTS. | Partidas gratis por el monedero de 25 pta |
| Jugador 4 | TOTAL PARTIDAS GRATIS MONEDAS DE 100 PTS. | Partidas gratis por el monedero de 100 pta |

### 5.3 BORRADO DE DISPLAY Y CREDITOS (switch 1 cerrado)

Encender en esta posición borra todos los créditos almacenados.

---

## 6. Primeros pasos

### 6.1 Las dos cosas que matarán la mesa

**(1) El switch 27 (*caída de bolas*) debe leerse CERRADO siempre que haya una
bola en el foso — que es el estado de reposo, incluido el encendido.**

Dos rutas distintas lo consultan, y fallan de forma diferente — conviene
separarlas, porque solo una de ellas es fatal:

* **Servir una bola.** Empiece una partida con el foso abierto y la máquina
  toma el crédito, arranca la partida y luego, simplemente, **nunca dispara
  SALIDA BOLAS**. Sin bola, sin avería, sin mensaje de error — espera. Medido
  durante 45 s: `C01C = 0x00` todo el tiempo, el kicker nunca disparado, y
  cerrar el switch 27 dejó continuar el juego con normalidad. Este es el
  comportamiento propio de la máquina ante la falta de bola y es benigno.
* **Recuperación de averías.** Tras una avería (falta, o el watchdog de
  contactos pegados del set 2) la ruta de recuperación en `0x030F` necesita el
  foso cerrado para soltar. Si se deja abierto, hace ping-pong con `0x0331`
  para siempre: los manejadores de interrupción siguen ejecutándose, así que la
  máquina *parece* viva — el refresco del display en marcha, el handshake de
  sonido completándose, las lámparas del attract con sentido — mientras el
  programa en primer plano está muerto y nada de lo que se haga tiene efecto.
  **Esta es la que matará la mesa.**

También debe **abrirse** una vez servida la bola, o el juego termina cada bola
en el instante en que la inicia. El modelo correcto es un foso de dos estados:

* cerrado al encender, y siempre que una bola esté posada en la caída;
* abierto cuando dispara el solenoide **10** (SALIDA BOLAS);
* cerrado de nuevo cuando la bola drena.

El driver contiene exactamente ese modelo, y **que se ejecute o no es una
elección de la mesa**, mediante el flag estándar de mecánica de PinMAME:

| `Controller.HandleMechanics` | Quién gobierna el switch 27 |
|---|---|
| `&HFF` (el valor por defecto de VPinMAME) | El driver siembra el contacto **cerrado** en el reset (`rfranco.c:1023`, escrito en la matriz por el manejador de switches en `rfranco.c:913`) y lo abre cuando dispara SALIDA BOLAS; **la mesa debe cerrarlo al drenar.** Cerrarlo también al encender es inocuo, no necesario — el driver ya lo ha hecho. |
| `0` | Nadie más que la mesa. El driver nunca toca el contacto — la física de bolas de la mesa lo gobierna de principio a fin, encendido incluido. |

Fíjese hacia qué lado cae el valor por defecto: VPinMAME pone el flag a `&HFF`
salvo que la mesa lo cambie (`src/win32com/Controller.cpp:186`, copiado al
global en `ControllerRun.cpp:102`), así que de serie PinMAME es el dueño de la
mecánica. libpinmame es el que arranca por defecto en `0`
(`src/libpinmame/libpinmame.cpp:31`); la compilación independiente coincide con
VPinMAME (`src/wpc/core.c:90`).

La posición de la bola es una propiedad mecánica, así que el driver la trata
como core.c trata cualquier otro mecanismo: condicionada a
`g_fHandleMechanics`. Ponga `Controller.HandleMechanics = 0` en `Table1_Init`
si quiere que la lógica de foso de la mesa sea lo único que escriba ese bit;
déjelo como está y el driver siembra el contacto cerrado en el reset y hace por
la mesa la mitad de la apertura. En cualquier caso, ciérrelo al drenar: la ruta
de drenaje propia del driver es la tecla DRAIN del teclado, y VPinMAME borra
`g_fHandleKeyboard` (`Controller.cpp:185`), así que `core.c:1780` no entrega al
manejador de switches ningún puerto de entrada.

*Medido con el flag desactivado:* el contacto no se toca al encender, y un
front end que gobierna el switch 27 por su cuenta obtiene una partida
completamente normal — moneda, partida, kicker, tanteo, drenaje. Ambas rutas
están cubiertas por un arnés: `tools/rfranco_mech.py` hace el papel del front
end a través de la API de depuración (la compilación independiente expone el
flag en `/api/mechanics`) y comprueba que el driver no toca el switch 27.

Una mesa que deja el flag en su valor por defecto lo conecta así:

```vbscript
Sub Table1_Init
    Controller.Switch(27) = True    ' a ball rests in the outhole. Harmless at
                                    ' the default - the driver already closed it
                                    ' at reset - and required if you ever set
                                    ' HandleMechanics = 0
End Sub

Sub SolBallRelease(enabled)
    If enabled Then
        Controller.Switch(27) = False   ' trough is now empty
        ' ...kick the ball into the shooter lane
    End If
End Sub

Sub Drain_Hit
    Controller.Switch(27) = True
End Sub
```

**(2) Los contactos de monedero deben recibir pulsos, no mantenerse cerrados.**

La rutina de moneda registra la moneda y luego espera a que el contacto se
**abra** en un plazo de 20 semiciclos de red (≈200 ms). Si sigue cerrado, cae
al manejador de averías, que bloquea la máquina de forma permanente — ningún
reset que no sea reiniciar la emulación la recupera.

```vbscript
Sub AddCoin25
    Controller.Switch(25) = True
    vpmTimer.AddTimer 60, "Controller.Switch(25) = False'"   ' well under 200 ms
End Sub
```

El driver convierte una *tecla* de moneda en un monoestable, pero una mesa que
escribe el switch directamente está por su cuenta — el driver, a propósito, no
toca un switch que no esté cambiando en ese momento (véase abajo), así que no
le acortará el pulso.

**(3) Solo en `supstarf4`: no deje cerrado el switch 11, 12, 18 o 47.**

El set 2 tiene un watchdog de contactos pegados que el set 1 no tiene. Un
contacto mantenido cerrado durante unas 128 pasadas consecutivas del bucle de
juego — medido en ~27 s desde una NVRAM fría y ~7 s con sus contadores ya
calientes — salta al manejador de averías, que deja los treinta dígitos con el
patrón del 7447 para 14. Parece exactamente un fallo del display y no lo es:
**lea `C01C` antes de sospechar del display; `0xFF` significa que la ROM entró
en avería.** La zona 18 de operador desactiva el watchdog (§5.1.1).

**(4) Una bola que no ha puntuado no se cuenta.**

Cierre el foso con una bola que no ha puntuado nada desde que se sirvió y el
juego no avanza el número de bola — simplemente vuelve a servir la misma bola,
y lo seguirá haciendo indefinidamente. Puntúe una vez y el siguiente drenaje
avanza con normalidad. Medido: dos drenajes consecutivos de una bola sin tocar
dejaron el número de bola donde estaba, y un único contacto de 10 puntos entre
el segundo y el tercero hizo que el tercero avanzara.

Es una regla propia de la máquina y es sensata — es lo que evita que se pierda
una bola que nunca salió del carril de lanzamiento — pero parecerá un drenaje
roto si la mesa puede devolver la bola al foso sin tocar nada.

### 6.1.1 El driver no peleará por un switch

Nada en `SWITCH_UPDATE` escribe un bit de la fila de mueble salvo que ese bit
esté cambiando del lado del propio driver — una tecla del teclado moviéndose, o
un monoestable de moneda arrancando o expirando. No reconstruye la fila en cada
fotograma. Así que un switch que la mesa activa permanece activo hasta que la
mesa lo borra, que es lo que se quiere, y es lo que hace que la secuencia
moneda/partida funcione con fiabilidad desde fuera del teclado.

El switch 27 es el único sitio donde el driver escribe un bit por iniciativa
propia y no en respuesta a una entrada, y eso es lo que desactiva
`Controller.HandleMechanics = 0` — véase §6.1. Con el flag a `0` el driver no
escribe en esa fila nada que no se le haya pedido.

### 6.2 El mínimo absoluto para echar una partida

| Elemento | Número | Por qué |
|---|---|---|
| Caída de bola / foso | switch **27** | Cerrado en reposo. Abierto, la máquina no servirá bola, y no puede recuperarse de una avería — §6.1 |
| Monedero de 25 pta | switch **25** | Una de las dos únicas vías hacia un crédito; púlselo |
| Monedero de 100 pta | switch **26** | Ídem |
| Botón de partida | switch **28** | Inicia la partida *y* maneja todos los menús de operador |
| Expulsión de bola | solenoide **10** (SALIDA BOLAS) | Sirve la bola. Además vacía el foso automáticamente, salvo que se ponga `HandleMechanics = 0` — §6.1 |

Además:

* **El switch 48 no es un contacto** — es una entrada flotante del registro de
  desplazamiento que el driver enmascara. Escribirlo no hace nada; déjelo
  abierto.
* La ROM nunca lee los switches 21–24, y por eso el driver toma prestados
  tres: el 21 es la *falta* (§1.5), el 23 y el 24 son los interruptores de
  puerta del operador (§5.1). El 22 no hace nada.
* **No busque un display de bola en juego** — use las lámparas 31–35
  (*BOLA 1*–*BOLA 5*).
* **El solenoide 2 dispara en cada *especial*.** Que la bobina que cuelga de él
  sea el knocker es lo único en que el manual y la ROM discrepan — §3.1.
* El solenoide 1 y el solenoide 6 no disparan nunca. Es correcto, no es un
  fallo.
* **Asocie la lámpara 11 para la falta, no la lámpara 1** (§2.9).

### 6.3 Primer arranque: la NVRAM empieza a cero

El driver usa `MDRV_NVRAM_HANDLER(generic_0fill)`, así que una instalación
nueva arranca con 2 KB de ceros en `0xC000`–`0xC7FF`.

La ruta de reset comprueba en `C000` el byte mágico `0x55` y, si falla,
ejecuta `RST 0` — que aterriza de nuevo en el vector de reset. Nada en ese
bucle escribe el byte mágico. Es el **manejador de TRAP** (la interrupción de
paso por cero de la red) el que detecta el byte mágico incorrecto, siembra
`C000` con `0x55` y resetea. Así que el primer encendido tarda un momento y
luego arranca con **todos los ajustes a cero**.

**Consecuencia práctica: cero partidas por moneda. La máquina parecerá tragarse
las monedas sin dar crédito.** Antes de publicar una mesa, o en el primer
arranque propio:

1. Cierre los switches 1 y 2 (ambos interruptores de puerta subidos) y resetee.
2. Se aterriza en la zona 1 (bolas por partida). Ambos cerrados + partida cambia
   el valor; abrir el switch 1 + partida avanza a la zona siguiente.
3. Recorra las zonas 1–8 y dé a cada una un valor razonable — en particular a
   la **zona 3** y a la **zona 4** (partidas por moneda).
4. Opcionalmente, use la zona 9 para verificar cada switch que la mesa acciona.
5. Abra otra vez los switches 1 y 2 y resetee.

Los valores persisten desde entonces en el archivo `.nv`. Distribuir la mesa
con un `.nv` ya ajustado es la opción más amable.

### 6.4 Esquema de conexión

```vbscript
' ---- solenoids -------------------------------------------------
SolCallback(2)  = "SolKnocker"          ' especial awarded - see 3.1
SolCallback(3)  = "SolCoinLockout"
SolCallback(4)  = "SolCoinMeter25"
SolCallback(5)  = "SolCoinMeter100"
SolCallback(7)  = "SolResetLeftBank"    ' BANCADA IZQUIERDA
SolCallback(8)  = "SolPicabolas"
SolCallback(9)  = "SolResetRightBank"   ' BANCADA DERECHA
SolCallback(10) = "SolBallRelease"      ' SALIDA BOLAS - opens switch 27 for you
                                        ' unless HandleMechanics = 0 (see 6.1)
SolCallback(17) = "SndLeftBumper"       ' synthesised from switch 18
SolCallback(18) = "SndRightBumper"      ' synthesised from switch 12
SolCallback(19) = "SndLeftSling"        ' synthesised from switch 11 ...
SolCallback(20) = "SndRightSling"       ' ... and so is this one: same contact
SolCallback(45) = "SolRFlipper"         ' synthesised by the PinMAME core
SolCallback(47) = "SolLFlipper"
' 1 and 6 are never asserted - do not bind them

' ---- flipper buttons (PinMAME's own cabinet column, not the game matrix) ----
' Controller.Switch(112) = right button, Controller.Switch(114) = left button

' ---- switches --------------------------------------------------
Sub Table1_Init
    ' Uncomment to own the trough outright - the driver then never touches
    ' switch 27 and your ball physics are the only writer. See 6.1.
    ' Controller.HandleMechanics = 0
    Controller.Switch(27) = True        ' ball in the trough: MUST be closed
End Sub

' tilt: hold switch 21 closed for as long as the pendulum is swinging
Sub Tilt_Hit  : Controller.Switch(21) = True  : End Sub
Sub Tilt_UnHit: Controller.Switch(21) = False : End Sub

' bumpers and slingshots: solenoids 17-20 are for effects only, do the physics here
Sub LeftBumper_Hit
    vpmTimer.PulseSw 18                 ' scoring contact
    ' ...and kick the ball with your own mechanics
End Sub

' drop targets: close the individual switch AND pulse the bank contact
Sub LeftTarget1_Hit
    Controller.Switch(33) = True        ' stays closed while the target is down
    vpmTimer.PulseSw 13                 ' DIANA IZQUIERDA, bank-level contact
End Sub
```

---

## Apéndice — números de contacto del manual ↔ números de switch de PinMAME

La zona 9 informa con la numeración del manual. Use esta tabla para traducir.

| Contacto del manual | Switch de PinMAME |
|---|---|
| 1 PASILLO SUPERIOR IZQUIERDO | 46 |
| 2 PASILLO SUPERIOR DERECHO | 45 |
| 3 RAMPA ESPECIAL IZQUIERDA | 14 (pasillo exterior superior izquierdo, un rollover) |
| 4 BUMPER IZQUIERDO | 18 |
| 5 PICABOLAS | 47 |
| 6 BUMPER DERECHO | 12 |
| 7 RAMPA ESPECIAL DERECHA | 16 (pasillo exterior superior derecho, un rollover) |
| 8 DIANA IZQUIERDA (bancada) | 13 |
| 9 DIANA DERECHA (bancada) | 15 |
| 10 100 PUNTOS | 17 (en paralelo con el 21; se informa como 21) |
| 11 DIANA 1 IZQUIERDA | 33 |
| 12 DIANA 2 IZQUIERDA | 35 |
| 13 DIANA 3 IZQUIERDA | 34 |
| 14 DIANA 4 IZQUIERDA | 36 |
| 15 DIANA 5 IZQUIERDA | 37 |
| 16 DIANA 1 DERECHA | 44 |
| 17 DIANA 2 DERECHA | 43 |
| 18 DIANA 3 DERECHA | 42 |
| 19 DIANA 4 DERECHA | 41 |
| 20 DIANA 5 DERECHA | 38 |
| 21 100 PUNTOS | 17 (en paralelo con el 10) |
| 22 PASILLO INFERIOR IZQUIERDO | 32 (en paralelo con el 26; se informa como 26) |
| 23 PASILLO INFERIOR DERECHO | 31 (en paralelo con el 27; se informa como 27) |
| 24 10 PUNTOS | 11 (slingshot izquierdo; en paralelo con el 25, se informa como 25) |
| 25 10 PUNTOS | 11 (slingshot derecho; en paralelo con el 24) |
| 26 PASILLO INFERIOR IZQUIERDO | 32 (en paralelo con el 22) |
| 27 PASILLO INFERIOR DERECHO | 31 (en paralelo con el 23) |
| 28 CAIDA DE BOLA | 27 (no cubierto por la zona 9) |
| 29 PULSADOR PARTIDA | 28 (no cubierto por la zona 9) |
| — FALTA | ninguno — RST 6.5, véase §1.5 |

Nótese la colisión de nombres: el contacto 27 del manual es *pasillo inferior
derecho*, y el switch 27 de PinMAME es *caída de bolas*. Son cosas distintas.

La tabla de la ROM guarda los contactos 21, 25, 26 y 27 con el bit 7 activado,
que es como marca los cuatro pares en paralelo; ese flag es el motivo de que
los contactos 10, 22, 23 y 24 nunca aparezcan solos en el test.

---

## Documentos relacionados

* `vpx-table-reference.md` — la versión inglesa (de referencia) de este documento.

* `driver-notes.md` — para revisores de PinMAME: arquitectura, las correcciones
  del núcleo 8085, carencias conocidas del driver.
* `hardware-findings.md` — el análisis de hardware completo y su pista de
  auditoría.
* `pinmame-keyboard-reference.md` — los mismos switches desde el otro extremo:
  qué tecla cierra qué contacto en PinMAME independiente, y cómo llegar al test
  de contactos de la zona 9 de la propia ROM.
* `sound-rom-map.md` — la ROM de sonido mapeada byte a byte, con el formato de
  las melodías y todos los comandos de sonido.
* `questions-for-a-real-machine.md` — lo que sigue sin resolver, y qué
  preguntar a alguien con una máquina física.
* `rom-provenance.md` — ROM sets, hashes y el caso BAD_DUMP de `supstarfa`.
