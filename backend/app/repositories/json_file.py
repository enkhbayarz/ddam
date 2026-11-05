from pathlib import Path

from pydantic import TypeAdapter


class JsonFile[T]:
    """Reads and writes a list of models in one JSON file."""

    def __init__(self, path: Path, item_type: type[T]) -> None:
        self._path = path
        self._adapter = TypeAdapter(list[item_type])

    def read(self) -> list[T]:
        if not self._path.exists():
            return []
        return self._adapter.validate_json(self._path.read_bytes())

    def write(self, items: list[T]) -> None:
        # Write to a temp file, then swap it in, so a crash mid-write
        # can never leave a half-written file behind.
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self._path.with_suffix(".tmp")
        temp_path.write_bytes(self._adapter.dump_json(items, indent=2))
        temp_path.replace(self._path)
