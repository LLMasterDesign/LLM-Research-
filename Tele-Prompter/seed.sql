-- Glyph-It Forge Database Seed
-- Creates tables and populates with starter data

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    credits INTEGER DEFAULT 100,
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_premium BOOLEAN DEFAULT FALSE,
    preferences JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_created_at ON users(created_at);

-- ============================================
-- GLYPHS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS glyphs (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    category VARCHAR(100),
    tags TEXT[],
    is_public BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    parent_glyph_ids INTEGER[],
    metadata JSONB DEFAULT '{}'::jsonb,
    FOREIGN KEY (user_id) REFERENCES users(telegram_id) ON DELETE CASCADE,
    UNIQUE(user_id, name)
);

CREATE INDEX idx_glyphs_user_id ON glyphs(user_id);
CREATE INDEX idx_glyphs_token_count ON glyphs(token_count);
CREATE INDEX idx_glyphs_is_public ON glyphs(is_public);
CREATE INDEX idx_glyphs_category ON glyphs(category);
CREATE INDEX idx_glyphs_tags ON glyphs USING GIN(tags);

-- ============================================
-- USAGE LOG TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS usage_log (
    id SERIAL PRIMARY KEY,
    glyph_id INTEGER NOT NULL,
    user_id BIGINT NOT NULL,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context VARCHAR(255),
    FOREIGN KEY (glyph_id) REFERENCES glyphs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(telegram_id) ON DELETE CASCADE
);

CREATE INDEX idx_usage_log_glyph_id ON usage_log(glyph_id);
CREATE INDEX idx_usage_log_user_id ON usage_log(user_id);
CREATE INDEX idx_usage_log_used_at ON usage_log(used_at);

-- ============================================
-- ACHIEVEMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    achievement_type VARCHAR(100) NOT NULL,
    achievement_name VARCHAR(255) NOT NULL,
    points INTEGER DEFAULT 0,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(telegram_id) ON DELETE CASCADE,
    UNIQUE(user_id, achievement_type)
);

CREATE INDEX idx_achievements_user_id ON achievements(user_id);
CREATE INDEX idx_achievements_type ON achievements(achievement_type);

-- ============================================
-- MARKETPLACE TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS marketplace_items (
    id SERIAL PRIMARY KEY,
    glyph_id INTEGER NOT NULL,
    seller_id BIGINT NOT NULL,
    price INTEGER NOT NULL,
    description TEXT,
    rating DECIMAL(3,2) DEFAULT 0.00,
    downloads INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (glyph_id) REFERENCES glyphs(id) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES users(telegram_id) ON DELETE CASCADE
);

CREATE INDEX idx_marketplace_seller ON marketplace_items(seller_id);
CREATE INDEX idx_marketplace_active ON marketplace_items(is_active);

-- ============================================
-- TRANSACTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount INTEGER NOT NULL,
    description TEXT,
    reference_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(telegram_id) ON DELETE CASCADE
);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);

-- ============================================
-- N8N DATABASE (separate schema)
-- ============================================
CREATE DATABASE n8n;

-- ============================================
-- SEED DATA: System User for Featured Glyphs
-- ============================================
INSERT INTO users (telegram_id, username, first_name, credits, level, is_premium)
VALUES (0, 'system', 'Glyph Forge', 999999, 100, TRUE)
ON CONFLICT (telegram_id) DO NOTHING;

-- ============================================
-- SEED DATA: Featured Starter Glyphs
-- ============================================
INSERT INTO glyphs (user_id, name, text, token_count, category, tags, is_public, is_featured, metadata) VALUES
(0, 'code_wizard', 'You are an expert programmer who explains code with clarity and technical precision', 13, 'programming', ARRAY['coding', 'technical', 'expert'], TRUE, TRUE, '{"seed": "wisdom", "intensity": "medium", "style": "technical"}'::jsonb),

(0, 'creative_muse', 'Channel creative inspiration to generate unique artistic ideas with poetic flair', 11, 'creative', ARRAY['creative', 'artistic', 'poetic'], TRUE, TRUE, '{"seed": "power", "intensity": "intense", "style": "poetic"}'::jsonb),

(0, 'debug_master', 'Analyze code systematically to identify bugs and provide clear fix recommendations', 11, 'programming', ARRAY['debugging', 'technical', 'problem-solving'], TRUE, TRUE, '{"seed": "wisdom", "intensity": "subtle", "style": "technical"}'::jsonb),

(0, 'story_weaver', 'Craft engaging narratives with rich characters and compelling plot developments', 10, 'creative', ARRAY['writing', 'storytelling', 'creative'], TRUE, TRUE, '{"seed": "power", "intensity": "medium", "style": "poetic"}'::jsonb),

