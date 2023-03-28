"""Simple workflow for downloading files via FTP."""

import subprocess

from typing import Optional

from latch import medium_task, workflow
from latch.types import (
    LatchAuthor,
    LatchFile,
    LatchDir,
    LatchMetadata,
    LatchParameter,
)

@medium_task
def ftp_task(
    out_dir: str,
    user: str,
    password: str,
    host: str,
    port: str,
    url: str = None,
) -> LatchDir:
    
    if url:
        _ftp_cmd = [
            "wget",
            "-c",
            "-r",
            url,
            "-P",
            f"/root/{out_dir}"
        ]
    else:
        _ftp_cmd = [
            "wget",
            "-c",
            "-r",
            f"ftp://{user}:{password}@{host}:{port}/",
            "-P",
            f"/root/{out_dir}"           
        ]
    
    subprocess.run(_ftp_cmd)

    return LatchDir(f'/root/{out_dir}', f'latch:///ftp/{out_dir}')
    
metadata = LatchMetadata(
    display_name="ftp downloader",
    author=LatchAuthor(
        name="James McaGann",
        email="jpaulmcgann@gmail.com",
        github="https://github.com/jpmcga",
    ),
    repository="https://github.com/jpmcga/ftp_downloader",
    license="MIT",
    parameters={
        "out_dir": LatchParameter(
            display_name="output directory",
            description="Name of Latch subdirectory for downloaded file; files \
                will be saved to /ftp/{output directory}.",
            batch_table_column=True,
        ),
        "user": LatchParameter(
            display_name="user/batch id",
            description="User ID or Batch ID (Novogene) for FTP download.",
            batch_table_column=True,
        ),
        "password": LatchParameter(
            display_name="password",
            description="Password for FTP download.",
            batch_table_column=True,
        ),
        "host": LatchParameter(
            display_name="host",
            description="Name of FTP host server.",
            batch_table_column=True,
        ),
        "port" : LatchParameter(
            display_name="port",
            description="Port to be used for FTP download.",
            batch_table_column=True,   
        ),
        "url" : LatchParameter(
            display_name="url",
            description="Full url for FTP download; takes precedence",
            batch_table_column=True,
        )
    },
    tags=[],
)

@workflow(metadata)
def ftp_download(
    out_dir: str,
    user: str,
    password: str,
    url: Optional[str],
    host: str = "usftp21.novogene.com",
    port: str = "21",
) -> LatchDir:
    
    return ftp_task(
        out_dir=out_dir,
        user=user,
        password=password,
        host=host,
        port=port,
        url=url
    )
