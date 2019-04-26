import dramatiq
import lupa

from account.models import User
from submission.models import Submission, TestPaperSubmission, GradeStatus
from judge.dispatcher import JudgeDispatcher
from utils.shortcuts import DRAMATIQ_WORKER_ARGS


@dramatiq.actor(**DRAMATIQ_WORKER_ARGS())
def judge_task(submission_id, problem_id):
    uid = Submission.objects.get(id=submission_id).user_id
    if User.objects.get(id=uid).is_disabled:
        return
    JudgeDispatcher(submission_id, problem_id).judge()


@dramatiq.actor(**DRAMATIQ_WORKER_ARGS())
def grade_task(submission_id):
    submission = TestPaperSubmission.objects.get(id=submission_id)
    submission.status = GradeStatus.GRADING
    submission.save(update_fields=("status",))

    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    content_questions = submission.contest.contestquestion_set.all()
    content = submission.content
    score = 0

    for item in content_questions:
        data = content.get(str(item.id))
        if data:
            try:
                lua_func = lua.eval(item.question.script)
                score += lua_func(data)
            except lupa.LuaError:
                submission.status = GradeStatus.ERROR
                submission.save(update_fields=("status",))
                return

    submission.score = score
    submission.status = GradeStatus.GRADED
    submission.save(update_fields=("status", "score"))
