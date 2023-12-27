from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import QueryBoard, Like, Dislike, Comment, CommentLike, CommentDislike
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from user_auth.decorators import token_required

import json



# 질문 게시물 목록
@require_http_methods(["GET"])
def list_queryboards(req):
    try:
        queryboards = QueryBoard.objects.all().order_by('-created_at')
        post_list = [{
            'id': query.id,
            'title': query.title,
            'writer': query.writer.nickname,
            'like': query.like,
            'dislike': query.dislike,
            'view': query.view,
            'created_at': query.created_at
        } for query in queryboards]

        return JsonResponse({
            'status': 'success',
            'message': '게시물 목록이 성공적으로 조회되었습니다.',
            'post_list': post_list
        })
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': '게시물 목록 조회 중 오류가 발생했습니다'
        }, status=500)

# 질문 게시물 조회
@require_http_methods(["GET"])
def detail_queryboard(req, query_id):
    queryboard = get_object_or_404(QueryBoard, id=query_id)
    comments = queryboard.comments.all()
    comment_data = [{
        'id': comment.id,
        'writer': {
            'nickname': comment.writer.nickname,
            'profile_url': comment.writer.profile_url
        },
        'content': comment.content,
        'created_at': comment.created_at
    } for comment in comments]

    payload = {
        'status': 'success',
        'message': '게시물이 성공적으로 조회되었습니다.',
        'post': {
            'id': queryboard.id,
            'title': queryboard.title,
            'content': queryboard.content,
            'writer': {
                'nickname': queryboard.writer.nickname,
                'profile_url': queryboard.writer.profile_url
            },
            'like': queryboard.like,
            'dislike': queryboard.dislike,
            'view': queryboard.view,
            'created_at': queryboard.created_at,
            'comments': comment_data
        }
    }

    return JsonResponse(payload)


# 질문 게시물 생성
@require_http_methods(["POST"])
@csrf_exempt
@token_required
def create_queryboard(req):
    try:
        data = json.loads(req.body)
        title = data.get('title')
        content = data.get('content')
        user = req.user

        print('type(req.user) >> ', type(req.user))

        print('req.user >> ', user.id, user.nickname, user.phone)


        if not title or not content:
            return JsonResponse({
                'status': 'fail',
                'message': '제목과 내용을 모두 입력해야 합니다.'
            }, status=400)

        queryboard = QueryBoard.objects.create(
            title=title,
            content=content,
            writer=user
        )

        print('queryboard >> ', queryboard)

        return JsonResponse({
            'status': 'success',
            'message': f'{queryboard.id}번 게시물이 성공적으로 등록되었습니다.'
        })
    except Exception as e:
        print(e)

        return JsonResponse({
            'status': 'fail',
            'message': '게시물 등록 중 오류가 발생했습니다'
        }, status=500)


# 질문 게시물 수정
@require_http_methods(["PUT"])
def update_queryboard(req, query_id):
    queryboard = get_object_or_404(QueryBoard, id=query_id)
    if queryboard.writer != req.user:
        raise PermissionDenied

    data = json.loads(request.body)
    queryboard.title = data.get('title', queryboard.title)
    queryboard.content = data.get('content', queryboard.content)
    queryboard.save()

    return JsonResponse({
        'status': 'success',
        'message': f'{queryboard.id}번 게시물이 성공적으로 수정되었습니다.'
    })


# 질문 게시물 삭제
@require_http_methods(["DELETE"])
def delete_queryboard(request, query_id):
    queryboard = get_object_or_404(QueryBoard, id=query_id)
    if queryboard.writer != request.user:
        raise PermissionDenied

    queryboard.delete()
    return JsonResponse({
        'status': 'success',
        'message': f'{queryboard.id}번 게시물이 성공적으로 삭제되었습니다.'
    })


# 질문 게시물 조회수 증가
@require_http_methods(["POST"])
def increase_view_queryboard(req, query_id):
    queryboard = get_object_or_404(QueryBoard, id=query_id)

    queryboard.view += 1
    queryboard.save()

    return JsonResponse({
        'status': 'success',
        'message': f'{query_id}번 게시물의 조회수가 증가되었습니다.'
    })


# 질문 게시물 좋아요 처리
@require_http_methods(["POST"])
def like_queryboard(request, query_id):
    queryboard = get_object_or_404(QueryBoard, id=query_id)
    user = request.user

    like, created = Like.objects.get_or_create(query=queryboard, user=user)
    if not created:
        like.delete()
        return JsonResponse({
            'status': 'success',
            'message': f'{query_id}번 게시물의 좋아요가 제거되었습니다.'
        })

    return JsonResponse({
        'status': 'success',
        'message': f'{query_id}번 게시물의 좋아요가 증가되었습니다.'
    })


# 질문 게시물 싫어요 처리
@require_http_methods(["POST"])
def dislike_queryboard(request, query_id):
    queryboard = get_object_or_404(QueryBoard, id=query_id)
    user = request.user


    dislike, created = Dislike.objects.get_or_create(query=queryboard, user=user)
    if not created:
        dislike.delete()
        return JsonResponse({
            'status': 'success',
            'message': f'{query_id}번 게시물의 싫어요가 제거되었습니다.'
        })

    return JsonResponse({
        'status': 'success',
        'message': f'{query_id}번 게시물의 싫어요가 증가되었습니다.'
    })


# 질문 게시물 댓글 작성
@require_http_methods(["POST"])
def create_comment(request, query_id):
    data = json.loads(request.body)
    content = data.get('content')
    user = request.user
    queryboard = get_object_or_404(QueryBoard, id=query_id)

    comment = Comment.objects.create(query=queryboard, user=user, content=content)
    
    return JsonResponse({
        'status': 'success',
        'message': f'{query_id}번 게시물에 댓글이 작성되었습니다.',
        'comment_id': comment.id
    })


# 댓글 수정
@require_http_methods(["PUT"])
def update_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user != request.user:
        raise PermissionDenied

    data = json.loads(request.body)
    comment.content = data.get('content', comment.content)
    comment.save()

    return JsonResponse({
        'status': 'success',
        'message': f'{query_id}번 게시물에 댓글이 수정되었습니다.',
        'comment_id': comment.id
    })


# 댓글 삭제
@require_http_methods(["DELETE"])
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user != request.user:
        raise PermissionDenied

    comment.delete()

    return JsonResponse({
        'status': 'success',
        'message': f'{query_id}번 게시물에 댓글이 삭제되었습니다.',
    })


# 댓글 좋아요
@require_http_methods(["POST"])
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    comment_like, created = CommentLike.objects.get_or_create(comment=comment, user=user)
    if not created:
        comment_like.delete()

        return JsonResponse({
            'status': 'success',
            'message': f'{comment_id}번 댓글의 좋아요가 제거되었습니다.'
        })

    return JsonResponse({
        'status': 'success',
        'message': f'{comment_id}번 댓글의 좋아요가 증가되었습니다.'
    })






# 댓글 싫어요
@require_http_methods(["POST"])
def dislike_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    comment_dislike, created = CommentDislike.objects.get_or_create(comment=comment, user=user)
    if not created:
        comment_dislike.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': f'{comment_id}번 댓글의 싫어요가 제거되었습니다.'
        })

    return JsonResponse({
        'status': 'success',
        'message': f'{comment_id}번 댓글의 싫어요가 증가되었습니다.'
    })