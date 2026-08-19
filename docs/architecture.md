# Architecture

Numerical Integration Studio follows a strict Model-View-Controller
(MVC) layering, built up incrementally across 11 modules.

## Layers

- **`models/`** — Plain `@dataclass` objects with no Qt or business
  logic: `IntegrationRequest` (in), `IntegrationResult` (raw algorithm
  output), `MethodResultSnapshot` / `HistoryEntry` (display + storage),
  `ComputationOutcome` (the full result of one "Compute" action),
  `FunctionModel` (a validated, evaluable SymPy expression).

- **`views/`** — Pure PySide6. `MainWindow` and its widgets/dialogs
  emit Qt signals describing user intent (`compute_requested`,
  `theme_change_requested`, etc.) but never call algorithms, services,
  or the database directly.

- **`controllers/`** — The only layer that touches both views and
  services. `MainController` connects `MainWindow`'s signals to
  focused sub-controllers:
  - `IntegrationController` — runs the selected algorithms
  - `HistoryController` — reads/writes calculation history
  - `ReportController` — drives PDF/CSV export
  - `ConvergenceController` — runs and plots convergence sweeps

- **`services/`** — Stateless, framework-agnostic business logic:
  `ExpressionParserService` (SymPy parsing/validation),
  `ValidationService` (limits/intervals/method-selection checks),
  `ErrorAnalysisService` (absolute/relative/percentage error),
  `ConvergenceService` (error/time-vs-n sweeps), `PDFReportService`,
  `CSVExportService`, `ThemeService`.

- **`algorithms/`** — The four numerical methods, each implementing
  `BaseAlgorithm.integrate()`. `AlgorithmFactory` maps canonical method
  keys (`"trapezoidal"`, `"simpson_1_3"`, `"simpson_3_8"`, `"taylor"`)
  to instances, so controllers can loop over selected methods generically.

- **`database/`** — `DatabaseManager` (SQLite CRUD) and
  `models_orm.py` (row ↔ `HistoryEntry` JSON serialization).

- **`plots/`** — `FunctionPlotter` and `ConvergencePlotter` draw onto
  the generic, content-agnostic `PlotWidget` (an embedded Matplotlib
  canvas with zoom/pan toolbar).

- **`reports/`** — `report_templates.py` holds shared ReportLab
  styling, kept separate from `PDFReportService`'s assembly logic.

- **`utils/`** — `ConfigManager` (YAML settings persistence), a
  custom exception hierarchy (`ValidationError`, `AlgorithmError`,
  `DatabaseError`, etc.), centralized logging, and shared constants.

## Data Flow: One "Compute" Click

1. `FunctionInputWidget` / `MethodSelectorWidget` (views) hold the
   current input; `MainWindow._on_compute_clicked` gathers it and
   emits `compute_requested`.
2. `MainController._on_compute_requested` builds an
   `IntegrationRequest` and calls `IntegrationController.compute()`.
3. `IntegrationController` validates via `ValidationService`, parses
   the function via `ExpressionParserService`, runs each selected
   algorithm via `AlgorithmFactory`, and builds error-annotated
   `MethodResultSnapshot`s via `ErrorAnalysisService`. All of this is
   bundled into a `ComputationOutcome`.
4. `MainController` updates the view (`display_results`,
   `display_comparison`, `FunctionPlotter.plot`), saves the outcome via
   `HistoryController`, and updates the status bar.

Errors at any step raise a subclass of
`NumericalIntegrationStudioError`, which `MainController` catches and
shows via `MainWindow.display_error` (a friendly `QMessageBox`) —
nothing propagates as a raw traceback to the user.

## Design Notes

- **Simpson's rules auto-adjust `n`.** Rather than rejecting a request
  outright when `n` doesn't meet a method's parity/multiple-of-3
  requirement, `SimpsonOneThirdRule` and `SimpsonThreeEighthRule` round
  up to the nearest valid value and report the actual `n` used via
  `IntegrationResult.num_intervals`. This means running all four
  methods together with one shared `n` "just works" instead of failing
  outright over one method's constraint.
- **Taylor's Method** is documented as a specific 4th-order
  formulation in `algorithms/taylor_method.py`, since it isn't a
  single standardized rule the way Trapezoidal/Simpson are.
- **History dialog deletes refresh in place.** `MainController`
  constructs the `HistoryDialog` directly (rather than delegating to
  `MainWindow`) so a delete can call `dialog.refresh()` on the same
  still-open modal dialog instance — a signal round-tripped through
  `MainWindow` would have no way to reach back into an already-open
  dialog.
