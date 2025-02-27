import numpy as np
import pandas as pd
import os
import yaml
import matplotlib.pyplot as plt
import matplotlib.colors as cls
from src.parse_data import DataParser
from src.param import one_tray_param
import warnings

pjoin = os.path.join

class PlotTool:
    def __init__(self, meta, features: 'pd.DataFrame', tray_dir, save_dir=None):
        """
        Parameters
        - `meta`: metadata of the features, including Tray ID, Operator, and Component ID
        - `features`: dataframe of features to plot
        - `save_dir`: directory to save the plots to"""
        self.save_dir = save_dir
        self.meta = meta
        self.tray_dir = tray_dir
        self.features = DataParser.get_xyz(features)
        self.x_points = self.features['X_coordinate']
        self.y_points = self.features['Y_coordinate']
        self.z_points = self.features['Z_coordinate']
    
    def __call__(self, **args):
        """Plot the 2D height map of the given data."""
        centerxy = self.get_center()
        im_bytes = self.plot2d(self.x_points, self.y_points, self.z_points, centerxy, **args)
        return im_bytes
    
    def get_center(self) -> int:
        """Get the index of the fiducial center in the dataframe by taking the average of the x and y coordinates."""
        center_x = (max(self.x_points) + min(self.x_points)) / 2
        center_y = (max(self.y_points) + min(self.y_points)) / 2
        print(f"Center of the sensor is at ({center_x:.3f}, {center_y:.3f}) mm")
        return (center_x, center_y)

    @staticmethod
    def plot2d(x, y, zheight, centerxy, vmini, vmaxi, new_angle, title, savename, mod_flat, show_plot, value = 1, rotate=0):
        """Plot 2D height map of the given data.
        Parameters
        - `x`: x-coordinates
        - `y`: y-coordinates
        - `zheight`: height values
        - `centerxy`: tuple of the center coordinates (x,y)
        - `vmini`: minimum height value
        - `vmaxi`: maximum height value
        - `rotate`: index of the fiducial to rotate the plot around
        - `new_angle`: angle to rotate the plot to
        - `title`: title of the plot
        - `show_plot`: whether to show the plot. Imcompatible with saving the plot.
        - `value`: 1 for plotting height values, 0 for plotting deviation from mean"""
        mean_h = np.mean(zheight)
        std_h = np.std(zheight)
        max_h = max(zheight)
        min_h = min(zheight)
        print(f"Average Height is {mean_h:.3f} mm")
        print(f"Maximum Height is {max_h:.3f} mm")
        print(f"Minimum Height is {min_h:.3f} mm")
        print(f"Height --> {mean_h:.3f} + ({max_h - mean_h:.3f}) - ({mean_h - min_h:.3f}) mm. \n")
        
        center_x, center_y = centerxy

        x = x- center_x
        y = y- center_y

        assert rotate >= 0 and rotate < len(x), "The specified index for rotation has to be within the range of the data."
        if rotate != 0:
            rotate_angle = vec_angle(x[rotate-1], y[rotate-1]) if rotate != 0 else 0
            for i in range(len(x)):
                x[i], y[i] = vec_rotate(x[i],y[i],rotate_angle, new_angle)

        fig=plt.figure(dpi=150, figsize=(9,5))
        axs=fig.add_subplot(111); axs.set_aspect('equal')
        
        axs.hexbin(x,y,zheight,gridsize=20, vmin = vmini, vmax = vmaxi, cmap=plt.cm.coolwarm)
        norm = cls.Normalize(vmin=vmini, vmax=vmaxi)
        sm = plt.cm.ScalarMappable(norm=norm, cmap=plt.cm.coolwarm)
        cb=plt.colorbar(sm, ax= axs); cb.minorticks_on()
        # else:
        #     if title == '815 PCB fiducials':
        #         thickness = np.array([10,11,12,13,14,15,16,17,18,1,2,3,4,5,6,7,8,9,19,20,21,22,23,24,25])
        #         axs.annotate(f"{thickness[i]}",(x[i],y[i]),color="black")
        # #axs.annotate(f"{i+1}",(temp[0][i],temp[1][i]),color="black")
        #     else:
        #         axs.annotate(f"{i+1}",(x[i],y[i]),color="black")

        axs.set_xlabel("x (mm)")
        axs.set_ylabel("y (mm)")
        axs.minorticks_on()
        axs.set_xlim(left=-100, right=100)
        axs.set_ylim(bottom=-100, top=100)
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

        if show_plot:
            print("Not saving the plot or the image bytes as show_plot is set to True.")
            plt.show(); 
            plt.close()
        
        from io import BytesIO  
        buffer = BytesIO()
        plt.savefig(savename, bbox_inches='tight')
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        return buffer.read()

    def get_offsets(self):
        """Get the offsets of the sensor from the tray fiducials.
        
        Return 
        - `XOffset`: x-offset of the sensor from the tray center
        - `YOffset`: y-offset of the sensor from the tray center
        - `AngleOff`: angle of the sensor from the tray fiducials"""

        #Position 
        if not self.meta.get('PositionID'): 
            warnings.warn("PositionID not found in metadata. Default to Position ID 1.")
            PositionID = 1
        else:
            PositionID = int(self.meta['PositionID'])

        #Geometry
        if not self.meta.get('Geometry'): 
            warnings.warn("Geometry not found in metadata. Default Geometry is Full.")
            Geometry = 'Full'
        else:
            Geometry = int(self.meta['Geometry'])

        #Density
        if not self.meta.get('Density'): 
            warnings.warn("Density not found in metadata. Default shape is LD.")
            density = 'LD'
        else:
            density = int(self.meta['Density'])

        #TrayNo
        if not self.meta.get('TrayNo'):
            warnings.warn("TrayNo not found in metadata. Default to Tray 1.")
            TrayNo = 1
        else:
            TrayNo = int(self.meta['TrayNo'])

        TrayFile = pjoin(self.tray_dir, f"Tray{TrayNo}.yaml") 
        with open(TrayFile, 'r') as f:
            trayinfo = yaml.safe_load(f)
        
        """
        if PositionID == 1:
            pos = 'left'
        else: pos = 'right'
        """
        #CURRENTLY SWAPPING THIS ^^^ WITH THIS VVV
        HolePin = ''; SlotPin = '';
        if Geometry == 'Full':
            if density == 'LD':
                if PositionID == 1:
                    HolePin = 'p1_center_pin'; SlotPin = 'p1O';  #not a zero
                elif PositionID == 2:
                    HolePin = 'p2_center_pin'; SlotPin = 'p2M';
            elif density == 'HD':
                if PositionID == 1:
                    HolePin = 'p1_center_pin'; SlotPin = 'p1O';  #not a zero
                elif PositionID == 2:
                    HolePin = 'p2_center_pin'; SlotPin = 'p2M';
        elif Geometry == 'Left':
            if density == 'LD':
                if PositionID == 1:
                    HolePin = 'p1C'; SlotPin = 'p1L';
                elif PositionID == 2:
                    HolePin = 'p2A'; SlotPin = 'p2K';
            elif density == 'HD':
                if PositionID == 1:
                    HolePin = 'p1F'; SlotPin = 'p1P';
                elif PositionID == 2:
                    HolePin = 'p2H'; SlotPin = 'p2N';
        elif Geometry == 'Right':
            if density == 'LD':
                if PositionID == 1:
                    HolePin = 'p1A'; SlotPin = 'p1K';
                elif PositionID == 2:
                    HolePin = 'p2C'; SlotPin = 'p2I';
            elif density == 'HD':
                if PositionID == 1:
                    HolePin = 'p1H'; SlotPin = 'p1N';
                elif PositionID == 2:
                    HolePin = 'p2F'; SlotPin = 'p2P';
        elif Geometry == 'Top':
            if density == 'LD':
                if PositionID == 1:
                    HolePin = 'p1D'; SlotPin = 'p1O';
                elif PositionID == 2:
                    HolePin = 'p2B'; SlotPin = 'p2M';
            elif density == 'HD':
                if PositionID == 1:
                    HolePin = 'p1E'; SlotPin = 'p1O';
                elif PositionID == 2:
                    HolePin = 'p2G'; SlotPin = 'p2M';
        elif Geometry == 'Bottom':
            if density == 'LD':
                if PositionID == 1:
                    HolePin = 'p1B'; SlotPin = 'p1M';
                elif PositionID == 2:
                    HolePin = 'p2D'; SlotPin = 'p2O';
            elif density == 'HD':
                if PositionID == 1:
                    HolePin = 'p1_center_pin'; SlotPin = 'p1M';
                elif PositionID == 2:
                    HolePin = 'p2_center_pin'; SlotPin = 'p2O';
        elif Geometry == 'Five':
                if PositionID == 1:
                    HolePin = 'p1_center_pin'; SlotPin = 'p1I';
                elif PositionID == 2:
                    HolePin = 'p2_center_pin'; SlotPin = 'p2K';
        else: print('ogpheightplotter:plottool:angle: Geometry Not recognized')

        HolePin_xy = tuple(trayinfo[f'{HolePin}_xy'])  
        SlotPin_xy = tuple(trayinfo[f'{SlotPin}_xy'])
        
        FD_points = self.features[self.features['FeatureName'].str.contains('FD')]
        FD_points = FD_points[['X_coordinate', 'Y_coordinate']].values

        plotFD(FD_points, HolePin_xy, HolePin_xy, SlotPin_xy, True, pjoin(self.save_dir, f"{self.meta['ComponentID']}_FDpoints.png"))        
    
        CenterOff, AngleOff, XOffset, YOffset = angle(HolePin_xy, SlotPin_xy, FD_points, Geometry, density, PositionID)    
        print(f"Assembly Survey X Offset: {XOffset:.3f} mm")
        print(f"Assembly Survey Y Offset: {YOffset:.3f} mm")
        print(f"Assembly Survey Rotational Offset is {AngleOff:.5f} degrees")
        print(f"Assembly Survey Center Offset is {CenterOff:.3f} mm")

        return XOffset, YOffset, AngleOff

