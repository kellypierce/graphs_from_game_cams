import exiftool 
import igraph as ig
import pandas as pd
import os as os
from os import linesep, path, R_OK
import csv
from warnings import warn
from string import Template
    
class Checks(object):
    
    def __init__(self):
        self.allowed_units = set(['H', 'D', 'T'])
        self.illegal_operators = set(['/', '.'])
        
    def check_file_type(self, filename, allowed_type):
        if filename.lower().endswith(allowed_type):
            return True
        else:
            return False
    
    def check_file_access(self, filename):
        '''
        return true if this is a file and is readable on the current filesystem
        '''
        try:
            if os.path.exists(os.path.abspath(filename)) \
                and os.path.isfile(os.path.abspath(filename)) \
                and os.access(os.path.abspath(filename), R_OK):
                return True
        except IOError:
            return False
            
    def check_args(self, window, units):
        if units is None:
            raise TypeError('Unit for time window required.')
        elif units not in self.allowed_units:
            raise TypeError('Time window unit specified is not supported as unit for time window.')
        elif window in self.illegal_operators:
            raise TypeError('Fractional time slices not supported.')
        else:
            return True   
            
    def check_outputs(self, outfile):
        warn_template = Template('Output file $f already exists. Delete? (y/n) ')
        if os.path.exists(outfile):
            warn_msg = warn_template.substitute(f = outfile)
            to_delete = raw_input(warn_msg)
            affirmative_set = set(['yes', 'y', 'Y', 'Yes'])
            if to_delete in affirmative_set:
                warn(('File %r will be deleted.' % outfile))
                os.remove(outfile)
            else:
                raise IOError('Terminating to avoid overwritting previous results')

class TimeStamp():

    def __init__(self):
        pass
        
    def from_exif(self, photo_names):

        '''
        input: list of photo names
        output: list
        '''
        #print len(photo_names)
        time_data_list = []
        with exiftool.ExifTool() as et:
            time_data_list.append(et.get_tag_batch('EXIF:DateTimeOriginal', photo_names))
        return time_data_list

class ProcessAnimalID():

    def __init__(self):
        pass
    
    def read_id_file(self, photo_list, out_file = None):
        '''
        input:
        - photo_list: path to csv file
        - out_file: path to csv file; will be overwritten with each execution
        output: none; calls other functions
        '''
        
        '''
        TODO
        - warn if output file already exists
        - check if input file exists and is accessible
        - check file extension on input paths (in case they're not photos?)
        - generally think of what to do if the exif data desired doesn't exist...
        '''
        # which is faster -- to read all the lines in the file, get a list of photo names, and batch-request the exif data?
        # or to read the file line by line and make a new call for the exif data every time?    
        # check that file is long enough to bother with (>1 line at minimum)
        first_line = True
        ts = TimeStamp()
        with open(photo_list, 'r') as photos:
            for line in photos:
                if not first_line:
                    
                    line = line.replace('\n','')
                    line_list = line.split(',')
                    file_path = line_list[0]
                    allowed_type = ('.jpg', '.jpeg')
                    ch = Checks()
                    
                    if not ch.check_file_type(file_path, allowed_type) and ch.check_file_access(file_path):
                        raise TypeError('File type incorrect.')
                    if not ch.check_file_access(file_path):
                        raise IOError('File not accessible at this path.')
                                
                    time_stamp = ts.from_exif([file_path])
                    
                    # format is yyyy:mm:dd hh:mm:ss
                    # pandas requires yyyy-mm-dd hh:mm:ss
                    # replace the colons in the timestamp to match pandas expectation
                    date_split = time_stamp[0][0].split(' ')
                    reformatted_y_m_d = date_split[0].replace(':', '-')
                    properly_formatted_date = reformatted_y_m_d + ' ' + date_split[1]

                    with open(out_file, 'a') as output:
                        output.write(line_list[0] + ',' + line_list[1] + ',' + properly_formatted_date + '\n')
                else:
                    with open(out_file, 'w') as output:
                        output.write('Photo' + ',' + 'AnimalID' + ',' + 'Time' + '\n')
                    first_line = False   
            
