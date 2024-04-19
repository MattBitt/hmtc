from pathlib import Path

import solara
from loguru import logger
from hmtc.models import Video

HERE = Path(__file__).parent
title = "use_thread"


@solara.component
def Page():
    router = solara.use_router()
    level = solara.use_route_level()
    if router.parts[-1] == "sandbox":
        return solara.Markdown("### Sandbox")

    video_id = router.parts[level:][0]
    vid = None
    try:
        if video_id.isdigit():
            vid = Video.get_or_none(Video.id == video_id)
        logger.debug(f"Current param: {video_id}")
    except Exception as e:
        logger.error(e)
        return solara.Markdown("### Error: Please provide a number as a parameter")

    if vid:
        solara.Markdown(f"### {vid.title}")
    else:
        solara.Markdown(f"### Video not found {video_id}")


# @solara.component
# def Page():
#     number, set_number = solara.use_state(17)
#     # the number that proofs it is not a prime
#     proof, set_proof = solara.use_state(cast(Optional[int], None))

#     def work():
#         for i in range(3, number):
#             reminder = number % i
#             if reminder == 0:
#                 set_proof(i)
#                 return False
#             # make it always take ~4 seconds
#             time.sleep(4 / number)
#         return True

#     # work will be cancelled/restarted every time the dependency changes
#     result: solara.Result[bool] = solara.use_thread(work, dependencies=[number])

#     with solara.VBox() as main:
#         rw.IntText(value=number, on_value=set_number)
#         if result.state == solara.ResultState.FINISHED:
#             if result.value:
#                 solara.Success(f"{number} is a prime!")
#             else:
#                 solara.Error(f"{number} is not a prime, it can be divided by {proof} ")
#         elif result.state == solara.ResultState.ERROR:
#             solara.Error(f"Error occurred: {result.error}")
#         else:
#             solara.Info(f"Running... (status = {result.state})")
#             rv.ProgressLinear(indeterminate=True)
#     return main
