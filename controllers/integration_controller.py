"""
Controller that runs the numerical integration algorithms for a request.
"""

from __future__ import annotations

from algorithms.algorithm_factory import AlgorithmFactory
from models.comparison_model import ComputationOutcome
from models.integration_request import IntegrationRequest
from services.error_analysis_service import ErrorAnalysisService
from services.expression_parser import ExpressionParserService
from services.validation_service import ValidationService
from utils.logger import get_logger


class IntegrationController:
    """Turns an ``IntegrationRequest`` into a full ``ComputationOutcome``.

    This controller contains no view code — it is safe to unit test in
    isolation. ``MainController`` calls this and then updates the view
    with the result.
    """

    def __init__(
        self,
        expression_parser: ExpressionParserService,
        error_analysis_service: ErrorAnalysisService,
        validation_service: ValidationService | None = None,
    ) -> None:
        self._expression_parser = expression_parser
        self._error_analysis_service = error_analysis_service
        self._validation_service = validation_service or ValidationService()
        self._logger = get_logger(__name__)

    def compute(self, request: IntegrationRequest) -> ComputationOutcome:
        """Run every method in ``request.methods`` and assemble the outcome.

        Args:
            request: The user's compute request.

        Returns:
            A ``ComputationOutcome`` with raw results, error-annotated
            snapshots, and the exact value (if determinable).

        Raises:
            ValidationError: If the limits are invalid or no methods
                were selected.
            ExpressionParsingError: If the function cannot be parsed.
            AlgorithmError: If a selected method rejects the interval count.
            IntegrationDomainError: If the function is undefined at a
                required sample point.
        """
        self._validation_service.validate_request(
            request.lower_limit, request.upper_limit, request.num_intervals, request.methods
        )

        function_model = self._expression_parser.parse(request.function_expression)
        exact_value = function_model.exact_definite_integral(
            request.lower_limit, request.upper_limit
        )

        raw_results = []
        for method_key in request.methods:
            algorithm = AlgorithmFactory.create(method_key)
            raw_results.append(
                algorithm.integrate(
                    function_model, request.lower_limit, request.upper_limit, request.num_intervals
                )
            )

        snapshots = [
            self._error_analysis_service.build_snapshot(result, exact_value)
            for result in raw_results
        ]

        self._logger.info(
            "Computed %d method(s) for '%s' on [%s, %s] with n=%s",
            len(raw_results), request.function_expression,
            request.lower_limit, request.upper_limit, request.num_intervals,
        )

        return ComputationOutcome(
            function_model=function_model,
            request=request,
            raw_results=raw_results,
            snapshots=snapshots,
            exact_value=exact_value,
        )
