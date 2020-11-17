import os.path as op
from glob import glob
import pandas as pd
import nibabel as nib

import nilearn
from nilearn import image
from nilearn import plotting
import matplotlib.pyplot as plt


class bids:

    # Initialises by generating a list of subjects/sessions/tasks. Requires only the base path to the BIDS file.
    def __init__(self,path):
        self.path=path
        self.subjects=[op.basename(s).split('-')[1] for s in
            sorted(glob(op.join(self.path, 'sub-*'))) if op.isdir(s)]

        self.submessage=f"Found {len(self.subjects)} participant(s) {self.subjects}"

        sessions = []
        sessmessage=[]
        for this_sub in self.subjects:
            these_ses = [
                op.basename(s).split('-')[1] for s in
                sorted(
                    glob(op.join(self.path, f'sub-{this_sub}', 'ses-*')))
                if op.isdir(s)
            ]

            sessmessage.append(f"Found {len(these_ses)} session(s) for sub-{this_sub} {these_ses}")
            sessions.append(these_ses)

        self.sessions=sessions
        self.sessmessage=sessmessage

        tasks=[]
        taskmessage=[]
        for this_sub, these_ses in zip(self.subjects, self.sessions):
            these_task = []
            for this_ses in these_ses:
                if this_ses is None:
                    tmp = glob(op.join(
                        self.path,
                        f'sub-{this_sub}',
                        'func',
                        f"*{'.nii'}*"
                    ))
                else:
                    tmp = glob(op.join(
                        self.path,
                        f'sub-{this_sub}',
                        f'ses-{this_ses}',
                        'func',
                        f"*{'.nii'}*"
                    ))

                these_ses_task = list(set(
                    [op.basename(f).split('task-')[1].split('_')[0]
                     for f in tmp]
                ))


                nullstring = "" if this_ses is None else f"and ses-{this_ses}"

                taskmessage.append(f"Found {len(these_ses_task)} task(s) for sub-{this_sub} {nullstring} {these_ses_task}")
                these_task.append(these_ses_task)



            self.taskmessage=taskmessage
            tasks.append(these_task)
        self.tasks=tasks

        sessions = []
        for this_sub in self.subjects:
            these_ses = [
                op.basename(s).split('-')[1] for s in
                sorted(
                    glob(op.join(self.path, f'sub-{this_sub}', 'ses-*')))
                if op.isdir(s)
            ]

    # Prints everything out.
    def elaborate(self):
        print(self.submessage)
        print(self.sessmessage)
        print(self.taskmessage)

    # Finds a func file.
    def find_funcs(self,sub,ses,task):

        ffunc_dir = op.join(self.path, f'sub-{sub}', f'ses-{ses}', 'func')

        funcs = sorted(glob(op.join(ffunc_dir, f'*task-{task}*')))
        if not funcs:
            raise ValueError(
                "Could not find functional data with the following parameters:\n"
                f"sub-{sub}, ses-{ses}, task-{task}")
        return funcs

    # Finds an anatomical file.
    def find_anats(self,sub,ses,weight):

        anat_dir = op.join(self.path, f'sub-{sub}', f'ses-{ses}', 'anat')

        anats = sorted(glob(op.join(anat_dir, f'*{weight}*')))

        if not anats:
            raise ValueError(
                "Could not find anatomical data with the following parameters:\n"
                f"sub-{sub}, ses-{ses}, weight-{weight}")

        return anats

    # Shows a file.
    def show(self,npath):

        niftifiledim=len(image.load_img(npath).shape)
        if niftifiledim == 3:
           display=plotting.view_img(npath)
        else:
            print ('>1 volume, plotting only the first for convenience')
            firstim=image.index_img(npath, 0)
            display=plotting.view_img(firstim)
        return display


    def getniftibits(self,npath):
        nifti = nib.load(npath)
        VOXSIZE = nifti.header['pixdim'][1:4]
        SHAPE= (nifti.header['dim'][1:5])
        TR = (nifti.header['pixdim'][4:5])
        VOXFRAME=pd.DataFrame(VOXSIZE)
        VOXFRAME=VOXFRAME.T
        SHAPEFRAME=pd.DataFrame(SHAPE)
        SHAPEFRAME=SHAPEFRAME.T
        VOXFRAME.columns=['VoxsizeX','VoxsizeY','VoxsizeZ']
        SHAPEFRAME.columns=['ShapeX','ShapeY','ShapeZ','Volumes']
        CFRAMEi=pd.concat([VOXFRAME,SHAPEFRAME],axis=1)
        CFRAMEi['TR'] = TR
        return(CFRAMEi)
