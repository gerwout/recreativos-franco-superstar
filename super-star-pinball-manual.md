# MANUAL — SUPER STAR

**Recreativos Franco, S.A.**
Alfonso Gómez, 4 — telf. 754 30 39 / 754 30 65 — 28037 Madrid

![Portada](manual-images/page-01.jpg)

---

> **About this file** — This is a transcription of the scanned Recreativos Franco
> "Super Star" pinball manual (`super-star-pinball-manual.pdf`, 61 scanned pages).
> All text has been transcribed from the page images; schematics, PCB layouts and
> exploded parts drawings cannot be represented as text and are linked as images
> from `manual-images/`.
>
> Headings are given as **PDF page N** (the page in the scan) followed by the
> printed manual page number where the original shows one. The scan is not in
> strict page order and contains two duplicated sheets — this is noted where it
> occurs.
>
> Uncertain readings on faint scans are marked with `[?]`.

---

## FE DE ERRATAS

*(PDF page 2)*

- **Pág. 15.** — Conector JA al revés. Quedando ahora JA1 Ma ..... JA 25 Gr.
- **Pág. 16.** — La lectura del contacto de picabolas pasa al conector JN2, quedando el JM3 N.U.
- **Pág. 17.** — La luz de falta sale por el pin 3 del IC1. El pin de salida del conector es el JA8.
- **Pág. 18.** — El pin 10 del IC5 sale por el JN1. El pin 11 del IC5 sale por el JN2 y corresponde al picabolas.
- **Pág. 21.** — Conector JA:

  | AHORA | | ANTES | |
  |---|---|---|---|
  | Ma 1 | Fase A | Vi 1 | GND |
  | Ma 2 | Fase A | Vi 2 | GND |
  | Vi 3 | GND | Ma 3 | Fase A |
  | Vi 4 | GND | Ma 4 | Fase A |

- **Pág. 25 y 26.** — Falta la pieza 01-2339 (Pantallas Luces Loteria).

![Fe de erratas](manual-images/page-02.jpg)

---

## ÍNDICE

*(PDF page 3)*

| Concepto | Página |
|---|---|
| INSTRUCCIONES | 1 |
| LUCES DE TABLERO | 2 |
| CONTACTOS DE TABLERO | 3 |
| SITUACION DE PLACAS Y CONECTORES | 4 |
| PLACA C. P. U. | 5 |
| FUENTE ALIMENTACION | 9 |
| DRIVER | 13 |
| DISPLAYS | 19 |
| CONEXION INTERMEDIA | 22 |
| CONTROL BUMPER Y EXPULSOR | 23 |
| REGULACION PIRULOS | 24 |
| MUEBLE | 25 |
| TABLERO DE JUEGO | 27 |
| PLASTICOS Y EMBELLECEDORES DE TABLERO | 29 |
| PUERTA | 31 |
| SALIDA DE BOLAS | 33 |
| FLIPPER | 35 |
| RECHAZADOR | 37 |
| BUMPER | 39 |
| PICABOLAS | 41 |
| CIERRE | 43 |
| LANZADOR | 45 |
| FALTA Y TACA | 47 |
| DIANAS ABATIBLES | 49 |
| ACCESORIOS DE TABLERO Y MUEBLE | 51 |

![Índice](manual-images/page-03.jpg)

---

# INSTRUCCIONES PARA AJUSTES, TEST Y VISUALIZACION DE RAM

*(PDF pages 4–5 — manual page 1 and following)*

Para realizar los ajustes, la máquina va provista de dos interruptores en la puerta,
los cuales realizan éstas funciones:

1. Los dos hacia arriba → **AJUSTES DE TANTEO Y TEST DE CONTACTOS**
2. Interruptor de test hacia arriba → **TEST DE LUCES Y VISUALIZACION DE RAM**
3. Los dos hacia abajo → **JUEGO**
4. Interruptor de ajuste hacia arriba → **BORRADO DE DISPLAY Y CREDITOS**

## 1.- AJUSTES DE TANTEO Y TEST DE CONTACTOS

Los ajustes están divididos en 9 zonas (el número de zona se visualiza en las
unidades del display de créditos) y son:

| Zona | Función |
|---|---|
| ZONA 1 | NUMERO DE BOLAS POR PARTIDA, DE 1 A 5 BOLAS |
| ZONA 2 | AJUSTE DE TANTEO BOLA EXTRA, DE 10.000 PTOS. A 100.000 PTOS. |
| ZONA 3 | NUMERO DE PARTIDAS POR MONEDA DE 25 PTAS. |
| ZONA 4 | NUMERO DE PARTIDAS POR MONEDA DE 100 PTAS. |
| ZONA 5 | NUMERO DE ESPECIALES POR TANTEO, DE 1 A 3 ESPECIALES |
| ZONA 6 | TANTEO PRIMER ESPECIAL |
| ZONA 7 | TANTEO SEGUNDO ESPECIAL |
| ZONA 8 | TANTEO TERCER ESPECIAL |
| ZONA 9 | TEST DE CONTACTOS |

Los pasos a seguir para entrar y modificar en las zonas son:

1. Apagar la máquina.
2. Poner los dos interruptores hacia arriba y conectar la máquina. (En éste momento
   entrará la zona 1 con su ajuste anterior).
3. Para pasar a cualquier zona, bajar el interruptor de ajuste y dando el pulsador
   de juegue pasará a la zona deseada.
4. Para realizar la modificación del tanteo, subir el interruptor de ajuste y
   pulsando el botón de juegue, variará el tanteo.

### TEST DE CONTACTOS (Zona 9)

Para entrar en esta zona se realizarán las mismas operaciones. Lo que nos indica el
display de unidades primer jugador es el número de contactos cerrados. El display del
tercer jugador, qué contactos son. (A cada contacto le corresponde un número, ver pág. 3.)

![Instrucciones 1](manual-images/page-04.jpg)

## 2.- TEST DE LUCES Y VISUALIZACION DE RAM

**Test de luces.** — Se comprueban todas la bombillas encendiéndose alternativamente
todas las luces del tablero y del frontal de la máquina.

Pasos a seguir para entrar en el test de luces:

1. Apagar la máquina.
2. Poner el interruptor de test hacia arriba.
3. Conectar la máquina (entrará directamente en el test de luces).

**Visualización de RAM.** — Estando dentro del test de luces, pulsar el botón de
Juegue y pasaremos a la zona deseada.

### ZONA 1

| Display | Contenido |
|---|---|
| 1er jugador | TOTAL PARTIDAS |
| 2º jugador | TOTAL ESPECIALES PRIMER TANTEO |
| 3er jugador | TOTAL ESPECIALES SEGUNDO TANTEO |
| 4º jugador | TOTAL ESPECIAL TERCER TANTEO |

### ZONA 2

| Display | Contenido |
|---|---|
| 1er jugador | TOTAL ESPECIAL POR LOTERIA |
| 2º jugador | TOTAL ESPECIALES POR PICABOLAS |
| 3er jugador | TOTAL ESPECIALES POR RAMPAS |
| 4º jugador | TOTAL BOLAS EXTRAS |

### ZONA 3

| Display | Contenido |
|---|---|
| 1er jugador | TOTAL MONEDAS DE 25 PTS. |
| 2º jugador | TOTAL MONEDAS DE 100 PTS. |
| 3er jugador | TOTAL PARTIDAS GRATIS MONEDAS DE 25 PTS. |
| 4º jugador | TOTAL PARTIDAS GRATIS MONEDAS DE 100 PTS. |

## 4.- BORRADO DISPLAY Y CREDITOS

En esta posición al conectar la máquina se borrarán todos los créditos almacenados.

![Instrucciones 2](manual-images/page-05.jpg)

---

# LUCES DE TABLERO

*(PDF page 6 — manual page 2)*

| # | Luz |
|---|---|
| 1 | PASILLO IZQUIERDO |
| 2 | PASILLO DERECHO |
| 3 | ESPECIAL PICABOLAS |
| 4 | BUMPER IZQUIERDO |
| 5 | BUMPER DERECHO |
| 6 | ESPECIAL IZQUIERDO |
| 7 | BOLA EXTRA, DIANA IZQUIERDA |
| 8 | BOLA EXTRA, DIANA DERECHA |
| 9 | ESPECIAL DERECHO |
| 10 | AVANCE 100.000 PUNTOS |
| 11 | AVANCE 90.000 PUNTOS |
| 12 | AVANCE 80.000 PUNTOS |
| 13 | AVANCE 70.000 PUNTOS |
| 14 | AVANCE 60.000 PUNTOS |
| 15 | AVANCE 50.000 PUNTOS |
| 16 | AVANCE 40.000 PUNTOS |
| 17 | AVANCE 30.000 PUNTOS |
| 18 | AVANCE 20.000 PUNTOS |
| 19 | AVANCE 10.000 PUNTOS |
| 20 | DOBLE AVANCE |
| 21 | TRIPLE AVANCE |
| 22 | PASILLO IZQUIERDO |
| 23 | PASILLO DERECHO |
| 24 | PASILLO IZQUIERDO |
| 25 | PASILLO DERECHO |
| 26 | BOLA EXTRA (CONSEGUIDA) |
| 27 | BOLA 1 |
| 28 | BOLA 2 |
| 29 | BOLA 3 |
| 30 | BOLA 4 |
| 31 | BOLA 5 |
| 32 | FINAL PARTIDA |
| 33 | PULSADOR PARTIDAS |

![Luces de tablero](manual-images/page-06.jpg)

---

# CONTACTOS DE TABLERO

*(PDF page 7 — manual page 3)*

| # | Contacto |
|---|---|
| 1 | PASILLO SUPERIOR IZQUIERDO |
| 2 | PASILLO SUPERIOR DERECHO |
| 3 | RAMPA ESPECIAL IZQUIERDA |
| 4 | BUMPER IZQUIERDO |
| 5 | PICABOLAS |
| 6 | BUMPER DERECHO |
| 7 | RAMPA ESPECIAL DERECHA |
| 8 | DIANA IZQUIERDA |
| 9 | DIANA DERECHA |
| 10 | 100 PUNTOS |
| 11 | DIANA 1 IZQUIERDA |
| 12 | DIANA 2 IZQUIERDA |
| 13 | DIANA 3 IZQUIERDA |
| 14 | DIANA 4 IZQUIERDA |
| 15 | DIANA 5 IZQUIERDA |
| 16 | DIANA 1 DERECHA |
| 17 | DIANA 2 DERECHA |
| 18 | DIANA 3 DERECHA |
| 19 | DIANA 4 DERECHA |
| 20 | DIANA 5 DERECHA |
| 21 | 100 PUNTOS |
| 22 | PASILLO INFERIOR IZQUIERDO |
| 23 | PASILLO INFERIOR DERECHO |
| 24 | 10 PUNTOS |
| 25 | 10 PUNTOS |
| 26 | PASILLO INFERIOR IZQUIERDO |
| 27 | PASILLO INFERIOR DERECHO |
| 28 | CAIDA DE BOLA |
| 29 | PULSADOR PARTIDA |

![Contactos de tablero](manual-images/page-07.jpg)

---

# SITUACION DE PLACAS Y CONECTORES

*(PDF page 8 — manual page 4)*

Block diagram of the four boards and their interconnection:

