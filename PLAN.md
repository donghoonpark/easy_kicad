# easy_kicad

LCSC 번호를 넣으면 `easyeda2kicad.py` 기반으로 KiCad용 심볼, 풋프린트, 3D 모델을 미리보고 한 번에 import하는 데스크톱 GUI 앱.

## 한 줄 결론

이 프로젝트는 `Python 백엔드 + 웹 프론트엔드 + 가벼운 데스크톱 셸` 조합이 가장 잘 맞는다.  
추천 스택은 아래와 같다.

- 데스크톱 셸: `pywebview`
- 백엔드: `Python 3.11+`, `FastAPI`, `Pydantic v2`, `easyeda2kicad.py`
- 프론트엔드: `React`, `TypeScript`, `Vite`, `Tailwind CSS`, `shadcn/ui`
- 상태/데이터: `TanStack Query`, `Zustand`
- 3D 미리보기: `three.js`
- 패키징: `PyInstaller`
- 설정 저장: `platformdirs` + `JSON` 또는 `TOML`

## 프로젝트 이름

### `easy_kicad`

의미:

- LCSC 부품을 KiCad 라이브러리로 "옮겨오는 포트"라는 뜻
- 기능이 바로 이해되고, 앱 이름으로도 무난함
- 추후 `easy_kicad Desktop`, `easy_kicad CLI`처럼 확장하기 좋음

## 왜 이 스택이 맞는가

### 1. 핵심 라이브러리가 Python 중심이다

`easyeda2kicad.py`는 Python 패키지이자 CLI이며, 내부적으로 EasyEDA API를 호출한 뒤 심볼/풋프린트/3D 모델을 생성한다.  
우리가 원하는 기능은 단순 CLI 실행보다 한 단계 더 깊다.

- LCSC 번호 입력 후 부품 정보 조회
- 심볼/풋프린트/3D 미리보기
- 설정값 반영 후 import
- proxy, custom certificate, certificate 검증 무시 옵션

이 요구사항은 CLI를 감싸는 것보다 Python 레벨에서 라이브러리 내부 importer/exporter를 직접 다루는 편이 훨씬 낫다.

### 2. proxy / certificate 옵션이 업스트림에 바로 있지 않다

업스트림 코드를 보면 EasyEDA API 호출이 `requests.get(...)`로 직접 박혀 있다. 즉, 아래 옵션은 앱 쪽 adapter 레이어에서 보강해야 한다.

- HTTP/HTTPS proxy
- custom CA bundle
- SSL certificate verify 끄기
- timeout / retry

그래서 Rust 메인앱이 Python CLI를 단순 호출하는 구조보다, Python 백엔드에서 네트워크 세션을 직접 제어하는 구조가 더 자연스럽다.

### 3. 웹 기술로 예쁜 UI를 만들기 쉽다

프론트엔드를 React + Vite + Tailwind로 두면:

- 카드형 3분할 미리보기 레이아웃
- 스무스한 검색/상태 전환
- 설정 모달/사이드 패널
- 파일 경로 선택, 경고 배지, 토스트

같은 UI를 빠르게 만들 수 있다.

### 4. Tauri/Electron보다 초기 복잡도가 낮다

Tauri나 Electron도 가능하지만, 이번 프로젝트의 어려움은 "데스크톱 셸"보다 "Python 라이브러리와의 밀착 통합"에 있다.  
초기 버전은 `pywebview + FastAPI + React`가 구현 속도와 유지보수성의 균형이 가장 좋다.

## 비추천 대안

### Tauri + React + Python sidecar

장점:

- 앱이 가볍고 배포 결과물이 세련됨
- 네이티브 파일 대화상자, 설정 저장이 좋음

단점:

- Python sidecar 번들링과 플랫폼별 패키징이 초기에 더 복잡함
- proxy / SSL adapter / preview 파이프라인을 결국 Python 쪽에서 따로 관리해야 함

판단:

- 나중에 2차 리팩터링 대상으로는 좋음
- 하지만 1차 버전에는 과투자

### Electron + React + Python subprocess

장점:

- 익숙한 조합
- 프론트 생태계 풍부

단점:

- 메모리 사용량이 큼
- Python 패키징 문제는 그대로 남음
- 이번 요구사항에는 Electron만의 큰 이점이 적음

판단:

- 굳이 지금 선택할 이유가 약함

## 추천 아키텍처

```text
pywebview window
  -> local FastAPI app
    -> easyeda adapter service
      -> easyeda2kicad.py internals
    -> preview generator
    -> import service
  -> React frontend
```

### 데스크톱 셸

- `pywebview`
- 역할:
  - 로컬 창 생성
  - React 앱 표시
  - 파일 선택 대화상자 연동
  - 앱 종료/창 상태 관리

선정 이유:

- Python 프로젝트와 궁합이 좋음
- HTML/CSS/JS UI를 그대로 쓸 수 있음
- 초기 배포가 Tauri sidecar보다 단순함

