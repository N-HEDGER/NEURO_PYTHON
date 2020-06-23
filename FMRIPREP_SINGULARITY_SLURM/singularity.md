# Running fmriprep on a HPC using slurm and singularity.

The purpose of this vignette is to illustrate how to get fmriprep working on a HPC such as the Reading academic computing cluster (RACC).


## Definitions.

### Slurm

Slurm is the workload manager that the computing cluster uses to manage jobs.

https://slurm.schedmd.com/documentation.html

### Singularity 

Singularity is a piece of software installed in the computing cluster. It allows users to create and run containerised images that contain scientific workflows (such as fmriprep). 

https://singularity.lbl.gov/


## Step by step guide.


### 1. Creating a singlarity image.

 First of all, you will need to create an fmriprep singularity image. The recomended way of doing this is to perform this on your local computer (i.e. not on the cluster) using docker2singularity. 

First, you will need docker installed and running on your system.

https://www.docker.com/

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

Now you should log into the cluster, as we need to spend some time preparing the envirnoment here. If you are unfamiliar with ssh and the cluster environment, then you can read up on it here: https://research.reading.ac.uk/act/knowledgebase/academic-cluster-usage/


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

In addition, you should install whatever output spaces you want your data sampled to. Here for instance, I grab an MNI template and fsaverage for outputing the data to surface space. 

```python

import templateflow.api as api
api.get(['MNI152NLin2009cAsym', 'OASIS30ANTs', 'fsaverage'])

```

### 4. Perform some tests of the image.

Now, we can perform a series of tests to make sure that everything is working as intended. These are also listed here:

https://fmriprep.org/en/stable/singularity.html

Firstly, try this.

```bash
singularity shell -B <path to your data here>:/data <path to your singularity image here>

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

Here, you should see that you were able to write a file called 'test'. Id this works, then you have write permissions.

Now delete this and exit.

```bash
rm /out/test
exit
```

### 5. Modify and run some version of my script.


In the same directory as this readme, you will find 2 scripts.

One of the scripts









