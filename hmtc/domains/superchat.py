from typing import Any, Dict
from PIL import Image
from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatFiles as SuperchatFilesModel
from hmtc.repos.superchat_repo import SuperchatRepo
from hmtc.repos.file_repo import FileRepo
from pathlib import Path
from hmtc.config import init_config


config = init_config()
STORAGE = Path(config["STORAGE"]) / "screenshots"

class Superchat(BaseDomain):
    model = SuperchatModel
    repo = SuperchatRepo()
    file_repo = FileRepo(SuperchatFilesModel)
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "frame": self.instance.frame,
            "video_id": self.instance.video_id,
            "segment_id": self.instance.segment_id,
        }

    def add_file(self, file: Path):
        
        target_path = STORAGE / self.instance.video.youtube_id
        new_name = f"{str(self.instance.frame).zfill(4)}.jpg"

        self.file_repo.add(
            item=self.instance, source=file, target_path=target_path, stem=new_name
        )
        
    def save_image(self, image):
        
        target_path = STORAGE / self.instance.video.youtube_id
        target_path.mkdir(exist_ok=True, parents=True)
        path = target_path / f"{str(self.instance.frame).zfill(4)}.jpg"
        
        im = Image.fromarray(image)
        im.save(path)
        self.add_file(path)