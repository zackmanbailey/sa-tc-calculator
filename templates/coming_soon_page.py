"""
Generic 'Coming Soon' placeholder page.
Used for sidebar links that don't yet have full implementations.
The handler passes `page_title` and `page_icon` via string replacement.
"""

COMING_SOON_PAGE_HTML = r"""
<style>
.coming-soon-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
    text-align: center;
    padding: 2rem;
}
.coming-soon-icon {
    font-size: 4rem;
    margin-bottom: 1.5rem;
    opacity: 0.7;
}
.coming-soon-title {
    font-size: 2rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 0.75rem;
}
.coming-soon-badge {
    display: inline-block;
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: #000;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 1.5rem;
}
.coming-soon-desc {
    font-size: 1.05rem;
    color: #94a3b8;
    max-width: 500px;
    line-height: 1.6;
    margin-bottom: 2rem;
}
.coming-soon-back {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(99,102,241,0.15);
    color: #818cf8;
    border: 1px solid rgba(99,102,241,0.3);
    padding: 0.6rem 1.25rem;
    border-radius: 0.5rem;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
}
.coming-soon-back:hover {
    background: rgba(99,102,241,0.25);
    color: #a5b4fc;
}
</style>

<div class="coming-soon-container">
    <div class="coming-soon-icon">{{PAGE_ICON}}</div>
    <div class="coming-soon-title">{{PAGE_TITLE}}</div>
    <span class="coming-soon-badge">Coming Soon</span>
    <div class="coming-soon-desc">
        This module is under active development and will be available in an upcoming release.
        Check back soon for updates.
    </div>
    <a href="/" class="coming-soon-back">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        Back to Dashboard
    </a>
</div>
"""