### 백엔드

- `Python 3.11+`
- `FastAPI`
- `Pydantic v2`
- `easyeda2kicad.py`

역할:

- LCSC 번호 검증
- EasyEDA 데이터 조회
- 심볼/풋프린트/3D preview용 데이터 생성
- 실제 KiCad 라이브러리 import 수행
- 설정 저장/불러오기
- proxy / certificate / timeout 처리

### 프론트엔드

- `React`
- `TypeScript`
- `Vite`
- `Tailwind CSS`
- `shadcn/ui`
- `TanStack Query`
- `Zustand`
- `three.js`

역할:

- 검색 화면
- 3분할 preview pane
- Import 버튼 단일 액션
- 설정 창
- 상태 표시와 에러 메시지

## 화면 설계 방향

스타일 목표는 "EDA 툴 느낌 + 과하게 무겁지 않은 세련됨"이다.

- 기본 톤: charcoal / slate / warm gray
- 포인트 컬러: copper 또는 cyan 중 하나로 통일
- 배경: 옅은 grid texture + soft gradient
- 폰트:
  - 제목: `Space Grotesk` 또는 `Sora`
  - 본문: `IBM Plex Sans` 또는 `Instrument Sans`
  - 숫자/경로/ID: `JetBrains Mono`

핵심 화면:

1. 검색 화면
   - 상단에 LCSC 번호 입력창
   - 바로 아래 부품 메타 정보
   - 하단에 `Symbol / Footprint / 3D` 3개 pane
   - 오른쪽 위 또는 하단 고정 `Import` 버튼

2. 설정 창
   - 라이브러리 기본 저장 위치
   - 라이브러리 베이스 이름
   - overwrite 여부
   - KiCad 심볼 포맷(v6+ 기본, v5 legacy 옵션)
   - project-relative 3D path 여부
   - proxy URL
   - custom CA bundle 경로
   - certificate verify 무시 토글
   - 네트워크 테스트 버튼

3. import 결과 다이얼로그
   - 저장된 심볼 파일
   - 생성된 `.pretty`
   - 생성된 `.3dshapes`
   - overwrite/skip 요약

## preview 전략

### Symbol preview

우선순위:

1. 백엔드에서 EasyEDA symbol 객체를 SVG-friendly JSON으로 변환
2. 프론트에서 SVG로 렌더링

이유:

- 브라우저에서 가장 가볍고 빠름
- 확대/축소가 쉬움
- theme 대응이 쉬움

### Footprint preview

우선순위:

1. 백엔드에서 패드/라인/홀 정보를 JSON으로 변환
2. 프론트에서 2D canvas 또는 SVG로 렌더링

이유:

- KiCad 실행 없이 즉시 미리보기 가능
- pad 색상, drill hole, silkscreen 분리 표현 가능

### 3D preview

우선순위:

1. `.wrl` 기반 미리보기
2. `three.js`로 회전/줌 지원
3. `.step`은 저장 대상으로 유지하고, 웹 preview는 WRL 위주로 처리

이유:

- 브라우저에서 STEP 직접 미리보는 것은 구현 비용이 큼
- 업스트림은 WRL/STEP 모두 저장하므로, 미리보기는 WRL로 충분함

## 백엔드 adapter 설계

업스트림을 그대로 CLI 실행하지 말고, 얇은 adapter 레이어를 둔다.

### 예상 모듈 구조

```text
backend/
  app.py
  api/
    parts.py
    settings.py
  core/
    config.py
    paths.py
    logging.py
    network.py
  services/
    easyeda_adapter.py
    preview_service.py
    import_service.py
  schemas/
    part.py
    settings.py
```

### 핵심 포인트

- `easyeda_adapter.py`
  - 업스트림 importer/exporter 호출 담당
  - 네트워크 옵션을 반영한 request layer 주입

- `network.py`
  - proxy
  - verify ssl
  - CA bundle
  - timeout
  - retry

- `preview_service.py`
  - symbol/footprint를 frontend용 JSON 또는 SVG로 변환

- `import_service.py`
  - 출력 경로 생성
  - overwrite 정책 적용
  - import 결과 요약 반환

## API 초안

### `POST /api/parts/inspect`

입력:

```json
{
  "lcscId": "C2040"
}
```

출력:

```json
{
  "part": {
    "lcscId": "C2040",
    "name": "NE555",
    "manufacturer": "TI"
  },
  "symbolPreview": {},
  "footprintPreview": {},
  "model3d": {
    "available": true,
    "previewUrl": "/api/parts/C2040/model.wrl"
  }
}
```

### `POST /api/parts/import`

입력:

```json
{
  "lcscId": "C2040",
  "target": {
    "libraryBasePath": "/Users/name/Documents/KiCad/libs/easy_kicad",
    "overwrite": true,
    "projectRelative3d": false
  }
}
```

출력:

