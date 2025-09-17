from django.db import models
from byrdie import Model, route, runserver

class Post(Model):
    title = models.CharField(max_length=200, expose=True)
    body = models.TextField(expose=True)
    created_at = models.DateTimeField(auto_now_add=True, expose=True)

    class Meta:
        ordering = ['-created_at']

@route()
def index(request, w):
    if not Post.objects.exists():
        Post.objects.create(title='First Post', body='This is the body of the first post.')
        Post.objects.create(title='Second Post', body='This is the body of the second post.')
    @w.do
def posts():
        return Post.objects.all()
    return {'posts': posts}

if __name__ == '__main__':
    runserver()
