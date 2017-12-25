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

# Views Strategies

At the end of the day, all Django views are functions. Even class-based views (CBV). Behind the scenes, it does all the magic and ends up returning a view function.

Class-based views were introduced to make it easier for developers to reuse and extend views. There are many benefits of using them, such as the extendability, the ability to use O.O. techniques such as multiple inheritances, the handling of HTTP methods are done in separate methods, rather than using conditional branching, and there are also the Generic Class-Based Views (GCBV).

Before we move forward, let’s clarify what those three terms mean:

* **Function-Based Views** (FBV)
* **Class-Based Views** (CBV)
* **Generic Class-Based Views** (GCBV)

A **FBV** is the simplest representation of a Django view: it’s just a function that **receives an HttpRequest object and returns an HttpResponse**.

A **CBV** is every Django view defined as a Python class that extends the `django.views.generic.View` abstract class. A CBV essentially is a class that wraps a FBV. CBVs are great to extend and reuse code.

**GCBVs** are built-in CBVs that solve specific problems such as listing views, create, update, and delete views.


## Function-Based View (FBV)

`views.py`:
```py
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'new_post.html', {'form': form})
```

`urls.py`
```py
urlpatterns = [
    url(r'^new_post/$', views.new_post, name='new_post'),
]
```

## Class-Based View

A CBV is a view that extends the View class. The main difference here is that the requests are handled inside class methods named after the HTTP methods, such as get, post, put, head, etc.

So, here we don’t need to do a conditional to check if the request is a POST or if it’s a GET. The code goes straight to the right method. This logic is handled internally in the View class.

`views.py`:
```py
from django.views.generic import View

class NewPostView(View):
    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post-list')
        return render(request, 'new_post.html', {'form': form})

    def get(self, request):
        form = PostForm()
        return render(request, 'new_post.html', {'form': form})
```

The way we refer to the CBVs in the **urls.py** module is a bit different:

`urls.py`:
```py
urlpatterns = [
    url(r'^new_post/$', views.NewPostView.as_view(), name='new_post'),
]
```

Here we need to use the `as_view()` class method, which returns a view function to the url patterns. In some cases, we can also feed the `as_view()` with some keyword arguments, so to customize the behavior of the CBV.

The good thing about CBV is that we can add more methods, and perhaps do something like this:

```py
from django.views.generic import View

class NewPostView(View):
    def render(self, request):
        return render(request, 'new_post.html', {'form': self.form})

    def post(self, request):
        self.form = PostForm(request.POST)
        if self.form.is_valid():
            self.form.save()
            return redirect('post-list')
        return self.render(request)

    def get(self, request):
        form = PostForm()
        return render(request)
```

It’s also possible to create some generic views that accomplish some tasks so that we can reuse it across the project.

That’s pretty much all we need to know about CBVs. Simple as that.

## Generic Class-Based View

Now about the GCBV. That’s a different story. As I mentioned earlier, those views are built-in CBVs for common use cases. Their implementation makes heavy usage of multiple inheritances (mixins) and other O.O. strategies.

They are very flexible and can save many hours of work. But in the beginning, it can be difficult to work with them.

At first, it’s hard to tell what is going on, because the code flow is not obvious, as there is good chunk of code hidden in the parent classes. The documentation is a little bit challenging to follow too, mostly because the attributes and methods are sometimes spread across eight parent classes. When working with GCBV, it’s always good to have the ccbv.co.uk opened for quick reference. No worries, we are going to explore it together.

Let’s see a GCBV example.

`views.py`:
```py
from django.views.generic import CreateView

class NewPostView(CreateView):
    model = Post
    form_class = PostForm
    sucess_url = reverse_lazy('post_list')
    template_name = 'new_post.html'
```

Here we are using a generic view used to create model objects. It does all the form processing and save the object if the form is valid.

Since it’s a CBV, we refer to it in the **urls.py** the same way as any other CBV:

`urls.py`:
```py
urlpatterns = [
    url(r'^new_post/$', views.NewPostView.as_view(), name='new_post'),
]
```

Other examples of GCBVs are :
* **DetailView** 
* **DeleteView** 
* **FormView** 
* **UpdateView** 
* **ListView**

### Update View
Let's use a GCBV to implement the **edit post** view:

`boards/views.py`

```py
# ...
from django.views.generic import UpdateView
from django.utils import timezone

class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)
```

With the **UpdateView** and the **CreateView**, we have the option to either define **form_class** or the **fields** attribute. In the example above we are using the **fields** attribute to create a model form on-the-fly. Internally, Django will use a model form factory to compose a form of the **Post** model. Since it’s a very simple form with just the message field, we can afford to work like this. But for complex form definitions, it’s better to define a model form externally and refer to it here.

