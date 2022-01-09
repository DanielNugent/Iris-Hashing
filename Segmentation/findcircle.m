% findcircle - returns the coordinates of a circle in an image using the
% Hough transform and Canny edge detection to create the edge map.
%
% Usage: 
% [row, col, radius] = findcircle(im, lowerRadius, upperRadius, scaling, 
%                            sigma, highThresh, lowThresh, verticalWeight, 
%                            horizontalWeight)
%
% Arguments:
%	im              - the image in which to find circles
%	lowerRadius		- lower radius to search for
%	upperRadius		- upper radius to search for
%	scaling		    - scaling factor for speeding up the
%			          Hough transform
%	sigma		    - amount of Gaussian smoothing to
%			          apply for creating edge map.
%	highThresh		    - threshold for creating edge map
%	lowThresh	    - threshold for connected edges
%	verticalWeight	- vertical edge contribution (0-1)
%	horizontalWeight - horizontal edge contribution (0-1)
%	
% Output:
%	row             - row of the circle's centre
%	col             - col of the circle's centre
%	radius          - radius of the circle
%
% Author: 
% Libor Masek
% masekl01@csse.uwa.edu.au
% School of Computer Science & Software Engineering
% The University of Western Australia
% November 2003

function [row, col, radius] = findcircle(im, lowerRadius, upperRadius, scaling, ...
    sigma, highThresh, lowThresh, verticalWeight, horizontalWeight)

lowerRadiusScaled = round(lowerRadius*scaling);
upperRadiusScaled = round(upperRadius*scaling);

% Generate the edge image.
[I2, orientation] = canny(im, sigma, scaling, verticalWeight, horizontalWeight);
I3 = adjgamma(I2, 1.9);
I4 = nonmaxsup(I3, orientation, 1.5);
edgeImage = hysthresh(I4, highThresh, lowThresh);

% Find the maximum in the Hough space, and hence the parameters of the circle.
[row, col, radius] = getHoughCircle(edgeImage, lowerRadiusScaled, upperRadiusScaled);

% Rescale radius and coordinates
radius = radius(1) / scaling;
col = int32(col(1) / scaling);
row = int32(row(1) / scaling);
