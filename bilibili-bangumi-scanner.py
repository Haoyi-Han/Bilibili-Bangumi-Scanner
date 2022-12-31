import requests
import os, time, logging, argparse
from threading import Thread
from bs4 import BeautifulSoup
from rich.progress import Progress, Task, Text, ProgressColumn, TextColumn, BarColumn, MofNCompleteColumn, TimeElapsedColumn, TimeRemainingColumn

# Progress Bar Configuration
class NaiveTransferSpeedColumn(ProgressColumn):
    def render(self, task: Task) -> Text:
        speed = task.finished_speed or task.speed
        if speed is None:
            return Text("?", style="progress.data.speed")
        return Text(f"({speed:>.2f}/s)", style="progress.data.speed")

progress = Progress(
    TextColumn('[green]{task.description}'),
    BarColumn(),
    MofNCompleteColumn(),
    TextColumn('[green][{task.percentage:>3.1f}%]'),
    NaiveTransferSpeedColumn(),
    'ETD:',
    TimeElapsedColumn(),
    'ETA:',
    TimeRemainingColumn(),
    auto_refresh=True
)

# Requests Session Configuration
max_retries = 5
sess = requests.Session()
sess.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}
sess.mount('https://', adapter=requests.adapters.HTTPAdapter(max_retries=max_retries))

# Temperary Filename List (Global Var)
tmp_file_list = []

# Bangumi Info Class
class BiliBGM:
    def __init__(self, md_key: int, title: str):
        self.md_key = md_key
        self.title = title
        self.url = 'https://www.bilibili.com/bangumi/media/md' + str(self.md_key)
    def __str__(self):
        return f'{self.md_key}\t{self.title}\t{self.url}'

# Page Info Extractor     
def extractPageInfo(md_key: int) -> BiliBGM:
    response = sess.get(url='https://www.bilibili.com/bangumi/media/md'+str(md_key))
    if response.status_code == 404:
        return
    html = response.content.decode('utf-8')
    soup = BeautifulSoup(html, 'lxml')
    meta = soup.find_all(name='meta', attrs={'property': 'og:title'})
    if meta:
        return BiliBGM(md_key, meta[0].attrs['content'])

# Data & Cache Treatment    
def loadData(file_path: str) -> list[BiliBGM]:
    loaded_bgm_data = []
    with open(file_path, 'r', encoding='utf-8') as in_fp:
        for info in in_fp.readlines():
            md_key, title, _ = info.split('\t')
            loaded_bgm_data.append(BiliBGM(md_key, title))
    return loaded_bgm_data

def saveData(bgm_data: list[BiliBGM], file_name: str):
    with open('./' + file_name, 'w', encoding='utf-8') as out_fp:
        for bgm in bgm_data:
            print(bgm, file=out_fp)

def clearCache(cache_file_list: list[str]):
    for cf in cache_file_list:
        os.remove('./' + cf)

# Thread Configuration        
class ScanThread(Thread):
    def __init__(self, begin_num: int, end_num: int, sleep_step: int):
        super().__init__()
        self.begin_num = begin_num
        self.end_num = end_num
        self.sleep_step = sleep_step
        self.bgm_data = []
    def run(self):
        for md_key in range(self.begin_num, self.end_num):
            new_BiliBGM = extractPageInfo(md_key)
            if new_BiliBGM:
                self.bgm_data.append(new_BiliBGM)
            no_diff = md_key - self.begin_num + 1
            if no_diff % sleep_step == 0:
                time.sleep(0.25 * min(8, no_diff // sleep_step))
            progress.update(task, advance=1)
        tmp_file_name = f'data_{self.begin_num}_{self.end_num}.tmp'
        saveData(self.bgm_data, tmp_file_name)
        tmp_file_list.append(tmp_file_name)

# Main Program
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('begin_num', type=int, help='beginning index')
    parser.add_argument('end_num', type=int, help='ending index (not included)')
    parser.add_argument('-S', '--sleep-step', nargs='?', type=int, const=200, default=200, help='step number for every sleep')
    parser.add_argument('-C', '--cache-step', nargs='?', type=int, const=1500, default=1500, help='step number for every cache')
    parser.add_argument('-T', '--thread-number', nargs='?', type=int, const=10, default=10, help='max thread number')
    parser.add_argument('-L', '--log', action='store_true', help='enable logging')
    
    args = parser.parse_args()
    
    begin_num: int = args.begin_num
    end_num: int = args.end_num
    sleep_step: int = args.sleep_step
    cache_step: int = args.cache_step
    thread_no: int = args.thread_number
    
    if args.log:
        logging.basicConfig(filename='main.log', encoding='utf-8', level=logging.DEBUG)
    
    progress.start()
    task = progress.add_task(description='BiliBGM', total=(end_num - begin_num))
    thread_IDs = [*range(begin_num, end_num, cache_step), end_num]
    sub_threads = [ScanThread(thread_IDs[idx], thread_IDs[idx + 1], sleep_step) for idx in range(len(thread_IDs) - 1)]
    for tid in range(0, len(sub_threads), thread_no):
        for t in sub_threads[tid:tid + thread_no]:
            t.start()
        for t in sub_threads[tid:tid + thread_no]:
            t.join()
    progress.stop()
    logging.info('media number all treated.')
    
    if tmp_file_list:
        logging.info(tmp_file_list)
        bgm_data = []
        for tmp_name in tmp_file_list:
            bgm_data += loadData('./' + tmp_name)
        logging.info('Cache all read.')
    
    target_file_name: str = 'bangumi_titles.txt'
    saveData(bgm_data, target_file_name)
    logging.info('Data saved to text file.')
    
    clearCache(tmp_file_list)
    logging.info('Cache all clear.')
    
    print('Mission completed.')