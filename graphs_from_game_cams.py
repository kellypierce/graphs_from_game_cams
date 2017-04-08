import exiftool 
from igraph import *
import pandas as pd
from os import linesep, path, R_OK, X_OK
    
class Checks():
    
    def __init__(self):
        pass
    
    def checkFile(filename):
        '''
        return true if this is a file and is readable on the current filesystem
        '''
        try:
            if os.path.exists(os.path.abspath(filename)) and os.path.isfile(os.path.abspath(filename)) and os.access(os.path.abspath(filename), R_OK):
                return True
            fullPath = string.join(os.getcwd(), filename[1:])
            return os.path.exists(fullPath) and os.path.isfile(fullPath) and os.access(fullPath, R_OK)
        except IOError:
            return False

class TimeStamp():

    def __init__(self):
        pass
        
    def from_exif(self, photo_names):

        '''
        input: list of photo names
        output: list
        '''
        print len(photo_names)
        time_data_list = []
        with exiftool.ExifTool() as et:
            time_data_list.append(et.get_tag_batch('EXIF:DateTimeOriginal', photo_names))
        return time_data_list

class ProcessAnimalID():

    def __init__(self):
        pass
    
    def read_id_file(self, photo_list, out_file = None):
        '''
        input: csv, tsv or txt file
        output: none; calls other functions
        '''
        #if not checkfile(photo_list):
        #    raise IOError("Input file does not exist: %s" % photo_list)
        
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
            		#print line_list, len(line_list), file_path
            		time_stamp = ts.from_exif([file_path])
            		new_line = [line_list[0], line_list[1], time_stamp[0]]
            		print new_line
            		# write new line to new file
            	else:
            		first_line = False   
            
class AnimalGraph():

    def __init__(self):
        pass
    
    def partition_sites(self, photo_data):
        '''
        input: pandas data frame
        output: a list of data frame subsets
        '''
        sites = photo_data.Site.unique()
        site_dataframes = []
        for site in sites:
            site_data = photo_data[photo_data.Site == site]
            site_dataframes.append(site_data)
        return site_dataframes
    
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
    
    def find_edges(self, time_slice):
        '''
        input: data frame containing only information from a certain time slice
        output: 
        '''
        all_edges = []
        for slice in time_slices:
            if len(slice) > 0:
                #ids_present <- time_slice.ids.unique()
                if len(ids_present) > 1:
                    time_slice_edges = brute_force_edges(ids_present)
                    all_edges.append(ts for ts in time_slice_edges)
        return all_edges
            
    ## CAN PARALLELIZE THIS PART ##
    def time_slice(self, site_data, window):
        '''
        input: data frame containing only information from a certain site; window size
        output: list of data frames partitioned by window size
        '''
        time_slices = []
        for site_data in site_partitions:
            # look up details on date time objects
            start_time = min(site_data.Time)
            max_time = max(site_data.Time)
            t = start_time
            while t < max_time:
                time_slice = site_data[site_data.Time >= t and site_data.Time < t + window]
                t += window
                time_slices.append(time_slice)
        return time_slices
        
    def generate_graph(self, data, window):
        pass
        '''
        input: data frame containing animal IDs and times; window size
        output: edge list
        '''
        site_partitions = partition_sites(photo_data)
        time_slice_data = time_slice(site_partitions, window)
        edges = find_edges(time_slice_data)
        
    ''' R code to translate
    edge.list<-cbind(as.character(deer.1), as.character(deer.2))
    g<-graph_from_edgelist(edge.list, directed = F)
    V(g)$color <- 'yellow'
    par(mar=c(1,1,1,1), mfrow=c(1,1))
    plot(g)

    '''
    
if __name__ == '__main__':
    
    import argparse
    
    parser = argparse.ArgumentParser(description = 'Game camera photo data management for contact network generation')
    parser.add_argument('-f', '--file', help = 'Tab-separated file containing paths to photos and animal IDs')
    parser.add_argument('-w', '--window', help = 'Window size for aggregating temporal data')
    parser.add_argument('-o', '--output', help = 'Path for writing output data', default = None)
    
    opts = parser.parse_args()
    # add some try/assert statements here to ensure that the infile exists
    in_file = opts.file
    window = opts.window
    out_file = opts.output
    
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
    #print ts.from_exif(in_files
    
    ##############################
    # test class ProcessAnimalID #
    ##############################
    
    ## in_file = spreadsheet
    pid = ProcessAnimalID()
    pid.read_id_file(in_file)
    
    #ag = AnimalGraph()
    #ag.generate_graph(in_file, window)