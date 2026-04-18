# Vesper AI Companion OS - System Prompt & Architecture Guide
**[Vibe Coding (AI Agent) 전용 마스터 지시서]**

**Document ID:** SRS-004-VIBE
**Revision:** 5.0 (Audit Report 반영 완전 보완본)
**Target:** Cursor, Windsurf, GitHub Copilot 등 AI 코딩 에이전트
**Rule Zero:** AI 에이전트는 환각(Hallucination) 없이 본 문서에 기재된 아키텍처와 코드를 구현하라. 사용자의 화면을 블러 처리하거나 앱 전환을 방해하는 억압적 UI 요소를 절대 넣지 마라. 대화 중 최신 시장 정보가 필요할 경우 반드시 **Vercel AI SDK의 Tool Calling** 기능을 활용해 실시간 웹 데이터를 긁어와야 한다.

**Audit Fixes Applied:** C-01, C-02, C-03, C-05, M-01, M-02, M-03, m-01, m-02, m-03

---

## 0. Value Proposition Core Directives (에이전트 필수 인지 사항)
AI 에이전트는 기획자의 4대 철학을 반드시 이해하고 코딩에 임하라.
1. **무한 페르소나 & 옴니채널:** 단순한 앱이 아닌 '평생의 친구'다. 자유로운 페르소나 변경과 FCM 푸시 알림 코드는 절대 누락하지 마라.
2. **초밀착 인지 동행 & 진화하는 지능:** 유저와 AI의 대화는 모두 1536차원 벡터로 저장되어 유저의 패턴과 취약점을 끝없이 학습해야 한다. (RAG)
3. **실무적 성과 창출 (Growth Coach):** AI는 단순 심리적 위로봇이 아니다. 실시간 뉴스 검색(Tavily)과 프리미엄 B2B 링크 큐레이션을 통해 포트폴리오 리밸런싱 등 실질적인 성과(BM)를 내야 한다.

## 1. Absolute Constraints (절대 규칙)

1. **NO CUSTOM BACKEND:** 서버는 오직 `Supabase Edge Functions (Deno)` 로만 작성한다.
2. **REAL-TIME DATA:** 정적 지식에 의존하지 말고, 최신 투자 트렌드 질문에는 Tavily API (또는 검색 도구)를 통해 실시간 뉴스를 조회하라.
3. **STRICT BUDGET LIMIT:** `gpt-4o-mini` 모델 사용. `maxTokens: 250` 제한. 월 예산 5만 원 초과 불가.
4. **NATIVE FETCH:** Edge Functions 내 `axios` 사용 금지. native `fetch` 사용.
5. **UI FRAMEWORK:** React Native (Expo) + NativeWind.
6. **ZERO INTRUSIVE UI:** 화면 블러링, 버튼 잠금, 앱 전환 방해 등 억압적 UX 기능을 일절 구현하지 마라. (OS-2 준수)
7. **COMPLIANCE GUARDRAIL:** LLM 응답에 대한 코드 레벨 정규식 후처리 필터를 반드시 구현하라. 시스템 프롬프트에만 의존하지 마라.

---

## 2. Comprehensive Database Schema (Seed.sql)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- ========================================
-- 2.1 Core Tables
-- ========================================

CREATE TABLE public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  persona_name TEXT NOT NULL,
  persona_tone TEXT NOT NULL,
  fcm_token TEXT,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

CREATE TABLE public.heritage_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  embedding VECTOR(1536), 
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

-- ========================================
-- 2.2 Cost Tracking (C-03 Fix: 예산 추적 시스템)
-- ========================================

CREATE TABLE public.api_usage_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  endpoint TEXT NOT NULL CHECK (endpoint IN ('chat', 'embedding', 'search')),
  token_count INT DEFAULT 0,
  estimated_cost_krw NUMERIC(10, 4) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

-- 월간 비용 합산 뷰 (예산 80% 체크용)
CREATE OR REPLACE VIEW public.monthly_cost_summary AS
SELECT 
  DATE_TRUNC('month', created_at) AS month,
  SUM(estimated_cost_krw) AS total_cost_krw
FROM public.api_usage_logs
GROUP BY DATE_TRUNC('month', created_at);

