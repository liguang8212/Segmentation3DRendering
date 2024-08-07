import os
import numpy as np
from scipy.ndimage import gaussian_filter
import vtk
import nibabel as nib
import vtkmodules.util.numpy_support as nps
import colorsys


def read_nifti_with_vtk(filepath):
    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(filepath)
    reader.Update()
    
    vtk_image = reader.GetOutput()
    
    return vtk_image, reader

def save_vtk_image_as_nifti(vtk_image, nifti_header, filepath):
    pass



def generate_color_for_label2(label, num_labels):
    #Use HSV calcuate the color, after that conver tht color to RGB
    hue = (label / (num_labels+0.1)) * 360  
    saturation = 100  
    value = 100  
    rgb = colorsys.hsv_to_rgb(hue / 360.0, saturation / 100.0, value / 100.0)
    return [int(c * 255) for c in rgb] 

def generate_color_for_label(label, num_labels):

    colors = [
        (1.0, 1.0, 1.0),
        (1.0, 0, 0),      # 红色
        (0, 1.0, 0),      # 绿色
        (0, 0, 1.0),      # 蓝色
        (1.0, 1.0, 0),    # 黄色
        (0, 1.0, 1.0),    # 青色
        (1.0, 0, 1.0),    # 品红
        (1.0,0.5,0),
        (1.0,0,0.5),
        (0.5,1.0,0),
        (0.5,0,1.0),
        (0,0.5,1.0),
        (0,1.0,0.5),
        (0.5,0.25,0),
        (0.5,0,0.25),
        (0.25,0,0.5),
        (0.25,0.5,0),
        (0,0.5,0.25),
        (0,0.25,0.5),
    ]
    
    # make sure the label in color array index range
    label_index = label % len(colors)
    
    return colors[label_index]


def multiplelabel_3D(vtk_image):

    #Obtain Vtk image and backup the data
    point_data = vtk_image.GetPointData()
    data_array = point_data.GetScalars()
    numpy_array = nps.vtk_to_numpy(data_array)
    numpy_array_back = numpy_array.copy()

    unique_labels = np.unique(numpy_array)
    #print(unique_labels)

    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.SetSize(1024, 1024) 
    render_window.AddRenderer(renderer)
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    # separately calculate the iso-surface and rendering for each label 
    for value in unique_labels:

        # copy the numpy data and set the other value = 0
        numpy_array = numpy_array_back.copy()
        numpy_array[numpy_array != value] = 0 
        iso_value = 0.5*value

        # smoothing
        #smoothed_array = gaussian_filter(numpy_array, sigma=0.15)
        #vtk_array = nps.numpy_to_vtk(smoothed_array)
        vtk_array = nps.numpy_to_vtk(numpy_array)
        point_data.SetScalars(vtk_array)

        # using MarchingCubes algorithm to calculate the iso-surface
        contour = vtk.vtkMarchingCubes()
        contour.SetInputData(vtk_image)
        contour.SetValue(0, iso_value)  
        contour.Update()
        poly_data = contour.GetOutput()

        # Set the rendering property
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)
        mapper.ScalarVisibilityOff()

        color = generate_color_for_label(value, unique_labels.size)
        print(color)
    

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color) 
        actor.GetProperty().SetSpecularColor(1, 1, 1)
        actor.GetProperty().SetSpecular(0.5)
        actor.GetProperty().SetDiffuse(0.6)
        actor.GetProperty().SetAmbient(0.2)
        renderer.AddActor(actor)

    # Set the background color and start the rendering interaction window in loop.
    renderer.SetBackground(0.0, 0.0, 0.0)
    render_window.Render()
    render_window_interactor.Start()

if __name__ == "__main__":

    current_dir = os.getcwd()
    nifti_filepath = current_dir + '/testdata/testdata.nii.gz'
    vtk_image, reader = read_nifti_with_vtk(nifti_filepath)
    multiplelabel_3D(vtk_image)