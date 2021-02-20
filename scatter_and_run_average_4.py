import numpy as np
import os, fnmatch
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import sys
import statistics
import subprocess
import re

# Finding traj file where to operate:
ruta = os.path.abspath(".")
data = ruta.split("/")

def find(pattern, path):
    result = []
    for files in os.listdir(path):
        if fnmatch.fnmatch(files, pattern):
            result.append(files)
    return result

target = find('*.traj', '.')
if len(target) > 1:
    print ('There is more than one *.traj in this folder. Please specify')
    sys.exit()

traj_file = target[0]
print (traj_file)

# Finding file for Edisp:
if 'reactions_last_10ps' in data:
    print ('analyzing last 10 ps')
    print ("remember to have done this: 'bash extract_Edisp.sh'")
    print ("and this: 'tail -10000  Edisp_R2-R27.txt  > last_10ps_Edisp_R2-R27.txt'")
    loc = '../../'
    target_1 = find('last*Edisp*.txt', loc)
    if target_1:
        edisp_file = target_1[0]
        print (edisp_file)
        print (f'There is {edisp_file} present. We will substract Edisp at each step')
    else:
        print (f'There is NO last*Edisp*.txt present. We will NOT substract Edisp at each step')
else:
    print ('analyzing all 100ps')
    print ("remember to have done this: 'bash extract_Edisp.sh'")
    loc = '../'
    target_1 = find('Edisp*.txt', loc)
    if target_1:
        edisp_file = target_1[0]
        print (edisp_file)
        print (f'There is {edisp_file} present. We will substract Edisp at each step')
    else:
        print (f'There is NO Edisp*.txt present. We will NOT substract Edisp at each step')


# Shift_time
if 'reactions_last_10ps' in data:
    print ("file './shift_time_last_10ps' will be used")
    # In case we're doing the last 10ps reactions analysis - create this 
    # file in the current directory with a 0 in it:
    a = np.loadtxt('./shift_time_last_10ps').T
else:
    print ("file '../shift_time' will be used")
    # shift time of the whole traj:
    a = np.loadtxt('../shift_time').T


shift_time  = a*1E-3
chunk = 500

# Improvement:
#cmd = "cat ./molecules_found.dat.*  |  awk '{print $1}' | sort  | uniq"
# If the number of molecules_found.dat.* files is very very large (i.e. the trajectory is large), this cat command can saturate and give error: /bin/cat: Argument list too long
# so we just use the all_molecules_found.dat generated by detect.py via a for loop:
cmd = "cat all_molecules_found.dat  |  awk '{print $1}' | sort  | uniq"
s = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE).stdout

au = s.read().splitlines()
LABELS = [i.decode() for i in au]


# Title of graphs:
names = {
       'Electrolyte' : 'Reactants @ ',
       'long_paths' : 'Products @ ',

       '1.5_Salt__1_Ur' : '1.5:1 mixture. ',
       '1.5_to_1' : '1.5:1 mixture. ',
       '10_urea_15_AlCl3' : '1.5:1 mixture. ',
       'One_to_one_Salt_Ur' : '1:1 mixture. ',
       'one_to_one_urea_salt' : '1:1 mixture. ',
       '14_urea_7_Al2Cl6' : '1:1 mixture. ',

       '650K_2_300K' : "T = 1000 K + 300 K\n",
       '650K_to_300K' : "T = 1000 K + 300 K\n",
       'at_300K_new' : "T = 300 K\n",
       'at_300K' : "T = 300 K\n",

       'Al2Cl7-__AlCl2Ur2+' : '$[$Al$_{2}$Cl$_{7}]^{-}$ + $[$AlCl$_{2}$(urea)$_{2}]^{+}$',
       'Al2Cl6Ur__plus__AlCl3Ur' : '$[$Al$_{2}$Cl$_{6}$(ur)$]$ + $[$AlCl$_{3}$(ur)$]$',
       'AlCl4-__Al2Cl5Ur2+' : '$[$AlCl$_{4}]^{-}$ + $[$Al$_{2}$Cl$_{5}$(urea)$_{2}]^{+}$' ,
       'AlCl3_ur' : '$[$AlCl$_{3}$ (urea)$]$ + $[$AlCl$_{3}$ (urea)$]$',
       'AlCl4-__AlCl2Ur2+' : '$[$AlCl$_{4}]^{-}$ + $[$AlCl$_{2}$(urea)$_{2}]^{+}$',

       'linked_to_same_Al' : '-(O,O) to same Al atom.',
       'linked_to_diff_Al' : '-(O,O) to diff Al atom.',

       'NaCl' : ' NaCl model',
       'NaCl_prim' : ' NaCl model',
       'CsCl' : ' CsCl model',

    'ADF' : 'ADF Packmol: ',
    'Quantum_ATK'    : 'ATK Packmol: '
}

