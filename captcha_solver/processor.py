# requirements python 2.7
import glob
import cv2
import pytesseract
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


def image_show(image):
    """
    display images. Essential when testing it.
    :param image:
    :return:
    """
    cv2.imshow('image', image)
    cv2.waitKey(0)


def erode_dilate(processed_img):
    """
    removes the small noises like white dots from the image.
    :param array processed_img: gray image in which colored lines have been removed
    :return array image:
    """
    k1 = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    kernel = np.ones((2, 2), np.uint8)
    processed_img = cv2.erode(processed_img, k1, iterations=1)

    for width_pixel in range(processed_img.shape[1]):
        white_edge = np.sum(processed_img[:, width_pixel] == 255)

        # turns single columns with single white dots to black colour.
        if white_edge < 2:
            processed_img[:, width_pixel] = 0

    processed_img = cv2.dilate(processed_img, kernel)

    return processed_img


def preprocess_image(img):
    """
    takes in a raw image. removes most coloured lines and dots
    :param img:
    :return:
    """
    height, width, channels = img.shape
    for x in range(0, height):
        for y in range(0, width):
            pixel_a = img[x, y, 3]

            if pixel_a == 0:
                img[x, y, 0] = 255
                img[x, y, 1] = 255
                img[x, y, 2] = 255
                img[x, y, 3] = 255

    # converts image from (720,1280,4) to (720,1280)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    img = gray_image.astype(np.uint8)
    im = cv2.bitwise_not(img)

    # finds for all major connected Components like alphabets.
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(im, connectivity=4)

    sizes = stats[1:, -1]

    # removing the condition where we consider the whole image
    # nb_components = nb_components - 1

    img2 = np.zeros(output.shape)

    # choosing 6 alphabet which we want to convert from image to text
    for i in range(0, 6):
        max_index = list(sizes).index(max(sizes))
        img2[output == max_index + 1] = 255
        sizes[max_index] = 0

    # erode meaning to remove noise
    k1 = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    img2 = cv2.erode(img2, k1, iterations=2)

    kernel = np.ones((2, 2), np.uint8)
    # dilate means to extra extra boundary to edges to make alphabets in image bolder.
    img2 = cv2.dilate(img2, kernel)

    return img2


def correct_letter_verification_for_l(image):
    """
    sometimes l is misclassified as 1. So,we look for the base line on l and 1.
    1 tends to have a longer base lines than l.

    :param image:
    :return boolean: whether the image has an l or 1
    """
    white_edge_list = []
    for width in range(image.shape[1]):
        white_edge_list.append(np.sum(image[:, width] == 255))

    # l and 1 difference when it comes to the length of right bottom strip
    right_strip_length = 0
    for white_pixel in white_edge_list:

        if 2 < white_pixel < 12:
            right_strip_length += 1

        if white_pixel > 20:
            break

    if right_strip_length > 7:
        return 1

    else:
        return 'l'


def letter_verification_for_capital(image):
    """
    sometimes smaller letter look like their capital counter and algorithm tends to be confused.
    like (c,C),(z,Z),(v,V). We tend to look for the space above the letter. If there is large space then it's a
    small word otherwise it's a capital letter.

    :param image:
    :return boolean: if it's a capital it'll return True
    """
    # average height where we find white pixel or the starting of a letter
    height_distance_for_small_letter = int(image.shape[0] / 4)
    black_pixel_count_for_finding_height = 0

    for height in range(image.shape[0]):

        if (np.sum(image[height, :] == 255)) < 3:
            black_pixel_count_for_finding_height += 1
        else:
            break

    if black_pixel_count_for_finding_height > height_distance_for_small_letter:
        return False
    else:
        return True


def correct_letter_verification_for_i(image):
    """
    I ,r so capital I is without the strip bars in the captcha and it resembles the
    the letter r.
    I and P are also sometimes mis-classified.
    This algorithm helps with the classification as I and r can be distinguish by the space
    above it. where P and I can be classified with the help of the bottom strip.
    :param image:
    :return:
    """
    height_distance_for_small_letter = int(image.shape[0] / 4) + 1

    black_pixel_count_for_finding_height = 0

    for width in range(image.shape[0]):

        if (np.sum(image[width, :] == 255)) < 3:
            black_pixel_count_for_finding_height += 1
        else:
            break

    sum_white_pixel_at_bottom = 0

    for bottom_width in range(50, image.shape[0]):
        white_pixel = np.sum(image[bottom_width, :] == 255)
        sum_white_pixel_at_bottom += white_pixel

    # print(sum_white_pixel_at_bottom)

    if sum_white_pixel_at_bottom > 140:
        char = 'I'

    else:
        char = 'P'
    # whether its 'r' are it's the char(P or I)
    if black_pixel_count_for_finding_height > height_distance_for_small_letter:
        return 'r'

    else:
        return char


