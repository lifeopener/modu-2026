# Vesper AI Companion OS - Atomic Task Master List

**작성 기준:** SRS v2.4 (Human Dev & Vibe Coding 동기화본) 및 감사 보고서(06_Vesper_Audit_Report.md) 보완사항 적용
**작성 목적:** AI 에이전트 및 인간 개발자가 오해 없이 단일 진실 공급원(SSOT)으로 삼아, 즉각적인 GitHub Project / Sprint 계획에 투입할 수 있도록 추출된 **초정밀 원자 단위(Atomic) Task 명세서.**

**Audit Fixes Applied:** C-03, M-02, M-03, M-05, M-06, m-05, m-06, m-07

---

## 1. Task Breakdown Principles
- **Data First:** DB 스키마, DTO(Zod 검증), 인터페이스 규약을 선행 추출.
- **State Mutation 격리:** 상태 변경 여부(CQRS)에 따라 FE/BE 로직을 단일 책임 단위로 파편화.
- **TDD 지향:** 인수 조건(AC)을 테스트 코드로 변환하여 할당.

---

## 1.5 Value Proposition (VP) Task Mapping
각 태스크가 4대 기획적 가치를 어떻게 기술적으로 실현하는지 매핑합니다.
- **[VP-1] 무한 페르소나 & 옴니채널:** `FE-007`, `FE-011` (페르소나 생성/전환), `PUSH-001~005` (일상 교감 선톡)
- **[VP-2] 진화하는 지능:** `DB-004`, `LOGIC-003~005` (양방향 RAG를 통한 패턴 학습)
- **[VP-3] 실무적 성과 창출:** `DB-006`, `FE-012`, `AI-001~002`, `INFRA-002` (웹 실시간 정보 획득 및 B2B 그룹바잉 수익 직결)
- **[VP-4] 초밀착 인지 동행:** NFR-000 제약사항 및 억압적 UI 배제 룰 주입 (`AI-003`, `TEST-004`)

## 2. Hyper-Granular Task List (Total: 57 Tasks)

