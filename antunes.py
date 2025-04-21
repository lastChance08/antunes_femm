import femm
import os
import glob
import matplotlib.pyplot as plt
import numpy as np
import imageio.v3 as iio3

take_screenshots = True
femm42_path = 'D:/Apps/femm42_dev'
task_folder = 'D:/cad/femm/Antunes/'
task_fem_file = 'Antunes.fem'
screens_folder = task_folder + 'scr/'
temp_file = 'temp'
torque_graph = 'torque.png'
voltage_graph = 'voltage.png'
dt = 5e-6  # simulation step duration, s
rpm = 2000.  # generator speed, RPM
simulation_angle = 120    # angular distance of the simulation, deg

femm.openfemm(femmpath=femm42_path)
femm.opendocument(task_folder + task_fem_file)
femm.main_maximize()
femm.main_resize(1058, 600)
femm.mi_saveas(task_folder + temp_file + '.fem')

if take_screenshots:
    isExist = os.path.exists(screens_folder)
    if not isExist:
        os.makedirs(screens_folder)
    else:
        files = glob.glob(screens_folder + '*')
        for f in files:
            os.remove(f)

dtta = rpm * 360 / 60 * dt

cogging_torque_dict = {}
C1flux_dict = {}
C2flux_dict = {}
C3flux_dict = {}

n = round(simulation_angle / dtta)

femm.mi_modifycircprop("A", 1, 0)
femm.mi_modifycircprop("B", 1, 0)
femm.mi_modifycircprop("C", 1, 0)

for k in range(n):
    tta = dtta * k
    t = dt * k

    femm.mi_modifyboundprop("mySlidingBand", 10, tta)
    femm.mi_analyse(1)
    femm.mi_loadsolution()

    tq = femm.mo_gapintegral("mySlidingBand", 0)
    cogging_torque_dict.update({tta: tq})

    fluxC1 = femm.mo_getcircuitproperties("A")[2]
    fluxC2 = femm.mo_getcircuitproperties("B")[2]
    fluxC3 = femm.mo_getcircuitproperties("C")[2]

    C1flux_dict.update({t: fluxC1})
    C2flux_dict.update({t: fluxC2})
    C3flux_dict.update({t: fluxC3})

    if k % 10 == 0:
        if take_screenshots:
            femm.mo_showdensityplot(1, 0, 0, 2, 'bmag')  # Flux density normalized to 2T
            femm.mo_showvectorplot(1)
            femm.mo_savebitmap(screens_folder + str(k) + '.png')
        print("Torque ")
        print({tta: tq})
        print("Flux A ")
        print({tta: fluxC1})
        print("Flux B ")
        print({tta: fluxC2})
        print("Flux C ")
        print({tta: fluxC3})

    femm.mo_close()

os.remove(task_folder + temp_file + '.fem')
os.remove(task_folder + temp_file + '.ans')
femm.closefemm()

if take_screenshots:
    files = glob.glob(screens_folder + '*.png')
    images = []
    for f in files:
        images.append(iio3.imread(f))
    iio3.imwrite(screens_folder + 'animation.gif', images, duration=100, loop=0)

angle = list(cogging_torque_dict.keys())

torque = cogging_torque_dict.values()
C1flux_dict = list(C1flux_dict.values())
C2flux_dict = list(C2flux_dict.values())
C3flux_dict = list(C3flux_dict.values())

C1voltage = 8 * np.diff(C1flux_dict) / dt
C2voltage = 8 * np.diff(C2flux_dict) / dt
C3voltage = 8 * np.diff(C3flux_dict) / dt

fig, ax = plt.subplots()

ax.plot(angle, torque)
ax.set(xlabel='Angle', ylabel='Torque N/m',
       title='Cogging Torque')
ax.grid()

fig.savefig(task_folder + torque_graph)
plt.show()

fig_flux, voltage = plt.subplots()
angle.pop()

voltage.set(xlabel='Angle', ylabel='Voltage V',
            title='Line-to-neutral voltage')
voltage.plot(angle, C1voltage)

color = 'tab:green'
voltage.plot(angle, C2voltage, color=color)

color = 'tab:red'
voltage.plot(angle, C3voltage, color=color)
voltage.grid()

fig_flux.savefig(task_folder + voltage_graph)
plt.show()
