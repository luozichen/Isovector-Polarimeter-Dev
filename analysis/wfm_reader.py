import struct
import numpy as np
import os

class WfmReader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.num_frames = 0
        self.time_size = 0
        self.time_scale = 0.0
        self.time_offset = 0.0
        self.volt_scale = 0.0
        self.volt_offset = 0.0
        self.data_format = 0 # 0=INT16, 7=INT8
        self.curve_offset = 0
        self.bytes_per_point = 1
        
        self._parse_header()
        
    def _parse_header(self):
        with open(self.filepath, 'rb') as f:
            # Endianness
            byte_order = f.read(2)
            if byte_order == b'\x0f\x0f':
                endian = '<'
            elif byte_order == b'\xf0\xf0':
                endian = '>'
            else:
                raise ValueError("Unknown byte order in WFM file")
            
            self.endian = endian
            
            # Version (Offset 2, 8 bytes)
            f.seek(2)
            self.version = f.read(8).decode('ascii', errors='ignore')
            
            # Bytes per point (Offset 15, 1 byte)
            f.seek(15)
            self.bytes_per_point = struct.unpack(endian + 'b', f.read(1))[0]
            
            # Curve Offset (Offset 16, 4 bytes)
            f.seek(16)
            self.curve_offset = struct.unpack(endian + 'I', f.read(4))[0]
            
            # FastFrame N (Offset 72, 4 bytes)
            f.seek(72)
            n_fastframes = struct.unpack(endian + 'I', f.read(4))[0]
            self.num_frames = n_fastframes + 1
            
            # SetType (Offset 78, 4 bytes)
            f.seek(78)
            set_type = struct.unpack(endian + 'i', f.read(4))[0]
            if set_type == 0: # Single waveform
                self.num_frames = 1
            
            # Explicit Dim 1 (Voltage)
            # Scale (Offset 168)
            f.seek(168)
            self.volt_scale = struct.unpack(endian + 'd', f.read(8))[0]
            # Offset (Offset 176)
            f.seek(176)
            self.volt_offset = struct.unpack(endian + 'd', f.read(8))[0]
            # Format (Offset 240)
            f.seek(240)
            self.data_format = struct.unpack(endian + 'i', f.read(4))[0]
            
            # Implicit Dim 1 (Time)
            # Scale (Offset 488)
            f.seek(488)
            self.time_scale = struct.unpack(endian + 'd', f.read(8))[0]
            # Offset (Offset 496)
            f.seek(496)
            self.time_offset = struct.unpack(endian + 'd', f.read(8))[0]
            # Size (Offset 504)
            f.seek(504)
            self.time_size = struct.unpack(endian + 'I', f.read(4))[0]
            
    def read_data(self):
        """
        Returns (time_array, volts_matrix)
        volts_matrix shape: (num_frames, time_size)
        """
        with open(self.filepath, 'rb') as f:
            f.seek(self.curve_offset)
            
            total_points = self.num_frames * self.time_size
            
            dtype = np.int16
            if self.data_format == 7: # INT8
                dtype = np.int8
            elif self.data_format == 0: # INT16
                dtype = np.int16
            elif self.data_format == 1: # INT32
                dtype = np.int32
            elif self.data_format == 4: # FP32
                dtype = np.float32
            
            # Read raw data
            # Note: struct.unpack is slow for large data. numpy.fromfile is better.
            # But numpy.fromfile reads machine byte order unless specified?
            # Actually we can specify dtype with endianness.
            
            dt_str = self.endian + ('b' if self.data_format == 7 else 
                                    'h' if self.data_format == 0 else 
                                    'i' if self.data_format == 1 else 
                                    'f')
                                    
            # Mapping to numpy dtype string
            np_dtype_map = {
                7: np.int8,
                0: np.int16,
                1: np.int32,
                4: np.float32
            }
            
            np_dtype = np_dtype_map.get(self.data_format, np.int16)
            
            # If endianness matches system, simpler. WFM is usually Little Endian.
            # Numpy defaults to system (usually Little).
            # If Big Endian, we need to swap.
            
            raw_data = np.fromfile(f, dtype=np_dtype, count=total_points)
            
            if self.endian == '>' and np.little_endian:
                raw_data = raw_data.byteswap()
            elif self.endian == '<' and not np.little_endian:
                raw_data = raw_data.byteswap()
                
            # Reshape
            frames = raw_data.reshape((self.num_frames, self.time_size))
            
            # Convert to Volts
            # V = code * scale + offset
            volts = frames.astype(np.float64) * self.volt_scale + self.volt_offset
            
            # Construct Time Array
            # T = index * scale + offset
            t = np.arange(self.time_size, dtype=np.float64) * self.time_scale + self.time_offset
            
            return t, volts

if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt
    
    path = sys.argv[1]
    wfm = WfmReader(path)
    print(f"Reading {path}")
    print(f"Frames: {wfm.num_frames}, Points: {wfm.time_size}")
    print(f"V Scale: {wfm.volt_scale}, V Offset: {wfm.volt_offset}")
    
    t, v = wfm.read_data()
    print(f"Data shape: {v.shape}")
    
    plt.figure()
    for i in range(min(5, wfm.num_frames)):
        plt.plot(t * 1e9, v[i], label=f"Frame {i}")
    plt.xlabel("Time (ns)")
    plt.ylabel("Volts")
    plt.legend()
    plt.savefig("wfm_test.png")
    print("Saved wfm_test.png")
