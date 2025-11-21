from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from types import NoneType, UnionType, get_original_bases
from typing import (
    Annotated,
    Any,
    Generic,
    TypeAliasType,
    TypeVar,
    Union,
    get_args,
    get_origin,
)


@dataclass(repr=False, eq=False, frozen=True, kw_only=True, slots=True)
class MatchingTypesConfig:
    ignore_none: bool = field(default=False)
    with_mro: bool = field(default=False)
    with_origin: bool = field(default=False)
    with_type_alias_value: bool = field(default=False)


def matching_types(
    type_hint: Any,
    /,
    config: MatchingTypesConfig | None = None,
) -> tuple[Any, ...]:
    return tuple(
        dict.fromkeys(
            _iter_matching_types(
                (type_hint,),
                config,
            ),
        ),
    )


def _get_bases(type_hint: Any, origin: Any) -> tuple[Any, ...]:
    target = type_hint if origin is None else origin

    try:
        return get_original_bases(target)
    except TypeError:
        return ()


def _get_generics(type_hint: Any, origin: Any) -> Mapping[TypeVar, Any]:
    args = get_args(type_hint)
    parameters = getattr(origin, "__parameters__", ())
    return dict(zip(parameters, args))


def _is_type_var(type_hint: Any) -> bool:
    return isinstance(type_hint, TypeVar)


def _is_none(type_hint: Any) -> bool:
    return type_hint in (None, NoneType)


def _iter_matching_types(
    type_hints: Sequence[Any],
    /,
    config: MatchingTypesConfig | None = None,
    params: Mapping[TypeVar, Any] | None = None,
) -> Iterator[Any]:
    config = config or MatchingTypesConfig()

    if params is None:
        params = {}

    for type_hint in type_hints:
        if config.ignore_none and _is_none(type_hint):
            continue

        if _is_type_var(type_hint):
            yield params[type_hint]
            continue

        origin = get_origin(type_hint)

        if origin is Generic:
            continue

        if unpacked_types := _unpack_types(type_hint, origin):
            yield from _iter_matching_types(unpacked_types, config, params)
            continue

        if origin is None:
            yield type_hint

        else:
            iter_args = (
                params[arg] if _is_type_var(arg) else arg for arg in get_args(type_hint)
            )
            yield origin[*iter_args]

            if config.with_origin:
                yield origin

        if config.with_mro and (bases := _get_bases(type_hint, origin)):
            generics = _get_generics(type_hint, origin)
            yield from _iter_matching_types(bases, config, generics)

        if config.with_type_alias_value:
            if isinstance(origin, TypeAliasType):
                values = (origin.__value__,)
                generics = _get_generics(type_hint, origin)
                yield from _iter_matching_types(values, config, generics)

            elif isinstance(type_hint, TypeAliasType):
                values = (type_hint.__value__,)
                yield from _iter_matching_types(values, config)


def _unpack_types(type_hint: Any, origin: Any) -> Sequence[Any]:
    if origin is Union or isinstance(type_hint, UnionType):
        return get_args(type_hint)

    elif origin is Annotated:
        return get_args(type_hint)[:1]

    return ()
