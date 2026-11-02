# Script to convert all data to npy format(after gridding them uniformly). The files should be kept in a 
# particular folder and filenames must be in a defined order
#
# Folder name: Any folder name inside data directory[name must be mentioned in variable folders in the class(variables)]
# file name inside folders: ${depth}_${FolderName}_dat
# Input data format : Lon(x-axis), Lat(y-axis), Depth(z-axis)
# Output data format : meshgrid saved in npy file format
# Output data variables : X(X Meshgrid), Y(Y meshgrid),depths(depths list),x_lon=xi_Lon,y_lat=yi_Lat, grid=data_3D

import numpy as np
import sys,os,tqdm
from scipy.interpolate import griddata
from scipy.interpolate import RegularGridInterpolator
import plotly.graph_objects as go

class variables:
    folders=['vs']
cn=variables()


def reFormatData(gridPoints,resolution_horizontal, resolution_vertical):
    # Loop through all folders and create the nyp files 
    for varname in cn.folders:
        largeArray=[]
        dirList=os.listdir("data/"+varname)
        depths=[]
        for i in dirList:
            if(i.endswith('dat')):
                depths.append(int(i.split('_')[0]))
        depths=np.sort(depths)

        ## We need to make all grid of same resolution. Therefore they need to be re-gridded
        # Generating a grid for interpolation. 

        xi_Lon=np.arange(gridPoints[0],gridPoints[1],resolution_horizontal)
        yi_Lat=np.arange(gridPoints[2],gridPoints[3],resolution_horizontal)
        X, Y, Z=np.meshgrid(xi_Lon,yi_Lat,depths,indexing='xy')
        
        # Make a 3D grid
        grid_3D=np.full((len(xi_Lon), len(yi_Lat), len(depths)), np.nan)

        
        ## Need the whole grid on memory for this method to work
        allData=[]
        for i,depth in enumerate(tqdm.tqdm(depths,desc="Processing variable %s"%(varname))):
            fName="data/%s/%i_%s_dat"%(varname,depth,varname)
            tmp=np.loadtxt(fName)
            lon_x=tmp[:,0]
            lat_y=tmp[:,1]
            val_z=tmp[:,2]

            # grid these data on uniform grid values created
            uniformDepthGrids=griddata((lon_x,lat_y),val_z,(X[:,:, i], Y[:,:,i]), method='cubic',fill_value=np.nan)
        
            # print(depth)
            # ## Plotly
            # fig = go.Figure(data=go.Contour(
            #     z=uniformDepthGrids,
            #     x=xi_Lon,
            #     y=yi_Lat,
            #     colorscale='icefire_r',
            #     colorbar_title='Value',
            #     ncontours=30,
            #     zmin=-10,
            #     zmax=10,
            #     line_smoothing=0.5
            # ))

            # fig.update_layout(
            #     xaxis_title='X',
            #     yaxis_title='Y',
            #     width=500,
            #     height=500
            # )
            # fig.show()
            # sys.exit()


            # Insert this grid into the 3D volume
            grid_3D[:,:,i]=uniformDepthGrids
        
        # Now the vertical axis needs to be further refined for good re-sampling
        zi_fine=np.arange(np.min(depths),np.max(depths)+resolution_vertical,resolution_vertical)
        depthsInterpolator=RegularGridInterpolator((xi_Lon,yi_Lat,depths),grid_3D,method='cubic',fill_value=np.nan)

        X_fine, Y_fine, Z_fine = np.meshgrid(xi_Lon, yi_Lat, zi_fine, indexing='ij')
        fine_points = np.vstack([X_fine.ravel(), Y_fine.ravel(), Z_fine.ravel()]).T
        fine_grid_3D = depthsInterpolator(fine_points).reshape(len(xi_Lon), len(yi_Lat), len(zi_fine))

        np.savez_compressed("data/npyFiles/%s.npz"%(varname), x=xi_Lon, y=yi_Lat, z=zi_fine, values=fine_grid_3D)



def main():
    ## Input variables
    resolution_horizontal=0.05  # (in degrees)
    resolution_vertical=5 # in km
    gridPoints=[60,105,0,45]  # x-min/x-max/y-min/y-max # Lon_left/Lon_right/Lat_bottom/Lat_top
    reFormatData(gridPoints,resolution_horizontal, resolution_vertical)
    return
    


if __name__=="__main__":
    main()