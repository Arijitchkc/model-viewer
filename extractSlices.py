import numpy as np
from scipy.interpolate import RegularGridInterpolator
import time, sys
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def stLineCoordinates(vertical_startPoint, vertical_endPoint, resolution):
    slope=(vertical_endPoint[1]-vertical_startPoint[1])/(vertical_endPoint[0]-vertical_startPoint[0])    
    theta=np.arctan(slope)
    distInitial=np.sqrt((vertical_endPoint[0]-vertical_startPoint[0])**2 + (vertical_endPoint[1]-vertical_startPoint[1])**2)
    lineCoordinates=[]
    lineCoordinates.append(vertical_startPoint)

    while(True):
        newx=lineCoordinates[-1][0]+resolution*np.cos(theta)
        newy=lineCoordinates[-1][1]+resolution*np.sin(theta)
        distTmp=np.sqrt((newx-vertical_startPoint[0])**2 + (newy-vertical_startPoint[1])**2)
        if(distTmp>distInitial):
            break
        lineCoordinates.append([newx, newy])
    lineCoordinates.append(vertical_endPoint)

    return np.array(lineCoordinates)



def getInterpolatedData(horizontalSlice,variableName,horizontal_depth=50, vertical_startPoint=[75,20], vertical_endPoint=[100,40], vertical_depthRange=[10,150], resolution_horizontal=0.05, resolution_vertical=5):
    
    model=np.load("data/npyFiles/%s.npz"%(variableName))
    x_lon=model['x']
    y_lat=model['y']
    depths=model['z']
    grid=model['values']

    

    if(horizontalSlice):
        interpolator=RegularGridInterpolator((x_lon, y_lat,depths),grid)
        points=[[x,y,horizontal_depth] for x in x_lon for y in y_lat]
        interpolated_plane=interpolator(points).reshape(len(x_lon), len(y_lat))
        x_dat=x_lon
        y_dat=y_lat

        xlabel='Longitude'
        ylabel='Latitude'
            
    else:
        interpolator=RegularGridInterpolator((x_lon, y_lat,depths),grid)
        line=stLineCoordinates(vertical_startPoint, vertical_endPoint, resolution_horizontal)
        allPoints=[]
        reqdDepths=np.arange(vertical_depthRange[0],vertical_depthRange[1],resolution_vertical)

        for i,depth in enumerate(reqdDepths):
            if(i==0):
                allPoints=np.insert(line,2,depth,axis=1)
            else:
                tmp=np.insert(line,2,depth,axis=1)
                allPoints=np.concatenate((allPoints,tmp))

        print(allPoints)
        interpolated_plane=interpolator(allPoints,method='linear').reshape(len(reqdDepths),len(line))

        if(abs(vertical_startPoint[0]-vertical_endPoint[0])>abs(vertical_startPoint[1]-vertical_endPoint[1])):
            range_xaxis=line[:,0] #np.linspace(vertical_startPoint[0],vertical_endPoint[0],len(line))
            xlabel='Longitude'
        else:
            range_xaxis=line[:,1]  #np.linspace(vertical_startPoint[1],vertical_endPoint[1],len(line))
            xlabel='Latitude'
        
        x_dat=range_xaxis
        y_dat=reqdDepths

        print(f'{x_dat=}')
        print(f'{y_dat=}')
        ylabel='depth'

    ## Plotly
    fig = make_subplots(rows=1,cols=2,subplot_titles=('mapview','profile'))

    points=[[x,y,20] for x in x_lon for y in y_lat]
    interpolated_plane_tmp=interpolator(points).reshape(len(x_lon), len(y_lat))
    fig.add_trace(go.Contour(
        z=interpolated_plane_tmp,
        x=x_lon,
        y=y_lat,
        colorscale='icefire_r',
        colorbar_title='Value',
        ncontours=40,
        zmin=2.1,
        zmax=5.0,
        line_smoothing=0.5
    ),1,1)
    fig.add_trace(go.Scatter(x=line[:,0],y=line[:,1],mode='markers',marker=dict(size=6, color='black', symbol='circle', opacity=0.8)),1,1)
    # fig.update_layout(
    #     xaxis_title='Longitude',
    #     yaxis_title='Latitude',
    # )


    fig.add_trace(go.Contour(
        z=interpolated_plane,
        x=x_dat,
        y=y_dat,
        colorscale='icefire_r',
        colorbar_title='Value',
        ncontours=40,
        zmin=2.1,
        zmax=5.0,
        line_smoothing=0.5
    ),1,2)

    fig.update_layout(
        xaxis_title=xlabel,
        yaxis_title=ylabel
    )
    if(ylabel=='depth'):
        fig.update_yaxes(autorange="reversed",row=1,col=2)
    fig.show()



def readFile(variableName):
    model=np.load("data/npyFiles/%s.npy"%(variableName))
    info=np.load("data/npyFiles/%s_info.npy"%(variableName))
    return model, info

def main():
    start_time = time.time()
    horizontalSlice=False
    variableName='vs'

    if(horizontalSlice==True):
        horizontal_depth=20
        resolution_horizontal=0.05 # degrees
        resolution_vertical=5 # km
        getInterpolatedData(horizontalSlice, variableName, horizontal_depth, [0,0], [0,0], [0,0], resolution_horizontal, resolution_vertical)
    else:
        # 09.00 78.00 27.00 74.00 250
        vertical_startPoint=[74.00,27.00] # Follow (x,y)<-->(Lon,Lat) format
        vertical_endPoint=[78.00,09.00] # Follow (x,y)<-->(Lon,Lat) format
        vertical_depthRange=[0,190] # (shallow, deep)
        resolution_horizontal=0.05 # degrees
        resolution_vertical= 5 # km
        getInterpolatedData(horizontalSlice, variableName, 0, vertical_startPoint, vertical_endPoint, vertical_depthRange, resolution_horizontal, resolution_vertical)
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__=="__main__":
    main()
