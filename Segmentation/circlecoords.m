% circlecoords - returns the pixel coordinates of a circle defined by the
%                radius and x, y coordinates of its centre.
%
% Usage: 
% [x,y] = circlecoords(c, r, imSize, nSides)
%
% Arguments:
%	c           - an array containing the centre coordinates of the circle
%	              [x, y]
%   r           - the radius of the circle
%   imSize      - size of the image matrix to plot coordinates onto
%   nSides      - the circle is actually approximated by a polygon, this
%                 argument gives the number of sides used in this
%                 approximation. Default is 600.
%
% Output:
%	x		    - an array containing x coordinates of circle boundary
%	              points
%   y		    - an array containing y coordinates of circle boundary
%                 points
%
% Author: 
% Libor Masek
% masekl01@csse.uwa.edu.au
% School of Computer Science & Software Engineering
% The University of Western Australia
% November 2003

function [xCoords, yCoords] = circlecoords(c, r, imSize, nSides)

if nargin == 3
    nSides = 600;
end

nSides = round(nSides);

a = 0:pi/nSides:2*pi;
xCoords = (double(r)*cos(a) + double(c(1)));
yCoords = (double(r)*sin(a) + double(c(2)));

xCoords = round(xCoords);
yCoords = round(yCoords);

%get rid of values outside range of the image
valid = xCoords > imSize(2);
xCoords(valid) = imSize(2);
valid = xCoords < 1;
xCoords(valid) = 1;

valid = yCoords > imSize(1);
yCoords(valid) = imSize(1);
valid = yCoords < 1;
yCoords(valid) = 1;

xCoords = int32(xCoords);
yCoords = int32(yCoords);

return