data_fmt = []
for k in data:
    if k in names:
        data_fmt.append(names[k])

if not '650K_2_300K' in data or not 'at_300K_new' in data or not 'at_300K'  in data or not '650K_to_300K' in data:
    data_fmt.append("T = 1000 K\n")

data_fmt = list(dict.fromkeys(data_fmt))

if "Products @ " in data_fmt:
    N_ureas = 16.
else:
    N_ureas = 12.

if "Products @ " in data_fmt:
    if not " NaCl model" in data_fmt and not " CsCl model" in data_fmt:
        data_fmt_sorted = [data_fmt[0], data_fmt[1], data_fmt[3], data_fmt[2]]
        data_fmt_sorted.append(" NaCl model")

    if " NaCl model" in data_fmt:
        data_fmt_sorted = [data_fmt[0], data_fmt[1], data_fmt[4], data_fmt[2], data_fmt[3]]

    if " CsCl model" in data_fmt and not "-(O,O) to same Al atom." in data_fmt and not "-(O,O) to diff Al atom." in data_fmt:
       data_fmt_sorted = [data_fmt[0], data_fmt[1], data_fmt[4], data_fmt[2], data_fmt[3]]

    if " CsCl model" in data_fmt and "-(O,O) to same Al atom." in data_fmt:
       data_fmt_sorted = [data_fmt[0], data_fmt[1], data_fmt[5], data_fmt[2], data_fmt[3], data_fmt[4]]

    if " CsCl model" in data_fmt and "-(O,O) to diff Al atom." in data_fmt:
       data_fmt_sorted = [data_fmt[0], data_fmt[1], data_fmt[5], data_fmt[2], data_fmt[3], data_fmt[4]]

    if "-(O,O) to same Al atom." in data_fmt and not " NaCl model" in data_fmt and not " CsCl model" in data_fmt:
        data_fmt_sorted = [data_fmt[0], data_fmt[1], data_fmt[4], data_fmt[2], data_fmt[3]]
        data_fmt_sorted.append(" NaCl model")

    if "-(O,O) to diff Al atom." in data_fmt and not " NaCl model" in data_fmt and not " CsCl model" in data_fmt:
        data_fmt_sorted = [data_fmt[0], data_fmt[1], data_fmt[4], data_fmt[2], data_fmt[3]]
        data_fmt_sorted.append(" NaCl model")


else: # Then these are Reactants:

    if "ADF Packmol: " in data_fmt: # ADF Packmol reactants
        r = re.compile(".*Rd.*")
        auxa1 = list(filter(r.match, data))
        print ('auxa1 = ', auxa1)
        target_Sd = auxa1[-1]
        data_fmt_sorted = [data_fmt[0], data_fmt[1], data_fmt[3], data_fmt[2], target_Sd]

    elif "ATK Packmol: " in data_fmt: # Quantumm ATK Packmol reactants
