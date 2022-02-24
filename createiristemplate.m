% createiristemplate - generates a biometric template from an iris in
% an eye image.
%
% Usage: 
% [template, mask] = createiristemplate(eyeImageFilePath, imageName)
%
% Arguments:
%	eyeImageFilePath   - the complete path to the eye image
%	imageName          - the name of the image used for labeling diagnostics
%
% Output:
%	template		   - the binary iris biometric template
%	mask			   - the binary iris noise mask
%
% Author: 
% Libor Masek
% masekl01@csse.uwa.edu.au
% School of Computer Science & Software Engineering
% The University of Western Australia
% November 2003

function [template, mask] = createiristemplate(eyeImageFilePath, imageName)

% Path for writing diagnostic images
global DIAGPATH
DIAGPATH = 'diagnostics';

% Normalisation parameters
% Can adjust these for datasets
radialRes = 28;
angularRes = 200;
% With these settings a 11200 bit iris template is created

% Feature encoding parameters
% Can adjust these for datasets
nscales=1;
minWaveLength=18;
mult=1; % not applicable if using nscales = 1
sigmaOnf=0.5;

eyeImage = imread(eyeImageFilePath);
[~, ~, img_channels]  = size(eyeImage);
if img_channels == 3
    eyeImage = rgb2gray(eyeImage);
end

savefile = ['cachedSegmentedIrises/', imageName, '-houghpara.mat'];
disp(savefile);
[stat, ~] = fileattrib(savefile);

if stat == 1
    % If this file has been processed before then load the circle
    % parameters and noise information for that file.
    load(savefile, 'irisCircle', 'pupilCircle', 'imageWithNoise');
else
    % If this file has not been processed before then perform automatic
    % segmentation and save the results to a file
    [irisCircle, pupilCircle, imageWithNoise] = segmentiris(eyeImage);
    save(savefile, 'irisCircle', 'pupilCircle', 'imageWithNoise');
end

if checkPupilWithinIris(irisCircle, pupilCircle)
    error("Pupil is not entirely within the iris");
end

% WRITE NOISE IMAGE
imageWithCircles = uint8(eyeImage);
noiseImageWithCircles = uint8(imageWithNoise);

% Get pixel coords for circle around iris
[x,y] = circlecoords([irisCircle(2), irisCircle(1)], irisCircle(3), size(eyeImage));
outerBorder = sub2ind(size(eyeImage), double(y), double(x));

% Get pixel coords for circle around pupil
[xp,yp] = circlecoords([pupilCircle(2), pupilCircle(1)], pupilCircle(3), size(eyeImage));
innerBorder = sub2ind(size(eyeImage), double(yp), double(xp));


% Write noise regions
noiseImageWithCircles(outerBorder) = 255;
noiseImageWithCircles(innerBorder) = 255;
% Write circles overlayed
imageWithCircles(outerBorder) = 255;
imageWithCircles(innerBorder) = 255;

w = cd;
cd(DIAGPATH);
imwrite(noiseImageWithCircles, strcat(imageName, '-noise.jpg'), 'jpg');
imwrite(imageWithCircles, strcat(imageName, '-segmented.jpg'), 'jpg');
cd(w);

% Perform normalisation
[polarArray, noiseArray] = normaliseiris(imageWithNoise, irisCircle(2),...
    irisCircle(1), irisCircle(3), pupilCircle(2), pupilCircle(1), pupilCircle(3),...
    imageName, radialRes, angularRes);


% WRITE NORMALISED PATTERN, AND NOISE PATTERN
w = cd;
cd(DIAGPATH);
imwrite(polarArray, strcat(imageName, '-polar.jpg'), 'jpg');
imwrite(noiseArray, strcat(imageName, '-polarnoise.jpg'), 'jpg');
cd(w);

% perform feature encoding
[template, mask] = encode(polarArray, noiseArray, nscales, minWaveLength, ...
    mult, sigmaOnf);
