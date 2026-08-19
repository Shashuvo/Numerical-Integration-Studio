# User Guide

## Getting Started

Run the application with:

```bash
python3 main.py
```

## Entering a Calculation

1. **Function f(x):** Type a mathematical expression using `x` as the
   only variable. Supported: `sin`, `cos`, `tan`, `exp`, `log`, `sqrt`,
   and standard arithmetic. Both `x^2` and `x**2` work for powers, and
   implicit multiplication like `2x` is accepted.
2. **Lower limit (a)** and **Upper limit (b):** The bounds of
   integration. The lower limit must be less than the upper limit.
3. **Number of intervals (n):** How finely the interval is subdivided.
   Larger n generally means a more accurate approximation (and a
   slightly longer computation).
4. **Methods:** Check one or more of Trapezoidal Rule, Simpson's 1/3
   Rule, Simpson's 3/8 Rule, and Taylor's Method.

   Note: Simpson's 1/3 Rule needs an even n, and Simpson's 3/8 Rule
   needs n divisible by 3. If your chosen n doesn't satisfy this, the
   application automatically rounds up to the nearest valid value for
   that method and shows the actual n used — you don't need to pick a
   different n for each method.
5. Click **Compute**.

## Reading the Results

- **Results tab:** A table with each method's approximation, the exact
  value (if SymPy could find a closed form), absolute error, relative
  error, and execution time.
- **Plot tab:** The function curve, the shaded area being integrated,
  and each method's sample nodes overlaid in a distinct color.
- **Comparison tab:** The same metrics side by side, with the most
  accurate method (smallest absolute error) highlighted in green.
- **Convergence tab:** Use **Analysis > Convergence Analysis** to see
  how error (log scale) and execution time change as n grows, for
  every currently selected method.

## Menus

- **File > New** — Clear the form and all results.
- **File > Open History** — Browse past calculations; double-click (or
  select + Open) to reload one, or Delete to remove it.
- **File > Export PDF / Export CSV** — Save a report of the current
  calculation. Requires a calculation to have been run first.
- **File > Settings** — Adjust theme, decimal precision, and default
  interval count.
- **View > Light Theme / Dark Theme** — Switch the application's
  color scheme.
- **Analysis > Compare Algorithms** — Jump to the Comparison tab.
- **Analysis > Convergence Analysis** — Run and display a convergence
  sweep for the currently selected methods.

## Troubleshooting

- **"is not a valid mathematical expression"** — Check for typos,
  unbalanced parentheses, or unsupported syntax.
- **"Only 'x' may be used as a variable"** — Your expression references
  a variable other than `x` (e.g. `y`, `t`); rewrite it in terms of `x` only.
- **"is undefined at x = ..."** — The function has a discontinuity
  (division by zero, square root of a negative number, etc.) somewhere
  in `[a, b]`. Choose different limits, or a function that's defined
  throughout the interval.
- **"Please run a calculation before exporting a report"** — Export
  requires a completed calculation in the current session.
