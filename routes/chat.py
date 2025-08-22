import os
import openai
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

chat_bp = Blueprint('chat', __name__)

# Crisis keywords for safety detection
CRISIS_KEYWORDS = [
    'suicide', 'kill myself', 'end my life', 'want to die', 'better off dead',
    'hurt myself', 'self harm', 'cut myself', 'overdose', 'pills',
    'jump off', 'hang myself', 'gun', 'knife', 'razor',
    'abuse', 'hitting me', 'hurting me', 'touching me'
]

def detect_crisis(message):
    """Detect if a message contains crisis-related content"""
    message_lower = message.lower()
    for keyword in CRISIS_KEYWORDS:
        if keyword in message_lower:
            return True
    return False

def get_crisis_response():
    """Return a crisis intervention response"""
    return {
        'message': "I'm really concerned about what you've shared. Your safety is the most important thing right now. Please reach out to someone who can help immediately:\n\n🚨 **Emergency: Call 911**\n📞 **Suicide Prevention: Call or text 988**\n💬 **Crisis Text Line: Text HOME to 741741**\n\nYou don't have to go through this alone. There are people who want to help you.",
        'is_crisis': True,
        'resources': [
            {'name': 'Emergency Services', 'contact': '911'},
            {'name': 'Suicide Prevention Lifeline', 'contact': '988'},
            {'name': 'Crisis Text Line', 'contact': 'Text HOME to 741741'}
        ]
    }

@chat_bp.route('/chat', methods=['POST'])
@cross_origin()
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Check for crisis content
        if detect_crisis(user_message):
            return jsonify(get_crisis_response())
        
        # Prepare the system prompt for empathetic mental health support
        system_prompt = """You are AuraMind, an AI companion designed to provide empathetic, non-judgmental mental health support for youth aged 13-24. Your role is to:

1. Listen actively and validate their feelings
2. Provide emotional support and encouragement
3. Offer practical coping strategies when appropriate
4. Guide them to professional resources when needed
5. Maintain a warm, understanding, and age-appropriate tone

Important guidelines:
- Never diagnose mental health conditions
- Don't provide medical advice
- Always validate their feelings and experiences
- Use empathetic language and show genuine care
- Keep responses concise but meaningful
- If they mention serious concerns, gently suggest professional help
- Focus on their strengths and resilience

Remember: You're a supportive companion, not a replacement for professional mental health care."""

        # Call OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        ai_message = response.choices[0].message.content
        
        return jsonify({
            'message': ai_message,
            'is_crisis': False
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'I apologize, but I\'m having trouble responding right now. Please try again in a moment.',
            'is_crisis': False
        }), 500

@chat_bp.route('/resources', methods=['GET'])
@cross_origin()
def get_resources():
    """Get mental health resources"""
    resources = {
        'crisis': [
            {
                'name': 'National Suicide Prevention Lifeline',
                'contact': '988',
                'description': '24/7 crisis support',
                'type': 'phone'
            },
            {
                'name': 'Crisis Text Line',
                'contact': 'Text HOME to 741741',
                'description': '24/7 text-based crisis support',
                'type': 'text'
            },
            {
                'name': 'SAMHSA National Helpline',
                'contact': '1-800-662-4357',
                'description': 'Treatment referral and information service',
                'type': 'phone'
            }
        ],
        'apps': [
            {
                'name': 'Calm',
                'description': 'Meditation and sleep stories',
                'category': 'mindfulness'
            },
            {
                'name': 'Headspace',
                'description': 'Mindfulness and meditation',
                'category': 'mindfulness'
            },
            {
                'name': 'Sanvello',
                'description': 'Anxiety and mood tracking',
                'category': 'tracking'
            }
        ],
        'articles': [
            {
                'title': 'Understanding Anxiety',
                'description': 'Learn about anxiety, its symptoms, and healthy coping strategies.',
                'category': 'education'
            },
            {
                'title': 'Building Resilience',
                'description': 'Discover techniques to build emotional resilience and bounce back from challenges.',
                'category': 'skills'
            },
            {
                'title': 'Mindfulness and Meditation',
                'description': 'Explore mindfulness practices that can help reduce stress and improve mental well-being.',
                'category': 'mindfulness'
            }
        ]
    }
    
    return jsonify(resources)

