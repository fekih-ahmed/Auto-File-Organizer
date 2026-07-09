import os
import shutil


RULES = {
    "pythoon": {"ext": (".py", ".ipynb", ".pyw")},
    "images": {"ext": (".jpeg", ".jpg", ".gif", ".png", ".webp",
                       ".bmp", ".tiff", ".tif", ".svg", ".ico",
                       ".heic", ".heif"),
               "prefix": ("WhatsApp",)},
    "videos": {"ext": (".mp4", ".mkv", ".avi", ".mov", ".wmv",
                       ".flv", ".webm", ".m4v", ".3gp")},
    "audio": {"ext": (".mp3", ".wav", ".flac", ".aac", ".ogg",
                      ".m4a", ".wma", ".opus")},
    "documents": {"ext": (".pdf", ".doc", ".docx", ".odt", ".rtf",
                          ".txt", ".md", ".pages")},
    "spreadsheets": {"ext": (".xls", ".xlsx", ".csv", ".ods", ".numbers")},
    "presentations": {"ext": (".ppt", ".pptx", ".odp", ".key")},
    "archives": {"ext": (".zip", ".rar", ".7z", ".tar", ".gz",
                         ".bz2", ".xz", ".tar.gz", ".tar.bz2")},
    "executables": {"ext": (".exe", ".msi", ".dmg", ".pkg", ".deb",
                            ".rpm", ".sh", ".bat", ".cmd", ".app")},
    "web": {"ext": (".html", ".htm", ".css", ".js", ".ts",
                    ".json", ".xml", ".yaml", ".yml")},
    "fonts": {"ext": (".ttf", ".otf", ".woff", ".woff2", ".eot")},
    "ebooks": {"ext": (".epub", ".mobi", ".azw", ".azw3", ".fb2")},
    "databases": {"ext": (".db", ".sqlite", ".sqlite3", ".sql",
                          ".mdb", ".accdb")},
    "torrents": {"ext": (".torrent",)},
    "others": {},  
}




def get_destination(filename: str) -> str | None:
    """Return the target folder name for *filename*, or None to skip."""
    name_lower = filename.lower()

    for folder, rule in RULES.items():
        if folder == "others":
            continue

       
        for ext in rule.get("ext", ()):
            if name_lower.endswith(ext):
                return folder

        
        for prefix in rule.get("prefix", ()):
            if filename.startswith(prefix):
                return folder

    return "others" 


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def safe_move(src: str, dst_dir: str) -> str:
    """Move *src* into *dst_dir*, renaming on collision. Returns final path."""
    basename = os.path.basename(src)
    dst = os.path.join(dst_dir, basename)

   
    if os.path.exists(dst):
        name, ext = os.path.splitext(basename)
        counter = 1
        while os.path.exists(dst):
            dst = os.path.join(dst_dir, f"{name} ({counter}){ext}")
            counter += 1

    shutil.move(src, dst)
    return dst




def organize(target_dir: str | None = None, dry_run: bool = False) -> None:
    """
    Organize files in *target_dir* (defaults to the directory of this script).

    Parameters
    ----------
    target_dir : str | None
        Folder to clean up. Defaults to the script's own directory.
    dry_run    : bool
        If True, only print what *would* happen — nothing is moved.
    """
    base = target_dir or os.path.dirname(os.path.realpath(__file__))
    base = os.path.abspath(base)

    moved = 0
    skipped = 0
    errors = 0

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Organizing: {base}\n")

    for filename in sorted(os.listdir(base)):
        src = os.path.join(base, filename)

       
        if os.path.isdir(src):
            continue
        if src == os.path.realpath(__file__):
            continue

        destination = get_destination(filename)
        if destination is None:
            skipped += 1
            continue

        dst_dir = os.path.join(base, destination)

        if dry_run:
            print(f"  {filename}  →  {destination}/")
            continue

        try:
            ensure_dir(dst_dir)
            final_path = safe_move(src, dst_dir)
            print(f"  ✓  {filename}  →  {os.path.relpath(final_path, base)}")
            moved += 1
        except Exception as exc:
            print(f"  ✗  {filename}  — ERROR: {exc}")
            errors += 1

    if not dry_run:
        print(f"\nDone — {moved} moved, {skipped} skipped, {errors} errors.\n")




if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Organize a downloads folder by file type."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=None,
        help="Folder to organize (default: folder containing this script)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without moving any files",
    )
    args = parser.parse_args()

    organize(target_dir=args.directory, dry_run=args.dry_run)