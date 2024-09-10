import pkgutil

def is_package_installed(package_name):
    return any(pkg.name == package_name for pkg in pkgutil.iter_modules())
