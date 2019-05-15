%% Read in Data

export_figures_bool=[0 0 0];
user_path=getenv('USERPROFILE');
dfp = [user_path, filesep, 'YOUR_PATH_HERE']; % data folder path
export_fig_toolbox_path= [user_path, filesep, 'export_fig']; % must be installed
output_path=[user_path, filesep, 'YOUR_PATH_HERE_OUTPUT'];

% Data takes a while to read in, comment out this portion to use data in memory
datafile=[dfp, 'DATA_FILE_NAME'];
keywords={'rtd', 'orp', 'ph', 'ec', 'do', 'co2'};
[data]=read_in_hydroponics_data(datafile, '\t', keywords);

%% Filter and Graph Data
close all;

figure_struct=struct();

for i = 1:numel(keywords)
    figure_struct(i).fig=figure;
    figure_struct(i).name=keywords{i};
    hold on;
    if isfield(data.(keywords{i}), 'datetime') % basically do not run for sensors that return nothing
        filtered_index=~isoutlier([data.(keywords{i}).value]);
        data.(keywords{i})=data.(keywords{i})(filtered_index);
    
        if strcmp(keywords{i}, 'rtd')
            m=mean([data.(keywords{i}).value].*(9/5)+32); % convert to fahrenheit
            sd=std([data.(keywords{i}).value].*(9/5)+32);

            scatter([data.(keywords{i}).datetime], [data.(keywords{i}).value].*(9/5)+32, '.');
            title(['Solution Temperature (mean: ', ...
                num2str(round(m, 1)), ...
                ' ± ', num2str(round(sd, 1)), ')']);
            
            xrange=[data.(keywords{i})(1).datetime:data.(keywords{i})(end).datetime];
            yup=[min([data.(keywords{i}).value].*(9/5)+32), max([data.(keywords{i}).value].*(9/5)+32)];
            for z = 1:numel(xrange)
                plot([xrange(z), xrange(z)], yup, 'Color', [0 0 0]+.75);
            end
            
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m], 'Color', 'r');
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m]+sd, 'Color', 'm');
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m]-sd, 'Color', 'm');
            xlabel('Dates');
            ylabel('°F');
            fprintf('%s\n', keywords{i});
            fprintf('mean: %.2f\n', mean([data.(keywords{i}).value].*(9/5)+32));
            fprintf('standard deviation: %.2f\n', std([data.(keywords{i}).value].*(9/5)+32));
            
            if export_figures_bool(1)
                export_fig([output_path, keywords{i}, '_graph.png'], '-transparent', '-m3.5');
            end
            
        elseif strcmp(keywords{i}, 'ph')
            m=mean([data.(keywords{i}).value]);
            sd=std([data.(keywords{i}).value]);
            
            scatter([data.(keywords{i}).datetime], [data.(keywords{i}).value], '.');
            title(['pH (mean: ', ...
                num2str(round(m, 2)), ...
                ' ± ', num2str(round(sd, 2)), ')']);
            
            xrange=[data.(keywords{i})(1).datetime:data.(keywords{i})(end).datetime];
            yup=[min([data.(keywords{i}).value]), max([data.(keywords{i}).value])];
            for z = 1:numel(xrange)
                plot([xrange(z), xrange(z)], yup, 'Color', [0 0 0]+.75);
            end
            
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m], 'Color', 'r');
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m]+sd, 'Color', 'm');
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m]-sd, 'Color', 'm');
            xlabel('Dates');
            ylabel('pH');
            fprintf('%s\n', keywords{i});
            fprintf('mean: %.2f\n', m);
            fprintf('standard deviation: %.2f\n', sd);
            
            if export_figures_bool(1)
                export_fig([output_path, keywords{i}, '_graph.png'], '-transparent', '-m3.5');
            end
            
        elseif strcmp(keywords{i}, 'ec')
            m=mean([data.(keywords{i}).value]);
            sd=std([data.(keywords{i}).value]);
            
            scatter([data.(keywords{i}).datetime], [data.(keywords{i}).value], '.');
            title(['Electroconductivity, K = 1.0, (mean: ', ...
                num2str(round(m, 1)), ...
                ' ± ', num2str(round(sd, 1)), ')']);
            
            xrange=[data.(keywords{i})(1).datetime:data.(keywords{i})(end).datetime];
            yup=[min([data.(keywords{i}).value]), max([data.(keywords{i}).value])];
            for z = 1:numel(xrange)
                plot([xrange(z), xrange(z)], yup, 'Color', [0 0 0]+.75);
            end
            
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m], 'Color', 'r');
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m]+sd, 'Color', 'm');
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m]-sd, 'Color', 'm');
            xlabel('Dates');
            ylabel('µS / cm');
            fprintf('%s\n', keywords{i});
            fprintf('mean: %.2f\n', m);
            fprintf('standard deviation: %.2f\n', sd);
            
            if export_figures_bool(1)
                export_fig([output_path, keywords{i}, '_graph.png'], '-transparent', '-m3.5');
            end
            
        elseif strcmp(keywords{i}, 'do')
            m=mean([data.(keywords{i}).value]);
            sd=std([data.(keywords{i}).value]);
            
            scatter([data.(keywords{i}).datetime], [data.(keywords{i}).value], '.');
            title(['Dissolved Oxygen (mean: ', ...
                num2str(round(m, 2)), ...
                ' ± ', num2str(round(sd, 2)), ')']);
            
            xrange=[data.(keywords{i})(1).datetime:data.(keywords{i})(end).datetime];
            yup=[min([data.(keywords{i}).value]), max([data.(keywords{i}).value])];
            for z = 1:numel(xrange)
                plot([xrange(z), xrange(z)], yup, 'Color', [0 0 0]+.75);
            end
            
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m], 'Color', 'r');
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m]+sd, 'Color', 'm');
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m]-sd, 'Color', 'm');
            xlabel('Dates');
            ylabel('mg / L');
            fprintf('%s\n', keywords{i});
            fprintf('mean: %.2f\n', m);
            fprintf('standard deviation: %.2f\n', sd);
            
            if export_figures_bool(1)
                export_fig([output_path, keywords{i}, '_graph.png'], '-transparent', '-m3.5');
            end
            
        elseif strcmp(keywords{i}, 'co2')
            m=mean([data.(keywords{i}).value]);
            sd=std([data.(keywords{i}).value]);
            
            scatter([data.(keywords{i}).datetime], [data.(keywords{i}).value], '.');
            title(['Atmospheric CO2 (mean: ', ...
                num2str(round(m, 1)), ...
                ' ± ', num2str(round(sd, 1)), ')']);
            
            xrange=[data.(keywords{i})(1).datetime:data.(keywords{i})(end).datetime];
            yup=[min([data.(keywords{i}).value]), max([data.(keywords{i}).value])];
            for z = 1:numel(xrange)
                plot([xrange(z), xrange(z)], yup, 'Color', [0 0 0]+.75);
            end
            
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m], 'Color', 'r');
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m]+sd, 'Color', 'm');
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m]-sd, 'Color', 'm');
            xlabel('Dates');
            ylabel('ppm');
            fprintf('%s\n', keywords{i});
            fprintf('mean: %.2f\n', m);
            fprintf('standard deviation: %.2f\n', sd);
            
            if export_figures_bool(1)
                export_fig([output_path, keywords{i}, '_graph.png'], '-transparent', '-m3.5');
            end
            
        elseif strcmp(keywords{i}, 'orp')
            m=mean([data.(keywords{i}).value]);
            sd=std([data.(keywords{i}).value]);
            
            scatter([data.(keywords{i}).datetime], [data.(keywords{i}).value], '.');
            title(['Oxidation Reduction Potential (mean: ', ...
                num2str(round(m)), ...
                ' ± ', num2str(round(sd)), ')']);
            
            xrange=[data.(keywords{i})(1).datetime:data.(keywords{i})(end).datetime];
            yup=[min([data.(keywords{i}).value]), max([data.(keywords{i}).value])];
            for z = 1:numel(xrange)
                plot([xrange(z), xrange(z)], yup, 'Color', [0 0 0]+.75);
            end
            
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m], 'Color', 'r');
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m]+sd, 'Color', 'm');
            plot([data.(keywords{i})(1).datetime, data.(keywords{i})(end).datetime], [m, m]-sd, 'Color', 'm');
            xlabel('Dates');
            ylabel('mV');
            fprintf('%s\n', keywords{i});
            fprintf('mean: %.2f\n', m);
            fprintf('standard deviation: %.2f\n', sd);
            
            if export_figures_bool(1)
                export_fig([output_path, keywords{i}, '_graph.png'], '-transparent', '-m3.5');
            end
            
        end
    end
