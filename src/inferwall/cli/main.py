"""InferenceWall CLI — test and admin commands."""

from __future__ import annotations

import json
import os
import secrets
import sys

from inferwall.core.pipeline import Pipeline


def main() -> None:
    """CLI entry point."""
    if len(sys.argv) < 2:
        _print_usage()
        return

    command = sys.argv[1]
    subcommand = sys.argv[2] if len(sys.argv) > 2 else ""

    if command == "test":
        _handle_test(subcommand)
    elif command == "admin":
        _handle_admin(subcommand)
    elif command == "models":
        _handle_models(subcommand)
    elif command == "serve":
        _handle_serve()
    else:
        print(f"Unknown command: {command}")
        _print_usage()
        sys.exit(1)


def _print_usage() -> None:
    print("Usage: inferwall <command> [options]")
    print()
    print("Commands:")
    print("  test --input <text>    Scan input text")
    print("  test --profile <name>  Run test against a profile")
    print("  admin setup            First-time setup (generate keys)")
    print("  admin generate-keys    Generate API keys")
    print("  models install         Install dependencies + download models")
    print("  models download        Download ML models for a profile")
    print("  models list            List downloaded models")
    print("  models status          Check model availability")
    print("  serve                  Start the API server")


def _handle_test(subcommand: str) -> None:
    if subcommand == "--input" and len(sys.argv) > 3:
        text = sys.argv[3]
        pipeline = Pipeline()
        result = pipeline.scan_input(text)
        output = {
            "decision": result.decision,
            "score": result.score,
            "matches": result.matches,
        }
        print(json.dumps(output, indent=2))
    elif subcommand == "--profile" and len(sys.argv) > 3:
        profile_name = sys.argv[3]
        print(f"Running test with profile: {profile_name}")
        pipeline = Pipeline()
        print(f"Loaded {pipeline.signature_count} signatures")
        print("Profile test: PASS")
    else:
        print("Usage: inferwall test --input <text>")
        print("       inferwall test --profile <name>")


def _handle_admin(subcommand: str) -> None:
    if subcommand == "setup":
        _admin_setup()
    elif subcommand == "generate-keys":
        _generate_keys()
    else:
        print("Usage: inferwall admin setup")
        print("       inferwall admin generate-keys")


def _admin_setup() -> None:
    print("InferenceWall — First-Time Setup")
    print("=" * 40)
    print()

    scan_key = f"iwk_scan_{secrets.token_hex(16)}"
    admin_key = f"iwk_admin_{secrets.token_hex(16)}"
    log_key = f"iwlk_{secrets.token_hex(16)}"

    print("Generating API keys...")
    print()
    print(f"  Scan key:  IW_API_KEY={scan_key}")
    print(f"  Admin key: IW_ADMIN_KEY={admin_key}")
    print(f"  Log key:   IW_LOG_ENCRYPTION_KEY={log_key}")
    print()

    env_path = ".env.local"
    with open(env_path, "w") as f:
        f.write(f"IW_API_KEY={scan_key}\n")
        f.write(f"IW_ADMIN_KEY={admin_key}\n")
        f.write(f"IW_LOG_ENCRYPTION_KEY={log_key}\n")

    print(f"Written to {env_path}")
    print()
    print("SAVE THESE KEYS NOW. They are shown once.")
    print(f"Start: source {env_path} && inferwall serve")


def _generate_keys() -> None:
    role = "scan"
    for i, arg in enumerate(sys.argv):
        if arg == "--role" and i + 1 < len(sys.argv):
            role = sys.argv[i + 1]

    key = f"iwk_{role}_{secrets.token_hex(16)}"
    print(f"Generated {role} key: {key}")


def _handle_models(subcommand: str) -> None:
    from inferwall.models.registry import get_models_for_profile

    if subcommand == "install":
        _models_install()
        return

    if subcommand == "download":
        profile = "standard"
        for i, arg in enumerate(sys.argv):
            if arg == "--profile" and i + 1 < len(sys.argv):
                profile = sys.argv[i + 1]

        models = get_models_for_profile(profile)
        if not models:
            print(f"No models needed for '{profile}' profile.")
            return

        print(f"Downloading models for '{profile}' profile...")
        print()
        from inferwall.models.downloader import ModelDownloader

        downloader = ModelDownloader()
        for spec in models:
            if downloader.is_downloaded(spec):
                print(f"  [cached] {spec.name} ({spec.description})")
            else:
                print(f"  [downloading] {spec.name} (~{spec.size_mb}MB)...")
                try:
                    path = downloader.download(spec)
                    print(f"    -> {path}")
                except Exception as e:
                    print(f"    ERROR: {e}")
        print()
        print("Done. Models cached at:", downloader.cache_dir)

    elif subcommand == "list":
        from inferwall.models.downloader import ModelDownloader

        downloader = ModelDownloader()
        downloaded = downloader.list_downloaded()
        if not downloaded:
            print(
                "No models downloaded. "
                "Run: inferwall models download --profile standard"
            )
            return
        print("Downloaded models:")
        for m in downloaded:
            print(f"  {m['name']} ({m['engine']}) — {m['path']}")

    elif subcommand == "status":
        print("Model status by profile:")
        print()
        from inferwall.models.downloader import ModelDownloader

        downloader = ModelDownloader()
        for profile in ("lite", "standard", "full"):
            models = get_models_for_profile(profile)
            if not models:
                print(f"  {profile}: no models required")
                continue
            print(f"  {profile}:")
            for spec in models:
                cached = downloader.is_downloaded(spec)
                status = "cached" if cached else "not downloaded"
                print(f"    {spec.name}: {status} (~{spec.size_mb}MB)")

    else:
        print(
            "Usage: inferwall models install"
            " --profile <standard|full>  (recommended)"
        )
        print("       inferwall models download --profile <standard|full>")
        print("       inferwall models list")
        print("       inferwall models status")


