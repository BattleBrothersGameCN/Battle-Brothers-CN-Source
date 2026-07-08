import sys
from pathlib import Path
from typing import List
import json

from bb_text_extractor import extractor
from pydantic import BaseModel, Field, parse_obj_as


SOURCE_PATH = Path(__file__).parent
MANIFEST_PATH = SOURCE_PATH / "manifest.json"
OUTPUT_MANIFEST_NAME = "localization.manifest.json"


class ProcessingJob(BaseModel):
    """需要提取文本的源码声明"""
    id: str = Field(description="组件 ID")
    type: str = Field(default="mod", description="组件类型: base/mod")
    input_path: Path = Field(description="源码目录")
    output_path: Path = Field(description="文本提取输出路径")

    name: str = Field(description="项目名称")
    description: str = Field(default="", description="项目描述")
    version: str = Field(description="版本信息")
    project_id: int = Field(description="Para Project ID")
    package_name: str = Field(default="", description="生成的汉化包文件名")
    detect: List[str] = Field(default_factory=list, description="用于检测组件是否安装的 glob")
    required: bool = Field(default=False, description="组件是否必选")


class Manifest(BaseModel):
    jobs: List[ProcessingJob] = Field(default_factory=list)


def build_localization_manifest(manifest: Manifest):
    components = []
    for job in manifest.jobs:
        package_name = job.package_name
        if not package_name:
            package_name = "zdata_cn.zip" if job.id == "base" else f"zdata_cn_{job.id}.zip"
        components.append(
            {
                "id": job.id,
                "type": job.type,
                "name": job.name,
                "description": job.description,
                "version": job.version,
                "project_id": job.project_id,
                "json_path": job.output_path.as_posix(),
                "package_name": package_name,
                "detect": job.detect,
                "required": job.required or job.type == "base",
            }
        )
    return {
        "version": 1,
        "language": "zh_CN.UTF-8",
        "components": components,
    }


def main(project_path: Path):
    manifest_data = MANIFEST_PATH.read_text()
    manifest = parse_obj_as(Manifest, json.loads(manifest_data))
    for job in manifest.jobs:
        extractor._literals.clear()
        extractor.core(SOURCE_PATH / job.input_path, project_path / job.output_path)
    output_manifest = build_localization_manifest(manifest)
    (project_path / OUTPUT_MANIFEST_NAME).write_text(
        json.dumps(output_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main(Path(sys.argv[1]))
