from sly_visualization_progress import init_progress

local_weights_path = None


def init(data, state):
    state["collapsed4"] = True
    state["disabled4"] = True
    state["modelLoading"] = False
    init_progress(4, data)

    state["weightsPath"] = ""
    data["done4"] = False


def restart(data, state):
    data["done4"] = False
