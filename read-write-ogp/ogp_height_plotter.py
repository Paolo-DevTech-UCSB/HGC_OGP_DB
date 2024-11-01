# import pandas as pd
# import os, sys
import numpy as np
import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as cls
import xlrd

# from hexmap.plot_summary import *

def read_file(loc,sheetname):
    wb=xlrd.open_workbook(loc)
    globals()[f"{sheetname}"]=wb.sheet_by_index(0)

def loadsheet(filenames):
    sheet = np.array([i.split(".xls")[0].split('/')[-1] for i in filenames])
    for i in range(len(filenames)):
        read_file(f'{filenames[i]}',sheet[i])
    return sheet

def displaysheet(sheet,row):
    for i in range(row):
        actual = globals()[f"{sheet}"].cell_value(i,2)
        print(actual)

def Height(sheetname,key = 'Thick', Shape = "HD Full"):   ### change the key here for searching where is the first Height in the excel
    row = globals()[f"{sheetname}"].nrows
    #print("total number of row is", row)
    for i in range(row):
        actual = str(globals()[f'{sheetname}'].cell_value(i,2))
        if (key in actual):
            print(f"First Height locates at line {i} in {sheetname}.xls")
            print(f"Row name: {actual}")
            print()
            height1 = i
            break
    #height1 = i
    globals()[f'Height_{sheetname}']=np.zeros((3,25))
    if sheetname == '815 unconstrained flatness':
        lines=[24,25,26]
    else:
        lines=[height1,height1+1,height1+2]
    #lines = [20,21,22]
    
    if Shape == "HD Full" or Shape == "LD Full":
        HeightsRange = 25;
    elif Shape == "LD Right" or Shape == "LD Left":
        HeightsRange = 21;
    
    for i in range(0,HeightsRange):
    #print(i)
        x=float(globals()[f'{sheetname}'].cell_value(lines[0]+i*5,5))
        y=float(globals()[f'{sheetname}'].cell_value(lines[1]+i*5,5))
        z=float(globals()[f'{sheetname}'].cell_value(lines[2]+i*5,5))
        globals()[f'Height_{sheetname}'][0,i]=x
        globals()[f'Height_{sheetname}'][1,i]=y
        globals()[f'Height_{sheetname}'][2,i]=z
        #print(x)
    return globals()[f'Height_{sheetname}']

def Flat(sheetname,key = 'Surf'): ### change the key here for searching where is the first Height in the excel
    key = 'Surface'; ##### <---- important for this, or else we'd need to separate the keys into two.
    row = globals()[f"{sheetname}"].nrows
    for i in range(row):
        actual = str(globals()[f'{sheetname}'].cell_value(i,2));
        subactual = str(globals()[f'{sheetname}'].cell_value(i,3));
    
        if (key in actual):
            if 'Profile' in subactual:
                height1 = i
                break
    globals()[f'Height_{sheetname}']=np.zeros((3,25))
    if sheetname == '815 unconstrained flatness':
        lines=[24,25,26]
    else:
        ines=[height1,height1+1,height1+2]
    
    if 'Points' in str(globals()[f'{sheetname}'].cell_value(height1,3)):
        flatness = (float(globals()[f'{sheetname}'].cell_value(height1,5)))
    else:
        flatness = (float(globals()[f'{sheetname}'].cell_value(height1,5)))
    print()
    print(f"Flatness is {flatness}, found on line {i} in {sheetname}.xls")
    return flatness;

def getDate(sheetname,key = 'Date'):   ### change the key here for searching where is the first Height in the excel
    row = globals()[f"{sheetname}"].nrows
    print('row acquired')
    #print("total number of row is", row)
    for i in range(row):
        print(i, str(globals()[f'{sheetname}'].cell_value(i,0)), str(globals()[f'{sheetname}'].cell_value(i,1)), str(globals()[f'{sheetname}'].cell_value(i,2)))
        actual = str(globals()[f'{sheetname}'].cell_value(i,2))
        if (key in actual):
            print(f"First Date locates at line {i} in {sheetname}.xls")
            print(f"Row name: {actual}")
            print()
            height1 = i
            break
    #height1 = i
    globals()[f'Height_{sheetname}']=np.zeros((3,25))
    if sheetname == '815 unconstrained flatness':
        lines=[24,25,26]
    else:
        lines=[height1,height1+1,height1+2]
    #lines = [20,21,22]
    for i in range(0,25):
    #print(i)
        x=float(globals()[f'{sheetname}'].cell_value(lines[0]+i*5,5))
        y=float(globals()[f'{sheetname}'].cell_value(lines[1]+i*5,5))
        z=float(globals()[f'{sheetname}'].cell_value(lines[2]+i*5,5))
        globals()[f'Height_{sheetname}'][0,i]=x
        globals()[f'Height_{sheetname}'][1,i]=y
        globals()[f'Height_{sheetname}'][2,i]=z
        #print(x)
    return globals()[f'Height_{sheetname}']

def AppendTime(sheetnames,key = 'Date'):
    All_Heights=[]
    for j in range(len(sheetnames)):
      All_Heights.append(np.array(getDate(sheetnames[j],key)))
    return All_Heights

def AppendHeights(sheetnames,key = 'Thick', mappings = None, Shape = "HD Full"):
    All_Heights=[]
    for j in range(len(sheetnames)):
        if mappings[j] is not None:
            All_Heights.append(np.array(Height(sheetnames[j],key,Shape))[:,mappings[j]])
        else:
            All_Heights.append(np.array(Height(sheetnames[j],key,Shape)))
    return All_Heights

def AppendFlats(sheetnames,key = 'Surface'):
    key = 'Surface';
    All_Flats=[]
    for j in range(len(sheetnames)):
        All_Flats.append(np.array(Flat(sheetnames[j],key)))
    return All_Flats

