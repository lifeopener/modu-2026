# Vesper SRS v2.4 적합성 감사 보고서 (Audit Report)

**감사 기준:** `01_Vesper_SRS_v2_Detailed.md` (Rev 2.4) + `02_Vesper_SRS_Revision_Summary.md`
**감사 대상:** `03_VibeCoding` / `04_HumanDev` / `05_TaskList`
**감사 일시:** 2026-04-18
**감사 결과:** ❌ **FAIL** — CRITICAL 5건, MAJOR 8건, MINOR 7건 (총 20건)

---

## 0. Value Proposition (VP) 얼라인먼트 집중 점검
기획서의 4대 핵심 가치가 기술적으로 구현 가능한지 감사했습니다.
| VP 핵심 가치 | 기능 매핑 | 기존 문서 누락 상태 | 보완 지시 (Pass 기준) |
|---|---|---|---|
| **VP-1. 무한 페르소나 & 옴니채널** | 페르소나 스위칭, FCM 선톡 | 푸시 알림 로직 전면 누락 (C-05) | Edge Function 내 Cron-Push 구현 강제 |
| **VP-2. 진화하는 지능 (Self-Evolution)** | Assistant 응답 양방향 RAG | User 응답만 임베딩됨 (C-01) | `heritage_logs`에 Assistant 응답도 Vector 저장 강제 |
| **VP-3. 실무적 성과 창출 (Execution)** | 실시간 뉴스 Tool Calling, B2B 큐레이션 | 타임아웃 방어 및 B2B DB 부재 (M-01, M-02) | 1.5초 타임아웃 추가 및 `b2b_curations` DB 구축 강제 |
| **VP-4. 초밀착 인지 동행** | 억압적 UI 완전 배제 | NFR 명시 누락 (C-04) | QA Reject 기준인 NFR-000 신설 강제 |

## 판정 요약 매트릭스

| SRS v2.4 핵심 요구사항 | 03 VibeCoding | 04 HumanDev | 05 TaskList | 판정 |
|:---|:---:|:---:|:---:|:---:|
| REQ-F-01 페르소나 빌더 | ✅ 스키마 | ✅ FR-001 | ✅ DB-003 | ⚠️ MINOR |
| REQ-F-02 Heritage 저장 (양방향) | ❌ User만 | ✅ FR-002 | ❌ 누락 | 🔴 CRITICAL |
| REQ-F-03 실시간 웹 검색 Tool Calling | ✅ | ✅ FR-003 | ✅ AI-001 | ✅ PASS |
| REQ-F-04 B2B 큐레이션 | ⚠️ 프롬프트만 | ✅ FR-004 | ⚠️ 시드 없음 | 🟡 MAJOR |
| REQ-F-05 옴니채널 FCM Push | ❌ 코드 없음 | ✅ FR-006 | ✅ PUSH-001~4 | 🔴 CRITICAL |
| REQ-NF-01 Compliance 정규식 | ❌ 코드 없음 | ✅ NFR-002 | ❌ 구현 태스크 없음 | 🔴 CRITICAL |
| REQ-NF-02 Performance 3초 | ❌ 타임아웃 없음 | ✅ NFR-001 | ❌ 타임아웃 태스크 부족 | 🟡 MAJOR |
| REQ-NF-03 Cost 5만원 방어 | ❌ 로직 없음 | ✅ NFR-003 | ⚠️ 추적 시스템 없음 | 🔴 CRITICAL |
| OS-2 억압적 UI 배제 | ✅ Rule Zero | ❌ NFR 미신설 | — | 🔴 CRITICAL |
| CP-1 비상 대응 | ⚠️ 피상적 | ✅ CP-1,2 | ⚠️ | 🟡 MAJOR |

---

## 🔴 CRITICAL 결함 (5건)

### C-01. Assistant 응답 임베딩 누락 (03 VibeCoding)
- **기준:** REQ-F-02 "대화 직후 텍스트가 임베딩되어 벡터 저장"
- **현황:** `03` 코드 Line 107-109에서 `user` 메시지만 heritage_logs에 INSERT
- **문제:** Assistant 응답이 저장되지 않으면 RAG가 편향적으로 동작하며, "진화하는 지능"이라는 핵심 가치가 절반만 구현됨
- **수정:** `streamText` 완료 후 assistant 응답도 임베딩하여 INSERT하는 로직 추가

### C-02. Compliance 정규식 필터 미구현 (03 VibeCoding)
- **기준:** REQ-NF-01 "정규식으로 마스킹", CON-3 "불법 단어 차단"
- **현황:** 시스템 프롬프트의 지시어에만 의존 (Line 100). 코드 레벨 가드레일 제로
- **문제:** LLM은 확률 모델이므로 시스템 프롬프트 지시를 100% 준수하지 않음. 법적 리스크
- **수정:** `streamText` 출력에 대한 후처리(Post-processing) 정규식 필터 함수 추가

### C-03. 예산 추적/비활성화 시스템 전무 (03 VibeCoding + 05 TaskList)
- **기준:** REQ-NF-03 "예산 80% 소진 시 실시간 검색 기능 비활성화"
- **현황:** `03`에 예산 체크 로직 없음. `05`에 NFR-003 태스크가 있으나, 비용을 **누적 추적**하는 시스템 자체에 대한 태스크가 없음
- **문제:** "80%에 도달했는지" 판단할 데이터 소스가 존재하지 않으므로 비활성화 로직도 동작 불가
- **수정:** `api_usage_logs` 테이블 + 비용 누적 쿼리 + 임계치 체크 로직 태스크 3종 추가

