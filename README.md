# Project Name

Kopernikus task

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Questions&Answers](#q&a)

## Installation


### Prerequisites

List of prerequisites that you need to install before:

- Python 3.7 or higher
- pip package manager

### Installation Steps

   ```bash
   git clone https://github.com/yourusername/yourproject.git

   cd Kopernikus_task
   
   pip install -r requirements.txt
   ```
   

## Usage 

    ```bash
    
    python python filter_images.py --dataset-path dataset
    
    ```
    
## Questions & Answers
    Q: What did you learn after looking on our dataset?
    A: The dataset consists of images captured from four cameras at different times of the day. The images vary in dimensions, and there are several corrupted images present. Some images have dimensions of 6x4 pixels. Additionally, there are numerous visually similar images in the dataset.
    
    Q: How does you program work?
    My program standardizes timestamps to a single format, then sorts them by time. Next, it resizes the images to a uniform resolution. The filtering process occurs in two stages. The first stage involves comparing neighboring frames, which is a fast way to filter out highly similar frames within a small time interval. The second stage compares all remaining images pairwise, in case morning and evening images, for example, are similar.

    Note: With a larger dataset, we could apply a time window, such as 1 hour, instead of only considering the nearest frame. Additionally, timestamps could be made independent of the day, focusing solely on the hour.

    Q: What values did you decide to use for input parameters and how did you find these values?
    A: All the input parameters are specified in the params.json file. I determined these parameters based on the results of the filtering process. The mask is applied on top, covering all the insignificant details. Gaussian filtering employs two kernels, one for fine noise and another for larger noise caused by light. The threshold value was chosen specifically for the camera. If there is a need to consolidate these parameters into a single parameter, then the smallest values from each parameter would be selected.
    
    Q: What you would suggest to implement to improve data collection of unique cases in future?
    A: To improve data collection for unique cases in the future, it is recommended to incorporate a greater variety of objects and scenarios. This can include instances where the vehicle is in proximity to both common and uncommon objects. Additionally, to address overexposure issues, consider introducing white objects or individuals wearing white clothing into the dataset, as these can pose unique challenges. The current dataset exhibits a high degree of similarity, so it would be beneficial to include larger vehicles and different vehicle models like the 'Matis.' Diversifying the dataset will enhance its representativeness and applicability.
    
    Q: Any other comments about your solution?
    A: The first improvement has been suggested earlier. Another potential enhancement within the current constraints is to create a more flexible mask based on multiple frames. This could help address issues related to light coming from windows, which has a significant impact in these conditions. In some cases, two images might differ mainly in the lighting from the windows, leading to a large object difference. A more adaptive mask could mitigate this issue.
    