#       r = re.compile(".*Rd.*")
#       auxa1 = list(filter(r.match, data))
#       print ('auxa1 = ', auxa1)
#       target_Sd = auxa1[-1]
        data_fmt_sorted = [data_fmt[0], data_fmt[1], data_fmt[3], data_fmt[2], "Rd_Seed_1"]

    else: # Protons reactants
        r = re.compile(".*Rd.*")
        auxa1 = list(filter(r.match, data)) 
        target_Sd = auxa1[0]
        data_fmt_sorted = [data_fmt[0], data_fmt[1], data_fmt[2], target_Sd]

suptitle_label = ''.join(data_fmt_sorted)
suptitle_label = "Model R1"

# remove species which average < 3.8%
new_LABELS = []
for i in LABELS:
    per, time = np.loadtxt(i + '.txt').T
    if (np.average(per)) > 0.:
        new_LABELS.append(i)


# Obtain the average of these
All_per_Av = []
All_per = []
for i in new_LABELS:
    per, time = np.loadtxt(i + '.txt').T

    per_av = np.average(per)
    All_per_Av.append(per_av)
    All_per.append(per)


All_per = np.array(All_per)
All_per_Av = np.array(All_per_Av)
new_LABELS = np.array(new_LABELS)

inds = np.argsort(-All_per_Av)

sorted_All_per = All_per[inds]
sorted_All_per_Av = All_per_Av[inds]
sorted_new_LABELS = new_LABELS[inds]

from ase.io.trajectory import Trajectory 
traj = Trajectory(traj_file) 
 
N_images = len(traj) 

inf = list(range(0, N_images-chunk))
sup = list(range(chunk, N_images)) 

import collections
All_concs_in_chunks = collections.defaultdict(list)
for i in sorted_new_LABELS:
    count, time = np.loadtxt(i + '.count.txt').T
    for k, l in zip(inf, sup):
        sum_conc = sum(count[k:l+1])
        All_concs_in_chunks[i].append(sum_conc)
        
species_step = []
for j in inf:
    aux1 = []
    for i in All_concs_in_chunks.items():
        aux = i[1][j]
        aux1.append(aux)
    species_step.append(aux1)

suma_species_step = []
for i in species_step:
    suma = sum(i)
    suma_species_step.append(suma)


aux5 = collections.defaultdict(list)
for i,f in zip(All_concs_in_chunks.keys(), All_concs_in_chunks.items()):
    aux2 = f[1]
    for j,m in zip(aux2, suma_species_step):
        aux4 = (j/m)*100
        aux5[i].append(aux4)

# remove species which average < 3.8%
new_LABELS = []
for i in LABELS:
    per, time = np.loadtxt(i + '.txt').T
    if (np.average(per)) > 3.8:
        new_LABELS.append(i)
        print ('i,  np.average(per) = ', i, np.average(per))

# Obtain the average of these
All_per_Av = []
All_per = []
for i in new_LABELS:
    per, time = np.loadtxt(i + '.txt').T

    per_av = np.average(per)
    All_per_Av.append(per_av)
    All_per.append(per)


All_per = np.array(All_per)
All_per_Av = np.array(All_per_Av)
new_LABELS = np.array(new_LABELS)

inds = np.argsort(-All_per_Av)

sorted_All_per = All_per[inds]
sorted_All_per_Av = All_per_Av[inds]
sorted_new_LABELS = new_LABELS[inds]