def vec_angle(x,y):
    angle_arctan = np.degrees(np.arctan2(y,x))
    return angle_arctan

def vec_rotate(old_x, old_y, old_angle, new_angle = 120):
    """Rotate a vector by a given angle.

    Parameters
    - `old_x`: x-coordinate of the vector
    - `old_y`: y-coordinate of the vector
    - `old_angle`: angle of the vector
    - `new_angle`: angle to rotate the vector to"""
    rad = np.radians(new_angle - old_angle)
    new_x = old_x*np.cos(rad)-old_y*np.sin(rad)
    new_y = old_x*np.sin(rad)+old_y*np.cos(rad)
    return new_x, new_y
    
def plotFD(FDpoints:np.array, FDCenter:tuple, CenterXY:tuple, OffXY:tuple, save=False, save_name='') -> None:
    """Plot the fiducial points and the center of the sensor.
    
    Parameters
    - `FDpoints`: array of fiducial points
    - `FDCenter`: center of the fiducial points
    - `CenterXY`: center of the sensor
    - `OffXY`: offset of the sensor
    - `save`: whether to save the plot. Incompatible with showing the plot.
    - `save_name`: name to save the plot as"""
    CenterX, CenterY = CenterXY
    OffX, OffY = OffXY
    x_values = np.append(FDpoints[:,0], [CenterX, OffX])
    y_values = np.append(FDpoints[:,1], [CenterY, OffY])
    names = [f'FD{no}' for no in range(1, len(FDpoints)+1)]
    names.extend(['Center', 'Offcenter'])

    plt.figure(dpi=250)
    plt.plot(x_values,y_values,'o',ms=2)
    plt.arrow(OffX, OffY, CenterX-OffX, CenterY-OffY, lw=0.5, color='g')
    plt.plot(FDCenter[0], FDCenter[1], 'ro', label='FDCenter', ms=2)
    for i in range(len(x_values)):
        plt.annotate(names[i], (x_values[i], y_values[i]))
    
    plt.legend()
    plt.xlim(60,160)
    plt.xlabel("x [mm]")
    plt.ylabel("y [mm]")

    plt.title("Fiducial Points")
    if save:
        plt.savefig(save_name)
        

