import random
import time

# ============================================================================
# DETERMINISTIC CAPTION ENGINE - POSITIVE/MOTIVATIONAL ONLY
# Zero ML dependencies - 100% rule-based with rich variation
# All captions are positive and encouraging - NO corrective suggestions
# ============================================================================

# GROUP PHOTO CAPTIONS (50+ variants)
GROUP_SMILING = [
    "Amazing group energy! Everyone nailed the smile 😄🔥",
    "Squad goals achieved! Perfect smiles all around 😎",
    "What a fantastic crew! Those smiles are contagious 😊",
    "Group perfection! Everyone's bringing the joy 🎉",
    "Incredible team spirit! Love those genuine smiles ✨",
    "Best group shot ever! The happiness is real 😄",
    "Awesome squad! Those smiles light up the frame 🌟",
    "Perfect harmony! Everyone's smile game is strong 💪",
    "What a beautiful group! Smiles on point 😊",
    "Epic crew moment! The joy is palpable 🔥",
    "Fantastic group vibe! Smiles for days 😎",
    "Dream team captured! Those grins are golden ✨",
    "Stellar group shot! Everyone's radiating happiness 🌟",
    "Amazing chemistry! The smiles say it all 😄",
    "Perfect squad moment! Joy overload 🎊",
    "Brilliant group capture! Smiles that inspire 💫",
    "What a crew! Those smiles are everything 😊",
    "Group excellence! The happiness is infectious 🔥",
    "Incredible moment! Everyone's smile shines bright ✨",
    "Squad perfection! Those grins are legendary 😎",
    "Beautiful group energy! Smiles that warm hearts 💖",
    "Epic team shot! The joy is undeniable 🎉",
    "Fantastic crew! Those smiles are pure gold 🌟",
    "Perfect group harmony! Everyone's glowing 😄",
    "Amazing squad vibes! Smiles that tell a story 📸",
    "Dream team moment! The happiness radiates 💫",
    "Stellar crew! Those smiles are picture-perfect ✨",
    "What a group! Joy captured beautifully 😊",
    "Incredible squad! Smiles that light up the world 🌍",
    "Perfect team spirit! Everyone's beaming 😎",
    "Brilliant group shot! The smiles are magnetic 🔥",
    "Amazing crew energy! Joy in every face 🎊",
    "Fantastic squad! Those grins are unforgettable 💖",
    "Epic group moment! Smiles that inspire joy ✨",
    "Beautiful team! Everyone's happiness shines through 🌟",
    "Perfect crew capture! The smiles are authentic 😄",
    "Stellar squad! Joy radiating from every smile 💫",
    "What a team! Those smiles are contagious 😊",
    "Incredible group! Happiness captured perfectly 📸",
    "Amazing crew! Smiles that brighten the day ☀️",
    "Dream squad moment! Everyone's joy is visible 🎉",
    "Fantastic group! Those smiles are heartwarming 💖",
    "Perfect team energy! Smiles all around 😎",
    "Brilliant crew! The happiness is overwhelming ✨",
    "Epic squad shot! Joy in its purest form 🔥",
    "What a group! Smiles that make memories 📷",
    "Stellar team! Everyone's radiating pure joy 🌟",
    "Amazing squad! Those smiles are priceless 💎",
    "Beautiful crew! Happiness captured in time ⏰",
    "Perfect group! The joy is absolutely real 😄",
]

GROUP_NOT_SMILING = [
    "Great group! Looking good together 😊",
    "Awesome crew! Nice capture 😄",
    "Nice squad! Great moment ✨",
    "Cool group! Well done 🌟",
    "Solid team! Looking sharp 💫",
    "Good crew! Nice shot 😊",
    "Nice group! Great capture 📸",
    "Great squad! Looking good 🔥",
    "Awesome team! Well captured 😄",
    "Cool crew! Nice moment ✨",
    "Solid group! Looking great 💖",
    "Good squad! Nice capture 🌟",
    "Nice team! Great shot 😊",
    "Great crew! Looking good 💫",
    "Awesome group! Well done 😄",
    "Cool squad! Nice capture ✨",
    "Solid crew! Looking sharp 🔥",
    "Good team! Great moment 💖",
    "Nice group! Well captured 😊",
    "Great squad! Looking good 🌟",
]

