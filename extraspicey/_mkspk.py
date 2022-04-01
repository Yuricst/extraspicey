"""
Spice helper
"""

import os
import numpy as np
from scipy.optimize import root_scalar
import spiceypy as spice

#from ._io_trajectory import array_to_file


def wrap_mkspk(
    filepath_set,
    filepath_in,
    filepath_out,
):
    """Wrapper to SPICE's mkspk utility. Make sure `mkspk.exe` exists in path. 
    
    Args:
        filepath_set (str): path to setup file
        filepath_in (str): path to trajectory file
        filepath_out (str): path to output file (expect extension `.bsp`)
    """
    assert os.path.splitext(filepath_out)[1] == ".bsp"
    if os.path.exists(filepath_out):
        overwrite = input(f"{filepath_out} already exists; would you like to remove? (y/n) [y]: ")
        if overwrite == "n":
            return
        else:
            os.remove(filepath_out)
    # run mkspk
    os.system(f'mkspk -setup {filepath_set} -input {filepath_in} -output {filepath_out}')
    if os.path.exists(filepath_out):
        print(f"Successfully generated {filepath_out}!")
    else:
        print("Failed!")
    return


def create_setup_file(
    filepath,
    INPUT_DATA_TYPE='STATES',
    OUTPUT_SPK_TYPE=9,
    OBJECT_ID=-10005,
    OBJECT_NAME="FOOBAR",
    CENTER_ID=3,
    CENTER_NAME="EARTH BARYCENTER",
    REF_FRAME_NAME="ECLIPJ2000",
    PRODUCER_ID="Yuri",
    DATA_DELIMITER=",",
    LINES_PER_RECORD=1,
    TIME_WRAPPER="# ETSECONDS",
    IGNORE_FIRST_LINE=1,
    LEAPSECONDS_FILE="naif0012.tls",
    FRAME_DEF_FILE=None,
    POLYNOM_DEGREE=9,
    OUTPUT_SPK_FILE=None,
    ts=None,
):
    """Create setup file to be used for mkspk. 
    For details on mkspk, see: 
    https://naif.jpl.nasa.gov/pub/naif/utilities/PC_Linux_32bit/mkspk.ug
    
    Args:
        filepath (str): path to setup file to be generated

    """
    # create file
    with open(filepath, 'w+') as file:
        file.write(f"\\begindata\n")
        file.write(f"   INPUT_DATA_TYPE   = '{INPUT_DATA_TYPE}'\n")
        file.write(f"   OUTPUT_SPK_TYPE   = {OUTPUT_SPK_TYPE}\n")

        # object
        if OBJECT_NAME is not None:
            file.write(f"   OBJECT_ID         = {OBJECT_ID}\n")
        else:
            file.write(f"   OBJECT_NAME       = '{OBJECT_NAME}'\n")

        # ephemeris center
        if CENTER_ID is not None:
            file.write(f"   CENTER_ID         = {CENTER_ID}\n")
        else:
            file.write(f"   CENTER_NAME       = '{CENTER_NAME}'\n")

        file.write(f"   REF_FRAME_NAME    = '{REF_FRAME_NAME}'\n")
        file.write(f"   PRODUCER_ID       = '{PRODUCER_ID}'\n")
        file.write(f"   DATA_ORDER        = 'EPOCH X Y Z VX VY VZ'\n")
        file.write(f"   INPUT_DATA_UNITS  = ('ANGLES=DEGREES' 'DISTANCES=km')\n")
        file.write(f"   DATA_DELIMITER    = '{DATA_DELIMITER}'\n")
        file.write(f"   LINES_PER_RECORD  = {LINES_PER_RECORD}\n")
        file.write(f"   TIME_WRAPPER      = '{TIME_WRAPPER}'\n")
        file.write(f"   IGNORE_FIRST_LINE = {IGNORE_FIRST_LINE}\n")
        
        # leap seconds file
        file.write(f"   LEAPSECONDS_FILE  = '{LEAPSECONDS_FILE}'\n")

        # reference frame file
        if FRAME_DEF_FILE is not None:
            file.write(f"   FRAME_DEF_FILE    = '{FRAME_DEF_FILE}'\n")
        
        file.write(f"   POLYNOM_DEGREE    = {POLYNOM_DEGREE}\n")
        file.write(f"   SEGMENT_ID        = 'SPK_STATES_0"+str(OUTPUT_SPK_TYPE)+"'\n")

        # output file name
        if OUTPUT_SPK_FILE is not None:
            file.write(f"   OUTPUT_SPK_FILE   = '{OUTPUT_SPK_FILE}'\n")

        file.write(f"\\begintext\n")
        # write valid epoch range
        if ts is not None:
            file.write(f"   EARLIEST_EPOCH    = {ts[0]}\n")
            file.write(f"   LATEST_EPOCH      = {ts[-1]}\n")
    print(f"Generated {filepath}!")
    return



