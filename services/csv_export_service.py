"""
Exports a calculation's inputs and results to a CSV file.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

from models.history_entry import MethodResultSnapshot
from models.integration_request import IntegrationRequest
from utils.constants import METHOD_DISPLAY_NAMES
from utils.exceptions import ReportGenerationError
from utils.logger import get_logger

_RESULT_COLUMNS = (
    "Method",
    "Approximate Value",
    "Exact Value",
    "Absolute Error",
    "Relative Error",
    "Percentage Error",
    "Execution Time (s)",
)


class CSVExportService:
    """Writes calculation inputs and per-method results to a CSV file."""

    def __init__(self) -> None:
        self._logger = get_logger(__name__)

    def export(
        self,
        output_path: str | Path,
        request: IntegrationRequest,
        results: list[MethodResultSnapshot],
        exact_value: Optional[float],
    ) -> None:
        """Write the calculation summary and results table to CSV.

        Args:
            output_path: Destination file path (parent dirs created if missing).
            request: The original computation request (function, limits, n).
            results: One snapshot per method that was computed.
            exact_value: The exact value if known, else None.

        Raises:
            ReportGenerationError: If the file cannot be written.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with output_path.open("w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)

                writer.writerow(["Numerical Integration Studio - Calculation Report"])
                writer.writerow(["Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                writer.writerow(["Function", request.function_expression])
                writer.writerow(["Lower Limit", request.lower_limit])
                writer.writerow(["Upper Limit", request.upper_limit])
                writer.writerow(["Number of Intervals", request.num_intervals])
                writer.writerow(
                    ["Methods", ", ".join(METHOD_DISPLAY_NAMES.get(m, m) for m in request.methods)]
                )
                writer.writerow(["Exact Value", exact_value if exact_value is not None else "N/A"])
                writer.writerow([])

                writer.writerow(_RESULT_COLUMNS)
                for result in results:
                    writer.writerow(
                        [
                            METHOD_DISPLAY_NAMES.get(result.method_name, result.method_name),
                            f"{result.approximate_value:.10f}",
                            f"{result.exact_value:.10f}" if result.exact_value is not None else "N/A",
                            f"{result.absolute_error:.6e}" if result.absolute_error is not None else "N/A",
                            f"{result.relative_error:.6e}" if result.relative_error is not None else "N/A",
                            f"{result.percentage_error:.6f}" if result.percentage_error is not None else "N/A",
                            f"{result.execution_time_seconds:.8f}",
                        ]
                    )
            self._logger.info("Exported CSV report to %s", output_path)
        except OSError as exc:
            self._logger.exception("Failed to write CSV report to %s", output_path)
            raise ReportGenerationError(f"Could not write CSV file: {exc}") from exc
