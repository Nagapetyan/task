import argparse
import datetime
import json
import os
import shutil
from typing import List, Tuple

import cv2
import numpy as np
from tqdm import tqdm

from imaging_interview import compare_frames_change_detection, preprocess_image_change_detection



parser = argparse.ArgumentParser()
parser.add_argument("--dataset-path", type=str, required=True, help="Path to the dataset")
parser.add_argument("--params-path", type=str, default="params.json", help="Path to file with parameters for filtering similar images")


def load_normalized_dataset(dataset_path: str):
    """
    Function loads dataset, normalize timestamps.
    Originally image name can be in 2 formats:
        c23-1616742781936.png or c21_2021_04_27__11_47_21.png
    Script will convert it to first type
    """
    
    camera2pathes = dict()
    
    image_pathes = os.listdir(dataset_path)
    for image_name in tqdm(image_pathes):
        image_path = os.path.join(dataset_path, image_name)
        try:
            img = cv2.imread(image_path)
            camera = image_name[:3]
            shape = img.shape[:2]
            assert shape[0] > 10
            assert shape[1] > 10

            if camera not in camera2pathes:
                camera2pathes[camera] = []
            
            if '_' in image_name:
                dt = datetime.datetime.strptime(image_name[4:][:-4], "%Y_%m_%d__%H_%M_%S")
                unix_timestamp_ms = int(dt.timestamp() * 1000)
                image_new_name = camera + "-" + str(unix_timestamp_ms) + ".png"
                new_image_path = os.path.join(dataset_path, image_new_name)
                shutil.move(image_path, new_image_path)
                
                camera2pathes[camera].append(new_image_path)
            else:
                camera2pathes[camera].append(image_path)
        except:
            os.remove(image_path)
                    
            
    for key in camera2pathes:
        camera2pathes[key] = sorted(camera2pathes[key], key=lambda filename: int(filename.split('-')[1][:-4]))

    return camera2pathes


def load_images(img_pathes: List[str]):
    """
    Loads all images for camera
    """
    imgs = []
    for path in tqdm(img_pathes):
        img = cv2.imread(path)
        img = cv2.resize(img, (640, 480))
        imgs.append(img)
    return imgs


def filter_subsequent(imgs: List[np.ndarray], 
                      img_pathes: List[str], 
                      gaussian_blur_radius_list: int, 
                      black_mask: Tuple[int], 
                      min_contour_area: float, 
                      thr: float):
    """
    Go through sorted by time frames first to reduce complexity
    """
    non_filtered_images = [imgs[0]]
    non_filtered_pathes = [img_pathes[0]]
    for ind in tqdm(range(len(imgs)-1)):

        img1 = imgs[ind]
        img2 = imgs[ind+1]
        

        img1_preprocessed = preprocess_image_change_detection(img1,
                                                 gaussian_blur_radius_list=gaussian_blur_radius_list, 
                                                 black_mask=black_mask)
        img2_preprocessed = preprocess_image_change_detection(img2, 
                                                 gaussian_blur_radius_list=gaussian_blur_radius_list, 
                                                 black_mask=black_mask)
        
            
        score, res_cnts, thresh  = compare_frames_change_detection(img1_preprocessed, 
                                                                   img2_preprocessed, 
                                                                   min_contour_area=min_contour_area)
            
        if score > thr:
            non_filtered_images.append(img2)
            non_filtered_pathes.append(img_pathes[ind+1])
        else:
            os.remove(img_pathes[ind+1])
            
    return non_filtered_images, non_filtered_pathes
    
    
def filter_nonsubsequent(imgs, img_pathes, gaussian_blur_radius_list, black_mask, min_contour_area, thr):
    """
    Filter the remaining images by comparing almost all of them with each other.
    """
    non_filtered_images = []
    non_filtered_pathes = []
    filtered_pathes = set()
    
    for i, img1 in tqdm(enumerate(imgs)):
        img1_path = img_pathes[i]
        
        if img1_path in filtered_pathes:
            continue
            
        for j, img2 in enumerate(imgs[i+1:]):
            img2_path = img_pathes[i+j+1]
            
            if img2_path in filtered_pathes:
                continue


            img1_preprocessed = preprocess_image_change_detection(img1,
                                                     gaussian_blur_radius_list=gaussian_blur_radius_list, 
                                                     black_mask=black_mask)
            img2_preprocessed = preprocess_image_change_detection(img2, 
                                                     gaussian_blur_radius_list=gaussian_blur_radius_list, 
                                                     black_mask=black_mask)


            score, res_cnts, thresh  = compare_frames_change_detection(img1_preprocessed, 
                                                                       img2_preprocessed, 
                                                                       min_contour_area=min_contour_area)
            if score <= thr :
                filtered_pathes.add(img2_path)
                
    for img, img_path in zip(imgs, img_pathes):
        if img_path not in filtered_pathes:
            non_filtered_images.append(img)
            non_filtered_pathes.append(img_path)
        else:
            os.remove(img_path)
                
    return non_filtered_images, non_filtered_pathes 
    

def filter_single_camera_images(img_paths: List[str], params: dict, camera: str):
    gaussian_blur_radius_list = params["gaussian_blur_radius_list"]
    black_mask = params["black_mask"]
    min_contour_area = params["min_contour_area"]
    thresh = params["thresh"] 
    
    imgs = load_images(img_paths)
    imgs, img_paths = filter_subsequent(imgs, img_paths, gaussian_blur_radius_list, black_mask, min_contour_area, thresh)
    imgs, img_paths = filter_nonsubsequent(imgs, img_paths, gaussian_blur_radius_list, black_mask, min_contour_area, thresh)
    print(f"Finished filtering {camera} frames")


if __name__ == "__main__":
    args = parser.parse_args()
    dataset_path = args.dataset_path
    
    params_path = args.params_path
    with open(params_path, "r") as f:
        params = json.load(f)
    
    camera2pathes = load_normalized_dataset(dataset_path)
    for camera in camera2pathes:
        filter_single_camera_images(camera2pathes[camera], params[camera], camera)
