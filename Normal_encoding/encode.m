% encode - generates a biometric template from the normalised iris region,
% also generates corresponding noise mask
%
% Usage: 
% [template, mask] = encode(polarArray, noiseArray, nscales,...
% minWaveLength, mult, sigmaOnf)
%
% Arguments:
% polarArray        - normalised iris region
% noiseArray        - corresponding normalised noise region map
% nscales           - number of filters to use in encoding
% minWaveLength     - base wavelength
% mult              - multicative factor between each filter
% sigmaOnf          - bandwidth parameter
%
% Output:
% template          - the binary iris biometric template
% mask              - the binary iris noise mask
%
% Author: 
% Libor Masek
% masekl01@csse.uwa.edu.au
% School of Computer Science & Software Engineering
% The University of Western Australia
% November 2003

function [template, mask] = encode(polarArray, noiseArray, nscales, ...
    minWaveLength, mult, sigmaOnf)

% convolve normalised region with Gabor filters
[E0, filtersum] = gaborconvolve(polarArray, nscales, minWaveLength, mult, sigmaOnf);

templateWidth = size(polarArray, 2) * 2 * nscales;

template = zeros(size(polarArray, 1), templateWidth);

polarWidth = size(polarArray, 2);
rows = 1:size(polarArray, 1);

mask = zeros(size(template));

for k = 1:nscales
    
    E1 = E0{k};
    
    %Phase quantisation
    H1 = real(E1) > 0;
    H2 = imag(E1) > 0;
    
    % if amplitude is close to zero then
    % phase data is not useful, so mark off
    % in the noise mask
    H3 = abs(E1) < 0.0001;
    
    
    for i = 0:(polarWidth-1)
        colOffset = double(2 * nscales * (i));

        %construct the biometric template
        template(rows, colOffset+(2*k)-1) = H1(rows, i+1);
        template(rows, colOffset+(2*k)) = H2(rows, i+1);
        
        %create noise mask
        mask(rows, colOffset+(2*k)-1) = noiseArray(rows, i+1) | H3(rows, i+1);
        mask(rows, colOffset+(2*k)) =   noiseArray(rows, i+1) | H3(rows, i+1);
    end
    
end
return