def read_setup_file(filepath):
    """Read setup file for SPK file
    
    Args:
        filepath (str): path to setup file
        
    Returns:
        (dict): dictionary with setup entries
    """
    with open(filepath) as f:
        lines = f.readlines()
    setup_dict = {}
    for line in lines:
        if "begin" not in line:
            setup_dict[line[3:21].rstrip()] = line[23:-1]
    return setup_dict


# def cr3bp_to_spice(
#     ts,
#     y,
#     filepath_out="tmp_spice_out.bsp",
#     INPUT_DATA_TYPE='STATES',
#     OUTPUT_SPK_TYPE=9,
#     OBJECT_ID=-10005,
#     OBJECT_NAME="FOOBAR",
#     CENTER_ID=3,
#     CENTER_NAME="EARTH BARYCENTER",
#     REF_FRAME_NAME="EARTHMOONROTATING",
#     PRODUCER_ID="Yuri",
#     DATA_DELIMITER=",",
#     LINES_PER_RECORD=1,
#     TIME_WRAPPER="# ETSECONDS",
#     IGNORE_FIRST_LINE=1,
#     LEAPSECONDS_FILE="naif0012.tls",
#     FRAME_DEF_FILE=None,
#     POLYNOM_DEGREE=9,
#     keep_setup_file=True,
#     keep_input_file=False,
# ):
#     """Create bsp file of CR3BP trajectory via SPICE utility mkspk.
#     Make sure `mkspk.exe` exists in path. 
#     Note that the created trajectory doesn't actually correspond to full-ephemeris propagation.
#     For details on mkspk, see: 
#     https://naif.jpl.nasa.gov/pub/naif/utilities/PC_Linux_32bit/mkspk.ug

#     Args:
#         ts (list): N time-stamps, in ephemeris seconds past J2000 TDB
#         y (np.array): state vectors [x,y,z,vx,vy,vz] in 6 x N matrix
#         filepath_out (str): path to output file (expect extension `.bsp`)
#     """
#     assert os.path.splitext(filepath_out)[1] == ".bsp"
#     # create temporary paths for setup and input files
#     filepath_set = os.path.splitext(filepath_out)[0] + "_setup.txt"
#     filepath_in  = os.path.splitext(filepath_out)[0] + "_input.txt"
#     # create setup file
#     create_setup_file(
#         filepath_set,
#         INPUT_DATA_TYPE=INPUT_DATA_TYPE,
#         OUTPUT_SPK_TYPE=OUTPUT_SPK_TYPE,
#         OBJECT_ID=OBJECT_ID,
#         OBJECT_NAME=OBJECT_NAME,
#         CENTER_ID=CENTER_ID,
#         CENTER_NAME=CENTER_NAME,
#         REF_FRAME_NAME=REF_FRAME_NAME,
#         PRODUCER_ID=PRODUCER_ID,
#         DATA_DELIMITER=DATA_DELIMITER,
#         LINES_PER_RECORD=LINES_PER_RECORD,
#         TIME_WRAPPER=TIME_WRAPPER,
#         IGNORE_FIRST_LINE=IGNORE_FIRST_LINE,
#         LEAPSECONDS_FILE=LEAPSECONDS_FILE,
#         FRAME_DEF_FILE=FRAME_DEF_FILE,
#         POLYNOM_DEGREE=POLYNOM_DEGREE,
#         ts=ts,
#     )
#     # create input file (trajectory)
#     array_to_file(ts, y, filepath_in)
#     # run mkspk
#     wrap_mkspk(filepath_set, filepath_in, filepath_out)
#     # remove temporary files
#     if keep_setup_file is False:
#         os.remove(filepath_set)
#     if keep_input_file is False:
#         os.remove(filepath_in)
#     return


# def get_sun_earth_moon_alignment(
#     bracket = [7.64e8, 7.655e8],
#     beta_target=np.pi
# ):
#     """Get epoch at prescribed beta_s angle.
#     The beta_s angle is defined between:
#         - rotating Earth-Moon line, and 
#         - the Earth-Moon barycenter -> Sun vector
#     and is positive anti-clockwise.
#     Sun-Earth-Moon ailgnment: beta_s == pi
#     Earth-Moon-Sun alignment: beta_s == 0.0
#     Make sure that the `EARTHMOONROTATING` frame kernel is loaded. 
    
#     Args:
#         bracket (list): lower and upper bound
#         beta_target (float): target beta_s, in radians. 
    
#     Returns:
#         (tuple): epoch and RootResults object
#     """
#     xhat = np.array([1.0,0.0,0.0])

#     def f_betas180deg(x):
#         sun_vec, _ = spice.spkpos("SUN", x, "EARTHMOONROTATING", 'NONE', 'EARTH BARYCENTER')
#         beta_s_iter = np.arccos(np.dot(xhat, sun_vec)/(np.linalg.norm(sun_vec)*np.linalg.norm(xhat)))
#         if sun_vec[1] < 0:  # if y-value is negative
#             beta_s_iter = 2*np.pi - beta_s_iter
#         return beta_s_iter - beta_target

#     # solve root-solving problem
#     sol = root_scalar(f_betas180deg, bracket=bracket, method='brentq', rtol=1.e-8, xtol=1.e-8)
#     return sol.root, sol

