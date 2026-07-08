import argparse
import json
from pathlib import Path
from typing import List, Optional

from bb_text_extractor import extractor
from pydantic import BaseModel, Field


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
    return Manifest(**json.loads(manifest_data))


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


def select_jobs(manifest: Manifest, job_id: Optional[str]) -> List[ProcessingJob]:
    if not job_id or job_id == "all":
        return manifest.jobs

    jobs = [job for job in manifest.jobs if job.id == job_id]
    if jobs:
        return jobs

    available_jobs = ", ".join(job.id for job in manifest.jobs)
    raise ValueError(f"Unknown job id: {job_id}. Available jobs: {available_jobs}")


def main(project_path: Path, job_id: Optional[str] = None):
    manifest = load_manifest()
    for job in select_jobs(manifest, job_id):
        extract_job(job, project_path)
    write_localization_manifest(manifest, project_path)


def main_from_argv(argv: List[str]):
    parser = argparse.ArgumentParser(description="Extract Battle Brothers localization text.")
    parser.add_argument("project_path", type=Path, help="Battle-Brothers-CN repository path")
    parser.add_argument(
        "--job",
        "--job-id",
        dest="job_id",
        default="all",
        help="Only extract one manifest job id. Use 'all' or omit this option to extract every job.",
    )
    args = parser.parse_args(argv[1:])
    try:
        main(args.project_path.resolve(), args.job_id.strip())
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    import sys

    main_from_argv(sys.argv)
