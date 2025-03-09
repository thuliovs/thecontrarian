from django.contrib import admin

from . import models as writer_models

admin.site.register(writer_models.Article)