| Board | Ref. | Connectors |
|---|---|---|
| F.A. (Fuente de Alimentación) | 53/3309 | JA 1–21 (entradas alimentación), JB 1–23, JC 1–7 (salidas alimentación) |
| C.P.U. | 53/3291 | JA 1–22, JB 1–8, JC 1–8, JD 1–13, JE 1–6, JF 1–16, JG 1–8, I1 (switches regulación tanteo) |
| DRIVER | 53/3308 | JA 1–25, JB 1–8, JC 1–8, JD 1–13, JE 1–6, JF 1–16, JG 1–21, JH 1–11, JK 1–6, JL 1–10, JM 1–10, JN 1–9, JO 1–5, JP 1–10, JQ 1–20 |
| DISPLAYS | 53/3307 | JA 1–25 |

Signal groupings marked on the drawing:

- **F.A. → C.P.U./DRIVER:** salidas alimentación, entradas alimentación
- **C.P.U. → DRIVER:** contactos tablero de juego
- **DRIVER JH/JK:** alimentaciones tablero de juego
- **DRIVER JL:** bobinas
- **DRIVER JM:** contactos tablero de juego / sonido altavoz
- **DRIVER JN:** contactos tablero de juego
- **DRIVER JO:** contactos mueble
- **DRIVER JP, JQ:** luces tablero juego
- **DRIVER JA → DISPLAYS JA:** control display, luces frontal y alimentaciones

![Situación de placas y conectores](manual-images/page-08.jpg)

---

# PLACA C.P.U. — Ref. 53/3291

## RELACION COMPONENTES C.P.U. SUPER STAR — Ref: 53/3291

*(PDF page 9 — manual page 5)*

### RESISTENCIAS

| Ref. | Valor | Ref. | Valor | Ref. | Valor | Ref. | Valor |
|---|---|---|---|---|---|---|---|
| R1 | N.U. | R16 | N.U. | R31 | 33K | R46 | 10K |
| R2 | N.U. | R17 | 4K7 | R32 | 33K | R47 | 10K |
| R3 | N.U. | R18 | 1K | R33 | 1K | R48 | 10K |
| R4 | PUENTE | R19 | 220 Ω | R34 | 470 Ω | R49 | 10K |
| R5 | PUENTE | R20 | 1K | R35 | 1 Ω | R50 | 10K |
| R6 | N.U. | R21 | 68K | R36 | 10K | R51 | 10K |
| R7 | N.U. | R22 | 4K7 | R37 | 1K8 | R52 | 10K |
| R8 | N.U. | R23 | 220K | R38 | 2M2 | R53 | 10K |
| R9 | N.U. | R24 | N.U. | R39 | 1K | | |
| R10 | N.U. | R25 | N.U. | R40 | 10K | | |
| R11 | N.U. | R26 | N.U. | R41 | 2'7 Ω | | |
| R12 | PUENTE | R27 | N.U. | R42 | 47 Ω | | |
| R13 | N.U. | R28 | N.U. | R43 | 2M2 | | |
| R14 | N.U. | R29 | 68K | R44 | 100K | | |
| R15 | 22K | R30 | 3K3 | R45 | 220 Ω | | |

> **NOTA.** — Todas las resistencias son de 1/4 W excepto R42 que es 2W.

### CONDENSADOR

| Ref. | Valor | Ref. | Valor | Ref. | Valor |
|---|---|---|---|---|---|
| C1 | N.U. | C16 | 10 µF 35V | C31 | 10 µF 15V |
| C2 | N.U. | C17 | 15 pF | C32 | 10 µF 15V |
| C3 | N.U. | C18 | 220 nF 16V | C33 | 10 µF 15V |
| C4 | 1 µF 35V | C19 | 6'8 µF 35V | C34 | 10 µF 15V |
| C5 | 10 nF | C20 | 100 nF 16V | C35 | 10 µF 15V |
| C6 | 22 pF | C21 | 1 nF 16V | C36 | 10 µF 15V |
| C7 | 100 nF 16V | C22 | 1 nF 16V | | |
| C8 | N.U. | C23 | 2'2 µF 35V | | |
| C9 | 1 nF 16V | C24 | 47 µF 16V | | |
| C10 | 22 pF 16V | C25 | 100 nF 10V | | |
| C11 | N.U. | C26 | 1000 µF 16V | | |
| C12 | 220 nF 16V | C27 | 10 nF 16V | | |
| C13 | N.U. | C28 | 330 µF 25V | | |
| C14 | N.U. | C29 | 10 µF 15V | | |
| C15 | N.U. | C30 | 10 µF 15V | | |

22-CD — 100 nF 16V

### CIRCUITOS

| Ref. | Tipo | Ref. | Tipo |
|---|---|---|---|
| IC1 | 8212 | IC16 | 74HC00 |
| IC2 | AY8910 | IC17 | 7400 |
| IC3 | AY8910 | IC18 | 7402 |
| IC4 | 2532 | IC19 | 27128 |
| IC5 | 8212 | IC20 | LM380 |
| IC6 | 8212 | | |
| IC7 | 8035 | | |
| IC8 | 74LS138 | | |
| IC9 | 8085 | | |
| IC10 | 8212 | | |
| IC11 | 5517 | | |
| IC12 | 74HC74 | | |
| IC13 | 74LS138 | | |
| IC14 | N.U. | | |
| IC15 | 7438 | | |

### DIODOS

| Ref. | Tipo | Ref. | Tipo |
|---|---|---|---|
| D1 | N.U. | D13 | 1N4007 |
| D2 | N.U. | D14 | 1N4007 |
| D3 | N.U. | D15 | 1N4148 |
| D4 | N.U. | D16 | 1N4148 |
| D5 | PUENTE | D17 | 1N4148 |
| D6 | OA95 | D18 | 1N4148 |
| D7 | OA95 | D19 | 1N4148 |
| D8 | N.U. | D20 | 1N4148 |
| D9 | 1N4148 | D21 | 1N4007 |
| D10 | N.U. | D22 | 1N4007 |
| D11 | 1N4148 | | |
| D12 | 1N4148 | | |

### VARIOS

- **X1** = 5,0688 MHz (impreso «50688 MHZ»)
- **N1** = Lámpara neón
- **I1** = Switch de 8 posiciones
- **AC1** = Acumulador 4,8 V
- **JD** = Conector MOLEX 2,54 — 13 pines  ┐
- **JE** = "        "        "   — 6 pines   │
- **JA** = N.U.                             │ Macho–Hembra
- **JB** = Conector MOLEX 2,54 — 8 pines    │
- **JC** = "        "        2,54 — 8 pines │
- **JF** = "        "        "   — 16 pines ┘
- **JG** = "        "        "   — 8 pines MACHO

### POTENCIOMETROS

- P1 = 250 Ω LIN.
- P2 = 1K LIN.

### ARRAY

| Ref. | Valor | Ref. | Valor |
|---|---|---|---|
| AR1 | 1K 8+1 | AR5 | 1K 8+1 |
| AR2 | 1K 8+1 | AR6 | 10K 6+1 |
| AR3 | 10K 8+1 | AR7 | 220 Ω 4+1 |
| AR4 | N.U. | AR8 | N.U. |
| | | AR9 | 4K7 8+1 |

![Relación componentes C.P.U.](manual-images/page-09.jpg)

## SITUACION DE COMPONENTES C.P.U. — Ref: 53/3291

*(PDF page 10 — manual page 6)*

Component placement drawing (silkscreen) for the CPU board.

![Situación de componentes C.P.U.](manual-images/page-10.jpg)

## CONECTORES C.P.U. "Super-star" — Ref: 53/3291

*(PDF page 11 — manual page 7)*

**JA** — pines 1 a 22: **N.U.**

**JB**

| Pin | Señal | |
|---|---|---|
| 1 | PA0 | ┐ |
| 2 | PA1 | │ IC3 |
| 3 | PA2 | │ |
| 4 | PA3 | ┘ |
| 5 | PA4 | ┐ |
| 6 | PA5 | │ IC3 |
| 7 | PA6 | │ |
| 8 | PA7 | ┘ |

**JC**

| Pin | Señal |
|---|---|
| 1 | PA4 IC2 — MICRO 25 PTS |
| 2 | PA5 IC2 — MICRO 100 PTS |
| 3 | PA6 IC2 — CONTAC. CAIDA BOLA |
| 4 | PA7 IC2 — PULSADOR PARTIDAS |
| 5 | PB0 ┐ |
| 6 | PB1 │ IC3 |
| 7 | PB2 │ |
| 8 | PB3 ┘ |

**JD**

| Pin | Señal |
|---|---|
| 1 | FALTA INT. 6,5 |
| 2 | PB5 IC3 |
| 3 | TRAP |
| 4 | PB4 IC3 |
| 5 | N.U. |
| 6 | PB6 IC3 |
| 7 | PB7 IC3 |
| 8 | FASE T1 8035 |
| 9 | N.U. |
| 10 | N.U. |
| 11 | SID |
| 12 | N.U. |
| 13 | N.U. |

**JE**

| Pin | Señal |
|---|---|
| 1 | N.U. |
| 2 | N.U. |
| 3 | /LOAD |
| 4 | /SOD |
| 5 | /CLK |
| 6 | N.U. |

**JF**

| Pin(es) | Señal |
|---|---|
| 1 | — |
| 2, 3 | +5 V |
| 4 | — |
| 5, 6, 7 | GND |
| 8, 9 | +16 V SONIDO |
| 10, 11 | SPK 8 Ω (–) |
| 12, 13 | SPK 8 Ω (+) |
| 14 | 6,3 V POWER |
| 15, 16 | N.C. |

**JG**

| Pin | Bus | Color | Señal |
|---|---|---|---|
| 1 | AD4 | Bl. Ma. | DIANA DERECHA |
| 2 | AD3 | Bl. Ro. | CONTACTO RAMPA ESPECIAL IZQ. |
| 3 | AD2 | Bl. Az. | DIANA IZQ. |
| 4 | AD5 | Bl. Ve. | CONTACTO RAMPA ESPECIAL DHO. |
| 5 | AD6 | Bl. Na. | CONTACTO 100 PUNTOS |
| 6 | AD1 | Bl. Am. | CONTACTO BUMPER DCHO. |
| 7 | AD7 | Am. Na. | CONTACTO BUMPER IZQ. |
| 8 | AD0 | Na. Ne. | CONTACTO 10 PUNTOS |

![Conectores C.P.U.](manual-images/page-11.jpg)

## ESQUEMA PLACA C.P.U. "SUPER-STAR" — Ref. 53-3291

*(PDF pages 13–14 — two-sheet schematic; in the scan these sheets follow the
power-supply component placement sheet)*

**Sheet 1 (grid columns 1–11)** — sound section: 8035 (IC7) with its EPROM 2532
(IC4) and 8212 address latch, the two AY-3-8910 PSGs (IC2 = PSG2, IC3 = PSG1),
LM380 audio amplifier (IC20) with 8 Ω speaker, 8212 I/O latches IC5/IC6, and the
74S138 (IC8) plus 7400/7402/7438 glue producing `/WR35`, `/RD35`, `/PCS1`,
`/PCS2`, `BDIR`, `BC1`, `CLK`, `LOAD`, `SOD` and the phase-detection logic (JD-9).

![Esquema C.P.U. — hoja 1](manual-images/page-13.jpg)