class AnimalGraph(object):

    def __init__(self, photo_data, out_edges, out_graph, window, units):
        self.photo_data = photo_data
        self.out_edges = out_edges
        self.out_graph = out_graph
        self.window = window
        self.units = units
    
    def brute_force_edges(self, id_list):
        '''
        input: list of unique animal IDs present in a given space/time
        output: list of lists containing animal edges
        '''
        edge_list = []
        for i in range(len(id_list)):
            for j in range(i+1, len(id_list)):
                edge_list.append([id_list[i], id_list[j]])
        return edge_list
    
    def find_edges(self, time_slices, out_edges):
        '''
        input: data frame containing only information from a certain time slice
        output: 
        '''
        all_edges = []
        all_ids = set()
        for slice in time_slices:
            if len(slice) > 0:
                ids_present = slice.AnimalID.unique()
                all_ids.update(ids_present)
                if len(ids_present) > 1:
                    time_slice_edges = self.brute_force_edges(ids_present)
                    for ts in time_slice_edges:
                        all_edges.append(ts)
                        if self.out_edges:
                            with open(self.out_edges, 'a') as oe:
                                wr = csv.writer(oe, quoting=csv.QUOTE_ALL)
                                wr.writerow(ts)            
        return all_edges, all_ids
            
    ## CAN PARALLELIZE THIS PART ##
    def time_slice(self, site_partitions):
        '''
        input: data frame containing only information from a certain site; window size
        output: list of data frames partitioned by window size
        '''
        time_slices = []
        window = int(self.window)
        if window > 1:
            pd_freq = window + self.units
        else:
            pd_freq = self.units
        
        for site_data in site_partitions:
            start_time = min(site_data.Time)
            max_time = max(site_data.Time)
            #print start_time, max_time
            t = start_time
            #print pd_freq, self.window, self.units
            slices = pd.date_range(start = start_time, end = pd.to_datetime(max_time) + pd.DateOffset(hours = int(self.window)), freq = pd_freq)
            for time_idx in range(1,len(slices)):
                #print slices[time_idx]
                time_slice = site_data[(pd.to_datetime(site_data.Time) >= pd.to_datetime(slices[time_idx-1])) & (pd.to_datetime(site_data.Time) < pd.to_datetime(slices[time_idx]))]
                time_slices.append(time_slice)
            
        return time_slices
          
    def partition_sites(self, photo_df):
        '''
        input: pandas data frame
        output: a list of data frame subsets
        '''
        sites = photo_df.Site.unique()
        site_dataframes = []
        for site in sites:
            site_data = photo_df[self.photo_df.Site == site]
            site_dataframes.append(site_data)
        return site_dataframes      

    def generate_graph(self):
        pass
        '''
        input: data frame containing animal IDs and times; window size
        output: edge list
        '''
        
        photo_df = pd.read_csv(self.photo_data)
        pd.to_datetime(pd.Series(photo_df.Time))
        photo_df.set_index(pd.DatetimeIndex(photo_df['Time']), inplace = True)

        if 'Site' in photo_df.columns.values:
            site_partitions = self.partition_sites(photo_df)
        else:
            site_partitions = [photo_df]
        time_slice_data = self.time_slice(site_partitions)
        edges, ids = self.find_edges(time_slice_data, self.out_edges)
        #print vertices
        # create an empty graph
        g = ig.Graph()

        # add vertices to the graph
        for v in ids:
            g.add_vertex(str(v))
        g.vs['size'] = 30
        g.vs['color'] = '#2b8cbe'
            
        # add edges to the graph
        for edge_pair in edges:
            node1 = g.vs.find(name=str(edge_pair[0]))
            node2 = g.vs.find(name=str(edge_pair[1]))
            if g.are_connected(node1, node2):
                g[node1, node2] += 1
            else:
                g.add_edge(node1, node2, weight = 1)
    
        # make the plot
        if self.out_graph:
            ig.plot(g, self.out_graph, layout = "kamada_kawai", vertex_label=g.vs["name"], edge_width=g.es["weight"])
        else:
            ig.plot(g, layout = "kamada_kawai", vertex_label=g.vs["name"], edge_width=g.es["weight"])
        return
      
if __name__ == '__main__':
    
    import argparse
    
    parser = argparse.ArgumentParser(description = 'Game camera photo data management for contact network generation')
    parser.add_argument('-f', '--file', help = 'Tab-separated file containing paths to photos and animal IDs')
    parser.add_argument('-w', '--window', help = 'Window size for aggregating temporal data')
    parser.add_argument('-u', '--units', help = 'Units for window size, if not hours. Acceptable entries are T (minutes), H (hours), and D (days)')
    parser.add_argument('-ot', '--output_time', help = 'Path for writing output time stamp data', default = None)
    parser.add_argument('-oe', '--output_edges', help = 'Path for writing output edge list', default = None)
    parser.add_argument('-og', '--output_graph', help = 'Path for writing output graph image', default = None)
    
    opts = parser.parse_args()
    # add some try/assert statements here to ensure that the infile exists
    in_file = opts.file
    window = opts.window
    units = str(opts.units)
    out_file = opts.output_time
    out_edges = opts.output_edges
    out_graph = opts.output_graph
    
    ''' TODO:
    Assess what needs to be done by checking which outfiles are requested?
    '''
    
    ch = Checks()
    ch.check_file_type(in_file, ('.csv'))
    ch.check_file_access(in_file)
    ch.check_args(window, units)
    
    if out_file:
        ch.check_outputs(out_file)
        ch.check_file_type(out_file, ('.csv'))
    if out_edges:
        ch.check_outputs(out_edges)
        ch.check_file_type(out_edges, ('.csv'))
    if out_graph:
        ch.check_outputs(out_graph)
        ch.check_file_type(out_graph, ('.png', '.PNG', '.pdf', '.PDF'))
    
    ########################
    # test class TimeStamp #
    ########################
    
    ## in_file = one photo
    #ts = TimeStamp()
    #print ts.from_exif(in_file)
    
    ## in_file = two photo names as a string; comma-separated
    ## tests batch functionality of pyexif
    #in_files = in_file.split(',')
    #ts = TimeStamp()
    #print ts.from_exif(in_files)
    
    ##############################
    # test class ProcessAnimalID #
    ##############################
    
    # in_file = spreadsheet
    pid = ProcessAnimalID()
    pid.read_id_file(in_file, out_file)
    
    ##########################
    # test class AnimalGraph #
    ##########################
    
    graph_in_file = out_file
    ag = AnimalGraph(graph_in_file, out_edges, out_graph, window, units)
    ag.generate_graph()