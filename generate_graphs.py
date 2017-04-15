import exiftool 
import igraph as ig
import pandas as pd
import os as os
from os import linesep, path, R_OK
import csv
from warnings import warn
from string import Template
import check_inputs as ch    
    
# TODO: parallelize?
# TODO: check pd.date_range -- are units other than hours supported??
def time_slice(site_partitions, window, units):
    '''
    site_partitions: data for all times for a single site/camera
    returns: a list of data frame subsets for a given time window
    '''
    time_slices = []
    window = int(window)
    if window > 1:
        pd_freq = window + units
    else:
        pd_freq = units
    
    for site_data in site_partitions:
        start_time = min(site_data.Time)
        max_time = max(site_data.Time)
        #print start_time, max_time
        t = start_time
        slices = pd.date_range(start = start_time, end = pd.to_datetime(max_time) + pd.DateOffset(hours = window), freq = pd_freq)
        for time_idx in range(1,len(slices)):
            #print slices[time_idx]
            time_slice = site_data[(pd.to_datetime(site_data.Time) >= pd.to_datetime(slices[time_idx-1])) & (pd.to_datetime(site_data.Time) < pd.to_datetime(slices[time_idx]))]
            time_slices.append(time_slice)
        
    return time_slices
      
def partition_sites(photo_df):
    '''
    photo_df: data frame containing data from multiple sites
    returns: a list of data frame subsets, each from a single site
    '''
    sites = photo_df.Site.unique()
    site_dataframes = []
    for site in sites:
        site_data = photo_df[photo_df.Site == site]
        site_dataframes.append(site_data)
    return site_dataframes      

def brute_force_edges(id_list):
    '''
    id_list: list of unique IDs present within a given time window
    returns: a list of all unique, order-independent pairwise combinations
    '''
    edge_list = []
    for i in range(len(id_list)):
        for j in range(i+1, len(id_list)):
            edge_list.append([id_list[i], id_list[j]])
    return edge_list

def find_edges(time_slices):
    '''
    time_slices: list of data frame subsets
    out_edges: path to output file
    returns: list of edges (node pairs) and list of all unique IDs 
    '''
    all_edges = []
    all_ids = set()
    for slice in time_slices:
        if len(slice) > 0:
            ids_present = slice.AnimalID.unique()
            all_ids.update(ids_present)
            if len(ids_present) > 1:
                time_slice_edges = brute_force_edges(ids_present)
                for ts in time_slice_edges:
                    all_edges.append(ts)            
    return all_edges, all_ids

def add_nodes(graph, ids):
    '''
    graph: igraph object
    ids: list of node (vertex) IDs
    returns: igraph object with nodes added in
    '''
    for v in ids:
        graph.add_vertex(str(v))
    graph.vs['size'] = 30
    graph.vs['color'] = '#2b8cbe'
    return graph

def add_edges(graph, edges):
    '''
    graph: igraph object with nodes (vertexes)
    edges: list of lists (edge pairs)
    returns: igrpah object with nodes and edges
    '''
    for edge_pair in edges:
        node1 = graph.vs.find(name=str(edge_pair[0]))
        node2 = graph.vs.find(name=str(edge_pair[1]))
        if graph.are_connected(node1, node2):
            graph[node1, node2] += 1
        else:
            graph.add_edge(node1, node2, weight = 1)
    return graph

def generate_graph(photo_data, window, units, out_graph):
    '''
    photo_data: CSV file containing photo names and animal IDs, and possibly site IDs
    returns: nothing (calls other functions to generate outputs)
    '''
    photo_df = pd.read_csv(photo_data)
    pd.to_datetime(pd.Series(photo_df.Time))
    photo_df.set_index(pd.DatetimeIndex(photo_df['Time']), inplace = True)

    if 'Site' in photo_df.columns.values:
        site_partitions = partition_sites(photo_df)
    else:
        site_partitions = [photo_df]
    time_slice_data = time_slice(site_partitions, window, units)
    edges, ids = find_edges(time_slice_data)
    
    g = ig.Graph()
    g = add_nodes(g, ids)
    g = add_edges(g, edges)

    if out_graph:
        ig.plot(g, out_graph, layout = "kamada_kawai", vertex_label=g.vs["name"], edge_width=g.es["weight"])
    else:
        ig.plot(g, layout = "kamada_kawai", vertex_label=g.vs["name"], edge_width=g.es["weight"])
    return
  
if __name__ == '__main__':
    
    import argparse
    
    parser = argparse.ArgumentParser(description = 'Game camera photo data management for contact network generation')
    parser.add_argument('-f', '--file', help = 'CSV file containing paths to photos and animal IDs')
    parser.add_argument('-w', '--window', help = 'Window size for aggregating temporal data')
    parser.add_argument('-u', '--units', help = 'Units for window size, if not hours. Acceptable entries are T (minutes), H (hours), and D (days)')
    parser.add_argument('-og', '--output_graph', help = 'Path for writing output graph image', default = None)
    
    opts = parser.parse_args()
    in_file = opts.file
    window = opts.window
    units = str(opts.units)
    out_graph = opts.output_graph
    
    ch.check_file_type(in_file, ('.csv'))
    ch.check_file_access(in_file)
    ch.check_args(window, 'window', illegal_operators = ['/', '.'])
    ch.check_args(units, 'units', allowed_values = ['H', 'D', 'T'])
    if out_graph:
        ch.check_outputs_exist(out_graph)
        ch.check_file_type(out_graph, ('.png', '.PNG', '.pdf', '.PDF'))
    
    ##########################
    # test class AnimalGraph #
    ##########################
    
    generate_graph(in_file, int(window), units, out_graph)