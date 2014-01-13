#!/usr/bin/env python

"""
Visualize demo of artificial LPU integration output.

Notes
-----
Generate demo output by running

python integration_demo.py
"""

import futures

import numpy as np
import matplotlib as mpl
mpl.use('agg')

import neurokernel.LPU.utils.visualizer as vis
import networkx as nx

nx.readwrite.gexf.GEXF.convert_bool = {'false':False, 'False':False,
                                        'true':True, 'True':True}

def run(out_name):
    V = vis.visualizer()
    
    V.add_LPU('./data/artificial_input_0.h5', LPU='Sensory')
    V.add_plot({'type':'waveform', 'ids': [[0]]}, 'input_Sensory')

    for i in [0, 1]:
        G = nx.read_gexf('./data/artificial_lpu_%s.gexf.gz' % i)
        neu_out = [k for k, n in G.node.items() if n['name'][:3] == 'out']
        
        V.add_LPU('artificial_output_%s_%s_spike.h5' % (i, out_name),
                  './data/artificial_lpu_%s.gexf.gz' % i,
                  'Artificial LPU %s' % i)
        V.add_plot({'type': 'raster',
                    'ids': {0: range(len(neu_out))},
                    #'yticks': range(1, 1+len(neu_out)),
                    #'yticklabels': range(len(neu_out))
                    },
                    'Artificial LPU %s' % i, 'Output')

    V._update_interval = 50
    V.rows = 3
    V.cols = 1
    V.fontsize = 18
    V.out_filename = 'artificial_output_%s.avi' % out_name
    V.codec = 'libtheora'
    V.dt = 0.0001
    V.xlim = [0, 1.0]
    V.run()

# Run the visualizations in parallel:
with futures.ProcessPoolExecutor() as executor:
    fs_dict = {}
    for out_name in ['un', 'co']:
        res = executor.submit(run, out_name)
        fs_dict[out_name] = res
    futures.wait(fs_dict.values())

    # Report any exceptions that may have occurred:
    for k in fs_dict:
        e = fs_dict[k].exception()
        if e:
            print '%s: %s' % (k, e)
