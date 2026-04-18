# [FE-LOGIC-001] `@ai-sdk/react` 채팅 훅 앱 채팅창에 연결

## 1. Task 개요
- **도메인:** Frontend / Chat Logic
- **목표:** 프론트엔드 UI를 실제 백엔드 AI 엔진(`chat` 엣지 함수)과 연결하여 대화를 가능하게 합니다.
- **선행 태스크:** FE-008, AI-004
- **핵심 가치 (VP):** 딜레이 없는 실시간 대화 환경 구축

## 2. Vibe Coding 프롬프트 (AI 입력용)

---
**[Prompt]**
이제 껍데기뿐인 채팅창에 생명을 불어넣을 시간이다. Vercel AI SDK의 `useChat` 훅을 사용해 서버와 통신하라.

작업 지시:
1. `screens/ChatScreen.tsx`를 수정하라.
2. `useChat` 훅의 `api` 경로를 우리가 배포할 Supabase Edge Function URL로 설정하라.
3. `handleInputChange`를 입력창의 `onChangeText`에, `handleSubmit`을 전송 버튼의 `onPress`에 연결하라.
4. `messages` 배열을 `FlatList`의 데이터로 넣어, AI가 보내는 스트리밍 메시지가 실시간으로 목록에 추가되도록 하라.
---

## 3. 검증 기준 (QA)
- [ ] 전송 버튼 클릭 시 백엔드 API로 요청이 날아가는가?
- [ ] 서버 응답이 올 때마다 `messages` 상태가 업데이트되어 화면이 리렌더링되는가?
