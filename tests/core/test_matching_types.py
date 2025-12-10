from types import NoneType
from typing import Annotated, Optional, TypeVar

from type_analyzer import MatchingTypesConfig, matching_types


def test_matching_types_with_annotated() -> None:
    assert matching_types(Annotated[str, "metadata"]) == (str,)


def test_matching_types_with_union() -> None:
    assert matching_types(str | int) == (str, int)


def test_matching_types_with_optional() -> None:
    assert matching_types(str | None) == (str, NoneType)
    assert matching_types(Optional[str]) == (str, NoneType)


def test_matching_types_with_optional_and_ignore_none() -> None:
    config = MatchingTypesConfig(ignore_none=True)
    assert matching_types(str | None, config) == (str,)
    assert matching_types(Optional[str], config) == (str,)


def test_matching_types_with_class() -> None:
    class Class: ...

    config = MatchingTypesConfig(with_bases=True)
    assert matching_types(Class, config) == (Class, object)


def test_matching_types_with_generic_class() -> None:
    class A[T]: ...

    class B[T]: ...

    class C[T1, T2](A[T1], B[T2]): ...

    config = MatchingTypesConfig(with_bases=True)
    assert matching_types(C[str, int], config) == (C[str, int], A[str], B[int])


def test_matching_types_with_generic_class_and_nested_generics() -> None:
    class A[T]: ...

    class B[T]: ...

    class C[T1, T2](A[list[T1]], B[list[T2]]): ...

    config = MatchingTypesConfig(with_bases=True)
    assert matching_types(C[str, int], config) == (
        C[str, int],
        A[list[str]],
        B[list[int]],
    )


def test_matching_types_with_generic_class_and_type_var_generic() -> None:
    class Class[T]: ...

    _T = TypeVar("_T")

    config = MatchingTypesConfig(with_bases=True, with_origin=True)
    assert matching_types(Class[_T], config) == (Class[_T], Class)  # type: ignore[valid-type]


def test_matching_types_with_origin() -> None:
    config = MatchingTypesConfig(with_origin=True)
    assert matching_types(list[str], config) == (list[str], list)


def test_matching_types_with_type_alias() -> None:
    type String = str
    config = MatchingTypesConfig(with_type_alias_value=True)
    assert matching_types(String, config) == (String, str)


def test_matching_types_with_generic_type_alias() -> None:
    type StringOr[T] = str | T
    config = MatchingTypesConfig(with_type_alias_value=True)
    assert matching_types(StringOr[int], config) == (StringOr[int], str, int)


def test_matching_types_with_bases_and_type_alias() -> None:
    type String = str
    config = MatchingTypesConfig(with_bases=True, with_type_alias_value=True)
    assert matching_types(String, config) == (String, str, object)
