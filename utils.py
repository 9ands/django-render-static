import os
import re
import requests
import importlib
from datetime import datetime
from django.urls import reverse
from django.conf import settings

# -----------------------------------------------------------------------------

class RenderStatic():
    """
    How do I know to which model view kwargs belong?
    Add {viewname}_objects variable to views.py pointing to the
    queryset to solve that. For example:
    album_view_objects = Album.objects.all()
    If prefer_html_extension is set to True all href attributes
    starting with "/" (internal pages) found in the rendered html
    will have trailing slash replaced with ".html".
    By default internal page links are left untouched, so a server
    hosting the static website (eg Apache) has to be able to redirect these
    links to corresponding .html files.
    """

    def __init__(self, prefer_html_extension=False):
        
        app_names = settings.RENDER_STATIC_APPS
        if not app_names:
            print("RenderStatic > List of apps in settings.py not found")
            self.urlpatterns = None
        else:
            self.urlpatterns = self.prepare_urlpatterns(app_names)
        self.html_ext = prefer_html_extension
        self.host = "http://"+settings.RENDER_STATIC_HOST
        self.savepath = os.path.join(
            settings.RENDER_STATIC_ROOT,
            datetime.now().strftime("%Y%m%d%H%M%S"
        ))

    #-----

    def prepare_urlpatterns(self, app_name_list):
        """
        Go through a list of apps and build urlpatterns for each view
        found in corresponding app/views.py
        """

        kwargs = re.compile(r"\<(?:\w+)\:(\w+)\>\/?")
        urlpatterns = []

        for app_name in app_name_list:
            app_urls = importlib.import_module(f"{app_name}.urls")
            app_views = importlib.import_module(f"{app_name}.views")

            for p in app_urls.urlpatterns:
                pat_dict = {
                    "app_name": app_urls.app_name,
                    "path_name": p.name,
                    # "path_view_func": p.callback,
                    "path_objects": getattr(app_views,
                        f"{p.name}_objects", None),
                    "path_kwargs": kwargs.findall(p.pattern._route)
                }
                urlpatterns.append(pat_dict)

        return urlpatterns

    #-----

    def add_canonical_meta(self, html, url):
        """
        Insert canonical link (preferred) version of the web page
        before </head> as part of search engine optimization.
        """

        head_end = html.find("</head>")
        canonical = f'<link rel="canonical" href="{settings.LIVE_URL}{url}" />'
        return html[:head_end] + "\t" + canonical + "\n" + html[head_end:]

    #-----

    def parse_and_save_request(self, url):
        """
        Make request using provided path and parse rendered html before
        saving it to RENDER_STATIC_ROOT.
        """

        print("url > ",url)
        url_list = url.strip("/").split("/")
        filename = url_list.pop()+".html"
        subpath = "/".join(url_list)
        savepath = os.path.join(self.savepath, subpath)
        parsed_html = ""

        r = requests.get(self.host+url)

        if self.html_ext:
            pattern = re.compile(r"(href=\"\/[a-z0-9-]+(\/[a-z0-9-]+)*)\/\"")
            parsed_html = pattern.sub(r'\1.html"', r.text)
        else:
            parsed_html = self.add_canonical_meta(r.text, url)

        if not os.path.exists(savepath): os.makedirs(savepath)

        with open(os.path.join(savepath, filename),"w",encoding='utf-8') as f:
            f.write(parsed_html)

    #-----

    def render_static(self):
        """
        If kwargs are present in url pattern the loop will try to work out
        full path to each individual object in {viewname}_objects.
        It hasn't really been tested with paths containing multiple kwargs.
        """

        for up in self.urlpatterns:

            if up["path_kwargs"]:

                if not up["path_objects"]:
                    print("{}_objects variable in views.py is missing".format(
                        up['path_name']
                    ))
                    return
                
                for o in up["path_objects"]:
                    kwargs = {}
                
                    for kwarg in up["path_kwargs"]:
                        kwargs[kwarg] = getattr(o, kwarg)

                    url = reverse(f"{up['app_name']}:{up['path_name']}",
                        kwargs=kwargs)
                    self.parse_and_save_request(url)

            else: # url with no dynamic kwargs
                url = reverse(f"{up['app_name']}:{up['path_name']}")
                self.parse_and_save_request(url)
                        
# -----------------------------------------------------------------------------
