import os
import re
import subprocess
import sys
from pathlib import Path
import pwd, grp, os


class JavaCompileError(Exception):
    pass


def _detect_package(content: str) -> str | None:
    m = re.search(r"^\s*package\s+([\w.]+)\s*;", content, re.MULTILINE)
    return m.group(1) if m else None


def _detect_main_class(content: str) -> str | None:
    m = re.search(
        r"public\s+class\s+(\w+)\b[\s\S]*?public\s+static\s+void\s+main\s*\(\s*String",
        content,
        re.MULTILINE,
    )
    return m.group(1) if m else None


def find_and_replace_main_class(java_file: Path) -> str:
    content = java_file.read_text(encoding="utf-8")

    package_name = _detect_package(content)
    current_class = _detect_main_class(content)
    if not current_class:
        print("Main method not found", file=sys.stderr)
        sys.exit(1)

    desired_class = java_file.stem
    if current_class != desired_class:
        content = re.sub(
            rf"public\s+class\s+{current_class}\b",
            f"public class {desired_class}",
            content,
            count=1,
        )
        java_file.write_text(content, encoding="utf-8")
        print(f"Renamed class {current_class} → {desired_class}")

    return f"{package_name}.{desired_class}" if package_name else desired_class




def _run(cmd: list[str]):
    print("$", " ".join(cmd))
    return subprocess.run(cmd, capture_output=True, text=True)


def compile_java(source: Path, out_dir: Path):
    out_dir.mkdir(exist_ok=True)

    for enc in ("UTF-8", "UTF8", None):
        cmd = ["javac"]
        if enc:
            cmd += ["-encoding", enc]
        cmd += ["-d", str(out_dir), str(source)]
        proc = _run(cmd)
        if proc.returncode == 0:
            print("Compilation succeeded")
            return
        if "unsupported encoding" not in proc.stderr:
            print("Compile error:\n" + proc.stderr, file=sys.stderr)
            sys.exit(1)

    print("Compile error:\n" + proc.stderr, file=sys.stderr)
    sys.exit(1)


def create_jar(jar_path: Path, main_class: str, classes_dir: Path):
    if jar_path.exists():
        jar_path.unlink()
    cmd = ["jar", "cfe", str(jar_path), main_class, "-C", str(classes_dir), "."]
    proc = _run(cmd)
    if proc.returncode != 0:
        print("jar error:\n" + proc.stderr, file=sys.stderr)
        sys.exit(1)
    print(f"Created {jar_path.relative_to(jar_path.parent)}")




def main():
    if len(sys.argv) != 2:
        print("Usage: python3 java_compile.py <File.java>")
        sys.exit(1)

    src = Path(sys.argv[1]).resolve()
    if src.suffix != ".java":
        print("Error: file must have .java extension", file=sys.stderr)
        sys.exit(1)
    if not src.exists():
        print(f"Error: {src} not found", file=sys.stderr)
        sys.exit(1)


    script_dir = Path(__file__).parent.resolve()

    main_class = find_and_replace_main_class(src)

    build_dir = script_dir / "build"
    compile_java(src, build_dir)

    jar_path = script_dir / f"{src.stem}.jar"
    create_jar(jar_path, main_class, build_dir)


    verify = subprocess.run(["jar", "tf", str(jar_path)],
                            capture_output=True, text=True)
    if verify.returncode != 0:
        print("Jar verification failed:\n", verify.stderr, file=sys.stderr)
        sys.exit(1)
    print("Jar contains:", verify.stdout.splitlines()[:5], "...")

    uid = pwd.getpwnam("user").pw_uid
    gid = grp.getgrnam("user").gr_gid

    os.chown(jar_path, uid, gid)
    jar_path.chmod(0o555)


if __name__ == "__main__":
    main()
