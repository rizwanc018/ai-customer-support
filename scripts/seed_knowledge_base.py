"""Load knowledge_base/*.md into the knowledge_base table.

Each file is one section; each `## ` heading is one entry. Rerunning updates
existing rows (and overwrites edits made elsewhere).
"""

from pathlib import Path

from app import db


def parse(path: Path) -> list[tuple[str, str, str]]:
    section = path.stem
    blocks = path.read_text().split("\n## ")[1:]  # drop the "# Title" preamble
    entries = []
    for block in blocks:
        title, _, content = block.partition("\n")
        entries.append((section, title.strip(), content.strip()))
    return entries


if __name__ == "__main__":
    with db.connect() as conn:
        for path in sorted(Path("knowledge_base").glob("*.md")):
            entries = parse(path)
            for section, title, content in entries:
                conn.execute(
                    """
                    insert into knowledge_base (section, title, content)
                    values (%s, %s, %s)
                    on conflict (section, title) do update
                      set content = excluded.content, updated_at = now()
                    """,
                    (section, title, content),
                )
            print(f"{path.stem}: {len(entries)} entries")
