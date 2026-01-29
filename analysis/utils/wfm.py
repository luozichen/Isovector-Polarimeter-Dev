import struct
import numpy as np
import os
from dataclasses import dataclass

# Tektronix WFM Header Offsets (Magic Numbers)
OFFSET_VERSION = 2
OFFSET_BYTES_PER_POINT = 15
OFFSET_CURVE_OFFSET = 16
OFFSET_FASTFRAME_COUNT = 72
OFFSET_SET_TYPE = 78
OFFSET_VOLT_SCALE = 168
OFFSET_VOLT_OFFSET = 176
OFFSET_DATA_FORMAT = 240
OFFSET_TIME_SCALE = 488
OFFSET_TIME_OFFSET = 496
OFFSET_TIME_SIZE = 504

# Data Formats
FORMAT_INT16 = 0
FORMAT_INT32 = 1
FORMAT_FP32 = 4
FORMAT_INT8 = 7

class WfmReader:
    """
    Robust reader for Tektronix WFM binary files.
    """
    def __init__(self, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"WFM file not found: {filepath}")
            
        self.filepath = filepath
        self.num_frames = 0
        self.time_size = 0
        self.time_scale = 0.0
        self.time_offset = 0.0
        self.volt_scale = 0.0
        self.volt_offset = 0.0
        self.data_format = 0
        self.curve_offset = 0
        self.bytes_per_point = 1
        self.endian = '<' # Default Little Endian
        
        self._parse_header()
        
    def _parse_header(self):
        with open(self.filepath, 'rb') as f:
            # Endianness Check
            byte_order = f.read(2)
            if byte_order == b'\x0f\x0f':
                self.endian = '<'
            elif byte_order == b'\xf0\xf0':
                self.endian = '>'
            else:
                raise ValueError(f"Unknown byte order {byte_order} in {self.filepath}")
            
            # Helper for unpacking
            def read_val(offset, fmt, size):
                f.seek(offset)
                return struct.unpack(self.endian + fmt, f.read(size))[0]

            self.version = f.read(8).decode('ascii', errors='ignore') # From offset 2
            
            self.bytes_per_point = read_val(OFFSET_BYTES_PER_POINT, 'b', 1)
            self.curve_offset = read_val(OFFSET_CURVE_OFFSET, 'I', 4)
            
            n_fastframes = read_val(OFFSET_FASTFRAME_COUNT, 'I', 4)
            self.num_frames = n_fastframes + 1
            
            set_type = read_val(OFFSET_SET_TYPE, 'i', 4)
            if set_type == 0: # Single waveform
                self.num_frames = 1
            
            # explicit dimension 1 (Voltage)
            self.volt_scale = read_val(OFFSET_VOLT_SCALE, 'd', 8)
            self.volt_offset = read_val(OFFSET_VOLT_OFFSET, 'd', 8)
            self.data_format = read_val(OFFSET_DATA_FORMAT, 'i', 4)
            
            # implicit dimension 1 (Time)
            self.time_scale = read_val(OFFSET_TIME_SCALE, 'd', 8)
            self.time_offset = read_val(OFFSET_TIME_OFFSET, 'd', 8)
            self.time_size = read_val(OFFSET_TIME_SIZE, 'I', 4)
            
    def read_data(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Returns (time_array, volts_matrix)
        volts_matrix shape: (num_frames, time_size)
        """
        with open(self.filepath, 'rb') as f:
            f.seek(self.curve_offset)
            
            total_points = self.num_frames * self.time_size
            
            # Determine Numpy Dtype
            dtype_map = {
                FORMAT_INT8: np.int8,
                FORMAT_INT16: np.int16,
                FORMAT_INT32: np.int32,
                FORMAT_FP32: np.float32
            }
            np_dtype = dtype_map.get(self.data_format, np.int16)
            
            # Read raw data
            raw_data = np.fromfile(f, dtype=np_dtype, count=total_points)
            
            # Handle Endianness swapping if necessary
            system_is_little = np.little_endian
            file_is_little = (self.endian == '<')
            
            if file_is_little != system_is_little:
                raw_data = raw_data.byteswap()
                
            # Reshape
            if raw_data.size != total_points:
                 # Fallback/Warning for truncated files
                 frames_read = raw_data.size // self.time_size
                 if frames_read == 0:
                     raise ValueError(f"File {self.filepath} is too short to contain data.")
                 raw_data = raw_data[:frames_read * self.time_size]
                 frames = raw_data.reshape((frames_read, self.time_size))
            else:
                 frames = raw_data.reshape((self.num_frames, self.time_size))
            
            # Convert to Volts: V = code * scale + offset
            volts = frames.astype(np.float64) * self.volt_scale + self.volt_offset
            
            # Construct Time Array: T = index * scale + offset
            t = np.arange(self.time_size, dtype=np.float64) * self.time_scale + self.time_offset
            
            return t, volts