# Plot labels: compilation of all fragments found (for products):
dict_labels = {                                                                                        
        'C2H8AlCl2N4O2'       : '$[$AlCl$_{2}$(ur)$_{2}]^{+}$',
        'Al2Cl7'              : '$[$Al$_{2}$Cl$_{7}]^{-}$',
        'AlCl4'               : '$[$AlCl$_{4}]^{-}$',
        'C2H8Al2Cl5N4O2'      : '$[$Al$_{2}$Cl$_{5}$(ur)$_{2}]^{+}$',
        'C2H8Al4Cl12N4O2'     : '$[$Al$_{4}$Cl$_{12}$(ur)$_{2}]$',
        'C2H8Al3Cl8N4O2'      : '$[$Al$_{3}$Cl$_{8}$(ur)$_{2}]^{+}$',
        'C2H8Al3Cl9N4O2'      : '$[$Al$_{3}$Cl$_{9}$(ur)$_{2}]$',
        'CH4AlCl3N2O'         : '$[$AlCl$_{3}$(ur)$]$',
        'CH4Al2Cl6N2O'        : '$[$Al$_{2}$Cl$_{6}$(ur)$]$',
        'C2H8Al5Cl15N4O2'     : '$[$Al$_{5}$Cl$_{15}$(ur)$_{2}]$',
        'C3H12AlClN6O3'       : '$[$AlCl(ur)$_{3}]$',  #x
        'H'                   : 'H',
        'CH3Al3Cl9N2O'        : 'CH$_{3}$Al$_{3}$Cl$_{9}$N$_{2}$O',
        'Cl'                  : 'Cl',
        'CH4Al3Cl9N2O'        : '$[$Al$_{3}$Cl$_{9}$(ur)$]$',
        'AlCl3'               : '$[$AlCl$_{3}]$',
        'CH4N2O'              : 'ur',
        'CH5N2O'              : 'CH$_{5}$N$_{2}$O',
        'C2H7Al2Cl5N4O2'      : 'C$_{2}$H$_{7}$Al$_{2}$Cl$_{5}$N$_{4}$O$_{2}$',
        'CH3Al2Cl6N2O'        : 'CH$_{3}$Al$_{2}$Cl$_{6}$N$_{2}$O',
        'CH4AlCl2N2O'         : '$[$AlCl$_{2}$(ur)$]^{+}$',
        'Al3Cl10'             : '$[$Al$_{3}$Cl$_{10}]^{-}$',
        'C2H7Al3Cl8N4O2'      : 'C$_{2}$H$_{7}$Al$_{3}$Cl$_{8}$N$_{4}$O$_{2}$',
        'C3H11Al2Cl4N6O3'     : 'C$_{3}$H$_{11}$Al$_{2}$Cl$_{4}$N$_{6}$O$_{3}$',
        'CH3AlCl2N2O'         : 'CH$_{3}$AlCl$_{2}$N$_{2}$O',  # added July-2020
        'C3H12Al5Cl14N6O3'    : '$[$Al$_{5}$Cl$_{14}$(ur)$_{3}]^{+}$',  # added Sept-2020
        'C2H8Al4Cl11N4O2'     : '$[$Al$_{4}$Cl$_{11}$(ur)$_{2}]^{+}$'  # added Sept-2020
}


# The colors:
dict_colors = {                                                                                        
        'C2H8AlCl2N4O2'       :  'green',
        'Al2Cl7'              :  'red',
        'AlCl4'               :  'blue', #before:firebrick
        'C2H8Al2Cl5N4O2'      :  'orange',
        'C2H8Al4Cl12N4O2'     :  'black',
        'C2H8Al3Cl8N4O2'      :  'sienna',
        'C2H8Al3Cl9N4O2'      :  'lawngreen',
        'CH4AlCl3N2O'         :  'orchid',
        'CH4Al2Cl6N2O'        :  'cyan',
        'C2H8Al5Cl15N4O2'     :  'crimson',
        'C3H12AlClN6O3'       :  'lightseagreen',  #x
        'H'                   :  'palevioletred',
        'CH3Al3Cl9N2O'        :  'darkgoldenrod',
        'Cl'                  :  'fuchsia',
        'CH4Al3Cl9N2O'        :  'chocolate',
        'AlCl3'               :  'mediumblue',
        'CH4N2O'              :  'pink',
        'CH5N2O'              :  'tomato',
        'C2H7Al2Cl5N4O2'      :  'yellow',
        'CH3Al2Cl6N2O'        :  'teal',
        'CH4AlCl2N2O'         :  'steelblue',
        'Al3Cl10'             :  'darkturquoise',
        'C2H7Al3Cl8N4O2'      :  'yellowgreen',
        'C3H11Al2Cl4N6O3'     :  'salmon',
        'CH3AlCl2N2O'         :  'gold',  # added July-2020
        'C3H12Al5Cl14N6O3'    :  'purple',  # added Sept-2020
        'C2H8Al4Cl11N4O2'     :  'darkorange'  # added Sept-2020
}


