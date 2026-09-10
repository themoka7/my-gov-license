#!/usr/bin/env python3
"""index.html(아티팩트용 조각)을 GitHub Pages용 완전한 HTML 문서로 감싼다.

index.html 은 Claude Artifact 로 발행되는 소스라서 <!doctype>·<html>·<head> 가 없다.
아티팩트 플랫폼은 발행 시 charset·viewport·기본 리셋을 자동으로 감싸주지만,
정적 호스팅은 그렇지 않으므로 같은 역할을 여기서 한다. 단일 원본을 유지하기 위한 빌드 단계.
"""
import os, re, shutil, sys

SRC = "index.html"
OUT_DIR = "_site"
BODY_MARKER = '<div class="bar">'

HEAD_RESET = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="정보관리기술사 1교시 단답형 기출 364문항(제110~139회)과 답안지 1면 분량 모범답안.">
<meta name="color-scheme" content="light dark">
<style>
  html{color-scheme:light dark}
  body{margin:0;font-size:14px}
  img{max-width:100%}
  [hidden]{display:none!important}
</style>"""


def main():
    if not os.path.exists(SRC):
        sys.exit("%s 를 찾을 수 없습니다" % SRC)
    src = open(SRC, encoding="utf-8").read()

    if src.lstrip().lower().startswith("<!doctype"):
        sys.exit("%s 가 이미 완전한 문서입니다 — 빌드 단계를 검토하세요" % SRC)
    i = src.find(BODY_MARKER)
    if i < 0:
        sys.exit("본문 시작 표지(%s)를 찾을 수 없습니다" % BODY_MARKER)

    head, body = src[:i].rstrip(), src[i:]
    title = re.search(r"<title>(.*?)</title>", head, re.S)

    doc = (
        "<!doctype html>\n<html lang=\"ko\">\n<head>\n"
        + HEAD_RESET + "\n"
        + head + "\n"
        + "</head>\n<body>\n"
        + body
        + "\n</body>\n</html>\n"
    )

    shutil.rmtree(OUT_DIR, ignore_errors=True)
    os.makedirs(OUT_DIR)
    open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8").write(doc)
    open(os.path.join(OUT_DIR, ".nojekyll"), "w").close()

    print("빌드 완료: %s/index.html" % OUT_DIR)
    print("  제목    : %s" % (title.group(1) if title else "(없음)"))
    print("  head    : %d자" % len(head))
    print("  body    : %d자" % len(body))
    print("  총 크기 : %.1f KB" % (len(doc.encode()) / 1024))


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # 출력이 head 등으로 잘린 경우 — 파일은 이미 기록됨
        os._exit(0)
