# fMRI software
The amount of data handling and pre-processing involved in fMRI analysis can be quite intimidating.

What options do we have available to help us with all this?

Currently, there is a huge range of software packages for fMRI analysis. Well-known examples include FSL, SPM, Freesurfer and many more.

![alt text](https://i.imgbox.com/FOp1JK5t.png "Title")

On the surface, this wide array of choices seems like a good thing, but it is actually associated with a range of issues.

### No unifying operating interface

The first problem is that these different software packages are interfaced with in fundamentally different ways. For instance:

* We interact with FSL, Freesurfer and AFNI commands via shell scripting.
* SPM is implemented in MATLAB
* Other options such as Nipy and Nilearn are implemented in Python.

This means that there is no unifying operating interface - we have to use different applications and programming languages.

To make matters worse, some software packages do not work on some operating systems. For instance, it isn't easy to get FSL and freesurfer to work on windows.

### The learning curve

Another issue associated with all this is the substantial learning curve involved.

Each of these software packages have their own quirks, parameters and usages that require extensive time and interaction to learn.

For instance, someone that wanted to use both SPM and FSL would have to learn both MATLAB and UNIX programming, which is a non-trivial task. In the context of a PhD for instance, this could take up a substantial chunk of your time. 

Perhaps because of this, researchers tend to remain ‘loyal’ to a particular software package, to avoid investing the time involved in learning how to use more than one.

This is bad practice, because some software packages are proven to be better at some aspects of pre-processing than others.

For instance, unbiased tests have shown that ANTs is found to be far superior to FSL at normalization, but many people would be reluctant to learn ANTS for just one task if they have already invested their time in learning FSL.

### Lack of transparency

Another problem that is produced is a lack of transparency in fMRI analyses.

The method sections in fMRI papers are often quite opaque and it can be very difficult to effectively share your analyses with other people, particularly if your workflow involved lots of different software packages.

This makes reproducing and replicating results even harder. 

# Nipype 

So you may have noticed that I am painting a fairly bleak picture here.

This is where Nipype comes in.

Nipype is a framework that allows you to interface with a number of different fMRI software packages within a single python script. 

The syntax of a Nipype script is actually very straightforward.  

Firstly, you import *interfaces* (these are your software packages, such as FSL, SPM and so on).

Next, you define *nodes* (these are the particular processes performed by the interfaces, like spatial smoothing, slice timing correction and so on).

As a next step, you define *inputs* for your nodes (for instance, the volume that you want to perform the spatial smoothing on).

Next, you can connect nodes together to form a *workflow*. For instance, I may want to perform slice timing correction with FSL and then spatial smoothing with SPM.

Finally, you run the workflow.

## A simple Nipype script.

Its probably useful to give an example of a Nipype script. 

![alt text](https://i.imgbox.com/baD5T4K1.png "Title")

Here I have given a very simple one, which is just 10 lines of code.

1. In this first section, I import the interfaces. In this case, I import dicom to nifti, which is a file converter and I also import fsl

2. Next, I define some nodes. I import the dicom to nifti converter from the dicom to nifti interface and I import a function that reorients volumes from the fsl interface

3. In this next section, I provide some inputs to the nodes, such as where the DICOM files can be found.

4. Next, I connect the nodes together into a workflow, so that once my data are converted by dicom to nifti, they will be reoriented by fsl

5. Finally I run the workflow.

Nipype then produces several outputs:

![alt text](https://i.imgbox.com/IrZkdgNV.png "Title")

It produces an intuitively appealing graph, that displays the workflow.

Nipype then produces a folder for each node. /CONVERTED contains the converted nifti file and /REORIENTED contains the reoriented and converted nifti file.

This is obviously a very straightforward workflow, but we can extend this example to form a full pre-processing pipeline for fMRI data. 

The example below takes a folder of DICOM files as input (fresh from the scanner), performs conversion to nifti, slice timing correction, motion correction, brain extraction, spatial smoothing and high pass temporal filtering. The final output is a nifti file that is fully-preprocessed and ready for a first level analysis. 

![alt text](https://i.imgbox.com/XRj6zpoZ.png "Title")

One nice feature of the workflow is that it is fully customised - dcm2nii is employed for converting the data, FSL commands are employed for slice timing correction and motion correction, AFNI commands are employed for despiking and smoothing the data and the python module 'nilearn' is employed for plotting the outputs at various stages. 


## Relation to fmriprep

fmriprep is a popular application for pre-processing fmri data that uses a nipype framework. It is very good. In fact, it is so robust that it almost renders moot the idea of trying to create your own pipelines.

However, fmriprep is minimal, by design. There may still be further stages of pre-processing that you might like to perform that fmriprep does not handle (detrending, smoothing, converting to percent signal change, averaging across runs etc). 

nipype offers a flexible way of doing this. 