**Sheet 2 (grid columns 13–21)** — main CPU section: 8085 (IC9), 8212 address
latch (IC10), 74S138 address decoder (IC8) generating `/CS0`…`/CS3` from A14/A15,
program EPROM socket IC19 (marked "EPROM 2532 ó 2564", fitted with a 27128),
second EPROM socket IC14 ("EPROM 2564", N.U.), 5517 RAM 2K×8 (IC11) on the
battery-backed `+P` rail, 74HC00 tilt/antenna circuit (IC16), 74HC74 (IC12),
and the `+P` battery back-up network (R42, D13/D14, AC1).

![Esquema C.P.U. — hoja 2](manual-images/page-14.jpg)

---

# FUENTE DE ALIMENTACION — Ref. 53/3309

## SITUACION COMPONENTES DE F. ALIMENTACION "SUPER STAR" — Ref: 53/3309

*(PDF page 12 — manual page 9)*

Component placement drawing for the power supply board.

![Situación componentes F. Alimentación](manual-images/page-12.jpg)

## COMPONENTES F. ALIMENTACION "Super star" — Ref: 53/3309

*(PDF page 15 — manual page 10)*

### RESISTENCIAS

| Ref. | Valor | Ref. | Valor |
|---|---|---|---|
| R1 | 220 Ω | R10 | 390 Ω |
| R2 | 5K6 | R11 | 510 Ω |
| R3 | 8K2 | R12 | 510 Ω |
| R4 | 470 Ω | R13 | 2K7 1W |
| R5 | 47K | R14 | 560 Ω 1/2 W |
| R6 | 1K | R15 | 560 Ω 1/2 W |
| R7 | 33 Ω | R16 | 330 Ω 1/2 W |
| R8 | 120K | R17 | 10K Ω 1/2 W |
| R9 | 390 Ω | | |

### CONDENSADORES

| Ref. | Valor |
|---|---|
| C1 | 470 K |
| C2 | 1 K |
| C3 | 10000 µF 16 v. |
| C4 | 10000 µF 16 v. |
| C5 | 10000 µF 16 v. |
| C6 | 10000 µF 16 v. |

### DIODOS

| Ref. | Tipo | Ref. | Tipo |
|---|---|---|---|
| D1 | N.U. | D8 | 1N4148 |
| D2 | N.U. | D9 | 1N4148 |
| D3 | 1N4148 | D10 | 1N3492 ┐ |
| D4 | 1N4148 | D11 | 1N3492 │ Cátodo común |
| D5 | 1N4148 | D12 | 1N3492 │ |
| D6 | 1N4148 | D13 | 1N3492 ┘ |
| D7 | 1N4148 | D14 | 1N4148 |

### TRANSISTORES

| Ref. | Tipo |
|---|---|
| TR1 | BC337 |
| TR2 | BC337 |
| TR3 | LM323 |

### PUENTES RECTIFICADORES

| Ref. | Tipo |
|---|---|
| PR1 | FAGOR 25 A. TIPO FB 2502 |
| PR2 | FAGOR 1 A. TIPO B125 C1000 |

### CONECTORES

| Ref. | Tipo |
|---|---|
| JA | CONECTOR MOLEX 3,96 MACHO 16 PINES CUADRADOS |
| JB | " " " " 23 " " |
| JC | NO MONTADO |

![Componentes F. Alimentación](manual-images/page-15.jpg)

## CONECTORES F. ALIMENTACION "SUPER-STAR" — REF: 53/3309

*(PDF page 16 — manual page 11)*

**JA**

| Pin | Color | Señal |
|---|---|---|
| 1 | Ma. | 7 v. ~ |
| 2 | Ma | 7 v. ~ |
| 3 | Ro | 7 v. ~ |
| 4 | Ro | 7 v. ~ |
| 5 | Vi | 0 v. |
| 6 | Vi | 0 v. |
| 7 | Am | 11 v. ~ |
| 8 | Am | 11 v. ~ |
| 9 | Bl | 11 v. ~ |
| 10 | Bl | 11 v. ~ |
| 11 | Na | 48 v. ~ |
| 12 | Na | 48 v. ~ |
| 13 | Ne | 0 v. |
| 14 | Ne | 0 v. |
| 15 | — | LLAVE |
| 16 | — | N.U. |
| 17–21 | — | N.C. |

**JB**

| Pin | Color | Señal |
|---|---|---|
| 1 | Bl | 9 v. |
| 2 | Bl | 9 v. |
| 3 | Ne | 9 v. |
| 4 | Ro | +5 v. |
| 5 | Ro | +5 v. |
| 6 | Ro | +5 v. |
| 7 | Am | 16 v. SONIDO |
| 8 | — | LLAVE |
| 9 | Na | 48 v. |
| 10 | Na | 48 v. |
| 11 | Ne | 48 v. |
| 12 | Gr. Ro. | TRAP |
| 13 | Gr. Az. | DETECCION DE FASE |
| 14 | Vi | GND |
| 15 | Vi | GND |
| 16 | Vi | GND |
| 17 | Vi | GND |
| 18 | — | LLAVE |
| 19 | Ma | FASE A |
| 20 | Ma | FASE A |
| 21 | Gr | FASE B |
| 22 | Gr | FASE B |
| 23 | Az | 6,3 v. POWER C.P.U. |

**JC** — pines 1 a 7: N.C.

![Conectores F. Alimentación](manual-images/page-16.jpg)

## FUENTE DE ALIMENTACION "SUPER-STAR" — Ref. 53/3309 (esquema)

*(PDF page 17 — manual page 12. **PDF page 19 is a duplicate scan of this same
sheet**, rotated differently.)*

Mains transformer with 110/120/130/200/210/220/230/240 V taps, secondaries for
7 V, 11 V, 12 V, 48 V and 6,3 V, bridge rectifiers PR1/PR2, LM323 (TR3) +5 V
logic regulator, the TR1/TR2 "TRAP" circuit and the phase-detection network,
plus fluorescent tube, reactancia (ballast), cebador (starter) and mains filter.

Outputs marked on the drawing:

| Salida | Destino |
|---|---|
| JB 7 | 16 v. SONIDO |
| JB 20-19 | FASE A |
| JB 1-2-3 | 9 v. DISPLAYS |
| JB 22-21 | FASE B |
| JB 4-5-6 | +5 v. LOGICA |
| JB 9-10-11 | 48 V |
| — | 0 V |
| — | 6,3 V |
| — | 6,3 V. LUCES FIJAS PANEL DE JUEGO LADO DERECHO (fusible 3A) |
| — | 6,3 V. LUCES FIJAS PANEL DE JUEGO LADO IZQUIERDO (fusible 3A) |
| JB 14-15-16-17 | GND |
| — | ALIMENTACION BUMPERS Y EXPULSORES (fusible 1,5 A) |
| JB 23 | 6,3 V POWER CPU |
| JB 12 | TRAP |
| JB 13 | DETECCION FASE |
| — | LUCES MONEDEROS DE 100 Y 25 PTS (fusible 1A) |

![Esquema Fuente de Alimentación](manual-images/page-17.jpg)

*(PDF page 19 — duplicate of the sheet above.)*

![Esquema Fuente de Alimentación (duplicado)](manual-images/page-19.jpg)

---

# DRIVER — Ref. 53/3308

## SITUACION DE COMPONENTES DRIVER — Ref: 53/3308

*(PDF page 18 — manual page 13)*

Component placement drawing for the driver board.

![Situación de componentes Driver](manual-images/page-18.jpg)

## RELACION DE COMPONENTES DRIVER — Ref. 53/3308

*(PDF page 20 — manual page 14)*

### RESISTENCIAS

| Ref. | Valor |
|---|---|
| R1 – R10 | 56 Ω |
| R11 – R23 | 56 Ω |
| R24 | 220 Ω |
| R25 | 1K |
| R26 – R35 | 100 Ω |

*(The list prints "R22" twice at the foot of the second column; R26–R35 are bracketed
together at 100 Ω.)*

### CONDENSADORES

| Ref. | Valor | Ref. | Valor |
|---|---|---|---|
| C1 | 2,2 µF 35 V | C12 | 2,2 µF 16 V |
| C2 | 2,2 µF 35 V | C13 | 47 µF 16 V |
| C3 | 47 µF 16 V | C14 | " " |
| C4 | " " | C15 | " " |
| C5 | " " | C16 | " " |
| C6 | " " | C17 | " " |
| C7 | " " | C18 | " " |
| C8 | " " | C19 | " " |
| C9 | " " | C20 | " " |
| C10 | " " | C21 | " " |
| C11 | 2,2 µF 16 V | | |

6 CD = 100 nF 16 V

### DIODOS

D1 al D36 — 1N4007

### ARRAY

| Ref. | Valor | Ref. | Valor |
|---|---|---|---|
| AR1 | 10K 8+1 | AR5 | 4K7 8+1 |
| AR2 | 10K 4+1 | AR6 | 10K 4+1 |
| AR3 | 4K7 4+1 | AR7 | 10K 4+1 |
| AR4 | 4K7 8+1 | AR8 | 10K 4+1 |

### TRANSISTORES

| Ref. | Tipo |
|---|---|
| T1 al T23 | BT106 |
| T24 al T30 | BC337 |
| T31 | BDX53C |
| T32 | BDX53C |
| T33 | " " |
| T34 | " " |
| T35 | TIP141 |
| T36 | BDX53C |
| T37 | " " |
| T38 | " " |
| T39 | " " |
| T40 | TIP141 |

### CIRCUITOS

| Ref. | Tipo |
|---|---|
| IC1 | 4028 |
| IC2 | 4028 |
| IC3 | 4028 |
| IC4 | 7414 |
| IC5 | 74165 |
| IC6 | 74165 |
| IC7 | 4028 |

### CONECTORES

| Ref. | Tipo | Ref. | Tipo |
|---|---|---|---|
| JA | MOLEX 2,54 — 25 PINES | JK | MOLEX 2,54 — 6 PINES |
| JB | MOLEX ACODADO 2,54 — 8 PINES | JL | " " — 10 " |
| JC | " " " — 8 " | JM | " " — 10 " |
| JD | " " " — 13 " | JN | " " — 9 " |
| JE | " " " — 6 " | JO | " " — 6 " |
| JF | " " " — 16 " | JP | " " — 10 " |
| JG | MOLEX 3,96 — 21 PINES | JQ | " " — 20 " |
| JH | MOLEX 2,54 — 11 PINES | | |

![Relación de componentes Driver](manual-images/page-20.jpg)

## RELACION CONECTORES DRIVER "Super-Star" — Ref: 53/3308

*(PDF page 21 — manual page 15. **See Fe de erratas: JA is reversed — JA1 Ma … JA25 Gr.**)*

**JA**

| Pin | Color | Señal | Fase A |
|---|---|---|---|
| 1 | Gr. | FASE B | |
| 2 | Gr. | FASE B | |
| 3 | Vi. | GND | |
| 4 | Vi. | GND | |
| 5 | Bl. | +9V | |
| 6 | Bl. | +9V | |
| 7 | Bl. Am. | JUGADOR 2º | JUGADOR 4º |
| 8 | Bl. Na. | LUZ FALTA | |
| 9 | Bl. Ve. | LOTERIA 0 | LOTERIA 90 |
| 10 | Bl. Az. | LOTERIA 10 | LOTERIA 80 |
| 11 | Bl. Ro. | LOTERIA 20 | LOTERIA 70 |
| 12 | Bl. Vi. | LOTERIA 30 | LOTERIA 60 |
| 13 | Bl. Ma. | LOTERIA 40 | LOTERIA 50 |
| 14 | Ro. | +5V | |
| 15 | Ro. | +5V | |
| 16 | Am. Ne. | /LOAD | |
| 17 | Ve. Ne. | /SOD | |
| 18 | Na. Ne. | /CLK | |
| 19 | Vi. | GND | |
| 20 | Vi. | GND | |
| 21 | Bl. Gr. | JUGADOR 1º | JUGADOR 3º |
| 22 | — | N.U. | |
| 23 | — | LLAVE | |
| 24 | Ma. | FASE A | |
| 25 | Ma. | FASE A | |

