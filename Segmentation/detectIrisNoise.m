% removeIrisNoise - Removes noise from the iris
%
% Usage:
% function imagewithnoise = removeIrisNoise(eyeImage, circleIris, circlePupil)
%
% Arguments:
%           eyeImage        - image of the iris.
%           circleIris      - Array containing x and y coordinates of the
%                             iris' centre and its radius
%           circlePupil     - Array containing x and y coordinates of the
%                             pupil's centre and its radius
% Output:
%           imageWithNoise	- image with all noise marked as NaN values
%
% Author: Philip Bradish
% July 2021

function imageWithNoise = detectIrisNoise(eyeImage, circleIris, circlePupil)

% Unpack the arrays for readability
irisRow = double(circleIris(1));
irisCol = double(circleIris(2));
irisRadius = double(circleIris(3));
pupilRow = double(circlePupil(1));
pupilCol = double(circlePupil(2));
pupilRadius = double(circlePupil(3));

imgSize = size(eyeImage);
irisRowLower = max(1, round(irisRow-irisRadius));
irisRowUpper = min(imgSize(1), round(irisRow+irisRadius));
irisColumnLower = max(1, round(irisCol-irisRadius));
irisColumnUpper = min(imgSize(2), round(irisCol+irisRadius));

% Get boundary points of the top and bottom eyelids
topBoundaryPoints = removeEyelid(eyeImage, irisColumnLower, irisCol, ...
    irisColumnUpper, irisRadius, irisRowLower, pupilRow-pupilRadius, 0);

heightOfBottomExaminedArea = irisRowUpper - (pupilRow+pupilRadius) + 1;
bottomBoundaryPoints = removeEyelid(eyeImage, irisColumnLower, irisCol, ...
    irisColumnUpper, irisRadius, pupilRow+pupilRadius, irisRowUpper, ...
    heightOfBottomExaminedArea);

% Remove all points outside boundary points
validIris = logical(eyeImage);
xs = irisColumnLower:irisColumnUpper;
for ind = 1:size(xs, 2)
    x = xs(ind);
    topBoundaryPoint = topBoundaryPoints(ind);
    bottomBoundaryPoint = bottomBoundaryPoints(ind);

    validIris(1:ceil(topBoundaryPoint), x) = false;
    validIris(floor(bottomBoundaryPoint):end, x) = false;
end

% Further processing to try to remove pixels which aren't part of the iris
imageWithNoise = double(eyeImage);

[columnsInImage, rowsInImage] = meshgrid(1:size(eyeImage,2), 1:size(eyeImage,1));

pupilRegion = (rowsInImage - pupilRow).^2 ./ pupilRadius^2 ...
    + (columnsInImage - pupilCol).^2 ./ pupilRadius^2 <= 1;

irisRegion = (rowsInImage - irisRow).^2 ./ irisRadius^2 ...
    + (columnsInImage - irisCol).^2 ./ irisRadius^2 <= 1;
irisRegion(pupilRegion) = false;

validIris = validIris & irisRegion;

imageWithNoise(~validIris) = NaN;

avg = mean(imageWithNoise, 'all', 'omitnan');
stdeviation = std(imageWithNoise, 0, 'all', 'omitnan');

% Adjust these values for datasets
% Set minimum values to prevent large portions of the iris from being
% classified as noise in the event the stdeviation is very small
upperThreshold = max(2 * stdeviation, 35);
lowerThreshold = max(2 * stdeviation, 35);

noiseFlags = ~logical(validIris);
noiseFlags(pupilRegion) = false;
% Mark anything outside thresholds as noise
noiseFlags(validIris) = imageWithNoise(validIris) > avg + upperThreshold |...
    imageWithNoise(validIris) < avg - lowerThreshold;
% Remove corrupt areas of the iris which are not connected to edges of the
% the iris since all eyelashes and eyelids must begin outside the iris
% region
uncorruptRegions = imfill(~noiseFlags, 'holes');

% Remove extreme outliers which are caused by reflections and
% missclassified sections of the pupil
uncorruptRegions = uncorruptRegions & imageWithNoise >= 40 & ...
    imageWithNoise <= 250;

imageWithNoise(~uncorruptRegions) = NaN;
return



% Helper function to detect and remove eyelid
function boundaryPoints = removeEyelid(eyeImage, irisColumnLower, irisCol, ...
    irisColumnUpper, irisRadius, eyelidMin, eyelidMax, defualtBoundary)

sampleX = [irisColumnLower, irisCol, irisColumnUpper];
sampleY = [defualtBoundary, defualtBoundary, defualtBoundary];

if eyelidMin < eyelidMax
    % Split iris in three and find eyelid for each of them
    irisThird = round((irisRadius * 2)/3);

    eyelidLeft = eyeImage(eyelidMin:eyelidMax, ...
        irisColumnLower:irisColumnLower+irisThird);
    linesLeft = findline(eyelidLeft);
    if size(linesLeft, 1) > 0
        [~, yLeft] = linecoords(linesLeft, size(eyelidLeft));
        sampleY(1) = yLeft(1);
    end

    eyelidCentre = eyeImage(eyelidMin:eyelidMax, irisColumnLower + ...
        irisThird + 1:irisColumnLower + (2*irisThird));
    linesCentre = findline(eyelidCentre);
    if size(linesCentre, 1) > 0
        [~, yCentre] = linecoords(linesCentre, size(eyelidCentre));
        sampleY(2) = yCentre(round(size(yCentre, 2)/2));
    end

    eyelidRight = eyeImage(eyelidMin:eyelidMax, irisColumnLower + ...
        (2*irisThird) + 1:irisColumnUpper);
    linesRight = findline(eyelidRight);
    if size(linesRight, 1) > 0
        [~, yRight] = linecoords(linesRight, size(eyelidRight));
        sampleY(3) = yRight(end);
    end
end

% Combine three sides of the eyelid
irisColumns = irisColumnLower:irisColumnUpper;
boundaryPoints = interp1(double(sampleX), double(sampleY), irisColumns);
boundaryPoints = boundaryPoints + eyelidMin;
return