# CHILD CAPTIONS - Strong Smile (50+ variants)
CHILD_STRONG_SMILE = [
    "That's a brilliant smile, little champ! 😄🔥",
    "Wow! What an amazing smile, superstar! ⭐",
    "Incredible grin, little one! You're shining bright ✨",
    "That smile could light up the world! 🌟",
    "Perfect smile, champ! You're a natural 😊",
    "What a beautiful smile! You're glowing 💫",
    "Amazing smile, little star! Keep shining ⭐",
    "That grin is pure magic! Fantastic job 🎉",
    "Brilliant smile! You're absolutely radiant 😄",
    "What a joyful smile! You're a sunshine ☀️",
    "Perfect capture! That smile is everything 💖",
    "Incredible smile, champ! You're amazing 🔥",
    "That grin lights up the frame! Superb ✨",
    "Beautiful smile! You're a little superstar 🌟",
    "Amazing job! That smile is contagious 😊",
    "What a fantastic smile! You're glowing 💫",
    "Perfect smile, little one! Pure joy captured ⭐",
    "That grin is absolutely wonderful! 😄",
    "Brilliant smile! You're radiating happiness 🎊",
    "Incredible capture! That smile is golden ✨",
    "What a beautiful grin! You're shining 🌟",
    "Amazing smile, champ! You're a star 💖",
    "Perfect joy captured! That smile rocks 🔥",
    "That grin is pure happiness! Fantastic 😊",
    "Beautiful smile! You're absolutely glowing 💫",
    "Incredible smile, little star! Keep it up ⭐",
    "What a joyful grin! You're amazing 😄",
    "Perfect smile! You're a natural superstar 🌟",
    "That smile is absolutely brilliant! ✨",
    "Amazing capture! That grin is priceless 💎",
    "Beautiful smile, champ! You're radiant 😊",
    "Incredible joy! That smile is everything 💖",
    "What a fantastic grin! You're glowing 🔥",
    "Perfect smile! You're a little champion 💫",
    "That smile lights up everything! Superb ⭐",
    "Amazing grin, little one! Pure magic 😄",
    "Beautiful capture! That smile shines 🌟",
    "Incredible smile! You're absolutely wonderful ✨",
    "What a joyful smile! You're a star 💖",
    "Perfect grin, champ! You're glowing 😊",
    "That smile is pure sunshine! Amazing ☀️",
    "Brilliant capture! That grin is golden 🔥",
    "Beautiful smile! You're radiating joy 💫",
    "Incredible grin, little star! Fantastic ⭐",
    "What an amazing smile! You're shining 😄",
    "Perfect joy! That smile is contagious 🌟",
    "That grin is absolutely perfect! ✨",
    "Amazing smile, champ! You're brilliant 💖",
    "Beautiful capture! That smile rocks 😊",
    "Incredible smile! You're a superstar 🔥",
]

# CHILD CAPTIONS - Moderate Smile (50+ variants)
CHILD_MODERATE_SMILE = [
    "Lovely smile, little champ! 😊",
    "Sweet grin! You're doing great 🌟",
    "Nice smile! You're shining ✨",
    "Great smile! Keep it up 😄",
    "Wonderful grin! You're glowing 💫",
    "Beautiful smile! You rock ⭐",
    "Perfect smile! You're amazing 🔥",
    "Awesome grin! You're fantastic 💖",
    "Lovely smile! You're brilliant 😊",
    "Sweet smile! You're wonderful 🌟",
    "Nice grin! You're shining bright ✨",
    "Great smile! You're a star 😄",
    "Wonderful smile! You're glowing 💫",
    "Beautiful grin! You're amazing ⭐",
    "Perfect smile! You're doing great 🔥",
    "Awesome smile! You're fantastic 💖",
    "Lovely grin! You're brilliant 😊",
    "Sweet smile! You're wonderful 🌟",
    "Nice smile! You're shining ✨",
    "Great grin! You're a star 😄",
    "Wonderful smile! You're glowing 💫",
    "Beautiful smile! You're amazing ⭐",
    "Perfect grin! You're doing great 🔥",
    "Awesome smile! You're fantastic 💖",
    "Lovely smile! You're brilliant 😊",
    "Sweet grin! You're wonderful 🌟",
    "Nice smile! You're shining bright ✨",
    "Great smile! You're a star 😄",
    "Wonderful grin! You're glowing 💫",
    "Beautiful smile! You're amazing ⭐",
    "Perfect smile! You're doing great 🔥",
    "Awesome grin! You're fantastic 💖",
    "Lovely smile! You're brilliant 😊",
    "Sweet smile! You're wonderful 🌟",
    "Nice grin! You're shining ✨",
    "Great smile! You're a star 😄",
    "Wonderful smile! You're glowing 💫",
    "Beautiful grin! You're amazing ⭐",
    "Perfect smile! You're doing great 🔥",
    "Awesome smile! You're fantastic 💖",
    "Lovely grin! You're brilliant 😊",
    "Sweet smile! You're wonderful 🌟",
    "Nice smile! You're shining bright ✨",
    "Great grin! You're a star 😄",
    "Wonderful smile! You're glowing 💫",
    "Beautiful smile! You're amazing ⭐",
    "Perfect grin! You're doing great 🔥",
    "Awesome smile! You're fantastic 💖",
    "Lovely smile! You're brilliant 😊",
    "Sweet grin! You're wonderful 🌟",
]