**JB**

| Pin | Señal |
|---|---|
| 8 | D ┐ |
| 7 | C │ IC1 |
| 6 | B │ |
| 5 | A ┘ |
| 4 | D ┐ |
| 3 | C │ IC2 |
| 2 | B │ |
| 1 | A ┘ |

**JC**

| Pin | Señal |
|---|---|
| 1 | D ┐ |
| 2 | C │ IC3 |
| 3 | B │ |
| 4 | A ┘ |
| 5 | PA 7 IC2 — PULSADOR PARTIDAS |
| 6 | PA 6 IC2 — CONTACTO FINAL PARTIDAS |
| 7 | PA 5 IC2 — MONEDERO DE 100 PTS |
| 8 | PA 4 IC2 — MONEDERO DE 25 PTS |

**JD**

| Pin | Señal |
|---|---|
| 1 | FALTA INT 6,5 |
| 2 | PB5 IC3 |
| 3 | TRAP |
| 4 | PB4 IC3 |
| 5 | N.C. |
| 6 | PB6 IC3 |
| 7 | PB7 IC3 |
| 8 | DETECCION FASE |
| 9 | N.C. |
| 10 | N.C. |
| 11 | SID |
| 12 | N.C. |
| 13 | N.C. |

**JE**

| Pin | Señal |
|---|---|
| 1 | N.C. |
| 2 | N.C. |
| 3 | /LOAD |
| 4 | /SOD |
| 5 | /CLK |
| 6 | N.C. |

**JF**

| Pin | Señal |
|---|---|
| 1 | +5V |
| 2 | +5V |
| 3 | +5V |
| 4 | GND |
| 5 | GND |
| 6 | GND |
| 7 | GND |
| 8 | +16V SONIDO |
| 9 | +16V SONIDO |
| 10 | GND SONIDO |
| 11 | GND SONIDO |
| 12 | SPK SONIDO |
| 13 | SPK SONIDO |
| 14 | POWER 6,3V |
| 15 | Vcc PERIFERICO |
| 16 | Vcc PERIFERICO |

**JG**

| Pin | Color | Señal |
|---|---|---|
| 1 | Az. | 6,3 V |
| 2 | Am. | 16 V |
| 3 | — | LLAVE |
| 4 | Vi. | GND |
| 5 | Vi. | GND |
| 6 | Vi. | GND |
| 7 | Vi. | GND |
| 8 | Ro. | +5 V |
| 9 | Ro. | +5 V |
| 10 | Ro. | +5 V |
| 11 | Gr. Az. | DETECCION FASE |
| 12 | Gr. Ro. | TRAP |
| 13 | Na. | 48 V |
| 14 | Na. | 48 V |
| 15 | — | LLAVE |
| 16 | Bl. | 9 V |
| 17 | Bl. | 9 V |
| 18 | Ma. | FASE A |
| 19 | Ma. | FASE A |
| 20 | Gr. | FASE B |
| 21 | Gr. | FASE B |

**JH**

| Pin | Color | Señal |
|---|---|---|
| 1 | Bl. | 9V |
| 2 | Bl. | 9V |
| 3 | — | LLAVE / N.C. |
| 4 | Ma. | FASE A |
| 5 | Ma. | FASE A |
| 6 | Gr. | FASE B |
| 7 | Gr. | FASE B |
| 8 | Na. | 48 V |
| 9 | Na. | 48 V |
| 10 | Na. | 48 V |
| 11 | Na. | 48 V |

![Relación conectores Driver](manual-images/page-21.jpg)

## RELACION CONECTORES DRIVER (Continuación) — Ref. 53/3308

*(PDF page 22 — manual page 16. **See Fe de erratas: the picabolas contact moves to
JN2, leaving JM3 N.U.**)*

**JK** — pines 1 a 6, color Vi.: **GND**

**JL — BOBINAS**

| Pin | Color | Bobina |
|---|---|---|
| 1 | Bl. Vi. | BANCADA DERECHA |
| 2 | Bl. Gr. | BANCADA IZQUIERDA |
| 3 | Bl. Ne. | FLIPPER |
| 4 | Am. Ve. | SALIDA BOLAS |
| 5 | Am. Az. | PICA-BOLAS |
| 6 | Am. Gr. | PARTIDA ESPECIAL |
| 7 | Am. Ne. | BOBINA MONEDERO |
| 8 | Na. Ve. | CONTADOR 100 PTS. |
| 9 | Na. Vi. | CONTADOR 25 PTS. |
| 10 | — | N.C. |

**JM — CONTACTOS**

| Pin | Color | Contacto |
|---|---|---|
| 1 | Am. Ro. | DIANA IZQUIERDA 4 |
| 2 | Am. Vi. | DIANA IZQUIERDA 5 |
| 3 | Na. Az. | PICA-BOLAS *(→ N.U., ver Fe de erratas)* |
| 4 | Na. Ro. | PASILLO INFERIOR DERECHO |
| 5 | Ve. Az. | PASILLO INFERIOR IZQUIERDO |
| 6 | Ve. Ro. | DIANA IZQUIERDA 1 |
| 7 | Ve. Ne. | DIANA IZQUIERDA 2 |
| 8 | Az. Ro. | DIANA IZQUIERDA 3 |
| 9 | Az. Ne. | SONIDO |
| 10 | Ro. Ne. | GND SONIDO |

**JN — CONTACTOS**

| Pin | Color | Contacto |
|---|---|---|
| 1 | — | N.C. |
| 2 | — | N.C. *(→ PICABOLAS, ver Fe de erratas)* |
| 3 | Az. Ma. | DIANA DERECHA 5ª |
| 4 | Ro. Gr. | DIANA DERECHA 4ª |
| 5 | Bl. Am. | DIANA DERECHA 3ª |
| 6 | Bl. Na. | DIANA DERECHA 2ª |
| 7 | Bl. Ve. | PASILLO SUP. DERECHO |
| 8 | Bl. Az. | PASILLO SUP. IZQUIERDO |
| 9 | Bl. Ro. | DIANA DERECHA 1ª |

**JO — CONTACTOS**

| Pin | Color | Contacto |
|---|---|---|
| 1 | Bl. Gr. | FALTA |
| 2 | Bl. Ma. | PULSADOR PARTIDAS |
| 3 | Bl. Ne. | FINAL PARTIDA |
| 4 | Am. Na. | MONEDERO 100 PTS. |
| 5 | Am. Az. | MONEDERO 25 PTS. |

**JP — LUCES**

| Pin | Color | Luz |
|---|---|---|
| 1 | Am. Ne. | BUMPER DERECHO |
| 2 | Na. Ve. | BUMPER IZQUIERDO |
| 3 | Na. Ro. | BOLA EXTRA DIANA DERECHA |
| 4 | Na. Vi. | BOLA EXTRA DIANA IZQUIERDA |
| 5 | Ve. Vi. | PULSADOR PARTIDAS |
| 6 | — | N.C. |
| 7 | Ve. Ma. | PASILLO DERECHO INF. Y SUPERIOR |
| 8 | Az. Ro. | PASILLO IZQUIERDO INF. Y SUPERIOR |
| 9 | Az. Ne. | ESPECIAL DERECHA |
| 10 | Ro. Ne. | ESPECIAL IZQUIERDA |

**JQ — LUCES**

| Pin | Color | Luz |
|---|---|---|
| 1 | Bl. Am. | LUZ 90000 PUNTOS |
| 2 | Bl. Na. | LUZ AVANZE DOBLE |
| 3 | Bl. Ve. | LUZ 70000 PUNTOS |
| 4 | Bl. Ro. | LUZ BOLA EXTRA (CONSEGUIDA) |
| 5 | Bl. Vi. | LUZ 60000 PUNTOS |
| 6 | Bl. Ma. | LUZ FINAL PARTIDA |
| 7 | Bl. Gr. | LUZ 100000 PUNTOS |
| 8 | Bl. Ne. | LUZ AVANZE TRIPLE |
| 9 | Am. Na. | LUZ 80000 PUNTOS |
| 10 | Am. Vi. | LUZ ESPECIAL PICABOLAS |
| 11 | Am. Gr. | LUZ 10000 PUNTOS |
| 12 | Na. Az. | LUZ BOLA 1ª |
| 13 | Na. Ne. | LUZ 30000 PUNTOS |
| 14 | Ve. Az. | LUZ BOLA 3ª |
| 15 | Ve. Re. | LUZ 50000 PUNTOS |
| 16 | Ve. Ne. | LUZ BOLA 5ª |
| 17 | Az. Ma. | LUZ 40000 PUNTOS |
| 18 | Az. Ne. | LUZ BOLA 4ª |
| 19 | Ro. Gr. | LUZ 20000 PUNTOS |
| 20 | Ro. Ne. | LUZ BOLA 2ª |

![Relación conectores Driver (continuación)](manual-images/page-22.jpg)

## DRIVER "SUPER-STAR" — Ref: 53-3308 (esquema)

*(PDF page 23 — manual page 17. **See Fe de erratas: la luz de falta sale por el
pin 3 del IC1; el pin de salida del conector es el JA8.**)*

Four 4028 BCD-to-decimal decoders (IC7, IC3, IC2, IC1) driving BT106 thyristors,
plus BLOQUE B (BC337 → TIP141 → BDX53C0 coil driver at +48 V) and the FASE A /
FASE B lamp drive block.

**IC7 — BOBINAS** (inputs JD4 PB4, JD2 PB5, JD6 PB6, JD7 PB7)

| Salida | Bobina |
|---|---|
| JL4 | SALIDA BOLAS |
| JL1 | BANCADA DERECHA |
| JL5 | PICA-BOLAS |
| JL2 | BANCADA IZQ. |
| JL3 | FLIPPER |
| JL8 | CONTADOR 100 PTS. |
| JL9 | CONTADOR 25 PTS. |
| JL7 | MONEDERO BOBINA |
| JL10 | N.C. |
| JL6 | TACA |

**IC3 — LUCES** (inputs JC8 PB3, JC7 PB2, JC6 PB1, JC5 PB0)

| Fase B | Fase A |
|---|---|
| N.C. | N.C. |
| N.C. | N.C. |
| N.C. | N.C. |
| N.C. | N.C. |
| N.C. | N.C. |
| JP6 N.C. | JP5 PULSADOR PARTIDAS |
| JP8 PASILLO IZQ. | JP7 PASILLO DCH. |
| JP4 DIANA IZQ. | JP3 DIANA DCH. |
| JP10 ESPECIAL IZQ. | JP9 ESPECIAL DCH. |
| JP2 BUMPER IZQ. | JP1 BUMPER DCH. |

**IC2 — LUCES** (inputs JB1 PA0, JB2 PA1, JB3 PA2, JB4 PA3)

