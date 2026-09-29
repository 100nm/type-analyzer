# type-analyzer

[![PyPI - Version](https://shieldcn.dev/pypi/v/type-analyzer.svg?color=3775A9&size=xs&variant=secondary)](https://pypi.org/project/type-analyzer)
[![PyPI - Downloads](https://shieldcn.dev/pypi/dm/type-analyzer.svg?color=3775A9&size=xs&variant=secondary)](https://pypistats.org/packages/type-analyzer)
[![GitHub Stars](https://shieldcn.dev/github/stars/100nm/type-analyzer.svg?size=xs&variant=secondary)](https://github.com/100nm/type-analyzer/stargazers)
[![CI](https://shieldcn.dev/github/ci/100nm/type-analyzer.svg?size=xs&variant=secondary&workflow=ci.yml)](https://github.com/100nm/type-analyzer/actions/workflows/ci.yml)
[![Ruff](https://shieldcn.dev/badge/code_style-Ruff-261230.svg?logo=ruff&size=xs&variant=secondary)](https://github.com/astral-sh/ruff)

## Installation

⚠️ _Requires Python 3.12 or higher_

```bash
pip install type-analyzer
```

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


class A[T]: ...


class B[T]: ...


class C[T1, T2](A[T1], B[T2]): ...


config = MatchingTypesConfig(with_bases=True)
matching_types(C[str, int], config)
# => (C[str, int], A[str], B[int])
```