def vec_angle(x,y):
    angle_arctan = np.degrees(np.arctan2(y,x))
    return angle_arctan

def vec_rotate(old_x, old_y, old_angle, new_angle = 120):
    rad = np.radians(new_angle - old_angle)
    new_x = old_x*np.cos(rad)-old_y*np.sin(rad)
    new_y = old_x*np.sin(rad)+old_y*np.cos(rad)
    return new_x, new_y

def plot2d(x, y, zheight, limit = 0, vmini=1.05, vmaxi=4.5, center = 0, rotate = 0 , new_angle = 120, details = 0, title="", savename="", value = 1, day_count = None, mod_flat = None, show_plot = True):

    # print('sorting for consisitency')
    # argx = np.argsort(x)
    # x, y, zheight = x[argx], y[argx], zheight[argx]
    # argy = np.argsort(y)
    # x, y, zheight = x[argy], y[argy], zheight[argy]
    mean_h = np.mean(zheight)
    std_h = np.std(zheight)
    max_h = max(zheight)
    min_h = min(zheight)
    print(f"Average Height is {mean_h:.3f} mm")
    print(f"Maximum Height is {max_h:.3f} mm")
    print(f"Minimum Height is {min_h:.3f} mm")
    print(f"Height --> {mean_h:.3f} + ({max_h - mean_h:.3f}) - ({mean_h - min_h:.3f}) mm")
    print()
    if center != 0:
        if (type(center) is int) and (center >0 and center <26):
            ######## Last point is the center if given 25
            x = x- x[center-1]
            y = y- y[center-1]
            if details == 1:
                print(f"Point {center} center at (0,0)")
        else:
            print("Please give a integer between 1 and 25 for center point") 
    else:
        if details == 1:
            print("No center")

    if rotate != 0:
        if (type(rotate) is int) and (rotate > 0 and rotate <26):
            rotate_angle = vec_angle(x[rotate-1], y[rotate-1])
        else:
            rotate_angle = 0
            # print("Please give a integer between 1 and 25 for rotate point")   
        for i in range(len(x)):
            x[i], y[i] = vec_rotate(x[i],y[i],rotate_angle, new_angle)
        if details == 1:
            print(f"Point {rotate} originally at {rotate_angle:.2f} degrees")
            print(f"Point {rotate} rotates to {new_angle:.2f} degrees")

    else:
        if details == 1:
            print("No rotation")

    fig=plt.figure(dpi=150, figsize=(9,5))
    axs=fig.add_subplot(111); axs.set_aspect('equal')
    
    
    if value == 1:
        image=axs.hexbin(x,y,zheight,gridsize=20, vmin = vmini, vmax = vmaxi, cmap=plt.cm.coolwarm)
        norm = cls.Normalize(vmin=vmini, vmax=vmaxi)
        sm = plt.cm.ScalarMappable(norm=norm, cmap=plt.cm.coolwarm)
        cb=plt.colorbar(sm, ax= axs); cb.minorticks_on()
        # for i in range(len(zheight)):
            # axs.annotate(f"${zheight[i]:.3f}$",(x[i],y[i]),color = "black", fontsize = 9)
            # axs.annotate(f"${i}$",(x[i]-2.5,y[i]-5.5),color = "green", fontsize = 7)
            # if zheight[i]-mean_h < 0:
            #     axs.annotate(f"(${(zheight[i]-mean_h):.3f}$)",(x[i]-2.5,y[i]-5.5),color = "blue", fontsize = 7)
            # else:
            #     axs.annotate(f"(${(zheight[i]-mean_h):.3f}$)",(x[i]-2.5,y[i]-5.5),color = "red", fontsize = 7)
    # elif value == 0:
    #     image=axs.hexbin(x,y,zheight-mean_h,gridsize=20, vmin = vmini, vmax = vmaxi, cmap=plt.cm.coolwarm)
    #     norm = cls.Normalize(vmin=vmini, vmax=vmaxi)
    #     for i in range(len(zheight)):
    #         axs.annotate(f"${(zheight[i]-mean_h):.3f}$",(x[i],y[i]),color = "black")
    else:
        if title == '815 PCB fiducials':
            thickness = np.array([10,11,12,13,14,15,16,17,18,1,2,3,4,5,6,7,8,9,19,20,21,22,23,24,25])
            axs.annotate(f"{thickness[i]}",(x[i],y[i]),color="black")
    #axs.annotate(f"{i+1}",(temp[0][i],temp[1][i]),color="black")
        else:
            axs.annotate(f"{i+1}",(x[i],y[i]),color="black")

    
    #axs.annotate("1", temp[0][0],temp[1][0])
    axs.set_xlabel("x (mm)")
    axs.set_ylabel("y (mm)")
    axs.minorticks_on()
    axs.set_xlim(left=-100, right=100)
    axs.set_ylim(bottom=-100, top=100)
    #axs.set_xticks([-100,-75,-50,-25,0,25,50,75,100])
    #axs.set_yticks([-100,-75,-50,-25,0,25,50,75,100])
    cb.set_label("Height (mm)")
    axs.set_title(title)
    if mod_flat is not None:
        textstr = '\n'.join((f'mean: {mean_h:.3f} mm',f'std:     {std_h:.3f} mm','', f'height: {mean_h:.3f} mm', f'       $+$ ({max_h - mean_h:.3f}) mm', f'       $-$ ({mean_h - min_h:.3f}) mm',
                            '',f'$\Delta$H = {max_h - min_h:.3f} mm','', f'maxH: {max_h:.3f} mm', f'minH:  {min_h:.3f} mm','', f'flatness: {mod_flat:.3f}'))
    else:
        textstr = '\n'.join((f'mean: {mean_h:.3f} mm',f'std:     {std_h:.3f} mm','', f'height: {mean_h:.3f} mm', f'       $+$ ({max_h - mean_h:.3f}) mm', f'       $-$ ({mean_h - min_h:.3f}) mm',
                         '',f'$\Delta$H = {max_h - min_h:.3f} mm','', f'maxH: {max_h:.3f} mm', f'minH:  {min_h:.3f} mm',''))
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    axs.text(1.3, 1.0, textstr, transform=axs.transAxes, fontsize=10, verticalalignment='top', bbox=props)
    # legendstr = '\n'.join(('*Numbers in brackets represent', 'deviation from mean.'))
    # axs.text(1.3, 0.40, legendstr, transform=axs.transAxes, fontsize=5, verticalalignment='top', color = 'blue')
    if day_count is not None:
        legendstr = '\n'.join((f'Day',f'{day_count}'))
        # legendstr = '\n'.join((f'',f'{day_count}'))
        axs.text(1.3, 0.20, legendstr, transform=axs.transAxes, fontsize=20, verticalalignment='top', color = 'blue')

    if show_plot:
        plt.show(); 
        plt.close()
    
    from io import BytesIO  
    buffer = BytesIO()
    #plt.savefig(f"{(savename.split('/'))[-1]}.png", bbox_inches='tight') # uncomment here for saving the 2d plot
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer.read()

