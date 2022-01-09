% linecoords - returns the x y coordinates of positions along a line
%
% Usage: 
% [x,y] = linecoords(lines, imSize)
%
% Arguments:
%	lines       - an array containing parameters of the line in
%                 form a*x + b*y + c where a, b and c are the three
%                 elements in the array
%   imSize      - size of the image, needed so that x y coordinates
%                 are within the image boundary
%
% Output:
%	xCoords     - x coordinates
%	yCoords     - corresponding y coordinates
%
% Author: 
% Libor Masek
% masekl01@csse.uwa.edu.au
% School of Computer Science & Software Engineering
% The University of Western Australia
% November 2003

function [xCoords, yCoords] = linecoords(lines, imSize)

xCoords = 1:imSize(2);
yCoords = (-lines(3) - lines(1)*xCoords ) / lines(2);

invalid = yCoords > imSize(1);
yCoords(invalid) = imSize(1);
invalid = yCoords < 1;
yCoords(invalid) = 1;

xCoords = int32(xCoords);
yCoords = int32(yCoords);

return
