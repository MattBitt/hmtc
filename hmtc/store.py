# import solara
# from typing import Dict, Any
# from loguru import logger

# my_storage: Dict[str, Any] = {}
# session_storage = solara.reactive(my_storage)


# def store_in_session_storage(key, value):
#     logger.debug(f"Storing {key} in session storage")
#     sesssion_id = solara.get_session_id()
#     if sesssion_id in session_storage.value.keys():
#         session_storage.value[sesssion_id][key] = value
#     else:
#         session_storage.value[sesssion_id] = {key: value}


# def read_from_session_storage(key):
#     logger.debug(f"Reading {key} from session storage")
#     sesssion_id = solara.get_session_id()
#     if sesssion_id in session_storage.value.keys():
#         if key in session_storage.value[sesssion_id].keys():
#             return session_storage.value[sesssion_id][key]
#     return None


# kernel_storage: Dict[str, str] = {}


# @solara.lab.on_kernel_start
# def initialize_kernel_storage():
#     # when a kernel gets started, we initialize the dict entry
#     kernel_storage[solara.get_kernel_id()] = "this does not"

#     def cleanup():
#         # when a kernel gets stopped, we remove the dict entry
#         del kernel_storage[solara.get_kernel_id()]

#     # cleaning up kernel storage, we prevent memory leaks
#     return cleanup


# def empty_storage():
#     kernel_storage[solara.get_kernel_id()] = "___Cleared___"
