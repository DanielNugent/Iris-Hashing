% findline - returns the coordinates of a line in an image using the
% linear Hough transform and Canny edge detection to create
% the edge map.
%
% Usage: 
% lines = findline(image)
%
% Arguments:
%	im      - the input image
%
% Output:
%	lines   - parameters of the detected line in polar form
%
% Author: 
% Libor Masek
% masekl01@csse.uwa.edu.au
% School of Computer Science & Software Engineering
% The University of Western Australia
% November 2003

function lines = findline(im)

[I2, orientation] = canny(im, 2, 1, 0.00, 1.00);

I3 = adjgamma(I2, 1.9);
I4 = nonmaxsup(I3, orientation, 1.5);
edgeimage = hysthresh(I4, 0.20, 0.15);

theta = (0:179)';
[R, radialCoords] = radon(edgeimage, theta);

[maxv] = max(R, [], 'all', 'linear');
if maxv <= 25
    lines = [];
    return;
end
maxInds = find(R == maxv);
[y, x] = ind2sub(size(R), maxInds);
thetaRad = -theta(x) * pi/180;
radialDist = radialCoords(y);

lines = [cos(thetaRad), sin(thetaRad), -radialDist];

cx = (size(im, 2) / 2) - 1;
cy = (size(im, 1) / 2) - 1;
lines(:, 3) = lines(:, 3) - lines(:, 1) * cx - lines(:, 2) * cy;

return