def get_data(x, y, zheight, limit = 0, vmini=1.05, vmaxi=4.5, center = 0, rotate = 0 , new_angle = 120, details = 0, title="", savename="", value = 1, day_count = None, mod_flat = None, show_plot = True):

    # print('sorting for consisitency')
    # argx = np.argsort(x)
    # x, y, zheight = x[argx], y[argx], zheight[argx]
    # argy = np.argsort(y)
    # x, y, zheight = x[argy], y[argy], zheight[argy]
    mean_h = np.mean(zheight)
    std_h = np.std(zheight)
    max_h = max(zheight)
    min_h = min(zheight)
    print(f"Average Height is {mean_h:.3f} mm")
    print(f"Maximum Height is {max_h:.3f} mm")
    print(f"Minimum Height is {min_h:.3f} mm")
    print(f"Height --> {mean_h:.3f} + ({max_h - mean_h:.3f}) - ({mean_h - min_h:.3f}) mm")
    print()
    if center != 0:
        if (type(center) is int) and (center >0 and center <26):
            ######## Last point is the center if given 25
            x = x- x[center-1]
            y = y- y[center-1]
            if details == 1:
                print(f"Point {center} center at (0,0)")
        else:
            print("Please give a integer between 1 and 25 for center point") 
    else:
        if details == 1:
            print("No center")

    if rotate != 0:
        if (type(rotate) is int) and (rotate > 0 and rotate <26):
            rotate_angle = vec_angle(x[rotate-1], y[rotate-1])
        else:
            rotate_angle = 0
            # print("Please give a integer between 1 and 25 for rotate point")   
        for i in range(len(x)):
            x[i], y[i] = vec_rotate(x[i],y[i],rotate_angle, new_angle)
        if details == 1:
            print(f"Point {rotate} originally at {rotate_angle:.2f} degrees")
            print(f"Point {rotate} rotates to {new_angle:.2f} degrees")

    else:
        if details == 1:
            print("No rotation")

    fig=plt.figure(dpi=150, figsize=(9,5))
    axs=fig.add_subplot(111); axs.set_aspect('equal')
    
    
    if value == 1:
        image=axs.hexbin(x,y,zheight,gridsize=20, vmin = vmini, vmax = vmaxi, cmap=plt.cm.coolwarm)
        norm = cls.Normalize(vmin=vmini, vmax=vmaxi)
        sm = plt.cm.ScalarMappable(norm=norm, cmap=plt.cm.coolwarm)
        cb=plt.colorbar(sm, ax= axs); cb.minorticks_on()
        for i in range(len(zheight)):
            axs.annotate(f"${zheight[i]:.3f}$",(x[i],y[i]),color = "black", fontsize = 9)
            # axs.annotate(f"${i}$",(x[i]-2.5,y[i]-5.5),color = "green", fontsize = 7)
            # if zheight[i]-mean_h < 0:
            #     axs.annotate(f"(${(zheight[i]-mean_h):.3f}$)",(x[i]-2.5,y[i]-5.5),color = "blue", fontsize = 7)
            # else:
            #     axs.annotate(f"(${(zheight[i]-mean_h):.3f}$)",(x[i]-2.5,y[i]-5.5),color = "red", fontsize = 7)
    # elif value == 0:
    #     image=axs.hexbin(x,y,zheight-mean_h,gridsize=20, vmin = vmini, vmax = vmaxi, cmap=plt.cm.coolwarm)
    #     norm = cls.Normalize(vmin=vmini, vmax=vmaxi)
    #     for i in range(len(zheight)):
    #         axs.annotate(f"${(zheight[i]-mean_h):.3f}$",(x[i],y[i]),color = "black")
    else:
        if title == '815 PCB fiducials':
            thickness = np.array([10,11,12,13,14,15,16,17,18,1,2,3,4,5,6,7,8,9,19,20,21,22,23,24,25])
            axs.annotate(f"{thickness[i]}",(x[i],y[i]),color="black")
    #axs.annotate(f"{i+1}",(temp[0][i],temp[1][i]),color="black")
        else:
            axs.annotate(f"{i+1}",(x[i],y[i]),color="black")

    
    #axs.annotate("1", temp[0][0],temp[1][0])
    axs.set_xlabel("x (mm)")
    axs.set_ylabel("y (mm)")
    axs.minorticks_on()
    axs.set_xlim(left=-100, right=100)
    axs.set_ylim(bottom=-100, top=100)
    #axs.set_xticks([-100,-75,-50,-25,0,25,50,75,100])
    #axs.set_yticks([-100,-75,-50,-25,0,25,50,75,100])
    cb.set_label("Height (mm)")
    axs.set_title(title)
    if mod_flat is not None:
        textstr = '\n'.join((f'mean: {mean_h:.3f} mm',f'std:     {std_h:.3f} mm','', f'height: {mean_h:.3f} mm', f'       $+$ ({max_h - mean_h:.3f}) mm', f'       $-$ ({mean_h - min_h:.3f}) mm',
                            '',f'$\Delta$H = {max_h - min_h:.3f} mm','', f'maxH: {max_h:.3f} mm', f'minH:  {min_h:.3f} mm','', f'flatness: {mod_flat:.3f}'))
    else:
        textstr = '\n'.join((f'mean: {mean_h:.3f} mm',f'std:     {std_h:.3f} mm','', f'height: {mean_h:.3f} mm', f'       $+$ ({max_h - mean_h:.3f}) mm', f'       $-$ ({mean_h - min_h:.3f}) mm',
                         '',f'$\Delta$H = {max_h - min_h:.3f} mm','', f'maxH: {max_h:.3f} mm', f'minH:  {min_h:.3f} mm',''))
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    axs.text(1.3, 1.0, textstr, transform=axs.transAxes, fontsize=10, verticalalignment='top', bbox=props)
    # legendstr = '\n'.join(('*Numbers in brackets represent', 'deviation from mean.'))
    # axs.text(1.3, 0.40, legendstr, transform=axs.transAxes, fontsize=5, verticalalignment='top', color = 'blue')
    if day_count is not None:
        legendstr = '\n'.join((f'Day',f'{day_count}'))
        # legendstr = '\n'.join((f'',f'{day_count}'))
        axs.text(1.3, 0.20, legendstr, transform=axs.transAxes, fontsize=20, verticalalignment='top', color = 'blue')

    if show_plot:
        plt.show(); 
        plt.close()
    
    plt.savefig(f"{(savename.split('/'))[-1]}.png", bbox_inches='tight') # uncomment here for saving the 2d plot
    plt.close()

