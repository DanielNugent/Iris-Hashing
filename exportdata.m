% exportdata - Get all iris templates from a folder of iris images
%
% Usage:
% function exportdata(directoryName, outputPath, datasetName)
%
% Arguments:
%           directoryName   - the directory name to search for iris images
%           outputPath      - the path to where the json file results should
%                             be placed
%           datasetName     - the folder located at the path which the
%                             results should be placed in. Also used to
%                             construct identifiers for the irises.
%
% Authors: Philip Bradish and Sarang Chaudhari
% February 2021
function exportdata(directoryName, outputPath, datasetName)
createDirectories(outputPath, datasetName);
directory =  dir(directoryName);

for i = 1 : length(directory)
    subDirName = directory(i).name;
    
    if(isequal(subDirName, '.') ||  isequal(subDirName, '..') ||  ~directory(i).isdir)
        continue;  
    end
    
    allTemplates = struct;
    allMasks = struct;
    allMaskedTemplates = struct;
    
    % Build full path to folders. Assumes each sub folder has a L and R
    % sub directory
    subDirPathL = fullfile(directoryName, subDirName, 'L');
    subDirPathR = fullfile(directoryName, subDirName, 'R');
    %subDirPath = fullfile(directoryName, subDirName);

    [allTemplates, allMasks, allMaskedTemplates] = getTemplatesFromFolder(...
        datasetName, subDirName, "L", subDirPathL, allTemplates, allMasks, ...
        allMaskedTemplates);
    [allTemplates, allMasks, allMaskedTemplates] = getTemplatesFromFolder(...
        datasetName, subDirName, "R", subDirPathR, allTemplates, allMasks, ...
        allMaskedTemplates);
    %[allTemplates, allMasks, allMaskedTemplates] = getTemplatesFromFolder(...
    %   datasetName, subDirName, "R", subDirPath, allTemplates, allMasks, ...
    %   allMaskedTemplates);

    templatesJson = jsonencode(allTemplates);
    outputFileName = strcat(outputPath, '\', datasetName, '\Templates\', ...
        subDirName, '.json');
    disp(outputFileName);
    fileID = fopen(outputFileName, 'w');
    fprintf(fileID, templatesJson);
    fclose(fileID);

    masksJson = jsonencode(allMasks);
    outputFileName = strcat(outputPath, '\', datasetName, '\Masks\', ...
        subDirName, '.json');
    fileID = fopen(outputFileName, 'w');
    fprintf(fileID, masksJson);
    fclose(fileID);

    maskedTemplatesJson = jsonencode(allMaskedTemplates);
    outputFileName = strcat(outputPath, '\', datasetName, '\MaskedTemplates\', ...
        subDirName, '.json');
    fileID = fopen(outputFileName, 'w');
    fprintf(fileID, maskedTemplatesJson);
    fclose(fileID);
end

return


% Helper function to get all iris templates from the left/right subfolder
function [allTemplates, allMasks, allMaskedTemplates] = ...
    getTemplatesFromFolder(datasetName, subDirName, rlIndicator, ...
        subDirPath, allTemplates, allMasks, allMaskedTemplates)

images = dir(subDirPath);
for j = 1 : length(images)
    imageName = images(j).name;

    if(isequal(imageName, '.') ||  isequal(imageName, '..' ))
        continue;
    end

    imagePath = fullfile(subDirPath, imageName);
    % Get image name without extension
    imageNameComponents = split(imageName, '.');
    imageName = imageNameComponents{1};

    try
        [template, mask] = createiristemplate(imagePath, imageName);
    catch e
        disp('Error getting iris template of ' + imagePath);
        disp(e);
        continue;
    end

    maskedTemplate = double(template & ~mask);
    maskedTemplate = reshape(maskedTemplate, [], 1);
    template = reshape(template, [], 1);
    mask = reshape(mask, [], 1);

    templateName = strcat(datasetName, "_", subDirName, "_", rlIndicator, "_", imageName);

    allTemplates.(templateName) = template';
    allMasks.(templateName) = mask';
    allMaskedTemplates.(templateName) = maskedTemplate';
end

return


% Helper function which creates the output directories if they do not exist
function createDirectories(outputPath, datasetName)
if not(isfolder(outputPath + "\" + datasetName))
    mkdir(outputPath + "\" + datasetName);
end
if not(isfolder(outputPath + "\" + datasetName + "\Templates"))
    mkdir(outputPath + "\" + datasetName + "\Templates");
end
if not(isfolder(outputPath + "\" + datasetName + "\Masks"))
    mkdir(outputPath + "\" + datasetName + "\Masks");
end
if not(isfolder(outputPath + "\" + datasetName + "\MaskedTemplates"))
    mkdir(outputPath + "\" + datasetName + "\MaskedTemplates");
end
return
