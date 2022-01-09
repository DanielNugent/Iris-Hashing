% houghcircle - takes an edge map image, and performs the Hough transform
% to find the row, column and radius of the best fit circle.
%
% Usage:
% [row, col, radius] = houghcircle(edgeIm, rmin, rmax)
%
% Arguments:
%	edgeIm      - the edge map image to be transformed
%   rMin, rMax  - the minimum and maximum radius values
%                 of circles to search for
% Output:
%	row         - the row of the circle centre point
%   col         - the col of the circle centre point
%   radius      - the radius of the circle centre point
%
% Author:
% Libor Masek
% masekl01@csse.uwa.edu.au
% School of Computer Science & Software Engineering
% The University of Western Australia
% November 2003
% Reworked and updated for efficiency
% Philip Bradish
% Trinity College Dublin
% July 2021

function [row, col, radius] = getHoughCircle(edgeIm, rMin, rMax)
% For each edge point, draw circles of different radii
% to get all the centre points it intersects with
% Performance critical code so it had been optimised for speed rather 
% than readibility
[rows, cols] = size(edgeIm);
nradii = rMax-rMin+1;
hSpace = nradii * rows * cols;

[edgeYs, edgeXs] = find(edgeIm~=0);

radiuses = rMin:rMax;
% Get max x value for each radius
maxXValues = fix(radiuses/(sqrt(2)));
highestMaxX = max(maxXValues);
% The x values used can never be higher than the highest max x value
xRange = 0:highestMaxX;
% Get grid of all the x values and the corresponding radiuses
[rRanges, xRanges] = meshgrid(radiuses, xRange);
% Remove all x values which are outside the range for that radius
valid = xRange(:) <= maxXValues;
x = xRanges(valid);
correspondingRadiuses = rRanges(valid);

% Get y values
costheta = sqrt(1 - ((x .^2) ./ (correspondingRadiuses .^ 2)));
y = round(correspondingRadiuses .* costheta);

% Now fill in the 8-way symmetric points on a circle for each edge
% point to get all centre coordinates each edge and radius pair intersects with
x = x';
y = y';
centreYs = edgeYs + [x  y  y  x -x -y -y -x];
centreXs = edgeXs + [y  x -x -y -y -x  x  y];
% Adjust the corresponding radius matrix so it corresponds to the size of
% the centre points matrices
correspondingRadiuses = repmat(correspondingRadiuses', size(edgeXs, 1), 8);

% Cull points that are outside limits
valid = centreYs>=1 & centreYs<=rows & centreXs>=1 & centreXs<=cols;

centreYs = centreYs(valid);
centreXs = centreXs(valid);
correspondingRadiuses = correspondingRadiuses(valid);

% Normalise the radius so that it can be used as an index
normalisedRadiuses = correspondingRadiuses - rMin + 1;

% Convert x, y, radius coordinates into a single number
indexes = sub2ind([rows, cols, nradii], centreYs, centreXs, normalisedRadiuses);
% Count occurances of each index in the hough space
[counts] = histcounts(indexes, 1:hSpace);
% Get index of largest count and convert it back into row, col and radius
% form
[~, ind] = max(counts);
[row, col, radius] = ind2sub([rows, cols, nradii], ind);
radius = radius + rMin - 1;
return