def uploadPostgres(x, y, zheight, mod_flat, title):
    return None

####################################

import os
def check(file):
    if os.path.exists(file):
        return True
    else:
        print('FILEPATHS MAY BE WRONG!! CANNOT FIND ' + file)
        print()
        return False

def searchTrayPin(sheet,keys, details = 0, Tray = 0, points = None):
    if Tray == 1:
        if "TrayNumber" in globals():
            sheet = Traysheets[globals()["TrayNumber"]-1]
        else:
            print("Could not find any Tray number in the OGPSurveyfile by auto detection")
            print("Continue using the GantryTrayfile")
            print()
    Feature = 0
    row = globals()[f"{sheet}"].nrows
    print("is this working?", sheet, row)
    #print(f"total row is {row}")
    for i in range(row):
        actual = str(globals()[f"{sheet}"].cell_value(i,2))
        for j in range(len(keys)):
            if (keys[j] in actual):
                Feature += 1
    print(f"Found {Feature} Feature rows")
    for i in range(row):
        actual = str(globals()[f"{sheet}"].cell_value(i,2))
        for j in range(len(keys)):
            #print(keys, actual)  #comment me out!!!
            if (keys[j] in actual):
                if Feature == 2:
                    x = float(globals()[f"{sheet}"].cell_value(i,5))
                    y = float(globals()[f"{sheet}"].cell_value(i+1,5))
                    points[f"{keys[j]}.X"] = x
                    points[f"{keys[j]}.Y"] = y
                if Feature == 4:
                    value = float(globals()[f"{sheet}"].cell_value(i,4))
                    if "X" in actual:
                         points[f"{keys[j]}.X"] = value
                    if "Y" in actual:
                        points[f"{keys[j]}.Y"] = value
                if details == 1:
                    print(f"{keys[j]} locates at line {i} in {sheet}.xls")
                    print(f"Row name: {actual}")
                    #print(f"value: {value}")
    print()

def searchSensorFD(sheet,keys,details = 0, fd = None, points=None):
    #def searchSensorFD(sheet,keys,details = 0,Tray = 0,Traykeys=["Tray"], fd = None, points=None):   Changed from this OCT 30
    print(sheet)
    row = globals()[f"{sheet}"].nrows
    for i in range(row):
        actual = str(globals()[f'{sheet}'].cell_value(i,2))
        """if Tray == 1:
            for k in range(len(Traykeys)):
                if (Traykeys[k] in actual):
                    for c in range(3,6):
                        if "T" in str(globals()[f"{sheet}"].cell_value(i,c)):
                            globals()["TrayNumber"] = int(actual.split("Tray")[-1])
                            print("Auto detect Tray to be", actual)
                            print()
                            break
                    break"""  #Commented out becuase it's uneeded
        for j in range(len(keys)):
            if (keys[j] in actual):
                x = float(globals()[f'{sheet}'].cell_value(i,5))
                y = float(globals()[f'{sheet}'].cell_value(i+1,5))
                if details == 1:
                    print(f"Sensor Fiducial locates at line {i} in {sheet}.xls")
                    print(f"Row name: {actual}")
                    print(f"x: {x}, y: {y}")
                fd.append(actual)
                points[actual] = np.array([x,y])
                break
    print(f"Found {len(fd)} Sensor Fiducial Points")
    print()
    return fd, points

