"""Build pinned Rofi extensions that distributions do not package."""
from pathlib import Path
import json
import os
import platform
import shutil
import subprocess
import tempfile


def _run(args, **kwargs):
    kwargs.setdefault('check', True)
    kwargs.setdefault('text', True)
    return subprocess.run(args, **kwargs)


def _command(*names):
    return next((name for name in names if shutil.which(name)), None)


def _have(*names):
    return all(shutil.which(name) for name in names)


def _download_rpm(package, directory):
    arch = platform.machine()
    _run(['dnf', 'download', '--quiet', '--forcearch', arch,
          '--destdir', str(directory), f'{package}.{arch}'])
    rpms = sorted(Path(directory).glob('*.rpm'))
    if not rpms:
        raise RuntimeError(f'dnf did not download {package}')
    return rpms[0]


def _extract_rpm(rpm, directory):
    rpm2cpio = _command('rpm2cpio')
    cpio = _command('cpio')
    if not rpm2cpio or not cpio:
        raise RuntimeError('rpm2cpio and cpio are required to extract Fedora packages')
    root = Path(directory) / 'root'
    root.mkdir(parents=True, exist_ok=True)
    extract = subprocess.Popen([rpm2cpio, str(rpm)], stdout=subprocess.PIPE)
    _run([cpio, '-idm', '--quiet'], cwd=root, stdin=extract.stdout)
    extract.wait()
    if extract.returncode:
        raise RuntimeError(f'cannot extract {rpm.name}')
    return root


def _fedora_root(package, cache):
    """Return an extracted package root, reusing the architecture cache."""
    arch = platform.machine()
    key = f'{package}.{arch}'
    marker = cache / key / '.complete'
    root = cache / key / 'root'
    if marker.is_file() and root.is_dir():
        return root
    shutil.rmtree(cache / key, ignore_errors=True)
    (cache / key).mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.maya-rpm-', dir=cache) as directory:
        rpm = _download_rpm(package, directory)
        root = _extract_rpm(rpm, cache / key)
    marker.write_text('')
    return root


def _pkg_config_env(root, env):
    pc = next((path for path in root.glob('usr/lib*/pkgconfig') if path.is_dir()), None)
    if pc is None:
        raise RuntimeError('package does not contain pkg-config metadata')
    include = root / 'usr/include'
    includes = [include]
    if include.is_dir():
        includes += [path for path in include.iterdir() if path.is_dir()]
    libdirs = [path for path in root.glob('usr/lib*') if path.is_dir()]
    env['PKG_CONFIG_PATH'] = f'{pc}:{env.get("PKG_CONFIG_PATH", "")}'.rstrip(':')
    flags = ' '.join(f'-I{path}' for path in includes)
    env['CFLAGS'] = f'{flags} {env.get("CFLAGS", "")}'.rstrip()
    env['CPPFLAGS'] = f'{flags} {env.get("CPPFLAGS", "")}'.rstrip()
    libs = ' '.join(f'-L{path}' for path in libdirs)
    env['LDFLAGS'] = f'{libs} {env.get("LDFLAGS", "")}'.rstrip()
    env['LIBRARY_PATH'] = ':'.join(
        [*(str(path) for path in libdirs), env.get('LIBRARY_PATH', '')]).rstrip(':')


def _rofi_dependencies(home, cache, warnings):
    env = dict(os.environ)
    pkg_config = shutil.which('pkg-config')
    if not pkg_config:
        warnings.append('Rofi extensions: install pkg-config, rofi-devel, json-glib-devel, meson and qalculate (qalc)')
        return None
    if _run([pkg_config, '--exists', 'rofi'], check=False).returncode != 0:
        if not _have('dnf', 'rpm2cpio', 'cpio'):
            warnings.append('Rofi extensions: install rofi-devel, json-glib-devel, meson and qalculate (qalc)')
            return None
        try:
            _pkg_config_env(_fedora_root('rofi-devel', cache), env)
        except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
            warnings.append(f'Rofi extensions: cannot prepare rofi-devel headers: {error}')
            return None
    if _run([pkg_config, '--exists', 'json-glib-1.0'], check=False).returncode != 0:
        if not _have('dnf', 'rpm2cpio', 'cpio'):
            warnings.append('Rofi extensions: install json-glib-devel and meson')
        else:
            try:
                json_root = _fedora_root('json-glib-devel', cache)
                _pkg_config_env(json_root, env)
                # The devel package's libjson-glib-1.0.so symlink needs the
                # runtime library in the same extracted prefix for linking.
                runtime_root = _fedora_root('json-glib', cache)
                runtime_lib = next(runtime_root.glob('usr/lib*/libjson-glib-1.0.so.0'))
                dev_lib = next(json_root.glob('usr/lib*/libjson-glib-1.0.so'))
                shutil.copy2(runtime_lib, dev_lib.parent / runtime_lib.name)
            except (OSError, RuntimeError, subprocess.CalledProcessError, StopIteration) as error:
                warnings.append(f'Rofi extensions: cannot prepare json-glib-devel headers: {error}')
    if not _have('meson', 'ninja', 'cc'):
        warnings.append('Rofi extensions: install meson, ninja, gcc and pkg-config')
        return None
    return env


