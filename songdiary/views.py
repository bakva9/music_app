from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Project, Memo
from .forms import ProjectForm


@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user)
    status_filter = request.GET.get('status', '')
    if status_filter:
        projects = projects.filter(status=status_filter)
    return render(request, 'songdiary/project_list.html', {
        'projects': projects,
        'current_status': status_filter,
        'status_choices': Project.STATUS_CHOICES,
    })


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect('songdiary:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'songdiary/project_form.html', {'form': form, 'is_edit': False})


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('songdiary:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'songdiary/project_form.html', {'form': form, 'is_edit': True, 'project': project})


def project_share(request, token):
    project = get_object_or_404(
        Project.objects.prefetch_related('memos'),
        share_token=token
    )
    return render(request, 'songdiary/project_share.html', {'project': project})


@login_required
def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.prefetch_related('memos'),
        pk=pk, user=request.user
    )
    return render(request, 'songdiary/project_detail.html', {'project': project})


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST':
        project.delete()
        return redirect('songdiary:project_list')
    return render(request, 'songdiary/project_confirm_delete.html', {'project': project})


@login_required
def add_text_memo(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST':
        text = request.POST.get('text_content', '').strip()
        if text:
            Memo.objects.create(project=project, memo_type='text', text_content=text)
    if request.headers.get('HX-Request'):
        return render(request, 'songdiary/_timeline.html', {'project': project})
    return redirect('songdiary:project_detail', pk=pk)


@login_required
def add_audio_memo(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST' and request.FILES.get('audio_file'):
        Memo.objects.create(
            project=project,
            memo_type='audio',
            audio_file=request.FILES['audio_file'],
        )
    if request.headers.get('HX-Request'):
        return render(request, 'songdiary/_timeline.html', {'project': project})
    return redirect('songdiary:project_detail', pk=pk)


@login_required
def add_photo_memo(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST' and request.FILES.get('photo_file'):
        Memo.objects.create(
            project=project,
            memo_type='photo',
            photo_file=request.FILES['photo_file'],
        )
    if request.headers.get('HX-Request'):
        return render(request, 'songdiary/_timeline.html', {'project': project})
    return redirect('songdiary:project_detail', pk=pk)


@login_required
def edit_memo(request, pk, memo_pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    memo = get_object_or_404(Memo, pk=memo_pk, project=project, memo_type='text')
    if request.method == 'POST':
        text = request.POST.get('text_content', '').strip()
        if text:
            memo.text_content = text
            memo.save()
    if request.headers.get('HX-Request'):
        return render(request, 'songdiary/_timeline.html', {'project': project})
    return redirect('songdiary:project_detail', pk=pk)


@login_required
def delete_memo(request, pk, memo_pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    Memo.objects.filter(pk=memo_pk, project=project).delete()
    if request.headers.get('HX-Request'):
        return render(request, 'songdiary/_timeline.html', {'project': project})
    return redirect('songdiary:project_detail', pk=pk)
