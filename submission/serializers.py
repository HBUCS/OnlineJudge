from .models import Submission, Comment, TestPaperSubmission
from utils.api import serializers
from utils.serializers import LanguageNameChoiceField


class CreateSubmissionSerializer(serializers.Serializer):
    problem_id = serializers.IntegerField()
    language = LanguageNameChoiceField()
    code = serializers.CharField(max_length=1024 * 1024)
    contest_id = serializers.IntegerField(required=False)
    captcha = serializers.CharField(required=False)


class TestPaperSubmissionSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestPaperSubmission
        fields = ("id", "create_time", "status", "score", "username")


class TestPaperSubmissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestPaperSubmission
        fields = ("id", "create_time", "status", "score", "user_id",
                  "content")


class CreateTestPaperSubmissionSerializer(serializers.Serializer):
    contest_id = serializers.IntegerField()
    content = serializers.DictField()
    captcha = serializers.CharField(required=False)


class CreateCommentSerializer(serializers.Serializer):
    submission_id = serializers.CharField()
    line = serializers.IntegerField()
    message = serializers.CharField()


class EditCommentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    message = serializers.CharField()


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        exclude = ("submission", "user_id")


class ShareSubmissionSerializer(serializers.Serializer):
    id = serializers.CharField()
    shared = serializers.BooleanField()


class SubmissionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Submission
        fields = "__all__"


# 不显示submission info的serializer, 用于ACM rule_type
class SubmissionSafeModelSerializer(serializers.ModelSerializer):
    problem = serializers.SlugRelatedField(read_only=True, slug_field="_id")

    class Meta:
        model = Submission
        exclude = ("info", "contest", "ip")


class SubmissionListSerializer(serializers.ModelSerializer):
    problem = serializers.SlugRelatedField(read_only=True, slug_field="_id")
    show_link = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Submission
        exclude = ("info", "contest", "code", "ip")

    def get_show_link(self, obj):
        # 没传user或为匿名user
        if self.user is None or not self.user.is_authenticated:
            return False
        return obj.check_user_permission(self.user)
