## Project
**Lidar & 3D visualization practice** 🏢 🏞️ 🛰️

<table>
  <tr>
      <td>
      <img src="./figures/internal/test_miami_beach_fl_isomtric.png?raw=true" align="center" alt="Preface - Miami Beach, FL basic" width="400">
      </td>
      <td>
      <img src="./figures/internal/fancy_preface.png?raw=true" align="center" alt="Preface - Dallas TX complex" width="600">
      </td>
   </tr>
 </table>

## 📖 Task description
> Placeholder

Work was inspired by the various `rayshader` (`raytracing` + `terrain shading/hillshading`, which cover both 'smart' light rendering and 'smart' relief shades above known topography) projects in particular and trends in 3D geodataviz in general. Usually people in DataViz community have been using either over-specialized tools (f.e. `blender`, `aeroid`, `3DMax`, `plugins for *GIS` family of professional software) or R programming language ecosystem (f.e. `rayshader`, `rayvista`). This project is trying to accelerate python-based pipeline.

Target goal of a project was to combine `3D rendered plots` (meshes above Digital Surface Models) with `OSM datasets` (polygons and their feature-attributes) acquired over the [Downtowns, Parks, Parkings](#link) project to color selected assets across dozens of urban areas in a fancy and automated way. However, I've meet some restrictions still working under trying to match and scale datasets. The major restriction was caused by a limited availability of a high quality (~1m/<3ft) actual point cloud open datasets.

<details>
  <summary><i>Pipeline scheme</i> - click to view draft</summary>
  <table>
   <tr>
      <td>
      Data flow (logic)
      </td>
   </tr>
   <tr>
      <td>
      <img src="./figures/external/pipeline_flow.jpg?raw=true" align="center" alt="pipeline flow (draft)" width="100%">
      </td>
   </tr>
</table>
</details>

Current raw report available, see [[html]](https://htmlpreview.github.io/) | [[ipynb]](https://nbviewer.org/)

## 📊 Selected charts
Selected charts are provided in high quality. See below.
<details>
  <summary><i>Charts</i> - click to expand</summary>
  <table>
    <tr>
        <td>isometric</td>
        <td>orthographic</td>
    </tr>
    <tr>
        <td>
          <img src="./figures/internal/miami_beach_fl_isometric.png?raw=true" align="center" alt="Miami Beach, FL - 3D isometric  projection" width="1280"  loading="lazy">
        </td>
        <td>
          <img src="./figures/internal/miami_beach_fl_orthographic.png?raw=true" align="center" alt="Miami Beach, FL - orthographic  projection" width="1280"  loading="lazy">
        </td>
    </tr>
      <td colspan=2>↑ <b>Miami Beach, FL.</b> <br><i>Data comes from State of Florida Division of Emergency Management LiDAR Project, 2007. 1ft aerial LiDAR. Tiled Lidar point cloud. [link](http://dpanther2.ad.fiu.edu/Lidar/lidarNew.php)</td>
    <tr>
        <td>isometric</td>
        <td>orthographic</td>
    </tr>
    </tr>
    <tr>
        <td>
          <img src="./figures/internal/dallas_tx_isometric.png?raw=true" align="center" alt="Dallas - 3D isometric  projection" width="1280" loading="lazy">
        </td>
        <td>
          <img src="./figures/internal/dallas_tx_orthographic.png?raw=true" align="center" alt="Dallas - top, 2D orthographic projection" width="1280" loading="lazy">
        </td>
    </tr>
      <td colspan=2>↑ <b>Dallas, TX.</b> <br><i>Data comes from USGS 2019 (Texas Pecos Dallas). Retrived via Texas Natural Resources Information System. 70cm aerial LiDAR. Tiled Compressed Lidar Point Cloud. [link](https://tnris.org/stratmap/elevation-lidar/)</td>
    <tr>
        <td>isometric</td>
        <td>orthographic</td>
    </tr>
    <tr>
        <td>
          <img src="./figures/internal/bishkek_kg_isometric.png?raw=true" align="center" alt="Bishkek, Kyrgyzstan - 3D isometric  projection" width="1280" loading="lazy">
        </td>
        <td>
          <img src="./figures/internal/bishkek_kg_orthographic.png?raw=true" align="center" alt="Bishkek, Kyrgyzstan - top, 2D orthographic projection" width="1280" loading="lazy">
        </td>
    </tr>
      <td colspan=2>↑ <b>Bishkek city, Kyrgyzstan.</b> <br><i>Data comes Pleiades tristereo optical imagery, 2013 (retrived via OpenTopography). 0.5m satellite remote sensing photogrammetry point cloud. [link](https://portal.opentopography.org/dataspace/dataset?opentopoID=OTDS.092021.32643.1)</td>
   </table>
</details>

## 📁 Structure of repository
```
Project structure:
+--data                       <- folder for datasets
¦  L--raw                       <- ... 1. raw data
¦  L--interim                   <- ... 2. auxiliary, generated, temporary, preprocessed data
¦  L--processed                 <- ... 3. final, ready-to-analysis data
¦  L--external                  <- ... +. additional datasets
¦  
+--notebooks                  <- folder for *.ipynb files
¦  L--*.ipynb 1                 <- ... file 1
¦
+--src                        <- folder for .py scripts
¦  L--*.py 1                    <- ... file 1
¦  L--*.py 2                    <- ... file 2
¦  L--*.py 3                    <- ... file 3
¦
+--figures                    <- folder for charts and images to reports
¦  L--external                  <- ... 1. external images
¦  L--internal                  <- ... 2. internal images
¦
+--reports                    <- folder for reports (i.e. *.pptx, *.html, *.ipynb)
¦
+--docs                       <- folder for documentation files
¦
+--README.md                  <- the top-level README for developers using this project
```
[Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/#directory-structure)

## 📌 Links
> Placeholder
<!--- * Feature engineering. Preprocessing. Charts [Here](https://nbviewer.org/) --->

## 🐉 License and legals
Ask before use.