| Fase B | Fase A |
|---|---|
| JQ8 AVAN. TRIPLE | JQ7 100000 |
| JQ2 AVAN. DOBLE | JQ1 90000 |
| JQ10 ESPECIAL PICABOLAS | JQ9 80000 |
| JQ4 BOLA EXTRA | JQ3 70000 |
| JQ6 FIN DE JUEGO | JQ5 60000 |
| JQ16 BOLA 5ª | JQ15 50000 |
| JQ18 BOLA 4ª | JQ17 40000 |
| JQ14 BOLA 3ª | JQ13 30000 |
| JQ20 BOLA 2ª | JQ19 20000 |
| JQ12 BOLA 1ª | JQ11 10000 |

**IC1 — LUCES** (inputs JB5 PA4, JB6 PA5, JB7 PA6, JB8 PA7)

| Fase B | Fase A |
|---|---|
| N.U. | N.U. |
| N.U. | N.U. |
| JA13 LOTERIA 40 | JA13 LOTERIA 50 |
| JA12 LOTERIA 30 | JA12 LOTERIA 60 |
| JA11 LOTERIA 20 | JA11 LOTERIA 70 |
| JA10 LOTERIA 10 | JA10 LOTERIA 80 |
| JA9 LOTERIA 00 | JA9 LOTERIA 90 |
| JA7 JUGADOR 2º | JA7 JUGADOR 4º |
| JA20 JUGADOR 1º | JA20 JUGADOR 3º |
| N.U. | — |

![Esquema Driver](manual-images/page-23.jpg)

## DRIVER "SUPER-STAR" — CONTACTOS — Ref: 53/3308

*(PDF page 24 — manual page 18. **See Fe de erratas: el pin 10 del IC5 sale por el
JN1; el pin 11 del IC5 sale por el JN2 y corresponde al picabolas.**)*

Two 74165 shift registers (IC5, IC6) scanned by `/CLK` (JE-2) and `/LOAD` (JE-4)
through 7414 inverters (IC4), output on `/SID` (JD-3).

**IC5 — DERECHA**

| Salida | Conector | Contacto |
|---|---|---|
| 10 | JN2 | N.U. |
| 6 (H) | JN3 | DIANA 5 |
| 5 (G) | JN4 | DIANA 4 |
| 4 (F) | JN5 | DIANA 3 |
| 3 (E) | JN6 | DIANA 2 |
| 14 (D) | JN9 | DIANA 1 |
| 13 (C) | JN8 | PASILLO SUPERIOR DERECHO |
| 12 (B) | JN7 | PASILLO SUPERIOR IZQUIERDO |
| 11 (A) | JN1 | N.U. |

**IC6 — IZQUIERDA**

| Salida | Conector | Contacto |
|---|---|---|
| 6 (H) | JM3 | PICABOLAS |
| 5 (G) | JM4 | PASILLO INFERIOR DERECHO |
| 4 (F) | JM5 | PASILLO INFERIOR IZQUIERDO |
| 3 (E) | JM6 | DIANA 1 |
| 14 (D) | JM7 | DIANA 2 |
| 13 (C) | JM8 | DIANA 3 |
| 12 (B) | JM1 | DIANA 4 |
| 11 (A) | JM2 | DIANA 5 |

Additional inputs debounced with AR3 pull-ups and capacitors:

| Entrada | Conector | Función |
|---|---|---|
| JD1 → IC4 → JO1 | JO1 | FALTA |
| JC5 | JO2 | PULSADOR PARTIDAS |
| JC6 | JO3 | CAIDA DE BOLAS |
| JC1 | JO4 | M. 100 PTS. |
| JC8 | JO5 | M. 25 PTS. |

![Driver — contactos](manual-images/page-24.jpg)

---

# DISPLAYS — Ref. 53/3307

## SITUACION COMPONENTES DISPLAY "Super Star" — Ref: 53/3307

*(PDF page 25 — manual page 19)*

Component placement drawing for the display board.

![Situación componentes Display](manual-images/page-25.jpg)

## COMPONENTES DISPLAYS "Super-Star" — REF: 53/3307

*(PDF page 26 — manual page 20)*

### RESISTENCIAS

| Ref. | Valor |
|---|---|
| R1, R2 | 2K2 1/4 W. |
| R3 – R9 | 18 Ω 3 W. |
| R10 | 680 Ω 1/4 W. |
| R11 – R20 | 680 Ω 1/4 W. |
| R21 – R25 | 680 Ω 1/4 W. |
| R26 – R32 | 18 Ω 3 W. |

*(The middle column of the original repeats the labels "R3" and "R4" where R13 and
R14 are meant.)*

### CONDENSADORES

| Ref. | Valor |
|---|---|
| C1 | 10 K |
| C2 | 100 K |
| 4 CD | 100 K |

### DISPLAYS

D1 – D2 .... D30 — **HDSP 3400**

### ARRAY

| Ref. | Valor |
|---|---|
| AR1 | 10K 8+1 |
| AR2 | 10K 8+1 |
| AR3 | 220 Ω 4+1 |

### CONECTORES

JA — MOLEX 2,54 ACODADO 25 PINES

### TRANSISTORES

| Ref. | Tipo |
|---|---|
| TR1 – TR7 | BC327 |
| TR8 – TR10 | TIP116 |
| TR11 – TR20 | TIP116 |
| TR21 – TR23 | TIP116 |
| TR24 – TR30 | BC327 |

### CIRCUITOS

| Ref. | Tipo |
|---|---|
| IC1 | 74164 |
| IC2 | 8279 |
| IC3 | 7414 |
| IC4 | 555 |
| IC5 | 7447 |
| IC6 | 74159 |
| IC7 | 7447 |

![Componentes Displays](manual-images/page-26.jpg)

## DISPLAY "SUPER STAR" — Ref: 53-3307 (esquema)

*(PDF page 27 — manual page 21. **See Fe de erratas for the corrected JA pinout.**)*

8279 keyboard/display controller (IC2) fed serially through a 74164 (IC1) from
`CLK` / `SOD` / `LOAD`; 74159 (IC6) drives the digit anodes through CIRCUITO A
(AR1/AR2 + TR8…TR23), and two 7447 decoders (IC5, IC7) drive the segments through
CIRCUITO B (R3…R9 / R26…R32 + TR1…TR7 / TR24…TR30). A 555 (IC4) provides the
scan clock.

**CONECTOR JA**

| Pin | Color | Señal |
|---|---|---|
| 1 | Vi. | GND |
| 2 | Vi. | GND |
| 3 | Ma. | FASE A |
| 4 | Ma. | FASE A |
| 5 | LLAVE | — |
| 6 | Nc. | — |
| 7 | Bl. Gr. | LUZ 1er Y 3er JUGADOR |
| 8 | Vi. | GND |
| 9 | Vi. | GND |
| 10 | Na. Ne. | CLK |
| 11 | Ve. Ne. | SOD |
| 12 | Am. Ne. | LOAD |
| 13 | Ro. | +5 V. |
| 14 | Ro. | +5 V. |
| 15 | Bl. Ma. | LUZ LOTERIA 40 y 50 |
| 16 | Bl. Vi. | " 30 y 60 |
| 17 | Bl. Ro. | " 20 y 70 |
| 18 | Bl. Az. | " 10 y 80 |
| 19 | Bl. Ve. | " 0 y 90 |
| 20 | Bl. Na. | FALTA |
| 21 | Bl. Am. | LUZ 2º y 4º JUGADOR |
| 22 | Bl. | +9 V. |
| 23 | Bl. | +9 V. |
| 24 | Gr. | FASE B |
| 25 | Gr. | FASE B |

Display groupings on the drawing:

- IC5 → displays D1-D2, D3-D4, D6-D7, D8-D9, D11-D12, D13-D14 (via TR2…TR7)
- IC7 → displays D15-D16, D17-D18, D19-D20, D21-D22, D23-D24, D25-D26, D27-D28, D29-D30

![Esquema Display](manual-images/page-27.jpg)

---

# CONEXION INTERMEDIA — Ref: 53/3310

*(PDF page 28 — manual page 22)*

Interconnect board carrying J1 (33 pines) ↔ J2 (35 pines), plus relay RL1 (75 Ω)
with D1 (1N4148), R1 (22 Ω 1W) and C1 (680K 400V) for the coil supply.

| J1 | Color | Señal | | J2 | Color | Señal |
|---|---|---|---|---|---|---|
| 1 | Am. Ve. | TIERRA | | 1 | Am. Ve. | TIERRA |
| 2 | — | LLAVE | | 2 | — | LLAVE |
| 3 | Ve. | — | | 3 | Ne. | — |
| 4 | Az. | — | | 4 | Az. | — |
| 5 | Bl. Ro. | SW TEST | | 5 | Bl. Ro. | SW DE TEST |
| 6 | Bl. Ve. | SW REGULACION | | 6 | Bl. Ve. | SW REGULACION TANTEO |
| 7 | Vi. | GND | | 7 | Vi. | GND |
| 8 | Am. Gr. | BOBINA TACA | | 8 | Am. Gr. | BOBINA TACA |
| 9 | — | NC | | 9 | Bl. Ne. | RELE ALIMENTACION BOBINAS |
| 10 | — | — | | 10 | Ro. | COMUN BOBINAS |
| 11 | — | — | | 11 | — | LLAVE |
| 12 | Ne. | GND | | 12 | Ne. | GND |
| 13 | Ne. | GND | | 13 | Ne. | GND |
| 14 | Bl. | +9V | | 14 | Bl. | +9V |
| 15 | — | LLAVE | | 15 | Bl. | +9V |
| 16 | Na. | +48V | | 16 | Na. | 48 V |
| 17 | Na. | +48V | | 17 | Na. | 48 V |
| 18 | Am. Ro. | PULSADOR DE FLIPPER IZQUIERDO | | 18 | Am. Ro. | PULSADOR DE FLIPPER IZQUIERDO |
| 19 | Am. Ve. | PULSADOR DE FLIPPER DERECHO | | 19 | Am. Ve. | PULSADOR DE FLIPPER DERECHO |
| 20 | Am. Na. | — | | 20 | Am. Na. | — |
| 21 | Am. Az. | — | | 21 | Am. Az. | — |
| 22 | Az. Ne. | — | | 22 | Az. Ne. | — |
| 23 | Ro. Ne. | GND ALTAVOZ | | 23 | Ro. Ne. | GND ALTAVOZ |
| 24 | Ma. | FASE A | | 24 | Ma. | FASE A |
| 25 | Ve. Vi. | LUZ PULSADOR PARTIDAS | | 25 | Ve. Vi. | L PULSADOR PARTIDAS |
| 26 | Bl. Ma. | PULSADOR PARTIDAS | | 26 | Bl. Ma. | PULSADOR PARTIDAS |
| 27 | Bl. Gr. | CONTACTO FALTA | | 27 | Bl. Gr. | CONTACTO FALTA |
| 28 | Na. Ve. | CONTADOR 100 PTS | | 28 | Na. Ve. | CONTADOR 100 PTS |
| 29 | Na. Vi. | CONTADOR 25 PTS | | 29 | Na. Vi. | CONTADOR 25 PTS |
| 30 | Am. Ne. | BOBINAS MONEDEROS | | 30 | Am. Ne. | BOBINAS MONEDEROS |
| 31 | Az. | 6,3 | | 31 | Az. | 6,3 |
| 32 | Az. | 6,3 | | 32 | Az. | 6,3 |
| — | — | LLAVE | | 33 | — | LLAVE |
| 33 | Ve. | 0V | | 34 | Ve. | 0V |
| — | Ve. | 0V | | 35 | Ve. | 0V |

