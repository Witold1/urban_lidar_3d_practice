import logging
#   https://docs.python.org/3/howto/logging.html
#   https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook
import datetime
import glob
import gc
import os

# https://towardsdatascience.com/python-libraries-for-mesh-and-point-cloud-visualization-part-1-daa2af36de30
try:
    import pyvista as pv
    from pyvista import examples as pyvista_examples
except ModuleNotFoundError::
    !pip install pyvista
    import pyvista as pv
    from pyvista import examples as pyvista_examples

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

display(pv.Report())
pv.start_xvfb()
pv.rcParams['transparent_background'] = True

def plot_raster_rasterio(raster_path=None, ax=None):
    """Auxilary plot of raster with matplotlib backend
        description

        Takes array representation of a chart
        Returns saved renders

    Parameters
    ----------
    raster_path : str
        file path to raster (.tif)
    axis : matplotlib.pyplot.axis
        axis object, where to plot
    """
    try:
        import rasterio
        from rasterio.plot import show as rasterio_show
    except ModuleNotFoundError::
        !pip install rasterio
        import rasterio
        from rasterio.plot import show as rasterio_show

    src = rasterio.open(raster_path)
    rasterio_show(src, transform=src.transform, ax=ax)

def _custom_save_rendered_plot(image_np_array=None, save_np_array=True, plot_filename='plot_temp_name.png'):
    """Saves an array of the rendered 3D chart in custom way

        * `pyvista` returns an error when one is trying to save a screenshot above of 4Kx4K window's size
            so, let's approach a workaround using `PIL` package and an array representations of the plot

        Takes array representation of a chart
        Returns saved renders

    Parameters
    ----------
    img_np_array : np.array
        output of `pyvista.Plotter.screenshot(filename=None, return_img=True)
    save_array : bool
        if save `img_np_array` in auxilary file
    plot_filename : str
        file name and extension of an output file (.png, .jpg, .gif)
    """
    try:
        from PIL import Image
    except ModuleNotFoundError::
        !pip install PIL
        from PIL import Image
    print(f'\t\t{datetime.datetime.now()} Saving high quality plot array')
    # https://numpy.org/doc/stable/reference/generated/numpy.save.html#numpy.save
    np.save(plot_filename + '.array', image_np_array)
    print(f'\t\t{datetime.datetime.now()} Saving high quality plot screenshot')
    # https://stackoverflow.com/questions/902761/saving-a-numpy-array-as-an-image
    im = Image.fromarray(image_np_array)
    im.save(plot_filename, optimize=True, quality=1.0, bbox_inches='tight')
    del(im, image_np_array)

