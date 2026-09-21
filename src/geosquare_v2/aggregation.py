"""Explicit value aggregation over already-assigned V2 cell rows."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable

from .errors import TableDependencyError, ValidationError


class ValueSemantics(str, Enum):
    COUNT = "COUNT"
    TOTAL = "TOTAL"
    DENSITY = "DENSITY"
    MEASUREMENT = "MEASUREMENT"
    RATE = "RATE"
    ORDINAL = "ORDINAL"


class NumericRule(str, Enum):
    COUNT = "count"
    SUM = "sum"
    WEIGHTED_SUM = "weighted_sum"
    MEAN = "mean"
    WEIGHTED_MEAN = "weighted_mean"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    STD = "std"
    QUANTILE = "quantile"


class CategoryRule(str, Enum):
    LARGEST_OVERLAP = "largest_overlap"
    MAJORITY_WEIGHTED = "majority_weighted"
    CENTROID_CATEGORY = "centroid_category"
    PRIORITY_ORDER = "priority_order"
    ALL_CATEGORIES = "all_categories"


class RangeRule(str, Enum):
    WEIGHTED_MEAN = "weighted_mean"
    MIN = "min"
    MAX = "max"
    FULL_RANGE = "full_range"
    DISTRIBUTION = "distribution"


def _require_pandas() -> Any:
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - exercised without table extra
        raise TableDependencyError(
            "aggregation requires the 'table' optional dependency group"
        ) from exc
    return pd


def _as_enum(value: Any, enum_type: Any, name: str) -> Any:
    try:
        return value if isinstance(value, enum_type) else enum_type(value)
    except ValueError as exc:
        raise ValidationError(f"unknown {name}: {value!r}") from exc


def _group_columns(frame: Any, cell_column: str) -> list[str]:
    preferred = ["domain", "level", "x_idx", "y_idx", cell_column, "uri"]
    columns = [column for column in preferred if column in frame.columns]
    if cell_column not in columns:
        columns.append(cell_column)
    if not columns:
        raise ValidationError("a cell column is required")
    return list(dict.fromkeys(columns))


def _validate_columns(frame: Any, columns: Iterable[str]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValidationError(f"missing table columns: {missing}")


def _weights(group: Any, weight_column: str | None) -> list[float]:
    if weight_column is None:
        return [1.0] * len(group)
    values = group[weight_column].astype(float).tolist()
    if any(value < 0 for value in values):
        raise ValidationError("weights must be non-negative")
    if not any(value > 0 for value in values):
        raise ValidationError("weights must contain at least one positive value")
    return values


def _weighted_median(values: list[float], weights: list[float]) -> float:
    ordered = sorted(zip(values, weights), key=lambda item: item[0])
    midpoint = sum(weights) / 2
    cumulative = 0.0
    for value, weight in ordered:
        cumulative += weight
        if cumulative >= midpoint:
            return value
    return ordered[-1][0]


def _weighted_quantile(values: list[float], weights: list[float], quantile: float) -> float:
    if not 0 <= quantile <= 1:
        raise ValidationError("quantile must be in [0, 1]")
    ordered = sorted(zip(values, weights), key=lambda item: item[0])
    target = sum(weights) * quantile
    cumulative = 0.0
    for value, weight in ordered:
        cumulative += weight
        if cumulative >= target:
            return value
    return ordered[-1][0]


def _base_result(group_columns: list[str], key: tuple[Any, ...]) -> dict[str, Any]:
    return dict(zip(group_columns, key))


def aggregate_numeric(
    frame: Any,
    value_column: str,
    *,
    cell_column: str = "gid",
    rule: NumericRule | str = NumericRule.MEAN,
    weight_column: str | None = None,
    value_semantics: ValueSemantics | str = ValueSemantics.MEASUREMENT,
    quantile: float = 0.5,
    output_column: str | None = None,
) -> Any:
    """Aggregate one numeric column per cell with an explicit rule."""
    pd = _require_pandas()
    if not isinstance(frame, pd.DataFrame):
        raise ValidationError("frame must be a pandas.DataFrame")
    _validate_columns(frame, [value_column] + ([weight_column] if weight_column else []))
    selected_rule = _as_enum(rule, NumericRule, "numeric rule")
    _as_enum(value_semantics, ValueSemantics, "value semantics")
    group_columns = _group_columns(frame, cell_column)
    output_name = output_column or value_column
    rows: list[dict[str, Any]] = []

    for key, group in frame.groupby(group_columns, dropna=False, sort=False):
        if not isinstance(key, tuple):
            key = (key,)
        values = group[value_column].astype(float).tolist()
        weights = _weights(group, weight_column)
        weighted_total = sum(value * weight for value, weight in zip(values, weights))
        total_weight = sum(weights)
        if selected_rule is NumericRule.COUNT:
            result = len(values)
        elif selected_rule is NumericRule.SUM:
            result = sum(values)
        elif selected_rule is NumericRule.WEIGHTED_SUM:
            result = weighted_total
        elif selected_rule is NumericRule.MEAN:
            result = sum(values) / len(values)
        elif selected_rule is NumericRule.WEIGHTED_MEAN:
            result = weighted_total / total_weight
        elif selected_rule is NumericRule.MEDIAN:
            result = _weighted_median(values, weights) if weight_column else float(pd.Series(values).median())
        elif selected_rule is NumericRule.MIN:
            result = min(values)
        elif selected_rule is NumericRule.MAX:
            result = max(values)
        elif selected_rule is NumericRule.STD:
            result = float(pd.Series(values).std(ddof=0))
        else:
            result = _weighted_quantile(values, weights, quantile) if weight_column else float(pd.Series(values).quantile(quantile))
        row = _base_result(group_columns, key)
        row[output_name] = result
        row["feature_count"] = len(values)
        rows.append(row)
    return pd.DataFrame(rows)


def aggregate_categorical(
    frame: Any,
    category_column: str,
    *,
    cell_column: str = "gid",
    rule: CategoryRule | str = CategoryRule.MAJORITY_WEIGHTED,
    weight_column: str | None = None,
    priority_order: Iterable[Any] | None = None,
    output_column: str | None = None,
) -> Any:
    """Aggregate categories using overlap, count, priority, or full distribution."""
    pd = _require_pandas()
    if not isinstance(frame, pd.DataFrame):
        raise ValidationError("frame must be a pandas.DataFrame")
    _validate_columns(frame, [category_column] + ([weight_column] if weight_column else []))
    selected_rule = _as_enum(rule, CategoryRule, "category rule")
    group_columns = _group_columns(frame, cell_column)
    output_name = output_column or category_column
    priority = list(priority_order or [])
    rows: list[dict[str, Any]] = []

    for key, group in frame.groupby(group_columns, dropna=False, sort=False):
        if not isinstance(key, tuple):
            key = (key,)
        weights = _weights(group, weight_column)
        scores: dict[Any, float] = {}
        counts: dict[Any, int] = {}
        for category, weight in zip(group[category_column].tolist(), weights):
            scores[category] = scores.get(category, 0.0) + weight
            counts[category] = counts.get(category, 0) + 1
        if selected_rule is CategoryRule.ALL_CATEGORIES:
            total = sum(scores.values())
            result: Any = {str(category): score / total for category, score in scores.items()}
        elif selected_rule is CategoryRule.CENTROID_CATEGORY:
            result = max(counts, key=lambda category: (counts[category], str(category)))
        elif selected_rule is CategoryRule.PRIORITY_ORDER:
            rank = {category: index for index, category in enumerate(priority)}
            result = min(
                scores,
                key=lambda category: (rank.get(category, len(rank)), -scores[category], str(category)),
            )
        else:
            result = max(scores, key=lambda category: (scores[category], str(category)))
        row = _base_result(group_columns, key)
        row[output_name] = result
        row["feature_count"] = len(group)
        if selected_rule is not CategoryRule.ALL_CATEGORIES:
            winning_score = scores[result]
            row["category_share"] = winning_score / sum(scores.values())
        rows.append(row)
    return pd.DataFrame(rows)


def aggregate_range(
    frame: Any,
    lower_column: str,
    upper_column: str,
    *,
    cell_column: str = "gid",
    rule: RangeRule | str = RangeRule.FULL_RANGE,
    weight_column: str | None = None,
    output_prefix: str = "range",
) -> Any:
    """Aggregate numeric ranges without silently treating them as ordinary values."""
    pd = _require_pandas()
    if not isinstance(frame, pd.DataFrame):
        raise ValidationError("frame must be a pandas.DataFrame")
    _validate_columns(frame, [lower_column, upper_column] + ([weight_column] if weight_column else []))
    selected_rule = _as_enum(rule, RangeRule, "range rule")
    group_columns = _group_columns(frame, cell_column)
    rows: list[dict[str, Any]] = []

    for key, group in frame.groupby(group_columns, dropna=False, sort=False):
        if not isinstance(key, tuple):
            key = (key,)
        lowers = group[lower_column].astype(float).tolist()
        uppers = group[upper_column].astype(float).tolist()
        if any(lower > upper for lower, upper in zip(lowers, uppers)):
            raise ValidationError("range lower values must not exceed upper values")
        weights = _weights(group, weight_column)
        centers = [(lower + upper) / 2 for lower, upper in zip(lowers, uppers)]
        row = _base_result(group_columns, key)
        if selected_rule is RangeRule.MIN:
            row[f"{output_prefix}_min"] = min(lowers)
            row[f"{output_prefix}_max"] = min(uppers)
        elif selected_rule is RangeRule.MAX:
            row[f"{output_prefix}_min"] = max(lowers)
            row[f"{output_prefix}_max"] = max(uppers)
        elif selected_rule is RangeRule.WEIGHTED_MEAN:
            total_weight = sum(weights)
            center = sum(value * weight for value, weight in zip(centers, weights)) / total_weight
            row[f"{output_prefix}_value"] = center
        elif selected_rule is RangeRule.DISTRIBUTION:
            row[f"{output_prefix}_distribution"] = [
                {"min": lower, "max": upper, "weight": weight}
                for lower, upper, weight in zip(lowers, uppers, weights)
            ]
        else:
            row[f"{output_prefix}_min"] = min(lowers)
            row[f"{output_prefix}_max"] = max(uppers)
        row["feature_count"] = len(group)
        rows.append(row)
    return pd.DataFrame(rows)


def aggregate_ordinal(
    frame: Any,
    value_column: str,
    *,
    cell_column: str = "gid",
    priority_order: Iterable[Any],
    weight_column: str | None = None,
    output_column: str | None = None,
) -> Any:
    """Aggregate ordinal categories with an explicit priority order."""
    return aggregate_categorical(
        frame,
        value_column,
        cell_column=cell_column,
        rule=CategoryRule.PRIORITY_ORDER,
        weight_column=weight_column,
        priority_order=priority_order,
        output_column=output_column,
    )


def aggregate_to_cells(
    frame: Any,
    *,
    value_type: str = "numeric",
    value_column: str | None = None,
    lower_column: str | None = None,
    upper_column: str | None = None,
    cell_column: str = "gid",
    rule: str | Enum | None = None,
    weight_column: str | None = None,
    value_semantics: ValueSemantics | str = ValueSemantics.MEASUREMENT,
    priority_order: Iterable[Any] | None = None,
    quantile: float = 0.5,
) -> Any:
    """Dispatch to the explicit numeric, category, ordinal, or range aggregator."""
    if value_type == "numeric":
        if value_column is None:
            raise ValidationError("value_column is required for numeric aggregation")
        return aggregate_numeric(
            frame,
            value_column,
            cell_column=cell_column,
            rule=rule or NumericRule.MEAN,
            weight_column=weight_column,
            value_semantics=value_semantics,
            quantile=quantile,
        )
    if value_type == "categorical":
        if value_column is None:
            raise ValidationError("value_column is required for categorical aggregation")
        return aggregate_categorical(
            frame,
            value_column,
            cell_column=cell_column,
            rule=rule or CategoryRule.MAJORITY_WEIGHTED,
            weight_column=weight_column,
            priority_order=priority_order,
        )
    if value_type == "ordinal":
        if value_column is None or priority_order is None:
            raise ValidationError("value_column and priority_order are required for ordinal aggregation")
        return aggregate_ordinal(
            frame,
            value_column,
            cell_column=cell_column,
            priority_order=priority_order,
            weight_column=weight_column,
        )
    if value_type == "range":
        if lower_column is None or upper_column is None:
            raise ValidationError("lower_column and upper_column are required for range aggregation")
        return aggregate_range(
            frame,
            lower_column,
            upper_column,
            cell_column=cell_column,
            rule=rule or RangeRule.FULL_RANGE,
            weight_column=weight_column,
        )
    raise ValidationError("value_type must be numeric, categorical, ordinal, or range")
