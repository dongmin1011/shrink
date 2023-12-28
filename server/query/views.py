from .models import QueryBoard, Like, Dislike, Comment, CommentLike, CommentDislike
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from user_auth.decorators import token_required
from django.shortcuts import get_object_or_404

import json


# 질문 게시물 목록
@require_http_methods(["GET"])
def list_queryboards(req):
    try:
        queryboards = QueryBoard.objects.all().order_by('-created_at')
        post_list = [{
            'id': query.id,
            'title': query.title,
            'content': query.content,
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
            'message': '게시물 목록 조회 중 오류가 발생했습니다: ' + str(e)
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
        'created_at': comment.created_at,
        'likes_count': comment.comment_likes.count(),
        'dislikes_count': comment.comment_dislikes.count()
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
            'like': queryboard.likes.count(),
            'dislike': queryboard.dislikes.count(),
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
        return JsonResponse({
            'status': 'fail',
            'message': '게시물 등록 중 오류가 발생했습니다: ' + str(e)
        }, status=500)


# 질문 게시물 수정
@require_http_methods(["PUT"])
@csrf_exempt
@token_required
def update_queryboard(req, query_id):
    try:
        queryboard = get_object_or_404(QueryBoard, id=query_id)
        if queryboard.writer != req.user:
            return JsonResponse({
                'status': 'fail',
                'message': '게시물 수정 권한이 없습니다.'
            }, status=403)

        data = json.loads(req.body)
        queryboard.title = data.get('title', queryboard.title)
        queryboard.content = data.get('content', queryboard.content)
        queryboard.save()

        return JsonResponse({
            'status': 'success',
            'message': f'{queryboard.id}번 게시물이 성공적으로 수정되었습니다.'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'fail',
            'message': '잘못된 형식의 데이터입니다.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': f'게시물 수정 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


# 질문 게시물 삭제
@require_http_methods(["DELETE"])
@csrf_exempt
@token_required
def delete_queryboard(req, query_id):
    try:
        queryboard = get_object_or_404(QueryBoard, id=query_id)
        if queryboard.writer != req.user:
            return JsonResponse({
                'status': 'fail',
                'message': '게시물 삭제 권한이 없습니다.'
            }, status=403)

        queryboard.delete()
        return JsonResponse({
            'status': 'success',
            'message': f'{query_id}번 게시물이 성공적으로 삭제되었습니다.'
        })
    except QueryBoard.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'message': '해당 게시물을 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': f'게시물 삭제 중 오류가 발생했습니다: {str(e)}'
        }, status=500)

# 질문 게시물 조회수 추가
@require_http_methods(["POST"])
@csrf_exempt
def increase_view_queryboard(req, query_id):
    try:
        queryboard = get_object_or_404(QueryBoard, id=query_id)
        queryboard.view += 1
        queryboard.save()
        return JsonResponse({
            'status': 'success',
            'message': f'{query_id}번 게시물의 조회수가 추가되었습니다.'
        })
    except QueryBoard.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'message': '해당 게시물을 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': f'조회수 추가 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


# 질문 게시물 좋아요
@require_http_methods(["POST"])
@csrf_exempt
@token_required
def like_queryboard(req, query_id):
    try:
        queryboard = get_object_or_404(QueryBoard, id=query_id)
        user = req.user

        dislike = Dislike.objects.filter(query=queryboard, user=user).first()
        if dislike:
            dislike.delete()

        like, created = Like.objects.get_or_create(query=queryboard, user=user)
        if not created:
            like.delete()
            return JsonResponse({
                'status': 'success',
                'message': f'{query_id}번 게시물의 좋아요가 제거되었습니다.'
            })
        return JsonResponse({
            'status': 'success',
            'message': f'{query_id}번 게시물의 좋아요가 추가되었습니다.'
        })
    except QueryBoard.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'message': '해당 게시물을 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': f'좋아요 처리 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


# 질문 게시물 싫어요
@require_http_methods(["POST"])
@csrf_exempt
@token_required
def dislike_queryboard(req, query_id):
    try:
        queryboard = get_object_or_404(QueryBoard, id=query_id)
        user = req.user

        like = Like.objects.filter(query=queryboard, user=user).first()
        if like:
            like.delete()

        dislike, created = Dislike.objects.get_or_create(query=queryboard, user=user)
        if not created:
            dislike.delete()
            return JsonResponse({
                'status': 'success',
                'message': f'{query_id}번 게시물의 싫어요가 제거되었습니다.'
            })
        return JsonResponse({
            'status': 'success',
            'message': f'{query_id}번 게시물의 싫어요가 추가되었습니다.'
        })
    except QueryBoard.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'message': '해당 게시물을 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': f'싫어요 처리 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


# 댓글 작성
@require_http_methods(["POST"])
@csrf_exempt
@token_required
def create_comment(req, query_id):
    print('req.body >> ', query_id)
    try:
        data = json.loads(req.body)
        content = data.get('content')
        user = req.user
        queryboard = get_object_or_404(QueryBoard, id=query_id)
        comment = Comment.objects.create(query=queryboard, writer=user, content=content)
        return JsonResponse({
            'status': 'success',
            'message': f'{query_id}번 게시물에 댓글이 작성되었습니다.',
            'comment_id': comment.id
        })
    except QueryBoard.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'message': '해당 게시물을 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': f'댓글 작성 중 오류가 발생했습니다: {str(e)}'
        }, status=500)

