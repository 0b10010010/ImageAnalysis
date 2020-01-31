# KSU SUAS Image Analysis GUI

Before anything else happens, run the following command when OBC boots:
```
ssh odroid@OBC_IP
lsyncd /etc/lsyncd/lsyncd.conf.lua
```
Above commands will ssh into OBC from GCS and start lsyncd to sync the target image directory on GCS to the source directory on OBC where images are actually stored.

To use the GUI simply launch the GUI python script. When it opens, click on "Load Image" button.
Image from sorted list should be loaded to GUI and users can use mouse wheel scroll to zoom in and out of the image.
Use right mouse button to drag an area of interest then manually input all characteristics of the target. Once all the fields are filled click on "Crop and Process" button to crop the image and save all the metadata from user. This will save the cropped target with all the relative information calculated as well.

To navigate through images simply press arrow keys.

"Detect Camera" button is used to check if the camera is visible to onboard computer. When the available camera returns in console, "Start Triggering Camera" button can be used to send signal to the camera. The camera is set to capture images at 3-second interval. Camera triggering can be aborted using the same button (it will say "Cancel Triggering Camera"). Green button means the camera is triggering and red button means it is not.

# Tasks
- [x] lsyncd
- [ ] Geotagging