def plot_3D(mesh=None, plotter_params=None, plot_isometric=True, save_plot_mode='save render', plot_filename=None):
    """Plot 3D rendered charts according to selected params
        Saves or shows the rendered chart

        Takes mesh and parameters
        Returns or shows saved renders

        * For colorbars, check
            https://docs.pyvista.org/examples/02-plot/scalar-bars.html
        * For titles, check
            https://docs.pyvista.org/api/plotting/_autosummary/pyvista.Plotter.add_title.html

    Parameters
    ----------
    mesh : PyVista Data Object, for example pv.UnstructuredGrid or pv.StructuredGrid
        See PyVista Data Model https://docs.pyvista.org/user-guide/data_model.html
    plotter_params : **kwarg
        data structure with parameters to init plotter object. NOT IMPLEMENTED YET.
    plot_isometric : bool
        set default isometric angle (view from around) if true
        set default orthographic view (from above) if false
    save_plot_mode : str
        - `save render orbiting` for orbiting (.gif, from many screenshots, imageio-ffmpeg backend)
        - `save render orbiting video` for orbiting video (.mp4, from many screenshots). NOT IMPLEMENTED YET.
        - `save render` for static render (.png)
        - `just show` for no save, show render only
    plot_filename : str
        param of _custom_save_rendered_plot
        file name and extension of an output file (.png, .jpg, .gif)
    """

    p = pv.Plotter(multi_samples=16, line_smoothing=True, lighting='light_kit', window_size=[3000, 3000])
    p.enable_lightkit()

    print(f'\t{datetime.datetime.now()} Add mesh')
    actor_1 = p.add_mesh(mesh, cmap='Blues', log_scale=False, show_scalar_bar=False)
    # actor2 = p.add_mesh(topo_clipped_water, clim=[-10, 2.5], cmap=['lightblue']) # "add water" the hard way

    if not plot_isometric:
        p.view_xy()
        print(f'\tUse orthographic view angle for plotter')
    else:
        print(f'\tUse default (isometric) view angle for plotter')

    print(f'\t{datetime.datetime.now()} Add custom light source')
    light = pv.Light(intensity=0.7)
    light.set_direction_angle(300, -20)
    p.add_light(light)

    ### check `light_kit`, `pv.Light` custom lights, or some other params to avoid VTK errors
    ### (vtkShaderProgram.cxx:452 / vtkOpenGLState errors)
    # print(f'\t{datetime.datetime.now()} Enable shadows')
    # p.enable_shadows() # disable

    print(f'\t{datetime.datetime.now()} Enable anti_aliasing')
    p.enable_anti_aliasing(aa_type='msaa')
    # p.enable_depth_peeling() # ?
    # p.enable_depth_of_field
    # p.enable_eye_dome_lighting

    print(f'\t{datetime.datetime.now()} Add grid')
    ### check coordinates and projection https://github.com/pyvista/pyvista-support/issues/394
    p.show_grid(color='lightgrey')
    print(f'\t{datetime.datetime.now()} Add bounding_box')
    p.add_bounding_box(opacity=0.75, color='lightgrey')

    if save_plot_mode == 'save render orbiting':
        !pip install imageio-ffmpeg
        print(f'\t{datetime.datetime.now()} Save orbiting')
        p.camera.zoom(1.5)
        path = p.generate_orbital_path(n_points=36, shift=mesh.length)
        p.open_gif(plot_filename) # "orbit_ortho1.gif"
        p.orbit_on_path(path, write_frames=True)
    elif save_plot_mode == 'save render':
        print(f'\t{datetime.datetime.now()} Save plot screenshot in high quality')
        image_np_array = p.screenshot(filename=None, return_img=True)
        _custom_save_rendered_plot(image_np_array=image_np_array, save_np_array=True,
                                   plot_filename=plot_filename)
    elif save_plot_mode == 'just show':
        p.show()

    print(f'\t{datetime.datetime.now()} Garbage collection and memory cleaning')
    p.deep_clean()
    p.clear()
    del(p, actor_1) # actor_2, etc
    gc.collect()

def _main_visualisation():
    """Runs through cities list
        renders charts, saves rendered charts
    """
    experiment_number = 1
    for indx, file in enumerate(glob.glob('/kaggle/input/miami-beach-lidar-raster/*.tif')):
        print(f"{datetime.datetime.now()} Reading for Visualisation. Processing {file}.")
        mesh = get_data._read_processed_rasterized_file(file_path=file,
                                          CUSTOM_READ=True)
        display(mesh)
        topo_clipped = mesh.clip_scalar(scalars="data", value=0.1, invert=False, progress_bar=True)
        display(topo_clipped)
        if 'mosaic' in file:
            topo_clipped.rotate_z(90) # if Miami
            key = 'MIAMI FL USA'
            wrap_factor = 0.02
        else:
            topo_clipped.rotate_z(-90) # if Dallas
            key = 'DALLAS TX USA'
            wrap_factor = 0.03
        gc.collect()
        print(f'\t{key}')

        print(f"\t{datetime.datetime.now()} Visualisation. Orbiting.")
        plot_filename = f"Shades_{key}_tst{experiment_number}_biliniar_orbiting_3K.gif" # png
        plot_3D(mesh=topo_clipped.warp_by_scalar(factor=wrap_factor), plotter_params=None, plot_isometric=True,
                save_plot_mode='save render orbiting', plot_filename=plot_filename)
        gc.collect()
        print(f"\t{datetime.datetime.now()} Visualisation. Isometric.")
        plot_filename = f"Shades_{key}_tst{experiment_number}_biliniar_isometric_3K.png"
        plot_3D(mesh=topo_clipped.warp_by_scalar(factor=wrap_factor), plotter_params=None, plot_isometric=True,
                save_plot_mode='save render', plot_filename=plot_filename)
        gc.collect()
        print(f"\t{datetime.datetime.now()} Visualisation. Orthographic.")
        plot_filename = f"Shades_{key}_tst{experiment_number}_biliniar_ortho_3K.png"
        plot_3D(mesh=topo_clipped.warp_by_scalar(factor=wrap_factor), plotter_params=None, plot_isometric=False,
                save_plot_mode='save render', plot_filename=plot_filename)
        gc.collect()
