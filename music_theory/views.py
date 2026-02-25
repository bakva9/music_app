from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Topic, Bookmark, ChordProgression, Conversation, Message
from .chatbot import retrieve_relevant_context, format_context_for_prompt, get_gemini_response


def topic_list(request):
    topics = Topic.objects.all()
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    if query:
        topics = topics.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(tags__icontains=query) |
            Q(body__icontains=query)
        )
    if category:
        topics = topics.filter(category=category)

    context = {
        'topics': topics,
        'query': query,
        'current_category': category,
        'categories': Topic.CATEGORY_CHOICES,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'music_theory/_topic_search_results.html', context)
    return render(request, 'music_theory/topic_list.html', context)


def topic_detail(request, slug):
    topic = get_object_or_404(Topic, slug=slug)
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, topic=topic).exists()
    return render(request, 'music_theory/topic_detail.html', {
        'topic': topic,
        'is_bookmarked': is_bookmarked,
        'related_topics': topic.related_topics.all(),
    })


@login_required
def toggle_bookmark(request, slug):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    topic = get_object_or_404(Topic, slug=slug)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, topic=topic)
    if not created:
        bookmark.delete()
        is_bookmarked = False
    else:
        is_bookmarked = True
    if request.headers.get('HX-Request'):
        return render(request, 'music_theory/_bookmark_button.html', {
            'topic': topic,
            'is_bookmarked': is_bookmarked,
        })
    return JsonResponse({'is_bookmarked': is_bookmarked})


@login_required
def bookmark_list(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('topic').order_by('-created_at')
    return render(request, 'music_theory/bookmark_list.html', {'bookmarks': bookmarks})


def progression_list(request):
    progressions = ChordProgression.objects.all()
    starting = request.GET.get('starting', '')
    if starting:
        progressions = progressions.filter(starting_chord=starting)
    context = {
        'progressions': progressions,
        'current_starting': starting,
        'starting_choices': ChordProgression.STARTING_CHOICES,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'music_theory/_progression_results.html', context)
    return render(request, 'music_theory/progression_list.html', context)


def diatonic_reference(request):
    return render(request, 'music_theory/diatonic_reference.html')


@login_required
@require_POST
def chat_send(request):
    user_message = request.POST.get('message', '').strip()
    conversation_id = request.POST.get('conversation_id', '').strip()

    if not user_message:
        return render(request, 'music_theory/_chat_error.html', {
            'error': 'メッセージを入力してください。'
        })

    # Rate limit: 10 messages per minute per user
    one_minute_ago = timezone.now() - timedelta(minutes=1)
    recent_count = Message.objects.filter(
        conversation__user=request.user,
        role='user',
        created_at__gte=one_minute_ago,
    ).count()
    if recent_count >= 10:
        return render(request, 'music_theory/_chat_error.html', {
            'error': 'メッセージの送信が速すぎます。少し待ってから再度お試しください。'
        })

    # Rate limit: 1400 messages per day globally
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    daily_count = Message.objects.filter(
        role='user',
        created_at__gte=today_start,
    ).count()
    if daily_count >= 1400:
        return render(request, 'music_theory/_chat_error.html', {
            'error': '本日のチャット利用上限に達しました。明日またお試しください。'
        })

    # Get or create conversation
    conversation = None
    if conversation_id:
        try:
            conversation = Conversation.objects.get(
                id=int(conversation_id), user=request.user
            )
        except (Conversation.DoesNotExist, ValueError):
            pass

    if not conversation:
        title = user_message[:50] if len(user_message) > 50 else user_message
        conversation = Conversation.objects.create(
            user=request.user, title=title
        )

    # Save user message
    user_msg = Message.objects.create(
        conversation=conversation, role='user', content=user_message
    )

    # RAG: retrieve relevant context
    topics, progressions = retrieve_relevant_context(user_message)
    context_text = format_context_for_prompt(topics, progressions)

    # Get conversation history (last 20 messages for context window)
    history = list(
        conversation.messages.exclude(id=user_msg.id).order_by('created_at')[:20]
    )

    # Call Gemini
    response_text = get_gemini_response(history, user_message, context_text)

    # Save assistant message
    assistant_msg = Message.objects.create(
        conversation=conversation, role='assistant', content=response_text
    )
    if topics:
        assistant_msg.context_topics.set(topics)

    # Update conversation timestamp
    conversation.save()

    response = render(request, 'music_theory/_chat_messages.html', {
        'user_message': user_msg,
        'assistant_message': assistant_msg,
        'context_topics': topics,
    })
    response['HX-Trigger'] = f'{{"chatConversationId": "{conversation.id}"}}'
    return response


@login_required
def chat_history(request):
    conversations = Conversation.objects.filter(
        user=request.user
    )[:20]
    return render(request, 'music_theory/_chat_history.html', {
        'conversations': conversations,
    })


@login_required
def chat_load(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )
    messages = conversation.messages.all().prefetch_related('context_topics')
    return render(request, 'music_theory/_chat_load.html', {
        'conversation': conversation,
        'messages': messages,
    })
