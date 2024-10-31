import numpy as np
import os, sys, asyncio, send2trash
import matplotlib
matplotlib.use('Agg')
from ogp_height_plotter import loadsheet, AppendFlats, AppendHeights, plot2d, uploadPostgres, get_offsets, check, get_shape_from_name, searchTrayID
from postgres_tools.upload_inspect import upload_PostgreSQL, GrabSensorOffsets
from make_accuracy_plot import make_accuracy_plot, make_fake_plot
from datetime import datetime

OGPSurveyfile = (sys.argv[1]).replace("\\", "/")
print(f'filename: {OGPSurveyfile}')
#print(f'filename: {OGPSurveyfile.split('data')[0]}')
#GantryTrayFile = OGPSurveyfile.split('OGP_results')[0]+'OGP_results/assembly_trays/assembly_tray_input.xls'
GantryTrayFile = OGPSurveyfile.split('data')[0]+'data/Tray 2 low light more points June 2023.xls';
#GantryTrayFile = OGPSurveyfile.split('data')[0]+'data/Tray 2 for NSH.xls';
#Tray1file = OGPSurveyfile.split('OGP_results')[0]+'data/Tray 1 for NSH.xls'
Tray1file = OGPSurveyfile.split('data')[0]+'data/Tray 1 for NSH.xls'
#Tray2file = OGPSurveyfile.split('OGP_results')[0]+'data/Tray 2 for NSH.xls'
Tray2file = OGPSurveyfile.split('data')[0]+'data/Tray 2 for NSH.xls'
Tray3file = OGPSurveyfile.split('data')[0]+'data/Tray 3 backlight.xls'
trash_file = False

if '/' in OGPSurveyfile:
    filesuffix = (OGPSurveyfile.split('/')[-1]).split('.')[0]
    home_folder = OGPSurveyfile.split('/')[-2]
    modname = OGPSurveyfile.split('/')[-1]
elif '\\' in OGPSurveyfile:    ############ this may not be needed.
    filesuffix = (OGPSurveyfile.split('\\')[-1]).split('.')[0]
    home_folder = OGPSurveyfile.split('\\')[-2]
    modname = OGPSurveyfile.split('/')[-1]
else:
    filesuffix = OGPSurveyfile.split('.')[0]
    modname = OGPSurveyfile.split('/')[-1]
    home_folder = None

if 'P' in modname:
    comp_type = 'protomodules';
if 'M' in modname: 
    comp_type = 'modules'
        
print('')
print(f"###### NEW {comp_type} UPLOAD #######")
print(f"###### FROM: {modname} #######")
print('')

print(f'Component type: {comp_type}')
if comp_type == 'baseplates':
    key = "Surface"
    vmini, vmaxi= 1.2, 2.2
    new_angle = 0
    db_table_name = 'bp_inspect'
elif comp_type == 'hexaboards':
    key = "flatness"
    vmini, vmaxi= 1.2, 2.9
    new_angle = 0
    db_table_name = 'hxb_inspect'
elif comp_type == 'protomodules':
    key = "Thick"
    vmini, vmaxi= 1.37, 1.79
    new_angle = 270
    db_table_name = 'proto_inspect'
else:
    key = "Thick"
    vmini, vmaxi= 2.75, 4.0
    new_angle = 270
    comp_type == 'modules'
    db_table_name = 'module_inspect'

print("key:", key)

resolution = 'LD'
geometry = 'full'
filenames = [OGPSurveyfile] #,OGPSurveyfile2,OGPSurveyfile3,OGPSurveyfile4]
sheetnames = loadsheet(filenames)
mod_flats = AppendFlats(sheetnames,key)
mappings = np.array([None],dtype=object)
Shape = get_shape_from_name(modname.replace('.xls',''));
sensor_Heights = AppendHeights(sheetnames,key, mappings, Shape)  ####### This prints line details
inspector = 'cmuperson'
comment = ''

date_inspect = datetime.now().date()
time_inspect = datetime.now().time()
# date_inspect = datetime.strptime(date, '%Y-%m-%d')
# time_inspect = datetime.strptime(time, '%H:%M:%S.%f')

if comp_type == 'modules' or comp_type == 'protomodules':
        filenames = [GantryTrayFile, OGPSurveyfile]
        sheetnames = loadsheet(filenames);
        TrayNum = searchTrayID(sheetnames[1], Shape)    # CONFUSING: Looking For Tray # in Survey File
        print("Tray Used for Assembly:", TrayNum)
filenames = [OGPSurveyfile] #,OGPSurveyfile2,OGPSurveyfile3,OGPSurveyfile4]
sheetnames = loadsheet(filenames)

if TrayNum == 1:
    CurrentTrayFile = Tray1file;
