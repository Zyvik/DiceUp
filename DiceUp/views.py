from django.shortcuts import render
from .forms import DiceUpForm
from django.views import View
from .models import DiceUpModel
from PIL import Image
from django.contrib.staticfiles import finders
import os, django.dispatch

from math import *


# example site
def example(request):
    return render(request, 'DiceUp/example.html')


delete_object = django.dispatch.Signal(providing_args=["object"])


class HomeView(View):
    form_temp = DiceUpForm

    def get(self, request):
        return render(request, 'DiceUp/home.html', {'form': self.form_temp})

    def post(self, request):
        form = self.form_temp(request.POST, request.FILES)
        message = 'Uploaded file has to be 200KB or smaller image.'  # message won't be displayed if everything is ok
        if form.is_valid():
            picture = request.FILES['original_picture']
            res = abs(int(request.POST['range'])) # resolution of "dice pixel" (less = more dice -> better resolution)
            # abs because I dont want any negativity in my View (slider is -8 to -2 )
            im = Image.open(picture).convert('L')
            width = floor(im.size[0] / res)  # width of picture in dice
            height = floor(im.size[1] / res)  # height of picture in dice
            model = DiceUpModel(original_picture=picture)
            model.save()

            if im.size[0]*im.size[1] > 1920 * 1080:
                message = 'Too many pixels - max resolution is 1920x1080.'
                model.delete()
                return render(request, 'DiceUp/home.html', {'form': self.form_temp, 'message': message})

            if width < 1 or height < 1:
                model.delete()
                message = 'Picture you provided is too small for this quality - upload different picture, or choose better quality.'
                return render(request, 'DiceUp/home.html', {'form': self.form_temp, 'message': message})

            d_im = []  # table with average bands of "dice pixels"
            d_ins = []  # table for instructions

            # loads images of dice ( right now images are 50x50 pixels):
            d1 = Image.open(os.path.abspath('DiceUp/static/DiceUp/Alea_1.png'))
            d2 = Image.open(finders.find('DiceUp/Alea_2.png'))
            d3 = Image.open(finders.find('DiceUp/Alea_3.png'))
            d4 = Image.open(finders.find('DiceUp/Alea_4.png'))
            d5 = Image.open(finders.find('DiceUp/Alea_5.png'))
            d6 = Image.open(finders.find('DiceUp/Alea_6.png'))

            size = 50  # size of d1-d6 in pixels (d1-6 are squares)

            # fills table with average bands of "dice pixels"
            k = 0
            while k < height:
                i = 0
                while i < width:
                    sum1 = 0
                    y = 0
                    while y < res:
                        x = 0
                        while x < res:
                            sum1 = sum1 + im.getpixel((res * i + x, k * res + y))
                            x = x + 1
                        y = y + 1
                    i = i + 1
                    avg = int(sum1) / (res * res)
                    d_im.append(avg)
                k = k + 1

            comp = (max(d_im) - min(d_im)) / 6  # calculates value of constant compartments
            #  calculates value of compartments that will be used to determine which die to paste (lower - darker)
            a_d1 = max(d_im) - comp * 0
            a_d2 = max(d_im) - comp * 1
            a_d3 = max(d_im) - comp * 2
            a_d4 = max(d_im) - comp * 3
            a_d5 = max(d_im) - comp * 4
            a_d6 = max(d_im) - comp * 5

            dice_im = Image.new('L', (size * width, size * height), 0)  # creates new, black image

            #  edits image by pasting images of adequate die to corresponding place
            y = 0
            i = 0
            while y < height:
                x = 0
                while x < width:
                    if a_d1 >= d_im[i] > a_d2:
                        dice_im.paste(d1, (size * x, size * y))
                        d_ins.append(1)
                    elif a_d2 >= d_im[i] > a_d3:
                        dice_im.paste(d2, (size * x, size * y))
                        d_ins.append(2)
                    elif a_d3 >= d_im[i] > a_d4:
                        dice_im.paste(d3, (size * x, size * y))
                        d_ins.append(3)
                    elif a_d4 >= d_im[i] > a_d5:
                        dice_im.paste(d4, (size * x, size * y))
                        d_ins.append(4)
                    elif a_d5 >= d_im[i] > a_d6:
                        dice_im.paste(d5, (size * x, size * y))
                        d_ins.append(5)
                    else:
                        dice_im.paste(d6, (size * x, size * y))
                        d_ins.append(6)
                    x = x + 1
                    i = i + 1
                y = y + 1

            dice_im.save('media/DiceUp/' + str(model.pk)+'DiceUpPic.png')
            image_path = os.path.abspath('media/DiceUp/' + str(model.pk)+'DiceUpPic.png')

            #  creates text file with instructions
            instruction_path = os.path.abspath('media/DiceUp/'+str(model.pk)+'instruction.txt')
            instruction = open(instruction_path, 'w')

            instruction.write(
                'Dice needed: ' + str(width * height) + ' - ' + str(width) + 'x' + str(height) + ' [dice] \n')
            instruction.write('Estimated dimensions: ' + str(8 * width / 10) + 'x' + str(
                8 * height / 10) + ' [cm] - regular die width is 8mm\n')
            instruction.write('INSTRUCTIONS - from left to right, top to bottom\n')

            y = 0
            while y < height:
                x = 0
                while x < width:
                    instruction.write(str(d_ins[y * width + x]))
                    instruction.write(' ')
                    if x == width - 1:
                        instruction.write('|\n')
                    x = x + 1
                y = y + 1

            # save image and instruction to model
            im = open(image_path, 'rb')
            ins = open(instruction_path, 'rb')

            model.dice_picture.name = 'DiceUp/' + str(model.pk)+'DiceUpPic.png'
            model.instruction.name = 'DiceUp/'+str(model.pk)+'instruction.txt'
            model.save()

            # del im, ins, dice_im, picture
            # t = threading.Thread(target=delete_after, name='thread1', args=(model.pk,))
            # t.start()

            dice = height * width  # number of dice needed

            return render(request, 'DiceUp/success.html', {'picture': model, 'quality': res, 'dice': dice})
        return render(request, 'DiceUp/home.html', {'form': self.form_temp, 'message': message})

# @receiver(delete_object)
# def handle_delete_object(sender,model,**kwargs):
#     time.sleep(5)
#     model.delete()

# def delete_after(pk):
#     model = DiceUpModel.objects.get(pk=pk)
#     time.sleep(60)
#     model.delete()
