import sys
import cv2
import json
import os

def get_img_output_length(width, height):
    def get_output_length(input_length):
        return input_length//16

    return get_output_length(width), get_output_length(height)

def get_pascal_data(input_annotation_path):
    """Parse the data from annotation file

    Args:
        input_path: annotation file path

    Returns:
        all_data: list(filepath, width, height, list(bboxes))
        classes_count: dict{key:class_name, value:count_num}
            e.g. {'Car': 2383, 'Mobile phone': 1108, 'Person': 3745}
        class_mapping: dict{key:class_name, value: idx}
            e.g. {'Car': 0, 'Mobile phone': 1, 'Person': 2}
    """
    with open(input_annotation_path,'r') as f:
        temp = json.loads(f.read())

    input_images_path = os.path.dirname(os.path.abspath(input_annotation_path))
    input_images_path = os.path.join(input_images_path, './images')
    found_bg = False
    all_imgs = {}

    classes_count = {}

    class_mapping = {}
    class_reverse_mapping = {}

    #fill class_mapping, no background
    for category in temp['categories']:
        class_name = category['name']
        class_id = category['id']-1
        class_mapping[class_name] = class_id
        class_reverse_mapping[class_id] = class_name

    annindex_start = 0
    for image in temp['images']:
        filename = image['file_name']
        filepath = os.path.join(input_images_path, filename)
        #import pdb;pdb.set_trace()
        all_imgs[filename] = {}
        all_imgs[filename]['filepath'] = filepath
        all_imgs[filename]['width'] = image['width']
        all_imgs[filename]['height'] = image['height']
        all_imgs[filename]['bboxes'] = []
        img_id = image['id']
        for index in range(annindex_start,len(temp['annotations'])):
            ann_temp = temp['annotations'][index]
            if ann_temp['image_id'] == img_id:
                x1 = ann_temp['bbox'][0]
                y1 = ann_temp['bbox'][1]
                x2 = x1+ann_temp['bbox'][2]
                y2 = y1+ann_temp['bbox'][3]
                tmp_class_id = ann_temp['category_id']-1
                tmp_class_name = class_reverse_mapping[tmp_class_id]

                if tmp_class_name not in classes_count:
                    classes_count[tmp_class_name] = 1
                else:
                    classes_count[tmp_class_name] += 1

                all_imgs[filename]['bboxes'].append(
                    {'class': tmp_class_name, 'x1': int(x1), 'x2': int(x2), 'y1': int(y1), 'y2': int(y2)})
            else:
                annindex_start = index
                break


    all_data = []
    for key in all_imgs:
        all_data.append(all_imgs[key])
    return all_data, classes_count, class_mapping




def get_data(input_path):
    """Parse the data from annotation file

    Args:
        input_path: annotation file path

    Returns:
        all_data: list(filepath, width, height, list(bboxes))
        classes_count: dict{key:class_name, value:count_num}
            e.g. {'Car': 2383, 'Mobile phone': 1108, 'Person': 3745}
        class_mapping: dict{key:class_name, value: idx}
            e.g. {'Car': 0, 'Mobile phone': 1, 'Person': 2}
    """
    found_bg = False
    all_imgs = {}

    classes_count = {}

    class_mapping = {}

    i = 1

    with open(input_path, 'r') as f:

        print('Parsing annotation files')

        for line in f:

            # Print process
            sys.stdout.write('\r' + 'idx=' + str(i))
            i += 1

            #line_split = line.strip().split(',')

            #(filename, y1, x1, y2, x2, class_name) = line_split
            print(line)
            filename = line.split()[0]
            y1, x1, y2, x2, class_name = line.split()[1].split(',')

            if class_name not in classes_count:
                classes_count[class_name] = 1
            else:
                classes_count[class_name] += 1

            if class_name not in class_mapping:
                if class_name == 'bg' and found_bg == False:
                    print(
                        'Found class name bg.Will be treated as background (this is usually for hard negative mining).')
                    found_bg = True
                class_mapping[class_name] = len(class_mapping)

            if filename not in all_imgs:
                all_imgs[filename] = {}

                img = cv2.imread(filename)
                (rows, cols) = img.shape[:2]
                all_imgs[filename]['filepath'] = filename
                all_imgs[filename]['width'] = cols
                all_imgs[filename]['height'] = rows
                all_imgs[filename]['bboxes'] = []
            # if np.random.randint(0,6) > 0:
            # 	all_imgs[filename]['imageset'] = 'trainval'
            # else:
            # 	all_imgs[filename]['imageset'] = 'test'

            all_imgs[filename]['bboxes'].append(
                {'class': class_name, 'x1': int(x1), 'x2': int(x2), 'y1': int(y1), 'y2': int(y2)})

        all_data = []
        for key in all_imgs:
            all_data.append(all_imgs[key])

        # make sure the bg class is last in the list
        if found_bg:
            if class_mapping['bg'] != len(class_mapping) - 1:
                key_to_switch = [key for key in class_mapping.keys() if class_mapping[key] == len(class_mapping) - 1][0]
                val_to_switch = class_mapping['bg']
                class_mapping['bg'] = len(class_mapping) - 1
                class_mapping[key_to_switch] = val_to_switch

        return all_data, classes_count, class_mapping