end


%% Read in 2nd File
% This reads in data from the secondary sensor suite (GroLine Sensor) and
% creates graphs for it as well
datafile2='YOUR_PATH2\YOUR_FILENAME_HEADER_REMOVED.xlsx'; % ensure that the header is removed
keywords2={'rtd', 'ec', 'ph'};

data2=cell(3, 1);

for i = 1:numel(keywords2)
    data2{i}=readtable(datafile2, 'Sheet', keywords2{i});
    data2{i}.Time=datetime(data2{i}.Time, 'ConvertFrom', 'excel');
    data2{i}.Date.Hour=data2{i}.Time.Hour;
    data2{i}.Date.Minute=data2{i}.Time.Minute;
    data2{i}.Date.Second=data2{i}.Time.Second;
    data2{i}.Time=[];
    
%     filtered_index=~isoutlier([data2{i}.Avg]);
%     data2{i}.Avg=data2{i}.Avg(filtered_index);
    
    if strcmp(keywords2{i}, 'ec')
        data2{i}.Avg=data2{i}.Avg*1000;
    end
    
    if any(cellfun(@strcmp, {figure_struct.name}, repmat(keywords2(i), 1, length(keywords))))
        % select figure, assume these have already been made
        figure(find(cellfun(@strcmp, {figure_struct.name}, repmat(keywords2(i), 1, length(keywords)))));
    else
        figure;
    end
    
    m=mean([data2{i}.Avg]);
    sd=std([data2{i}.Avg]);
    
    hold on;
    scatter([data2{i}.Date], [data2{i}.Avg], '.');
    
    xrange=[data2{i}.Date(1):data2{i}.Date(end)];
    yup=[min([data2{i}.Avg]), max([data2{i}.Avg])];
    
    for z = 1:numel(xrange)
        plot([xrange(z), xrange(z)], yup, 'Color', [0 0 0]+.75);
    end
    
    plot([data2{i}.Date(1), data2{i}.Date(end)], [m, m], 'Color', [0.3010 0.7450 0.9330]);
    plot([data2{i}.Date(1), data2{i}.Date(end)], [m, m]+sd, 'Color', [0.9290 0.6940 0.1250]);
    plot([data2{i}.Date(1), data2{i}.Date(end)], [m, m]-sd, 'Color', [0.9290 0.6940 0.1250]);
    
    xlabel('Dates');
    fprintf('%s\n', keywords2{i});
    fprintf('mean: %.2f\n', m);
    fprintf('standard deviation: %.2f\n', sd);
    
    if strcmp(keywords2{i}, 'ec')
        title(['Electroconductivity (mean: ', ...
            num2str(round(m,2)), ...
            ' ± ', num2str(round(sd,2)), ')']);
        ylabel('µS / cm');
        if export_figures_bool(2)
            export_fig([output_path, keywords2{i}, '_graph_real.png'], '-transparent', '-m3.5');
        end
    elseif strcmp(keywords2{i}, 'rtd')
        title(['Solution Temperature (mean: ', ...
            num2str(round(m,2)), ...
            ' ± ', num2str(round(sd,2)), ')']);
        ylabel('°F');
        if export_figures_bool(2)
            export_fig([output_path, keywords2{i}, '_graph_real.png'], '-transparent', '-m3.5');
        end
    elseif strcmp(keywords2{i}, 'ph')
        title(['pH (mean: ', ...
            num2str(round(m,2)), ...
            ' ± ', num2str(round(sd,2)), ')']);
        ylabel('pH');
        if export_figures_bool(2)
            export_fig([output_path, keywords2{i}, '_graph_real.png'], '-transparent', '-m3.5');
        end
    end
