# pylint: disable=no-member
"""Import required Libraries"""
import json
import pandas as pd
import numpy as np
from more_itertools import split_when


def bbscale(bbox, W, H):
    """Scale the Bounding box"""
    W = round(W, 2)
    H = round(H, 2)
    temp = []
    temp.append(round(bbox[0] * W))
    temp.append(round(bbox[1] * H))
    temp.append(round(bbox[2] * W))
    temp.append(round(bbox[3] * H))
    return temp


def compare_bbox(b1, b2):
    """Compare Bounding boxes for intersection"""
    if b2[1] < b1[1] and b2[3] < b1[3]:
        return True
    elif b2[1] > b1[1] and b2[3] > b1[3]:
        return True
    else:
        return False


def if_intersects(bb1, bb2, return_percent_overlap=False):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.
    """
    assert bb1[0] < bb1[2]
    assert bb1[1] < bb1[3]
    assert bb2[0] < bb2[2]
    assert bb2[1] < bb2[3]

    # determine the coordinates of the intersection rectangle
    x_left = max(bb1[0], bb2[0])
    y_top = max(bb1[1], bb2[1])
    x_right = min(bb1[2], bb2[2])
    y_bottom = min(bb1[3], bb2[3])

    if x_right < x_left or y_bottom < y_top:
        if return_percent_overlap:
            return False, None
        else:
            return False
    else:
        if return_percent_overlap:
            intersection_area = (x_right - x_left) * (y_bottom - y_top)
            area_box_1 = (bb1[2] - bb1[0]) * (bb1[3] - bb1[1])
            area_box_2 = (bb2[2] - bb2[0]) * (bb2[3] - bb2[1])
            if area_box_1 > area_box_2:
                percentage_area_covered = intersection_area / area_box_1
            else:
                percentage_area_covered = intersection_area / area_box_2
            return True, percentage_area_covered
        else:
            return True


def check_and_add_text(text_list, dict_obj):
    """Recursive function to add the text to a list"""
    for key, value in dict_obj.items():
        if key in ["Search Start", "Search Stop"] and value is not None:
            text_list.append(value.strip().lower())
        elif key == "Children":
            if len(value) > 0:
                for obj in value:
                    check_and_add_text(text_list, obj)
            else:
                return


def get_control_file_text(contorl_file_path):
    """Appends all the relevant text present in the Control File
    Takes in the path of the control file as the input"""
    with open(contorl_file_path, "r", encoding="utf-8") as control_file:
        control_dict = json.load(control_file)

    text_list = []
    for obj in control_dict["control_file"]["Children"]:
        check_and_add_text(text_list, obj)

    return text_list


def not_vertically_overlapping(b1, b2):
    """Check the overlapping of bounding boxes"""
    up1, down1 = b1[1], b1[3]
    up2, down2 = b2[1], b2[3]
    return down1 < up2 or (down1 - up2) < (up2 - up1)


def groupbyrow(boxes):
    """Sort the bounding boxes and group them by row"""
    sorted_boxes = sorted(boxes, key=lambda x: x[5])
    return list(split_when(sorted_boxes, not_vertically_overlapping))


################## Dataframe function for getting BB of Doc AI response
def document_to_dataframe(documents, text_alone, width, height):
    """Doc AI response too Dataframe for finding Bounding boxes"""
    lst_min_max = []
    for document, _ in enumerate(documents):
        # vertices = document.bounding_poly.vertices
        vertices = documents[document]

        _x1 = round(vertices[0]["x"] * width)
        _y1 = round(vertices[0]["y"] * height)

        _x2 = round(vertices[1]["x"] * width)
        _y2 = round(vertices[1]["y"] * height)

        _x3 = round(vertices[2]["x"] * width)
        _y3 = round(vertices[2]["y"] * height)

        _x4 = round(vertices[3]["x"] * width)
        _y4 = round(vertices[3]["y"] * height)

        _xmin = min(_x1, _x2, _x3, _x4)
        _xmax = max(_x1, _x2, _x3, _x4)

        _xc = (_xmin + _xmax) // 2

        _ymin = min(_y1, _y2, _y3, _y4)
        _ymax = max(_y1, _y2, _y3, _y4)

        _yc = (_ymin + _ymax) // 2

        # lst_word_bound.append([str(text_alone[document]), _x1, _y1, _x2, _y2, _x3, _y3, _x4, _y4])
        lst_min_max.append(
            [str(text_alone[document]), _xmin, _ymin, _xmax, _ymax, _xc, _yc]
        )

    # import pdb; pdb.set_trace()
    # lst_word_bound = lst_word_bound[1:]
    lst_min_max = lst_min_max[1:]
    min_max_df = pd.DataFrame(
        lst_min_max, columns=["word", "xmin", "ymin", "xmax", "ymax", "xc", "yc"]
    )  # min_max_df.iloc[1:]

    return min_max_df


def get_words_within_bbox(document_dataframe, xmin, xmax, ymin, ymax):
    """Getting words within specified Bounding box"""
    selected_doc_dataframe = document_dataframe[
        (document_dataframe["xc"] >= xmin)
        & (document_dataframe["xc"] <= xmax)
        & (document_dataframe["yc"] >= ymin)
        & (document_dataframe["yc"] <= ymax)
    ]

    return selected_doc_dataframe


def bb_to_text(min_max_df, bbox):
    """Bounding box to text conversion"""
    xmin, ymin, xmax, ymax = bbox[0], bbox[1], bbox[2], bbox[3]
    selected_doc_dataframe = get_words_within_bbox(min_max_df, xmin, xmax, ymin, ymax)

    return list(selected_doc_dataframe["word"])


########################### from doc_ext_rwell.py file ########
def print_paragraphs(paragraphs: dict, text: str) -> None:
    """Print paragrahs in Doc AI response"""
    number_of_para = len(paragraphs)
    text_paragraph = {}
    for para, _ in enumerate(paragraphs):
        text_para = layout_to_text(paragraphs[para]["layout"], text)
        text_paragraph[para + 1] = text_para
    return number_of_para, text_paragraph


def print_paragraphs_1(paragraphs: dict, text: str) -> None:
    """Print paragrahs in Doc AI response"""
    text_paragraph = []
    text_para = layout_to_text(paragraphs["layout"], text)
    text_paragraph.append(text_para)
    return text_paragraph[0]


def layout_to_text(layout: dict, text: str) -> str:
    """
    Document AI identifies text in different parts of the document by their
    offsets in the entirity of the document's text. This function converts
    offsets to a string.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in layout["text_anchor"]["text_segments"]:
        start_index = (
            int(segment["start_index"])
            if segment in layout["text_anchor"]["text_segments"]
            else 0
        )
        end_index = int(segment["end_index"])
        response += text[start_index:end_index].replace("\n", " ")
    return response


