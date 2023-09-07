# Contributing

OpenRPC Client Generator is open source and open to feedback and contributions from
the community!

## Requirements

- [Poetry](https://python-poetry.org/docs/)
- [Black](https://github.com/psf/black/)
- [pre-commit](https://pre-commit.com/)

## Getting Started

Fork or clone this repository, then run the following.

```shell
cd openrpc-client-generator
poetry shell
poetry install
pre-commit install
pre-commit run
```

Start hacking!

## Pull Requests

- An [issue](https://gitlab.com/mburkard/openrpc-client-generator/-/issues)
  should be made for any substantial changes.
- Commit messages should follow the
  [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
  specification.

### Commit Custom Scopes
- cs - Commit changes C# generation.
- kt - Commit changes Kotlin generation.
- py - Commit changes Python generation.
- ts - Commit changes TypeScript generation.
