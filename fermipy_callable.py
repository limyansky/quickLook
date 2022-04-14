# Take care of matplotlib causing core dumps
from matplotlib import use
use('Agg')

# Import generic plotting tools
import matplotlib.pyplot as plt

# Import analysis tools
from fermipy.gtanalysis import GTAnalysis
from fermipy.plotting import ROIPlotter

# Import tool to take in commandline arguements
import sys

# Import tools to read the .yaml config file
import yaml

# Read in arguements from commandline.

### CHANGE THIS ###
config = sys.argv[1]
outname = '/start_00.npy'

enable_Fit = True
enable_Optimize = False

# Read in the configuration file
# The same information is asked for at multiple points in the process, and this
# helps to keep things consistent.
with open(config) as stream:
    try:
        configFile = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        print('FAILURE')

# Extract the important things from the config file
target = configFile['selection']['target']
scfile = configFile['data']['scfile']
outdir = configFile['fileio']['outdir']

### CHANGE THIS maybe... ###
srcmdl = outdir + '/final_00_00.xml'
savefile = outdir + '/quick_00'
imagefile = outdir + '/residual_image.png'


# Define a function to make some plots
def auto_plotter(roi_object, source_name, save_name, clean=False):

    if not clean:
        resid = roi_object.residmap(source_name)

        o = resid
        fig = plt.figure(figsize=(14, 6))
        ROIPlotter(o['sigma'],
                   roi=roi_object.roi).plot(vmin=-5, vmax=5,
                                            levels=[-5, -3, 3, 5, 7, 9],
                                            subplot=121, cmap='RdBu_r')
        plt.gca().set_title('Significance')
        ROIPlotter(o['excess'],
                   roi=roi_object.roi).plot(vmin=-800, vmax=800, subplot=122,
                                            cmap='RdBu_r')
        plt.gca().set_title('Excess Counts')
        plt.savefig(save_name)

    elif clean:
        resid = roi_object.residmap(source_name)

        o = resid
        fig = plt.figure(figsize=(14, 6))
        ROIPlotter(o['sigma']).plot(vmin=-5, vmax=5,
                                    levels=[-5, -3, 3, 5, 7, 9],
                                    subplot=121, cmap='RdBu_r')
        plt.gca().set_title('Significance')
        ROIPlotter(o['excess']).plot(vmin=-800, vmax=800, subplot=122,
                                     cmap='RdBu_r')
        plt.gca().set_title('Excess Counts')
        plt.savefig(save_name)


# Create the analysis object.
gta = GTAnalysis(config, logging={'verbosity': 3})

# Run the setup
gta.setup()

if enable_Optimize:
    # Optimize
    opt1 = gta.optimize()

if enable_Fit:

    gta.free_sources(free=False)
    gta.free_source('galdiff')
    gta.free_source('isodiff')

#    gta.set_edisp_flag('galdiff', flag=False)
    gta.set_edisp_flag('isodiff', flag=False)

    gta.fit()

#gta.write_roi(outdir + '/quick_look_00')
gta.write_roi('quick_look_00')
auto_plotter(gta, target, imagefile, clean=True)