# 댓글 수정
@require_http_methods(["PUT"])
@csrf_exempt
@token_required
def update_comment(req, comment_id):
    try:
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.writer != req.user:
            return JsonResponse({
                'status': 'fail',
                'message': '댓글 수정 권한이 없습니다.'
            }, status=403)
        data = json.loads(req.body)
        comment.content = data.get('content', comment.content)
        comment.save()
        return JsonResponse({
            'status': 'success',
            'message': f'{comment_id}번 댓글이 수정되었습니다.',
            'comment_id': comment.id
        })
    except Comment.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'message': '해당 댓글을 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': f'댓글 수정 중 오류가 발생했습니다: {str(e)}'
        }, status=500)

# 댓글 삭제
@require_http_methods(["DELETE"])
@csrf_exempt
@token_required
def delete_comment(req, comment_id):
    try:
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.writer != req.user:
            return JsonResponse({
                'status': 'fail',
                'message': '댓글 삭제 권한이 없습니다.'
            }, status=403)
        comment.delete()
        return JsonResponse({
            'status': 'success',
            'message': f'{comment_id}번 댓글이 삭제되었습니다.'
        })
    except Comment.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'message': '해당 댓글을 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': f'댓글 삭제 중 오류가 발생했습니다: {str(e)}'
        }, status=500)

# 댓글 좋아요
@require_http_methods(["POST"])
@csrf_exempt
@token_required
def like_comment(req, comment_id):
    try:
        comment = get_object_or_404(Comment, id=comment_id)
        user = req.user

        comment_dislike = CommentDislike.objects.filter(comment=comment, user=user).first()
        if comment_dislike:
            comment_dislike.delete()

        comment_like, created = CommentLike.objects.get_or_create(comment=comment, user=user)
        if not created:
            comment_like.delete()
            return JsonResponse({
                'status': 'success',
                'message': f'{comment_id}번 댓글의 좋아요가 제거되었습니다.'
            })
        return JsonResponse({
            'status': 'success',
            'message': f'{comment_id}번 댓글의 좋아요가 추가되었습니다.'
        })
    except Comment.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'message': '해당 댓글을 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': f'댓글 좋아요 처리 중 오류가 발생했습니다: {str(e)}'
        }, status=500)

# 댓글 싫어요
@require_http_methods(["POST"])
@csrf_exempt
@token_required
def dislike_comment(req, comment_id):
    try:
        comment = get_object_or_404(Comment, id=comment_id)
        user = req.user

        comment_like = CommentLike.objects.filter(comment=comment, user=user).first()
        if comment_like:
            comment_like.delete()

        comment_dislike, created = CommentDislike.objects.get_or_create(comment=comment, user=user)
        if not created:
            comment_dislike.delete()
            return JsonResponse({
                'status': 'success',
                'message': f'{comment_id}번 댓글의 싫어요가 제거되었습니다.'
            })
        return JsonResponse({
            'status': 'success',
            'message': f'{comment_id}번 댓글의 싫어요가 추가되었습니다.'
        })
    except Comment.DoesNotExist:
        return JsonResponse({
            'status': 'fail',
            'message': '해당 댓글을 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'fail',
            'message': f'댓글 싫어요 처리 중 오류가 발생했습니다: {str(e)}'
        }, status=500)
