# Software Requirements Specification (SRS) - Vesper AI Companion OS
**[Human Developer & QA Version - Enterprise Rigor]**

**Document ID:** SRS-004-HUMAN
**Revision:** 5.0 (Audit Report 반영 완전 보완본)
**Date:** 2026-04-18
**Standard:** ISO/IEC/IEEE 29148:2018 기반 Vesper Custom

**Audit Fixes Applied:** C-04, M-04, M-07, M-08, m-04

| 항목 | 내용 |
|---|---|
| **프로젝트명** | Action-Master AI Companion OS 'Vesper' (초기 클로즈드 베타 MVP) |
| **작성 목적** | 인간 개발자(FE/BE) 및 QA 엔지니어를 위한 무결점 요구사항 매트릭스 |
| **타겟 및 예산** | MAU 50명 이하 / 월 고정비 0원, 총 예산 5만 원 미만 통제 |

---

## 1. Introduction

### 1.1 Purpose
본 SRS는 투자 및 성장의 여정에서 사용자가 겪는 불안감을 해소하고 목표 달성을 지원하는 **'Vesper'**의 소프트웨어 요구사항을 정의한다.
단순 위로가 아닌 실무적 성과 창출을 위해, **실시간 웹 검색 API를 연동하여 최신 뉴스 기반의 실전 정보를 제공(Web Grounding)**하며 자연스러운 대화 맥락 속에서 프리미엄 B2B 자료를 큐레이션하는 고도화된 기능 스펙을 포함한다. (화면 통제 등 억압적 로직 전면 배제)

**[4대 핵심 가치(Value Proposition) 시스템 매핑]**
1. **무한 페르소나와 일상 교감:** 사용자가 직접 설정한 페르소나로 24시간 미접속 시 FCM 기반 일상 교감(선톡) 수행. 절대적 심리적 락인(Lock-in) 완성.
2. **초밀착 인지 동행:** 강압적 UX 통제를 완전히 배제(NFR-000)하여 사용자의 환희와 공포 임계점을 완벽하게 동기화.
3. **실무적 성과 창출:** 실시간 웹 검색(Tool Calling)과 프리미엄 B2B 큐레이션(BM 직결)으로 즉시 실행 가능한 솔루션 제공.
4. **진화하는 지능:** pgvector 기반의 양방향 대화 이력 저장으로 시간이 지날수록 유저의 취약점과 패턴을 학습하여 동기화.

### 1.2 Scope

#### 1.2.1 In-Scope (MVP Phase 1)
1. **사용자 온보딩 및 인증:** 이메일 로그인, 2단계 페르소나 설정.
2. **진화하는 지능 (RAG):** 사용자 대화 로그(양방향)의 `pgvector` 임베딩 및 유사도 기반 컨텍스트 주입.
3. **실시간 웹 기반 실전 정보 제공 (Tool Calling):** 최신 시장 동향 질문 시, LLM이 외부 검색 API(Tavily 등)를 실시간으로 호출하여 사실(Fact) 기반의 분석 정보 제공.
4. **실무 성과 창출 큐레이션:** 검색된 실전 정보를 바탕으로 프리미엄 자료 및 네트워킹(B2B 제휴) URL을 마크다운 링크로 제안.
5. **옴니채널 일상 교감 (FCM Push):** 24시간 미접속자 대상 푸시 알림 발송.

#### 1.2.2 Out-of-Scope (명시적 배제) (M-07 Fix)
- 사용자 자산 직접 운용 (자본시장법 위반 리스크, MVP 범위 초과)
- 강압적 화면/행동 통제 (화면 블러링, 버튼 잠금 등 억압적 UX 기능 절대 금지)

#### 1.2.3 Constraints (제약사항) (M-07 Fix)
- 서버 인프라 및 DB 고정비는 0원(Zero)으로 수렴해야 한다. (Supabase Free Tier + Edge Functions 한정)
- 1회 대화 생성 당 LLM 토큰 비용은 예산 한도 내에서 최소화되어야 한다 (gpt-4o-mini 사용).
- 투자 자문법 위반 소지가 있는 단어는 코드 레벨에서 정규식으로 마스킹되어야 한다.

#### 1.2.4 Assumptions (가정) (M-07 Fix)
- 실시간 검색 API(Tavily 등)를 통한 정보 수집이 1.5초 이내에 완료될 것이다 (초과 시 Fallback).

