# type-analyzer

[![PyPI - Version](https://shieldcn.dev/pypi/v/type-analyzer.svg?color=3775A9&size=xs&variant=secondary)](https://pypi.org/project/type-analyzer)
[![PyPI - Downloads](https://shieldcn.dev/pypi/dm/type-analyzer.svg?color=3775A9&size=xs&variant=secondary)](https://pypistats.org/packages/type-analyzer)
[![GitHub Stars](https://shieldcn.dev/github/stars/100nm/type-analyzer.svg?size=xs&variant=secondary)](https://github.com/100nm/type-analyzer/stargazers)
[![CI](https://shieldcn.dev/github/ci/100nm/type-analyzer.svg?size=xs&variant=secondary&workflow=ci.yml)](https://github.com/100nm/type-analyzer/actions/workflows/ci.yml)
[![Ruff](https://shieldcn.dev/badge/code_style-Ruff-261230.svg?logo=ruff&size=xs&variant=secondary)](https://github.com/astral-sh/ruff)

Functions for introspecting Python type hints.

## Installation

⚠️ _Requires Python 3.12 or higher_

```bash
pip install type-analyzer
```

## Usage

### `matching_types`

`matching_types` returns every type a type hint matches, without duplicates. Unions
are unpacked into their members, and `Annotated` metadata is removed:

```python
from typing import Annotated

from type_analyzer import matching_types

matching_types(str | int)
# => (str, int)

matching_types(Annotated[str, "metadata"] | None)
# => (str, NoneType)

matching_types(list[Annotated[int, "metadata"]])
# => (list[int],)
```

### Options

`MatchingTypesConfig` adds more types to the result. Every option is disabled by
default:

| Option                  | Effect                                                   |
|-------------------------|----------------------------------------------------------|
| `ignore_none`           | Leaves out `None`.                                       |
| `with_bases`            | Adds the base classes, with their type arguments.        |
| `with_origin`           | Adds the origin of generic types (`list[str]` → `list`). |
| `with_type_alias_value` | Adds the value of type aliases.                          |

```python
from type_analyzer import MatchingTypesConfig, matching_types

# ----- ignore_none -----

config = MatchingTypesConfig(ignore_none=True)
matching_types(str | None, config)
# => (str,)

# ----- with_bases -----


class A[T]: ...


class B[T]: ...


class C[T1, T2](A[T1], B[T2]): ...


config = MatchingTypesConfig(with_bases=True)
matching_types(C[str, int], config)
# => (C[str, int], A[str], B[int])

# ----- with_origin -----

config = MatchingTypesConfig(with_origin=True)
matching_types(list[str], config)
# => (list[str], list)

# ----- with_type_alias_value -----

type StringOr[T] = str | T

config = MatchingTypesConfig(with_type_alias_value=True)
matching_types(StringOr[int], config)
# => (StringOr[int], str, int)
```

Options can be combined: `MatchingTypesConfig(with_bases=True, with_origin=True)`.

### `iter_matching_types`

`iter_matching_types` is the lazy counterpart of `matching_types`: it yields the
types one by one, and keeps the duplicates.

```python
from type_analyzer import MatchingTypesConfig, iter_matching_types


class Left: ...


class Right: ...


class Both(Left, Right): ...


config = MatchingTypesConfig(with_bases=True)
list(iter_matching_types(Both, config))
# => [Both, Left, object, Right, object]
```