(0, 'data_sage', 'Interpret data patterns to extract meaningful insights and actionable recommendations', 10, 'analysis', ARRAY['data', 'analysis', 'insights'], TRUE, TRUE, '{"seed": "wisdom", "intensity": "intense", "style": "technical"}'::jsonb),

(0, 'quick_summarizer', 'Distill complex information into clear concise summaries preserving key points', 10, 'productivity', ARRAY['summary', 'productivity', 'efficiency'], TRUE, TRUE, '{"seed": "balance", "intensity": "subtle", "style": "professional"}'::jsonb),

(0, 'brainstorm_buddy', 'Generate diverse creative solutions through lateral thinking and innovative approaches', 10, 'creative', ARRAY['brainstorming', 'innovation', 'creativity'], TRUE, TRUE, '{"seed": "chaos", "intensity": "intense", "style": "poetic"}'::jsonb),

(0, 'learn_coach', 'Break down complex topics into digestible explanations with clear examples', 10, 'education', ARRAY['learning', 'teaching', 'education'], TRUE, TRUE, '{"seed": "wisdom", "intensity": "subtle", "style": "professional"}'::jsonb),

(0, 'research_assistant', 'Gather analyze and synthesize information from multiple sources for comprehensive insights', 11, 'research', ARRAY['research', 'analysis', 'academic'], TRUE, TRUE, '{"seed": "wisdom", "intensity": "medium", "style": "technical"}'::jsonb),

(0, 'motivator', 'Inspire action with encouraging words that blend wisdom and empowering energy', 11, 'personal', ARRAY['motivation', 'inspiration', 'personal-growth'], TRUE, TRUE, '{"seed": "power", "intensity": "intense", "style": "poetic"}'::jsonb),

(0, 'code_reviewer', 'Evaluate code for quality best practices and suggest improvements with examples', 11, 'programming', ARRAY['code-review', 'quality', 'best-practices'], TRUE, TRUE, '{"seed": "balance", "intensity": "medium", "style": "technical"}'::jsonb),

(0, 'meeting_notes', 'Capture key discussion points decisions and action items in structured format', 11, 'productivity', ARRAY['meetings', 'notes', 'productivity'], TRUE, TRUE, '{"seed": "balance", "intensity": "subtle", "style": "professional"}'::jsonb),

(0, 'seo_optimizer', 'Enhance content for search visibility while maintaining natural engaging readability', 10, 'marketing', ARRAY['seo', 'marketing', 'content'], TRUE, TRUE, '{"seed": "power", "intensity": "medium", "style": "professional"}'::jsonb),

(0, 'philosophical_guide', 'Explore deep questions through multiple philosophical lenses with balanced perspectives', 10, 'philosophy', ARRAY['philosophy', 'thinking', 'wisdom'], TRUE, TRUE, '{"seed": "wisdom", "intensity": "intense", "style": "mystical"}'::jsonb),

(0, 'perfect_27', 'You embody efficiency crafting precise impactful responses within exact token constraints always', 27, 'meta', ARRAY['perfect', '27-tokens', 'efficiency'], TRUE, TRUE, '{"seed": "balance", "intensity": "medium", "style": "technical", "is_perfect_27": true}'::jsonb)

ON CONFLICT (user_id, name) DO NOTHING;

-- Update usage counts for featured glyphs
UPDATE glyphs SET usage_count = floor(random() * 1000 + 100) WHERE is_featured = TRUE;

-- ============================================
-- SEED DATA: Achievement Definitions
-- ============================================
CREATE TABLE IF NOT EXISTS achievement_definitions (
    achievement_type VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    points INTEGER DEFAULT 0,
    icon VARCHAR(10)
);

INSERT INTO achievement_definitions (achievement_type, name, description, points, icon) VALUES
('first_glyph', 'Seed Planted', 'Create your first glyph', 10, '🌱'),
('perfect_27', 'Perfect Shot', 'Create a glyph with exactly 27 tokens', 50, '🎯'),
('ten_glyphs', 'Librarian', 'Create 10 glyphs', 30, '📚'),
('fifty_glyphs', 'Collector', 'Create 50 glyphs', 100, '📖'),
('hundred_uses', 'Power User', 'Use glyphs 100 times', 100, '🔥'),
('mixer', 'Alchemist', 'Mix 5 glyphs together', 40, '🧪'),
('sharer', 'Community Champion', 'Share 5 glyphs publicly', 60, '🤝'),
('streak_7', 'Dedicated', 'Use bot 7 days in a row', 50, '⭐'),
('marketplace_seller', 'Entrepreneur', 'Sell your first glyph', 75, '💰'),
('the_27_club', 'Club Member', 'Create 5 perfect 27-token glyphs', 200, '👑')
ON CONFLICT (achievement_type) DO NOTHING;

-- ============================================
-- VIEWS FOR ANALYTICS
-- ============================================

