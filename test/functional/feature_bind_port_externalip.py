#!/usr/bin/env python3
# Copyright (c) 2020 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""
Test that the proper port is used for -externalip=
"""

from test_framework.test_framework import BitcoinTestFramework, SkipTest
from test_framework.util import assert_equal

# We need to bind to a routable address for this test to exercise the relevant code.
# To set a routable IP address on the machine use:
# Linux:
# ifconfig lo:0 138.68.248.245/32 up  # to set up
# ifconfig lo:0 down  # to remove it, after the test
# FreeBSD:
# ifconfig lo0 138.68.248.245/32 alias  # to set up
# ifconfig lo0 138.68.248.245 -alias  # to remove it, after the test
addr = '138.68.248.245'

# array of tuples [arguments, expected port to be assumed for localaddresses]
expected = [
    [['-externalip=138.0.0.1',       '-port=20001'                               ], 20001],
    [['-externalip=138.0.0.1',       '-port=20002', '-bind={}'.format(addr)],       20002],
    [['-externalip=138.0.0.1',                      '-bind={}'.format(addr)],       11002],
    [['-externalip=138.0.0.1',       '-port=20003', '-bind={}:20004'.format(addr)], 20004],
    [['-externalip=138.0.0.1',                      '-bind={}:20005'.format(addr)], 20005],
    [['-externalip=138.0.0.1:20006', '-port=20007'                               ], 20006],
    [['-externalip=138.0.0.1:20008', '-port=20009', '-bind={}'.format(addr)],       20008],
    [['-externalip=138.0.0.1:20010',                '-bind={}'.format(addr)],       20010],
    [['-externalip=138.0.0.1:20011', '-port=20012', '-bind={}:20013'.format(addr)], 20011],
    [['-externalip=138.0.0.1:20014',                '-bind={}:20015'.format(addr)], 20014],
    [['-externalip=138.0.0.1',       '-port=20016', '-bind={}:20017'.format(addr),
                                               '-whitebind={}:20018'.format(addr)], 20017],
    [['-externalip=138.0.0.1',       '-port=20019',
                                               '-whitebind={}:20020'.format(addr)], 20020],
]

class BindPortTest(BitcoinTestFramework):
    def set_test_params(self):
        # Avoid any -bind= on the command line. Force the framework to avoid adding -bind=127.0.0.1.
        self.setup_clean_chain = True
        self.bind_to_localhost_only = False
        self.num_nodes = len(expected)

    def add_options(self, parser):
        parser.add_argument(
            "--forcerun", action='store_true', dest="forcerun",
            help="Run the test, assuming {} is configured on the machine".format(addr),
            default=False)

    def setup_nodes(self):
        args = []
        for t in expected:
            args.append(t[0])
        self.add_nodes(self.num_nodes, extra_args=args)
        self.start_nodes()

    def run_test(self):
        if not self.options.forcerun:
            raise SkipTest(
                "To run this test make sure that {} (a routable address) is assigned "
                "to one of the interfaces on this machine and rerun with --forcerun".format(addr))

        for i in range(len(expected)):
            expected_port = expected[i][1]
            found = False
            for local in self.nodes[i].getnetworkinfo()['localaddresses']:
                if local['address'] == '138.0.0.1':
                    assert_equal(local['port'], expected_port)
                    found = True
                    break
            assert(found)

if __name__ == '__main__':
    BindPortTest().main()
