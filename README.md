# type-analyzer

[![CI](https://github.com/100nm/type-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/100nm/type-analyzer)
[![PyPI - Version](https://img.shields.io/pypi/v/type-analyzer.svg?color=blue)](https://pypi.org/project/type-analyzer)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/type-analyzer.svg?color=blue)](https://pypistats.org/packages/type-analyzer)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Quick start

### matching_types

```python
from type_analyzer import MatchingTypesConfig, matching_types

# ----- Union type -----

matching_types(str | int)
# => (str, int)

# ----- Generic type alias -----

type StringOr[T] = str | T

config = MatchingTypesConfig(with_type_alias_value=True)
matching_types(StringOr[int], config)
# => (StringOr[int], str, int)

# ----- Generic classes -----

class A[T]: 
    ...

class B[T]: 
    ...

class C[T1, T2](A[T1], B[T2]):
    ...

config = MatchingTypesConfig(with_mro=True)
matching_types(C[str, int], config)
# => (C[str, int], A[str], B[int])
```