*(J1 has 33 positions and J2 has 35; the original drawing aligns the two rows
side-by-side, so the pin numbers above the "LLAVE" keys line up but the tail of
the list is offset by two positions.)*

![Conexión intermedia](manual-images/page-28.jpg)

---

# CONTROL BUMPER Y EXPULSOR — Ref. 53/3311

*(PDF page 29 — manual page 23)*

15-way connector J1:

| Pin | Color | Señal |
|---|---|---|
| 1 | Na. Ma. | ENTRADA BUMPER IZQUIERDO |
| 2 | Bl. Az. | SALIDA BUMPER IZQUIERDO |
| 3 | — | LLAVE |
| 4 | Ve. Vi. | ENTRADA BUMPER DERECHO |
| 5 | Am. Az. | SALIDA BUMPER DERECHO |
| 6 | Bl. Am. | ENTRADA EXPULSOR IZQUIERDO |
| 7 | Bl. Ve. | SALIDA EXPULSOR IZQUIERDO |
| 8 | Vi | GND |
| 9 | Vi | GND |
| 10 | Bl. Ro. | ENTRADA EXPULSOR DERECHO |
| 11 | Ve. Ne. | SALIDA EXPULSOR DERECHO |
| 12 | Na. | 48 V |
| 13 | Na. | 48 V |
| 14 | — | — |
| 15 | — | — |

Board components: C1–C4, D1–D8, R1–R8, T1–T4.
Drive circuits: coil at +48 V with 1N4007 flyback, BDX53C output transistor,
470 Ω base bleed, 1K5 series resistor, 4,7 µF (bumper) / 10 µF 35 V (expulsor)
timing capacitor, fed from +9 V through a 1N4007 and the playfield switch;
the expulsor branch is fused at 1,5 A.

![Control bumper y expulsor](manual-images/page-29.jpg)

---

# REGULACION DE PIRULOS

*(PDF page 30 — manual page 24)*

Playfield drawing showing the post ("pirulo") positions, with the legend:

- ◌ (dashed) = **FACIL**
- ○ (solid) = **DIFICIL**

![Regulación de pirulos](manual-images/page-30.jpg)

---

# MUEBLE

*(PDF page 31 — manual page 25; drawing on PDF page 32 — manual page 26)*

> **Fe de erratas:** falta la pieza **01-2339 — Pantallas Luces Loteria**.

| # | Referencia | Descripción |
|---|---|---|
| 1 | 16-CII | CERRADURA DE PUERTA |
| 2 | 01-2398 | ESCUADRA SUJECCION PATAS |
| 3 | — | BISAGRA 20x20x265 |
| 4 | 01-2301 | EMBELLECEDOR TRASERO CRISTAL |
| 5 | 01-2331 | EMBELLECEDOR LATERAL IZQUIERDO DE MUEBLE |
| 6 | — | JUNQUILLO PARA LUNA DE CAMPO DE JUEGO (COMERCIAL) |
| 7 | 01-461 | PLETINA FIJACION MARCO DE PUERTA |
| 8 | 01-453 | MARCO DE PUERTA |
| 9 | 01-2374 | CAJON CON TIRADOR |
| 10 | 01-2372 | SEPARADOR CAJON MONEDAS |
| 11 | 01-2373 | TAPA DE CAJON MONEDAS |
| 12 | 01-2363 | ESCUADRA SUJECION CAJON MONEDAS |
| 13 | 01-2332 | EMBELLECEDOR LATERAL DERECHO DE MUEBLE |
| 14 | 01-2474 | PLETINA FIJACION CABEZA DE MUEBLE |
| 15 | 01-2366 | EJE GIRO DE CABEZA |
| 16 | 10-S1145 | MUEBLE INFERIOR |
| 17 | 06-W3/8D934 | TUERCA W 3/8 DIN 934 |
| 18 | — | NIVELADOR MUEBLE (COMERCIAL) |
| 19 | 06-W3/8x70D933 | TORNILLO W 3/8x70 DIN 933 |
| 20 | 01-476 | PATA DE MAQUINA |
| 21 | 01-394 | PLETINA FIJACION PATA |
| 22 | 01-2401 | GANCHO FIJACION CRISTAL |
| 23 | 01-461 | PLETINA FIJACION GANCHO |
| 24 | 10-S1136 | CRISTAL MUEBLE SUPERIOR |
| 25 | — | REJILLA VENTILACION MUEBLE SUPERIOR (COMERCIAL) |
| 26 | 01-2414 | ESCUADRA SUJECION FLUORESCENTE |
| 27 | 01-2399 | ESCUADRA SUJECION DISPLAYS |
| 28 | 10-S1144 | MUEBLE SUPERIOR |
| 29 | 06-W3/8x70D933 | TORNILLO W3/8x70 DIN 933 |
| 30 | 06-AL3/8 | ARANDELA PLANA LISA 3/8 |
| 31 | 01-2367 | PLACA GIRO DE CABEZA |
| 32 | 01-1781 | MARCO IDENTIFICACIONES |
| 33 | 01-1782 | PROTECCION IDENTIFICACIONES |
| 34 | 01-540 | GOMA TOPE |
| 35 | 10-666 | REJILLA DE ALTAVOZ |

![Mueble — lista](manual-images/page-31.jpg)
![Mueble — despiece](manual-images/page-32.jpg)

---

# TABLERO DE JUEGO

*(PDF page 33 — manual page 27; drawing on PDF page 34 — manual page 28)*

| # | Referencia | Descripción |
|---|---|---|
| 1 | 06-M3'5x9'5D7981 | TORNILLO M3'5x9'5 DIN 7981 |
| 2 | 01-2272 | U DE CIERRE FINAL |
| 3 | 01-2475 | VARILLA NYLON Ø 6 |
| 4 | 01-2480 | TORNILLO PARA PIRULO Y PLASTICO |
| 5 | 01-2271 | PIRULO SALIDA DE BOLAS |
| 6 | 02-210 | LISTON IZQUIERDO DE TABLERO |
| 7 | 06-4x55D97 | TORNILLO 4x55 DIN 97 |
| 8 | 01-2275 | TANTEADOR TARJETERO |
| 9 | 10-S1142 | INSTRUCCIONES TARJETERO |
| | 10-S1139 | LEYENDA TANTEOS 2.500.000 P. |
| | 10-S1140 | LEYENDA TANTEOS 3.200.000 P. |
| | 10-S1141 | LEYENDA TANTEOS EN BLANCO |
| 10 | 10-S1138 | TARJETERO |
| 11 | 01-2300 | DISTANCIADOR TARJETERO |
| 12 | 10-S1143 | METACRILATO SERIGRAFIADO |
| 13 | 02-204 | TABLERO DE MADERA |
| 14 | 06-3'5x13D7981 | TORNILLO 3'5x13 DIN 7981 |
| 15 | 06-3'5x13D7981 | TORNILLO 3'5x13 DIN 7981 |
| 16 | 01-309 | ESCUADRA TRASERA SUJECION TARJETERO |
| 17 | 06-M3x8D84 | TORNILLO M3x8 DIN 84 |
| 18 | 01-2299 | ESCUADRA SUJECION TABLERO |
| 19 | 06-4'2x16D7981 | TORNILLO 4'2x16 DIN 7981 |
| 20 | 06-3'5x35D72 | TORNILLO 3'5x35 DIN 72 |
| 21 | 02-209 | LISTON DERECHO DE TABLERO |
| 22 | 02-208 | LISTON CENTRAL DE TABLERO |
| 23 | 10-S1137 | FLECHA |
| 24 | 06-3'5x9'5D7981 | TORNILLO 3'5x9'5 DIN 7981 |
| 25 | 01-396 | TAPA SALIDA DE BOLAS |
| 26 | 01-2333 | LUNA PARA CAMPO DE JUEGO |

![Tablero de juego — lista](manual-images/page-33.jpg)
![Tablero de juego — despiece](manual-images/page-34.jpg)

---

# PLASTICOS Y EMBELLECEDORES DE TABLERO

*(PDF page 35 — manual page 29; drawing on PDF page 36 — manual page 30)*

## PLASTICOS TABLERO

| # | Referencia | Descripción |
|---|---|---|
| 1 | 10-S1119 | MEDIA LUNA |
| 2 | 10-S1122 | PLASTICO CENTRAL PICABOLAS |
| 3 | 10-S1121 | PLASTICO LATERAL IZQUIERDO GRANDE |
| 4 | 10-S1120 | PLASTICO LATERAL DERECHO GRANDE |
| 5 | 10-S1124 | PLASTICO LATERAL IZQUIERDO PEQUEÑO |
| 6 | 10-S1123 | PLASTICO LATERAL DERECHO PEQUEÑO |
| 7 | 10-S1125 | PLASTICO INFERIOR IZQUIERDO |
| 8 | 10-S1126 | PLASTICO INFERIOR DERECHO |

## EMBELLECEDORES

| # | Referencia | Descripción |
|---|---|---|
| 9 | 01-2255 | PLETINA EMBELLECEDORA IZQUIERDA PEQUEÑA |
| 10 | 01-2254 | PLETINA EMBELLECEDORA IZQUIERDA GRANDE |
| 11 | 01-2253 | PLETINA EMBELLECEDORA DERECHA PEQUEÑA |
| 12 | 01-2252 | PLETINA EMBELLECEDORA DERECHA GRANDE |

![Plásticos tablero — lista](manual-images/page-35.jpg)
![Plásticos tablero — despiece](manual-images/page-36.jpg)

---

# PUERTA

*(PDF page 37 — manual page 31; drawing on PDF page 38 — manual page 32)*

*(The left-hand item numbers are clipped in the scan; they run 1–44 in sequence.)*

| # | Referencia | Descripción |
|---|---|---|
| 1 | 06-DE3D6798 | ARANDELA DENTADA EXTERIOR 3 DIN 6798 |
| 2 | 06-DE4D6798 | ARANDELA DENTADA EXTERIOR 4 DIN 6798 |
| 3 | 06-AL4 | ARANDELA PLANA LISA 4 |
| 4 | 06-AL3 | ARANDELA PLANA LISA 3 |
| 5 | 06-M3x5D7985 | TORNILLO M3x5 DIN 7985 |
| 6 | 06-M3x8D84 | TORNILLO M3x8 DIN 84 |
| 7 | 06-M3x6D84 | TORNILLO M3x6 DIN 84 |
| 8 | 06-M4x8D7985 | TORNILLO M4x8 DIN 7985 |
| 9 | 06-M3x20D7985 | TORNILLO M3x20 DIN 7985 |
| 10 | 06-M4x5D933 | TORNILLO M4x5 DIN 933 |
| 11 | 06-2'9x6'5D7981 | TORNILLO 2'9x6'5 DIN 7981 |
| 12 | 06-W1/8x15D84 | TORNILLO W 1/8x15 DIN 84 |
| 13 | 07-TGV7 | TOTALIZADOR |
| 14 | 01-48 | ESCUADRA CONTACTOS |
| 15 | 05-1082 | CONTACTO DE FALTA |
| 16 | — | AISLANTE |
| 17 | 01-464 | RESORTE DEVOLUCIÓN MONEDAS |
| 18 | 10-S1152 | PULSADOR DEVOLUCION 25 PTAS. |
| | 10-S1153 | PULSADOR DEVOLUCION 100 PTAS. |
| 19 | 01-2278 | SOPORTE TOTALIZADOR |
| 20 | 01-2407 | CARTON AISLANTE |
| 21 | 01-449 | EMBELLECEDOR ENTRADA MONEDAS |
| 22 | 01-623 | PORTALAMPARAS |
| 23 | 01-450 | EMBELLECEDOR SALIDA MONEDAS |
| 24 | 01-462 | TRAMPILLA CAZOLETA DEVOLUCION |
| 25 | 01-457 | PUERTA DOS MONEDEROS |
| 26 | 01-1729 | ESCUADRA FIJACION PLACA |
| 27 | 16-CII | CERRADURA PUERTA |
| 28 | 01-446 | GUIA MONEDAS CORTO |
| 29 | 01-2382 | MUELLE PARA ACCIONADOR DE PALANCA MONEDERO |
| 30 | 01-469 | RESORTE DE BOBINA |
| 31 | 01-466 | CONJUNTO NUCLEO BOBINA |
| 32 | 01-455 | CAZOLETA DEVOLUCION MONEDAS |
| 33 | 01-459 | SOPORTE LARGO DE MICRO |
| 34 | 06-M3D934 | TUERCA M-3 DIN 934 |
| 35 | 14/137 | MICRO MONEDERO |
| 36 | 01-2313 | AMARRE ANTERIOR MONEDERO |
| 37 | 01-2314 | SOPORTE UNION GUIA MONEDAS |
| 38 | 01-439 | SOPORTE CORTO DE MICRO |
| 39 | 10-B257/24 | BOBINA MONEDERO |
| 40 | 01-437 | BALANCIN PARA BOBINA |
| 41 | 01-2325 | SOPORTE GENERAL MONEDERO |
| 42 | 01-454 | GUIA MONEDAS LARGO |
| 43 | 10-S1150 | PROTECCION MONEDERO |
| 44 | 06-M3x10 D7985 | TUERCA M3x10 DIN 7985 |