print ('sorted_new_LABELS = ', sorted_new_LABELS)
sorted_new_LABELS_fmt = [dict_labels[key] for key in sorted_new_LABELS]
sorted_new_LABELS_colors = [dict_colors[key] for key in sorted_new_LABELS]


#### Statistics

f = open('stats.tex', 'w')

print ("""

\\documentclass{article}
\\usepackage[margin=0.3in]{geometry}
\\usepackage{multirow}
%\\usepackage{adjustbox}
\\begin{document}

\\begin{table}[]
%\\begin{adjustbox}{width=\\hsize, totalheight=\\textheight, keepaspectratio}
\\begin{tabular}{|l|l|}
\\hline
Species & Average composition (\\%) \\\ \\hline

""", file=f)


for i, j, k in zip(sorted_new_LABELS_fmt, sorted_new_LABELS, sorted_All_per_Av):
    print ('sorted_new_LABELS_fmt , sorted_new_LABELS, sorted_All_per_Av = ', i, j, k)
    print (f" {{{i}}} & {{{k}}} \\\  \\hline", file=f)


print ("""

\\end{tabular}
%\\end{adjustbox}
\\end{table}

    """, file=f)

res = dict((k, aux5[k]) for k in sorted_new_LABELS if k in aux5) 

times = [i*1E-3 for i in sup]

for i,j,k,c in zip(res.keys(), res.items(), sorted_new_LABELS_fmt, sorted_new_LABELS_colors):
    plt.plot(times, j[1], label='%s' % k, color='%s' %c)

ax = plt.gca()
# Shrink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])

# Put a legend to the right of the current axis
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.ylim(bottom=3.8) 

plt.ylabel('Percentage')
plt.xlabel('Time (ps)')
plt.suptitle(suptitle_label, fontsize=15)

plt.xticks(np.arange(min(time), max(time)+1, 1))
plt.ticklabel_format(useOffset=False)
plt.savefig('start_on_0ps_6.pdf', bbox_inches='tight')


# Plotting running average of composition:
plt.figure()

new_time = [(item + shift_time) for item in times]

for i,j,k,c in zip(res.keys(), res.items(), sorted_new_LABELS_fmt, sorted_new_LABELS_colors):
    plt.plot(new_time, j[1], label='%s' % k, color='%s' %c)

ax = plt.gca()
# Shrink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])

# Put a legend to the right of the current axis
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.ylim(bottom=0.0)  

plt.ylabel('Percentage')
plt.xlabel('Time (ps)')

plt.suptitle(suptitle_label, fontsize=15)
plt.ticklabel_format(useOffset=False)

plt.savefig('composition_6.pdf', bbox_inches='tight')


# Plotting running average of energy:
All_e = []
All_e_normalized = []
# If we want to substract Edisp:
#if edisp_file:
if target_1:
    edisp_file = target_1[0]
    edisp = np.loadtxt(loc + edisp_file).T
    if len(edisp) != len(traj):
        print (f'{edisp_file} and {traj_file} do not have same length')
        sys.exit()
    else:
        print (f'{edisp_file} and {traj_file} have same length')
        print (f'Substracting Edisp at each step')
        for i in range(0, len(traj)):
            atoms = traj[i]
            e = atoms.get_potential_energy() - edisp[i]
            All_e_normalized.append(e/N_ureas)
            All_e.append(e)

# If we DO NOT want to substract Edisp:
else:
    for i in range(0, len(traj)):
        atoms = traj[i]
        e = atoms.get_potential_energy()
        All_e_normalized.append(e/N_ureas)
        All_e.append(e)


N_images = len(traj)
inf = list(range(0, N_images-chunk))
sup = list(range(chunk, N_images))