def searchTrayID(sheet, Shape):
    keys = ['Tray 1','Tray 2','Tray 3','TRAY','Tray1','Tray2','Tray3']
    TrayInfo = []
    red = 0;
    row = globals()[f"{sheet}"].nrows
    for i in range(row):
        actual = str(globals()[f'{sheet}'].cell_value(i,2))
        TrayBoolean = str(globals()[f'{sheet}'].cell_value(i,3))
        for j in range(len(keys)):
            if (keys[j] in actual):
                TrayInfo.append([keys[j],actual,TrayBoolean])
    #print("Tray info:", TrayInfo)
    for info in TrayInfo:
        if str(1) in info[0]:
            TrayNum = 1; 
            red = red + 1;
        if str(2) in info[0]:
            TrayNum = 2; 
            red = red + 1;
        if str(3) in info[0]:
            TrayNum = 3; 
            red = red + 1;
    if red > 1 :
        TrayNum = int(input("It says there more than 2 tray sheets which one is it? : "))
    return TrayNum

def plotFD(FDpoints,FDCenter,Center, Off, points, fd, sheetnames = ['','']):
    CenterX = f"{Center}.X"
    CenterY = f"{Center}.Y"
    OffX = f"{Off}.X"
    OffY = f"{Off}.Y"
    if FDpoints == 2:
        Xp = [points[CenterX],points[OffX], points[fd[0]][0],points[fd[1]][0]]
        Yp = [points[CenterY],points[OffY], points[fd[0]][1],points[fd[1]][1]]
        plt.figure(dpi=250)
        plt.plot(Xp,Yp,'o',ms=2)
        plt.arrow(Xp[1],Yp[1],Xp[0]-Xp[1],Yp[0]-Yp[1],lw=0.5,color='g')
        plt.arrow(Xp[2],Yp[2],Xp[3]-Xp[2],Yp[3]-Yp[2],lw=0.5,color='orange')
        plt.plot(FDCenter[0],FDCenter[1],'ro',label='FDCenter',ms=2)
        names = ['P1CenterPin','P1OffcenterPin','FD1','FD2']
        for i in range(len(Xp)): 
            plt.annotate(names[i],(Xp[i],Yp[i]))
        plt.legend()
        plt.xlim(60,160)
        plt.title(sheetnames[1])
        plt.xlabel("x [mm]")
        plt.ylabel("y [mm]")
    if FDpoints == 4:
        Xp = [points[CenterX],points[OffX], points[fd[0]][0],points[fd[1]][0],points[fd[2]][0],points[fd[3]][0]]
        Yp = [points[CenterY],points[OffY], points[fd[0]][1],points[fd[1]][1],points[fd[2]][1],points[fd[3]][1]]
        plt.figure(dpi=250)
        plt.plot(Xp,Yp,'o',ms=2)
        plt.arrow(Xp[1],Yp[1],Xp[0]-Xp[1],Yp[0]-Yp[1],lw=0.5,color='g')
        #plt.plot([(Xp[3]+Xp[2])/2],[(Yp[3]+Yp[2])/2],lw=0.5)
        plt.arrow(Xp[2],Yp[2],Xp[4]-Xp[2],Yp[4]-Yp[2],lw=0.5,color='orange')
        plt.arrow(Xp[3],Yp[3],Xp[5]-Xp[3],Yp[5]-Yp[3],lw=0.5,color='orange')
        plt.plot(FDCenter[0],FDCenter[1],'ro',label='FDCenter',ms=2)
        names = ['P1CenterPin','P1OffcenterPin','FD1','FD2','FD3','FD4']
        for i in range(len(Xp)): 
            plt.annotate(names[i],(Xp[i],Yp[i]))
        plt.legend()
        plt.xlim(60,160)
        plt.title(sheetnames[1])
        plt.xlabel("x [mm]")
        plt.ylabel("y [mm]")
    print()