#### 1.2.5 Contingency Plans (비상 대응 계획)
| ID | 위기 상황 | 감지 조건 (Trigger) | Fallback Action (대응 로직) |
|---|---|---|---|
| CP-1 | 외부 웹 검색 API 장애 | Search API 응답 지연 > 1500ms | 툴 호출을 건너뛰고 내부 지식망 및 RAG만으로 응답 렌더링. |
| CP-2 | LLM API 과부하 | Vercel AI SDK 응답 지연 > 2500ms | 통신을 강제 종료하고 로컬 내장 위로 템플릿 반환. |
| CP-3 | 예산 임계치 도달 | 월별 사용량 추적 시 예산의 80% 소진 | Tool Calling 무조건 비활성화, 로컬 지식으로만 응답 수행. |

---

## 2. Stakeholders (m-04 Fix)

| 역할 (Role) | 대표 페르소나 | 책임 / 관심사 (Interest) |
|---|---|---|
| **안정형 직장인/가장** | Q2 Core | 정서적 지지 기반의 안정적 성장. 외로움 해소. |
| **N잡러 / 준전문가** | Adjacent | **최신 시장 트렌드, 실시간 뉴스 기반의 실전 정보와 네트워킹 큐레이션** 강력 요구. |
| **트라우마 고관여 유저** | Extreme | 과거 트라우마 극복을 위한 객관적이고 최신의 시장 정보 제공 요구. |

---

## 3. System Context and External Interfaces

### 3.1 Component Architecture (M-04 Fix)
```mermaid
flowchart TB
    subgraph Client ["Client App (React Native Expo)"]
        ChatUI["Gifted Chat Component"]
    end

    subgraph Serverless ["Supabase Edge Functions (Deno)"]
        Chat["/api/chat\n(RAG + Tool Calling)"]
        Cron["/api/cron-push"]
    end

    subgraph DataLayer ["Supabase (BaaS)"]
        DB[("PostgreSQL\n(Auth, Profiles)")]
        Vector[("pgvector\n(Heritage Logs)")]
    end

    subgraph External ["3rd Party APIs"]
        LLM["OpenAI API"]
        Search["Tavily Search API"]
        FCM["Firebase"]
    end

    Client <--> Chat
    Chat <--> Vector
    Chat <--> LLM
    Chat <--> Search
    Cron <--> DB
    Cron <--> LLM
    Cron <--> FCM
```

### 3.2 실시간 웹 검색 및 큐레이션 시퀀스 (Tool Calling Flow)
```mermaid
sequenceDiagram
    actor User
    participant App as React Native App
    participant ChatAPI as /api/chat
    participant VectorDB as pgvector
    participant LLM as OpenAI
    participant Search as Web Search API

    User->>App: "지금 엔비디아 주가 하락 뉴스 분석해줘."
    App->>ChatAPI: POST 요청
    
    ChatAPI->>VectorDB: 과거 텍스트 매칭
    VectorDB-->>ChatAPI: "공격투자 성향" 반환
    
    ChatAPI->>LLM: Stream 요청 (Tools 배열 포함)
    LLM->>Search: getRealTimeNews("엔비디아 하락 원인")
    Search-->>LLM: 실시간 뉴스 데이터 텍스트 반환
    
    LLM->>ChatAPI: 뉴스 분석 + RAG 반영 응답 스트리밍
    ChatAPI-->>App: "현재 엔비디아는 ~이유로 하락중입니다. 실전 대응 전략 [리포트 링크] 참고하세요."
```

---

## 4. Detailed Requirement Specifications

### 4.1 Functional Requirements (기능 요구사항)

