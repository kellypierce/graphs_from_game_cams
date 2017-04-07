import exiftool	
from igraph import *
import pandas as pd

class time_stamp(self):

	def __init__(self):
	
	def from_exif(self, data):
	
		'''
		input: csv, tsv or txt file without time stamp data
		output: csv, tsv or txt file with time stamp data
		'''
	
		# check the EXIF data for the listed images
		# TO DO:
		# 	what is the expected directory structure?
		#	should images be grouped into folders (site, camera)?
		#	should full file paths be specified in the input file?
		
		# https://smarnach.github.io/pyexiftool/
		
		# alternatively, pandas:
		# read file to pandas data frame
		# extract the column of file names as a list
		# check the existence of each file name in the list
		# 	return an error if any of the files do not exist
		# with exiftool.ExifTool() as et:
		#	metadata = et.get_metadata_batch(files)
		# for d in metadata:
		#	# do the parsing to get the time stamps
				
	
	def fromFile(self):
	
		# get time stamps from the file... but is this necessary?



class process_animal_id_file(self):

	def __init__(self):
	
	def read_id_file(self, photo_list):
	
		'''
		input: csv, tsv or txt file
		output: none; calls other functions
		'''
		# check that the file exists
		
		# check that file is long enough to bother with (>1 line at minimum)
		with open(photo_list, 'r') as photos:
			first_line = photos.readline().strip()
			if len(first_line
				# open the exif data for the file listed in that line
				# (check that the file actually exists)
				
		
		contains_time_stamp = time_stamp_file(data)
		# return true if time stamp in file
		# return false if time stamp needed from exif
		
		if contains_time_stamp:
			return
			
		else:
			from_exif(data)
			return
			
class animal_graph(self):

	def __init__(self):
	
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
      			ids_present <- time_slice.ids.unique()
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
		'''
		input: data frame containing animal IDs and times; window size
		output: edge list
		'''
		site_partitions = partition_sites(photo_data)
		time_slice_data = time_slice(site_partitions, window)
		edges = find_edges(time_slice_data)
		return edges
		
		
		
''' R code to translate
edge.list<-cbind(as.character(deer.1), as.character(deer.2))
g<-graph_from_edgelist(edge.list, directed = F)
V(g)$color <- 'yellow'
par(mar=c(1,1,1,1), mfrow=c(1,1))
plot(g)

'''