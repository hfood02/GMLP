"""
    Purpose:
        Convert deepmd input file format to train.in of nep.
        The structure of the input directory is as follows:
          Type:1 (has virial)
            deepmd/init.000/
            ├── set.000
            │   ├── box.npy
            │   ├── coord.npy
            │   ├── energy.npy
            │   ├── force.npy
            │   └── virial.npy
            ├── type.raw
            └── type_map.raw
          Type:2 (no virial)
            deepmd/init.001/
            ├── set.000
            │   ├── box.npy
            │   ├── coord.npy
            │   ├── energy.npy
            │   └── force.npy
            ├── type.raw
            └── type_map.raw
    An example:
        https://github.com/Kick-H/nep_deepmd_mutual_conversion
    Ref:
        dpdata: https://github.com/deepmodeling/dpdata
    Run:
        python nep2xyz.py deepmd
    Author:
        Ke Xu <twtdq(at)qq.com>
"""

import os
import sys
import glob
import numpy as np

def convervirial(invirial):

    vxx = invirial[0,0]
    vxy = invirial[0,1]
    vzx = invirial[0,2]
    vyy = invirial[1,1]
    vyz = invirial[1,2]
    vzz = invirial[2,2]

    return [vxx, vyy, vzz, vxy, vyz, vzx]

def vec2volume(cells):
    va = cells[:3]
    vb = cells[3:6]
    vc = cells[6:]
    return np.dot(va, np.cross(vb,vc))

def cond_load_data(fname) :
    tmp = None
    if os.path.isfile(fname) :
        tmp = np.load(fname)
    return tmp

def load_type(folder, type_map=None) :
    data = {}
    data['atom_types'] \
        = np.loadtxt(os.path.join(folder, 'type.raw'), ndmin=1).astype(int)
    ntypes = np.max(data['atom_types']) + 1
    data['atom_numbs'] = []
    for ii in range (ntypes) :
        data['atom_numbs'].append(np.count_nonzero(data['atom_types'] == ii))
    data['atom_names'] = []
    # if find type_map.raw, use it
    if os.path.isfile(os.path.join(folder, 'type_map.raw')) :
        with open(os.path.join(folder, 'type_map.raw')) as fp:
            my_type_map = fp.read().split()
    # else try to use arg type_map
    elif type_map is not None:
        my_type_map = type_map
    # in the last case, make artificial atom names
    else:
        my_type_map = []
        for ii in range(ntypes) :
            my_type_map.append('Type_%d' % ii)
    assert(len(my_type_map) >= len(data['atom_numbs']))
    for ii in range(len(data['atom_numbs'])) :
        data['atom_names'].append(my_type_map[ii])

    return data

def load_set(folder) :
    cells = np.load(os.path.join(folder, 'box.npy'))
    coords = np.load(os.path.join(folder, 'coord.npy'))
    eners  = cond_load_data(os.path.join(folder, 'energy.npy'))
    forces = cond_load_data(os.path.join(folder, 'force.npy'))
    virs   = cond_load_data(os.path.join(folder, 'virial.npy'))
    return cells, coords, eners, forces, virs

def to_system_data(folder):
    # data is empty
    data = load_type(folder)
    data['orig'] = np.zeros([3])
    data['docname'] = folder
    sets = sorted(glob.glob(os.path.join(folder, 'set.*')))
    all_cells = []
    all_coords = []
    all_eners = []
    all_forces = []
    all_virs = []
    for ii in sets:
        cells, coords, eners, forces, virs = load_set(ii)
        nframes = np.reshape(cells, [-1,3,3]).shape[0]
        all_cells.append(np.reshape(cells, [nframes,3,3]))
        all_coords.append(np.reshape(coords, [nframes,-1,3]))
        if eners is not None:
            eners = np.reshape(eners, [nframes])
        if eners is not None and eners.size > 0:
            all_eners.append(np.reshape(eners, [nframes]))
        if forces is not None and forces.size > 0:
            all_forces.append(np.reshape(forces, [nframes,-1,3]))
        if virs is not None and virs.size > 0:
            all_virs.append(np.reshape(virs, [nframes,3,3]))
    data['frames'] = nframes
    data['cells'] = np.concatenate(all_cells, axis = 0)
    data['coords'] = np.concatenate(all_coords, axis = 0)
    if len(all_eners) > 0 :
        data['energies'] = np.concatenate(all_eners, axis = 0)
    if len(all_forces) > 0 :
        data['forces'] = np.concatenate(all_forces, axis = 0)
    if len(all_virs) > 0:
        data['virials'] = np.concatenate(all_virs, axis = 0)
    if os.path.isfile(os.path.join(folder, "nopbc")):
        data['nopbc'] = True
    return data

