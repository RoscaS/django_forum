# Links

* [googleFonts](https://fonts.google.com/?selection.family=Dancing+Script)

# Divers

## get_object_or_404

```py
# ...
from django.http import Http404

def board_topics(request, pk):
    try:
        board = Board.objects.get(pk=pk)
    except Board.DoesNotExist:
        raise Http404
    return render(request, 'topics.html', {'board': board})
```

That's a very common use case, Django hs a shortcut to try to get an object, or return a 404 if the object does not exist:

```py
# ...
from django.shortcuts import render, get_object_or_404

def board_topics(request, pk):
    board = get_object_or_404(board, pk=pk)
    return render(request, 'topics.html', {'board': board})
```




# Summary of model's operations

Using the **Board** model as a reference. Uppercase **Board** refers to the class, lowercase **board** refere to an instance of the **Board** model class:

* `board = Board()`: Create an object without saving
* `board.save()`: Save an object (create or update)
* `Board.objects.create(name='...', description='...')`: Create and save an object in the database
* `Board.objects.all()` : List all objects
* `Board.objects.get(field = value)` Get a single object identified by a field


# Dynamic Urls

`url(r'^boards/(?P<pk>\d+)/$', views.board_topics, name='board_topics')`

* `\d+`: Will match an integer of arbitrary size. It will be used to retrieve the **Board** from the database
* `(?P<pk>\d+)` This is telling to Django to capture the value into a keyword argument named `pk`

Here is how we write a view that will use `pk`:

```py
def board_topics(request, pk):
    # code...
```

>PK or ID?
>
>PK stands for Primary Key. It's a shortcut for accessing a model's primary key. All Django models >have this attribute.
>
>For the most cases, using the pk property is the same as id. That's because if we don't define a >primary key for a model, Django will automatically create an AutoField named id, which will be its >primary key.
>
>If you defined a different primary key for a model, for example, let's say the field email is your >primary key. To access it you could either use obj.email or obj.pk. 

## List of useful URL patterns

### Primary key AutoField

* Regex: `(?P<pk>\d+)`
* Example: `url(r'^questions/(?P<pk>\d+)/$', views.question, name='question')`
* Valid URL: `/questions/934/`
* Captures: `{'pk': '934'}`

### Slug Field

* Regex: `(?P<slug>[-\w]+)`
* Example: `url(r'^posts/(?P<slug>[-\w]+)/$', views.post, name='post')`
* Valid URL: `/posts/hello-world/`
* Captures: `{'slug': 'hello-world'}`

### Slug Field with Primary Key

* Regex: `(?P<slug>[-\w]+)-(?P<pk>\d+)`
* Example: `url(r'^blog/(?P<slug>[-\w]+)-(?P<pk>\d+)/$', views.blog_post, name='blog_post')`
* Valid URL: `/blog/hello-world-159/`
* Captures: `{'slug': 'hello-world', 'pk': '159'}`

### Django User Username

* Regex: `{'slug': 'hello-world', 'pk': '159'}`
* Example: `url(r'^profile/(?P<username>[\w.@+-]+)/$', views.user_profile, name='user_profile')`
* Valid URL: `/profile/vitorfs/`
* Captures: `{'username': 'vitorfs'}`

### Year

* Regex: `(?P<year>[0-9]{4})`
* Example: `url(r'^articles/(?P<year>[0-9]{4})/$', views.year_archive, name='year')`
* Valid URL: `/articles/2016/`
* Captures: `{'year': '2016'}`

### Year / month

* Regex: `(?P<year>[0-9]{4})/(?P<month>[0-9]{2})`
* Example: `url(r'^articles/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', views.month_archive, name='month')`
* Valid URL: `/articles/2016/01/`
* Captures: `{'year': '2016', 'month': '01'}`

[List of Useful URL Patterns](https://simpleisbetterthancomplex.com/references/2016/10/10/url-patterns.html)