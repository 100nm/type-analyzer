from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from types import NoneType, UnionType, get_original_bases
from typing import (
    Annotated,
    Any,
    Generic,
    Self,
    TypeAliasType,
    TypeVar,
    Union,
    get_args,
    get_origin,
)


@dataclass(repr=False, eq=False, frozen=True, kw_only=True, slots=True)
class MatchingTypesConfig:
    ignore_none: bool = field(default=False)
    with_bases: bool = field(default=False)
    with_origin: bool = field(default=False)
    with_type_alias_value: bool = field(default=False)


@dataclass(repr=False, eq=False, frozen=True, slots=True)
class _TypeHint:
    value: Any
    origin: Any

    @property
    def args(self) -> tuple[Any, ...]:
        return get_args(self.value)

    @property
    def generics(self) -> Mapping[TypeVar, Any]:
        parameters = getattr(self.origin, "__parameters__", ())
        return dict(zip(parameters, self.args))

    @property
    def is_none(self) -> bool:
        return self.value in (None, NoneType)

    @property
    def is_union(self) -> bool:
        return self.origin is Union or isinstance(self.value, UnionType)

    @property
    def target(self) -> Any:
        return self.value if self.origin is None else self.origin

    def apply_generics(self, generics: Mapping[TypeVar, Any]) -> Self:
        if isinstance(self.value, TypeVar):
            return self.from_value(generics.get(self.value, self.value))

        if self.origin is None:
            return self

        if self.origin is Annotated:
            return self.from_value(self.args[0]).apply_generics(generics)

        args = tuple(
            self.from_value(arg).apply_generics(generics).value for arg in self.args
        )

        if self.is_union:
            return self.from_value(Union[*args])

        return self.from_value(self.origin[*args])

    @classmethod
    def from_value(cls, value: Any) -> Self:
        return cls(value, get_origin(value))


_empty_config = MatchingTypesConfig()


def iter_matching_types(
    type_hint: Any,
    /,
    config: MatchingTypesConfig | None = None,
) -> Iterator[Any]:
    config = config or _empty_config
    return _iter_matching_types((type_hint,), config, {})


def matching_types(
    type_hint: Any,
    /,
    config: MatchingTypesConfig | None = None,
) -> tuple[Any, ...]:
    return tuple(dict.fromkeys(iter_matching_types(type_hint, config)))


def _iter_bases(type_hint: _TypeHint, config: MatchingTypesConfig) -> Iterator[Any]:
    try:
        bases = get_original_bases(type_hint.target)
    except TypeError:
        return

    yield from _iter_matching_types(bases, config, type_hint.generics)


def _iter_matching_types(
    type_hints: Sequence[Any],
    config: MatchingTypesConfig,
    generics: Mapping[TypeVar, Any],
) -> Iterator[Any]:
    for value in type_hints:
        type_hint = _TypeHint.from_value(value)

        if type_hint.origin is Generic:
            continue

        yield from _iter_type_hint_matching_types(
            type_hint.apply_generics(generics),
            config,
        )


def _iter_type_alias_value(
    type_hint: _TypeHint,
    config: MatchingTypesConfig,
) -> Iterator[Any]:
    type_alias = type_hint.target

    if not isinstance(type_alias, TypeAliasType):
        return

    values = (type_alias.__value__,)
    yield from _iter_matching_types(values, config, type_hint.generics)


def _iter_type_hint_matching_types(
    type_hint: _TypeHint,
    config: MatchingTypesConfig,
) -> Iterator[Any]:
    if config.ignore_none and type_hint.is_none:
        return

    if type_hint.is_union:
        yield from _iter_matching_types(type_hint.args, config, {})
        return

    yield type_hint.value

    if config.with_origin and type_hint.origin is not None:
        yield type_hint.origin

    if config.with_bases:
        yield from _iter_bases(type_hint, config)

    if config.with_type_alias_value:
        yield from _iter_type_alias_value(type_hint, config)
