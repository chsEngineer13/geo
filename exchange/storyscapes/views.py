from .models import Story
from django.http import HttpResponse
import json

_PERMISSION_MSG_LOGIN = 'You must be logged in to save this story'
_PERMISSION_MSG_SAVE = 'You are not permitted to save or edit this story'


def save_story(request, storyid):
    if not request.user.is_authenticated():
        return HttpResponse(
                _PERMISSION_MSG_LOGIN,
                status=401,
                content_type="text/plain"
        )

    story_obj = Story.objects.get(id=storyid)
    if not request.user.has_perm('change_resourcebase', story_obj):
        return HttpResponse(
                _PERMISSION_MSG_SAVE,
                status=401,
                content_type="text/plain"
        )

    try:
        story_obj.update_from_viewer(request.body)
        return HttpResponse(json.dumps(story_obj.viewer_json(request.user)))
    except ValueError as e:
        return HttpResponse(
                "The server could not understand the request." + str(e),
                content_type="text/plain",
                status=400
        )


def new_story_json(request):
    if not request.user.is_authenticated():
        return HttpResponse(
                'You must be logged in to save new maps',
                content_type="text/plain",
                status=401
        )
    story_obj = Story(owner=request.user)
    story_obj.save()

    try:
        body = request.body
    except Exception:
        body = ''

    try:
        story_obj.update_from_viewer(body)
    except ValueError as e:
        return HttpResponse(str(e), status=400)
    else:
        return HttpResponse(
                json.dumps({'id': story_obj.id}),
                status=200,
                content_type='application/json'
        )