def angle(points,FDpoints=4,OffCenterPin = "Left", details = 0, plot = 0, Center = None, Off = None, fd = None, Position = 1, Shape = "HD Full", comp_type = "module"):
    #this needs to be reorganized/reconfigured -Paolo Oct 30
    # def angle(points,FDpoints=4,OffCenterPin = "Left", details = 0, plot = 0, Center = None, Off = None, fd = None):
    ValidOffCenterPins = ['P1E','P1F','P1G','P1H','P2E','P2F','P2G','P2H']
    
    CenterX = f"{Center}.X"
    CenterY = f"{Center}.Y"
    OffX = f"{Off}.X"
    OffY = f"{Off}.Y"
    
    #Errors and Warning Messaging ##### #####
    
    if (FDpoints != 2) and (FDpoints != 4):
        print(f"{FDpoints} Fiducial Points. Invalid Number. Please use either 2 or 4 Fiducial Points")
        #print("Detailing the Sensor FD points searching process for debugging")
        return 
    else:
        print(f"Using {FDpoints} Fiducial Points ")
    print()
    ValidPin = False;
    for pin in ValidOffCenterPins:
        if OffCenterPin == pin:
            print("Valid Pin Positions")
            ValidPin = True;
    if ValidPin == False:
        print("Invalid OffCenter Pin Position")
        print("Please indicate whether OffCenter Pin is on the Left or Right to the Center Pin")
        #break
        return
    
    #print(points)
    # MAKING 'PIN' VECTOR ####### #######
    # PIN VECTOR POINTS TO THE RIGHT ----> OR up +90
    print("Making a Vector using Pin Data With the Following Configuartion:")
    if OffCenterPin == "P1E":     #FULLS and TOPS
        Pin = np.array([points[CenterX],points[CenterY]]) - np.array([points[OffX],points[OffY]])
        PinAdj = 0;
        print("OffCenter Pin is on the Left relative to the Center Pin   (oc) ----> (c)   +0 ")
    elif OffCenterPin == "P2G":     #FULLS and TOPS
        Pin = np.array([points[OffX],points[OffY]]) - np.array([points[CenterX],points[CenterY]])
        PinAdj = 0;
        print("OffCenter Pin is on the Right relative to the Center Pin   (c) ----> (oc)  +0 ")
        
        
    elif OffCenterPin == "P1G":     #BOTTOMS
        Pin = np.array([points[OffX],points[OffY]]) - np.array([points[CenterX],points[CenterY]])
        PinAdj = 0;
        print("OffCenter Pin is on the Right relative to the Center Pin   (c) ----> (oc)  +0 ")
    elif OffCenterPin == "P2E":     #BOTTOMS
        Pin = np.array([points[CenterX],points[CenterY]]) - np.array([points[OffX],points[OffY]])
        PinAdj = 0;
        print("OffCenter Pin is on the Right relative to the Center Pin   (oc) ----> (c)  +0 ")
        
         
    elif OffCenterPin == "P1H":     #LEFTS
        Pin = np.array([points[CenterX],points[CenterY]]) - np.array([points[OffX],points[OffY]]) 
        PinAdj = 90;
        print("OffCenter Pin is Below the Center Pin   (up)  +90 ")
    elif OffCenterPin == "P2F":     #LEFTS
        Pin = np.array([points[OffX],points[OffY]]) - np.array([points[CenterX],points[CenterY]])
        PinAdj = 90;
        print("OffCenter Pin is Above the Center Pin   (up)  +90 ")
    
    
    elif OffCenterPin == "P1F":     #RIGHTS
        Pin = np.array([points[CenterX],points[CenterY]]) - np.array([points[OffX],points[OffY]])
        PinAdj = 90;
        print("OffCenter Pin is Above the Center Pin   (up)  +90")
    elif OffCenterPin == "P2H":     #RIGHTS
        Pin = np.array([points[OffX],points[OffY]]) - np.array([points[CenterX],points[CenterY]])
        PinAdj = 90;
        print("OffCenter Pin is Below the Center Pin   (up)  +90 ")
        
    # MAKING 'PIN' ANGLE ####### #######    
    angle_Pin = np.degrees(np.arctan2(Pin[1],Pin[0])) + PinAdj;
    print(f"Angle Pin = ArcTan [ {Pin[1]:.3f} / {Pin[0]:.3f}] = {angle_Pin:.3f} deg")
    if PinAdj != 0:
        print(f"Angle Pin {angle_Pin:.3f} deg Adjusted by {PinAdj:.3f} deg")
        
    dynamic_var = ''
    new_points = {f'{dynamic_var}{key.split("_")[1]}': value for key, value in points.items() if 'FD' in key}
    #print("new_points:", new_points)
    keys = ['FD1', 'FD2', 'FD3', 'FD4']
    if all(f'pos1_{key}' in points for key in keys):
        print("FD1:", new_points['FD1'], "FD2:", new_points['FD2'], "FD3:", new_points['FD3'], "FD4:", new_points['FD4'])
    else:
        print("One or more keys are missing.")

    print("Big CheckPoint 2!!")    

    #FD Center Calculation (AVG of Select Points)    (translations come later***)
    if Shape == "HD Full": 
        FDC_x = (new_points['FD1'][0] + new_points['FD2'][0] + new_points['FD3'][0] + new_points['FD4'][0]) / 4
        FDC_y = (new_points['FD1'][1] + new_points['FD2'][1] + new_points['FD3'][1] + new_points['FD4'][1]) / 4
        ### Center of board, and center of pin
    elif Shape == "LD Right":
        FDC_x = (new_points['FD1'][0] + new_points['FD3'][0] ) / 2
        FDC_y = (new_points['FD1'][1] + new_points['FD3'][1] ) / 2
        ### Slightly offcenter from pin (different for PM and M)
    elif Shape == "LD Five":
        FDC_x = (new_points['FD1'][0] + new_points['FD3'][0] + new_points['FD4'][0]) / 3
        FDC_y = (new_points['FD1'][1] + new_points['FD3'][1] + new_points['FD4'][1]) / 3
        # Center of the Board and Center Pin
    else:
        print("Error or Not Programmed yet!!")
    FDCenter = [FDC_x, FDC_y]
     
    # Vector 1&2 (vector of select Fiducials) (going UP** 1 is on left) (2 is also up but secondary *if applicable*)
    V2_Adj = 0
    if Shape == "HD Full":
        if Position == 1: 
            Vector_1 = np.array(new_points['FD2']) - np.array(new_points['FD1']) #up left
            Vector_2 = np.array(new_points['FD3']) - np.array(new_points['FD4']) #up right
        if Position == 2:
            Vector_1 = np.array(new_points['FD4']) - np.array(new_points['FD3']) #up left
            Vector_2 = np.array(new_points['FD1']) - np.array(new_points['FD2']) # up right
    elif Shape == "LD Right":
        if Position == 1: 
            Vector_1 = np.array(new_points['FD2']) - np.array(new_points['FD4']) # up middle
            Vector_2 = np.array(new_points['FD1']) - np.array(new_points['FD3']) # left translated
            V2_Adj = -90
        if Position == 2:
            Vector_1 = np.array(new_points['FD4']) - np.array(new_points['FD2']) #up middle
            Vector_2 = np.array(new_points['FD3']) - np.array(new_points['FD1']) # left translated
            V2_Adj = -90
    elif Shape == "LD Five":
        if Position == 1: 
            Vector_1 = np.array(new_points['FD4']) - np.array(new_points['FD2']) # up middle
            Vector_2 = np.array(new_points['FD1']) - np.array(new_points['FD3']) # left translated
            V2_Adj = -90
        if Position == 2:
            Vector_1 = np.array(new_points['FD2']) - np.array(new_points['FD4']) #up middle
            Vector_2 = np.array(new_points['FD3']) - np.array(new_points['FD1']) # left translated
            V2_Adj = -90
    else:
        print("Error or Not Programmed yet!!")
    
    # MAKING 'Vector 1' ANGLE ####### #######    
    angle_Vector_1 = np.degrees(np.arctan2(Vector_1[1],Vector_1[0]));
    print(f"Angle Vector 1 = ArcTan [ {Vector_1[1]:.3f} / {Vector_1[0]:.3f}] = {angle_Vector_1:.3f} deg")

    # MAKING 'Vector 2' ANGLE ####### #######    
    angle_Vector_2 = np.degrees(np.arctan2(Vector_2[1],Vector_2[0]));
    print(f"Angle Vector 2 = ArcTan [ {Vector_2[1]:.3f} / {Vector_2[0]:.3f}] = {angle_Vector_2:.3f} deg")   
    if V2_Adj != 0:
        print(f"Angle Vector 2 {angle_Vector_2:.3f} deg Adjusted by {V2_Adj:.3f} deg")    
        #Calculated Angle Offset (Difference Between Pin and FD1 angle)
    

    #Angle Calculation         IS THIS ALLWAYS TRUE?  IDK - need more time

    #Which is with respec to the Assembly tray (not rotated with respect to ch1)
    AngleOffset = angle_Vector_1 - angle_Pin
    print(f"Assembly Survey Rotational Offset is {AngleOffset:.5f} degrees")
    print(f"{AngleOffset:.5f} = {angle_Vector_1:.5f} - {angle_Pin:.5f} degrees")
         

    #TRANSLATIONS / OFFSETS, NEEDED FOR ALL PARTIALS EXCEPT LD FIVE:
    X_Adj = 0
    Y_Adj = 0
    print()
    print(f"shape: {Shape}")
    print()
    if Shape == "LD Right":
        if comp_type == 'modules':
            if Position == 1:
                Y_Adj = -38.06
            if Position == 2:
                Y_Adj = 38.06
        elif comp_type == 'protomodules':
            if Position == 1:
                Y_Adj = -18
            if Position == 2:
                Y_Adj = 18
        else: print("invalid comp_type: location: in angle() ")
    else:
        X_Adj = 0
        Y_Adj = 0
    

    #Offset Calculation:     FDC and Pin Ceneter Will get new definitions, dependent on shape
    
    XOffset = float(FDC_x) - float(points[CenterX]) + float(X_Adj)
    YOffset = float(FDC_y) - float(points[CenterY]) + float(Y_Adj)
    print(f"{XOffset:.5f} = {FDC_x:.5f} - {points[CenterX]:.5f} + {X_Adj:.5f} mm")
    print(f"{YOffset:.5f} = {FDC_y:.5f} - {points[CenterY]:.5f} + {Y_Adj:.5f} mm")
    
    #Offset ROTATION: FROM relative to ASSEMBLY TRAY TO relative to CH1/HB   
    if Position == 1:
        NEWY = XOffset*-1;
        NEWX = YOffset; 
    elif Position == 2:
        NEWY = XOffset;
        NEWX = YOffset*1; 
    
    #print(f"Assembly Survey X Offset: {XOffset:.3f} mm w.r.t. Assembly Tray")
    #print(f"Assembly Survey Y Offset: {YOffset:.3f} mm w.r.t. Assembly Tray")
    print()
    print(f"Reported: Assembly Survey X Offset: {NEWX:.3f} mm w.r.t CH1")
    print(f"Reported: Assembly Survey Y Offset: {NEWY:.3f} mm w.r.t CH1")
    print()

    if plot == 1:
        plotFD(FDpoints, FDCenter, Center, Off, points, fd,)
    CenterOffset = np.sqrt(XOffset**2 + YOffset**2)
    return CenterOffset, AngleOffset, NEWX, NEWY

