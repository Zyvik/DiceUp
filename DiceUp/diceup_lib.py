from math import floor, ceil
from PIL import Image
from django.contrib.staticfiles import finders
from diceup_project import settings
import os


class DiceUpImage:

    def __init__(self, image, slider_value, model, max_size_in_mb):
        self.image = Image.open(image)
        self.resolution = slider_value
        self.model = model
        self.width = 0  # width of image in dice - its calculated in calculate_dimensions_in_dice
        self.height = 0  # height of image in dice
        self.max_size_in_mb = max_size_in_mb

    def calculate_dimensions_in_dice(self):
        """calculate dimensions in dice if resolution (range slider) value is valid.
        (ex: height = 20 dice, width = 10 dice, so 200 dice needed to create image) """
        try:
            self.resolution = abs(int(self.resolution))
        except (TypeError, ZeroDivisionError):
            self.resolution = 2

        if self.resolution > 0:
            self.width = floor(self.image.size[0] / self.resolution)  # width of image in dice
            self.height = floor(self.image.size[1] / self.resolution)  # height of image in dice

    def get_error_message(self):
        """Verifies image, returns error message, ret. None when valid. Delete() also removes image from server"""
        org_image_path = settings.MEDIA_ROOT + '/' + self.model.original_picture.name
        if os.stat(org_image_path).st_size > self.max_size_in_mb * 1048576:
            message = f'File is too large - max is {self.max_size_in_mb} MB'
            self.model.delete()
            return message

        if self.image.size[0] * self.image.size[1] > 1920 * 1080:
            message = 'Too many pixels - max resolution is 1920x1080.'
            self.model.delete()
            return message

        self.calculate_dimensions_in_dice()

        if self.width < 1 or self.height < 1:
            self.model.delete()
            message = 'Picture you provided is too small for this quality - upload ' \
                      'different picture, or choose better quality.'
            return message
        return None


def load_dice():
    """loads images of dice (right now images are 50x50 pixels)"""
    dice_list = []
    for n in range(1, 7):
        dice_list.append(Image.open(finders.find(f'DiceUp/Alea_{n}.png')))
    return dice_list


def get_lower_resolution(dice_up_image):
    """Lowers resolution of original image and returns pixels' values in list.
    I know it looks terrible and now that I think about it I should've used PIL function... well...
    Despite 4(!!!!) nested loops each pixel is visited only once.
    """
    lower_resolution_list = []

    # big loop - whole image
    current_height = 0
    while current_height < dice_up_image.height:
        current_width = 0
        while current_width < dice_up_image.width:
            # small loop - square of pixels that will be averaged to one value
            sum1 = 0
            y = 0  # local y coordinate in small square
            while y < dice_up_image.resolution:
                x = 0  # local x coordinate in small square
                while x < dice_up_image.resolution:
                    sum1 = sum1 + dice_up_image.image.getpixel(
                        (dice_up_image.resolution * current_width + x, current_height * dice_up_image.resolution + y))
                    x += 1
                y += 1
            current_width += 1
            average = int(sum1) / (dice_up_image.resolution * dice_up_image.resolution)
            lower_resolution_list.append(average)
        current_height += 1
    return lower_resolution_list


def calculate_ranges(lower_resolution_list):
    """Calculates values of ranges that will be used to determine which die to paste in place of each pixel.
    Ex: pixel value is in range (0,10) - paste die nr 6; pixel val is in range (11, 50) paste die nr 5 etc.
    """
    maximum_pixel_val = max(lower_resolution_list)
    interval = (maximum_pixel_val - min(lower_resolution_list)) / 6  # calculates value of constant compartments
    compartments_list = []

    upper_band = ceil(maximum_pixel_val)
    for n in range(1,7):
        lower_band = int(maximum_pixel_val - interval*n)
        compartments_list.append((lower_band, upper_band))
        upper_band = lower_band
    return compartments_list


def create_results(dice_up_image, interval_list, lower_resolution_list, dice_list):
    """Creates result image and instruction string"""
    size = 50  # dimension of dice image (they are square)
    instruction = ''
    result_image = Image.new('L', (size * dice_up_image.width, size * dice_up_image.height), 0)  # creates new image
    y = 0
    while y < dice_up_image.height:
        x = 0
        while x < dice_up_image.width:
            for n, interval in enumerate(interval_list):
                # finds dice for each pixel and pastes it on result image
                if ceil(lower_resolution_list[y * dice_up_image.width + x]) in range(interval[0], interval[1]+1):
                    result_image.paste(dice_list[n], (size * x, size * y))
                    instruction += str(n+1)
                    break
            x += 1
        y += 1
        instruction += '|\n'

    return result_image, instruction


def create_instruction_file(instruction_string, dice_up_image):
    instruction_path = os.path.abspath(settings.MEDIA_ROOT + '/DiceUp/'
                                       + str(dice_up_image.model.pk) + 'instruction.txt')
    instruction = open(instruction_path, 'w')

    instruction.write(
        'Dice needed: ' + str(dice_up_image.width * dice_up_image.height) + ' - '
        + str(dice_up_image.width) + 'x' + str(dice_up_image.height) + ' [dice] \n')
    instruction.write('Estimated dimensions: ' + str(8 * dice_up_image.width / 10) + 'x' +
                      str(8 * dice_up_image.height / 10) + ' [cm] - regular die width is 8mm\n')
    instruction.write('INSTRUCTIONS - from left to right, top to bottom\n')
    instruction.write(instruction_string)
    instruction.close()

