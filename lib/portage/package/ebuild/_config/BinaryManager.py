__all__ = ("BinaryManager",)


from portage import os
from portage.const import USER_CONFIG_PATH
from portage.util import grabdict_package


class BinaryManager:
    def __init__(self, config_root):
        path = os.path.join(config_root, USER_CONFIG_PATH, "package.select")
        self._binpkg_dict = grabdict_package(
            path,
            allow_repo=True,
            allow_wildcard=True,
            recursive=True,
        )

    def isSelected(self, pkg):
        matched = [a for a in self._binpkg_dict if a.match(pkg)]
        if not matched:
            return True

        binhosts = []
        flags = []
        for atom in matched:
            binhost_expand = False
            for token in self._binpkg_dict[atom]:
                if token == "BINHOST:":
                    binhost_expand = True
                elif binhost_expand or token.startswith("binhost_"):
                    binhosts.append(token.removeprefix("binhost_"))
                else:
                    flags.append(token)

        types = set()
        valid = ("ebuild", "pkgdir", "installed")
        for flag in flags:
            if flag == "*":
                types.update(valid)
            elif flag in valid:
                types.add(flag)
            else:
                # FIXME
                raise RuntimeError(f"Invalid flag: {flag}")

        if pkg.type_name in ("ebuild", "installed"):
            return pkg.type_name in flags
        else:
            if pkg.remote:
                return "*" in binhosts or pkg.binhost in binhosts
            else:
                return "pkgdir" in flags
