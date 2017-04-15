import exiftool 
import csv
import check_inputs as ch

def from_exif(photo_names):
    '''
    photo_names: path to a photograph file
    returns: list of time stamps with format yyyy-mm-dd hh:mm:ss
    '''
    #print len(photo_names)
    time_data_list = []
    with exiftool.ExifTool() as et:
        time_stamp = et.get_tag_batch('EXIF:DateTimeOriginal', photo_names) # format is yyyy:mm:dd hh:mm:ss
        date_split = time_stamp[0].split(' ')
        reformatted_y_m_d = date_split[0].replace(':', '-')
        properly_formatted_date = reformatted_y_m_d + ' ' + date_split[1]
        time_data_list.append(properly_formatted_date)
    return time_data_list

# TODO: what if exif data don't exist?
# TODO: time batch exif data vs one-by-one exif data
# TODO: check if file has a header?
# TODO: what if there are multiple sites?
def read_id_file(photo_list, out_file = None):
    '''
    photo_list: path to csv file
    out_file: path to csv file; will be overwritten with each execution
    returns: none; calls other functions
    '''
    first_line = True
    with open(photo_list, 'r') as photos:
        for line in photos:
            if not first_line:
                
                line = line.replace('\n','')
                line_list = line.split(',')
                file_path = line_list[0]
                allowed_type = ('.jpg', '.jpeg')
                if not ch.check_file_type(file_path, allowed_type) and check_file_access(file_path):
                    raise TypeError('File type incorrect.')
                if not ch.check_file_access(file_path):
                    raise IOError('File not accessible at this path.')
                            
                time_stamp = from_exif([file_path])
                with open(out_file, 'a') as output:
                    output.write(line_list[0] + ',' + line_list[1] + ',' + time_stamp[0] + '\n')
            else:
                with open(out_file, 'w') as output:
                    output.write('Photo' + ',' + 'AnimalID' + ',' + 'Time' + '\n')
                first_line = False   
                
if __name__ == '__main__':
    
    import argparse
    
    parser = argparse.ArgumentParser(description = 'Game camera photo data management for contact network generation')
    parser.add_argument('-f', '--file', help = 'Tab-separated file containing paths to photos and animal IDs')
    parser.add_argument('-ot', '--output_time', help = 'Path for writing output time stamp data')

    opts = parser.parse_args()
    in_file = opts.file
    out_file = opts.output_time

    ch.check_file_type(in_file, ('.csv'))
    ch.check_file_access(in_file)
    ch.check_outputs_exist(out_file)
    ch.check_file_type(out_file, ('.csv'))
    
    read_id_file(in_file, out_file)