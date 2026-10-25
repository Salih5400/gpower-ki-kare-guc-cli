"""Command line adapter for :mod:`gpower_clone.engine`."""

from __future__ import annotations

import json
import math
import re
import sys

from .engine import a_priori, post_hoc


_DECIMAL = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
_INTEGER = re.compile(r"^[+-]?\d+$")
_KNOWN = {"test", "mode", "w", "alpha", "power", "df", "n_total"}


class InputError(Exception):
    def __init__(self, code: str):
        self.code = code


def _error(code: str) -> int:
    sys.stdout.write(json.dumps({"error": code}, separators=(",", ":")) + "\n")
    return 2


def _parse_args(argv: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    i = 0
    while i < len(argv):
        token = argv[i]
        if not token.startswith("--") or token == "--":
            raise InputError("UNKNOWN_PARAM")
        key_value = token[2:].split("=", 1)
        key = key_value[0].replace("-", "_")
        if key not in _KNOWN:
            raise InputError("UNKNOWN_PARAM")
        if key in values:
            raise InputError("INVALID_VALUE")
        if len(key_value) == 2:
            value = key_value[1]
        else:
            i += 1
            if i >= len(argv) or argv[i].startswith("--"):
                raise InputError("MISSING_PARAM")
            value = argv[i]
        values[key] = value
        i += 1
    return values


def _number(values: dict[str, str], name: str, integer: bool = False) -> int | float:
    if name not in values:
        raise InputError("MISSING_PARAM")
    raw = values[name]
    pattern = _INTEGER if integer else _DECIMAL
    if not pattern.fullmatch(raw):
        raise InputError("INVALID_VALUE")
    try:
        parsed = int(raw) if integer else float(raw)
    except (ValueError, OverflowError):
        raise InputError("INVALID_VALUE") from None
    if not integer and not math.isfinite(parsed):
        raise InputError("INVALID_VALUE")
    return parsed


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    try:
        values = _parse_args(argv)
        if "test" not in values or "mode" not in values:
            raise InputError("MISSING_PARAM")
        if values["test"] != "chi2-contingency":
            raise InputError("UNSUPPORTED")
        mode = values["mode"]
        if mode not in {"a-priori", "post-hoc"}:
            raise InputError("UNSUPPORTED")

        required = {"w", "alpha", "power", "df"} if mode == "a-priori" else {"w", "alpha", "n_total", "df"}
        extra = set(values) - {"test", "mode"} - required
        if extra:
            raise InputError("UNKNOWN_PARAM")
        if not required.issubset(values):
            raise InputError("MISSING_PARAM")

        w = _number(values, "w")
        alpha = _number(values, "alpha")
        df = _number(values, "df", integer=True)
        if w <= 0 or not 0 < alpha < 1 or df < 1:
            raise InputError("OUT_OF_RANGE")

        if mode == "a-priori":
            requested_power = _number(values, "power")
            if not 0 < requested_power < 1:
                raise InputError("OUT_OF_RANGE")
            result = a_priori(w, alpha, requested_power, df)
        else:
            n_total = _number(values, "n_total", integer=True)
            if n_total < 2:
                raise InputError("OUT_OF_RANGE")
            result = post_hoc(w, alpha, n_total, df)
        sys.stdout.write(json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n")
        return 0
    except InputError as exc:
        return _error(exc.code)
    except ArithmeticError:
        return _error("NO_SOLUTION")
    except (OverflowError, ValueError):
        return _error("OUT_OF_RANGE")


if __name__ == "__main__":
    raise SystemExit(main())