![Puerta — lista](manual-images/page-37.jpg)
![Puerta — despiece](manual-images/page-38.jpg)

---

# SALIDA DE BOLAS

*(PDF page 39 — manual page 33; drawing on PDF page 40 — manual page 34)*

| # | Referencia | Descripción |
|---|---|---|
| 1 | 01-336 | MUELLE |
| 2 | 01-74 | NUCLEO DE BOBINA |
| 3 | 06-PA5x40D81 | PASADOR DE ALETAS PA5x40 DIN 81 |
| 4 | 01-2308 | BIELA DE CELOTEX |
| 5 | 06-SG5D6799 | ARANDELA DE SEGURIDAD 5 DIN 6799 |
| 6 | 06-SG4D6799 | ARANDELA DE SEGURIDAD 4 DIN 6799 |
| 7 | 01-2260 | EXPULSOR |
| 8 | 01-518 | TOPE DE BIELA |
| 9 | — | PASADOR DE ALETAS (COMERCIAL) |
| 10 | 01-2358 | CONJUNTO SOPORTE |
| 11 | 01-663 | ENVOLVENTE INFERIOR BOBINA |
| 12 | 01-2470 | ENVOLVENTE SUPERIOR |
| 13 | 06-M4x8D7985 | TORNILLO M4x8 DIN 7985 |
| 14 | 06-DE4D6798 | ARANDELA DENTADA EXTERIOR DIN 6798 |
| 15 | 06-M4D936 | TUERCA M4 DIN 936 |
| 16 | 10-B257/27 | BOBINA |
| 17 | 06-DE4D6798 | ARANDELA DENTADA EXTERIOR 4 DIN 6798 |
| 18 | 06-M4x15D7985 | TORNILLO M4x15 DIN 7985 |
| 19 | 06-M4x12D7985 | TORNILLO M4x12 DIN 7985 |
| 20 | 06-4x15D81 | TORNILLO 4x15 DIN 81 |
| 21 | 01-2344 | RAMPA SALIDA DE BOLAS |
| 22 | 05-1086 | CONTACTO |
| 23 | 06-M3x12D84 | TORNILLOS M3x12 DIN 84 |
| 24 | 01-2462 | ALAMBRE |

![Salida de bolas — lista](manual-images/page-39.jpg)
![Salida de bolas — despiece](manual-images/page-40.jpg)

---

# FLIPPER

*(PDF page 41 — manual page 35; drawing on PDF page 42 — manual page 36)*

| # | Referencia | Descripción |
|---|---|---|
| 1 | 01-503 | BANDERA BATEADOR |
| 2 | 01-502 | GOMA DE BATEADOR |
| 3 | 01-534 | SOPORTE DE BANDERA |
| 4 | 06-3'5x16 DIN 7981 | TORNILLO 3'5x16 DIN 7981 |
| 5 | 01-2341 | SOPORTE DE FLIPPER IZQUIERDO |
| | 01-2342 | SOPORTE DE FLIPPER DERECHO |
| 6 | 01-2311 | PALANCA DE FLIPPER DERECHA |
| | 01-2312 | PALANCA DE FLIPPER IZQUIERDA |
| 7 | 01-267 | EJE DE NUCLEO |
| 8 | 05-1078 | CONTACTO |
| 9 | 06-W1/8x15D84 | TORNILLO W 1/8x15 DIN 84 |
| 10 | 06-W1/8x15D84 | TORNILLO W 1/8x15 |
| 11 | 01-2469 | ENVOLVENTE DE FLIPPER |
| 12 | 10-B257/26 | BOBINA |
| 13 | 06-DE4'2D6798 | ARANDELA DENTADA EXTERIOR 4'2 DIN 6798 |
| 14 | 06-M4x8D933E | TORNILLO M4x8 DIN 933E |
| 15 | 01-46 | NUCLEO |
| 16 | 06-M4D985 | TUERCA AUTOBLOCANTE M4 DIN 985 |
| 17 | 01-44 | SOPORTE DE BOBINA |
| 18 | 01-2343 | BIELA DE CELOTEX |
| 19 | 06-M5D985 | TUERCA AUTOBLOCANTE M5 DIN 985 |
| 20 | 06-4'2x22D7981 | TORNILLO 4'2x22 DIN 7981 |
| 21 | 01-2376 | MUELLE |

![Flipper — lista](manual-images/page-41.jpg)
![Flipper — despiece](manual-images/page-42.jpg)

---

# RECHAZADOR

*(PDF page 43 — manual page 37; drawing on PDF page 44 — manual page 38)*

| # | Referencia | Descripción |
|---|---|---|
| 1 | 01-48 | EXCUADRA CONTACTO |
| 2 | 05-1034 | CONTACTO |
| 3 | 06-W1/8x10D84 | TORNILLO W 1/8x10 DIN 84 |
| 4 | 01-76 | BIELA DE CELOTEX |
| 5 | — | ARANDELA DE NYLON Ø 6'7 INTERIOR |
| 6 | 06-SG5D6799 | ARANDELA DE SEGURIDAD 5 DIN 6799 |
| 7 | 06-PA5x40D81 | PASADOR DE ALETAS PA5x40 DIN 81 |
| 8 | 01-332 | MUELLE |
| 9 | 01-74 | NUCLEO |
| 10 | 01-42 | SOPORTE DE BOBINA |
| 11 | 10-B257/27 | BOBINA |
| 12 | 01-478 | CAMISA PARA NUCLEO |
| 13 | 01-2466 | CONJUNTO DE ENVOLVENTE |
| 14 | 06-M4x8D933E | TORNILLO M4x8 DIN 933E |
| 15 | 06-DE4D6798 | ARANDELA DENTADA EXTERIOR DIN 6798 |
| 16 | 06-AL4 | ARANDELA PLANA LISA 4 |
| 17 | 06-4'2x15D81 | TORNILLO 4'2x15 DIN 81 |
| 18 | 01-2228 | CONJUNTO PALANCA RECHAZADOR |

![Rechazador — lista](manual-images/page-43.jpg)
![Rechazador — despiece](manual-images/page-44.jpg)

---

# BUMPER

*(PDF page 45 — manual page 39; drawing on PDF page 46 — manual page 40.
**PDF page 48 is a duplicate scan of the same drawing.**)*

| # | Referencia | Descripción |
|---|---|---|
| 1 | 10-S1148 | TAPA |
| 2 | 10-S1149 | CUERPO |
| 3 | 01-535 | CONJUNTO ARO DE BUMPER |
| 4 | 05-1085 | CONTACTO |
| 5 | 06-3'5x13D7981 | TORNILLO 3'5x13 DIN 7981 |
| 6 | 06-W1/8x40D84 | TORNILLO W1/8x40 DIN 84 |
| 7 | 01-89 | NUCLEO |
| 8 | 01-95 | BRIDA DE HIERRO |
| 9 | 06-3'5x13D7981 | TORNILLO 3'5x13D7981 |
| 10 | 01-41 | SOPORTE BOBINA |
| 11 | 06-AL4'2 | ARANDELA PLANA LISA 4'2 |
| 12 | 06-DE4'2D6798 | ARANDELA DENTADA EXTERIOR 4'2 DIN 6798 |
| 13 | 06-M4x8D933E | TORNILLO M4x8 DIN 933E |
| 14 | 01-2465 | CONJUNTO ENVOLVENTE Y TOPE DE BOBINA |
| 15 | 10-B257/25 | BOBINA |
| 16 | 01-478 | CAMISA PARA NUCLEO |
| 17 | 01-336 | MUELLE |
| 18 | 06-M4D985 | TUERCA AUTOBLOCABLE M4 DIN 985 |
| 19 | 01-297 | BASE DE BUMPER |
| 20 | 01-347 | MUELLE |
| 21 | 01-298 | BOTON |
| 22 | 01-296 | BALANCIN |
| 23 | 01-162 | BRIDA DE CELOTEX |

![Bumper — lista](manual-images/page-45.jpg)
![Bumper — despiece](manual-images/page-46.jpg)
![Bumper — despiece (duplicado)](manual-images/page-48.jpg)

---

# PICABOLAS

*(PDF page 47 — manual page 41; drawing on PDF page 49 — manual page 42)*

| # | Referencia | Descripción |
|---|---|---|
| 1 | 06-4'2x15D81 | TORNILLO 4'2x15 DIN 81 |
| 2 | 06-DE4'2D6798 | ARANDELA DENTADA EXTERIOR 4'2 DIN 6798 |
| 3 | 01-62 | PROTECCION PICABOLAS |
| 4 | 01-69 | CAZOLETA |
| 5 | 06-3'5x13D7981 | TORNILLO 3'5x13 DIN 7981 |
| 6 | 05-1079 | CONTACTO |
| 7 | 06-3'2x22D81 | TORNILLO 3'2x22 DIN 81 |
| 8 | 06-M4x8D933E | TORNILLO M4x8 DIN 933 E |
| 9 | 06-DE4'2D6798 | ARANDELA DENTADA EXTERIOR 4'2 DIN 6798 |
| 10 | 06-AL4'2 | ARANDELA PLANA LISA 4'2 |
| 11 | 01-2466 | CONJUNTO ENVOLVENTE TOPE DE BOBINA |
| 12 | 01-478 | CAMISA PARA NUCLEO |
| 13 | 10-B257/27 | BOBINA |
| 14 | 01-42 | SOPORTE DE BOBINA |
| 15 | 01-74 | NUCLEO |
| 16 | 01-332 | MUELLE NUCLEO DE BOBINA |
| 17 | 06-PA5x40D81 | PASADOR DE ALETAS PA5x40 DIN 81 |
| 18 | 01-76 | BIELA DE CELOTEX |
| 19 | — | ARANDELA DE NYLON Ø 4'2 INTERIOR |
| 20 | 06-SG5D6799 | ARANDELA DE SEGURIDAD 5 DIN 6799 |
| 21 | 3'5x13D7981 | TORNILLO 3'5x13 DIN 7981 |
| 22 | 01-529 | CONJUNTO SOPORTE PALANCA |
| 23 | 01-530 | CONJUNTO PALANCA ACCIONADORA |
| 24 | 01-531 | CONJUNTO PALANCA INTERMEDIA |
| 25 | 01-487 | MUELLE CORTO |
| 26 | 06-SG5D6799 | ARANDELA DE SEGURIDAD 5 DIN 6799 |

