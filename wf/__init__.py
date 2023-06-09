"""Simple workflow for downloading files via FTP."""

import subprocess

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Union

from latch import medium_task, workflow
from latch.types import (
    LatchAuthor,
    LatchDir,
    LatchMetadata,
    LatchParameter,
    LatchRule
)

@dataclass_json
@dataclass
class Ftp_url:
    user: str
    password: str
    host: str = "usftp21.novogene.com"
    port: str = "21"

@medium_task
def download_task(
    out_dir: str,
    source_url: Union[Ftp_url, str]
) -> LatchDir:
    
    if type(source_url) == str:
        _ftp_cmd = [
            "wget",
            "-c",
            "-r",
            source_url,
            "-P",
            f"/root/{out_dir}"
        ]
    elif type(source_url) == Ftp_url:
        _ftp_cmd = [
            "wget",
            "-c",
            "-r",
            (f"ftp://{source_url.user}:"
            f"{source_url.password}@"
            f"{source_url.host}:"
            f"{source_url.port}/"),
            "-P",
            f"/root/{out_dir}"           
        ]
    else:
        raise Exception("Download url incorrect format; please check url.") 
    
    subprocess.run(_ftp_cmd)

    return LatchDir(f'/root/{out_dir}', f'latch:///downloads/{out_dir}')
    
metadata = LatchMetadata(
    display_name="ftp downloader",
    author=LatchAuthor(
        name="AtlasXomics, Inc.",
        email="jamesm@atlasxomics.com",
        github="https://github.com/atlasxomics",
    ),
    repository="https://github.com/atlasxomics/ftp_downloader",
    license="MIT",
    parameters={
        "out_dir": LatchParameter(
            display_name="output directory",
            description="Name of Latch subdirectory for downloaded file; files \
                will be saved to /downloads/{output directory}.",
            batch_table_column=True,
            rules=[
                LatchRule(
                    regex="^[^/].*",
                    message="output directory cannot start with a '/'"
                )
            ]
        ),
        "source_url": LatchParameter(
            display_name="download url",
            description="Ftp parameters or single url for download.",
            batch_table_column=True
        )
    },
    tags=[],
)

@workflow(metadata)
def ftp_download(
    out_dir: str,
    source_url: Union[Ftp_url, str]
) -> LatchDir:
    """Simple workflow for downloading files via FTP.
    Downloader for FTP or other
    ----
    Simple Latch UI for downloading files directly into Latch Console.

    Allows downloads with either FTP parameters or download url.

    Files are saved in the specified output directory in latch:///downloads/outdir.

    FTP will download recursively with url format:
    ```
    ftp://user:password@host:port/
    ```
    Providing full url will download recurively for directories, once for files.

    Tested with ftp and https downloads; interally just calling
    ```
    wget -c  -r <link> -P <output>
    ```
    so should work with most download urls.
"""
    
    return download_task(out_dir=out_dir, source_url=source_url)