def get_shape_from_name(modname):
    print("Name:" , modname) #print(modname[3], modname[10])
    if len(modname) == 13 and modname[6] == '-':
        Shape = modname[2]; #print('ucsb Convention')
        Density = modname[1]; #print('ucsb Convention')
    elif len(modname) == 12:
        Shape = modname[2]; #print('ucsb Convention w/o dash- ')
        Density = modname[1];
    elif len(modname) == 16 and modname[3] == '-':
         Shape = modname[6]; #print('ucsb Convention w/o 2nd dash w/ 320 ')
         Density = modname[5];
    elif len(modname) == 16 and modname[9] == '-':     
        Shape = modname[5]; #print('ucsb Convention  w/o 1st dash w/ 320')
        Density = modname[4];
    elif len(modname) == 17 and modname[3] == '-' and modname[10] == '-':
        Shape = modname[6]; #print('ucsb Convention  w/ 320 and two dashes')
        Density = modname[5];
    elif len(modname) == 15:
        Shape = modname[5]; #print('ucsb Convention  w/ 320 and no dashes')
        Density = modname[4];
    else:
        #print('no accepted name')
        Shape = 'none';
        Density = 'none';
    #print(Shape)
    
    if Shape == 'F' and Density == 'H':
        ShapeID = 'HD Full';
    elif Shape == 'F' and Density == 'L':
        ShapeID = 'LD Full'
    elif Shape == '5' and Density == 'L':
        ShapeID = 'LD Five'
    elif Shape == 'R' and Density == 'L':
        ShapeID = 'LD Right'
    elif Shape == 'L' and Density == 'L':
        ShapeID = 'LD Left'
    elif Shape == 'T' and Density == 'L':
        ShapeID = 'LD Top'
    elif Shape == 'B' and Density == 'L':
        ShapeID = 'LD Bottom'
    elif Shape == 'R' and Density == 'H':
        ShapeID = 'HD Right'
    elif Shape == 'L' and Density == 'H':
        ShapeID = 'HD Left'
    elif Shape == 'T' and Density == 'H':
        ShapeID = 'HD Top'
    elif Shape == 'B' and Density == 'H':
        ShapeID = 'HD Bottom'
    else:
        ShapeID = 'Unkown Shape'
        print('invalid density or shape')
    #print(ShapeID)
    return ShapeID

