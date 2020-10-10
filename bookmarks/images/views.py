from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST

from common.decorators import ajax_required
from .models import Image
from .forms import ImageCreateForm


@login_required
def image_create(request):
    if request.method == 'POST':
        # форма отправлена
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # данные формы действительны
            cd = form.cleaned_data
            new_item = form.save(commit=False)

            # назначить текущего пользователя item
            new_item.user = request.user
            new_item.save()
            messages.success(request, 'Image added successfully')

            # перенаправить на detail view нового созданного элемента
            return redirect(new_item.get_absolute_url())
    else:
        # создать форму с данными, предоставленными букмарклетом через GET
        form = ImageCreateForm(data=request.GET)

    return render(request,
                  'images/image/create.html',
                  {'section': 'images',
                   'form': form})


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    return render(request,
                  'images/image/detail.html',
                  {'section': 'images',
                   'image': image})


@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # Если page не является целым числом, показать первую страницу
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # Если запрос был AJAX и страница вне допустимого диапазона
            # вернуть пустую страницу
            return HttpResponse('')
        # Если страница выходит за пределы допустимого диапазона, показать последнюю страницу результатов
        images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request, 'images/image/list_ajax.html',
                      {'section': 'images', 'images': images})
    return render(request, 'images/image/list.html',
                  {'section': 'images', 'images': images})