def _ensure_qalc(home, cache, warnings):
    if _command('qalc'):
        return
    target = home / '.local/bin/qalc'
    if target.is_file() and os.access(target, os.X_OK):
        return
    if not _have('dnf', 'rpm2cpio', 'cpio'):
        warnings.append('rofi-calc: install qalculate so the qalc command is available')
        return
    try:
        root = _fedora_root('qalculate', cache)
        source = root / 'usr/bin/qalc'
        if not source.is_file():
            raise RuntimeError('qalculate package does not contain usr/bin/qalc')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        target.chmod(0o755)
        if _run([str(target), '-t', '2+2'], capture_output=True).returncode:
            raise RuntimeError('extracted qalc cannot run; install the qalculate package')
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        target.unlink(missing_ok=True)
        warnings.append(f'rofi-calc: {error}')


def _build_extension(spec, plugin_target, launcher_target, cache, env):
    """Build one pinned Rofi extension and install its plugin/launcher."""
    with tempfile.TemporaryDirectory(prefix='.maya-rofi-extension-', dir=cache) as directory:
        checkout = Path(directory) / 'checkout'
        _run(['git', 'init', '--quiet', str(checkout)])
        _run(['git', '-C', str(checkout), 'fetch', '--quiet', '--depth=1',
              spec['url'], spec['commit']])
        _run(['git', '-C', str(checkout), 'checkout', '--quiet', '--detach', 'FETCH_HEAD'])
        actual = subprocess.check_output(
            ['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != spec['commit']:
            raise RuntimeError(f"revision mismatch: {actual}")
        _run(['meson', 'setup', 'build'], cwd=checkout, env=env,
             stdout=subprocess.DEVNULL)
        _run(['meson', 'compile', '-C', 'build'], cwd=checkout, env=env,
             stdout=subprocess.DEVNULL)
        plugin = checkout / spec.get('build', f"build/src/{spec['plugin']}")
        if not plugin.is_file():
            raise RuntimeError(f"build did not produce {spec['plugin']}")
        plugin_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(plugin, plugin_target)
        plugin_target.chmod(0o755)
        if launcher_target:
            launcher = checkout / spec['launcher']
            if not launcher.is_file():
                raise RuntimeError("build did not produce the Rofi launcher")
            launcher_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(launcher, launcher_target)
            launcher_target.chmod(0o755)


def install(root, home):
    """Build pinned Rofi extensions; return non-fatal warnings."""
    warnings = []
    manifest = json.loads((root / 'dependencies.json').read_text())
    extensions = manifest['rofi_extensions']
    try:
        rofi_version = subprocess.check_output(['rofi', '-v'], text=True).strip()
    except OSError:
        warnings.append('Rofi extensions: install Rofi before building extensions')
        return warnings
    state_path = home / '.local/state/maya-dotfiles/rofi-extensions.json'
    state = {}
    try:
        state = json.loads(state_path.read_text())
    except (OSError, ValueError):
        pass
    if not isinstance(state, dict):
        state = {}
    cache = home / '.cache/maya-dotfiles/rofi-rpm'
    cache.mkdir(parents=True, exist_ok=True)
    env = None

    def build_env():
        nonlocal env
        if env is None:
            env = _rofi_dependencies(home, cache, warnings)
        return env

    calc = extensions.get('rofi-calc')
    calc_target = home / '.local/lib/rofi' / calc['plugin'] if calc else None
    calc_current = bool(calc and calc_target.is_file() and state.get('rofi-calc') == {
        'commit': calc['commit'], 'rofi': rofi_version})
    if calc and not calc_current:
        build = build_env()
        if build is not None:
            try:
                _build_extension(calc, calc_target, None, cache, build)
                state['rofi-calc'] = {'commit': calc['commit'], 'rofi': rofi_version}
            except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
                warnings.append(f'rofi-calc: build failed: {error}')
    if calc_target and calc_target.is_file():
        _ensure_qalc(home, cache, warnings)

    universal = extensions.get('rofi-universal')
    universal_target = (
        home / '.local/lib/rofi' / universal['plugin'] if universal else None)
    launcher_target = (
        home / '.local/bin' / Path(universal['launcher']).name if universal else None)
    universal_current = bool(
        universal and universal_target.is_file() and launcher_target.is_file()
        and state.get('rofi-universal') == {
            'commit': universal['commit'], 'rofi': rofi_version})
    if universal and not universal_current:
        build = build_env()
        if build is not None:
            try:
                _build_extension(universal, universal_target, launcher_target,
                                 cache, build)
                state['rofi-universal'] = {
                    'commit': universal['commit'], 'rofi': rofi_version}
            except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
                warnings.append(f'rofi-universal: build failed: {error}')

    if state:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, indent=2) + '\n')
    return warnings
