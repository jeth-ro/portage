# Copyright 2010-2025 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

import gzip
import hashlib

from portage.tests.resolver.ResolverPlayground import PlaygroundTestData
from portage.tests.ebuild.EbuildPlayground import (
    EbuildPlayground,
    EbuildPlaygroundTestCase,
)
from portage.tests.ebuild.test_phase_unpack import EbuildPhaseTestCase


class EbuildPreparePhaseTestCase(EbuildPhaseTestCase):
    def testPreparePhase(self):
        ebuilds = {
            "app-misc/foo-1.0": {
                "EAPI": 6,
                "SRC_URI": "http://example.com/foo-1.0.tar",
#                "SRC_URI": "http://example.com/foo-1.0.gz",
            },
        }

        payload = b"foo\n"
        distfiles = {
            # FIXME: the path prefix needs to match the ebuild name and
            #        so perhaps PlaygroundTestData should handle it
            "foo-1.0.tar": PlaygroundTestData("foo-1.0.tar", {"foo-1.0/file": b"foo\n"}),
#            "foo-1.0.gz": gzip.compress(payload)
        }

        patches = {
            "app-misc/foo": {
                "user.patch": (
                    b"--- a/file 1970-01-01 00:00:00.00000000 +0000\n"
                    b"+++ b/file 1970-01-01 00:00:00.00000000 +0000\n"
                    b"@@ -1 +1 @@\n"
                    b"+bar\n"
                    b"-foo\n"
                )
            }
        }

        # confirm prepare phase applies user patches to WORKDIR files
        test_cases = (
            EbuildPlaygroundTestCase(
                "app-misc/foo-1.0",
                "prepare",
                success=True,
                workdir={"file": b"bar\n"}
            ),
        )

        self.runEbuildPhaseTest(
            test_cases,
            ebuilds=ebuilds,
            distfiles=distfiles,
            patches=patches,
        )

    def testPreparePhaseUserPatches(self):
        ebuilds = {
            "app-misc/foo-1.0": {
                "EAPI": 6,
                "SRC_URI": "http://example.com/foo-1.0.tar",
#                "SRC_URI": "http://example.com/foo-1.0.gz",
            },
        }

        payload = b"foo\n"
        distfiles = {
            # FIXME: the path prefix needs to match the ebuild name and
            #        so perhaps PlaygroundTestData should handle it
            "foo-1.0.tar": PlaygroundTestData("foo-1.0.tar", {"foo-1.0/file": b"foo\n"}),
#            "foo-1.0.gz": gzip.compress(payload)
        }

        patches = {
            "app-misc/foo": {
                "00-user.patch": (
                    b"--- a/file 1970-01-01 00:00:00.00000000 +0000\n"
                    b"+++ b/file 1970-01-01 00:00:00.00000000 +0000\n"
                    b"@@ -1 +1 @@\n"
                    b"+bar\n"
                    b"-foo\n"
                ),
                "01-user.patch": (
                    b"--- a/file 1970-01-01 00:00:00.00000000 +0000\n"
                    b"+++ b/file 1970-01-01 00:00:00.00000000 +0000\n"
                    b"@@ -1 +1 @@\n"
                    b"+baz\n"
                    b"-bar\n"
                ),
            }
        }

        hashes = lambda e: {f: hashlib.sha256(p).hexdigest() for f, p in patches[e].items()}
        total = "".join(hashes("app-misc/foo").values()).encode()

        digests = "\n".join(f"{h} {f}" for f, h in hashes("app-misc/foo").items())

        test_cases = (
            # confirm prepare phase applies user patches and generates expected metadata
            EbuildPlaygroundTestCase(
                "app-misc/foo-1.0",
                "prepare",
                success=True,
                workdir={"file": b"baz\n"},
                metadata={
                    "user_patch.digests": digests,
                    "USER_PATCHES": hashlib.sha256(total).hexdigest(),
                },
            ),
        )

        self.runEbuildPhaseTest(
            test_cases,
            ebuilds=ebuilds,
            distfiles=distfiles,
            patches=patches,
        )
