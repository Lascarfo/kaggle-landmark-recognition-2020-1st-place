from typing import Union
from supervisely_lib.project.project_meta import ProjectMeta
from supervisely_lib.api.api import Api
from supervisely_lib.annotation.annotation import Annotation
import sly_globals as g
from sly_visualization_progress import init_progress

# html example
# <sly-grid-gallery
#         v-if="data.gallery"
#         :content="data.gallery.content"
#         :options="data.gallery.options">
#     <template v-slot:card-footer="{ annotation }">
#         <div class="mt5" style="text-align: center">
#             <el-tag type="primary">{{annotation.title}}</el-tag>
#         </div>
#     </template>
# </sly-grid-gallery>


class CompareGallery:

    def __init__(self, task_id, api: Api, v_model,
                 project_meta: ProjectMeta, columns=2, rows=1):
        self.cols = columns
        self.rows = rows
        self._task_id = task_id
        self._api = api
        self._v_model = v_model
        self._project_meta = project_meta.clone()

        self._options = {
            "enableZoom": True,
            "syncViews": True,
            "showPreview": False,
            "selectable": False,
            "opacity": 0.5,
            "showOpacityInHeader": True,
            # "viewHeight": 450,
        }

    def update_project_meta(self, project_meta: ProjectMeta):
        self._project_meta = project_meta.clone()

    def update_grid_size(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def _set_item(self, name, title, image_url, ann: Union[Annotation, dict] = None):
        setattr(self, f"_{name}_title", title)
        setattr(self, f"_{name}_image_url", image_url)
        res_ann = Annotation((1, 1))
        if ann is not None:
            if type(ann) is dict:
                res_ann = Annotation.from_json(ann, self._project_meta)
            else:
                res_ann = ann.clone()
        setattr(self, f"_{name}_ann", res_ann)

    def set_row_data(self, title, image_url, ann: Union[Annotation, dict] = None):

        for row in range(1, self.rows+1):
            self._set_item(f"original_{row}", title, image_url, ann)
            for col in range(1, self.cols+1):
                self._set_item(f"top_{col}", title, image_url, ann)

    def _get_item_annotation(self, name):
        return {
            "url": getattr(self, f"_{name}_image_url"),
            "figures": [label.to_json() for label in getattr(self, f"_{name}_ann").labels],
            "title": getattr(self, f"_{name}_title"),
        }

    def update(self):
        # if self._left_image_url is None:
        #     raise ValueError("Left item is not defined")
        # if self._right_image_url is None:
        #     raise ValueError("Right item is not defined")
        gallery_json = self.to_json()
        self._api.task.set_field(self._task_id, self._v_model, gallery_json)

    def to_json(self, ):
        if self._left_image_url is None or self._right_image_url is None:
            return None
        layout = [["left"], ["right"]]
        annotations = {
            "left": self._get_item_annotation("left"),
            "right": self._get_item_annotation("right"),
        }
        views_bindings = [["left", "right"]]

        return {
            "content": {
                "projectMeta": self._project_meta.to_json(),
                "layout": layout,
                "annotations": annotations
            },
            "options": {
                **self._options,
                "syncViewsBindings": views_bindings
            }
        }


def init(data, state):
    global image_gallery
    state["collapsed5"] = True
    state["disabled5"] = True
    state["modelLoading"] = False
    init_progress(5, data)

    state["weightsPath"] = ""
    data["done5"] = False
    data['Gallery'] = {}


def restart(data, state):
    data["done5"] = False


image_gallery = None
v_model = 'data.Gallery'
image_gallery = CompareGallery(g.task_id, g.api, v_model, g.project_meta)