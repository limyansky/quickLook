# This script does the following:
# Takes in target name, output location, number of cores, and email
# Writes an appropriate submission script
# Writes an appropriate .yaml file
# Submits the submission script

# Needed to read in commandline arguments
import sys

# Import tools to read the .yaml config file
import yaml

# Import tools that allow you to run commandline from python
import argparse

# Import tools for creating a log
import logging

# Create the log object
log = logging.getLogger(__name__)


# The function that runs when the script is called
def main():
    """
    Automatically calculate spectral information about an input source.

    Parameters:
        param_1: The first parameter
        param_2: The second parameter

    Keyword Arguments:
        opt_1: The first optional argument
        opt_2: The second optional argument
    """

    # Add the docstring to the argument parser
    # This doesn't currently work the way I want it to
    # Try print(__doc__) to see.
    parser = argparse.ArgumentParser(description=__doc__)

    # Add arguments
    parser.add_argument('target', help='The 4FGL target name.')
    parser.add_argument('outdir', help='The output directory.')
    parser.add_argument('config', help='A .yaml file containing paths to the '
                                       'relivant templates.')
    parser.add_argument('ncores', help='The number of cores to be used in '
                                       'diffuse response generation.')
    parser.add_argument('email', help='Your email address.')

    # #xtract the arguments from the parser
    args = parser.parse_args()

    # Remove trailing slashes from the outdir
    args.outdir = args.outdir.strip('/')

    # Log the input information
    log.info('Looking at source %s.', args.target)
    log.info('Storing output in %s.', args.outdir)
    log.info('Jobs will be submitted with %f cores.', args.ncores)
    log.info('Emailing %s output from the cluster.', args.email)

    config_dict = read_config(args.config)

    # Log the information from the configuration file
    log.info('Using the fermipy template: %s',
             config_dict['fermipy_yaml_template'])
    log.info('Using the submission script template: %s',
             config_dict['submit_template'])

    # Create a copy of the fermipy yaml template, filling in appropriate
    # blanks so that the file will work when passed to fermipy.
    fill_yaml(args.target, args.outdir, config_dict['fermipy_yaml_template'])

    # Create the script that will be submitted to the cluster.



def read_config(config):
    """
    Extract the various filepaths specified command-line configuration file.

    Parameters:
        config: An input command-line configuration file.
    """

    with open(config) as file:
        config_dict = yaml.full_load(file)

    return config_dict


def fill_yaml(target, outdir, template):
    """
    Take the yaml input file, and fill in appropriate blanks.

    Parameters:
        target: The 4FGL target name.
        outdir: The output directory.
        template: The template fermipy .yaml file.
    """

    # Create the full-path name of the yaml file we will generate
    yaml_working = outdir + '/configuration.yaml'

    # Begin construction of the yaml file.
    # Open the reading and writing files
    yt = open(template, 'r')
    yw = open(yaml_working, 'w')

    # Loop through all the lines in the yaml template file
    for line in yt:

        # Look for where to insert the target item
        if line.strip() == 'insert_target':
            yw.write('  target  : \'%s\'\n' % (target))

        # Look for where to insert the ourdir item
        elif line.strip() == 'insert_outdir':
            yw.write('  outdir   : \'%s\'\n' % (outdir))

        # If we aren't inserting the target or ourdir, print the template line
        else:
            yw.write(line)

    # Close the reading and writing yaml files
    yt.close()
    yw.close()

def fill_submit(outdir, template):
    """
    Take the submission script template file, and fill in appropriate blanks.

    Parameters:

    """

    # Create the full-path name of the .sh file we will generate
    submit_working = outdir + '/submission.sh'

    # Begin construction of the submission script
    # Open the reading and writing files
    st = open(template, 'r')
    sw = open(submit_working, 'w')

    for line in st:

        # Look for where to insert the cluster_output
        if line.strip() == 'cluster_outputs':
            sw.write('#$ -o %s/cluster_out_$JOB_ID.txt\n' % (outdir))

        # Look for where to insert the job name
        elif line.strip() == 'job_name':
            spaceless_name = target[0:4] + target[5:]
            print(spaceless_name)
            sw.write('#$ -N %s\n' % (spaceless_name[1:]))

        # Look for wohere to insert the email address
        elif line.strip() == 'email_address':
            sw.write('#$ -M %s\n' % (email))

        # Otherwise, print the template line
        else:
            sw.write(line)

    # Lines to run python scripts
    sw.write('\n')

    sw.write('python %s \'%s\'\n' % (fermipy_file, yaml_working))

    sw.write('python %s %s \'%s\' \'%s\' \'%s\' \'%s\' \'%s\'\n'
             % (gtdiffrsp_file, ncores, evfile, scfile, srcmdl,
                'CALDB', diffrsp_file))

    sw.write('python %s \'%s\' \'%s\' \'%s\'\n'
             % (gtsrcprob_file, yaml_working, diffrsp_file, srcmdl))

    # Close the reading and writing .sh files
    st.close()
    sw.close()


# Set the location of the template files
yaml_template = '/home/brent/python_scripts/quicker_look/script_templates/quicker_template_4FGL.yaml'
submit_template = '/home/brent/python_scripts/quicker_look/script_templates/quicker_control_template.sh'


submit_working = outdir + '/submission.sh'

# For testing purposes
#yaml_working = 'configuration.yaml'
#submit_working = 'submit.sh'

# Define files for fermipy, gtdiffrsp_mp_brent,         and gtsrcprob
# At some point, it might be worth turning these into their own scripts
# which accept command line arguements.
fermipy_file = '/home/brent/python_scripts/quicker_look/script_templates/quicker_fermipy_callable.py'
gtdiffrsp_file = '/home/brent/python_scripts/gtdiffrsp_mp_brent.py'
gtsrcprob_file = '/home/brent/python_scripts/quicker_look/script_templates/quicker_gtsrcprob_callable.py'

# gtdiffrsp_mp_brent requires an evfile and srcmdl. These are generated by
# fermipy, and I hardcode their paths here.
evfile = outdir + '/ft1_00.fits'
srcmdl = outdir + '/quick_look_00_00.xml'
diffrsp_file = outdir + '/diffrsp.fits'



# Once the yaml file has been written, we actually have to open it again to
# get a few more details out of it. These could probably be hardcoded, but
# I think it is more versitile to do it this way, in the event that they
# later change.
with open(yaml_working) as stream:
    try:
        configFile = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        print('FAILURE')

# Extract the important things from the config file
scfile = configFile['data']['scfile']



# Finally, we submit the job to the cluster
#sub_command = 'qsub -l hostname=%s %s ' % (com_node, submit_working)
sub_command = 'qsub %s' % (submit_working)
print sub_command
call(sub_command, shell=True)
