# Test Isolated App (WebApp Launcher 샘플 애플리케이션)

이 프로젝트는 **WebApp Launcher** 환경에서 어플리케이션이 어떻게 구성되고 기동되는지 보여주는 공식 개발자 가이드이자 초경량 샘플 애플리케이션입니다.

WebApp Launcher는 가벼운 포인터 파일(`.wapk`)을 더블 클릭하는 것만으로 깃허브 원본 저장소에서 코드를 안전하게 내려받고, 중복 없는 고유 폴더 구조와 격리된 의존성 환경(pnpm, uv)을 자동으로 구축해 실행합니다.

---

## 📂 프로젝트 구조 (Project Structure)

```
test-isolated-app/
├── metadata.toml             # 런처 패키지 메타데이터 (GitHub 연동 및 구조 정의)
├── TestIsolatedApp.webapp    # 웹뷰 창 스타일 및 백엔드 실행 구성 정의 파일
├── run.ps1                   # 어플리케이션 진입점 실행 스크립트 (PowerShell)
├── requirements.txt          # Python 의존성 라이브러리 목록 (uv venv 연동)
├── package.json              # Node.js 의존성 라이브러리 목록 (pnpm-store 연동)
└── server/
    └── app.py                # 초경량 HTTP 백엔드 서버 (포트 자동 할당 및 헬로월드)
```

---

## 📑 핵심 구성 파일 상세 설명

### 1. `metadata.toml` (메타데이터 정의)
런처 설치기가 깃허브에서 원본 소스코드 ZIP을 다운로드한 후, 내부 핵심 파일들의 상대 위치를 찾을 수 있도록 정의하는 경로 매핑 파일입니다.

```toml
name = "TestIsolatedApp"
version = "1.0.0"
repository = "https://github.com/hhsshoo12/webapp_test" # 소스코드가 업로드된 깃허브 주소
ref = "main" # 빌드/체크아웃할 브랜치명 또는 태그/커밋 해시

# 소스 추출 후 내부 파일들의 상대 경로 지정
webapp_path = "TestIsolatedApp.webapp"   # .webapp 설정 파일의 위치
run_path = "run.ps1"                     # 어플리케이션 진입 실행 스크립트 위치
server_path = "server"                   # 백엔드 코드가 모여있는 서버 폴더 위치
```

---

### 2. `TestIsolatedApp.webapp` (웹앱 런처 프로필)
런처의 브라우저 창 스펙과 구동 방식을 Electron에 지시하는 핵심 설정 파일입니다.

```toml
name = "TestIsolatedApp"
url = "http://localhost:{PORT}" # {PORT} 플레이스홀더는 실행 시 동적으로 치환됩니다.

[window]
fullscreen = false
frameless = false
transparent_background = false

[window.size]
width = 600
height = 400
use_default = false

[window.position]
use_default = true

[server]
script = "run.ps1"               # 기동 시 동시 실행할 백엔드 진입점 파일 지정
keep_alive = false
```

---

### 3. `run.ps1` (자식 프로세스 진입점)
웹뷰 창이 열리기 전 백엔드 프로세스를 제어하는 파워셸 실행 파일입니다.
* **환경 격리 보장**: 실행 시 WebApp Launcher가 **시스템 변수를 영구 오염시키지 않고**, 오직 이 프로세스의 일회성 환경 변수 상단에 공유 가상환경 경로를 주입합니다.
* 이에 따라 이 스크립트 내부에서 `python` 명령어를 수행하면 전역 파이썬이 아닌 공유 가상환경(`.venv`)의 실행 파일이 자동으로 동작합니다.

```powershell
Write-Host "Verifying Python dependencies inside the virtual environment..."
# 공유 가상환경 내에 설치된 requests 모듈 임포트 검증
python -c "import requests; print('requests version successfully imported:', requests.__version__)"

# 백엔드 서버 실행
python server/app.py
```

---

### 4. `server/app.py` (포트 Allocator 연동 및 HTTP 구동)
런처 내부의 포트 분배 서버(Port Allocator, `23001`번 포트)와 통신하여 충돌하지 않는 고유 포트를 할당받고 웹 서버를 가동하는 예제입니다.

```python
import http.server
import socketserver
import urllib.request
import os

# 1. 런처 인증 토큰 로드 (~/.webapp/.port_token)
home_dir = os.path.expanduser('~')
token_file = os.path.join(home_dir, '.webapp', '.port_token')
with open(token_file, 'r') as f:
    token = f.read().strip()

# 2. 포트 서버(23001)에 통신하여 남는 포트 요청
req = urllib.request.Request("http://127.0.0.1:23001/get-port?app=TestIsolatedApp")
req.add_header('Authorization', token)

with urllib.request.urlopen(req) as response:
    PORT = int(response.read().decode().strip())

# 3. 할당받은 포트로 간단한 Hello World HTTP 웹서버 구동
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("<h1>Hello World</h1>".encode("utf-8"))

socketserver.TCPServer(("127.0.0.1", PORT), Handler).serve_forever()
```

---

## ⚡ 격리 및 공유 공간 의존성 원리 (Dependencies Isolation)

어플리케이션마다 무거운 `node_modules` 폴더와 `venv` 가상환경을 별도로 가지고 있으면 하드 디스크 용량이 낭비됩니다. WebApp Launcher는 설치 및 구동 단계에서 이를 영리하게 격리/공유합니다.

1. **Python (`uv` 사용)**:
   * 설치 시 `requirements.txt`가 감지되면, 유저 홈 경로의 `%USERPROFILE%\webapp\.packages\.venv\` 공간에 공유 가상환경을 uv로 생성(혹은 업데이트)하고 패키지를 설치합니다.
   * 모든 웹앱이 이 가상환경을 공유하여 중복 용량을 최소화합니다.
2. **Node.js (`pnpm-store` 사용)**:
   * 설치 시 `package.json`이 감지되면, `%USERPROFILE%\webapp\.packages\pnpm-store\` 경로를 하드 링크 저장소로 지정하고 설치합니다.
   * 물리적으로 하나의 모듈 버전은 디스크에 딱 1개만 저장되며, 각 어플리케이션은 링크로 연결되어 실제 점유 디스크 크기가 **0바이트**에 수렴하게 됩니다.

---

## 📦 `.wapk` 패키징 방법 (How to Package)

런처 배포 시 사용자에게 코드 전체를 보낼 필요 없이, 다음 단계로 만들어진 매우 가벼운 **포인터 파일**만 배포하면 됩니다.

1. 프로젝트 내의 `metadata.toml` 파일을 생성하여 저장소 정보와 상대 경로를 기재합니다.
2. `metadata.toml` 파일(및 필요한 경우 아이콘 파일 `icon.ico`)을 선택해 **최고 압축률의 ZIP 파일**로 압축합니다.
3. 압축 파일의 이름을 `어플리케이션명.wapk`로 변경합니다. (예: `TestIsolatedApp.wapk`)
4. 완성된 `.wapk` 파일을 런처로 더블 클릭해 실행하면 다운로드 및 격리 배포 과정이 자동으로 시작됩니다.
