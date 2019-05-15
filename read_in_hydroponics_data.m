function [data] = read_in_hydroponics_data(datafile, delim, keywords)
%% READ_IN_HYDROPONICS_DATA
% Read in data using keywords, bin based on keyword, spit out matrix of
% timestamp and datapoint

fid=fopen(datafile);
raw_data = textscan(fid, ['%s',delim,'%.4f',delim,'%s',delim,'%s']);

for i = 1:numel(keywords)
    data.(keywords{i})=struct();
end

for i = 1:numel(keywords)
    index=~cellfun(@isempty, strfind(raw_data{1}, keywords{i}));
    if all(index == 0)
       continue; 
    end
    values = raw_data{2}(index, 1);
    
    data.(keywords{i})=struct('date', {raw_data{3}{index}}, ...
                              'time', {raw_data{4}{index}});
    for j = 1:sum(index)
        try
            data.(keywords{i})(j).('value') = values(j);
            data.(keywords{i})(j).datetime=datetime([data.(keywords{i})(j).date ' ' data.(keywords{i})(j).time], 'InputFormat', 'yyyy-MM-dd HH:mm:ss.SSSSSS');
        catch
            try
                data.(keywords{i})(j).datetime=datetime([data.(keywords{i})(j).date ' ' data.(keywords{i})(j).time], 'InputFormat', 'yyyy-MM-dd HH:mm:ss');
            catch
                continue;
            end
        end
    end
end

fclose(fid);