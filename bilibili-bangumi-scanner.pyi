import requests
import json
import os, time, logging, argparse
from threading import Thread
from bs4 import BeautifulSoup
from rich.progress import Progress, Task, Text, ProgressColumn, TextColumn, BarColumn, MofNCompleteColumn, TimeElapsedColumn, TimeRemainingColumn
from typing import Optional

# Progress Bar Configuration
class NaiveTransferSpeedColumn(ProgressColumn):
    def render(self, task: Task) -> Text: ...

# Bangumi Info Class
class BiliBGM:
    def __init__(self, md_key: int, title: str): ...
    def __str__(self): ...

# Page Info Extractor     
def extractPageInfo(md_key: int) -> Optional[BiliBGM]: ...
    
def extractPageInfoByAPI(md_key: int) -> Optional[BiliBGM]: ...
    
# Data & Cache Treatment    
def loadData(file_path: str) -> list[BiliBGM]: ...

def saveData(bgm_data: list[BiliBGM], file_name: str): ...

def clearCache(cache_file_list: list[str]): ...

# Thread Configuration        
class ScanThread(Thread):
    def __init__(self, begin_num: int, end_num: int, sleep_step: int, use_api: bool): ...
    def run(self): ...
    