-- ========================================
-- 2.3 B2B Curation Catalog (M-02 Fix)
-- ========================================

CREATE TABLE public.b2b_curations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  category TEXT NOT NULL,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

-- ========================================
-- 2.4 RPC Functions
-- ========================================

CREATE OR REPLACE FUNCTION match_heritage_logs(
  query_embedding VECTOR(1536), match_threshold FLOAT, match_count INT, p_user_id UUID
) RETURNS TABLE (id UUID, content TEXT, similarity FLOAT) LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY SELECT h.id, h.content, 1 - (h.embedding <=> query_embedding) AS similarity
  FROM heritage_logs h WHERE h.user_id = p_user_id AND 1 - (h.embedding <=> query_embedding) > match_threshold
  ORDER BY h.embedding <=> query_embedding LIMIT match_count;
END; $$;

-- 월간 총 비용 조회 함수
CREATE OR REPLACE FUNCTION get_monthly_cost()
RETURNS NUMERIC LANGUAGE plpgsql AS $$
DECLARE total NUMERIC;
BEGIN
  SELECT COALESCE(SUM(estimated_cost_krw), 0) INTO total
  FROM api_usage_logs
  WHERE created_at >= DATE_TRUNC('month', NOW());
  RETURN total;
END; $$;

-- ========================================
-- 2.5 Auto Triggers
-- ========================================

-- Auth 가입 시 profiles 자동 생성
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
  INSERT INTO public.profiles (id, persona_name, persona_tone)
  VALUES (NEW.id, '베스퍼', '따뜻하고 전문적인');
  RETURN NEW;
END; $$;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

---

## 3. Edge Function Source Codes (Deno)

### 3.1 `/supabase/functions/chat/index.ts` (RAG + Tool Calling + B2B Nudge + Compliance)

시스템 프롬프트와 Vercel AI SDK의 `tools` 옵션을 활용하여 **실시간 웹데이터 수집**과 **실전/교육 자료 큐레이션**을 동시 수행한다.

