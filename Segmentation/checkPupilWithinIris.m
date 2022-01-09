% checkPupilWithinIris - Checks that the boundaries of the iris are valid
%
% Usage:
% function validBoundaries = checkPupilWithinIris(irisCircle, circlepupil)
%
% Arguments:
%           irisCircle      - centre coordinates and radius of the iris
%           pupilCircle     - centre coordinates and radius of the pupil
% Output:
%           pupilWithinIris	- boolean to indicate whether the pupil lies
%                             entirely within the iris
%
% Author: Philip Bradish
% July 2021
function pupilWithinIris = checkPupilWithinIris(irisCircle, pupilCircle)

centreDisplacement = sqrt(double((irisCircle(1) - pupilCircle(1)) ^ 2 + ...
    (irisCircle(2) - pupilCircle(2)) ^ 2));
% If the radius of the circle and the centre displacement is larger than
% than the radius of the iris than it must go outside it at some point.
pupilWithinIris = centreDisplacement + pupilCircle(3) > irisCircle(3);

return
