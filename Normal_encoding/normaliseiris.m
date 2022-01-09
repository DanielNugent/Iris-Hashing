% normaliseiris - performs normalisation of the iris region by
% unwraping the circular region into a rectangular block of
% constant dimensions.
%
% Usage: 
% [polar_array, polar_noise] = normaliseiris(image, x_iris, y_iris, r_iris,...
% x_pupil, y_pupil, r_pupil, eyeimage_filename, radpixels, angulardiv)
%
% Arguments:
% image                 - the input eye image to extract iris data from
% x_iris                - the x coordinate of the circle defining the iris
%                         boundary
% y_iris                - the y coordinate of the circle defining the iris
%                         boundary
% r_iris                - the radius of the circle defining the iris
%                         boundary
% x_pupil               - the x coordinate of the circle defining the pupil
%                         boundary
% y_pupil               - the y coordinate of the circle defining the pupil
%                         boundary
% r_pupil               - the radius of the circle defining the pupil
%                         boundary
% eyeImageFilename      - original filename of the input eye image
% radpixels             - radial resolution, defines vertical dimension of
%                         normalised representation
% angulardiv            - angular resolution, defines horizontal dimension
%                         of normalised representation
%
% Output:
% polar_array
% polar_noise
%
% Author: 
% Libor Masek
% masekl01@csse.uwa.edu.au
% School of Computer Science & Software Engineering
% The University of Western Australia
% November 2003

function [polar_array, polar_noise] = normaliseiris(eyeImage, x_iris, y_iris, ...
    r_iris, x_pupil, y_pupil, r_pupil, eyeImageFilename, radpixels, angulardiv)

radiuspixels = radpixels + 2;

angleStepSize = (2*pi)/angulardiv;
theta = 0:angleStepSize:(2*pi)-angleStepSize; % Range should be half closed

x_iris = double(x_iris);
y_iris = double(y_iris);
r_iris = double(r_iris);

x_pupil = double(x_pupil);
y_pupil = double(y_pupil);
r_pupil = double(r_pupil);

% Calculate displacement of pupil center from the iris center
ox = x_pupil - x_iris;
oy = y_pupil - y_iris;

if ox == 0 && oy > 0
    sgn = 1;
elseif ox <= 0
    sgn = -1;
else
    sgn = 1;
end

alpha = ones(1, angulardiv) * (ox^2 + oy^2);

% Need to do something for ox = 0
if ox == 0
    phi = pi/2;
else
    phi = atan(oy/ox);
end

beta = sgn .* cos(pi - phi - theta);

% Calculate radius around the iris as a function of the angle
r = (sqrt(alpha) .* beta) + sqrt( alpha .* (beta.^2) - (alpha - (r_iris^2)) );

r = r - r_pupil;

rmat = ones(radiuspixels, 1) * r;

rmat = rmat .* (ones(angulardiv, 1) * (0:1/(radiuspixels-1):1))';
rmat = rmat + r_pupil;


% Exclude values at the boundary of the pupil iris border, and the iris scelra border
% as these may not correspond to areas in the iris region and will introduce noise.
% ie don't take the outside rings as iris data.
rmat  = rmat(2:(radiuspixels-1), :);

% Calculate cartesian location of each data point around the circular iris
% region
xcosmat = ones(radiuspixels-2, 1) * cos(theta);
xsinmat = ones(radiuspixels-2, 1) * sin(theta);

xo = rmat .* xcosmat;    
yo = rmat .* xsinmat;

xo = x_pupil + xo;
yo = y_pupil - yo;

%saveNormalisationImage(eyeImage, x_iris, y_iris, r_iris, x_pupil, y_pupil, ...
%    r_pupil, xo, yo, eyeImageFilename);

% Extract intensity values into the normalised polar representation through
% interpolation
[x,y] = meshgrid(1:size(eyeImage,2), 1:size(eyeImage,1));
polar_array = interp2(x, y, eyeImage, xo, yo);

% Create noise array with location of NaNs in polar_array
polar_noise = zeros(size(polar_array));
coords = isnan(polar_array);
polar_noise(coords) = 1;

polar_array = double(polar_array)./255;

% Replace NaNs before performing feature encoding
coords = isnan(polar_array);
avg = mean(polar_array, 'all', 'omitnan');
polar_array(coords) = avg;

return




% Run diagnostics, writing out eye image with rings overlayed
function saveNormalisationImage(eyeImage, x_iris, y_iris, r_iris, x_pupil, ...
    y_pupil, r_pupil, xo, yo, eyeimage_filename)

global DIAGPATH

% Get rid of outling points in order to write out the circular pattern
invalid = xo > size(eyeImage, 2);
xo(invalid) = size(eyeImage, 2);
invalid = xo < 1;
xo(invalid) = 1;

invalid = yo > size(eyeImage,1);
yo(invalid) = size(eyeImage,1);
invalid = yo < 1;
yo(invalid) = 1;

xo = round(xo);
yo = round(yo);

eyeImage = uint8(eyeImage);

pointIndexes = sub2ind(size(eyeImage), yo, xo);
eyeImage(pointIndexes) = 255;

% Get pixel coords for circle around iris
[x, y] = circlecoords([x_iris, y_iris], r_iris, size(eyeImage));
outerBorder = sub2ind(size(eyeImage), double(y), double(x));
eyeImage(outerBorder) = 255;

% Get pixel coords for circle around pupil
[xp, yp] = circlecoords([x_pupil, y_pupil], r_pupil, size(eyeImage));
innerBorder = sub2ind(size(eyeImage), double(yp), double(xp));
eyeImage(innerBorder) = 255;

% Write out rings overlaying original iris image
w = cd;
cd(DIAGPATH);
imwrite(eyeImage, [eyeimage_filename,'-normal.jpg'],'jpg');
cd(w);

return