![Picabolas — lista](manual-images/page-47.jpg)
![Picabolas — despiece](manual-images/page-49.jpg)

---

# CIERRE

*(PDF page 50 — manual page 43; drawing on PDF page 51 — manual page 44)*

| # | Referencia | Descripción |
|---|---|---|
| 1 | 01-2305 | EMBELLECEDOR SUPERIOR CIERRE |
| 2 | 01-2303 | SOPORTE GENERAL |
| 3 | 01-2307 | CORREDERA |
| 4 | 01-2296 | U DE CIERRE CORREDERA |
| 5 | 06-DE3D6798 | ARANDELA DENTADA EXTERIOR 3 DIN 6798 |
| 6 | 06-M3x8D7985 | TORNILLO M3x8 DIN 7985 |
| 7 | 06-4x15D81 | TORNILLO 4x15 DIN 81 |
| 8 | 06-M5D934 | TUERCA M5 DIN 934 |
| 9 | 06-M5x12D913 | TORNILLO ALLEN M5x12 DIN 913 |
| 10 | 06-4x15D81 | TORNILLO 4x15 DIN 81 |
| 11 | 06-4x15D81 | TORNILLO 4x15 DIN 81 |
| 12 | 06-M3D934 | TUERCA M3 DIN 934 |

![Cierre — lista](manual-images/page-50.jpg)
![Cierre — despiece](manual-images/page-51.jpg)

---

# LANZADOR

*(PDF page 52 — manual page 45; drawing on PDF page 53 — manual page 46)*

| # | Referencia | Descripción |
|---|---|---|
| 1 | 06-SG18x10'5D6799 | ARANDELA DE SEGURIDAD 18x10'5 DIN 6799 |
| 2 | 06-M5x20D933E | TORNILLO M5x20 DIN 933E |
| 3 | 06-DE5'3D6798 | ARANDELA DENTADA EXTERIOR 5'3 DIN 6798 |
| 4 | 01-536 | CONJUNTO ESPARRAGO DE LANZADOR |
| 5 | 06-AL10'5 | ARANDELA PLANA LISA 10'5 |
| 6 | 06-AL10'5 | ARANDELA PLANA LISA 10'5 |
| 7 | 01-104 | PUNTA EXTERIOR |
| 8 | 01-105 | MUELLE CORTO |
| 9 | 01-116 | BASE DE LANZADOR |
| 10 | 01-118 | PLETINA DE FIJACION |
| 11 | 01-106 | MUELLE LARGO |
| 12 | 06-AL10'5 | ARANDELA PLANA LISA 10'5 |

![Lanzador — lista](manual-images/page-52.jpg)
![Lanzador — despiece](manual-images/page-53.jpg)

---

# FALTA Y TACA

*(PDF page 54 — manual page 47; drawing on PDF page 55 — manual page 48)*

| # | Referencia | Descripción |
|---|---|---|
| 1 | 06-4'2x16D7981 | TORNILLO 4'2x16 DIN 7981 |
| 2 | 01-2454 | BASTIDOR CON SOPORTE BOBINA |
| 3 | 53-3312 | PLACA |
| 4 | 01-2336 | SOPORTE FALTA |
| 5 | 06-3'5x13D7981 | TORNILLO 3'5x13 DIN 7981 |
| 6 | 01-2236 | CONTRAPESO |
| 7 | 06-M4x4D934 | TORNILLO ALLEN M4x4 DIN 934 |
| 8 | 01-2237 | TIRANTE CONTRAPESO |
| 9 | 06-M3x5D7985 | TORNILLO M3x5 DIN 7985 |
| 10 | 01-2235 | ARANDELA ANTICONTACTO |
| 11 | 06-DE3D6798 | ARANDELA DENTADA EXTERIOR 3 DIN 6798 |
| 12 | 01-2337 | SOPORTE CONTRAPESO |
| 13 | 06-AL4'3 | ARANDELA PLANA LISA 4'3 |
| 14 | 06-DE4'3D6798 | ARANDELA DENTADA EXTERIOR DIN 6798 |
| 15 | 06-M4x5D84 | TORNILLO M4x5 DIN 84 |
| 16 | 01-120 | SOPORTE BOBINA |
| 17 | 01-341 | NUCLEO Y TACO |
| 18 | 01-540 | GOMA TOPE |
| 19 | 10-B257/28 | BOBINA |
| 20 | 01-523 | CAMISA DE NUCLEO |

![Falta y taca — lista](manual-images/page-54.jpg)
![Falta y taca — despiece](manual-images/page-55.jpg)

---

# DIANAS ABATIBLES

*(PDF page 56 — manual page 49; drawing on PDF page 57 — manual page 50)*

| # | Referencia | Descripción |
|---|---|---|
| 1 | 10-S1147 | DIANA ABATIBLE |
| 2 | 01-2486 | MUELLE DE DIANA |
| 3 | 01-2487 | MUELLE PALANCA DIANA |
| 4 | — | BOBINA DIANAS ABATIBLES |
| 5 | 01-2489 | BLOQUE DE DIANAS (COMPLETO) |
| 6 | 01-2488 | MUELLE RECUPERADOR DIANAS |
| 7 | 05-1077 | CONTACTO DIANA ABATIBLE |
| 8 | 05-1083 | CONTACO DE BANDA |
| 9 | 05-1000 | CONTACTO CORTO DE EXPULSOR |
| 10 | 01-2490 | SOPORTE POTENCIOMETRO |
| 11 | 01-2491 | PESTILLERA TRASERA |

![Dianas abatibles — lista](manual-images/page-56.jpg)
![Dianas abatibles — despiece](manual-images/page-57.jpg)

---

# ACCESORIOS DE TABLERO Y MUEBLE

*(PDF page 58 — manual page 51; drawing on PDF page 59 — manual page 52)*

| # | Referencia | Descripción |
|---|---|---|
| 1 | 01-2427 | MONTAJE APERTURA TABLERO |
| 2 | 01-2477 | SOPORTE APERTURA TABLERO |
| 3 | 01-2478 | TETON POSICIONADOR DE TABLERO |
| 4 | 01-2479 | ESCUADRA SOPORTE TETON POSICIONADOR TABLERO |
| 5 | 01-2406 | SOPORTE TABLERO |
| 6 | 01-2413 | CONJUNTO SALIDA DE BOLAS |
| 7 | 01-2476 | CONJUNTO MONTAJE PASILLO |
| 8 | 05-1080 | CONTACTO PASILLO SENCILLO |
| 9 | 05-1081 | CONTACTO DIANA |
| 10 | 01-2361 | PORTALAMPARAS BOLA |
| 11 | 01-2368 | SOPORTE LUCES PICABOLAS |
| 12 | 01-2480 | TORNILLO SUJECION PIRULO Y PLASTICO |
| 13 | 06-4'5x50D97 | TORNILLO SUJECION PIRULO 4'5x50 DIN 97 |
| 14 | 01-252 | PIRULO LARGO |
| 15 | 01-250 | PIRULO METALICO |
| 16 | 06-AL4 | ARANDELA PLANA LISA 4 |
| 17 | 06-M4x25D933 | TORNILLO |
| 18 | 01-334 | PULSADOR DE FLIPPER |
| 19 | 06-SG5'84 | ARANDELA DE SEGURIDAD 5'84 |
| 20 | 01-335 | GUIA BOTON DE FLIPPER |
| 21 | 05-1029 | CONTACTO PULSADOR FLIPPER |
| 22 | 19-RIRO6M | PULSADOR PARTIDAS |
| 23 | 01-528 | GOMA DE PIRULO |

![Accesorios — lista](manual-images/page-58.jpg)
![Accesorios — despiece](manual-images/page-59.jpg)

---

# ANILLOS ELASTICOS, PORTALAMPARAS Y BARANDILLAS

*(PDF page 60 — manual page 53)*

## ANILLOS ELASTICOS

| Ref. | ØA | ØB |
|---|---|---|
| 01-542 | 8,5 | 6 |
| 01-543 | 27 | 6 |
| 01-544 | 44,5 | 6,5 |
| 01-545 | 66 | 6,5 |

## PORTALAMPARAS

| # | Referencia |
|---|---|
| 1 | 01-61 |
| 2 | 01-54 |
| 3 | 01-2482 |
| 4 | 01-2428 (PORTAFUSIBLES) |
| 5 | 01-2493 |

## BARANDILLAS

| Ref. | A | B | Ø |
|---|---|---|---|
| 01-51 | 35 | 80 | Ø 3,5 |
| 01-53 | 21 | 80 | Ø 2 |
| 01-52 | 35 | 46,5 | Ø 3,5 |
| 01-50 | 35 | 87 | Ø 3,5 |
| 01-49 | 35 | 182,5 | Ø 3,5 (Curvada) |

![Anillos elásticos, portalámparas y barandillas](manual-images/page-60.jpg)

---

# ELEMENTOS ELECTRICOS

*(PDF page 61)*

| Elemento | Especificación |
|---|---|
| POTENCIOMETRO | 47 Ω ; 3 W |
| ALTAVOZ | 8 Ω |
| INTERRUPTOR | K-200 T (casa CYMEN) |
| FLUORESCENTE | 15 W |
| REACTANCIA | 20 W 220 V |
| CEBADOR | 220-240 V 4... 80 W |
| TRANSFORMADOR PEQUEÑO | 7'5 V + 7'5 V 300 mA |
| TRANSFORMADOR F. ALIMENTACION | REF.: 03/3016 |

![Elementos eléctricos](manual-images/page-61.jpg)

---

# Appendix — ROM / memory devices (not part of the original manual)

Summary of the memory devices across the four boards, compiled from the component
lists and schematics above.

| Board | Ref. | Designator | Device | Type | Size | Role |
|---|---|---|---|---|---|---|
| C.P.U. | 53/3291 | **IC19** | **27128** | EPROM | 16 KB | 8085 main game program (`/CE`=pin 20 from `RD`, `/OE`=pin 22 from `/CS0`, A0–A13 all wired) |
| C.P.U. | 53/3291 | **IC4** | **2532** | EPROM | 4 KB | 8035 sound program (A0–A11, D0–D7 to the 8035 external program bus) |
| C.P.U. | 53/3291 | IC14 | 2564 socket | EPROM | — | **N.U.** — second program socket, not fitted |
| C.P.U. | 53/3291 | IC11 | 5517 | Static RAM 2K×8 | 2 KB | Battery-backed working RAM / audits on the `+P` rail (AC1 4,8 V) |

The DRIVER (53/3308: 4028 ×4, 7414, 74165 ×2), DISPLAYS (53/3307: 74164, 8279,
7414, 555, 7447 ×2, 74159) and FUENTE DE ALIMENTACION (53/3309) boards contain no
memory devices.
