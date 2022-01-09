% segmentiris - peforms automatic segmentation of the iris region
% from an eye image. Also isolates noise areas such as occluding
% eyelids and eyelashes.
%
% Usage: 
% [circleIris, circlePupil, imageWithNoise] = segmentiris(image)
%
% Arguments:
%	eyeimage		- the input eye image
%	
% Output:
%	circleIris	    - centre coordinates and radius
%			          of the detected iris boundary
%	circlePupil	    - centre coordinates and radius
%			          of the detected pupil boundary
%	imageWithNoise	- original eye image, but with
%			          location of noise marked with
%			          NaN values
%
% Author: 
% Libor Masek
% masekl01@csse.uwa.edu.au
% School of Computer Science & Software Engineering
% The University of Western Australia
% November 2003

function [circleIris, circlePupil, imageWithNoise] = segmentiris(eyeImage)

% Define range of pupil & iris radii
% Should adjust these for the dataset

%CASIA Interval
lowerPupilRadius = 25;
upperPupilRadius = 70;
lowerIrisRadius = 75;
upperIrisRadius = 120;

%CASIASyn
%lowerPupilRadius = 30;
%upperPupilRadius = 65;
%lowerIrisRadius = 65;
%upperIrisRadius = 120;

%IITD
%lowerPupilRadius = 30;
%upperPupilRadius = 65;
%lowerIrisRadius = 65;
%upperIrisRadius = 125;


% Define scaling factor, thresholds and weights.
scaling = 0.4;
sigma = 2;
highThresh = 0.2;   % Interval - 0.2, IITD - 0.2, Synthetic - 0.2
lowThresh = 0.18;   % Interval - 0.18, IITD - 0.18, Synthetic - 0.19
verticalWeight = 1;
horizontalWeight = 0;

% Find the iris boundary
[irisRow, irisCol, irisRadius] = findcircle(eyeImage, lowerIrisRadius, upperIrisRadius, ...
    scaling, sigma, highThresh, lowThresh, verticalWeight, horizontalWeight);

circleIris = [irisRow irisCol irisRadius];

irisRow = double(irisRow);
irisCol = double(irisCol);
irisRadius = double(irisRadius);

imgSize = size(eyeImage);

irisRowLower = max(1, round(irisRow-irisRadius));
irisRowUpper = min(imgSize(1), round(irisRow+irisRadius));
irisColumnLower = max(1, round(irisCol-irisRadius));
irisColumnUpper = min(imgSize(2), round(irisCol+irisRadius));

% To find the inner pupil, use just the region within the previously
% detected iris boundary
imagepupil = eyeImage(irisRowLower:irisRowUpper, irisColumnLower:irisColumnUpper);

% Define scaling factor, thresholds and weights.
scaling = 1;
sigma = 2;
highThresh = 0.25;
lowThresh = 0.25;
verticalWeight = 1;
horizontalWeight = 1;

%find pupil boundary
[pupilRow, pupilCol, pupilRadius] = findcircle(imagepupil, lowerPupilRadius, ...
    upperPupilRadius, scaling, sigma, highThresh, lowThresh, verticalWeight, ...
    horizontalWeight);

pupilRow = round(double(irisRowLower) + double(pupilRow));
pupilCol = round(double(irisColumnLower) + double(pupilCol));
pupilRadius = round(double(pupilRadius));

circlePupil = [pupilRow pupilCol pupilRadius];

imageWithNoise = detectIrisNoise(eyeImage, circleIris, circlePupil);

return
