from pathlib import Path

def print_tree(root_path: str):
    root = Path(root_path)

    if not root.exists():
        print(f"Pfad existiert nicht: {root}")
        return

    if not root.is_dir():
        print(f"Pfad ist kein Ordner: {root}")
        return

    print(root.name)

    def walk(directory: Path, prefix=""):
        entries = sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))

        for index, entry in enumerate(entries):
            is_last = index == len(entries) - 1
            connector = "└── " if is_last else "├── "
            print(prefix + connector + entry.name)

            if entry.is_dir():
                extension = "    " if is_last else "│   "
                walk(entry, prefix + extension)

    walk(root)

if __name__ == "__main__":
    pfad = input("Ordnerpfad eingeben: ").strip()
    print_tree(pfad)