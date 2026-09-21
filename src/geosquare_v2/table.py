"""Pandas table readers and point-to-cell table adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from .boundary import BoundaryPredicate
from .conversion import cell_to_geometry
from .errors import ValidationError
from .facade import GeosquareService


def _require_pandas() -> Any:
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - exercised without table extra
        from .errors import TableDependencyError

        raise TableDependencyError(
            "table operations require the 'table' optional dependency group"
        ) from exc
    return pd


def read_table(source: Any, *, input_format: str | None = None, **read_options: Any) -> Any:
    """Read CSV, XLSX, or Parquet into a Pandas DataFrame."""
    pd = _require_pandas()
    if isinstance(source, pd.DataFrame):
        return source.copy()
    path = Path(source)
    format_name = (input_format or path.suffix.lstrip(".")).lower()
    if format_name in {"csv", "txt"}:
        return pd.read_csv(path, **read_options)
    if format_name in {"xlsx", "xls"}:
        return pd.read_excel(path, **read_options)
    if format_name in {"parquet", "pq"}:
        return pd.read_parquet(path, **read_options)
    raise ValidationError("input_format must be csv, xlsx, or parquet")


def _read_table_chunks(source: Any, *, input_format: str | None, chunksize: int, **read_options: Any) -> Iterator[Any]:
    pd = _require_pandas()
    if isinstance(source, pd.DataFrame):
        for start in range(0, len(source), chunksize):
            yield source.iloc[start : start + chunksize].copy()
        return
    path = Path(source)
    format_name = (input_format or path.suffix.lstrip(".")).lower()
    if format_name in {"csv", "txt"}:
        yield from pd.read_csv(path, chunksize=chunksize, **read_options)
        return
    yield read_table(path, input_format=format_name, **read_options)


def _validate_columns(frame: Any, columns: list[str]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValidationError(f"missing table columns: {missing}")


def table_to_cells(
    source: Any,
    service: GeosquareService,
    domain_code: str,
    level: int,
    *,
    input_format: str | None = None,
    longitude_column: str | None = "longitude",
    latitude_column: str | None = "latitude",
    x_column: str | None = None,
    y_column: str | None = None,
    keep_columns: list[str] | None = None,
    output_geometry: bool = False,
    geometry_crs: str = "grid",
    geometry_format: str = "wkt",
    boundary_policy: BoundaryPredicate | str | None = None,
    drop_outside_boundary: bool = False,
    boundary_match_column: str = "boundary_match",
    **read_options: Any,
) -> Any:
    """Add V2 cell fields to a point table while preserving selected source fields.

    Use either longitude/latitude columns or projected x/y columns. All input columns
    are retained by default. ``drop_outside_boundary`` only has an effect when a point
    boundary policy is supplied.
    """
    pd = _require_pandas()
    if not isinstance(service, GeosquareService):
        raise ValidationError("service must be a GeosquareService")
    frame = read_table(source, input_format=input_format, **read_options)
    if keep_columns is None:
        result = frame.copy()
    else:
        _validate_columns(frame, keep_columns)
        result = frame.loc[:, keep_columns].copy()

    context = service._context(domain_code)
    if (x_column is None) != (y_column is None):
        raise ValidationError("x_column and y_column must be supplied together")
    if x_column is not None and y_column is not None:
        _validate_columns(frame, [x_column, y_column])
        from .batch import encode_projected_pandas

        encoded = encode_projected_pandas(context.grid, frame, x_column, y_column, level)
        source_coordinates = list(zip(frame[x_column].tolist(), frame[y_column].tolist()))
        coordinate_mode = "projected"
    else:
        if longitude_column is None or latitude_column is None:
            raise ValidationError("provide longitude/latitude or projected x/y columns")
        _validate_columns(frame, [longitude_column, latitude_column])
        from .batch import encode_lonlat_pandas

        encoded = encode_lonlat_pandas(context.grid, frame, longitude_column, latitude_column, level)
        source_coordinates = list(zip(frame[longitude_column].tolist(), frame[latitude_column].tolist()))
        coordinate_mode = "lonlat"

    result["domain"] = encoded["domain"]
    result["level"] = encoded["level"]
    result["x_idx"] = encoded["x_idx"]
    result["y_idx"] = encoded["y_idx"]
    result["gid"] = encoded["gid"]
    result["uri"] = encoded["gid"].map(lambda gid: f"geosquare:v2:{domain_code}:{gid}")
    result["packed_id"] = encoded["packed_id"]

    if boundary_policy is not None:
        boundary = service._boundary(context)
        try:
            selected_boundary_policy = (
                boundary_policy
                if isinstance(boundary_policy, BoundaryPredicate)
                else BoundaryPredicate(boundary_policy)
            )
        except ValueError as exc:
            raise ValidationError("unknown point boundary policy") from exc
        if selected_boundary_policy is not BoundaryPredicate.COVERS_POINT:
            raise ValidationError("table_to_cells point filtering requires COVERS_POINT")
        if coordinate_mode == "lonlat":
            matches = [
                boundary.covers_lonlat(float(first), float(second), context.transformer)
                for first, second in source_coordinates
            ]
        else:
            matches = [boundary.covers_projected(float(first), float(second)) for first, second in source_coordinates]
        result[boundary_match_column] = matches
        if drop_outside_boundary:
            result = result.loc[result[boundary_match_column]].copy()

    if output_geometry:
        result["geometry"] = [
            cell_to_geometry(
                context.grid,
                gid,
                output_crs=geometry_crs,
                geometry_format=geometry_format,
            )
            for gid in result["gid"]
        ]
    return result


def table_to_cells_chunks(
    source: Any,
    service: GeosquareService,
    domain_code: str,
    level: int,
    *,
    chunksize: int = 100_000,
    **kwargs: Any,
) -> Iterator[Any]:
    """Stream point-table conversion in chunks."""
    input_format = kwargs.pop("input_format", None)
    for frame in _read_table_chunks(source, input_format=input_format, chunksize=chunksize):
        yield table_to_cells(
            frame,
            service,
            domain_code,
            level,
            input_format="csv",  # DataFrame input; format is ignored.
            **kwargs,
        )


def write_table(frame: Any, destination: str | Path, *, output_format: str | None = None, **write_options: Any) -> None:
    """Write a converted table to CSV, XLSX, or Parquet."""
    pd = _require_pandas()
    if not isinstance(frame, pd.DataFrame):
        raise ValidationError("frame must be a pandas.DataFrame")
    path = Path(destination)
    format_name = (output_format or path.suffix.lstrip(".")).lower()
    if format_name == "csv":
        frame.to_csv(path, index=False, **write_options)
    elif format_name in {"xlsx", "xls"}:
        frame.to_excel(path, index=False, **write_options)
    elif format_name in {"parquet", "pq"}:
        frame.to_parquet(path, index=False, **write_options)
    else:
        raise ValidationError("output_format must be csv, xlsx, or parquet")