All_e_chunks_n = []
for k, l in zip(inf, sup):
    aux_n  = sum(All_e_normalized[k:l+1])/(len(All_e_normalized[k:l+1]))
    All_e_chunks_n.append(aux_n)

times = [i*1E-3 for i in sup]
times_images = [i*1E-3 for i in range(0, N_images)]

new_time = [(item + shift_time) for item in times]
new_time_images = [(item + shift_time) for item in times_images]

plt.figure()

plt.plot(new_time, All_e_chunks_n, 'red')
plt.plot(new_time_images, All_e_normalized, 'blue', alpha=.4)

plt.ylabel('Energy (eV)')
plt.xlabel('Time (ps)')

plt.suptitle(suptitle_label, fontsize=15)
plt.ticklabel_format(useOffset=False)
plt.savefig('running_av_E_6.pdf', bbox_inches='tight')


Average_E = np.average(All_e)
Average_E_normalized = np.average(All_e_normalized)
print ('Average_E_normalized = ', Average_E_normalized)
print("Standard Deviation of sample is % s "  % (statistics.stdev(All_e_normalized)))

# working on the running average:
Average_E_runn = np.average(All_e_chunks_n)
print ('Average_E runn av.= ', Average_E_runn)
print("Standard Deviation of the E runn av. is % s "  % (statistics.stdev(All_e_chunks_n)))

print (f" Average (E running averages) = {Average_E_runn} \\\\", file=f)
print (f" std. deviation = {statistics.stdev(All_e_chunks_n)} ", file=f)

print (" \\end{document}", file=f)
f.close()


# Plotting running_average of E and composition:
fig, ax1 = plt.subplots()

ax1.set_xlabel('Time (ps)')
ax1.set_ylabel('Percentage')

for i,j,k,c in zip(res.keys(), res.items(), sorted_new_LABELS_fmt, sorted_new_LABELS_colors):
    ax1.plot(new_time, j[1], label='%s' % k, color='%s' %c)

h1, l1 = ax1.get_legend_handles_labels()

print (l1)
#sys.exit()

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

ax2.set_ylabel('Energy (eV)')
ax2.plot(new_time, All_e_chunks_n, 'grey', alpha=0.6, linewidth=2.5, label='Energy')


h2, l2 = ax2.get_legend_handles_labels()

h3 = h1 + h2
l3 = l1 + l2

# normal legend:
#ax1.legend(h3, l3, loc=0)

#fig.ticklabel_format(useOffset=False)

fig.tight_layout(rect=[0, 0.03, 1, 0.95])


# Shrink current axis by 20%
box = ax1.get_position()
ax1.set_position([box.x0, box.y0, box.width * 0.9, box.height]) # original: box.width * 0.9 & ax2

# Put a legend to the right of the current axis
fig.legend(loc='center left', bbox_to_anchor=(0.99, 0.5)) # -> for box.width * 0.9

#box = ax1.get_position()
#ax1.set_position([box.x0, box.y0, box.width * 0.9, box.height]) # original: box.width * 0.9 & ax2


#fig.suptitle(suptitle_label, fontsize=15)
ax1.set_title(suptitle_label, fontsize=15)
print ('==== The title for this model is: ', suptitle_label)

# normal legend: (init)
#ax1.legend(loc='center left')                                                                          
#ax2.legend(loc='center right')

#ax1.set_ylim(bottom=99.7, top=100.05)
if "Products @ " in data_fmt and "1:1 mixture. " in data_fmt and "$[$AlCl$_{3}$ (urea)$]$ + $[$AlCl$_{3}$ (urea)$]$" in data_fmt:
    ax1.set_ylim(bottom=0.0, top=102.30)

else:
    ax1.set_ylim(bottom=0.0)
#fig.tight_layout() # otherwise the right y-label is slightly clipped


## legend outside: 
#ax = plt.gca()
#box = ax.get_position()
#ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])
#ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))




fig.savefig('composition_and_running_av_E_6.pdf', bbox_inches='tight')