-- Most popular glyphs
CREATE OR REPLACE VIEW v_popular_glyphs AS
SELECT 
    g.id,
    g.name,
    g.text,
    g.token_count,
    g.category,
    g.usage_count,
    g.is_public,
    u.username as creator,
    COUNT(DISTINCT ul.user_id) as unique_users
FROM glyphs g
LEFT JOIN users u ON g.user_id = u.telegram_id
LEFT JOIN usage_log ul ON g.id = ul.glyph_id
WHERE g.is_public = TRUE
GROUP BY g.id, u.username
ORDER BY g.usage_count DESC, unique_users DESC;

-- User statistics
CREATE OR REPLACE VIEW v_user_stats AS
SELECT 
    u.telegram_id,
    u.username,
    u.level,
    u.xp,
    u.credits,
    COUNT(DISTINCT g.id) as total_glyphs,
    COUNT(DISTINCT CASE WHEN g.token_count = 27 THEN g.id END) as perfect_27_glyphs,
    SUM(g.usage_count) as total_uses,
    COUNT(DISTINCT a.achievement_type) as achievements_unlocked,
    SUM(a.points) as total_achievement_points
FROM users u
LEFT JOIN glyphs g ON u.telegram_id = g.user_id
LEFT JOIN achievements a ON u.telegram_id = a.user_id
GROUP BY u.telegram_id;

-- Daily activity
CREATE OR REPLACE VIEW v_daily_activity AS
SELECT 
    DATE(used_at) as activity_date,
    COUNT(*) as total_uses,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT glyph_id) as unique_glyphs
FROM usage_log
GROUP BY DATE(used_at)
ORDER BY activity_date DESC;

-- Category breakdown
CREATE OR REPLACE VIEW v_category_stats AS
SELECT 
    category,
    COUNT(*) as glyph_count,
    SUM(usage_count) as total_uses,
    AVG(token_count)::DECIMAL(5,2) as avg_tokens,
    COUNT(DISTINCT user_id) as creators
FROM glyphs
WHERE category IS NOT NULL
GROUP BY category
ORDER BY total_uses DESC;

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function to update glyph usage
CREATE OR REPLACE FUNCTION increment_glyph_usage(p_glyph_id INTEGER, p_user_id BIGINT)
RETURNS VOID AS $$
BEGIN
    -- Increment usage count
    UPDATE glyphs SET usage_count = usage_count + 1 WHERE id = p_glyph_id;
    
    -- Log the usage
    INSERT INTO usage_log (glyph_id, user_id) VALUES (p_glyph_id, p_user_id);
    
    -- Update user last active
    UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE telegram_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Function to award achievement
CREATE OR REPLACE FUNCTION award_achievement(p_user_id BIGINT, p_achievement_type VARCHAR(100))
RETURNS BOOLEAN AS $$
DECLARE
    v_points INTEGER;
    v_name VARCHAR(255);
BEGIN
    -- Get achievement details
    SELECT points, name INTO v_points, v_name
    FROM achievement_definitions
    WHERE achievement_type = p_achievement_type;
    
    -- Insert achievement (if not already unlocked)
    INSERT INTO achievements (user_id, achievement_type, achievement_name, points)
    VALUES (p_user_id, p_achievement_type, v_name, v_points)
    ON CONFLICT (user_id, achievement_type) DO NOTHING;
    
    -- Add XP to user
    UPDATE users SET xp = xp + v_points WHERE telegram_id = p_user_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate user level
CREATE OR REPLACE FUNCTION calculate_user_level(p_xp INTEGER)
RETURNS INTEGER AS $$
BEGIN
    -- Level formula: level = floor(sqrt(xp / 100)) + 1
    RETURN floor(sqrt(p_xp / 100.0)) + 1;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update user level
CREATE OR REPLACE FUNCTION update_user_level()
RETURNS TRIGGER AS $$
BEGIN
    NEW.level := calculate_user_level(NEW.xp);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_user_level
BEFORE UPDATE OF xp ON users
FOR EACH ROW
EXECUTE FUNCTION update_user_level();

-- ============================================
-- GRANTS (for bot user)
-- ============================================
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO glyph;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO glyph;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO glyph;

-- ============================================
-- SAMPLE TEST USER (for testing)
-- ============================================
INSERT INTO users (telegram_id, username, first_name, credits)
VALUES (123456789, 'test_user', 'Test User', 100)
ON CONFLICT (telegram_id) DO NOTHING;

-- ============================================
-- COMPLETION MESSAGE
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '✨ Glyph-It Forge Database Initialized Successfully!';
    RAISE NOTICE '📊 Seeded with % featured glyphs', (SELECT COUNT(*) FROM glyphs WHERE is_featured = TRUE);
    RAISE NOTICE '🏆 Added % achievement types', (SELECT COUNT(*) FROM achievement_definitions);
    RAISE NOTICE '🚀 Ready to forge glyphs!';
END $$;
