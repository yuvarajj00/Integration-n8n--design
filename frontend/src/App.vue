<script setup>
import CreatePost from './components/CreatePost.vue'
</script>

<template>
  <div class="shell">
    <nav class="toc">
      <div class="brand">velorq<span class="dim">.publisher</span></div>
      <div class="grp-label">Modules</div>
      <a href="#create-post" class="active">01 · Create & Publish</a>
      <a href="#pipeline-status">02 · Pipeline Specs</a>
      <div class="grp-label">Integration</div>
      <a href="http://localhost:8000/docs" target="_blank" rel="noopener">FastAPI Swagger ↗</a>
      <a href="http://localhost:5678" target="_blank" rel="noopener">n8n Webhook UI ↗</a>
      <a href="https://cloudinary.com/console" target="_blank" rel="noopener">Cloudinary Console ↗</a>
    </nav>

    <main>
      <header class="hero">
        <div class="term">
          <span class="l"><b>&gt;</b> whoami</span>
          <span class="l">velorq.media-publisher</span>
          <span class="l"><b>&gt;</b> pipeline --source=cloudinary --sink=n8n --targets=instagram,facebook</span>
          <span class="l">&gt; PIPELINE READY<span class="cursor"></span></span>
        </div>

        <h1 class="title">Media Publisher <span class="accent">Console</span></h1>
        <p class="lede">Upload media directly to Cloudinary, configure platform targets, and dispatch posts across Meta Graph API via automated n8n workflows.</p>

        <div class="stats">
          <div class="stat"><div class="n">Cloudinary</div><div class="l">cbl5jblk (JPG Auto-Transcode)</div></div>
          <div class="stat"><div class="n">FastAPI</div><div class="l">Port 8000 · Validated</div></div>
          <div class="stat"><div class="n">n8n Engine</div><div class="l">social-publisher webhook</div></div>
          <div class="stat"><div class="n">Meta APIs</div><div class="l">Instagram &amp; Facebook</div></div>
        </div>
      </header>

      <div class="content-area">
        <CreatePost />
      </div>

      <footer>
        velorq.media-publisher — v1.0 · FastAPI + Cloudinary + n8n + Meta API
      </footer>
    </main>
  </div>
</template>

<style scoped>
.shell {
  display: flex;
  max-width: 1360px;
  margin: 0 auto;
  width: 100%;
}

nav.toc {
  position: sticky;
  top: 0;
  align-self: flex-start;
  height: 100vh;
  width: 240px;
  flex-shrink: 0;
  padding: 28px 18px;
  overflow-y: auto;
  border-right: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

nav.toc .brand {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 700;
  color: var(--signal);
  margin-bottom: 22px;
  letter-spacing: 0.5px;
}

nav.toc .brand .dim {
  color: var(--muted2);
}

nav.toc a {
  display: block;
  font-size: 13px;
  color: var(--muted);
  text-decoration: none;
  padding: 7px 10px;
  border-radius: 7px;
  font-family: 'JetBrains Mono', monospace;
  transition: background 0.15s, color 0.15s;
}

nav.toc a:hover,
nav.toc a.active {
  background: var(--panel2);
  color: var(--text);
}

nav.toc .grp-label {
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: var(--muted2);
  margin: 16px 10px 4px;
  font-family: 'JetBrains Mono', monospace;
}

@media (max-width: 920px) {
  nav.toc {
    display: none;
  }
}

main {
  flex: 1;
  min-width: 0;
  padding: 0 0 60px;
}

.hero {
  padding: 48px 48px 36px;
  border-bottom: 1px solid var(--line);
  position: relative;
  overflow: hidden;
}

.term {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  color: var(--signal-dim);
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px 18px;
  max-width: 620px;
  margin-bottom: 24px;
}

.term .l {
  color: var(--muted);
  display: block;
  margin-bottom: 4px;
}

.term .l b {
  color: var(--signal);
  font-weight: 500;
}

.term .cursor {
  display: inline-block;
  width: 7px;
  height: 14px;
  background: var(--signal);
  animation: blink 1.1s steps(1) infinite;
  vertical-align: middle;
  margin-left: 4px;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

h1.title {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: clamp(26px, 3.5vw, 40px);
  margin: 0 0 12px;
  letter-spacing: -0.5px;
  color: var(--text);
}

h1.title .accent {
  color: var(--signal);
}

.lede {
  color: var(--muted);
  font-size: 15px;
  max-width: 680px;
  margin: 0 0 26px;
  line-height: 1.6;
}

.stats {
  display: flex;
  gap: 0;
  flex-wrap: wrap;
  border-top: 1px solid var(--line);
  border-left: 1px solid var(--line);
  max-width: 820px;
}

.stat {
  flex: 1;
  min-width: 180px;
  padding: 14px 18px;
  border-right: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  background: var(--panel);
}

.stat .n {
  font-family: 'JetBrains Mono', monospace;
  font-size: 16px;
  color: var(--signal);
  font-weight: 600;
}

.stat .l {
  font-size: 12px;
  color: var(--muted);
  margin-top: 2px;
}

.content-area {
  padding: 36px 48px;
}

footer {
  padding: 36px 48px;
  color: var(--muted2);
  font-size: 12.5px;
  font-family: 'JetBrains Mono', monospace;
  border-top: 1px solid var(--line);
}

@media (max-width: 640px) {
  .hero, .content-area, footer {
    padding: 24px 20px;
  }
}
</style>
