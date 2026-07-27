# Copyright 2010-2025 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

import os
import sys

from portage.dep import Atom
from portage.package.ebuild.doebuild import doebuild
from portage.package.ebuild.config import config
from portage.tests.resolver.ResolverPlayground import ResolverPlayground


class EbuildPlayground:
    """
    This class helps to create the necessary files on disk and
    the needed settings instances, etc, to test ebuild.sh. It
    leverages ResolverPlayground for much of this.
    """

    def __init__(
        self,
        ebuilds={},
        user_config={},
        distfiles={},
        patches={},
        # FIXME: profile, eclasses, eprefix, targetroot, debug?
    ):

        self.playground = ResolverPlayground(
            ebuilds=ebuilds,
            user_config=user_config,
            distfiles=distfiles,
            patches=patches,
        )

    def cleanup(self):
        self.playground.cleanup()

    def run(self, ebuild, phase):
        root = self.playground.eroot
        tree = "porttree"
        dbapi = self.playground.trees[root][tree].dbapi

        # FIXME: this essentially what ResolverPlayground._create_ebuilds() does
        #        so reuse that code
        atom = Atom(f"={ebuild}", allow_repo=True)
        repo = self.playground._get_repo_dir(atom.repo if atom.repo else "test_repo")
        ebuild = os.path.join(repo, atom.cp, atom.cpv.split("/")[1] + ".ebuild")

        settings = config(clone=self.playground.settings)

        result = doebuild(
            ebuild,
            phase,
            # FIXME: how safe is this? playground.settings still contains
            #        some things seeming to point at the host.
            #
            # CONFIG_PROTECT_MASK	/etc/env.d
            # CONFIG_PROTECT		/etc/
            # GENTOO_MIRRORS		https://distfiles.gentoo.org
            # RPMDIR			/var/cache/rpm
            #
            # are any of these absolute, or all relative to PORTAGE_ROOT ... ?
            # are any of these used by doebuild() ... ?
            settings=settings,
            mydbapi=dbapi,
            tree=tree,
            # FIXME: fd_pipes to capture output?
        )

        return EbuildPlaygroundResult(ebuild, result == 0, settings)

    def run_TestCase(self, test_case):
        if not isinstance(test_case, EbuildPlaygroundTestCase):
            raise TypeError("EbuildPlayground needs a EbuildPlaygroundTestCase")

        for phase in test_case.phases:
            result = self.run(test_case.ebuild, phase)
            if not test_case.compare_with_result(result):
                return


class EbuildPlaygroundTestCase:
    def __init__(self, ebuild, phases, success, **kwargs):
        self.ebuild = ebuild  # FIXME: generate full path to ebuild in playground
        self.phases = [phases] if isinstance(phases, str) else phases
        self.success = success
        self._checks = kwargs

    def compare_with_result(self, result):
        fail_msgs = []
        self.fail_msg = None
        self.test_success = True

        if self.success != result.success:
            pass # FIXME: fail_msgs.append()

        if "metadata" in self._checks:
            for k, v in self._checks["metadata"].items():
                if k not in result.metadata:
                    fail_msgs.append(f"{k} missing from metadata")
                    continue
                value = result.metadata[k].strip().decode()
                if value != v:
                    fail_msgs.append(f"{k} metadata value incorrect (expected: {v}, got: {value}")

        if "workdir" in self._checks:
            for f, content in self._checks["workdir"].items():
                if f not in result.workdir:
                    fail_msgs.append(f"Expected file '{f}' not found in WORKDIR")
                    continue
                if result.workdir[f] != content:
                    fail_msgs.append(f"File '{f}' in WORKDIR has incorrect content")

        if fail_msgs:
            self.fail_msg = "\n".join(fail_msgs)
            self.test_success = False
        return self.test_success


class EbuildPlaygroundResult:
    def __init__(self, ebuild, success, settings):
        self.ebuild = ebuild
        self.success = success

        # FIXME: recursive? use pathlib? does this already exist?
        def _files_dict(path):
            result = {f: None for f in os.listdir(path)}
            for name in result:
                with open(os.path.join(path, name), 'rb') as f:
                    result[name] = f.read()
            return result

        pv = os.path.basename(ebuild).rsplit(os.path.extsep, maxsplit=1)[0]

        self.metadata = _files_dict(os.path.join(settings["PORTAGE_BUILDDIR"], "build-info"))
        self.workdir = _files_dict(os.path.join(settings["WORKDIR"], pv))
