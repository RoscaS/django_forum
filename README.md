# Links

* [googleFonts](https://fonts.google.com/?selection.family=Dancing+Script)

# Divers


## django_extensions

* [More](https://django-extensions.readthedocs.io/en/latest/shell_plus.html#interactive-python-shells)

```
pip install django_extensions
```

```
INSTALLED_APPS = (
     ....
    'django_extensions'
)
```

Activate Ipython shell
```
python manage.py shell_plus
```

Encore mieux:
```
pip install 'ipython[notebook]'
python manage.py shell_plus --notebook
```



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

# Migration

>Migration is a fundamental part of Web development with Django. It’s how we evolve our application’s models keeping the models’ files synchronized with the database.

* `python manage.py makemigrations` : Create the database/regenerate db
* `python manage.py migrate` : apply the migration we generated to the database

When we first run the command `python manage.py migrate` Django grab all migration files and generate the database schema.

When Django applies a migration, it has a special table called django_migrations. In this table, Django registers all the applied migrations.

So if we try to run the command again, Django will know there’s nothing to do.
<br>
If we want to add a new field to a model we have to use `python manage.py makemigrations` after adding the code in the model. The `makemigrations` command will automatically generate a file that looks like that : `XXXX_tableName_modificationName.py` which will be used to modify the database adding the new field.

To apply the migration we're using `python manage.py migrate`


# Some model's operations

Using the **Board** model as a reference. Uppercase **Board** refers to the class, lowercase **board** refere to an instance of the **Board** model class:

* `board = Board()`: Create an object without saving
* `board.save()`: Save an object (create or update)
* `Board.objects.create(name='...', description='...')`: Create and save an object in the database
* `Board.objects.all()` : List all objects
* `Board.objects.get(field = value)` Get a single object identified by a field



## A bit more complicated querys

* **Getting the current topics count:**

```py
>>> board = Board.objects.get(name='Django')
>>> board.topics.all()

<QuerySet [<Topic: My first topic>, <Topic: Another one>, <Topic: J'aime la viande>, <Topic: La lune>, <Topic: Blanche comme neige>, <Topic: J'aime la viande fraiche !!!>, <Topic: Une route une fourchette>]>
>>> board.topics.all().count()

7
```

* **The number of posts within a board is a little bit trickier because Post is not directly related to Board**

```py
>>> from boards.models import Post
>>> Post.objects.all()
>>>
<QuerySet [<Post: La pie niche haut, l'oie ni...>, <Post: Bacon ipsum dolor amet beef...>, <Post: Pork chop pancetta chuck, b...>, <Post: Grande et belle, elle est p...>, <Post: De son prénom bien aimé par...>, <Post: Owiiiiiii viens, viens, on ...>, <Post: Je t'aime mon coeur!>, <Post: Oui, oui, bacon ipsum lolil...>, <Post: Moi aussi ma chache !>, <Post: Getting there, what about you?>, <Post: So far so good>]>
>>> Post.objects.count()

11
```

* **Here we have 11 posts. But not all of them belongs to the “Django” board. Here is how we can filter it:**

```py
>>> from boards.models import Board, Post
>>> board = Board.objects.get(name='Django')
>>> Post.objects.filter(topic__board=board)

<QuerySet [<Post: La pie niche haut, l'oie ni...>, <Post: Je t'aime mon coeur!>, <Post: Moi aussi ma chache !>, <Post: Bacon ipsum dolor amet beef...>, <Post: Oui, oui, bacon ipsum lolil...>, <Post: Pork chop pancetta chuck, b...>, <Post: Grande et belle, elle est p...>, <Post: De son prénom bien aimé par...>, <Post: Owiiiiiii viens, viens, on ...>]>

>>> Post.objects.filter(topic__board=board).count()
9
```
The double underscores `topic__board` is used to navigate through the models’ relationships. Under the hoods, Django builds the bridge between the Board - Topic - Post, and build a SQL query to retrieve just the posts that belong to a specific board.

* **Identify last posted post Order by the `created_at` field, is getting the most recent first:**

```py
>>> Post.objects.filter(topic__board=board).order_by('-created_at')

<QuerySet [<Post: Moi aussi ma chache !>, <Post: Oui, oui, bacon ipsum lolil...>, <Post: Je t'aime mon coeur!>, <Post: Owiiiiiii viens, viens, on ...>, <Post: De son prénom bien aimé par...>, <Post: Grande et belle, elle est p...>, <Post: Pork chop pancetta chuck, b...>, <Post: Bacon ipsum dolor amet beef...>, <Post: La pie niche haut, l'oie ni...>]>
```

We can use the first() method to just grab the result that interest us

```py
>>> Post.objects.filter(topic__board=board).order_by('-created_at').first()
<Post: Moi aussi ma chache !>
```

* **Implementation**

```py
class Board(models.Model):
    name        = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
#   topics      = Topic[0..*]

    def __str__(self):
        return self.name

    def get_posts_count(self):
        return Post.objects.filter(topic__board=self).count()

    def get_last_post(self):
        return Post.objects.filter(topic__board=self).order_by('-created_at').first()
```

>Note that we are using `self`, because **this method will be used by a Board instance**. So that means we are using this instance to filter the QuerySet.

* **More efficient way**

```py
from django.db.models import Count
from boards.models import Board

board = Board.objects.get(name='Django')

topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts'))

for topic in topics:
    print(topic.replies)

2
4
2
1
```

Here we are using the `annotate` **QuerySet** method to generate a new "column" on the fly. This new column, which will be translated into a property, accessible via topic.replies contain the count of posts a given topic has.

We can do just a minor fix because the replies should not consider the starter topic (which is also a Post instance).

So here is how we do it:

```py
topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)

for topic in topics:
    print(topic.replies)

1
3
1
0
```



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

# Template filters

`myproject > templatetags > form_tags.py`

```py
from django import template

register = template.Library()

@register.filter
def field_type(bound_field):
    return bound_field.field.widget.__class__.__name__

@register.filter
def input_class(bound_field):
    css_class = ''
    if bound_field.form.is_bound:
        if bound_field.errors:
            css_class = 'is-invalid'
        elif field_type(bound_field) != 'PasswordInput':
            css_class = 'is-valid'
    return 'form-control {}'.format(css_class)
```

First, we load it in a template as we do with the `widget_tweaks` or `static` template tags. Note that after creating this file, we have to manually stop the development server and start it again so Django can identify the new template tags.

```html
{% load form_tags %}
```

Then we can use them in a template:

```html
{{ form.username|field_type}}
```

It will return:

```
'TextInput'
```

Or in case of the `input_class`:

```html
{{ form.username|input_class }}

<!-- if the form is not bound, it will simply return: -->
'form-control '

<!-- if the form is bound and valid: -->
'form-control is-valid'

<!-- if the form is bound and invalid: -->
'form-control is-invalid'
```