

from portage.tests.resolver.test_binpackage_selection import BinPkgSelectionTestCase
from portage.tests.resolver.ResolverPlayground import ResolverPlaygroundTestCase


# test packages.binary config file
class PackageBinaryTestCase(BinPkgSelectionTestCase):

    def testPackageBinaryLocal(self):
        ebuilds = self.pkgs_no_deps
        binpkgs = self.pkgs_no_deps

        user_config = {
            "package.binary": ("app-misc/foo ebuild",),
        }

        test_cases = (
            # no effect without --usepkg
            ResolverPlaygroundTestCase(
                self.pkg_atoms,
                success=True,
                mergelist=[
                    "app-misc/foo-1.0",
                    "app-misc/bar-1.0",
                    "app-misc/baz-1.0",
                ],
            ),
            # deselect foo with -*
            ResolverPlaygroundTestCase(
                self.pkg_atoms,
                success=True,
                options={"--usepkg": True},
                mergelist=[
                    "app-misc/foo-1.0",
                    "[binary]app-misc/bar-1.0",
                    "[binary]app-misc/baz-1.0",
                ],
            ),
            # combined with --usepkg-exclude
            ResolverPlaygroundTestCase(
                self.pkg_atoms,
                success=True,
                options={"--usepkg": True,
                         "--usepkg-exclude": ["baz"]},
                mergelist=[
                    "app-misc/foo-1.0",
                    "[binary]app-misc/bar-1.0",
                    "app-misc/baz-1.0",
                ],
            ),
            # combined with --usepkg-include
            ResolverPlaygroundTestCase(
                self.pkg_atoms,
                success=True,
                options={"--usepkg": True,
                         "--usepkg-include": ["baz"]},
                mergelist=[
                    "app-misc/foo-1.0",
                    "app-misc/bar-1.0",
                    "[binary]app-misc/baz-1.0",
                ],
            ),
        )

        self.runBinPkgSelectionTest(
            test_cases,
            binpkgs=binpkgs,
            ebuilds=ebuilds,
            user_config=user_config,
        )

    def testPackageBinaryRemote(self):
        ebuilds = self.pkgs_no_deps
        binpkgs = self.pkgs_no_deps

        user_config = {
            "package.binary": (
                "app-misc/foo ebuild",
                "app-misc/bar pkgdir",
            )
        }

        binrepos = {"test_binrepo": self.pkgs_no_deps}

        test_cases = (
            # no effect without --usepkg
            ResolverPlaygroundTestCase(
                self.pkg_atoms,
                success=True,
                mergelist=[
                    "app-misc/foo-1.0",
                    "app-misc/bar-1.0",
                    "app-misc/baz-1.0",
                ],
            ),
            # -remote to no effect without --getbinpkg
            ResolverPlaygroundTestCase(
                self.pkg_atoms,
                success=True,
                options={"--usepkg": True},
                mergelist=[
                    "app-misc/foo-1.0",
                    "[binary]app-misc/bar-1.0",
                    "[binary]app-misc/baz-1.0",
                ],
            ),
            # deselect app-misc-bar from binhost with -remote
            ResolverPlaygroundTestCase(
                self.pkg_atoms,
                success=True,
                options={"--getbinpkg": True},
                mergelist=[
                    "app-misc/foo-1.0",
                    "[binary]app-misc/bar-1.0",
                    "[binary,remote]app-misc/baz-1.0",
                ],
            ),
        )

        self.runBinPkgSelectionTest(
            test_cases,
            binpkgs=binpkgs,
            binrepos=binrepos,
            ebuilds=ebuilds,
            user_config=user_config,
        )