def read_multi_deepmd(folder):

    data_multi = {}
    for i, fi in enumerate(os.listdir(folder)):
        if os.path.isdir(os.path.join(folder, fi)):
            ifold = os.path.join(folder, fi)
            idata = to_system_data(ifold)
            if 'virials' in idata and len(idata['virials']) == idata['frames']:
                idata['has_virial'] = np.ones((idata['frames']), dtype=bool)
                #print(idata['frames'],len(idata['virials']), idata['has_virial'])
            else:
                idata['has_virial'] = np.zeros((idata['frames']), dtype=bool)
                #print(idata['frames'],idata['has_virial'])
            data_multi[i] = idata

    nframes = np.sum([data_multi[i]['frames'] for i in data_multi])

    data = {}
    data['nframe'] = nframes
    data['docname'] = ['' for i in range(nframes)]
    data['atom_numbs'] = np.zeros((data['nframe']))
    data['has_virial'] = np.zeros((data['nframe']))
    data['energies'] = np.zeros((data['nframe']))
    data['virials'] = np.zeros((data['nframe'], 6))
    data['cells'] = np.zeros((data['nframe'], 9))
    data['volume'] = np.zeros((data['nframe']))
    data['atom_types'] = {}
    data['coords'] = {}
    data['forces'] = {}


    ifr = -1
    for i in data_multi:

        #atom_types = [data_multi[i]['atom_names'][j] for j in data_multi[i]['atom_types']]

        for j in range(data_multi[i]['frames']):

            ifr += 1
            data['atom_numbs'][ifr] = len(data_multi[i]['atom_types'])
            data['has_virial'][ifr] = data_multi[i]['has_virial'][j]
            data['energies'][ifr] = data_multi[i]['energies'][j]
            if data['has_virial'][ifr]:
                data['virials'][ifr] = convervirial(data_multi[i]['virials'][j])
            data['cells'][ifr] = np.reshape(data_multi[i]['cells'][j],9)
            data['volume'][ifr] = vec2volume(data['cells'][ifr])
            #data['atom_types'][ifr] = atom_types
            data['atom_types'][ifr] = data_multi[i]['atom_types']
            data['coords'][ifr] = data_multi[i]['coords'][j]
            data['forces'][ifr] = data_multi[i]['forces'][j]
            data['docname'][ifr] = data_multi[i]['docname']

    return data


def check_data(data):

    print('Nframes:', data['nframe'])
    for i in range(data['nframe']):
        print(i, data['docname'][i])

        print('    atom_numbs', int(data['atom_numbs'][i]), end=' ')
        #print('has_virial', int(data['has_virial'][i]))
        #print('energies', data['energies'][i])
        #print('virials', len(data['virials'][i]))
        #print('volume', data['volume'][i])
        #print('cells', len(data['cells'][i]))
        print('atom_types', len(data['atom_types'][i]))
        print('    coords', len(data['coords'][i]), end=' ')
        print('forces', len(data['forces'][i]))

def dump (folder, data):
    os.makedirs(folder, exist_ok = True)

    fout = open(os.path.join(folder, 'train.in'), 'w')

    outstr = str(data['nframe']) + '\n'
    for i in range(data['nframe']):
        outstr=outstr+str(int(data['atom_numbs'][i]))+' '+str(int(data['has_virial'][i]))+'\n'
    fout.write(outstr)

    for i in range(data['nframe']):
        outstr = ''
        if data['has_virial'][i]:
            outstr=outstr+str(data['energies'][i])+' '
            outstr=outstr+' '.join(map(str, data['virials'][i]))+'\n'
        else:
            outstr=outstr+str(data['energies'][i])+'\n'
        outstr=outstr+' '.join(map(str, data['cells'][i]))+'\n'
        for j in range(int(data['atom_numbs'][i])):
            outstr=outstr+str(int(data['atom_types'][i][j]+1))+' '
            outstr=outstr+' '.join(map(str, data['coords'][i][j]))+' '
            outstr=outstr+' '.join(map(str, data['forces'][i][j]))+'\n'
        fout.write(outstr)

    fout.close()


def main():

    instr = sys.argv[1]

    data = read_multi_deepmd('./'+instr)
    #check_data(data)
    dump('./nep', data)

if __name__ == "__main__":
    main()
