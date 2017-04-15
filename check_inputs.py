import os as os
from os import linesep, path, R_OK
from warnings import warn
from string import Template

def check_file_type(filename, allowed_ext):
    '''
    filename: path to a file
    allowed_ext: allowed extension
    returns: true or ValueError
    '''
    if filename.lower().endswith(allowed_ext):
        return True
    else:
        raise ValueError('Incorrect output file type specified. Use extension .csv.')

    
def check_file_access(filename):
    '''
    filename: path to a file
    returns: true if this is a file and is readable on the current filesystem
    '''
    try:
        if os.path.exists(os.path.abspath(filename)) \
            and os.path.isfile(os.path.abspath(filename)) \
            and os.access(os.path.abspath(filename), R_OK):
            return True
    except IOError:
        return False

def check_args(arg, arg_name, allowed_values = None, illegal_operators = None):
    '''
    arg: user-supplied argument value
    arg_name: user-supplied argument name
    returns: true or TypeError
    '''
    if arg is None:
        raise TypeError(('User-supplied argument %r required.' % arg_name))
    if allowed_values:
        if arg not in allowed_values:
            allowed_value_template = Template('User-supplied argument $a is of a type not supported. Please use values in $av.')
            allowed_value_error = allowed_value_template.substitute(a = arg, av = allowed_values)
            raise TypeError(allowed_value_error)
    if illegal_operators:
        for operator in illegal_operators:
            if operator in arg:
                illegal_op_template = Template('User-supplied argument $a contains an illegal operator $op. Please use values that do not contain $iops.')
                illegal_op_error = illegal_op_template.substitute(a = arg, op = operator, iops = illegal_operators)
                raise TypeError(illegal_op_error)
    return True   
            
def check_outputs_exist(outfile):
    '''
    outfile: path to output file
    returns: true if output file does not previously exist or user indicates it can be deleted
    '''
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




    