```json
{
  "success": true,
  "files": {
    "symbol": ".../easy_kicad.kicad_sym",
    "footprintDir": ".../easy_kicad.pretty",
    "modelDir": ".../easy_kicad.3dshapes"
  }
}
```

### `GET /api/settings`

사용자 설정 조회.

### `PUT /api/settings`

사용자 설정 저장.

### `POST /api/settings/test-connection`

현재 proxy / CA / certificate 설정으로 EasyEDA 연결 확인.

## 설정 모델 초안

```json
{
  "libraryBasePath": "",
  "defaultLibraryName": "easy_kicad",
  "overwrite": false,
  "projectRelative3d": false,
  "proxyUrl": "",
  "caBundlePath": "",
  "ignoreSslVerification": false,
  "requestTimeoutSeconds": 20
}
```

## 구현 시 꼭 챙길 제약

### 1. AGPL-3.0 라이선스 확인

`easyeda2kicad.py`는 AGPL-3.0이다.  
이 앱을 배포할 계획이라면 라이선스 의무를 먼저 검토해야 한다.

### 2. 업스트림 requests 하드코딩

proxy / certificate 옵션은 바로 꽂히지 않는다.  
가장 현실적인 선택지는 아래 둘 중 하나다.

1. adapter 레이어에서 `EasyedaApi`를 감싸고 요청 함수를 주입
2. 필요한 경우 작은 fork를 유지

초기에는 1번으로 시작하고, 불안정하면 2번으로 전환한다.

### 3. 3D preview는 WRL 우선

STEP까지 브라우저에서 완벽히 다루려 하면 일정이 늘어난다.  
미리보기는 WRL 위주로 가고, STEP은 import 산출물로 저장만 하는 전략이 현실적이다.

### 4. overwrite는 안전장치 필요

- import 전에 대상 파일 존재 여부 확인
- overwrite 시 백업 파일 생성 옵션 제공
- UI에서 변경 요약 표시

## 개발 단계 제안

### Phase 0. 기술 검증

- `easyeda2kicad.py` importer/exporter를 Python 코드에서 직접 호출
- proxy / SSL 옵션 주입 방식 검증
- LCSC 샘플 3~5개로 symbol/footprint/3D 데이터 확보

완료 기준:

- 코드 한 번으로 inspect + import가 가능

### Phase 1. 백엔드 골격

- FastAPI 앱 생성
- settings 모델 생성
- `inspect`, `import`, `settings` API 초안 구현

완료 기준:

- curl 또는 Swagger에서 import까지 동작

### Phase 2. 프론트엔드 골격

- React/Vite 앱 구성
- 검색 화면
- 설정 모달
- Import 버튼 플로우

완료 기준:

- 샘플 JSON 기준 UI가 완성

### Phase 3. 실제 preview 연결

- symbol preview 렌더러
- footprint preview 렌더러
- WRL 3D preview

완료 기준:

- LCSC 번호 입력 시 3개 pane 모두 실데이터 렌더링

### Phase 4. import UX 마감

- overwrite 경고
- 경로 선택 다이얼로그
- 성공/실패 결과 표시
- 연결 테스트 버튼

완료 기준:

- 실제 라이브러리 import를 일반 사용자가 문제없이 수행

### Phase 5. 패키징

- pywebview 데스크톱 앱 패키징
- macOS 우선
- 이후 Windows 배포 검토

완료 기준:

- 별도 Python 설치 없이 실행 가능한 앱 산출

## 지금 시점의 추천 결정

### 최종 추천

1. 앱 이름은 `easy_kicad`
2. 1차 기술 스택은 `pywebview + FastAPI + React + TypeScript + three.js`
3. 업스트림 라이브러리는 CLI가 아니라 Python 내부 API로 감싼다
4. preview는 symbol/footprint는 2D SVG 기반, 3D는 WRL 기반으로 간다
5. proxy / certificate / verify 옵션은 앱 자체 네트워크 adapter에서 책임진다

## 다음 액션

이 문서 다음 단계로 바로 이어서 할 일은 아래 순서가 가장 좋다.

1. `easyeda2kicad.py`를 코드 레벨에서 감싸는 spike 작성
2. LCSC 번호 하나로 `inspect` 결과 JSON schema 확정
3. 그 다음에 프론트엔드 레이아웃을 붙이기

## 참고 자료

- `easyeda2kicad.py` repo: <https://github.com/uPesy/easyeda2kicad.py>
- pywebview docs: <https://pywebview.flowrl.com/>
- FastAPI docs: <https://fastapi.tiangolo.com/>
- React docs: <https://react.dev/>
- Vite docs: <https://vite.dev/guide/>
- Tailwind docs: <https://tailwindcss.com/docs>
- shadcn/ui docs: <https://ui.shadcn.com/>
- TanStack Query docs: <https://tanstack.com/query/latest>
- three.js docs: <https://threejs.org/docs/>
- PyInstaller docs: <https://www.pyinstaller.org/en/stable/>