def correct_letter_verification_for_h(image):
    """
    n tends to be sometimes predicted as h, but the algorithm predicts it as capital 'H'. So, we look
    for the space in the top most region of the letter.
    h will have some white pixels where n won't have.

    :param image:
    :return:
    """

    height_distance_for_small_letter = int(image.shape[0] / 4) + 1
    black_pixel_count_for_finding_height = 0

    for height in range(image.shape[0]):

        if (np.sum(image[height, :] == 255)) < 3:
            black_pixel_count_for_finding_height += 1
        else:
            break

    if black_pixel_count_for_finding_height > height_distance_for_small_letter:
        return False
    else:
        return True


def correct_letter_verification_for_r(image):
    """
    again 'i' and 'r' can be classified when we walk towards y axis
    looking for white pixels.
    'i' will have concentration at 2-3 columns where r will be have concentration
    at moire then 4 columns.
    :param image:
    :return:
    """
    white_pixel_list = []

    for width in range(image.shape[1]):
        white_pixel = np.sum(image[:, width] == 255)
        if white_pixel != 0:
            white_pixel_list.append(white_pixel)

    if len(white_pixel_list) > 4:
        return True
    else:
        return False


def correct_letter_verification_for_0(image):
    """
    so 'O' or big O tends to be thicker than 0.
    So, the letter with thicker width is O and other one is 0

    :param image:
    :return:
    """
    white_pixel_list = []

    for width in range(image.shape[1]):
        white_pixel = np.sum(image[:, width] == 255)
        if white_pixel != 0:
            white_pixel_list.append(white_pixel)

    if len(white_pixel_list) > 25:
        return False
    else:
        return True


def correct_letter_verification_for_capital_j(image):
    """
    j and J tends to look exactly the same in captcha format except for the dot on small
    j.
    :param image:
    :return:
    """
    # image_show(image)
    white_pixel_list = []

    for height in range(image.shape[0]):
        white_pixel = (np.sum(image[height, :] == 255))
        white_pixel_list.append(white_pixel)

    distance_between_j_and_dot = 0
    dot_flag = 0

    for element in white_pixel_list:

        if element != 0 and dot_flag != 1:
            dot_flag = 1
            if distance_between_j_and_dot > 0:
                break

        if dot_flag == 1 and element == 0:
            distance_between_j_and_dot += 1
            dot_flag = 0

    # print(distance_between_j_and_dot)

    if distance_between_j_and_dot == 0:
        return True
    else:
        return False


def correct_letter_verification_for_capital_d(image):
    """
    if you see p without the bottom vertical strip, it's a D
    that's why it's mis-classify.
    We tend to look for the bottom vertical strip.

    :param image:
    :return:
    """

    white_pixel_list = []

    for height in range(image.shape[0]):
        white_pixel_list.append((np.sum(image[height, :] == 255)))

    sum_last_five_element = 0

    for elements_last in white_pixel_list[-4:]:
        sum_last_five_element += elements_last

    # print('correct_letter_verification_for_capital_d', sum_last_five_element)

    if sum_last_five_element > 6:
        return 'p'

    elif sum_last_five_element == 0:
        return 'D'


def removing_extra_char_cropped_img(cropped_img):
    """
    it looks whether a single cropped_img has two characters in it.
    if there are two letters in one image, there will be two white columns separated by big columns of dark space.
    1.) the letter is in the start and the partial character is in the end. In this case we look for the sum of white
    spaces in the start. If it's greater than 120,there will be a letter. So, we can remove what comes after it.

    2.) their is a partial letter, in that case the sum of white pixels will be less than 120 and we can delete the
    first character if we find a partial print at the end.

    :param cropped_img:
    :return:
    """
    blank_space = 0

    flag_blank_space_found = 0
    sum_white_pixels = 0

    for width in range(cropped_img.shape[1]):

        white_pixels = (np.sum(cropped_img[:, width] == 255))
        sum_white_pixels += white_pixels

        if white_pixels == 0:
            blank_space += 1
            if blank_space == 15:
                flag_blank_space_found = 1

        else:

            blank_space = 0

            if flag_blank_space_found == 1:

                # print(sum_white_pixels, 'CROPPING')
                # on average a letter has 110 white pixels in it
                if sum_white_pixels > 110:

                    new_end_y = width - 5
                    cropped_img = cropped_img[:, :new_end_y]
                    # print('Delete extra character from end ')
                    break

                else:
                    # print('sum of white pixel of front character', sum_white_pixels)
                    new_start_y = width - 15
                    cropped_img = cropped_img[:, new_start_y:]
                    # print('Delete extra character from front')
                    break

    return cropped_img


