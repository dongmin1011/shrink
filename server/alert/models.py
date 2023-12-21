from django.db import models
from user_auth.models import User
from django.utils import timezone
class Alert(models.Model):
    """
        설명:
            toUser (수신자): 알림을 받는 사용자를 식별합니다
            Verb (행동): 발생한 이벤트의 종류를 설명합니다 (예: 슈링크플레이션, 댓글, 좋아요)
            Target (대상): 알림과 연관된 대상 객체 (예: 슈링크플레이션이 발생한 상품명)
            content (내용): 알림을 전달할 내용을 기록합니다
            Read (읽음 여부): 알림이 읽혔는지 여부를 나타냅니다
            Timestamp (시간 정보): 알림이 생성된 시간을 기록합니다
        작성일: 23.12.20
        작성자: yujin
    """
    toUser = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    verb = models.CharField(max_length=255, blank=True, null=True)
    target = models.CharField(max_length=255, blank=True, null=True)
    content = models.CharField(max_length=512, blank=True, null=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    # created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'alert'

    def __str__(self):
        return self.content


