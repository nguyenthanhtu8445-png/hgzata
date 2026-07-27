"""
ðŸ¦‰ Game Text Translator - Android App
Cháº¡y trÃªn Kivy, dá»‹ch file game English â†’ Vietnamese
"""

import os, re, json, time, zipfile, shutil, tempfile, threading
import urllib.request, urllib.parse, concurrent.futures
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window

# â”€â”€â”€ Translator Engine â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
CTRL_RE = re.compile(r'\\(?:c\[\d+\]|m\[\w+\]|C\[\d+\]|SET\w+(?:\[[^\]]*\])?|Lshake|Rshake|plf|prf|PLF|PRF|narr|Cam\w+|\.\.\.|opt[BD]\[[^\]]*\])')
EN_RE = re.compile(r'[A-Za-z]')
KEY_RE = re.compile(r'^[\w]+/[\w]+$')
TEXT_EXT = {'.txt', '.json', '.jsonl', '.yaml', '.yml', '.ini', '.srt', '.properties', '.csv', '.tsv', '.lua', '.xml', '.rpy', '.po'}

def log(s, cb=None):
    print(s)

def has_en(s): return bool(EN_RE.search(s))

def walk_text_files(src):
    files = []
    for r, _, fs in os.walk(src):
        for f in fs:
            ext = os.path.splitext(f)[1].lower()
            if ext not in TEXT_EXT: continue
            fp = os.path.join(r, f)
            try:
                with open(fp, 'r', encoding='utf-8') as fh: fh.read(128)
                files.append(os.path.relpath(fp, src))
            except: pass
    return sorted(files)

def skip_line(s):
    s = s.strip()
    if not s: return True
    if re.match(KEY_RE, s): return True
    if s.startswith('#'): return True
    return False

def segment(line):
    parts = CTRL_RE.split(line)
    codes = CTRL_RE.findall(line)
    res = []; ci = 0
    for i, p in enumerate(parts):
        if i > 0 and ci < len(codes):
            res.append(('code', codes[ci])); ci += 1
        if p: res.append(('text', p))
    return res

def extract_texts_from_line(line):
    raw = line.strip(); texts = []
    if skip_line(raw): return texts
    for tp, tx in segment(raw):
        if tp != 'text': continue
        tx = tx.strip()
        if tx and has_en(tx) and len(tx) >= 2:
            for sep in ['ï¼š', ':']:
                if sep in tx:
                    after = tx.split(sep, 1)[1].strip()
                    if after and has_en(after) and len(after) >= 2: texts.append(after); break
            else: texts.append(tx)
    return texts

def translate_text(text):
    url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=vi&dt=t&q={urllib.parse.quote(text)}'
    for _ in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = json.loads(urllib.request.urlopen(req, timeout=15).read().decode('utf-8'))
            if data and data[0] and data[0][0]: return data[0][0][0] or text
        except: time.sleep(1)
    return text

def apply(text, mapping):
    s = text.strip()
    if not s or not has_en(s) or len(s) < 2: return text
    for sep in ['ï¼š', ':']:
        if sep in text:
            before, after = text.split(sep, 1)
            a_s = after.strip()
            if a_s and has_en(a_s) and len(a_s) >= 2:
                trans = mapping.get(a_s, a_s)
                if trans != a_s:
                    wl = after[:len(after)-len(after.lstrip())]
                    wr = after[len(after.rstrip()):] if after.rstrip() else ''
                    return before + sep + wl + trans + wr
    trans = mapping.get(s, s)
    if trans != s:
        wl = text[:len(text)-len(text.lstrip())]
        wr = text[len(text.rstrip()):]
        return wl + trans + wr
    return text

def rebuild_line(line, mapping):
    s = line.rstrip('\r\n')
    st = s.strip()
    if skip_line(st): return s, False
    parts = segment(st)
    new_parts = []; changed = False
    for tp, tx in parts:
        if tp == 'code': new_parts.append(tx)
        else:
            t = apply(tx, mapping); new_parts.append(t)
            if t != tx: changed = True
    if not changed: return s, False
    lead = s[:len(s)-len(s.lstrip())]
    trail = '' if len(s) == len(s.rstrip()) else s[len(s.rstrip()):]
    return lead + ''.join(new_parts) + trail, True


