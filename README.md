# kgupc-toolkit

KGUPC의 공통 LaTeX 템플릿과 한글 PDF 생성기를 배포하는 Python 패키지입니다. 공개 문제·해설 본문은 archive에, 미공개 대회 자료는 운영진의 로컬과 Polygon에 보관합니다.

## 제공 기능

- 문제 통합본과 개별 PDF를 같은 지문에서 생성
- 표지와 문제 목록을 쪽 번호에서 제외하고 첫 문제를 1쪽으로 시작
- 문제 목록의 내부 링크, 여러 페이지 머리말, 한글 예제 환경
- Beamer 에디토리얼, 해설 목록의 내부 링크
- 공통 글꼴·색상·매크로·로고를 설치 패키지에 포함

문제집 표지는 본문과 별도로 대회명 26pt, 검정색 문서 종류 18pt, 목록 14pt의 서식을 사용합니다. `\title{KGUPC 2027 Spring (Beginner)}`처럼 title에는 대회명만 설정하고, `Problem Set`은 제목 아래 별도 줄에 자동으로 표시합니다. 문서 종류는 `\renewcommand{\problemsetlabel}{...}`로 바꿀 수 있습니다. 표지는 구분선 없이 대회명 → 문서 종류 → 작성자·날짜 → 목차(`Contents`) 순서입니다. 날짜는 `\date{2025-10-29}`처럼 설정합니다. 제목 영역은 본문 영역 위쪽에서 95pt 내려온 위치에 시작하며, 200pt 높이의 고정 영역 안에 작성자와 날짜를 왼쪽과 오른쪽으로 정렬합니다. 제목과 문서 종류를 위한 영역은 72pt 높이입니다. 목록 시작 위치는 문제 수에 영향을 받지 않으며, 추가 항목은 아래로 이어집니다. 표지에는 쪽 번호를 표시하지 않습니다. 목록의 제목과 쪽수 모두 해당 문제로 연결됩니다. 표지 배치는 `resources/latex/core/problem-set.tex`에서 관리하며, 본문의 문단 간격과 예제 서식은 `resources/latex/layouts/problem.tex`에서 관리합니다.

## 설치와 호출

문제 본문은 문단 내부 줄 간격을 `1.08`, 문단 사이 간격을 `0.75em`으로 설정합니다. `enumerate`와 `itemize`는 항목 사이 `0.2em`, 목록 안 문단 사이 `0pt`를 사용합니다. 입력·출력·제한 등의 제목 앞 간격은 `3.5ex`로 두어 구역을 구분하고, 제목 바로 아래 간격은 `0.5ex`로 유지합니다. 예제는 별도의 ‘예제’ 제목 없이 ‘예제 입력 N / 예제 출력 N’ 상자 제목으로 표시합니다. 기존 `\SampleSection` 호출은 예제 앞 간격을 넣으므로 계속 사용할 수 있습니다.

Python 3.10 이상, XeLaTeX와 latexmk가 필요합니다. 아래 명령은 toolkit 저장소에서 실행합니다.

```powershell
python -m pip install .
kgupc-toolkit build C:/private/2026-fall/problems/main.tex
kgupc-toolkit build C:/private/2026-fall/solutions/main.tex
kgupc-toolkit resources
```

Python API도 사용할 수 있습니다.

```python
from pathlib import Path
from kgupc_toolkit.build import build, find_main

pdfs = build(find_main(Path("C:/private/2026-fall/problems/main.tex")),
             lock=Path("C:/private/2026-fall/toolkit.lock.json"))
```

렌더러는 각 문서의 무시되는 `build/toolkit-path.tex`를 생성합니다. 문서에는 다음을 사용합니다. 설치 경로를 직접 복사하지 않습니다.

```tex
\documentclass[11pt]{article}
\input{build/toolkit-path.tex}
\input{\KGUPCToolkitRoot/latex/layouts/problem.tex}
% 대회별 title, author, date, contestname 설정
\begin{document}
\problemsetfrontmatter
\input{problem-list.tex}
\checkselectedproblem
\end{document}
```

에디토리얼은 beamer 문서 클래스와 `\KGUPCToolkitRoot/latex/layouts/beamer.tex`를 사용합니다. 개별 본문과 대회 메타데이터는 toolkit에 넣지 않습니다.

## 버전과 원본 보존

첫 정식 버전은 `1.0.0`이며 `v1.0.0` Git 태그로 소스를 고정합니다. `release-lock.json`은 이 버전의 패키지 내용 해시입니다. 각 대회는 자체 환경에 패키지를 설치하고 `toolkit.lock.json`에 버전과 패키지 내용 SHA-256을 고정합니다.

