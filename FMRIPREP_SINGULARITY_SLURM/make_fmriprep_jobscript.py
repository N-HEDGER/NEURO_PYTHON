
#### Script for passing fmriprep jobs to SLURM.

## Requirements
# 1. An fmriprep singularity image
# 2. The fmriprep_base.sh template
# 3. All of the required templateflow libraries installed locally (see readme)

####


####
## Imports
####


import re
import os


####
## Participant input.
####

# The participant identifiers in the BIDS directory (can be a list).
PIDS=["02"]


####
## Execution options
####

EX={}

# sbatch or sh? (sbatch if using the RACC)
EX['execute_type']='sbatch'

# Send the jobs fo excution, or just write? If set to False, then you will need to submit the job manually. 
EX['execute']=False

# Number of CPUs requested from SLURM.
EX['cpus']='16'

# Memory per CPU requested from SLURM.
EX['memperCPU']='4G'

# Email to send error messages to
EX['email']='nhedger1@gmail.com'



####
## Path options
####

# To avoid confusion - use the following scheme

# L_= local location
# S_= Singularity image location
# B_= Base location.


# Here we set the local paths to mount onto the singularity image.
# All of these in this section must be existing locations


# Start with local paths.
LPATH={}

# Location of the singularity image itself (static)
LPATH['im_path']='/storage/basic/nh_leverhulme/UTILS/poldracklab_fmriprep_latest-2020-04-09-30f9d1d80eba.simg'

# Path to the templateflow cache (static)
LPATH['tflow_path']='/storage/basic/nh_leverhulme/cache/templateflow'

# Path to the jobscript template to modify (static)
LPATH['jobscript_path']='/storage/basic/nh_leverhulme/BASE/BASE2/fmriprep_base.sh'

# Path to output the job scripts (static)
LPATH['job_path']='/storage/basic/nh_leverhulme/JOBS/fmriprep'

# Directory to the BIDS directory data (The one that contains the participant subdirectories).
LPATH['data_path']='/storage/basic/nh_leverhulme/DATA/knapenprf'

# Path to freesurfer directory (static - I think...).
LPATH['fs_path']='/storage/basic/nh_leverhulme/freesurfer'

# Base temporary working directory (dynamic). This is where fmriprep will store temporary files.
LPATH['B_work_path']='/storage/basic/nh_leverhulme/TEMP'

# Path to the freesurfer liscence (For convenience, I put mine in my temporary directory.
# It makes sense to do this, since it needs to be mounted anyway).
LPATH['fsli_path']=os.path.join(LPATH['B_work_path'],'license.txt')


# Base directory to outputs (dynamic).
LPATH['B_output_path']='/storage/basic/nh_leverhulme/DATA/knapenprf'


# Now some singularity locations
SPATH={}

# Data path (dynamic)
SPATH['B_data_path']='/data'

# Temp path (dynamic)
SPATH['B_work_path']='/work'

# License path (static)
SPATH['lipath']='/license'

SPATH['fsli_path']=os.path.join(SPATH['lipath'],'license.txt')

# Freesurfer directory path (static)
SPATH['fs_path']='/fsdir'

# Base output path (dynamic)
SPATH['B_output_path']='/output'

####
## Mount options
####

MOUNTS={}

# Make the static mounts now

# Mount the templateflow directory.


# The templateflow directory is mounted. 
MOUNTS['tfmount']='-B ' +'${TEMPLATEFLOW_HOST_HOME}:${SINGULARITYENV_TEMPLATEFLOW_HOME}'

# The freesurfer directory is mounted to /fsdir
MOUNTS['fsmount']= '-B ' + LPATH['fs_path']+':'+SPATH['fs_path']

# Mount the path to the lisence
MOUNTS['fslmount']= '-B ' + LPATH['B_work_path'] +':'+SPATH['lipath']

####
## Fmriprep specific options
####


FMRIPREP={}

# Set the output spaces.
FMRIPREP['output_spaces'] = ['fsaverage','MNI152NLin2009cAsym']
FMRIPREP['output_spaces']=" ".join(FMRIPREP['output_spaces'])


