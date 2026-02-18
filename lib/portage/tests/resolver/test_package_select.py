from portage.tests.resolver.test_binpackage_selection import (
    BinPkgSelectionTestCase,
    with_build_id,
)
from portage.tests.resolver.ResolverPlayground import ResolverPlaygroundTestCase


# test packages.binary config file
class PackageSelectTestCase(BinPkgSelectionTestCase):

    def testPackageSelectType(self):
        ebuilds = self.pkgs_no_deps
        binpkgs = self.pkgs_no_deps

        binrepos = {"test_binrepo": self.pkgs_no_deps}

        user_config = {
            "package.select": (
                "app-misc/foo ebuild",
                "app-misc/bar pkgdir",
                "app-misc/baz binhost_test_binrepo",
            )
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
            # app-misc/foo from ebuild, even under --usepkg
            ResolverPlaygroundTestCase(
                ["foo", "bar"],
                success=True,
                options={"--usepkg": True},
                mergelist=[
                    "app-misc/foo-1.0",
                    "[binary]app-misc/bar-1.0",
                ],
            ),
            # app-misc/bar from pkgdir, even under --getbinpkg
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
            # --usepkg-exclude must leave all required binpkgs in bintree
            ResolverPlaygroundTestCase(
                self.pkg_atoms,
                success=True,
                options={"--getbinpkg": True, "--usepkg-exclude": ["foo"]},
                mergelist=[
                    "app-misc/foo-1.0",
                    "[binary]app-misc/bar-1.0",
                    "[binary,remote]app-misc/baz-1.0",
                ],
            ),
            ResolverPlaygroundTestCase(
                ["foo", "bar"],
                success=False,
                options={"--usepkg": True, "--usepkg-exclude": ["bar"]},
            ),
            ResolverPlaygroundTestCase(
                self.pkg_atoms,
                success=False,
                options={"--getbinpkg": True, "--usepkg-exclude": ["bar"]},
            ),
            # --usepkg-include must leave all required binpkgs in bintree
            ResolverPlaygroundTestCase(
                self.pkg_atoms,
                success=True,
                options={"--getbinpkg": True, "--usepkg-include": ["bar", "baz"]},
                mergelist=[
                    "app-misc/foo-1.0",
                    "[binary]app-misc/bar-1.0",
                    "[binary,remote]app-misc/baz-1.0",
                ],
            ),
            ResolverPlaygroundTestCase(
                ["foo", "bar"],
                success=False,
                options={"--usepkg": True, "--usepkg-include": ["foo"]},
            ),
            ResolverPlaygroundTestCase(
                self.pkg_atoms,
                success=False,
                options={"--getbinpkg": True, "--usepkg-include": ["foo"]},
            ),
        )

        self.runBinPkgSelectionTest(
            test_cases,
            binpkgs=binpkgs,
            binrepos=binrepos,
            ebuilds=ebuilds,
            user_config=user_config,
        )

    def testPackageSelectBinhost(self):
        pkgs_no_deps_b1 = with_build_id(self.pkgs_no_deps, "1")
        pkgs_no_deps_b2 = with_build_id(self.pkgs_no_deps, "2")

        ebuilds = self.pkgs_no_deps
        binpkgs = pkgs_no_deps_b1 + pkgs_no_deps_b2

        binrepos = {
            "test_binrepo": pkgs_no_deps_b1,
            "other_binrepo": pkgs_no_deps_b2,
        }

        user_config = {
            "binrepos.conf": (
                "[test_binrepo]",
                "priority=1",
                "[other_binrepo]",
                "priority=2",
            )
        }

        test_cases = {
            (
                "app-misc/foo BINHOST: test_binrepo",
                "app-misc/bar BINHOST: other_binrepo",
                "app-misc/baz BINHOST: other_binrepo",
            ): (
                # use only the specific binrepos in package.select
                ResolverPlaygroundTestCase(
                    self.pkg_atoms,
                    success=True,
                    options={"--getbinpkg": True},
                    mergelist=[
                        "[binary,remote]app-misc/foo-1.0-1",
                        "[binary,remote]app-misc/bar-1.0-2",
                        "[binary,remote]app-misc/baz-1.0-2",
                    ],
                ),
            ),
            (
                "app-misc/foo binhost_other_binrepo",
                "app-misc/bar binhost_test_binrepo",
                "app-misc/baz binhost_test_binrepo",
            ): (
                # equivalent syntax to above
                ResolverPlaygroundTestCase(
                    self.pkg_atoms,
                    success=True,
                    options={"--getbinpkg": True},
                    mergelist=[
                        "[binary,remote]app-misc/foo-1.0-2",
                        "[binary,remote]app-misc/bar-1.0-1",
                        "[binary,remote]app-misc/baz-1.0-1",
                    ],
                ),
            ),
            (
                "app-misc/foo BINHOST: *",
                "app-misc/bar BINHOST: test_binrepo",
                "app-misc/baz BINHOST: other_binrepo",
            ): (
                # any binhost for app-misc/foo (by above binhost priority)
                ResolverPlaygroundTestCase(
                    self.pkg_atoms,
                    success=True,
                    options={"--getbinpkg": True},
                    mergelist=[
                        "[binary,remote]app-misc/foo-1.0-1",
                        "[binary,remote]app-misc/bar-1.0-1",
                        "[binary,remote]app-misc/baz-1.0-2",
                    ],
                ),
            ),
        }

        self.runBinPkgSelectionTestUserConfig(
            "package.select",
            test_cases,
            binpkgs=binpkgs,
            binrepos=binrepos,
            ebuilds=ebuilds,
            user_config=user_config,
        )