| Task ID | Epic (도메인) | Feature (기능명) | 관련 SRS | Dependencies |
|---|---|---|---|---|
| **Step 1. DB Schema & Contract (Backend)** |
| `DB-001` | Infra | [DB] Supabase Project 생성 및 0원 고정비 Tier 셋업 | 1.2.3 | None |
| `DB-002` | Database | [DB] PostgreSQL `vector` Extension 활성화 스크립트 작성 | FR-002 (M-05) | DB-001 |
| `DB-003` | Database | [DB/DDL] `profiles` 테이블(이름, 톤앤매너, fcm_token) 생성 쿼리 작성 | FR-001 | DB-001 |
| `DB-004` | Database | [DB/DDL] `heritage_logs` 테이블(임베딩 1536차원 포함) 생성 쿼리 작성 | FR-002 | DB-002 |
| `DB-005` | Database | [DB/DDL] `api_usage_logs` 비용 추적 테이블 및 월간 비용 View 생성 (C-03) | NFR-003 | DB-001 |
| `DB-006` | Database | [DB/DDL] `b2b_curations` 큐레이션 시드 데이터 카탈로그 생성 (M-02) | FR-004 | DB-001 |
| `DB-007` | Security | [DB/RLS] `profiles` 테이블 Row Level Security(본인 열람) 정책 적용 | NFR-000 | DB-003 |
| `DB-008` | Security | [DB/RLS] `heritage_logs` 테이블 Row Level Security 정책 적용 | NFR-000 | DB-004 |
| `DB-009` | Database | [DB/Trigger] Auth 가입 시 `profiles` 빈 레코드 자동 생성 트리거 함수 작성 | FR-001 | DB-003 |
| `DB-010` | Database | [DB/RPC] `match_heritage_logs` (Cosine 유사도 RAG) RPC Function 작성 | FR-002 | DB-004 |
| `DB-011` | Database | [DB/RPC] `get_monthly_cost` 예산 추적 RPC Function 작성 (C-03) | NFR-003 | DB-005 |
| `DB-012` | Mocking | [Mock] `supabase/seed.sql`에 UI 테스트용 더미 유저, B2B 시드, Heritage 주입 | 5. 검증 | DB-010, DB-006 |
| `API-001` | Contract | [API Spec] 백-프론트 통신용 `/api/chat` DTO 인터페이스(Type) 정의 | FR-005 (M-05) | None |
| `API-002` | Contract | [Mock] 프론트엔드 병렬 개발용 Mock Chat SSE Edge Function 뼈대 작성 | FR-005 | API-001 |
| `API-003` | Contract | [API/Zod] 프로필 폼 업데이트 및 채팅 페이로드 검증을 위한 Zod 스키마 정의 | FR-001 | None |
| **Step 2. Client Scaffolding & State (Frontend)** |
| `FE-001` | Infra | [FE] React Native (Expo Managed) 및 NativeWind 프로젝트 스캐폴딩 | 3.2 | None |
| `FE-002` | Config | [FE] Supabase Client 초기화 및 환경변수(Auth Key) 세팅 | 3.2 | DB-001 |
| `FE-003` | Infra | [FE/Infra] 앱 공통 테마, 폰트 및 Expo Router 기반 Navigation 골격 셋업 | 3.2 | FE-001 |
| `FE-004` | Store | [FE] Zustand `useUserStore` (Auth/Profile 데이터 캐싱 전용) (m-07) | 3.2 | FE-001 |
| `FE-005` | UI/Auth | [FE/UI] 로그인 스크린 UI 퍼블리싱 (Email/Social 기반) | FR-001 | FE-003 |
| `FE-006` | UI/Auth | [FE/UI] 미로그인 유저 접근 차단용 Expo Router Auth Guard (보호 라우트) 구현 | NFR-000 | FE-005 |
| `FE-007` | UI | [FE/UI] 페르소나 셋업 스크린 (이름, 톤앤매너 입력) UI 퍼블리싱 | FR-001 | FE-003 |
| `FE-008` | UI | [FE/UI] 메인 채팅 스크린 (Gifted Chat 등 기반) UI 뼈대 구현 | 3.2 | FE-003 |
| `FE-009` | UI/Chat | [FE/UI] 텍스트 입력창 오토 리사이징 및 전송 버튼이 포함된 `ChatInput` 컴포넌트 분리 | 3.2 | FE-008 |
| `FE-010` | UI/Chat | [FE/UI] 새 메시지 수신 시 리스트 최하단으로 이동하는 `Scroll to Bottom` 훅 적용 | 3.2 | FE-008 |
| `FE-011` | UI/Chat | [FE/UI] 다중 페르소나 선택/전환 드롭다운(Persona Selector) 컴포넌트 추가 | IS-1 | FE-008 |
| `FE-012` | UI/Chat | [FE/UI] B2B 큐레이션용 마크다운 렌더링(Link) 지원 Custom Bubble 컴포넌트 구현 | FR-004 | FE-008 |
| **Step 3. Business Logic Mutation (Auth & RAG)** |
| `LOGIC-001` | Auth | [FE/Command] 프론트엔드 Supabase Auth 로그인 비즈니스 로직 연동 | FR-001 | FE-005, FE-002 |
| `LOGIC-002` | Auth | [FE/Command] 페르소나 셋업 정보 Zod 검증 및 `profiles` 테이블 DB 업데이트 연동 | FR-001 | FE-007, API-003 |
| `LOGIC-003` | RAG | [Edge/Command] 메시지 수신 시 OpenAI API를 호출하여 임베딩 변환 로직 작성 | FR-002 | API-001 |
| `LOGIC-004` | RAG | [Edge/Command] 변환된 임베딩(User & Assistant 모두)을 `heritage_logs`에 Insert (C-01) | FR-002 | LOGIC-003, DB-004 |
| `LOGIC-005` | RAG | [Edge/Query] Deno 엣지 함수 내 `match_heritage_logs` 호출 및 컨텍스트 추출 | FR-002 (m-06) | DB-010, API-001 |
| **Step 4. AI SDK & Web Grounding (Core Edge)** |
| `AI-001` | Web Search | [Edge/Query] `getRealTimeNews` Tool Calling + Timeout(1500ms) 추가 (M-01) | FR-003 | None |
| `AI-002` | Prompt | [Edge/Logic] B2B Catalog `b2b_curations` DB Fetch 및 프롬프트 빌더에 포함 (M-02) | FR-004 | DB-006 |
| `AI-003` | Prompt | [Edge/Logic] 빌더 내부에 RAG 컨텍스트와 시스템 룰(억압적 UI 금지) 조립 | NFR-000 | AI-002, LOGIC-005 |
| `AI-004` | LLM | [Edge/Stream] Vercel AI SDK `streamText` 구동 및 OpenAI `gpt-4o-mini` 연동 로직 | FR-005 | AI-003, AI-001 |
| `AI-005` | Fallback | [Edge/Logic] 타임아웃 2500ms 발생 시 정적 템플릿 반환용 try-catch Fallback 로직 | CP-2 | AI-004 |
| `AI-006` | Compliance | [Edge/Logic] 스트리밍 완료 후 텍스트 내 정규식 기반 불법 단어 마스킹 적용 (C-02) | NFR-002 | AI-004 |
| **Step 5. Client Chat Engine (Frontend)** |
| `FE-LOGIC-001`| Chat | [FE/Query] `@ai-sdk/react`의 `useChat` 훅을 앱 채팅창(FE-008)에 연결 | FR-005 | FE-008, API-002 |
| `FE-LOGIC-002`| Chat | [FE/Render] 서버의 SSE 스트리밍 데이터를 실시간 뷰 업데이트로 렌더링 | FR-005 | FE-LOGIC-001 |
| `FE-LOGIC-003`| Chat | [FE/Error] 클라이언트 단 네트워크 에러 시 Fallback 정적 메시지 렌더링 방어 로직 | CP-2 | FE-LOGIC-001 |
| **Step 6. Cron & Push Notification (Omni-channel)** |
| `PUSH-001` | Update | [Edge/Logic] Chat 메시지 발생 시 `profiles.updated_at` 갱신 로직 추가 (M-03) | FR-006 | DB-003 |
| `PUSH-002` | Notification | [Edge/Query] `profiles.updated_at` 기준 24시간 미접속자 추출 로직 | FR-006 | PUSH-001 |
| `PUSH-003` | Notification | [Edge/LLM] 미접속자 컨텍스트 기반 위로/선톡 메시지 생성 로직 (LLM 호출) | FR-006 | PUSH-002 |
| `PUSH-004` | Notification | [Edge/Command] Firebase Admin SDK를 통해 FCM으로 푸시 발송하는 로직 (C-05) | FR-006 | PUSH-003 |
| `PUSH-005` | Infra | [Infra] Supabase pg_cron을 이용한 `/api/cron-push` 매일 1회 스케줄링 등록 | FR-006 | PUSH-004 |
| **Step 7. Automated Tests (AC Translation)** |
| `TEST-001` | Infra | [Test] Vitest (또는 Jest) 테스트 환경 스캐폴딩 및 `package.json` 스크립트 세팅 | N/A | None |
| `TEST-002` | Security | [Test] Supabase RLS 정책 우회 시도 차단 여부 자동화 단위 테스트 작성 | NFR-000 | DB-007, TEST-001 |
| `TEST-003` | Logic | [Test] Zod 스키마 Validation 에러 반환 검증 단위 테스트 작성 | FR-001 | API-003, TEST-001 |
| `TEST-004` | Logic | [Test] 프롬프트 빌더 시스템 룰(억압적 UI 금지 가드레일) 주입 여부 단위 테스트 | NFR-000 | AI-003, TEST-001 |
| `TEST-005` | RAG | [Test] Dummy Heritage 로그 삽입 후 Cosine Distance 검색 Recall율 단위 테스트 | FR-002 | DB-012, TEST-001 |
| `TEST-006` | Compliance | [Test] LLM 응답 내 불법 자문 단어 Regex 마스킹 동작 검증 단위 테스트 | NFR-002 | AI-006, TEST-001 |
| `TEST-007` | Fallback | [Test] 강제 지연 주입 시 2500ms 내 로컬 Fallback 반환 확인 통합 테스트 작성 | CP-2 | AI-005, TEST-001 |
| **Step 8. Non-Functional & Release (Infra)** |
| `INFRA-001` | Infra | [Infra] Edge Function CLI 배포 스크립트 작성 및 Secret Keys (OpenAI, Tavily) 주입 세팅 (M-06) | 3.2 | AI-001 |
| `INFRA-002` | Analytics | [FE/Logic] Mixpanel 초기화 및 `b2b_link_clicked` 이벤트 트래킹 로직 클라이언트 삽입 | H1 | FE-012 |
| `INFRA-003` | Cost | [Edge/Logic] API 호출 시마다 토큰 비용을 `api_usage_logs`에 적재 (C-03) | NFR-003 | DB-005 |
| `INFRA-004` | Cost | [Edge/Logic] 월 예산 80% 임계치 도달 감지 시 Tool Calling 비활성화 분기 로직 적용 (m-05) | NFR-003 | INFRA-003 |

