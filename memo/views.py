from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy

from .models import Bookmark


class BookmarkListView(ListView):
    model = Bookmark
    paginate_by = 10


def create_bookmark(request):
    return render(request, 'memo/bookmark_create.html')



def add_bookmark(request):
    if request.method == 'POST':
        bookmark = Bookmark()
        bookmark.site_name = request.POST['title']
        bookmark.author = request.user
        bookmark.url = "/third?theid=" + str(request.POST['pmc_id'])
        bookmark.save()
        message = 'created successful'
        return HttpResponse(message)





class BookmarkDetailView(DetailView):
    model = Bookmark


class BookmarkUpdateView(UpdateView):
    model = Bookmark
    fields = ['site_name', 'url']
    success_url = reverse_lazy('list')
    template_name_suffix = '_update'


class BookmarkDeleteView(DeleteView):
    model = Bookmark
    success_url = reverse_lazy('list')
