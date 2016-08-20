#!/usr/bin/env python

import os
import shutil

def run_vasp(scale,
             mul,
             precision,
             title,
             atoms,
             num,
             tag,
             var,
             potpath):
    # Pretreatment
    nums=sum(map(int,num.split()))
    # Generate POSCAR
    p=precision
    cys = "%%.%df %%.%df %%.%df\n%%.%df %%.%df %%.%df\n%%.%df %%.%df %%.%df"%(
        p,p,p,p,p,p,p,p,p
    )%(
        scale*mul,0,0,
        0,scale*mul,0,
        0,0,scale*mul
    )
    posi = ""
    for i in range(nums):
        if i == 0:
            posi+="%%.%df %%.%df %%.%df F F F\n"%(p,p,p)%(
                0,0,0)
        elif i == 1:
            posi+="%%.%df %%.%df %%.%df T F F\n"%(p,p,p)%(
                var[0],0,0)
        elif i == 2:
            posi+="%%.%df %%.%df %%.%df T T F\n"%(p,p,p)%(
                var[1],var[2],0)
        else:
            posi+="%%.%df %%.%df %%.%df T T T\n"%(p,p,p)%(
                var[i*3-6],var[i*3-5],var[i*3-4])
    poscar = "%s\n%s\n%s\n%s\n%s\nS\nC\n%s"%(
        title,
        "%%.%df"%precision%1,
        cys,
        atoms,
        num,
        posi
    )
    # Copy Files
    name="try_%d"%tag
    shutil.rmtree(name,ignore_errors=True)
    os.makedirs(name)
    with open("%s/POSCAR"%name,"w") as posc:
        posc.write(poscar)
    with open("%s/KPOINTS"%name,"w") as kpoi:
        kpoi.write("""Gamma-point only
        1
        rec
        0 0 0 1
        """)
    with open("%s/POTCAR"%name,"w") as potc:
        for i in atoms.split():
            with open("%s/%s/POTCAR"%(potpath,i),"r") as to_read:
                to_copy = to_read.read()
            potc.write(to_copy)
    shutil.copy("INCAR","%s/INCAR"%name)
    os.system("cd %s;vasp_without_mpi 1>output"%name)
    with open("%s/OUTCAR"%name,"r") as outc:
        src=outc.read()
    # Define Get Single Energy
    def get_single_point(src,pos):
        test=src.find("POSITION",pos)
        if test == -1:
            return None
        starter=src.find("\n",src.find("\n",test)+1)
        ender=src.find("\n -",starter)
        pre_position=src[starter:ender].split()
        position=[]
        for i in range(len(pre_position)/6):
            if i==0:
                pass
            elif i==1:
                position.append(pre_position[i*6+0])
            elif i==2:
                position.append(pre_position[i*6+0])
                position.append(pre_position[i*6+1])
            else:
                position.append(pre_position[i*6+0])
                position.append(pre_position[i*6+1])
                position.append(pre_position[i+8+2])
        position=map(float,position)
        position=map(lambda x:x if x<scale*mul/2 else x-scale*mul,position)
        pre_en=src.find("=",ender)
        en=float(src[pre_en+1:src.find("eV",pre_en)].split()[0])
        return position,en,pre_en
    # Get Energy
    pos=0
    ans=[get_single_point(src,pos)]
    while ans[-1]!=None:
        pos=ans[-1][-1]
        ans.append(get_single_point(src,pos))
    return [[i[0],i[1]] for i in ans[:-1]]
