from PIL import Image
import numpy as np
from generate_supervisely import create_ann
from utils import generate_features 
from skimage.color import gray2rgb
from skimage import io
from skimage.io import imsave
import json
import math
import os
import shutil

def calcuate_grid_size(masks, objects_per_patch):
    """
    Returns the size of the square patch that axproximately contains n_objects
    Arguments:
        masks: 2D ndarray
            output array of objects
        objects_per_patch: int
            The required number of objects per patch
    Returns
    grid_size, ids_set 
    """
    ids = np.unique(masks) 
    object_density = ids.shape[0] / float(masks.shape[0] * masks.shape[1])
    correcting_area = objects_per_patch / object_density
    grid_size = int(math.ceil(math.sqrt(correcting_area)))
    ids = list(ids)
    if 0 in ids:
        ids.remove(0)
    ids = set(ids)
    return grid_size, ids 


def generate_bmp(rgb_image):
    """
    Returns the a contrasted bmp image for the original fov

    Arugments:
        rgb_image: filename
            The fov file name
	
    returns ndarray
        The 2d array in 0-255 formate
    """
    import skimage
    from PIL import Image

    image = Image.open(rgb_image)
    array = np.array(image)
    v_min, v_max = np.percentile(array, (0.2, 99.8))
    from skimage import exposure
    gray_contrast = exposure.rescale_intensity(array, in_range=(v_min, v_max))
    scaled = skimage.img_as_ubyte(gray_contrast)
    return scaled


def process_fov(fov_image, segmentation_output, output_dir, objects_per_patch=50):
    """
    Generates the supervisely directory for the given gov.
    
    Arguments:
        fov_image: filename 
            Path to the gray scale FOV. 
        segmentation_output: ndarray 2D uint16
            The instance segmentation output. One int id per object.
        output_dir: foldername
            The location of the output supervisely folder
        objects_per_patch: int
            Number of objects per supervisely ROI
    """


    scaled = generate_bmp(fov_image)
    project_dir = output_dir
    masks = segmentation_output
    if os.path.isdir(project_dir):
    	shutil.rmtree(project_dir)
    
    os.mkdir(project_dir)
    
    ann_dir = os.path.join(project_dir, "ann")
    image_dir = os.path.join(project_dir, "img")
    
    os.mkdir(image_dir)
    os.mkdir(ann_dir)
    
    edges, center_blobs, areas, borders, contours = generate_features(masks)
    
    
    x_dim = masks.shape[0]
    y_dim = masks.shape[1]
    
    
    grid_size, id_list = calcuate_grid_size(masks, objects_per_patch)
    processed_ids = set([])
    x_index = 0
    for x_start in range(0, x_dim, grid_size):
        y_index = 0
        for y_start in range(0, y_dim, grid_size):
            lower_bound = x_start
            upper_bound = x_start + grid_size
            
            left_bound = y_start
            right_bound = y_start + grid_size
            
            if upper_bound > x_dim:
                upper_bound = x_dim
            if right_bound > y_dim:
                right_bound = y_dim
            
            roi_ids = list(np.unique(masks[lower_bound:upper_bound,left_bound:right_bound]))
            if 0 in roi_ids:
                roi_ids.remove(0)
    
            roi_ids_set = set(roi_ids)
    
            roi_to_be_processed = list(roi_ids_set.difference(processed_ids))
            roi_already_processed = list (roi_ids_set  & processed_ids)
            #to_be_processed = list(id_list & roi_ids_set)
    
            #already_processed = region_ids_set.difference(id_list)
    
            #update id_list with the remaining ids that will be processed
            #id_list = id_list.difference(region_ids_set)
            processed_ids.update(roi_to_be_processed) 
       
            print "{0}:{1}, {2}:{3} to process {4}, already_processed: {5}".format(
                lower_bound, upper_bound, left_bound, right_bound, 
                len(roi_to_be_processed), len(roi_already_processed))
            
            contours_to_process = [cont[0] for cont in contours if cont[1] in roi_to_be_processed]   
            contours_already_processed = [cont[0] for cont in contours if cont[1] in roi_already_processed]   
    
    
            bb = (left_bound, upper_bound, right_bound, lower_bound)
            annotations = create_ann(masks.shape, 
                                     contours_to_process,
                                     bb,
                                     contours_already_processed)
    
            result_prefix = "{0}_{1}_{2}_{3}_{4}_{5}".format(
                x_index, y_index, lower_bound, upper_bound, left_bound, right_bound)
    
            ann_file_name = result_prefix + ".json"
            ann_file = os.path.join(ann_dir, ann_file_name) 
    
            with open(ann_file, 'w') as outfile:
                json.dump(annotations, outfile)
   

            image_file_name = result_prefix + ".bmp"
            image_file = os.path.join(image_dir, image_file_name)

            imsave(image_file, scaled)
            #shutil.copyfile(bmp_image_file, image_file)
            y_index += 1
        x_index += 1



if __name__ == "__main__":

    
    import argparse 
    parser = argparse.ArgumentParser(description = 'Generate the Supervisely project from an instance segmentation')
    parser.add_argument('fov', help='filename for the gray scale fov')
    parser.add_argument('masks', help='filename for uint image masks')
    parser.add_argument('--out_dir', default="supervisely_project", help='the supervisely directory')
    parser.add_argument('--objects_per_roi', type=int, default=50, help='the number of object per supervisely region of interest')

    args = parser.parse_args()
    ouput = Image.open(args.masks)
    masks = np.array(ouput)
    process_fov(args.fov, masks, args.out_dir, args.objects_per_roi)