# CHILD CAPTIONS - Subtle/No Smile (50+ variants)
CHILD_SUBTLE_SMILE = [
    "Nice photo, little champ! 😊",
    "Sweet capture! Looking good 🌟",
    "Great shot! You're wonderful ✨",
    "Lovely photo! You're amazing 😄",
    "Nice capture! You're fantastic 💫",
    "Sweet shot! You're brilliant ⭐",
    "Great photo! You're a star 🔥",
    "Lovely capture! You're glowing 💖",
    "Nice shot! You're wonderful 😊",
    "Sweet photo! You're amazing 🌟",
    "Great capture! You're fantastic ✨",
    "Lovely shot! You're brilliant 😄",
    "Nice photo! You're a star 💫",
    "Sweet capture! You're glowing ⭐",
    "Great shot! You're wonderful 🔥",
    "Lovely photo! You're amazing 💖",
    "Nice capture! You're fantastic 😊",
    "Sweet shot! You're brilliant 🌟",
    "Great photo! You're a star ✨",
    "Lovely capture! You're glowing 😄",
    "Nice shot! You're wonderful 💫",
    "Sweet photo! You're amazing ⭐",
    "Great capture! You're fantastic 🔥",
    "Lovely shot! You're brilliant 💖",
    "Nice photo! You're a star 😊",
    "Sweet capture! You're glowing 🌟",
    "Great shot! You're wonderful ✨",
    "Lovely photo! You're amazing 😄",
    "Nice capture! You're fantastic 💫",
    "Sweet shot! You're brilliant ⭐",
    "Great photo! You're a star 🔥",
    "Lovely capture! You're glowing 💖",
    "Nice shot! You're wonderful 😊",
    "Sweet photo! You're amazing 🌟",
    "Great capture! You're fantastic ✨",
    "Lovely shot! You're brilliant 😄",
    "Nice photo! You're a star 💫",
    "Sweet capture! You're glowing ⭐",
    "Great shot! You're wonderful 🔥",
    "Lovely photo! You're amazing 💖",
    "Nice capture! You're fantastic 😊",
    "Sweet shot! You're brilliant 🌟",
    "Great photo! You're a star ✨",
    "Lovely capture! You're glowing 😄",
    "Nice shot! You're wonderful 💫",
    "Sweet photo! You're amazing ⭐",
    "Great capture! You're fantastic 🔥",
    "Lovely shot! You're brilliant 💖",
    "Nice photo! You're a star 😊",
    "Sweet capture! You're glowing 🌟",
]

