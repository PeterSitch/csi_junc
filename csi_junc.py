import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import matplotlib.patches as patches
from scipy import ndimage
from io import BytesIO


st.set_page_config(page_title="CSI Junc", layout="wide")

st.title("CSI Junc")


def rota3(img,ang,x1_ext,y1_ext):

    padX = [img.shape[1] - sum(x1_ext)//2, sum(x1_ext)//2]
    padY = [img.shape[0] - sum(y1_ext)//2, sum(y1_ext)//2]
    
    imgP = np.pad(img, [padY, padX], 'constant')
    
    #ndimage.rotate(canvas,ang,reshape=False)
    imgR = ndimage.rotate(imgP, ang, reshape=False)
    
    return imgR[padY[0] : -padY[1], padX[0] : -padX[1]]

@st.cache_data
def make_field (width,length,junc_length):
    canvas = make_canvas()
    y_size, x_size = np.shape(canvas)
    
    for x in range(x_size):
        for y in range (y_size):
            if x < x_size/2 + width/2 and x > x_size/2-width/2 and y <y_size/2+length/2 and y >y_size/2-length/2:
                junc_start = y_size/2 - length/2 + junc_length
                if y > junc_start:
                    canvas[y,x]=1
                else:
                    canvas[y,x]=1-(junc_start - y)/junc_length 
    return canvas


def make_canvas():
    return np.zeros((1000,1000))


@st.cache_data
def pos_field(img,f_x,f_y,f_angle,length,junc_length,x_ext,y_ext,iso):
    
    sign = 1
    
    if iso=="sup":
        img = np.rot90(img,2,)
        sign = -1
    
    img = np.roll(img,f_x,axis=1)
    img = np.roll(img,-f_y,axis=0)
    
    img = np.roll(rota3(img, -f_angle, x_ext, y_ext), sign*(length-junc_length)//2, axis=0)
    
    return img



def rotate_around_point_highperf(xy, radians, origin=(0, 0)):
    """Rotate a point around a given point.
    
    I call this the "high performance" version since we're caching some
    values that are needed >1 time. It's less readable than the previous
    function but it's faster.
    """
    x, y = xy
    offset_x, offset_y = origin
    adjusted_x = (x - offset_x)
    adjusted_y = (y - offset_y)
    cos_rad = math.cos(radians)
    sin_rad = math.sin(radians)
    qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
    qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y

    return qx, qy


width = 80
length = 400
ptv=10
blur_factor = 3


col1, col2, = st.columns([1.6,1])

plot_space = col1.empty()

with col2:
    st.text("")
    st.text("")
    st.text("")
    st.text("")
    st.text("")
    x_prof_space = st.empty()
    y_prof_space = st.empty()


with st.sidebar:
    with st.form("parameters"):

        st.markdown("### Junction")
        junc_length = st.slider("length (mm)",min_value = 0, max_value = length, value = 100, )
        
        #f2
        st.markdown("### Sup iso")
        show_f2 = st.checkbox("show",value=True, key= "show_f2")
        col1, col2, col3 = st.columns(3)
        f2_angle = col1.number_input("angle (deg)", min_value = -90.0, max_value = 90.0, value=0.0, key = "f2_angle")
        f2_x = col2.number_input("x_shift (mm)", min_value = -100, max_value = 100, value=0, key = "f2_x")
        f2_y = col3.number_input("y_shift (mm)", min_value = -100, max_value = 100, value=0, key = "f2_y")
        
        
        #f1
        st.text("")
        st.markdown("### Inf iso")
        show_f1 = st.checkbox("show",value=True,key = "show_f1")
        col1, col2, col3 = st.columns(3)
        f1_angle = col1.number_input("angle (deg)", min_value = -90.0, max_value = 90.0, value=0.0, key = "f1_angle")
        f1_x = col2.number_input("x_shift (mm)", min_value = -100, max_value = 100, value=0, key = "f1_x")
        f1_y = col3.number_input("y_shift (mm)", min_value = -100, max_value = 100, value=0, key = "f1_y")
        
        st.text("")
        st.markdown("### Plot parameters")
        col1, col2 = st.columns(2)
        dmin = col1.number_input("dose min", min_value=0.0, max_value = 2.0, value=0.9, key = "dmin")
        dmax = col2.number_input("dose dmax", min_value=0.0, max_value = 2.0, value=1.1, key = "dmax")
        
        show_prof = st.checkbox("show x/y profiles",value=True)
        
        
        #f2_angle = -2



        build_it = st.form_submit_button("make plot")
        
        if build_it:
                


        #junc_length = 50


            

            #f1_angle = 2
            #f2_angle = -2

            #f1_x=50
            #f2_x=50

            #f1_y=0
            #f2_y=0







            x1_ext=(500 - width//2 - f1_x, 500 + width//2 - f1_x)
            x2_ext=(500 - width//2 + f2_x, 500 + width//2 + f2_x)

            y1_ext=(500 - length//2 - f1_y, 500 + length//2 - f1_y)
            y2_ext=(500 - length//2 - f2_y, 500 + length//2 - f2_y)



            x_trim = int(max(0,
                    1000 - (
                    500 + width//2 + 40 + int(length*math.sin(math.pi*max(abs(x) for x in (f1_angle, f2_angle))/180)/2)
                        ) - max(abs(x) for x in (f1_x,f2_x)) ))
            y_trim = int(max(0,
                    1000 - (500 + length//2 + (length-junc_length)//2 + 40
                        ) - max(abs(x) for x in (f1_y,f2_y) )))



            inf_coords = (500-width/2+ptv-x_trim+f1_x, 500-width/2+ptv-x_trim+f1_x +width-2*ptv,
                (500-length//2)+(length-junc_length)//2 + ptv-y_trim-f1_y, (500-length//2)+(length-junc_length)//2 + ptv-y_trim-f1_y + length-2*ptv
                )

            sup_coords = (500-width/2+ptv-x_trim+f2_x, 500-width/2+ptv-x_trim+f2_x +width-2*ptv,
                (500-length//2)-(length-junc_length)//2 + ptv-y_trim-f2_y, (500-length//2)-(length-junc_length)//2 + ptv-y_trim-f2_y + length-2*ptv
                )

            inf_cent = ((inf_coords[1]+inf_coords[0])/2,(inf_coords[3]+inf_coords[2])/2)
            sup_cent = ((sup_coords[1]+sup_coords[0])/2,(sup_coords[3]+sup_coords[2])/2)
            
            
            inf_junc_point = rotate_around_point_highperf((inf_cent[0],inf_coords[2]),-f1_angle*math.pi/180,origin=inf_cent)

            sup_junc_point = rotate_around_point_highperf((sup_cent[0],sup_coords[3]),-f2_angle*math.pi/180,origin=sup_cent)

            prof_point = ((sup_junc_point[0]+inf_junc_point[0])/2,(sup_junc_point[1]+inf_junc_point[1])/2)
            
            x_prof_length = 100
            y_prof_length = min(max(150,junc_length*1.5),1.6*y_trim)
            

            canvas = make_field(width,length,junc_length)

            if show_f1:                
                f1 =  pos_field(np.copy(canvas),f1_x,f1_y,f1_angle,length,junc_length,x1_ext,y1_ext, iso = "inf")             
            else:
                f1 = make_canvas()
            
            
            #f2 = np.rot90(np.copy(canvas),2,)
            
            if show_f2:  
                f2 = pos_field(np.copy(canvas),f2_x+1,f2_y-1,f2_angle,length,junc_length,x2_ext,y2_ext, iso = "sup")
            else:
                f2 = make_canvas()
            
           # f1 = np.copy(canvas)
           # f1 = np.roll(f1,f1_x,axis=1)
           # f1 = np.roll(f1,-f1_y,axis=0)
           # f1 = np.roll(rota3(f1, -f1_angle, x1_ext, y1_ext), (length-junc_length)//2, axis=0)


#            f2 = np.copy(canvas)
#            f2 = np.rot90(f2,2,)
#            f2 = np.roll(f2,f2_x+1,axis=1)
#            f2 = np.roll(f2,-f2_y+1,axis=0)
 #           f2 = np.roll(rota3(f2, -f2_angle, x2_ext, y2_ext), - (length-junc_length)//2, axis=0)

            
            f1 = ndimage.gaussian_filter(f1,sigma=blur_factor)
            f2 = ndimage.gaussian_filter(f2,sigma=blur_factor)


            res = f1 + f2

            #plt.imshow(np.where(res<0.9, np.nan, res),vmax=1.05,vmin=0.8)
            #ax.imshow(np.where(res<0.8, np.nan, res)[150:850,400:600],vmax=1.10,vmin=0.8)

            

        

            plot_x = (np.shape(res)[1]-2*x_trim+200)*13/800 
            plot_y = (np.shape(res)[0]-2*y_trim)*13/800
            
            #st.write(plot_x,plot_y)

            f, ax = plt.subplots(1, 1, figsize = (int(plot_x), int(plot_y)))
            pl = ax.imshow(np.where(res<dmin, np.nan, res)[y_trim:-y_trim,x_trim:-x_trim],vmax=dmax,vmin=dmin, cmap='jet')


            rect1 = patches.Rectangle((500-width/2+ptv-x_trim+f1_x,
                                       (500-length//2)+(length-junc_length)//2 + ptv-y_trim-f1_y),
                                      width-2*ptv, length-2*ptv, angle=f1_angle,
                                      rotation_point = 'center', linewidth=1, edgecolor='r', facecolor='none')
            if show_f1:
                ax.add_patch(rect1)

            rect2 = patches.Rectangle((500-width/2+ptv-x_trim+f2_x,
                                       (500-length//2)-(length-junc_length)//2 + ptv-y_trim-f2_y),
                                      width-2*ptv, length-2*ptv, angle=f2_angle,
                                      rotation_point = 'center', linewidth=1, edgecolor='g', facecolor='none')

            # Add the patch to the Axes
            
            if show_f2:
                ax.add_patch(rect2)
                
            if show_prof:
                plt.plot([prof_point[0],prof_point[0]],[prof_point[1]-y_prof_length/2,prof_point[1]+y_prof_length/2],'k--')
                plt.plot([prof_point[0]-x_prof_length/2,prof_point[0]+x_prof_length/2],[prof_point[1],prof_point[1]],'k--')
                
                
            plt.colorbar(pl, ax=ax)

            buf = BytesIO()
            f.savefig(buf, format="png")
            plot_space.image(buf)


            if show_prof:
                f, ax = plt.subplots(1, 1, figsize = (int(plot_x/1.2), int(plot_y/3)))
                _res  = res[y_trim:-y_trim,x_trim:-x_trim]

                _f1 = f1[y_trim:-y_trim,x_trim:-x_trim]
                _f2 = f2[y_trim:-y_trim,x_trim:-x_trim]
                
                
                plt.plot(_f2[int(prof_point[1]-y_prof_length/2):int(prof_point[1]+y_prof_length/2),int(prof_point[0])],'g')
                plt.plot(_f1[int(prof_point[1]-y_prof_length/2):int(prof_point[1]+y_prof_length/2),int(prof_point[0])],'r')
                plt.plot(_res[int(prof_point[1]-y_prof_length/2):int(prof_point[1]+y_prof_length/2),int(prof_point[0])])
                
                plt.title("Y - Profile")
                
                
                #buf = BytesIO()
                f.savefig(buf, format="png")
                
                with y_prof_space.container():
                    st.text("")
                    #st.markdown("Y - Profile")
                    st.image(buf)#.pyplot(f)

                
                
                #y_prof_space.image(buf)#.pyplot(f)
                
                f, ax = plt.subplots(1, 1, figsize = (int(plot_x/1.2), int(plot_y/3)))
                
                plt.plot(_f2[int(prof_point[1]),int(prof_point[0]-x_prof_length/2):int(prof_point[0]+x_prof_length/2)],'g')
                plt.plot(_f1[int(prof_point[1]),int(prof_point[0]-x_prof_length/2):int(prof_point[0]+x_prof_length/2)],'r')
                plt.plot(_res[int(prof_point[1]),int(prof_point[0]-x_prof_length/2):int(prof_point[0]+x_prof_length/2)])
                
                plt.title("X - Profile")
                
                f.savefig(buf, format="png")
                
                with x_prof_space.container():
                    st.text("")
                    #st.markdown("X - Profile")
                    st.image(buf)#.pyplot(f)


            #plot_space.pyplot(fig=f)
            
            
#'Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r',
#'CMRmap', 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Greens', 'Greens_r', 'Greys', 'Greys_r',
#'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r',
#'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r',
#'PuRd', 'PuRd_r', 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu',
#'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r',
#'Spectral', 'Spectral_r', 'Wistia', 'Wistia_r', 'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r',
#'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r', 'autumn', 'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg',
#'brg_r', 'bwr', 'bwr_r', 'cividis', 'cividis_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r',
#'cubehelix', 'cubehelix_r', 'flag', 'flag_r', 'gist_earth',
#'gist_earth_r', 'gist_gray', 'gist_gray_r', 'gist_heat', 'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow',
#'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 'gist_yarg_r', 'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r',
#'gray', 'gray_r', 'hot', 'hot_r', 'hsv', 'hsv_r', 'inferno', 'inferno_r', 'jet', 'jet_r', 'magma', 'magma_r', 'nipy_spectral',
#'nipy_spectral_r', 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r', 'rainbow', 'rainbow_r',
#'seismic', 'seismic_r', 'spring', 'spring_r', 'summer', 'summer_r', 'tab10', 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r',
#'tab20c', 'tab20c_r', 'terrain', 'terrain_r', 'turbo', 'turbo_r', 'twilight', 'twilight_r', 'twilight_shifted', 'twilight_shifted_r',
#'viridis', 'viridis_r', 'winter', 'winter_r'