def print_lines(lines: dict, text: str) -> None:
    """Layout to text conversion"""
    text_paragraph = []
    text_para = layout_to_text(lines["layout"], text)
    text_paragraph.append(text_para)
    return text_paragraph[0]


# calculate IoU
def get_intersections(bb1, bb2):
    """Get the intersection status between the bboxes input shape = [N, 4]"""

    bb1_mins = bb1[..., None, 0:2]
    bb1_maxes = bb1[..., None, 2:4]

    bb2_mins = bb2[None, ..., 0:2]
    bb2_maxes = bb2[None, ..., 2:4]

    intersect_mins = np.maximum(bb1_mins, bb2_mins)
    intersect_maxes = np.minimum(bb1_maxes, bb2_maxes)
    intersection_wh = np.maximum(intersect_maxes - intersect_mins, 0.0)

    intersection_areas = intersection_wh[..., 0] * intersection_wh[..., 1]
    intersection_mask = np.where(intersection_areas > 0.0, True, False)

    return intersection_mask


def area(bbox):
    """Calculate the area of a given bounding rectangle"""
    return (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])


def scale_to_pdf_dim(img_dim, pdf_dim, coords):
    """scale from image space to pdf space"""
    xmin, ymin, xmax, ymax = coords
    img_h, img_w = img_dim
    pdf_w, pdf_h = pdf_dim

    scale_h, scale_w = pdf_h / img_h, pdf_w / img_w

    shifted_coords = [xmin, img_h - ymin, xmax, img_h - ymax]

    scaled_coords = []
    for i, coord in enumerate(shifted_coords):
        if i % 2 == 0:
            scaled_coords.append(round(coord * scale_w))
        else:
            scaled_coords.append(round(coord * scale_h))

    return scaled_coords