# YOUNG ADULT CAPTIONS - Strong Smile (50+ variants)
YOUNG_ADULT_STRONG_SMILE = [
    "Confident and camera-ready 😎🔥",
    "Absolutely nailing it! That smile is fire 🔥",
    "Perfect capture! You're glowing ✨",
    "Stunning smile! Camera loves you 📸",
    "Flawless! That confidence shines through 💫",
    "Incredible smile! You're a natural ⭐",
    "Picture-perfect! That grin is everything 😄",
    "Amazing energy! You're radiating joy 🌟",
    "Brilliant smile! You're absolutely glowing 💖",
    "Stellar capture! That smile rocks 🔥",
    "Perfect vibes! You're camera-ready 😎",
    "Fantastic smile! You're shining bright ✨",
    "Incredible capture! That confidence shows 💫",
    "Stunning! You're absolutely radiant ⭐",
    "Flawless smile! You're a natural 😄",
    "Amazing! That grin is contagious 🌟",
    "Brilliant capture! You're glowing 💖",
    "Perfect smile! You're camera-ready 🔥",
    "Stellar! That confidence radiates 😎",
    "Fantastic! You're shining bright ✨",
    "Incredible smile! You're absolutely glowing 💫",
    "Stunning capture! That smile rocks ⭐",
    "Flawless! You're radiating joy 😄",
    "Amazing smile! You're a natural 🌟",
    "Brilliant! That grin is everything 💖",
    "Perfect! You're camera-ready 🔥",
    "Stellar smile! You're glowing 😎",
    "Fantastic capture! That confidence shows ✨",
    "Incredible! You're shining bright 💫",
    "Stunning smile! You're absolutely radiant ⭐",
    "Flawless capture! You're a natural 😄",
    "Amazing! That smile is contagious 🌟",
    "Brilliant smile! You're glowing 💖",
    "Perfect! You're camera-ready 🔥",
    "Stellar! That confidence radiates 😎",
    "Fantastic smile! You're shining bright ✨",
    "Incredible capture! You're absolutely glowing 💫",
    "Stunning! That smile rocks ⭐",
    "Flawless! You're radiating joy 😄",
    "Amazing smile! You're a natural 🌟",
    "Brilliant capture! That grin is everything 💖",
    "Perfect smile! You're camera-ready 🔥",
    "Stellar! You're glowing 😎",
    "Fantastic! That confidence shows ✨",
    "Incredible smile! You're shining bright 💫",
    "Stunning capture! You're absolutely radiant ⭐",
    "Flawless smile! You're a natural 😄",
    "Amazing! That smile is contagious 🌟",
    "Brilliant! You're glowing 💖",
    "Perfect! That confidence shines 🔥",
]

# YOUNG ADULT CAPTIONS - Moderate Smile (50+ variants)
YOUNG_ADULT_MODERATE_SMILE = [
    "Great smile! Looking good 😎",
    "Nice! You're shining ✨",
    "Looking sharp! That smile works 💫",
    "Awesome! You're glowing ⭐",
    "Perfect! That grin is nice 😄",
    "Fantastic! You're looking good 🌟",
    "Brilliant! That smile shines 💖",
    "Great! You're rocking it 😎",
    "Nice smile! Looking sharp ✨",
    "Looking good! You're glowing 💫",
    "Awesome! That smile works ⭐",
    "Perfect! You're looking good 😄",
    "Fantastic! That grin is nice 🌟",
    "Brilliant! You're shining 💖",
    "Great! Looking sharp 😎",
    "Nice! You're glowing ✨",
    "Looking good! That smile works 💫",
    "Awesome! You're looking good ⭐",
    "Perfect! That grin shines 😄",
    "Fantastic! You're rocking it 🌟",
    "Brilliant! That smile is nice 💖",
    "Great! You're glowing 😎",
    "Nice! Looking sharp ✨",
    "Looking good! You're shining 💫",
    "Awesome! That smile works ⭐",
    "Perfect! You're looking good 😄",
    "Fantastic! That grin is nice 🌟",
    "Brilliant! You're rocking it 💖",
    "Great! You're glowing 😎",
    "Nice! That smile shines ✨",
    "Looking sharp! You're looking good 💫",
    "Awesome! That grin works ⭐",
    "Perfect! You're shining 😄",
    "Fantastic! That smile is nice 🌟",
    "Brilliant! You're glowing 💖",
    "Great! Looking sharp 😎",
    "Nice! You're rocking it ✨",
    "Looking good! That smile works 💫",
    "Awesome! You're looking good ⭐",
    "Perfect! That grin shines 😄",
    "Fantastic! You're glowing 🌟",
    "Brilliant! That smile is nice 💖",
    "Great! You're shining 😎",
    "Nice! Looking sharp ✨",
    "Looking good! You're looking good 💫",
    "Awesome! That smile works ⭐",
    "Perfect! You're rocking it 😄",
    "Fantastic! That grin is nice 🌟",
    "Brilliant! You're glowing 💖",
    "Great! That smile shines 😎",
]

