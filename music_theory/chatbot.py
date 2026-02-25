import logging
from django.conf import settings
from django.db.models import Q
from .models import Topic, ChordProgression

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """あなたは「残音」の音楽理論アシスタントです。作曲・編曲をサポートする専門家として振る舞ってください。

## 役割
- J-POP、邦楽を中心とした作曲・編曲のアドバイスを提供する
- 音楽理論（スケール、コード、コード進行、リズムなど）の質問に答える
- ユーザーの作曲プロジェクトを支援する

## ルール
- 日本語で回答すること
- 具体例を交えること（例: 「この進行はback numberの"高嶺の花子さん"で使われています」）
- ディグリーネーム（I, IIm, IIIm, IV, V, VIm, VIIdim）を積極的に使用すること
- 簡潔に回答すること（長すぎる回答は避ける）
- 音楽以外の質問は丁寧に断ること
- 参照データが提供された場合、それを活用して回答すること
"""


def _extract_keywords(query):
    stop_words = {
        'の', 'に', 'は', 'を', 'が', 'で', 'と', 'も', 'から', 'まで',
        'より', 'な', 'だ', 'です', 'ます', 'た', 'て', 'して', 'する',
        'ある', 'いる', 'ない', 'この', 'その', 'あの', 'どの',
        'what', 'how', 'the', 'is', 'a', 'an', 'in', 'of', 'to',
        '教えて', 'ください', 'について', 'とは', '知りたい', 'したい',
    }
    words = query.replace('　', ' ').split()
    return [w for w in words if w not in stop_words and len(w) > 1]


def retrieve_relevant_context(query):
    keywords = _extract_keywords(query)
    if not keywords:
        keywords = [query]

    topic_q = Q()
    for kw in keywords:
        topic_q |= (
            Q(title__icontains=kw) |
            Q(tags__icontains=kw) |
            Q(summary__icontains=kw) |
            Q(body__icontains=kw)
        )
    topics = Topic.objects.filter(topic_q).distinct()[:3]

    prog_q = Q()
    for kw in keywords:
        prog_q |= (
            Q(name__icontains=kw) |
            Q(degrees__icontains=kw) |
            Q(tags__icontains=kw) |
            Q(description__icontains=kw)
        )
    progressions = ChordProgression.objects.filter(prog_q).distinct()[:3]

    return list(topics), list(progressions)


def format_context_for_prompt(topics, progressions):
    if not topics and not progressions:
        return ''

    parts = ['【参照データ】']

    if topics:
        parts.append('\n■ 関連トピック:')
        for t in topics:
            parts.append(f'・{t.title}: {t.summary}')
            if t.body:
                body_preview = t.body[:300]
                parts.append(f'  詳細: {body_preview}')

    if progressions:
        parts.append('\n■ 関連コード進行:')
        for p in progressions:
            parts.append(f'・{p.name}: {p.degrees} (Cキー: {p.chords_in_c})')
            if p.description:
                parts.append(f'  説明: {p.description[:200]}')

    return '\n'.join(parts)


def get_gemini_response(conversation_messages, user_query, context_text=''):
    try:
        import google.generativeai as genai
    except ImportError:
        return 'チャットボット機能は現在利用できません（ライブラリ未インストール）。'

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return 'チャットボット機能は現在設定中です。しばらくお待ちください。'

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-lite',
            system_instruction=SYSTEM_PROMPT,
        )

        history = []
        for msg in conversation_messages:
            history.append({
                'role': 'user' if msg.role == 'user' else 'model',
                'parts': [msg.content],
            })

        chat = model.start_chat(history=history)

        prompt = user_query
        if context_text:
            prompt = f'{context_text}\n\n【ユーザーの質問】\n{user_query}'

        response = chat.send_message(prompt)
        return response.text

    except Exception as e:
        logger.error(f'Gemini API error: {e}')
        return 'すみません、回答の生成中にエラーが発生しました。もう一度お試しください。'
