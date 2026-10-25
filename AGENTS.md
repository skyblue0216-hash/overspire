# Overspire Agent Loop Engineering Protocol (ALEP)

모든 AI 코딩 에이전트는 <Overspire> 코드베이스 작업 시 다음 헌장을 절대적으로 준수해야 합니다.
세부 설계 명세는 `docs/loop-engineering-architecture.md`를 참조하십시오.

---

### [규칙 0] 루프 작업 전 독립 브랜치 생성 의무화 (Branch-per-Loop Isolation)
- 각 루프 계층(Layer) 작업 또는 세부 기능 구현에 착수하기 전, 반드시 최신 기준 브랜치에서 **해당 루프 전용 브랜치를 새로 생성(`git checkout -b <branch-name>`)하고 전환한 후** 작업을 진행해야 합니다.
  - 브랜치 명명 규칙: `loop/<layer-number>-<feature-name>` (예: `loop/l1-micro-bump`, `loop/l2-slime-ai`, `loop/l3-session-dungeon`)
- `main` 브랜치에 직접 코드를 커밋하거나 검증되지 않은 코드를 작성하는 행위를 엄격히 금지합니다.
- 해당 루프의 독립 테스트 하네스가 100% 통과(Green)하고 검증이 완료된 후에만 병합(Merge) 또는 PR을 진행합니다.

### [규칙 1] 계층 침범 및 순서 건너뛰기 절대 금지 (Bottom-Up Verification Only)
- 구현 작업은 반드시 **Layer 1: Micro(0.1s~1.0s) -> Layer 2: Tactical(5~30s) -> Layer 3: Session(2~3m) -> Layer 4: Meta -> Layer 5: Expansion** 순서로만 진행합니다.
- 상위 루프 작업에 착수하기 전, 직전 하위 루프의 테스트 하네스 통과 로그를 증빙해야 합니다.
  - 예: Micro Loop(각도 충돌/넉백/히트스탑) 미완성 상태에서 Slime AI(Tactical) 작성 금지.
  - 예: Tactical Loop(단일/무리 전투) 미검증 상태에서 던전 생성(Session) 작성 금지.

### [규칙 2] 루프 관심사 분리 및 단방향 의존성 (Separation of Concerns)
- 하위 루프는 절대로 상위 루프의 클래스나 상태를 import/reference 하지 않습니다.
- `core/physics/bump`는 `monsters/slime`이나 `dungeon/floor`의 구체 타입을 몰라야 하며, 오직 `ICombatEntity` 및 기하학적 벡터 수학만 처리합니다.
- 계층 간 통신은 순수 이벤트 스트림(`EntityBumpedEvent`, `MonsterKilledEvent`, `SessionEndedEvent` 등)을 통해서만 결합을 최소화합니다.

### [규칙 3] 하위 루프 독립 테스트 하네스 의무화 (Isolated Test Harness)
- 모든 루프는 게임 씬 전체를 구동하지 않고도 터미널/헤드리스 환경에서 실행 가능한 독립 테스트 러너를 동봉해야 합니다.
  - `Micro Loop`: 각도별($0^\circ, 30^\circ, 45^\circ, 90^\circ, 180^\circ$) 충돌 시 일방 타격 vs 정면 상호 타격 및 분리 임펄스(무적 시간 없이도 1회만 정확히 발생하는지) 검증.
  - `Tactical Loop`: 슬라임 선회 속도($\omega = 120^\circ/s$)에 따른 텔레그래프-회피-측면 카운터 가능 시간(Window) 검증.
  - `Session Loop`: 생성된 던전의 열쇠 획득 가능성 및 계단 도달성 1,000회 시드 무결성 시뮬레이션.
  - `Meta Loop`: 사망 시 선택 보존(장비1+스킬1) 및 다음 회차 유해(Remains) 1개 정확 복원/재사망 시 덮어쓰기 무결성.

### [규칙 4] 개방-폐쇄 원칙 (OCP) 강제 (Zero Core Switch)
- 신규 무기군, 적 아키타입, 룬/접두사, 환경 기믹 추가 시 기존 코어 매니저를 수정하는 `switch(itemType)` 작성을 금지합니다.
- 확장은 반드시 `IBumpInterceptor`, `IArchetypeBrain`, `IAffixRule`, `ITileGimmick` 인터페이스를 구현하고 레지스트리에 등록하는 방식으로만 수행합니다.

### [규칙 5] UI 및 일시정지(Zero-Risk Pause) 불변식
- 인벤토리 및 바닥 장비 비교 UI가 열릴 때, 물리/AI 시뮬레이션 루프는 반드시 완전히 일시정지되어야 합니다.
- 플레이어가 아이템을 비교하는 동안 적이 다가오거나 피해를 입히는 코드는 치명적 결함(Defect)으로 간주합니다.

### [규칙 6] 루프 완료 전 사람(사용자) 웹 플레이테스트 의무화 (Human-in-the-Loop Web Playtest)
- 게임 개발 엔진은 **Godot(고닷)**을 사용합니다.
- 하위 루프의 단위/독립 테스트(규칙 3) 통과만으로 루프 작업 완료를 선언하는 것을 엄격히 금지합니다.
- 각 루프 작업을 완료하기 전, 반드시 Godot 웹(HTML5/Web) 빌드를 생성하고 로컬 웹 서버를 구동하여 `http://localhost:<포트>` 접속 환경을 제공해야 합니다.
- 사람이 직접 브라우저(로컬호스트)를 통해 플레이 테스트를 거치고 최종 승인(Approval)을 내린 경우에만 해당 루프의 완료 및 상위 브랜치 병합을 진행할 수 있습니다.