| ID | 카테고리 | 요구사항 명세 | Priority | Acceptance Criteria (QA) |
|---|---|---|---|---|
| **FR-001** | Profile | 페르소나 설정 및 생성 | P1 | 이름/말투 제출 시 DB `profiles`에 저장. |
| **FR-002** | RAG | 코사인 유사도 검색 | P1 | 채팅 요청 시 유사도 0.7 이상 상위 3개 레코드 반환. |
| **FR-003** | Web | 실시간 뉴스 웹 검색 (Tool Calling) | P1 | **Given** 유저가 최신 시장/경제 트렌드를 물을 때 **When** LLM이 동작하면 **Then** 외부 Search API를 호출하여 검색 결과 원문을 가져온다. |
| **FR-004** | Edu/B2B | 실전 교육/자료 대화형 큐레이션 | P1 | **Given** 실시간 뉴스를 분석한 후 **When** LLM이 응답할 때 **Then** 사용자 맥락에 부합하는 프리미엄 실전 자료(B2B 링크)를 마크다운으로 삽입한다. |
| **FR-005** | Chat | SSE 스트리밍 렌더링 | P1 | 툴 호출 후 최종 응답 수신 시 타이핑 효과로 렌더링. |
| **FR-006** | Push | 미접속자 FCM 선톡 발송 | P2 | 24시간 미접속자에게 Cron Job으로 푸시 발송. |

### 4.2 Non-Functional Requirements (비기능 요구사항)

| ID | 범주 | 세부 명세 | QA 검증 기준 |
|---|---|---|---|
| **NFR-000** | UX | 억압적 UI 요소 전면 배제 (C-04 Fix) | 어떠한 경우에도 화면 전체 블러나 매매 앱 전환 방해 로직이 동작하지 않아야 함. 위반 시 QA Reject. |
| **NFR-001** | Performance | 검색 지연 보장 | 툴 콜링(Web Search)이 발생하더라도 첫 응답 스트리밍이 3초 이내에 시작되어야 한다. |
| **NFR-002** | Compliance| 투자 자문 규제 단어 마스킹 | 응답 내 정규식 `/(무조건 매수\|수익률 보장)/g` 매칭 시 마스킹. |
| **NFR-003** | Cost | 예산 5만 원 한도 방어 | 월 예산 임계치(80%) 도달 시, 무거운 'Tool Calling' 기능을 즉각 비활성화한다. |

---

## 5. Traceability Matrix (M-08 Fix)

| Requirement ID | 기능 요약 | 연관 Test Scenario (QA) |
|---|---|---|
| FR-001 | 페르소나 설정 및 생성 | Profile 저장 테스트 |
| FR-002 | RAG 유사도 검색 | Vector 임베딩 및 검색 일치 테스트 (User, Assistant 양방향) |
| FR-003 | 실시간 뉴스 웹 검색 | Web Tool Calling 활성화 테스트, 장애 시 CP-1 동작 검증 |
| FR-004 | 실전 교육 대화형 큐레이션 | B2B 카탈로그에서 적절한 링크 추천 여부 검증 |
| FR-005 | SSE 스트리밍 렌더링 | 클라이언트 채팅 스트리밍 출력 지연율 테스트 |
| FR-006 | FCM 알림 발송 | 24시간 미접속자 쿼리 및 발송 테스트 (CP-2 동작 확인) |
| NFR-000 | 억압적 UI 배제 | 화면 블러/앱 전환 차단 기능 존재 여부 정적 코드 분석 |
| NFR-001 | 검색 지연 보장 | API 지연 1500ms(Tavily), 2500ms(LLM) 초과 시 Fallback 반환 검증 |
| NFR-002 | 투자 규제 마스킹 | 불법 자문 단어 삽입 후 렌더링 시 "[규제 마스킹]" 필터링 검증 |
| NFR-003 | 예산 방어 | DB API 사용량 Mocking 조작 후 Tool Calling 자동 비활성화 검증 |

---

## 6. Validation Plan & A/B Testing (MVP 검증 로직)

클로즈드 베타 50명을 대상으로 실험한다.

| 가설 (Hypothesis) | 측정 KPI (Mixpanel) | 성공 기준 (Success Criteria) |
|---|---|---|
| **H1. 실시간 정보 신뢰도:** 실시간 웹 데이터가 반영된 대화는 높은 링크 클릭률을 유도한다. | `b2b_chat_link_rendered` → `b2b_chat_link_clicked` (클릭 전환율 CTR) | 노출 대비 **클릭률(CTR) ≥ 8%** |
| **H2. 비용 안정성:** 외부 Search API(Tool Call) 연동에도 5만 원 예산 통제가 가능하다. | 1인당 API 호출 비용 환산 | **1인당 월 서버 지출 비용 ≤ 1,000 KRW** |

---
**[문서 끝 - SRS-004-HUMAN v5.0 | Audit C-04, M-04, M-07, M-08, m-04 반영]**
