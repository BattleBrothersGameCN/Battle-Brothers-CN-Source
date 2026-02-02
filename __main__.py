import sys
from pathlib import Path
from typing import Optional, List
import json

from bb_text_extractor.extractor import core
from pydantic import BaseModel, Field, parse_obj_as


SOURCE_PATH = Path(__file__).parent
MANIFEST_PATH = SOURCE_PATH / "manifest.json"


class ProcessingJob(BaseModel):
    """需要提取文本的源码声明"""
    input_path: Path = Field(description="源码目录")
    output_path: Path = Field(description="文本提取输出路径")

    name: str = Field(description="项目名称")
    description: str = Field(default="", description="项目描述")
    version: str = Field(description="版本信息")
    project_id: str = Field(description="Para Project ID")


class Manifest(BaseModel):
    jobs: List[ProcessingJob] = Field(default_faculty=list)



def main(project_path: Path):
    manifest_data = MANIFEST_PATH.read_text()
    manifest = parse_obj_as(Manifest, json.loads(manifest_data))
    for job in manifest.jobs:
        core(SOURCE_PATH / job.input_path, project_path / job.output_path)
        (project_path / job.output_path / "job.json").write_text(job.json(ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
