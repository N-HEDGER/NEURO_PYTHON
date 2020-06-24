# Running fmriprep on a HPC using slurm and singularity.

The purpose of this vignette is to illustrate how to get *fmriprep* working via *singularity* on the *Reading academic computing cluster* (RACC).


## Definitions.


### Fmriprep

[fmriprep](https://fmriprep.org/en/stable/index.html) is a pipeline for minimal pre-processing of fMRI data. It is very robust and follows state-of-the-art practices.   

### Slurm

[Slurm](https://slurm.schedmd.com/documentation.html) is the workload manager that the computing cluster uses to manage jobs.


### Singularity 

[Singularity](https://singularity.lbl.gov/) is a piece of software installed in the computing cluster. It allows users to create and run containerised images that contain scientific workflows (such as fmriprep). 

### RACC

The [RACC](https://research.reading.ac.uk/act/knowledgebase/academic-cluster-service/) is Reading's Linux cluster that has a good computing power. 



## Step by step guide.


### 1. Creating a singlarity image.

 First of all, you will need to create an fmriprep singularity image. The recomended way of doing this is to perform this on your local computer (i.e. not on the cluster) using docker2singularity. 

First, you will need [docker](https://www.docker.com/) installed and running on your system.


With this all in order, you can run the following command.


 *For windows*:

```bash
docker run --privileged -t --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v <insert output path here>:/output \
    singularityware/docker2singularity \
    poldracklab/fmriprep:<version>

```

For *Unix*:

```bash
docker run --privileged -t --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v <insert output path here>:/output \
    singularityware/docker2singularity \
    poldracklab/fmriprep:<version>

```

To save yourself some time, please note that you will need to get rid of the backslashes at the end of each line. These will be expected on windows, but not unix. 


### 2. Sending the singularity image to the RACC.

2. Once you have created the image, you should have a .simg file (a singularity image). You should transfer this to the computing cluster using *rsync* or *scp*.


For instance, the general recipe for this would be as follows

```bash

scp <localpathtoimagehere> <yourusernamehere>@cluster.act.rdg.ac.uk:<desiredlocationfortheimagehere>

```

Now you should log into the cluster, as we need to spend some time preparing the envirnoment here. If you are unfamiliar with ssh and the cluster environment, then you can read up on it [here](https://research.reading.ac.uk/act/knowledgebase/academic-cluster-usage/)


### 3. Setting up a templateflow directory on the cluster.


Templateflow allows you (and more importantly, fmriprep) to access a set of standard neuroimaging templates (e.g. the MNI brain, fsaverage etc). fmriprep will first look for these files on your system. If it can't find them, then it will try to download them.

The problem is, something on the cluster will prevent the fmriprep singularity image from downloading these files reliably. Therefore, you will need to prepare the templates that you need yourself.

First, you will need to follow these instructions to prepare a python environment on the cluster.

https://research.reading.ac.uk/act/knowledgebase/python-on-the-academic-computing-cluster/


Then, use pip to install templateflow in this environment
```bash
pip install templateflow
```

Next, you will need to install the relevent templates that you need.

At a minimum, you should install the OASIS30ANTs template, since fmriprep uses this as part of its workflow.

In addition, you should install whatever output spaces (i.e. anything you list under 'output_spaces' in your call to fmriprep) you want your data sampled to.

 Here for instance, I grab an MNI template and fsaverage for outputing the data to surface space. 

```python

import templateflow.api as api
api.get(['MNI152NLin2009cAsym', 'OASIS30ANTs', 'fsaverage'])

```

*In the longer term, it may be useful to have 1 shared location for all of these templates, so we dont have everyone downloading them and consuming space*


### 4. Perform some tests of the image.

Now, we can perform a series of tests to make sure that everything is working as intended. These are also listed [here](https://fmriprep.org/en/stable/singularity.html)

Firstly, try this.

```bash
singularity shell -B <path to your BIDS data here>:/data <path to your singularity image here>

ls /data

bids-validator /data
```

Here, we mount our data directory onto /data in the singularity image.

Therefore, once we open the singularity shell (1st line) a call to 'ls' should list the contents of out data directory.

We also (3rd line) use the bids-validator here to check the validity of our data. This is a useful way of making sure that our fmriprep call will run. 

To exit the singularity shell, simply type. 


```bash
exit
```

As a second test, try this:

```bash
singularity shell -B <path to a directory here>:/out <path to your singularity image here>

touch /out/test

ls /out
```

Here, you should see that you were able to write a file called 'test'. If this works, then you have write permissions.

Now delete this and exit.

```bash
rm /out/test
exit
```

### 5. Modify and run some version of my script.

In the same directory downstream of this readme, you will find 2 scripts.

You will be able to download versions of these scripts via:

```bash
wget https://raw.githubusercontent.com/N-HEDGER/NEURO_PYTHON/master/FMRIPREP_SINGULARITY_SLURM/scripts/make_fmriprep_jobscript.py

wget https://raw.githubusercontent.com/N-HEDGER/NEURO_PYTHON/master/FMRIPREP_SINGULARITY_SLURM/scripts/fmriprep_base.sh

```

Or, if you know what you are doing, you can use git to clone the entire repository. 


[fmriprep_base.sh](/FMRIPREP_SINGULARITY_SLURM/scripts/fmriprep_base.sh) is a script that contains a template call to fmriprep using slurm.

You will see that the first few lines start with the prefix 'SBATCH'.

```bash
#SBATCH -N 1-1
#SBATCH --cpus-per-task=---cpus---
#SBATCH --mem-per-cpu=---memperCPU---
#SBATCH --mail-type=ALL
#SBATCH --mail-user=---email---
#SBATCH --error=---errpath---

```

This indicates that these lines are to be interpreted by slurm, our task manager.

Here, we specify the hardware that we want to run the task. For instance, we specify the number of cpus, the memory per cpu etc. etc..


The long line that begins with 'singularity run' is our call to fmriprep.

Here, we mount the relevant directories onto the singularity image, and specify a bunch of execution options for fmriprep.

You will notice that throughout the script there are a series of placeholders enclosed within dashes '--- ----'.

These placeholders will all be populated by the other script [make_fmriprep_jobscript.py](/FMRIPREP_SINGULARITY_SLURM/scripts/make_fmriprep_jobscript.py).

In this script, we first specify the participant, or list of participants that are to be fmriprepped. This should correspond to real directories within your main BIDS directory.


```python
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
```

One unique job script will be created for each participant, and so in principle, we should be able to run multiple participants in paralell (if the resources are available).


We then set a bunch of execution options, which will populate the SLURM elements of the template script shown above. Currently, I am not sure whether these values make best use of the hardware. All I can tell you is that a call to fmriprep *works* with these values. I was able to complete a job (including fressurfer) in around 20 hours. I will need to do a bit more work to determine how best to use the resources available. 

 

```python
####
## Execution options
####

EX={}

# sbatch or sh? (sbatch if using the RACC)
EX['execute_type']='sbatch'

# Send the jobs fo excution, or just write? If set to False, then you will need to submit the job manually via 'sbatch' 
EX['execute']=False

# Number of CPUs requested from SLURM.
EX['cpus']='16'

# Memory per CPU requested from SLURM.
EX['memperCPU']='4G'

# Email to send error messages to
EX['email']='nhedger1@gmail.com'
```

Note that the default value of 'execute' is false. This means that a jobscript will be created, but not executed. This is useful for checking the script before submitting it. Conversely, if set to 'True' the job will immediately be sent to the scheduler on execution.  


Next, we set local paths. All of these locations *must be existing locations* on your system. This includes:

1. The path to the singularity image
2. The path to the directory where your downloaded templateflow templates are. 
3. The path to the template script
4. The path to the directory for where you wish to produce the jobscript to be submitted to slurm.
5. The path to the BIDS directory.
6. The path to a directory for freesurfer outputs.
7. A path for fmriprep to store temporary files.
8. The path to your freesurfer license.
9. A directory to store outputs.

```python
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

```

Next, some singulaity locations are defined. There shouldn't be any real reason to change any of these.

```python
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
```

Next, some mounts are created.

1. We mount the templateflow directory onto the image.
2. We mount the freesurfer directory onto the image
3. We mount the freesurfer license onto the image

```python
MOUNTS={}

# Make the static mounts now

# Mount the templateflow directory.


# The templateflow directory is mounted. 
MOUNTS['tfmount']='-B ' +'${TEMPLATEFLOW_HOST_HOME}:${SINGULARITYENV_TEMPLATEFLOW_HOME}'

# The freesurfer directory is mounted to /fsdir
MOUNTS['fsmount']= '-B ' + LPATH['fs_path']+':'+SPATH['fs_path']

# Mount the path to the license
MOUNTS['fslmount']= '-B ' + LPATH['B_work_path'] +':'+SPATH['lipath']

```

We then define our fmriprep specific arguments. See [here](https://fmriprep.org/en/stable/usage.html) for further details

The 'optionals' input can be used to add additional arguments to the end of the call. 


```python
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
```

Finally, in the 'main loop' section, we loop through the list of participants and create some participant-specific working directories, output directories and job scripts.

```python
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
	

	# Force unique working directory according to PID.
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


	# Make unique error file for the participant (thanks Carolyn)
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

	print('Job script written to' + '' + LPATH['jobscript_current_path'])
	# Execute, or just write the file. 
	
	if EX['execute']:
		os.system(EX['execute_type'] + ' ' + LPATH['jobscript_current_path'])

```

The terminal should print a message to indicate that your jobscript has been saved in the desired location.


**TBC**



