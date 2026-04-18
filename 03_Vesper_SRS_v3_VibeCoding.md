# Vesper AI Companion OS - System Prompt & Architecture Guide
**[Vibe Coding (AI Agent) 전용 마스터 지시서]**

**Document ID:** SRS-004-VIBE
**Revision:** 4.3 (Real-time Web Grounding via Tool Calling)
**Target:** Cursor, Windsurf, GitHub Copilot 등 AI 코딩 에이전트
**Rule Zero:** AI 에이전트는 환각(Hallucination) 없이 본 문서에 기재된 아키텍처와 코드를 구현하라. 사용자의 화면을 블러 처리하는 요소를 절대 넣지 마라. 대화 중 최신 시장 정보가 필요할 경우 반드시 **Vercel AI SDK의 Tool Calling** 기능을 활용해 실시간 웹 데이터를 긁어와야 한다.

---

## 1. Absolute Constraints (절대 규칙)

1. **NO CUSTOM BACKEND:** 서버는 오직 `Supabase Edge Functions (Deno)` 로만 작성한다.
2. **REAL-TIME DATA:** 정적 지식에 의존하지 말고, 최신 투자 트렌드 질문에는 Tavily API (또는 검색 도구)를 통해 실시간 뉴스를 조회하라.
3. **STRICT BUDGET LIMIT:** `gpt-4o-mini` 모델 사용.
4. **NATIVE FETCH:** Edge Functions 내 `axios` 사용 금지. native `fetch` 사용.
5. **UI FRAMEWORK:** React Native (Expo) + NativeWind.

---

## 2. Comprehensive Database Schema (Seed.sql)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

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

CREATE OR REPLACE FUNCTION match_heritage_logs(
  query_embedding VECTOR(1536), match_threshold FLOAT, match_count INT, p_user_id UUID
) RETURNS TABLE (id UUID, content TEXT, similarity FLOAT) LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY SELECT h.id, h.content, 1 - (h.embedding <=> query_embedding) AS similarity
  FROM heritage_logs h WHERE h.user_id = p_user_id AND 1 - (h.embedding <=> query_embedding) > match_threshold
  ORDER BY h.embedding <=> query_embedding LIMIT match_count;
END; $$;
```

---

## 3. Edge Function Source Codes (Deno)

### 3.1 `/supabase/functions/chat/index.ts` (RAG + Tool Calling + B2B Nudge)
시스템 프롬프트와 Vercel AI SDK의 `tools` 옵션을 활용하여 **실시간 웹데이터 수집**과 **실전/교육 자료 큐레이션**을 동시 수행한다.

```typescript
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { openai } from 'npm:@ai-sdk/openai'
import { streamText, tool } from 'npm:ai'
import { z } from 'npm:zod'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type' };

serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders });

  try {
    const { messages, userId } = await req.json();
    const supabase = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!);

    const { data: profile } = await supabase.from('profiles').select('*').eq('id', userId).single();
    const latestMessage = messages[messages.length - 1].content;
    
    // 1. RAG Vector Search
    const embedRes = await fetch('https://api.openai.com/v1/embeddings', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${Deno.env.get('OPENAI_API_KEY')}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ input: latestMessage, model: 'text-embedding-3-small' })
    });
    const embedData = await embedRes.json();
    const embedding = embedData.data[0].embedding;

    const { data: ragDocs } = await supabase.rpc('match_heritage_logs', {
      query_embedding: embedding, match_threshold: 0.7, match_count: 3, p_user_id: userId
    });
    const contextStr = ragDocs?.map((d: any) => d.content).join('\n') || "";

    // 2. System Prompt
    const systemPrompt = `
      You are '${profile.persona_name}'. Tone: '${profile.persona_tone}'.
      RULES:
      1. Use the 'getRealTimeNews' tool automatically when the user asks about current market trends, stock prices, or recent economic news.
      2. Analyze the real-time data and the user's past memory to provide highly practical, fact-based investment guidance.
      3. NEVER use illegal words ("무조건 매수", "수익 보장").
      4. Subtly provide Markdown links to premium B2B education or practical resources if the user needs structured growth.
      [PAST MEMORY]
      ${contextStr}
    `;

    // 3. Log user message asynchronously
    supabase.from('heritage_logs').insert({
      user_id: userId, role: 'user', content: latestMessage, embedding: embedding
    }).then();

    // 4. Stream Text with Tools (Web Grounding)
    const result = await streamText({
      model: openai('gpt-4o-mini'),
      system: systemPrompt,
      messages,
      maxTokens: 250, 
      tools: {
        getRealTimeNews: tool({
          description: 'Fetch the latest real-time news and market updates from the web.',
          parameters: z.object({ query: z.string().describe('Search query for market news') }),
          execute: async ({ query }) => {
            // Use Tavily or duckduckgo search API here
            const searchRes = await fetch('https://api.tavily.com/search', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ api_key: Deno.env.get('TAVILY_API_KEY'), query, search_depth: 'basic' })
            });
            const data = await searchRes.json();
            return data.results.map((r:any) => `${r.title}: ${r.content}`).join('\n');
          },
        }),
      },
    });

    return result.toDataStreamResponse({ headers: corsHeaders });

  } catch (error) {
    return new Response(JSON.stringify({ error: "LLM Timeout" }), { status: 500, headers: corsHeaders });
  }
});
```

---

## 4. React Native Client Implementation

### 4.1 `src/hooks/useVesperChat.ts`
```typescript
import { useChat } from '@ai-sdk/react';

export function useVesperChat(userId: string) {
  const { messages, input, handleInputChange, handleSubmit, setMessages } = useChat({
    api: 'https://[SUPABASE_ID].supabase.co/functions/v1/chat',
    headers: { Authorization: `Bearer [SUPABASE_ANON_KEY]` },
    body: { userId },
    onError: (error) => {
      const fallbackMsg = { id: Date.now().toString(), role: 'assistant', content: '연결이 지연되고 있습니다. 잠시만 기다려 주세요.' };
      setMessages((prev) => [...prev, fallbackMsg as any]);
    }
  });

  return { messages, input, handleInputChange, handleSubmit };
}
```