# Here I use a recipe that seems to work fairly well.

# Upper bound memory limit for fMRIPrep processes
FMRIPREP['mem_mb']='30000'

# Maximum number of threads per-process
FMRIPREP['ot']='8'

# Maximum number of threads across all processes
FMRIPREP['nt']='12'


# Put any optional flags here and they will get appended to the end of the call.
FMRIPREP['optionals']=['--write-graph','--ignore slicetiming', '--low-mem']
FMRIPREP['optionals']=" ".join(FMRIPREP['optionals'])

####
## Main loop
####

for PID in PIDS:

	#The path to the jobfile to be written
	LPATH['jobscript_current_path']=os.path.join(LPATH['job_path'],'myjob_'+PID+'.sh')


	# Force unique output directory for participant.
	# This will need to be made into a real location.

	if not os.path.isdir(os.path.join(LPATH['B_output_path'],PID,'derivatives')):
		os.mkdir(os.path.join(LPATH['B_output_path'],PID))	
		os.mkdir(os.path.join(LPATH['B_output_path'],PID,'derivatives'))
	

	LPATH['output_path']=os.path.join(LPATH['B_output_path'],PID,'derivatives')

	SPATH['output_path']=os.path.join(SPATH['B_output_path'],PID,'derivatives')
	

	# Force unique working directory.
	if not os.path.isdir(os.path.join(LPATH['B_work_path'],PID)):
		os.mkdir(os.path.join(LPATH['B_work_path'],PID))
	
	LPATH['work_path']=os.path.join(LPATH['B_work_path'],PID)
	SPATH['work_path']=os.path.join(SPATH['B_work_path'],PID)

	# Mount the data in a distinct location.
	SPATH['data_path']=os.path.join(SPATH['B_data_path'],PID)


	# Now add the dynamic mounts
	MOUNTS['dmount']= '-B ' + LPATH['data_path']+':'+SPATH['data_path']
	MOUNTS['wmount']= '-B ' + LPATH['work_path']+':'+SPATH['work_path']
	MOUNTS['omount']= '-B ' + LPATH['output_path']+':'+SPATH['output_path']

	
	# Join these mount commands altogether. 
	MOUNTS['mounts']=[MOUNTS['dmount'],MOUNTS['wmount'],MOUNTS['tfmount'],MOUNTS['fslmount'],MOUNTS['omount']]
	MOUNTS['mounts']=" ".join(MOUNTS['mounts'])


	# Make unique error file for the participant
	EX['errfile']=os.path.join(LPATH['job_path'],'myjob'+PID+'.err')



	RE_dict =  {

	'---cpus---':EX['cpus'],
	'---memperCPU---':EX['memperCPU'],
	'---email---':EX['email'],
	'---errpath---':EX['errfile'],
	'---tflow_path---':LPATH['tflow_path'],
	'---mounts---':MOUNTS['mounts'],
	'---imloc---':LPATH['im_path'],
	'---data_base---':SPATH['data_path'],
	'---outputpath---':SPATH['output_path'],
	'---pid---':PID,
	'---wpath---':SPATH['work_path'],
	'---output_spaces---':FMRIPREP['output_spaces'],
	'---mem_mb---':FMRIPREP['mem_mb'],
	'---ot---':FMRIPREP['ot'],
	'---nt---':FMRIPREP['nt'],
	'---fsdir---':SPATH['fs_path'],
	'---fsli---':SPATH['fsli_path'],
	'---optionals---':FMRIPREP['optionals']
	}
	print(RE_dict)

	jobscript = open(LPATH['jobscript_path'])
	working_string = jobscript.read()
	jobscript.close()



	# Populate the template with the relevant information for this participant.
	for e in RE_dict:
		rS = re.compile(e)
		working_string = re.sub(rS, RE_dict[e], working_string)
		of = open(LPATH['jobscript_current_path'],'w')
		of.write(working_string)
		of.close()

	# Execute, or just write the file. 
	
	if EX['execute']:
		os.system(EX['execute_type'] + ' ' + LPATH['jobscript_current_path'])
