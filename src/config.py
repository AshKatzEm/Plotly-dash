# -*- coding: utf-8 -*-
from configparser import ConfigParser


def config(filename="/Users/asherkatz/Library/CloudStorage/GoogleDrive-asher.katz3@gmail.com/My Drive/Plotly-dash/src/credentials.ini" , section='postgresql'):
    # create parser
    parser = ConfigParser()

    # read config file
    parser.read(filename)
    db={}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    
    else:
        raise Exception('Section {0} is not found in the {1} file.'.format(section,filename))
    return db