#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""
__author__ = 'Yuta Hayashibe' 
__version__ = ""
__copyright__ = ""
__license__ = "GPL v3"


import multiprocessing
# import Process, current_process, freeze_support
import sys

# make sockets pickable/inheritable
if sys.platform == 'win32':
    import multiprocessing.reduction

def serve_forever(server):
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

def runpool(server, address, number_of_processes):
    for i in range(number_of_processes-1):
        multiprocessing.Process(target=serve_forever, args=(server,)).start()
    serve_forever(server)


def main(opts):
    server_address = ('', opts.port)

    import os
    import web.base
    import web.correcter
    httpd = web.correcter.Server(opts, server_address, web.base.Server)
    static_dir = os.path.dirname( os.path.abspath( __file__ ) ) + "/web/static"

    if opts.root:
        os.chdir(opts.root)
    else:
        os.chdir(static_dir)

    ADDRESS = httpd.socket.getsockname()
    NUMBER_OF_PROCESSES = opts.process
    print 'Serving at http://%s:%d using %d worker processes' % \
          (ADDRESS[0], ADDRESS[1], NUMBER_OF_PROCESSES)
    print 'To exit press Ctrl-' + ['C', 'Break'][sys.platform=='win32']

    runpool(httpd, ADDRESS, NUMBER_OF_PROCESSES)



if __name__=='__main__':
    import optparse
    parser = optparse.OptionParser()
    parser.add_option('-p', '--port', dest = 'port', type='int', default=9000)
    parser.add_option('-P', '--process', dest = 'process', type='int', default=4)
    parser.add_option('-R', '--root', dest = 'root')

    parser.add_option('-m', dest = 'model_dir', help='Model directory')

#    parser.add_option('--index', dest = 'index', default)

    #for log
    parser.add_option('-l', '--log', dest='log', default='', help="Filename for log output",)
    parser.add_option("--debug", action="store_true", dest="debug", default=False)

    (opts, args) = parser.parse_args()

    main(opts)
