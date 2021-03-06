#!python
#
import re
import os
import shutil
import platform
import numpy as np
import elastic3rd.energy.glue as glue

def get_base_vec(BaseName):
    BaseVec = np.zeros((3, 3))
    FileName = BaseName + ".cell"
    fopen = open(FileName, 'r')
    flag = 0
    count = 0
    for eachline in fopen:
        eachline = eachline.strip('\n')
        eachline = eachline.strip();
        if eachline == "%BLOCK LATTICE_CART":
            flag = 1
            continue
        elif eachline == "%ENDBLOCK LATTICE_CART":
            break
        if flag:
            linei = re.split('\s+', eachline)
            Basei = np.asarray(linei)
            Basei = Basei.astype(np.float64)
            BaseVec[count] = Basei
            count = count + 1
    fopen.close()
    return BaseVec

def write_base_vec(BaseName, BaseVec):
    FileName = BaseName + ".cell"
    fopen = open(FileName, 'r')
    tmpopen = open('tmpfile', 'a')
    flag = 0
    count = 0
    lines = []
    for eachline in fopen:
        linei = eachline.strip('\n')        
        linei = linei.strip();
        #print eachline
        if linei == "%BLOCK LATTICE_CART":
            tmpopen.write("%BLOCK LATTICE_CART\n")
            flag = 1
            continue
        elif linei == "%ENDBLOCK LATTICE_CART":
            flag = 0
        if flag:
            for j in range(0,3):
                tmpopen.write("      ")
                tmpopen.write("%.15f" % BaseVec[count][j])
            tmpopen.write("\n")
            count = count + 1
        else:
            tmpopen.write(eachline)
    fopen.close()
    tmpopen.close()
    os.remove(FileName)
    os.rename('tmpfile', FileName)

def run(NP, BaseName):
    plat = platform.platform().split("-")[0].lower()
    if plat == "windows":
        #print("Windows")
        RunStr = "RunCASTEP -np " + str(int(NP)) + " " + BaseName
    elif plat == "linux" :
        RunStr = "./RunCASTEP.sh -np " + str(int(NP)) + " " + BaseName
    return RunStr

def get_energy(BaseName):
    FileName = BaseName + ".castep"
    fopen = open(FileName, 'r')
    for eachline in fopen:
        linei = eachline.split("=")
        flag = linei[0].strip()
        flag0 = flag.split(",")[0]
        if flag0 == "Final energy":
            energy = linei[1].strip().split(' ')[0]
    fopen.close()
    energy = float(energy)
    # eV, Hartree, kJ/mol, kcal/mol
    Energy = glue.multi_energy(energy)
    return Energy

def copy_files(BaseName, Path):
    #TODO: need to be improved
    plat = platform.platform().split("-")[0].lower()
    shutil.copyfile(BaseName + ".cell", Path + "/" + BaseName + ".cell")
    shutil.copyfile(BaseName + ".param", Path + "/" + BaseName + ".param")
    if plat == "windows":
        #print("Windows")
        shutil.copyfile("RunCASTEP.bat", Path + "/RunCASTEP.bat")
    elif plat == "linux" :
        shutil.copyfile("RunCASTEP.sh", Path + "/RunCASTEP.sh")
        #chmodstr = "chmod 777 " + Path + "/RunCASTEP.sh"
        os.system("chmod 777 " + Path + "/RunCASTEP.sh")

'''
BaseVec = get_base_vec("Al.cell")
BaseVec[0][2] = 3
print BaseVec
Energy = get_energy("Al.castep")
print Energy
write_base_vec("Al.cell", BaseVec)

ERun = run(4, "Al")
print ERun
'''