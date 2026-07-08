import json
from pathlib import Path
from typing import List

from bb_text_extractor import extractor
from pydantic import BaseModel, Field, parse_obj_as


SOURCE_PATH = Path(__file__).resolve().parents[1]
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


def load_manifest(path: Path = MANIFEST_PATH) -> Manifest:
    manifest_data = path.read_text(encoding="utf-8")
    return parse_obj_as(Manifest, json.loads(manifest_data))


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


def extract_job(job: ProcessingJob, project_path: Path):
    input_path = SOURCE_PATH / job.input_path
    if not input_path.exists():
        raise FileNotFoundError(
            f"Input path for job '{job.id}' does not exist: {input_path}. "
            "Run `git submodule update --init --recursive` if this is a submodule."
        )

    extractor._literals.clear()
    extractor.core(input_path, project_path / job.output_path)


def write_localization_manifest(manifest: Manifest, project_path: Path):
    output_manifest = build_localization_manifest(manifest)
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / OUTPUT_MANIFEST_NAME).write_text(
        json.dumps(output_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(project_path: Path):
    manifest = load_manifest()
    for job in manifest.jobs:
        extract_job(job, project_path)
    write_localization_manifest(manifest, project_path)


def main_from_argv(argv: List[str]):
    if len(argv) != 2:
        raise SystemExit(f"Usage: {Path(argv[0]).name} <Battle-Brothers-CN path>")
    main(Path(argv[1]).resolve())


if __name__ == "__main__":
    import sys

    main_from_argv(sys.argv)
