from types import NoneType
from typing import Annotated, Any, Optional, TypeVar

import pytest

from type_analyzer import MatchingTypesConfig, iter_matching_types, matching_types

_T = TypeVar("_T")


class _Parent: ...


class _Child(_Parent): ...


class _Left: ...


class _Right: ...


class _LeftAndRight(_Left, _Right): ...


class _GenericLeft[T]: ...


class _GenericRight[T]: ...


class _GenericLeftAndRight[T1, T2](_GenericLeft[T1], _GenericRight[T2]): ...


class _NestedGenericLeftAndRight[T1, T2](
    _GenericLeft[list[T1]],
    _GenericRight[list[T2]],
): ...


class _GenericChild[T](_GenericLeft[T]): ...


class _GenericGrandchild[T](_GenericChild[T]): ...


type _String = str

type _StringOr[T] = str | T

type _ListOf[T] = list[T]

type _NestedListOf[T] = _ListOf[T]


def test_iter_matching_types_with_shared_bases_returns_duplicates() -> None:
    config = MatchingTypesConfig(with_bases=True)

    types = list(iter_matching_types(_LeftAndRight, config))

    assert types == [_LeftAndRight, _Left, object, _Right, object]


@pytest.mark.parametrize(
    ("type_hint", "expected"),
    [
        (str, (str,)),
        (_Child, (_Child,)),
        (list[str], (list[str],)),
        (list[int | str], (list[int | str],)),
        (list[Annotated[int, "metadata"]], (list[int],)),
        (_String, (_String,)),
        (_T, (_T,)),
        (Annotated[str, "metadata"], (str,)),
        (str | int, (str, int)),
        (str | None, (str, NoneType)),
        (Optional[str], (str, NoneType)),  # noqa: UP045
        (Annotated[str | int, "metadata"] | None, (str, int, NoneType)),
    ],
)
def test_matching_types_with_default_config_returns_unpacked_types(
    type_hint: Any,
    expected: tuple[Any, ...],
) -> None:
    assert matching_types(type_hint) == expected


@pytest.mark.parametrize(
    ("type_hint", "expected"),
    [
        (None, ()),
        (NoneType, ()),
        (str | None, (str,)),
        (Optional[str], (str,)),  # noqa: UP045
    ],
)
def test_matching_types_with_ignore_none_returns_types_without_none(
    type_hint: Any,
    expected: tuple[Any, ...],
) -> None:
    config = MatchingTypesConfig(ignore_none=True)

    assert matching_types(type_hint, config) == expected


@pytest.mark.parametrize(
    ("type_hint", "expected"),
    [
        (str, (str,)),
        (list[str], (list[str], list)),
        (dict[str, int], (dict[str, int], dict)),
    ],
)
def test_matching_types_with_origin_returns_types_and_their_origin(
    type_hint: Any,
    expected: tuple[Any, ...],
) -> None:
    config = MatchingTypesConfig(with_origin=True)

    assert matching_types(type_hint, config) == expected


@pytest.mark.parametrize(
    ("type_hint", "expected"),
    [
        (_Child, (_Child, _Parent, object)),
        (_LeftAndRight, (_LeftAndRight, _Left, object, _Right)),
        (_GenericLeft[_T], (_GenericLeft[_T],)),  # type: ignore[valid-type]
        (
            _GenericLeftAndRight[str, int],
            (
                _GenericLeftAndRight[str, int],
                _GenericLeft[str],
                _GenericRight[int],
            ),
        ),
        (
            _NestedGenericLeftAndRight[str, int],
            (
                _NestedGenericLeftAndRight[str, int],
                _GenericLeft[list[str]],
                _GenericRight[list[int]],
            ),
        ),
        (
            _GenericGrandchild[int],
            (_GenericGrandchild[int], _GenericChild[int], _GenericLeft[int]),
        ),
    ],
)
def test_matching_types_with_bases_returns_types_and_their_bases(
    type_hint: Any,
    expected: tuple[Any, ...],
) -> None:
    config = MatchingTypesConfig(with_bases=True)

    assert matching_types(type_hint, config) == expected


def test_matching_types_with_bases_and_origin_returns_types_bases_and_origins() -> None:
    config = MatchingTypesConfig(with_bases=True, with_origin=True)

    types = matching_types(_GenericLeftAndRight[str, int], config)

    assert types == (
        _GenericLeftAndRight[str, int],
        _GenericLeftAndRight,
        _GenericLeft[str],
        _GenericLeft,
        _GenericRight[int],
        _GenericRight,
    )


@pytest.mark.parametrize(
    ("type_hint", "expected"),
    [
        (str, (str,)),
        (_String, (_String, str)),
        (_StringOr[int], (_StringOr[int], str, int)),
        (_NestedListOf[int], (_NestedListOf[int], _ListOf[int], list[int])),
    ],
)
def test_matching_types_with_type_alias_value_returns_types_and_alias_values(
    type_hint: Any,
    expected: tuple[Any, ...],
) -> None:
    config = MatchingTypesConfig(with_type_alias_value=True)

    assert matching_types(type_hint, config) == expected


def test_matching_types_with_bases_and_type_alias_value_returns_value_bases() -> None:
    config = MatchingTypesConfig(with_bases=True, with_type_alias_value=True)

    types = matching_types(_String, config)

    assert types == (_String, str, object)