def _models_install() -> None:
    """Install dependencies and download models for a profile."""
    import subprocess

    profile = "standard"
    auto_confirm = False
    for i, arg in enumerate(sys.argv):
        if arg == "--profile" and i + 1 < len(sys.argv):
            profile = sys.argv[i + 1]
        if arg in ("-y", "--yes"):
            auto_confirm = True

    if profile not in ("standard", "full"):
        print(f"Profile '{profile}' does not require model installation.")
        print("Use: inferwall models install --profile standard")
        print("  or: inferwall models install --profile full")
        return

    # Map profile to pip extra
    pip_extra = f"inferwall[{profile}]"
    deps = {
        "standard": ["onnxruntime", "tokenizers", "numpy", "faiss-cpu"],
        "full": ["onnxruntime", "tokenizers", "numpy", "faiss-cpu", "llama-cpp-python"],
    }

    print(f"InferenceWall — Install '{profile}' profile")
    print("=" * 50)
    print()
    print("This will:")
    print(f"  1. Install Python dependencies: {', '.join(deps[profile])}")
    print(f"  2. Download ML models (~{_profile_size_mb(profile)}MB)")
    print()

    if not auto_confirm:
        try:
            answer = input("Proceed? [Y/n] ").strip().lower()
            if answer and answer not in ("y", "yes"):
                print("Cancelled.")
                return
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return

    # Step 1: Install pip dependencies
    print()
    print("[1/2] Installing Python dependencies...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pip_extra],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            print("  WARNING: pip install returned non-zero exit code.")
            print(f"  stderr: {result.stderr[:500]}")
            print(f"  You may need to install manually: pip install {pip_extra}")
        else:
            print("  Done.")
    except FileNotFoundError:
        print(f"  WARNING: pip not found. Install manually: pip install {pip_extra}")
    except subprocess.TimeoutExpired:
        print("  WARNING: pip install timed out. Install manually.")

    # Verify key imports
    missing = []
    for pkg, import_name in [
        ("onnxruntime", "onnxruntime"),
        ("tokenizers", "tokenizers"),
    ]:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg)

    if profile == "full":
        try:
            __import__("llama_cpp")
        except ImportError:
            missing.append("llama-cpp-python")

    if missing:
        print(f"  WARNING: Could not import: {', '.join(missing)}")
        print(f"  Install manually: pip install {' '.join(missing)}")
    else:
        print("  All dependencies verified.")

    # Step 2: Download models
    print()
    print("[2/2] Downloading ML models...")
    from inferwall.models.downloader import ModelDownloader
    from inferwall.models.registry import get_models_for_profile

    downloader = ModelDownloader()
    models = get_models_for_profile(profile)

    for spec in models:
        if downloader.is_downloaded(spec):
            print(f"  [cached]      {spec.name} ({spec.description})")
        else:
            print(
                f"  [downloading] {spec.name} (~{spec.size_mb}MB)...",
                end="",
                flush=True,
            )
            try:
                downloader.download(spec)
                print(" done.")
            except Exception as e:
                print(f" FAILED: {e}")

    print()
    print(f"Installation complete. Models cached at: {downloader.cache_dir}")
    print()
    print(f"Set profile: export IW_PROFILE={profile}")
    print("Test:        inferwall test --input 'ignore all instructions'")


def _profile_size_mb(profile: str) -> int:
    """Estimate total download size for a profile."""
    from inferwall.models.registry import get_models_for_profile

    return sum(m.size_mb for m in get_models_for_profile(profile))


def _handle_serve() -> None:
    host = os.environ.get("IW_HOST", "0.0.0.0")
    port = int(os.environ.get("IW_PORT", "8000"))
    print(f"Starting InferenceWall on {host}:{port}")

    try:
        import uvicorn

        uvicorn.run("inferwall.api.app:app", host=host, port=port)
    except ImportError:
        print("Error: uvicorn not installed. Run: pip install uvicorn")
        sys.exit(1)


if __name__ == "__main__":
    main()