# YOUNG ADULT CAPTIONS - Subtle/No Smile (50+ variants)
YOUNG_ADULT_SUBTLE_SMILE = [
    "Looking sharp! Nice capture 😊",
    "Nice! Great shot ✨",
    "Good! Looking good 💫",
    "Looking good! Nice photo ⭐",
    "Great! Well captured 😄",
    "Nice! Good shot 🌟",
    "Looking sharp! Great capture 💖",
    "Good! Nice photo 😊",
    "Nice! Well done ✨",
    "Looking good! Great shot 💫",
    "Great! Nice capture ⭐",
    "Nice! Good photo 😄",
    "Looking sharp! Well captured 🌟",
    "Good! Great shot 💖",
    "Nice! Nice capture 😊",
    "Looking good! Well done ✨",
    "Great! Good photo 💫",
    "Nice! Great capture ⭐",
    "Looking sharp! Nice shot 😄",
    "Good! Well captured 🌟",
    "Nice! Great photo 💖",
    "Looking good! Nice capture 😊",
    "Great! Well done ✨",
    "Nice! Good shot 💫",
    "Looking sharp! Great photo ⭐",
    "Good! Nice capture 😄",
    "Nice! Well captured 🌟",
    "Looking good! Great shot 💖",
    "Great! Good photo 😊",
    "Nice! Nice shot ✨",
    "Looking sharp! Well done 💫",
    "Good! Great capture ⭐",
    "Nice! Good photo 😄",
    "Looking good! Well captured 🌟",
    "Great! Nice shot 💖",
    "Nice! Great photo 😊",
    "Looking sharp! Good capture ✨",
    "Good! Well done 💫",
    "Nice! Great shot ⭐",
    "Looking good! Nice photo 😄",
    "Great! Well captured 🌟",
    "Nice! Good shot 💖",
    "Looking sharp! Great capture 😊",
    "Good! Nice photo ✨",
    "Nice! Well done 💫",
    "Looking good! Great photo ⭐",
    "Great! Good capture 😄",
    "Nice! Nice shot 🌟",
    "Looking sharp! Well captured 💖",
    "Good! Great photo 😊",
]

# ADULT/SENIOR CAPTIONS - Use same pools as young adult for consistency
ADULT_STRONG_SMILE = YOUNG_ADULT_STRONG_SMILE
ADULT_MODERATE_SMILE = YOUNG_ADULT_MODERATE_SMILE
ADULT_SUBTLE_SMILE = YOUNG_ADULT_SUBTLE_SMILE


def generate_caption(age_range: str, smile_detected: bool, blur_score: float, 
                    face_count: int = 1, smile_level: str = "Moderate Smile", 
                    smile_strength: float = 50.0) -> str:
    """
    Deterministic caption generation with rich variation.
    Zero ML dependencies - 100% rule-based with randomized selection.
    ALL CAPTIONS ARE POSITIVE AND MOTIVATIONAL - NO CORRECTIVE SUGGESTIONS.
    
    Args:
        age_range: Age range string like "(0-2)", "(15-20)", etc.
        smile_detected: Whether smile was detected
        blur_score: Image quality score (not used for corrections)
        face_count: Number of faces in the photo (default: 1)
        smile_level: Smile level - "Strong Smile", "Moderate Smile", "Subtle Smile"
        smile_strength: Numeric smile strength 0-100
        
    Returns:
        str: Generated caption (< 120 characters)
    """
    # Seed random with current time for variation
    random.seed(int(time.time()) % 100000)
    
    # Parse age range to determine age category
    try:
        age_lower = int(age_range.strip("()").split("-")[0])
    except:
        age_lower = 25  # Default to adult if parsing fails
    
    # Determine age category
    if age_lower <= 12:
        age_category = "child"
    elif age_lower <= 25:
        age_category = "young_adult"
    else:
        age_category = "adult"
    
    # Handle group photos
    if face_count > 1:
        if smile_detected:
            return random.choice(GROUP_SMILING)
        else:
            return random.choice(GROUP_NOT_SMILING)
    
    # Select caption pool based on age and smile level
    caption_pool = []
    
    if age_category == "child":
        if smile_level == "Strong Smile":
            caption_pool = CHILD_STRONG_SMILE
        elif smile_level == "Moderate Smile":
            caption_pool = CHILD_MODERATE_SMILE
        else:  # Subtle or No smile
            caption_pool = CHILD_SUBTLE_SMILE
    
    elif age_category == "young_adult":
        if smile_level == "Strong Smile":
            caption_pool = YOUNG_ADULT_STRONG_SMILE
        elif smile_level == "Moderate Smile":
            caption_pool = YOUNG_ADULT_MODERATE_SMILE
        else:  # Subtle or No smile
            caption_pool = YOUNG_ADULT_SUBTLE_SMILE
    
    else:  # adult/senior
        if smile_level == "Strong Smile":
            caption_pool = ADULT_STRONG_SMILE
        elif smile_level == "Moderate Smile":
            caption_pool = ADULT_MODERATE_SMILE
        else:  # Subtle or No smile
            caption_pool = ADULT_SUBTLE_SMILE
    
    # Select random caption from pool
    if caption_pool:
        return random.choice(caption_pool)
    
    # Fallback caption (should never reach here)
    return "Photo captured successfully! 📸"
