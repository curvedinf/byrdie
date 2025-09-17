
from byrdie.api import route

@route('/blog/post')
def blog_post(request):
    return {'message': 'Blog post view'}