elif TrayNum == 2:
    CurrentTrayFile = Tray2file;
elif TrayNum == 3:
    CurrentTrayFile = Tray3file;
print("Current Tray File: ", CurrentTrayFile)

for i in range(len(filenames)):
    modtitle = f"{sheetnames[i]}"
    #modtitle = f"{(filenames[i].split('/')[-1]).split('.')[0]}"
    print('modtitle',modtitle)
    im_bytes = plot2d(sensor_Heights[i][0], sensor_Heights[i][1], sensor_Heights[i][2],
           limit = 0, vmini=vmini, vmaxi=vmaxi, 
           center = 25, rotate = 345, new_angle = new_angle,
           title = modtitle, savename = f"{comp_type}\{filesuffix}_heights", value = 1,details=1, day_count = None, mod_flat = mod_flats[i], show_plot = False)
    acc_bytes = make_fake_plot();
    
    print(float(mod_flats[0]))
    db_upload = {
        'flatness': np.round(mod_flats[i],3), 
        'thickness': np.round(np.mean(sensor_Heights[i][2]),3), 
        'x_points':(sensor_Heights[i][0]).tolist(), 
        'y_points':(sensor_Heights[i][1]).tolist(), 
        'z_points':(sensor_Heights[i][2]).tolist(), 
        'date_inspect':date_inspect, 
        'time_inspect': time_inspect, 
        'hexplot':im_bytes, 
        'inspector':inspector, 
        'comment':comment}
    if comp_type == 'baseplates':
        material = 'cf'
        db_upload.update({'bp_name': modtitle})
    elif comp_type == 'hexaboards':
        db_upload.update({'hxb_name':modtitle})
    elif comp_type == 'protomodules':
        #Needs More Code Here For Different Shapes of ProtoModules'
        print('1010101: this is modtitle:', modtitle)
        Shape = get_shape_from_name(modtitle);
        
        if check(Tray3file) & check(Tray1file) & check(Tray2file):
            Traysheets = loadsheet([Tray1file,Tray2file,Tray3file])
        elif check(Tray1file) & check(Tray2file):
            Traysheets = loadsheet([Tray1file,Tray2file])
                
        XOffset, YOffset, AngleOff = get_offsets([GantryTrayFile, OGPSurveyfile], Traysheets, Shape, comp_type, TrayNum)
        db_upload.update({'proto_name': modtitle, 'x_offset_mu':np.round(XOffset*1000), 'y_offset_mu':np.round(YOffset*1000), 'ang_offset_deg':np.round(AngleOff,3)})
    else:
        #Needs More Code Here For Differet Shapes of Modules
        print('1010101: this is modtitle:', modtitle)
        Shape = get_shape_from_name(modtitle);
        
        if check(Tray3file) & check(Tray1file) & check(Tray2file):
            Traysheets = loadsheet([Tray1file,Tray2file,Tray3file])
        elif check(Tray1file) & check(Tray2file):
            Traysheets = loadsheet([Tray1file,Tray2file])

        XOffset, YOffset, AngleOff = get_offsets([GantryTrayFile, OGPSurveyfile], Traysheets, Shape, comp_type, TrayNum)
        db_upload.update({'module_name': modtitle, 'x_offset_mu':np.round(XOffset*1000), 'y_offset_mu':np.round(YOffset*1000), 'ang_offset_deg':np.round(AngleOff,3)})
        try:
            PMoffsets = asyncio.run(GrabSensorOffsets(modtitle))
            print(PMoffsets)
        except:
            PMoffsets =(asyncio.get_event_loop()).run_until_complete(GrabSensorOffsets(modtitle))
        
        #SensorXOffset, SensorYOffset, SensorAngleOff = PMoffsets[0]
        SensorXOffset, SensorYOffset, SensorAngleOff = PMoffsets

        print('Retreived Protomodule Offset Info: ', SensorXOffset, SensorYOffset, SensorAngleOff)
        print('Making Accuracy Plot With:', modtitle, SensorXOffset, SensorYOffset, XOffset, YOffset, SensorAngleOff, AngleOff)
        acc_bytes = make_accuracy_plot(modtitle, SensorXOffset, SensorYOffset, int(XOffset*1000), int(YOffset*1000), SensorAngleOff, AngleOff)

    try:
        asyncio.run(upload_PostgreSQL(db_table_name, db_upload)) ## python 3.7
    except:
        (asyncio.get_event_loop()).run_until_complete(upload_PostgreSQL(db_table_name, db_upload)) ## python 3.6
    print(modtitle, 'uploaded!')
    if trash_file:
        send2trash.send2trash(OGPSurveyfile)
        print(f'Moved {OGPSurveyfile} to recycle bin.')




    
