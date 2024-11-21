import numpy as np
import pandas as pd
import asyncio, send2trash, glob, re, yaml, os
import matplotlib
matplotlib.use('Agg')
from src.ogp_height_plotter import PlotTool, get_offsets
from src.upload_inspect import DBClient
from src.parse_data import DataParser
from src.make_accuracy_plot import make_accuracy_plot
from src.param import *
from datetime import datetime

pbase = os.path.basename
pdir = os.path.dirname
pjoin = os.path.join

class SurveyProcessor():
    """Process Parsed OGP Survey CSV files and extract data for plotting and uploading to database."""
    def __init__(self, OGPSurveyFilePath: list, MetaFilePath: list, yamlconfig):
        """Initialize ImageProcessor object.
        
        Parameters:
        - OGPSurveyFilePath (list): (list of) Paths to parsed output csvs of OGP Surveys.
        - MetaFilePath (list): Paths to the metadata file for the OGP Survey files."""
        self.OGPSurveyFile = OGPSurveyFilePath
        self.MetaFile = MetaFilePath

        for i, file in enumerate(self.OGPSurveyFile):
            if not file.endswith('.csv'):
                raise ValueError('Parsed OGP result must be a csv file.')
            self.OGPSurveyFile[i] = file.replace('\\', '/')
        
        im_dir = pjoin(pdir(self.OGPSurveyFile[0]), 'images')
        if not os.path.exists(im_dir):
            os.makedirs(im_dir)
        self.im_dir = im_dir

        print(f'filename to process/upload: {self.OGPSurveyFile}')
        self.client = DBClient(yamlconfig)
        pass

    def __call__(self, component_type):
        """Process and upload OGP Survey files."""
        # self.getTrayFile()  
        self.process_and_upload(component_type)

    def getTrayFile(self):
        """Get Gantry Tray file and Tray files for NSH. 
        
        Return 
        - GantryTrayFile (str): Path to Gantry Tray file.
        - tray_files (list): List of paths to Tray files for NSH.
        - trash_file (bool): True if OGP Survey file is to be trashed."""

        base_path = self.OGPSurveyFile[0].split('OGP_results')[0]
        GantryTrayFile = base_path + 'OGP_results/assembly_trays/assembly_tray_input.xls'

        tray_files_pattern = base_path + 'data/Tray * for NSH.xls' 
        tray_files = glob.glob(tray_files_pattern)

        if tray_files == []: 
            raise FileNotFoundError(f'Tray files not found. Please put pin measurement files for trays as {base_path}data/Tray * for NSH.xls')
        
        tray_files.sort(key=lambda x: int(re.search(r'Tray (\d+)', x).group(1)))

        # placeholder
        trash_file = False

        self.tray_files = tray_files
        self.GantryTrayFile = GantryTrayFile

        return GantryTrayFile, tray_files, trash_file
 
    def __getArgs__(self, ex_file, meta_file, comp_type):
        """Get arguments for uploading to database, including the necessary meta data to upload and the image bytes.
        
        Return 
        - db_upload (dict): Dictionary of data to upload to database.
        - db_table_name (str): Name of the table in the database to upload to.
        - modtitle (str): Title of the module."""
        db_upload = {}

        with open(meta_file, 'r') as f:
            metadata = yaml.safe_load(f)

        modtitle = metadata['ComponentID']

        df = pd.read_csv(ex_file)
        filesuffix = pbase(ex_file).split('.')[0]

        if comp_type == 'baseplates':
            db_upload.update({'bp_name': modtitle})
            component_params = baseplates_params
        elif comp_type == 'hexaboards':
            db_upload.update({'hxb_name':modtitle})
            component_params = hexaboards_params
        elif comp_type == 'protomodules':
            component_params = protomodules_params
            ### This part will break! Need to fix it.
            Traysheets = [pd.read_csv(tray) for tray in self.tray_files]
            XOffset, YOffset, AngleOff = get_offsets([self.GantryTrayFile, self.OGPSurveyFile], Traysheets)
            db_upload.update({'proto_name': modtitle, 'x_offset_mu':np.round(XOffset*1000), 'y_offset_mu':np.round(YOffset*1000), 'ang_offset_deg':np.round(AngleOff,3)})
        else:
            raise ValueError("Component type not recognized. \
                Currently only supports baseplates, hexaboards, and protomodules. Please change the directory this file belongs to or add customed component type.")
        # else:
        #     component_params = others_params
        #     try:
        #         PMoffsets = asyncio.run(self.client.GrabSensorOffsets(modtitle))
        #         print(PMoffsets)
        #     except:
        #         PMoffsets =(asyncio.get_event_loop()).run_until_complete(self.client.GrabSensorOffsets(modtitle))
            
        #     SensorXOffset, SensorYOffset, SensorAngleOff = PMoffsets

        #     print('Retreived Protomodule Offset Info: ', SensorXOffset, SensorYOffset, SensorAngleOff)
        #     print('Making Accuracy Plot With:', modtitle, SensorXOffset, SensorYOffset, XOffset, YOffset, SensorAngleOff, AngleOff)
        #     acc_bytes = make_accuracy_plot(modtitle, SensorXOffset, SensorYOffset, int(XOffset*1000), int(YOffset*1000), SensorAngleOff, AngleOff)

        print("key:", component_params['key'])

        im_args = {"vmini":component_params['vmini'], "vmaxi":component_params['vmaxi'], 
                   "new_angle": component_params['new_angle'], "savename": pjoin(self.im_dir, comp_type, f"{filesuffix}_heights"),
                   "mod_flat": metadata['Flatness'], "title": metadata['ComponentID']}
        
        plotter = PlotTool(df)
        im_bytes = plotter(show_plot=False)

        comment = ''

        db_upload = {
            'flatness': metadata['Flatness'], 
            'thickness': np.round(np.mean(plotter.z_points),3), 
            'x_points':(plotter.x_points).tolist(), 
            'y_points':(plotter.y_points).tolist(), 
            'z_points':(plotter.z_points).tolist(),
            'hexplot':im_bytes, 
            'inspector': metadata['Operator'], 
            'comment':comment}
        
        db_upload.update(self.getDateTime(metadata))

        db_table_name = component_params['db_table_name']

        return db_upload, db_table_name, modtitle  
    
    def process_and_upload(self, comp_type):
        """Process all OGP Survey files and upload to database.
        
        Parameters:
        - `comp_type` (str): Type of component to process."""
        for ex_file, meta_file in zip(self.OGPSurveyFile, self.MetaFile):
            db_upload, db_table_name, modtitle = self.__getArgs__(ex_file, meta_file, comp_type)
            mappings = np.array([None],dtype=object)
            self.print_db_msg(comp_type, modtitle)
            # try:
            asyncio.run(self.client.upload_PostgreSQL(db_table_name, db_upload)) ## python 3.7
            # except:
                #(asyncio.get_event_loop()).run_until_complete(self.client.upload_PostgreSQL(db_table_name, db_upload)) ## python 3.6
            print(modtitle, 'uploaded!')
            # if trash_file:
                # send2trash.send2trash(ex_file)
            # print(f'Moved {ex_file} to recycle bin.')
        
    @staticmethod
    def print_db_msg(comp_type, modname):
        print('')
        print(f"###### NEW {comp_type} UPLOAD #######")
        print(f"###### FROM: {modname} #######")
        print('')

        print(f'Component type: {comp_type}')

    @staticmethod
    def getDateTime(metadata):
        """Get date and time from metadata."""
        date_inspect = datetime.strptime(metadata['RunDate'], '%m:%d:%y').date()
        time_inspect = datetime.strptime(metadata['RunTime'], '%H:%M:%S').time()
        
        return {"date_inspect": date_inspect, "time_inspect": time_inspect}
        
    