---

## 3. Workflow Suggestion (오케스트레이션 가이드)

프로젝트 리드 및 AI 에이전트는 위 태스크를 다음의 **의존성 기반 파이프라인**에 맞춰 순차적/병렬적으로 실행하십시오.

1. **Phase 1 (Data Foundation):** `DB-001` ~ `DB-012`, `API-001` ~ `API-003` 완료. (데이터 스키마, 비용 추적 뷰, Zod 검증 확정)
2. **Phase 2 (UI Scaffolding & Routing):** `FE-001` ~ `FE-012` 완료. (React Native 화면, 네비게이션, 오토스크롤 채팅창 등 프론트 뼈대 완성)
3. **Phase 3 (Core Mutation):** `LOGIC-001` ~ `LOGIC-005` 완료. (Auth 연동 및 임베딩 양방향 변환/저장)
4. **Phase 4 (AI Engine):** `AI-001` ~ `AI-006` 완료. (프롬프트 빌더, B2B 카탈로그, Tool Calling, 타임아웃, 마스킹 처리)
5. **Phase 5 (Client Integration):** `FE-LOGIC-001` ~ `FE-LOGIC-003` 완료. (채팅 연동)
6. **Phase 6 (Omni-channel):** `PUSH-001` ~ `PUSH-005` 완료. (Activity 갱신 및 푸시 알림)
7. **Phase 7 (Verification):** `TEST-001` ~ `TEST-007` 완료. (프롬프트 주입 누락, RLS, Zod, 타임아웃 등 테스트 전면 통과 확인)
8. **Phase 8 (Release):** `INFRA-001` ~ `INFRA-004` 완료. (배포, 트래킹, 예산 차단 로직 적용)