end

%% Read in Efficiency and Graph

data3_filename='YOUR_FILENAME_HERE.xlsx';
data3=readtable([dfp, data3_filename]);
duration=[16, 18, 20];
distance=[3, 7, 11];

% Graph Data
figure;
hold on;
title('Average Photosynthesis Efficiency');
h1=bar([16, 18, 20], [data3.mean(1:3), data3.mean(4:6), data3.mean(7:9)].*100);
axis([15, 21, 0, 100])
ylabel('% Fv / Fm');
xlabel('Duration (hours)');
errorbar([15.5, 16, 16.5; 17.5, 18, 18.5; 19.5, 20, 20.5], [data3.mean(1:3), data3.mean(4:6), data3.mean(7:9)].*100, [data3.std(1:3), data3.std(4:6), data3.std(7:9)].*100, '.k');
legend(h1, [num2str(distance(1)), '"'], [num2str(distance(2)), '"'], [num2str(distance(3)), '"']);

if export_figures_bool(3)
    export_fig([output_path, 'photosynthesis_efficiency', '_graph_real.png'], '-transparent', '-m3.5');
end
% duration = columns
% distance = rows

data4=readtable([dfp, data3_filename], 'Sheet', 'front');

stats_data=[];
for i = 1:length(duration)
    stats_data=[stats_data, data4.fv_m(data4.duration==duration(i))];
end

% Run Stats
[p, table, stats] = anova2(stats_data, 5);