def finding_edges_alphabet(processed_img):
    """
    it helps in finding starting index of each character.

    :param processed_img:
    :return:
    """
    processed_img = erode_dilate(processed_img)

    letter_y_list = []
    sum_black_pixel = 0
    new_edge_found = 1

    for width_pixel in range(processed_img.shape[1]):
        white_edge = np.sum(processed_img[:, width_pixel] == 255)

        # makes sure there is a distance of black pixel region between two regions
        if white_edge == 0:

            sum_black_pixel += 1
            if sum_black_pixel > 8:
                new_edge_found = 1
                sum_black_pixel = 0

        # 3 is the size for most dots going for 4 and above makes it robust
        if white_edge > 3 and new_edge_found == 1:
            # this was made for characters like L or N where the white pixels starts suddenly, in order to give
            # enough space for it, we use white_edge >32

            # white edge is greater than 32 in case of edges like L or I, so we need to give
            # some extra right space to them so we can make an evenly spaced image.
            if white_edge > 32:
                # print('GREATER THAN 32\n', width_pixel)

                if len(letter_y_list) > 0:

                    # only if there is a difference of 25 between two characters they'll be considered otherwise
                    # we will be reading the same character and we can overlook it.

                    if width_pixel - letter_y_list[-1] > 31:
                        width_straight_figures = width_pixel
                        letter_y_list.append(width_straight_figures)

                else:
                    # append 0 as the index for the fist word
                    letter_y_list.append(0)

            else:
                if len(letter_y_list) > 0:

                    # only if there is a difference of 25 between two characters they'll be considered otherwise
                    # we will be reading the same character and we can overlook it.

                    if width_pixel - letter_y_list[-1] > 31:
                        letter_y_list.append(width_pixel)

                else:
                    # case for the first character / letter
                    letter_y_list.append(0)

            sum_black_pixel = 0
            new_edge_found = 0

    # print(len(letter_y_list))
    # print(letter_y_list)
    return processed_img, letter_y_list


def preprocessing_each_alphabet(processed_img, letter_edges):
    """
    each processed image is broken into 6 letter, these letter are feed into pytesseract algorithm for prediction.

    :param processed_img:
    :param letter_edges:
    :return:
    """
    full_text = ""

    for individual_image_scale in range(0, 6):

        if individual_image_scale == 0:
            start_y = 0
            end_y = 40

        elif individual_image_scale == 5:

            start_y = processed_img.shape[1] - 38
            end_y = processed_img.shape[1]

        else:

            start_y = letter_edges[individual_image_scale] - 2
            end_y = start_y + 40

            if end_y >= processed_img.shape[1]:
                end_y = processed_img.shape[1] - 1

        # image_show(processed_img)
        cropped_img = processed_img[0:processed_img.shape[0], start_y: end_y]
        # image_show(cropped_img)

        cropped_img = removing_extra_char_cropped_img(cropped_img)

        if cropped_img.shape[0] * cropped_img.shape[1] < 1000:
            full_text = None
            break
        # print('Area',cropped_img.shape[0]*cropped_img.shape[1])

        single_char = pytesseract.image_to_string(cropped_img,
                                                  config="-oem -O -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -psm 10",
                                                  lang="eng")

        if single_char in ["None", None, "none", "null", "", [], {}, set(), tuple()]:
            full_text = None
            break

        if single_char == 'l':
            single_char = str(correct_letter_verification_for_l(cropped_img))

        letter_check = ['O', 'C', 'S', 'W', 'J', 'V', 'Z', 'X', 'U', 'P', 'E',
                        'o', 'c', 's', 'w', 'v', 'z', 'x', 'u', 'p']
        if single_char in letter_check:
            if letter_verification_for_capital(cropped_img) == False:
                single_char = single_char.lower()
            else:
                # It's capital than.
                single_char = single_char.upper()

        if single_char == 'H':
            if correct_letter_verification_for_h(cropped_img) == False:
                single_char = 'n'

        if single_char == 'I':
            single_char = correct_letter_verification_for_i(cropped_img)

        if single_char == 'J':
            if correct_letter_verification_for_capital_j(cropped_img) == False:
                single_char = 'j'

        if single_char == 'D':
            single_char = correct_letter_verification_for_capital_d(cropped_img)

        if single_char == 'r':
            if correct_letter_verification_for_r(cropped_img) == False:
                single_char = 'i'

        if single_char in ['0', 'O']:

            if correct_letter_verification_for_0(cropped_img):
                single_char = '0'
            else:
                single_char = 'O'

        if single_char is None:
            full_text = None
            break

        full_text += single_char
        # print(single_char)
        # image_show(cropped_img)

    return full_text


def preprocessing_each_full_text(processed_img):
    """
    preprocesses the image to full text in a single go.
    [CAN BE IMPLEMENTED TO GET 100% accuracy when used with individual letter pre-processing]
    [ BUT WHEN IT implemented along with other its coverage is 26% only ]
    :param processed_img:
    :return:
    """
    full_text = pytesseract.image_to_string(processed_img,
                                            config="-oem -O -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -psm 6",
                                            lang="eng")
    return full_text


def captcha_to_text(image_path):
    """
    converts captcha to text. If no prediction returns none.

    :param image: takes in the image path
    :return:
    """
    loaded_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    processed_img = preprocess_image(loaded_img)

    processed_img, letter_edges = finding_edges_alphabet(processed_img)

    if len(letter_edges) == 6:
        full_text_method1 = preprocessing_each_alphabet(processed_img, letter_edges)

        return full_text_method1
    # if there are more than 6 or less than 6 letters, it returns none
    else:
        return None


def testing_images():
    dir_name = 'captcha_images_test_5'
    images = glob.glob(dir_name + "/*.png")

    for image in images:
        text = captcha_to_text(image)
        if text is None:
            print('refresh')
        else:
            print(text)


if __name__ == '__main__':
    testing_images()
