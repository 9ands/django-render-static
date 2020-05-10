# Django Render Static
### A simple static site renderer for django projects using vanilla urlpatterns

This method is a good starting point if you are looking for a "base" functionality. It is easy to understand and adapt for your own projects.

Please note, this isn't a Python package yet. It is a Django app that can be "installed" by placing `render_static` to the project base directory.

`requests` is required.

`urls.py` must have `app_name` declared.

Tested with django 3.0.5.


## `Settings.py`

Add to `INSTALLED_APPS`: `'render_static.apps.RenderStaticConfig',`

`RENDER_STATIC_ROOT = os.path.join(BASE_DIR, "rendered")`

`RENDER_STATIC_APPS = ['appname',]`

`RENDER_STATIC_HOST = '127.0.0.1:8000'`

`ALLOWED_HOSTS = ['localhost', '127.0.0.1']`

## `Views.py`

Add `{viewname}_objects` variable to `views.py` pointing to the queryset.

For example:

```python
# urls.py ---------------------------------------------------------------------

app_name = 'music'

urlpatterns = [
    path('<slug:slug>/',
        views.album_view,
        name='album_view'),
]
        
# -----------------------------------------------------------------------------


# views.py --------------------------------------------------------------------

album_view_objects = Album.objects.all()

# -----------------------------------------------------------------------------
```

This will tell which queryset is used for each view that uses kwargs.

Currently this renderer **can't yet handle more complex views** that use kwargs
from multiple models at the same time.

## Usage

Use two terminal windows. One running development server `python manage.py runserver`.

In the second window use either command:

`python manage.py render`

`python manage.py render --html` if you prefer internal links ending with .html instead of slash 