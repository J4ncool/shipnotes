# Shipnotes

Shipnotes turns Git history into a clean Markdown release note draft. It groups [Conventional Commits](https://www.conventionalcommits.org/) into sections, highlights breaking changes, and works offline with Python's standard library and Git.

## Install

Requires Python 3.9+ and Git.

```bash
python -m pip install .
```

## Usage

Create notes for commits after the previous release tag through `HEAD`:

```bash
shipnotes --since v1.2.0
```

Choose an end tag and save the result:

```bash
shipnotes --since v1.2.0 --until v1.3.0 --output CHANGELOG-draft.md
```

Run it against another repository:

```bash
shipnotes ../my-project --since v1.2.0 --title "Version 1.3.0"
```

Without `--since`, Shipnotes summarizes the available history. Output goes to the terminal unless `--output` is provided.

## Commit format

Recognized types include `feat`, `fix`, `perf`, `docs`, `refactor`, `build`, `ci`, `test`, and `chore`. Scope is optional:

```text
feat(parser): support nested lists
fix: handle empty configuration
feat(api)!: remove the deprecated endpoint
```

A commit body line beginning with `BREAKING CHANGE:` is also highlighted. Nonconventional subjects are preserved under **Other changes**. The generated notes are a draft; review them before publishing.

## Contributing

Issues and pull requests are welcome. Keep changes focused, explain the user impact, and include examples in the README when behavior changes. Please use Conventional Commit messages where practical.

## License

MIT. See [LICENSE](LICENSE).
