from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
import markdown2
import random
from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    content = util.get_entry(title)

    if content is None:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "error": "Entry not found."
        })

    html = markdown2.markdown(content)

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html
    })


def search(request):
    query = request.GET.get("q", "")
    entries = util.list_entries()
    if query in entries:
        return entry(request, query)
    else:
        results = [entry for entry in entries if query.lower() in entry.lower()]
        return render(request, "encyclopedia/search.html", {
            "query": query,
            "results": results
        })


def create(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        if not title or not content:
            return render(request, "encyclopedia/create.html", {
                "error": "Title and content cannot be empty."
            })
        if util.get_entry(title):
            return render(request, "encyclopedia/create.html", {
                "error": "An entry with this title already exists."
            })
        util.save_entry(title, content)
        return redirect(reverse("index"))
    return render(request, "encyclopedia/create.html")


class EditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": 20}))

def edit_page(request, title):
    content = util.get_entry(title)

    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "Page not found."
        })

    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            util.save_entry(title, form.cleaned_data["content"])
            return redirect("entry", title=title)
    else:
        form = EditForm(initial={"content": content})

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": form
    })


def random_page(request):
    entries = util.list_entries()
    title = random.choice(entries)
    return redirect("entry", title=title)