def Pos_One_Or_Two(fd, points):
    if len(fd) == 4:
        FDCenter = (points[fd[0]]+points[fd[1]]+points[fd[2]]+points[fd[3]])/4;
    elif len(fd) == 2: 
        FDCenter = (points[fd[0]]+points[fd[1]])/2;
    
    if FDCenter[1] > 210:
        Position = 1;
    else:
        Position = 2;
    return Position;

def Get_The_Pins(Shape, Position):
    print("running get the pins: ", Position, Shape)
    if Shape == 'HD Full' or Shape == 'LD Full':
        if Position == 1:
            OffKey = 'P1E';
            CenKey = 'P1C';
        if Position == 2:
            OffKey = 'P2G'
            CenKey = 'P2C';
    elif Shape == 'LD Right':
        if Position == 1:
            OffKey = 'P1F';
            CenKey = 'P1A';
        if Position == 2:
            OffKey = 'P2H';
            CenKey = 'P2C';
    
    return OffKey, CenKey;
        
    
def get_offsets(filenames, Traysheets, Shape, comp_type, TrayNum):
    print("Code Works Up to Here... (here is:) get_offsets(); in ogp_height_plotter")
    #Just added Shape to inputs, needs to be accounted for. Oct 30 -Paolo
        ##FIRST; Get the points and use thier Locations to determine P1 or P2:
    
    #print("FIXING GET OFFSETS;", CurrentTrayFile, filenames)
    sheetnames = loadsheet(filenames);    fd=[]; points = {};

    #print("this is sheetnames inside get_offsets", sheetnames)

    #print("running get the pins: ",  Shape)

    sensorKeys = ["FD"] #needs to adapt/be tested for other shapes
    fd, points = searchSensorFD(sheetnames[1], sensorKeys, details = 0, fd=fd,points = points)

    Position = Pos_One_Or_Two(fd, points);
    
        ##Second: Find Tray Pin Keys with Knowladge of Position and File/Tray Name 

    print("This is Tray Sheets:", Traysheets, "and traynum: ", TrayNum)
    
    Off, Center = Get_The_Pins(Shape, Position); keys = [Center, Off];
    
        ##Third Use Tray Keys to Determine Pin locations
    
    TrayKeys = ["Tray","T",'P1','P2']
    searchTrayPin( Traysheets[(int(TrayNum)-1)],keys,details=0,Tray = 0, points = points)
        
        ##Fourth: Use Pin locations, Position, Shape, and FD points to Calculate Offsets
    
    #print(points); """for sheetname in sheetnames: TrayNum = TrayID(sheetname); PosNum = PositionID(sheetname);""" #print(fd);
    print(points)
    CenterOff, AngleOff, XOffset, YOffset = angle(points, FDpoints=len(fd), OffCenterPin=Off, details=0,plot=1, Center = Center, Off = Off, fd = fd, Position = Position, Shape = Shape, comp_type = comp_type)
    return XOffset, YOffset, AngleOff




import re
import colorama
from colorama import Fore, Style

colorClassify = {'-1': Fore.MAGENTA + 'NO INFO' + Fore.BLACK, 
                       '0': Fore.GREEN + 'GREEN' + Fore.BLACK,
                       '1': Fore.YELLOW + 'YELLOW' + Fore.BLACK, 
                       '2': Fore.RED + 'RED' + Fore.BLACK}
classify = {'-1': 'NO INFO',
                         '0': 'GREEN',
                         '1': 'YELLOW',
                         '2': 'RED'}
degrees = [0.03, 0.06, 90]
centers = [0.050, 0.100, 10.0]

def quality(Center, Rotation, position = "P1", details =0, note = 0):
    '''
    QC designation for different measurements
    Measurement      |         GREEN          |        YELLOW         |          RED          |
    _________________|________________________|_______________________|_______________________|
    Angle of Plac.   |0 < abs(x - 90.) <= 0.03 |0.03 < abs(x - 90.) <= .06| 0.06 < abs(x - 90.)<90| 
    Placement        |      0 < x <= 0.05     |    0.05 < x <= 0.1    |      0.1 < x <= 10.   | 
    Height           |0 < abs(x - Nom) <= 0.05|0.05 <abs(x - Nom)<=0.1|0.1 < abs(x - Nom)<=10.| 
    Max Hght from Nom|      0 < x <= 0.05     |    0.05 < x <= 0.1    |    0.1 < x <= 10.     | 
    Min Hght ffrom Nom|      0 < x <= 0.05     |    0.05 < x <= 0.1    |    0.1 < x <= 10.     | 
    
    '''
    if details == 1:
        print(f"The Center Offset is {Center:.3f} mm")
        print(f"The Rotational Offset is {Rotation:.5f} degrees ")
        print()
        
    for i, p in enumerate(centers):
        if Center < p:
            print(f"The placement in position {position} is {colorClassify[str(i)]}")
            break
        elif Center > centers[-1]:
            print(f"The placement in position {position} is more than {centers[-1]} mm")
            break
            
    for j, d in enumerate(degrees):
        if abs(Rotation) < d:
            print(f"The angle in position {position} is {colorClassify[str(j)]}")
            break
        elif abs(Rotation) > degrees[-1]:
            print(f"The angle in position {position} is more than {degrees[-1]} degree")
            break
    return colorClassify[str(i)], colorClassify[str(j)]
    # if note == 1:
    #     print()
    #     help(QualityControl)


#####Testing#########
#get_shape_from_name('MHR1CXSB0001')
#get_shape_from_name('MLL1CX-SB0001')
##get_shape_from_name('320MHT1CX-SB0001')
#get_shape_from_name('320-MLR1CX-SB0001')
#get_shape_from_name('320-MHL1CXSB0001')
#get_shape_from_name('320MLT1CXSB0001')
#searchTrayID("MLR3TX-SB0005")