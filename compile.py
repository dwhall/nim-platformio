from os import makedirs, system, path
from shutil import copyfile
from pathlib import Path

Import("env")
prj_dir = Path(env.subst("$PROJECT_DIR"))
prj_src_dir = Path(env.subst("$PROJECT_SRC_DIR"))

def copy_files():
    """Copies a minimum set of files needed to compile
    if they do not already exist in the project.
    """
    files_to_copy = (
        ("nim.cfg", prj_dir),
        ("panicoverride.nim", prj_src_dir),
        ("main.nim", prj_src_dir),
    )
    for fn, dest in files_to_copy:
        if not path.exists(dest):
            makedirs(dest)
        if not path.exists(dest / fn):
            copyfile(Path().parent / fn, dest / fn)

def append_options_to_config_file():
    """Appends the PlatformIO platform support files path and cpu options
    to the config file if they are not already present
    """
    lib_deps_in_quotes = f'"{env.subst("$PROJECT_LIBDEPS_DIR/$PIOENV")}"'
    fwd_slash_lib_deps_in_quotes = lib_deps_in_quotes.replace("\\", "/")
    nimcache_dir_in_quotes = f'"{path.join(prj_src_dir, "nimcache")}"'
    fwd_slash_nimcache_dir_in_quotes = nimcache_dir_in_quotes.replace("\\", "/")
    options_to_append = (
        ("path", fwd_slash_lib_deps_in_quotes),
        ("cpu", _get_cpu(env.subst("$PIOPLATFORM"))),
        ("nimcache", fwd_slash_nimcache_dir_in_quotes),
    )
    fwd_slash_config_path = str(prj_dir / "nim.cfg").replace("\\", "/")
    file_lines = open(fwd_slash_config_path).readlines()
    config_file_contents = ''.join(file_lines)
    if "# END nim-platformio" not in config_file_contents:
        with open(fwd_slash_config_path, "a") as cfg_file:
            cfg_file.write("# BEGIN nim-platformio\n")
            for optn, val in options_to_append:
                if optn not in config_file_contents:
                    cfg_file.write(f"{optn}:{val}\n")
            cfg_file.write("# END nim-platformio\n")


def _get_cpu(pio_plat: str) -> str:
    """Returns the CPU type to give to the Nim compiler
    based on the PlatformIO platform setting.  Reference:
    https://docs.platformio.org/en/latest/platforms/index.html
    """
    DEFAULT_CPU = "arm"
    platform_cpu = {
        "atmelavr": "avr",
        "atmelmegaavr": "avr",
        "espressif32": "esp",
        "espressif8266": "esp",
        "riscv_gap": "riscv32",
        "sifive": "riscv32",
        "timsp430": "msp430",
    }
    return platform_cpu.get(pio_plat, DEFAULT_CPU)


def compile():
    """Calls the nim compiler on main.nim and with
    path and cpu flags derived from PlatformIO values.
    Returns the result from the system() call to the compiler.
    """
    prj_src_dir = Path(env.subst("$PROJECT_SRC_DIR"))
    return system(f"nim cpp {prj_src_dir / 'main'}")


copy_files()
append_options_to_config_file()
result = compile()
if result != 0:
    exit(result)