class Translator:
    def __init__(self, status_cb=None, progress_cb=None):
        self.status_cb = status_cb or (lambda x: None)
        self.progress_cb = progress_cb or (lambda a, b: None)

    def run(self, src, dst):
        t0 = time.time()
        os.makedirs(dst, exist_ok=True)
        files = walk_text_files(src)
        if not files:
            self.status_cb("âŒ KhÃ´ng tÃ¬m tháº¥y file text nÃ o.")
            return

        all_texts = []
        for rel in files:
            for line in open(os.path.join(src, rel), encoding='utf-8', errors='ignore'):
                all_texts.extend(extract_texts_from_line(line))
        unique = list(dict.fromkeys(all_texts))
        self.status_cb(f"ðŸ“Š {len(files)} files, {len(unique)} unique texts")

        if not unique:
            self.status_cb("âœ… KhÃ´ng cÃ³ text cáº§n dá»‹ch.")
            for rel in files:
                sp = os.path.join(src, rel); dp = os.path.join(dst, rel)
                os.makedirs(os.path.dirname(dp), exist_ok=True); shutil.copy2(sp, dp)
            return

        # Translate
        mapping = {}; total = len(unique)
        self.status_cb(f"ðŸŒ Äang dá»‹ch {total} texts...")
        done = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as exe:
            futs = {exe.submit(lambda t: (t, translate_text(t)), t): t for t in unique}
            for f in concurrent.futures.as_completed(futs):
                o, r = f.result(); mapping[o] = r
                done += 1
                if done % 500 == 0 or done == total:
                    self.progress_cb(done, total)
                    self.status_cb(f"   {done}/{total} ({int(done*100/total)}%)")

        # Rebuild
        total_changes = 0
        for rel in files:
            sp = os.path.join(src, rel); dp = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            lines = open(sp, encoding='utf-8', errors='ignore').readlines()
            out = []; changes = 0
            for line in lines:
                rebuilt, mod = rebuild_line(line, mapping); out.append(rebuilt)
                if mod: changes += 1
            open(dp, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
            total_changes += changes

        elapsed = time.time() - t0
        self.status_cb(f"âœ… XONG: {total_changes:,} changes, {len(files)} files ({elapsed:.0f}s)")
        self.status_cb(f"ðŸ“ Output: {dst}")


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10

        # Title
        title = Label(
            text="ðŸ¦‰ Game Text Translator",
            size_hint_y=0.1, font_size='20sp', bold=True
        )
        self.add_widget(title)

        # SRC
        self.add_widget(Label(text="ðŸ“‚ Folder ENG:", size_hint_y=0.05, halign='left'))
        self.src_input = TextInput(
            text="/storage/emulated/0/Download/ENG",
            size_hint_y=0.08, multiline=False
        )
        self.add_widget(self.src_input)

        # DST
        self.add_widget(Label(text="ðŸ“ Folder xuáº¥t VIE:", size_hint_y=0.05, halign='left'))
        self.dst_input = TextInput(
            text="/storage/emulated/0/Download/VIE",
            size_hint_y=0.08, multiline=False
        )
        self.add_widget(self.dst_input)

        # ZIP mode
        zip_row = BoxLayout(size_hint_y=0.06, spacing=10)
        self.zip_input = TextInput(
            text="hoáº·c kÃ©o tháº£ file .zip vÃ o Ä‘Ã¢y",
            size_hint_x=0.7, multiline=False
        )
        self.zip_btn = Button(text="ðŸ“¦ Xá»­ lÃ½ ZIP", size_hint_x=0.3)
        self.zip_btn.bind(on_press=self.on_zip)
        zip_row.add_widget(self.zip_input)
        zip_row.add_widget(self.zip_btn)
        self.add_widget(zip_row)

        # Translate button
        self.go_btn = Button(text="ðŸš€ Dá»‹ch ngay", size_hint_y=0.08)
        self.go_btn.bind(on_press=self.on_translate)
        self.add_widget(self.go_btn)

        # Progress
        self.progress = ProgressBar(max=100, value=0, size_hint_y=0.04)
        self.add_widget(self.progress)

        # Status log
        self.status = Label(
            text="Sáºµn sÃ ng ðŸ¦‰", size_hint_y=0.06, font_size='14sp'
        )
        self.add_widget(self.status)

        # Log scroll
        self.log_area = TextInput(
            text="", readonly=True, size_hint_y=0.4, font_size='12sp'
        )
        self.add_widget(self.log_area)

    def log(self, msg):
        def upd(dt):
            self.log_area.text += msg + "\n"
            self.log_area.cursor = (0, len(self.log_area.text))
        Clock.schedule_once(upd)

    def set_status(self, msg):
        def upd(dt):
            self.status.text = msg if len(msg) < 80 else msg[:77]+"..."
        Clock.schedule_once(upd)
        self.log(msg)

    def set_progress(self, current, total):
        def upd(dt):
            self.progress.value = int(current * 100 / total) if total else 0
        Clock.schedule_once(upd)

    def on_translate(self, instance):
        src = self.src_input.text.strip()
        dst = self.dst_input.text.strip()
        if not src or not os.path.isdir(src):
            self.set_status("âŒ Folder ENG khÃ´ng tá»“n táº¡i!")
            return
        if not dst:
            dst = src + "_VIE"
        self.go_btn.disabled = True
        self.go_btn.text = "â³ Äang dá»‹ch..."
        self.progress.value = 0

        t = Translator(
            status_cb=self.set_status,
            progress_cb=self.set_progress
        )
        thread = threading.Thread(target=self._run_translate, args=(t, src, dst))
        thread.daemon = True
        thread.start()

    def _run_translate(self, t, src, dst):
        try:
            t.run(src, dst)
        except Exception as e:
            self.set_status(f"âŒ Lá»—i: {e}")
        finally:
            def upd(dt):
                self.go_btn.disabled = False
                self.go_btn.text = "ðŸš€ Dá»‹ch ngay"
            Clock.schedule_once(upd)

    def on_zip(self, instance):
        zip_path = self.zip_input.text.strip()
        if not zip_path or not os.path.isfile(zip_path) or not zip_path.lower().endswith('.zip'):
            self.set_status("âŒ File .zip khÃ´ng há»£p lá»‡!")
            return
        self.set_status(f"ðŸ“¦ Äang giáº£i nÃ©n: {os.path.basename(zip_path)}")
        tmp = tempfile.mkdtemp(prefix='gtt_')
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(tmp)
            # Detect ENG folder
            src = tmp
            for item in sorted(os.listdir(tmp)):
                fp = os.path.join(tmp, item)
                if os.path.isdir(fp) and item.upper() in ('ENG', 'EN', 'ENGLISH', 'TEXT'):
                    src = fp; break
            outdir = tempfile.mkdtemp(prefix='gtt_out_')
            outzip = os.path.join(os.path.dirname(zip_path), 'VIE_' + os.path.basename(zip_path))

            t = Translator(
                status_cb=self.set_status,
                progress_cb=self.set_progress
            )
            t.run(src, outdir)

            with zipfile.ZipFile(outzip, 'w', zipfile.ZIP_DEFLATED) as z:
                for r, _, fs in os.walk(outdir):
                    for f in fs:
                        fp = os.path.join(r, f)
                        z.write(fp, os.path.relpath(fp, outdir))
            self.set_status(f"ðŸ—œï¸ Zip: {outzip}")
        except Exception as e:
            self.set_status(f"âŒ Lá»—i: {e}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class GTApp(App):
    def build(self):
        self.title = "ðŸ¦‰ Game Text Translator"
        return MainLayout()


if __name__ == '__main__':
    GTApp().run()