The `pk_url_kwarg` will be used to identify the name of the keyword argument used to retrieve the Post object. **It’s the same as we define in the urls.py**.

If we don’t set the `context_object_name` attribute, the Post object will be available in the template as `object.`. So, here we are using the `context_object_name` to rename it to `post` instead. You will see how we are using it in the template below.

In this particular example, we had to override the  `form_valid()` method and set some extra fields such as the `updated_by` and `updated_at`. You can see what the base `form_valid()` method looks like here: [UpdateView#form_valid](https://ccbv.co.uk/projects/Django/1.11/django.views.generic.edit/UpdateView/#form_valid).

`myproject/urls.py`:
```py
from django.conf.urls import url
from boards import views

urlpatterns = [
    # ...
    url(r'^boards/(?P<pk>\d+)/topics/(?P<topic_pk>\d+)/posts/(?P<post_pk>\d+)/edit/$',
        views.PostUpdateView.as_view(), name='edit_post'),
]
```

And now we can add the link to the edit page:

`templates/topic_posts.html`:
```html
<!-- ... -->
{% if post.created_by == user %}
  <div class="mt-3">
    <a href="{% url 'edit_post' post.topic.board.pk post.topic.pk post.pk %}"
       class="btn btn-primary btn-sm"
       role="button">Edit</a>
  </div>
{% endif %}
<!-- ... -->
```

`templates/edit_post.html`
```html
{% extends 'base.html' %}

{% block title %}Edit post{% endblock %}

{% block breadcrumb %}
  <li class="breadcrumb-item"><a href="{% url 'home' %}">Boards</a></li>
  <li class="breadcrumb-item"><a href="{% url 'board_topics' post.topic.board.pk %}">{{ post.topic.board.name }}</a></li>
  <li class="breadcrumb-item"><a href="{% url 'topic_posts' post.topic.board.pk post.topic.pk %}">{{ post.topic.subject }}</a></li>
  <li class="breadcrumb-item active">Edit post</li>
{% endblock breadcrumb %}

{% block content %}
  <form method="post" class="mb-4" novalidate>
    {% csrf_token %}
    {% include 'includes/form.html' %}
    <button type="submit" class="btn btn-success">Save changes</button>
    <a href="{% url 'topic_posts' post.topic.board.pk post.topic.pk %}" class="btn btn-outline-secondary" role="button">Cancel</a>
  </form>
{% endblock content %}

```

Observe now how we are navigating through the post object: `post.topic.board.pk`. If we didn’t set the `context_object_name` to **post**, it would be available as: `object.topic.board.pk`.


# Pagination

`python manage.py shell`

```py
from boards.models import Topic

# All the topics in the app
Topic.objects.count()
107

# Just the topics in the Django board
Topic.objects.filter(board__name='Django').count()
104

# Let's save this queryset into a variable to paginate it
queryset = Topic.objects.filter(board__name='Django').order_by('-last_updated')
```

It’s very important always define an ordering to a QuerySet you are going to paginate! Otherwise, it can give you inconsistent results.

Now let’s import the Paginator utility

```py
from django.core.paginator import Paginator

paginator = Paginator(queryset, 20)
```
Here we are telling Django to paginate our QuerySet in pages of 20 each. Now let’s explore some of the paginator properties:

```py
# count the number of elements in the paginator
paginator.count
104

# total number of pages
# 104 elements, paginating 20 per page gives you 6 pages
# where the last page will have only 4 elements
paginator.num_pages
6

# range of pages that can be used to iterate and create the
# links to the pages in the template
paginator.page_range
range(1, 7)

# returns a Page instance
paginator.page(2)
<Page 2 of 6>

page = paginator.page(2)

type(page)
django.core.paginator.Page

type(paginator)
django.core.paginator.Paginator
```

Here we have to pay attention because if we try to get a page that doesn’t exist, the Paginator will throw an exception:

```py
paginator.page(7)
EmptyPage: That page contains no results
```

Or if we try to pass an arbitrary parameter, which is not a page number:

```py
paginator.page('abc')
PageNotAnInteger: That page number is not an integer
```

We have to keep those details in mind when designing the user interface.

Now let’s explore the attributes and methods offered by the Page class a little bit:

```py
page = paginator.page(1)

# Check if there is another page after this one
page.has_next()
True

# If there is no previous page, that means this one is the first page
page.has_previous()
False

page.has_other_pages()
True

page.next_page_number()
2

# Take care here, since there is no previous page,
# if we call the method `previous_page_number() we will get an exception:
page.previous_page_number()
EmptyPage: That page number is less than 1
```