현재 개발 작업에서는 요청에 따라 문단 사이 여백과 예제 글꼴을 조정하면서 버전 번호 `1.0.0`을 유지합니다. 문단 내부의 줄 간격은 원래 `1.08`이며, 빈 줄로 나뉜 문단 사이에는 `0.75em` 여백을 둡니다. 예제 입출력은 Consolas를 사용합니다. 이 작업 트리의 `release-lock.json`은 조정된 내용 해시이므로, 기존 `v1.0.0` 태그의 소스·wheel과 내용이 다릅니다. 이 변경을 사용하는 대회에는 해당 소스 또는 일치하는 wheel을 설치해야 합니다. 기존 태그는 보존하며, 기존 lock으로 고정된 다른 대회에는 자동 적용하지 않습니다.

```powershell
kgupc-toolkit fingerprint
kgupc-toolkit verify-lock C:/private/2026-fall/toolkit.lock.json
```

fingerprint 출력은 새 대회의 lock으로 저장할 수 있습니다. 기존 대회의 lock을 최신 템플릿에 맞춰 덮어쓰지 않습니다. 설치된 버전이나 템플릿·글꼴·렌더러의 내용이 다르면 빌드를 거부합니다. 개발용 소스 변경은 일반 설치된 과거 대회의 환경에 반영되지 않습니다. 과거 대회에는 editable 설치를 사용하지 않습니다.

템플릿을 수정하면 `src/kgupc_toolkit/__init__.py`의 버전을 올리고 새 릴리스를 배포합니다. 릴리스 wheel과 해당 Git 커밋을 보관하며, 기존 태그·릴리스 파일을 교체하지 않습니다. GitHub 조직은 소비 저장소와 달라도 됩니다.

```powershell
python -m pip wheel --no-deps --wheel-dir dist .
```

다른 컴퓨터에서는 고정된 태그에서 설치할 수 있습니다. PyPI에 등록된 패키지는 아닙니다.

```powershell
python -m pip install "kgupc-toolkit @ git+https://github.com/SOLUTIO-NEST/kgupc-toolkit.git@v1.0.0"
kgupc-toolkit verify-lock C:/private/2025/toolkit.lock.json
```

wheel은 위 태그를 checkout한 소스에서 만들고 배포할 수 있습니다. wheel을 만든 뒤 `verify-lock`으로 내용 해시를 확인합니다. 같은 버전의 소스·태그를 수정하지 않으며, 이후 템플릿 변경은 `1.0.1` 이상의 새 버전으로 배포합니다. 재현 시 TeX Live 버전과 OS 글꼴 사용 여부도 기록해야 합니다.

## 구조와 검증

Polygon 형태의 분리 지문도 지원합니다. 문제의 조립 파일에는 `\polygonstatement{A}{statement-sections/korean}`만 두고, 같은 문제 폴더의 `statement.json`에 `language`, `timeLimit`(ms), `memoryLimit`(MB), `sampleLayout`을 설정합니다. 지문 폴더에는 `name.tex`, `legend.tex`, `input.tex`, `output.tex`, 선택 `notes.tex`, `example.01` / `example.01.a`를 둡니다. 선택 `interaction.tex`와 `scoring.tex`도 표시하며, 풀이 `tutorial.tex`는 문제 PDF에서 제외합니다.

예제는 숫자 순서로 읽으며, 입력·출력 쌍이 불완전하면 실패합니다. 짧은 예제는 한 행에 입력·출력을 나란히, 긴 예제는 전체 폭으로 나눠 출력합니다. `sampleLayout`의 기본값은 `auto`이고 `paired` / `stacked`로 지정할 수도 있습니다. 본문에는 KGUPC 전용 레이아웃 명령을 넣지 않습니다. 조립 파일은 무시되는 문서의 `build/statements/`에 생성됩니다. 기존 단일 tex 지문도 계속 지원합니다.

`statement.json`은 toolkit 자체의 메타데이터이며 Polygon 공식 패키지 파일로 취급하지 않습니다. pol2dom은 공식 API의 [지문 필드](https://codeforces.github.io/polygon-misc/API#statement)와 [테스트 표시 설정](https://codeforces.github.io/polygon-misc/API#test)을 이 구조로 변환합니다.

`src/kgupc_toolkit/resources/latex`에 테마, `fonts`와 `images`에 공통 자산이 있습니다. `build.py`는 공유 렌더러이고 `resources.py`는 경로와 버전 검증을 담당합니다.

설치한 환경에서 실행합니다.

```powershell
python -m unittest discover -s tests -v
```

경로 독립성, 잘못된 문제 목록, 같은 버전에서 바뀐 템플릿 거부를 검사합니다. 실제 PDF 통합 검증은 kgupc-archive의 `tests/verify_pdfs.py`에서 실행합니다.

코드 라이선스와 기존 Beamer 테마의 출처는 LICENSE를 참고하세요. 패키지의 외부 글꼴·이미지에는 각각 원래 권리가 적용됩니다.