### C-04. 억압적 UI 배제 NFR 미신설 (04 HumanDev)
- **기준:** 02 Revision Summary "NFR-001 항목 신설: 어떠한 경우에도 화면 전체 블러나 매매 앱 전환 방해 로직이 동작하지 않아야 함 (위반 시 QA Reject)"
- **현황:** `04`의 NFR-001은 "Performance: 검색 지연 보장"으로 사용 중. 억압적 UI 배제 NFR이 아예 존재하지 않음
- **문제:** Revision Summary에서 가장 강조한 변경사항이 Human Dev 문서에 반영되지 않은 치명적 불일치
- **수정:** NFR-000으로 "Zero Intrusive UI" 항목 최상단 신설

### C-05. FCM Push 엣지 함수 코드 부재 (03 VibeCoding)
- **기준:** REQ-F-05 "24h 미접속 시 FCM 알림 발송", IS-5 "옴니채널 일상 교감"
- **현황:** `03` VibeCoding에 `/api/cron-push` 엣지 함수 코드가 전혀 없음
- **수정:** Cron Push 엣지 함수 뼈대 코드 및 FCM 발송 로직 추가

---

## 🟡 MAJOR 결함 (8건)

### M-01. Tavily Fetch 타임아웃 미구현 (03)
- **기준:** 04 CP-1 "Search API 응답 지연 > 1500ms 시 건너뛰기"
- **현황:** Tool `execute` 내부에 `AbortController`나 타임아웃 없음
- **수정:** `AbortController` + `setTimeout(1500)` 패턴 적용

### M-02. B2B 링크 시드 데이터 및 관리 체계 부재 (03 + 05)
- **기준:** REQ-F-04 "프리미엄 자료(B2B) 링크를 자연스럽게 제안"
- **현황:** 시스템 프롬프트에 "링크를 제안하라"만 있고, 실제 B2B URL 카탈로그가 없음
- **수정:** `b2b_curations` 테이블 또는 JSON 시드 + 관련 태스크 추가

### M-03. `updated_at` 갱신 트리거 누락 (03 + 05)
- **기준:** PUSH-001이 `profiles.updated_at` 기준으로 24시간 미접속자를 감지
- **현황:** 사용자가 채팅할 때 `updated_at`을 갱신하는 트리거/로직이 없음
- **수정:** Chat API에서 `profiles.updated_at = now()` 업데이트 로직 + 태스크 추가

### M-04. 아키텍처 명칭 불일치 (04 HumanDev)
- **기준:** 01 SRS "Supabase Edge Functions" 명확 지정, CON-2 "서버 고정비 0원"
- **현황:** `04` Line 49 "Edge Functions (Vercel/Supabase)" — Vercel 사용 시 유료화 위험
- **수정:** "Vercel" 제거, "Supabase Edge Functions (Deno)" 통일

### M-05. SRS 섹션 참조번호 오류 (05 TaskList)
- **현황:** DB 태스크들이 "6.1" 참조, API 태스크들이 "2.1" 참조 — 01 SRS에 해당 섹션 없음
- **수정:** 실제 SRS v2.4 섹션 번호 또는 REQ ID로 정정

### M-06. NFR ID 충돌 (04 vs 05)
- **현황:** 04의 NFR-001 = "Performance", 05의 NFR-001 = "Infra 배포" — 동일 ID, 완전히 다른 내용
- **수정:** 05 TaskList의 NFR 접두사를 `INFRA-`로 변경하여 네임스페이스 분리

### M-07. Out-of-Scope / Constraints / Assumptions 누락 (04 HumanDev)
- **기준:** 01 SRS 1.2.2~1.2.5에 명시된 배제 항목, 제약사항, 가정
- **현황:** 04에 해당 섹션이 일절 없음
- **수정:** Scope 섹션에 Out-of-Scope, Constraints, Assumptions 추가

### M-08. Traceability Matrix 누락 (04 HumanDev)
- **기준:** 01 SRS Section 5 Traceability Matrix
- **현황:** 04에 추적 매트릭스 없음
- **수정:** FR/NFR → Test Scenario 추적 매트릭스 추가

---

## ⚠️ MINOR 결함 (7건)

| ID | 위치 | 내용 | 수정 |
|:---|:---|:---|:---|
| m-01 | 03 L84 | 임베딩 모델명 하드코딩, 상수 미분리 | 환경변수 또는 상수로 분리 |
| m-02 | 03 L126 | Tavily `max_results` 미지정, 불필요한 토큰 소비 | `max_results: 3` 추가 |
| m-03 | 03 L157 | Fallback 메시지가 `as any`로 타입 우회 | 적절한 Message 타입 정의 |
| m-04 | 04 | Stakeholders 섹션 없음 | 01의 Section 2 참조 추가 |
| m-05 | 05 | AI-001 Blocks에 `INFRA-003` 참조 → 존재하지 않는 태스크 ID | `NFR-003`으로 정정 |
| m-06 | 05 | LOGIC-005 관련 SRS가 "FR-003"이나 실제로는 FR-002(RAG)에 더 가까움 | FR-002로 정정 |
| m-07 | 05 | FE-004 "Zustand" — 02 Revision에서 "블러 상태 전면 삭제"와 혼동 우려 | 주석으로 "Auth/Profile 전용" 명시 |

---

> **수정본:** 위 20건의 결함을 모두 반영한 보완 문서를 `07`, `08`, `09` 번호로 본 폴더에 생성합니다.
