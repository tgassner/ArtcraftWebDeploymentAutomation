import fnmatch
import pathlib
import shutil
import zipfile
import requests

# === Global standards for all Artcraft projects ===
OWNER = "storytold"
ASSET_FILTER = "*-web-*.zip"
BASE_WEB_DIR = pathlib.Path("/var/www")
BASE_ARTCRAFT_DIR = BASE_WEB_DIR / "artcraft"

# The repository / project names
PROJECT_REPOS = [
    "vectorcraft",
    "cadcraft",
    "photocraft",
    "lightcraft",
    "filmcraft",
    "effectcraft",
    "designcraft",
    "figcraft",
    "pdfcraft",
    "soundcraft",
    "wordcraft",
    "gridcraft",
    "deckcraft",
]


def check_and_deploy(repo):
  base_dir = BASE_ARTCRAFT_DIR / repo / "releases"
  current_link = BASE_WEB_DIR / repo

  print(f"Checking project: {OWNER}/{repo}...")

  url = f"https://api.github.com/repos/{OWNER}/{repo}/releases/latest"
  response = requests.get(url)
  if response.status_code != 200:
    print(
        f"  [Error] Failed to fetch release for {repo}"
        f" (Status: {response.status_code})"
    )
    return

  data = response.json()
  tag_name = data.get("tag_name")

  # Find matching asset
  asset_url = None
  for asset in data.get("assets", []):
    name = asset["name"]
    # Check if asset matches the naming convention (e.g. "vectorcraft-web-0.17.0.zip")
    if fnmatch.fnmatch(name, ASSET_FILTER) and name.endswith(".zip"):
      asset_url = asset["browser_download_url"]
      print(f"  [Info] Matching web asset found: {name}")
      break

  if not tag_name or not asset_url:
    print(f"  [Warning] No matching release or asset found for {repo}.")
    return

  target_dir = base_dir / tag_name

  if target_dir.exists():
    print(f"  [Info] {repo} is already up to date (version {tag_name}).")
    return

  print(f"  [Update] New release found for {repo}: {tag_name}. Starting...")
  target_dir.mkdir(parents=True, exist_ok=True)
  zip_path = target_dir / "release.zip"

  # Download ZIP
  print(f"Downloading from {asset_url}...")
  r = requests.get(asset_url)
  zip_path.write_bytes(r.content)

  # Unpack ZIP into a temporary subdirectory
  print("Unpacking archive...")
  extract_temp_dir = target_dir / "_extracted"
  extract_temp_dir.mkdir(exist_ok=True)

  with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(extract_temp_dir)
  zip_path.unlink()

  # Clean up wrapper directory structure (flattening GitHub structure)
  items = list(extract_temp_dir.iterdir())
  if len(items) == 1 and items[0].is_dir():
    # If a wrapper directory exists, move its contents directly to target_dir
    inner_dir = items[0]
    for child in inner_dir.iterdir():
      shutil.move(str(child), str(target_dir))
    inner_dir.rmdir()
  else:
    # If files were archived without a wrapper folder
    for child in extract_temp_dir.iterdir():
      shutil.move(str(child), str(target_dir))

  extract_temp_dir.rmdir()

  relative_target = pathlib.Path("artcraft") / repo / "releases" / tag_name

  # Switch symlink
  temp_link = current_link.with_suffix(".tmp")
  if temp_link.is_symlink() or temp_link.exists():
    temp_link.unlink()

  temp_link.symlink_to(relative_target)
  temp_link.replace(current_link)

  print(f"  [Success] {repo} successfully updated to {tag_name}!")

  # Cleanup (keep last 3 versions)
  cleanup_old_releases(base_dir, keep=3)


def cleanup_old_releases(base_dir, keep=3):
  if not base_dir.exists():
    return
  releases = sorted(
      [d for d in base_dir.iterdir() if d.is_dir()],
      key=lambda x: x.stat().st_mtime,
      reverse=True,
  )
  if len(releases) > keep:
    for old_release in releases[keep:]:
      print(f"  [Cleanup] Deleting old version: {old_release.name}")
      for f in old_release.glob("**/*"):
        if f.is_file():
          f.unlink()
      old_release.rmdir()


if __name__ == "__main__":
  print("=== Starting automatic Artcraft deployment run ===")
  for repo in PROJECT_REPOS:
    try:
      check_and_deploy(repo)
    except Exception as e:
      print(f"  [Fatal Error] Failed for {repo}: {e}")
  print("=== Run finished ===")
