# Informe de sesión — ym-lattice-numerics (empuje M0-exacto + M4-seed)

## Plantilla §B2

```
HECHO (TODO VERIFICADO LOCALMENTE — 20/20 tests en verde, primera vez en la
sesión que el contenedor puede ser juez):
  Rama push/m0-exact2d-certified:
    exact2d.py — clausuras de intervalo CERTIFICADAS (redondeo dirigido
      Decimal + cota de cola geométrica explícita) de las Bessel
      modificadas, de la plaqueta exacta 2D I₂(β)/I₁(β) y de la tensión de
      cuerda exacta σ = −log(I₂/I₁). Es el gemelo numérico del satélite
      lean-2d-yang-mills: el mismo sandbox soluble, desde el lado empírico.
      σ(β=1) = 1.42630949844493605150036… con 25 dígitos certificados.
    tests/test_mc_vs_exact2d.py — validación cruzada: el heatbath del T0
      reproduce la plaqueta exacta 2D en β=1 (MC 0.2502 ± 0.007 vs exacto
      0.24019) — primer contacto verificado entre el kernel MC y un valor
      exacto del ecosistema.
    analysis.py — jackknife (exacto sobre la media), binning, tensión de
      cuerda por Creutz ratio con errores (estimador M1, validado
      exactamente sobre un área law sintético), masas efectivas (estimador
      M2, exacto sobre exponenciales puras).
    Interval.ln añadido al kernel de intervalos (redondeo hacia fuera).
    scripts/honesty_gap_2d.py + data/processed/honesty_gap_2d.json —
      SEMILLA M4 ENTREGADA: con la σ exacta certificada, la ventana formal
      (16d+1)²σ < 1 en d=2 FALLA certificadamente en β = 1, 2, 4
      (acoplamientos físicos) y PASA certificadamente en β = 2000
      (σ ≈ 3/2β): la ventana se abre a TRES ÓRDENES DE MAGNITUD en β de la
      región física. Certificados de intervalo en ambos lados.
    HYPOTHESIS_FRONTIER.md actualizado.
SIGUIENTE: medición de correladores 0++ (el estimador de masa efectiva ya
  existe y está testado; falta el código de medición) — desbloquea M2.
BLOQUEOS: ninguno. M3 real sigue pendiente de sincronizar constantes del
  madre por hash de commit (la maquinaria ya se ejercita con el caso 2D).
IMPACTO-INTERFAZ: Interfaces.lean intacto. intervals.py recibió UN método
  aditivo (ln); constants.py sin tocar (kp_sigma_lhs reutilizado tal cual).
HONESTIDAD: (1) El honesty-gap está calculado sobre la σ 2D exacta como
  stand-in declarado; la versión 4D (la que de verdad concierne a la
  ventana del madre) sigue abierta y así consta en el JSON y el frontier.
  (2) La validación MC usa tolerancia holgada (0.02) porque el error naive
  ignora autocorrelación; el estimador binned ya está disponible para
  hacerlo bien en ensembles de verdad. (3) A diferencia de los cinco
  empujes Lean de hoy, AQUÍ NO HAY "UNVERIFIED-LOCALLY": pytest corre en
  este contenedor y los 20 tests pasan; el CI remoto debe reproducirlo.
```

## Cómo aplicar

```bash
git fetch origin
git checkout -b push/m0-exact2d-certified origin/main
git am 0001-*.patch
git push -u origin push/m0-exact2d-certified   # CI reproduce; si verde → PR a main
```

## Verificación local ejecutada

- `python3 -m pytest` → 20 passed (7 del T0 + 13 nuevos).
- `python3 scripts/honesty_gap_2d.py` → fail/fail/fail/pass como se documenta,
  informe regenerable y comiteado en data/processed/.
- Runtime total de la suite ≈ 5 s (el test MC 2D domina con ~2.5 s).

## Qué gana el madre con este empuje

Dos cosas. Primera: el bucle numérico↔formal se cierra por primera vez en
pequeño — el kernel MC está validado contra un valor exacto del mismo modelo
que lean-2d-yang-mills formaliza, y la σ exacta viene con certificado de
intervalo (25 dígitos), que es el formato que un futuro import Lean podría
consumir. Segunda: el deliverable M4 existe en miniatura con certificados en
ambos lados: la ventana formal estilo KP se abre en β ≈ 2000 mientras la
física vive en β ≈ 1–4. Ese número —tres órdenes de magnitud— es exactamente
la brecha de honestidad que este satélite fue creado para medir, y ahora
está en un JSON reproducible en vez de en una frase.
