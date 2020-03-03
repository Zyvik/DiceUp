from django.shortcuts import render
from django.views import View
import django.dispatch
from diceup_project import settings

from .forms import DiceUpForm
from .models import DiceUpModel
from .diceup_lib import DiceUpImage, load_dice, get_lower_resolution, calculate_ranges, create_results, \
    create_instruction_file


# example site
def example(request):
    return render(request, 'DiceUp/example.html')


delete_object = django.dispatch.Signal(providing_args=["object"])


class HomeView(View):
    form_temp = DiceUpForm
    max_size = 1  # max image size in mb
    def get(self, request):
        return render(request, 'DiceUp/home.html', {'form': self.form_temp, 'max_size': self.max_size})

    def post(self, request):
        form = self.form_temp(request.POST, request.FILES)
        message = 'Provided file has to be image...'
        if form.is_valid():
            model = DiceUpModel(original_picture=request.FILES['original_picture'])
            model.save()  # saves picture to database so it can be easily deleted if its too small or too bi

            #  DiceUpImage(picture, slider value, db_model_instance, max image size in MB)
            dice_up_image = DiceUpImage(request.FILES['original_picture'], request.POST['range'], model, self.max_size)

            # checks image's dimensions and size
            message = dice_up_image.get_error_message()
            if message:
                return render(request, 'DiceUp/home.html', {'form': self.form_temp, 'message': message, 'max_size': self.max_size})

            dice_up_image.image = dice_up_image.image.convert('L')  # converts original image to grayscale
            lower_resolution_list = get_lower_resolution(dice_up_image)  # lowers resolution and returns val in list
            dice_list = load_dice()  # loads images of dice and returns them in list
            range_list = calculate_ranges(lower_resolution_list)  # calculates range of pixel val for each dice picture

            # creates and saves result image and instruction
            result_path = settings.MEDIA_ROOT + '/DiceUp/results/'
            result_image, instruction = create_results(dice_up_image, range_list, lower_resolution_list, dice_list)
            result_image.save(f'{result_path}{str(model.pk)}DiceUpPic.png')  # saves result image (png file)
            create_instruction_file(instruction, dice_up_image)  # saves instruction (txt file)

            # links result image and instruction to model
            model.dice_picture.name = f'{result_path}{str(model.pk)}DiceUpPic.png'
            model.instruction.name = f'{result_path}{str(model.pk)}instruction.txt'
            model.save()

            dice_needed = dice_up_image.height * dice_up_image.width  # number of dice needed to create image irl
            return render(request, 'DiceUp/success.html', {'picture': model, 'dice': dice_needed})
        return render(request, 'DiceUp/home.html', {'form': self.form_temp, 'message': message, 'max_size': self.max_size})