```typescript
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { openai } from 'npm:@ai-sdk/openai'
import { streamText, tool } from 'npm:ai'
import { z } from 'npm:zod'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// ── Constants (m-01 Fix) ──
const EMBEDDING_MODEL = 'text-embedding-3-small';
const LLM_MODEL = 'gpt-4o-mini';
const MAX_TOKENS = 250;
const SEARCH_TIMEOUT_MS = 1500;  // CP-1: Search API 타임아웃
const LLM_TIMEOUT_MS = 2500;    // CP-2: LLM 타임아웃
const BUDGET_LIMIT_KRW = 50000;
const BUDGET_THRESHOLD = 0.8;   // 80%

// ── Compliance Regex Filter (C-02 Fix) ──
const ILLEGAL_PATTERNS = /(무조건 매수|수익률 보장|확정 수익|원금 보장|반드시 오른다)/g;
function sanitizeResponse(text: string): string {
  return text.replace(ILLEGAL_PATTERNS, '[투자 자문 규제에 의해 마스킹됨]');
}

const corsHeaders = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type' };

serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders });

  try {
    const { messages, userId } = await req.json();
    const supabase = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!);

    // ── 0. Budget Gate (C-03 Fix: 예산 체크) ──
    const { data: costData } = await supabase.rpc('get_monthly_cost');
    const currentCost = costData ?? 0;
    const isBudgetCritical = currentCost >= BUDGET_LIMIT_KRW * BUDGET_THRESHOLD;

    const { data: profile } = await supabase.from('profiles').select('*').eq('id', userId).single();
    const latestMessage = messages[messages.length - 1].content;
    
    // ── 1. RAG Vector Search ──
    const embedRes = await fetch('https://api.openai.com/v1/embeddings', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${Deno.env.get('OPENAI_API_KEY')}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ input: latestMessage, model: EMBEDDING_MODEL })
    });
    const embedData = await embedRes.json();
    const embedding = embedData.data[0].embedding;

    const { data: ragDocs } = await supabase.rpc('match_heritage_logs', {
      query_embedding: embedding, match_threshold: 0.7, match_count: 3, p_user_id: userId
    });
    const contextStr = ragDocs?.map((d: any) => d.content).join('\n') || "";

    // ── 2. B2B Curation Catalog Fetch (M-02 Fix) ──
    const { data: b2bLinks } = await supabase
      .from('b2b_curations')
      .select('title, url, category')
      .eq('is_active', true)
      .limit(5);
    const b2bCatalog = b2bLinks?.map((l: any) => `- [${l.title}](${l.url}) (${l.category})`).join('\n') || "없음";

    // ── 3. System Prompt ──
    const systemPrompt = `
      You are '${profile.persona_name}'. Tone: '${profile.persona_tone}'.
      RULES:
      1. Use the 'getRealTimeNews' tool automatically when the user asks about current market trends, stock prices, or recent economic news.${isBudgetCritical ? ' (NOTE: Tool Calling is currently DISABLED due to budget threshold. Respond using only internal knowledge and RAG.)' : ''}
      2. Analyze the real-time data and the user's past memory to provide highly practical, fact-based investment guidance.
      3. NEVER use illegal words ("무조건 매수", "수익 보장", "확정 수익", "원금 보장").
      4. When the context calls for it, subtly suggest relevant premium B2B resources using Markdown links from the catalog below.
      5. NEVER implement screen blur, button lock, or any intrusive UI control in your responses.
      [PAST MEMORY]
      ${contextStr}
      [B2B RESOURCE CATALOG]
      ${b2bCatalog}
    `;

    // ── 4. Log user message + Update activity timestamp (M-03 Fix) ──
    supabase.from('heritage_logs').insert({
      user_id: userId, role: 'user', content: latestMessage, embedding: embedding
    }).then();
    supabase.from('profiles').update({ updated_at: new Date().toISOString() }).eq('id', userId).then();

    // ── 5. Define Tools (conditionally disabled by budget) ──
    const tools = isBudgetCritical ? {} : {
      getRealTimeNews: tool({
        description: 'Fetch the latest real-time news and market updates from the web.',
        parameters: z.object({ query: z.string().describe('Search query for market news') }),
        execute: async ({ query }) => {
          // M-01 Fix: AbortController for 1500ms timeout
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), SEARCH_TIMEOUT_MS);
          try {
            const searchRes = await fetch('https://api.tavily.com/search', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              signal: controller.signal,
              body: JSON.stringify({
                api_key: Deno.env.get('TAVILY_API_KEY'),
                query,
                search_depth: 'basic',
                max_results: 3  // m-02 Fix: 토큰 절약
              })
            });
            clearTimeout(timeoutId);
            const data = await searchRes.json();
            // Log search cost
            supabase.from('api_usage_logs').insert({
              user_id: userId, endpoint: 'search', token_count: 0, estimated_cost_krw: 0.5
            }).then();
            return data.results.map((r:any) => `${r.title}: ${r.content}`).join('\n');
          } catch (err) {
            clearTimeout(timeoutId);
            return '실시간 뉴스를 가져오지 못했습니다. 내부 지식으로 답변합니다.';
          }
        },
      }),
    };

    // ── 6. Stream Text with LLM Timeout (CP-2) ──
    const abortLLM = new AbortController();
    const llmTimeout = setTimeout(() => abortLLM.abort(), LLM_TIMEOUT_MS);

    try {
      const result = await streamText({
        model: openai(LLM_MODEL),
        system: systemPrompt,
        messages,
        maxTokens: MAX_TOKENS,
        tools,
        abortSignal: abortLLM.signal,
      });
      clearTimeout(llmTimeout);

      // ── 7. Post-stream: Log assistant response + Embed (C-01 Fix) ──
      const fullResponse = await result.text;
      const sanitized = sanitizeResponse(fullResponse); // C-02 Fix

      // Log cost
      supabase.from('api_usage_logs').insert({
        user_id: userId, endpoint: 'chat', token_count: MAX_TOKENS, estimated_cost_krw: 0.3
      }).then();

      // Embed and store assistant response (C-01 Fix: 양방향 Heritage)
      const assistantEmbedRes = await fetch('https://api.openai.com/v1/embeddings', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${Deno.env.get('OPENAI_API_KEY')}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: sanitized, model: EMBEDDING_MODEL })
      });
      const assistantEmbedData = await assistantEmbedRes.json();
      supabase.from('heritage_logs').insert({
        user_id: userId, role: 'assistant', content: sanitized, embedding: assistantEmbedData.data[0].embedding
      }).then();

      return result.toDataStreamResponse({ headers: corsHeaders });

    } catch (streamError) {
      clearTimeout(llmTimeout);
      // CP-2 Fallback: 로컬 위로 템플릿
      const fallback = JSON.stringify({
        role: 'assistant',
        content: '지금 서버가 잠시 바빠요. 잠깐만 기다려 주시면 더 좋은 답변을 드릴게요. 😊'
      });
      return new Response(fallback, { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } });
    }

  } catch (error) {
    return new Response(JSON.stringify({ error: "Internal Server Error" }), { status: 500, headers: corsHeaders });
  }
});
```

