# IrisTemplateExtractor
Matlab code for extracting iris vector templates.

Uses Masek's iris identification code from his dissertation as a basis. However, several enhancements to the speed and efficiency have been made. Most notably the eyelid segmentation process utilised in NIST's VASIR system is implemented.

To run the code first add the two subfolders to your Matlab path. Create two other subfolders entitled "diagnostics" and "cachedSegmentedIrises". The former of these is used to store diagnostic images of the process for each image. These are useful for assessing the efficiency of the system. The latter of these caches the segmentation results for the images as this is the computationally expensive part of the code. This allows for rapid testing of experimental changes to the later stages of the system.

Setup a folder for the results at a specified location \<path to parent of results folder>/\<name of dataset>. Within this create three subfolders for Templates, Masks and MaskedTemplates. Then call exportdata(\<path to dataset folder>, \<path to parent of results folder>, \<name of dataset>). This will populate the three subfolders at \<path to parent of results folder>/\<name of dataset> with a json file for each user in the dataset.

The dataset must have a subfolder for each user. Each of these must have a subfolder for 'L' and 'R'. These can be empty or include any number of iris images for that user.

Code to compare the vector templates is not included.

There are a number of parameters throughout the code which may need to be adjusted for each dataset. These include the thresholds for detecting the iris boundaries, the radial and angular resolutions and the minimum and maximum sizes of the pupil and iris radiuses.

Authors:
Libor Masek, Peter Kovesi, Sarang Chaudhari and Philip Bradish.

References:

Libor Masek, Peter Kovesi. MATLAB Source Code for a Biometric Identification System Based on Iris Patterns. The School of Computer Science and Software Engineering, The University of Western Australia. 2003.

Y. Lee, R. J. Micheals, J. J. Filliben, and P. J. Phillips, "Vasir: an open-source research platform for advanced iris recognition technologies," Journal of research of the National Institute of Standards and Technology, vol. 118, p. 218, 2013.