#! Messy part: serve as reference for future development
    # if FDpoints == 2:
    #     plt.arrow(Xp[2],Yp[2],Xp[3]-Xp[2],Yp[3]-Yp[2],lw=0.5,color='orange')

    # if FDpoints == 4:
    #     plt.arrow(Xp[2],Yp[2],Xp[4]-Xp[2],Yp[4]-Yp[2],lw=0.5,color='orange')
    #     plt.arrow(Xp[3],Yp[3],Xp[5]-Xp[3],Yp[5]-Yp[3],lw=0.5,color='orange')
    #     plt.plot(FDCenter[0],FDCenter[1],'ro',label='FDCenter',ms=2)
    #     names = ['P1CenterPin','P1OffcenterPin','FD1','FD2','FD3','FD4']

def angle(holeXY:tuple, slotXY:tuple, FDPoints:np.array, shape, density, position):
    """Calculate the angle and offset of the sensor from the tray fiducials.
    
    Parameters
    - `holeXY`: the location of the pin that corresponds to the HOLE in the base plate. previously called: "the center pin"
    - `slotXY`: the location of the pin that corresponds to the SLOT in the base plate. previously called: "the offcenter pin"
    - `FDPoints`: array of fiducial points: 2, 4, 6, or 8, FD points are accepted
    - `shape`: the shape of the module eg, Full/Five/Left/Right
    - `desnity`: the desity of the module, HD or LD
    - `position`: the position its assembled in, P1 or P2

    Return
    - `CenterOffset`: offset of the sensor from the tray center
    - `AngleOffset`: angle of the sensor from the tray fiducials
    - `XOffset`: x-offset of the sensor from the tray center
    - `YOffset`: y-offset of the sensor from the tray center"""
    
    #rename:
        #changing name "center" to "hole" refering to the hole on the baseplate
        #changing name "offcenter" to "slot" refering to the slot on the baseplate

    holeX, holeY = holeXY
    slotX, slotY = slotXY

    pinX = slotX - holeX     #X component of a vector pointing from hole to slot
    pinY = slotY - holeY     #Y component "" ""

    Hole = np.array([holeX, holeY])

    assert len(FDPoints) == 2 or len(FDPoints) == 4 or len(FDPoints) == 6 or len(FDPoints) == 8, "The number of fiducial points must be 2,4,6 or 8."

    if shape == 'Full' or shape == 'Bottom' or shape == 'Top':
        angle_Pin= np.degrees(np.arctan2(pinY, pinX))
    elif shape == 'Left' or shape == 'Right' or shape == 'Five':
        angle_Pin= (np.degrees(np.arctan2(pinX, pinY)) * -1)
    else: print('ogpheightplotter: angle: shape not recognized')
    
    if density == 'HD':   
        if shape == 'Full':
            FDCenter = np.mean(FDPoints, axis=0) #Average of ALl FDs
        else:
            FDCenter = np.mean(FDPoints[0,2], axis=0)  #Average of FD1 and FD3, this applies to modules except HD Full
    if density == 'LD':
        if shape == 'Full':
            FDCenter = np.mean(FDPoints, axis=0) #Average of ALl FDs
        else:
            FDCenter = np.mean(FDPoints[0,2], axis=0)  #Average of FD1 and FD3, this applies to all modules except LD Full

     #   FDPoints[0] must be "FD1" and FDPoints[2] must be "FD3" , or else this system will not work.
     #  It is up to the parsing system and the file output to assign the fiducials correctly  -PJ 1/9/25

     #adjustmentX and adjustmentY is appropriate for all modules except Fulls, and the Five

    if shape == 'Full' or shape == 'Five':
        adjustmentX = 0; adjustmentY = 0;
    # Waiting on Adjustment INFO, This needs to be filled out after measurements !!!!WORK IN PROGRESS!!!
    
    XOffset = FDCenter[0]-Hole[0]-adjustmentX
    YOffset = FDCenter[1]-Hole[1]-adjustmentY

    print(f"Assembly Survey X Offset: {XOffset:.3f} mm. \n")
    print(f"Assembly Survey Y Offset: {YOffset:.3f} mm. \n")

    CenterOffset = np.sqrt(XOffset**2 + YOffset**2)

    FD3to1 = FDPoints[0] - FDPoints[2]  #Vector from FD3 to FD1
    

    if shape == 'Bottom' or shape == 'Top':       #if shape is Top or bottom, FD3to1 will point either left or right
        angle_FD3to1 = np.degrees(np.arctan2(FD3to1[1],FD3to1[0]))
    elif shape == 'Left' or shape == 'Right' or shape == 'Five':     #if shape is Five, Right or Left, FD3to1 will point either up or down
        angle_FD3to1 = (np.degrees(np.arctan2(FD3to1[0],FD3to1[1])) * -1);
    elif shape == 'Full' & density == 'HD':
        # in this case angle_FD3to1 is actually the angle of the line that goes from 1 to 2, this points up and down wrt tray
        FD3to1 = FDPoints[1] - FDPoints[0]
        angle_FD3to1 = (np.degrees(np.arctan2(FD3to1[0],FD3to1[1])) * -1);
    elif shape == 'Full' & density == 'LD':
        # in this case angle_FD3to1 is actually the angle of the line that goes from 6 to 3, this points up and down wrt tray
        FD3to1 = FDPoints[2] - FDPoints[5]
        angle_FD3to1 = (np.degrees(np.arctan2(FD3to1[0],FD3to1[1])) * -1);
    else: print('ogpheightplotter: angle: shape not recognized')

    print(f"FD1-2 X'' axis is at angle {angle_FD3to1:.5f} degrees. \n")
    print(f"FDCenter at x:{FDCenter[0]:.3f} mm, y:{FDCenter[1]:.3f} mm")
    print(f"Pin&Hole at x:{holeX[0]:.3f} mm, y:{HoleY[1]:.3f} mm")

    AngleOffset = angle_FD3to1 - angle_Pin

    return CenterOffset, AngleOffset, XOffset, YOffset

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