### 3.2 `/supabase/functions/cron-push/index.ts` (C-05 Fix: FCM Push)

24시간 미접속자를 감지하여 LLM 기반 위로 메시지를 FCM으로 발송한다.

```typescript
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { openai } from 'npm:@ai-sdk/openai'
import { generateText } from 'npm:ai'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  try {
    const supabase = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!);

    // 1. 24시간 미접속자 추출
    const cutoff = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
    const { data: inactiveUsers } = await supabase
      .from('profiles')
      .select('id, persona_name, persona_tone, fcm_token')
      .lt('updated_at', cutoff)
      .not('fcm_token', 'is', null);

    if (!inactiveUsers || inactiveUsers.length === 0) {
      return new Response(JSON.stringify({ pushed: 0 }), { status: 200 });
    }

    // 2. 각 유저별 맞춤 선톡 메시지 생성 + FCM 발송
    const results = [];
    for (const user of inactiveUsers) {
      const { text } = await generateText({
        model: openai('gpt-4o-mini'),
        prompt: `You are '${user.persona_name}' (tone: ${user.persona_tone}). 
                 Generate a short, warm push notification message (under 50 chars) 
                 to bring the user back. Do NOT mention stocks or investments directly.`,
        maxTokens: 60,
      });

      // FCM 발송
      if (user.fcm_token) {
        await fetch('https://fcm.googleapis.com/fcm/send', {
          method: 'POST',
          headers: {
            'Authorization': `key=${Deno.env.get('FCM_SERVER_KEY')}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            to: user.fcm_token,
            notification: { title: user.persona_name, body: text },
          }),
        });
        results.push({ userId: user.id, status: 'sent' });
      }
    }

    return new Response(JSON.stringify({ pushed: results.length, details: results }), { status: 200 });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Cron Push Failed' }), { status: 500 });
  }
});
```

---

## 4. React Native Client Implementation

### 4.1 `src/hooks/useVesperChat.ts`
```typescript
import { useChat } from '@ai-sdk/react';

// m-03 Fix: 적절한 타입 정의
interface FallbackMessage {
  id: string;
  role: 'assistant';
  content: string;
}

export function useVesperChat(userId: string) {
  const { messages, input, handleInputChange, handleSubmit, setMessages } = useChat({
    api: 'https://[SUPABASE_ID].supabase.co/functions/v1/chat',
    headers: { Authorization: `Bearer [SUPABASE_ANON_KEY]` },
    body: { userId },
    onError: (error) => {
      const fallbackMsg: FallbackMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: '연결이 지연되고 있습니다. 잠시만 기다려 주세요.'
      };
      setMessages((prev) => [...prev, fallbackMsg as any]);
    }
  });

  return { messages, input, handleInputChange, handleSubmit };
}
```

### 4.2 `src/utils/complianceFilter.ts` (C-02 Client-side Double Check)
```typescript
const ILLEGAL_REGEX = /(무조건 매수|수익률 보장|확정 수익|원금 보장|반드시 오른다)/g;

export function clientSanitize(text: string): string {
  return text.replace(ILLEGAL_REGEX, '[규제 마스킹]');
}
```

---

**[문서 끝 - SRS-004-VIBE v5.0 | Audit C-01~C-05, M-01~M-03, m-01~m-03 반영]**
