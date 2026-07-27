# Copyright 2010-2025 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

import gzip

from portage.tests import TestCase
from portage.tests.ebuild.EbuildPlayground import (
    EbuildPlayground,
    EbuildPlaygroundTestCase,
)


class EbuildPhaseTestCase(TestCase):
    def runEbuildPhaseTest(self, test_cases, **kwargs):
        playground = EbuildPlayground(**kwargs)

        try:
            for test_case in test_cases:
                playground.run_TestCase(test_case)
                self.assertEqual(test_case.test_success, True, test_case.fail_msg)
        finally:
            playground.cleanup()


class EbuildUnpackPhaseTestCase(EbuildPhaseTestCase):
    def testUnpackPhase(self):

        ebuilds = {
            "app-misc/foo-1.0": {"SRC_URI": "http://example.com/foo-1.0.gz"},
#            "app-misc/foo-1.0": PlaygroundTestData("foo-1.0.ebuild"),
            "app-misc/bar-1.0": {},
        }

        payload = b"foobar"
        distfiles = {
            "foo-1.0.gz": gzip.compress(payload)
#            "foo-1.0.tar.gz": PlaygroundTestData("foo-1.0.tar.gz"),
        }

        # confirm unpack phase produces expected files in WORKDIR
        test_cases = (
            EbuildPlaygroundTestCase(
                "app-misc/foo-1.0",
                "unpack",
                success=False, # FIXME: .gz payload has no dir structure
                workdir={"foo-1.0": payload},
            ),
        )

        self.runEbuildPhaseTest(
            test_cases,
            ebuilds=ebuilds,
            distfiles=distfiles
        )
