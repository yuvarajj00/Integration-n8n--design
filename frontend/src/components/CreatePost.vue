<template>
  <div class="publisher-wrapper" id="create-post">
    <div class="section-head">
      <span class="tag">DISPATCH PIPELINE</span>
      <h2>Create Post</h2>
    </div>
    <p class="section-sub">
      Upload creative assets to Cloudinary, draft your caption, and trigger n8n distribution to Meta Graph API.
    </p>

    <!-- Upload Card -->
    <div class="post-card">
      <div class="card-step-header">
        <span class="dnum">STEP 01</span>
        <span class="step-title">Media Asset (Cloudinary Upload)</span>
      </div>

      <!-- Dropzone when no image -->
      <div
        v-if="!imageUrl"
        class="dropzone"
        :class="{ 'is-dragging': isDragging, 'is-uploading': isUploading }"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <input
          ref="fileInputRef"
          type="file"
          accept="image/*"
          class="hidden-input"
          @change="handleFileChange"
        />

        <div v-if="!isUploading" class="dropzone-content">
          <div class="upload-icon-circle">
            <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <p class="dropzone-title mono">&gt; Click to browse or drag &amp; drop</p>
          <p class="dropzone-hint">PNG, JPG, WEBP, GIF (auto-converts to JPEG for Meta compliance)</p>
        </div>

        <div v-else class="uploading-state">
          <div class="spinner"></div>
          <p class="mono">&gt; Streaming to Cloudinary bucket...</p>
        </div>
      </div>

      <!-- Preview when uploaded -->
      <div v-else class="preview-box">
        <div class="preview-media">
          <img :src="imageUrl" alt="Upload preview" class="preview-img" />
        </div>
        <div class="preview-details">
          <div class="preview-tags">
            <span class="chip-status signal">● Cloudinary Secure URL</span>
            <span v-if="imageMeta.format" class="chip-info">{{ imageMeta.format.toUpperCase() }}</span>
            <span v-if="imageMeta.width" class="chip-info">{{ imageMeta.width }}×{{ imageMeta.height }}</span>
          </div>

          <div class="url-bar">
            <span class="url-label mono">URL:</span>
            <input type="text" readonly :value="imageUrl" class="url-field mono" />
            <button type="button" class="btn-copy mono" @click="copyUrl">
              {{ copied ? 'COPIED!' : 'COPY' }}
            </button>
          </div>
        </div>

        <button type="button" class="btn-clear mono" @click="removeImage" title="Remove Asset">
          ✕
        </button>
      </div>

      <div v-if="uploadError" class="alert-box error mono">
        <b>[ERR_UPLOAD]</b> {{ uploadError }}
      </div>
    </div>

    <!-- Caption Card -->
    <div class="post-card">
      <div class="card-step-header">
        <span class="dnum">STEP 02</span>
        <span class="step-title">Caption &amp; Copy</span>
      </div>

      <div class="input-shell">
        <textarea
          v-model="caption"
          placeholder="// Type your caption here... supports hashtags, emojis, and copy."
          rows="4"
          class="caption-area"
        ></textarea>
        <div class="char-bar mono">
          <span>LEN: {{ caption.length }} chars</span>
        </div>
      </div>
    </div>

    <!-- Platform Selection Card -->
    <div class="post-card">
      <div class="card-step-header">
        <span class="dnum">STEP 03</span>
        <span class="step-title">Target Platform</span>
      </div>

      <div class="platform-grid">
        <label class="platform-pill" :class="{ selected: platform === 'instagram' }">
          <input
            type="radio"
            name="platform"
            value="instagram"
            v-model="platform"
            class="hidden-radio"
          />
          <div class="pill-indicator"></div>
          <div class="pill-content">
            <div class="pill-header">
              <span class="pill-name mono">Instagram</span>
              <span class="kind-tag ig mono">IG_FEED</span>
            </div>
            <p class="pill-desc">Meta Graph API Container → Media Publish</p>
          </div>
        </label>

        <label class="platform-pill" :class="{ selected: platform === 'facebook' }">
          <input
            type="radio"
            name="platform"
            value="facebook"
            v-model="platform"
            class="hidden-radio"
          />
          <div class="pill-indicator"></div>
          <div class="pill-content">
            <div class="pill-header">
              <span class="pill-name mono">Facebook</span>
              <span class="kind-tag fb mono">FB_PAGE</span>
            </div>
            <p class="pill-desc">Page Feed Photos Endpoint</p>
          </div>
        </label>

        <label class="platform-pill" :class="{ selected: platform === 'both' }">
          <input
            type="radio"
            name="platform"
            value="both"
            v-model="platform"
            class="hidden-radio"
          />
          <div class="pill-indicator"></div>
          <div class="pill-content">
            <div class="pill-header">
              <span class="pill-name mono">Both</span>
              <span class="kind-tag both mono">DUAL_DISPATCH</span>
            </div>
            <p class="pill-desc">Concurrent publish across IG &amp; FB</p>
          </div>
        </label>
      </div>
    </div>

    <!-- Notifications -->
    <div v-if="publishSuccessMessage" class="alert-box success mono">
      <div class="alert-title">&gt; [OK_200] DISPATCHED TO N8N WEBHOOK</div>
      <p>{{ publishSuccessMessage }}</p>
    </div>

    <div v-if="publishErrorMessage" class="alert-box error mono">
      <div class="alert-title">&gt; [ERR_DISPATCH_FAILED]</div>
      <p>{{ publishErrorMessage }}</p>
    </div>

    <!-- Submit Action -->
    <div class="action-row">
      <button
        type="button"
        class="btn-dispatch mono"
        :disabled="!isFormValid || isPublishing"
        @click="handleSendNow"
      >
        <span v-if="isPublishing" class="btn-spinner"></span>
        <span v-if="isPublishing">DISPATCHING VIA N8N...</span>
        <span v-else>&gt; SEND NOW [ENTER]</span>
      </button>

      <div class="pipeline-summary mono">
        <span>TARGET: <b class="highlight">{{ platform.toUpperCase() }}</b></span>
        <span>•</span>
        <span>STATUS: <b>{{ isFormValid ? 'PAYLOAD READY' : 'AWAITING INPUT' }}</b></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const fileInputRef = ref(null)
const isDragging = ref(false)
const isUploading = ref(false)
const isPublishing = ref(false)
const copied = ref(false)

const imageUrl = ref('')
const imageMeta = ref({ format: '', width: null, height: null })
const caption = ref('')
const platform = ref('instagram')

const uploadError = ref('')
const publishSuccessMessage = ref('')
const publishErrorMessage = ref('')

const isFormValid = computed(() => {
  return imageUrl.value.trim() !== '' && caption.value.trim() !== '' && platform.value !== ''
})

function triggerFileInput() {
  if (fileInputRef.value) {
    fileInputRef.value.click()
  }
}

function handleFileChange(event) {
  const file = event.target.files?.[0]
  if (file) {
    uploadFile(file)
  }
}

function handleDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer.files?.[0]
  if (file) {
    uploadFile(file)
  }
}

async function uploadFile(file) {
  if (!file.type.startsWith('image/')) {
    uploadError.value = 'Only image assets permitted (PNG, JPG, WEBP, etc.)'
    return
  }

  uploadError.value = ''
  isUploading.value = true

  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch('/api/uploads/image', {
      method: 'POST',
      body: formData,
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Upload failed')
    }

    imageUrl.value = data.image.url
    imageMeta.value = {
      format: data.image.format,
      width: data.image.width,
      height: data.image.height,
    }
  } catch (err) {
    uploadError.value = err.message || 'Failed to stream image to Cloudinary'
  } finally {
    isUploading.value = false
  }
}

function removeImage() {
  imageUrl.value = ''
  imageMeta.value = { format: '', width: null, height: null }
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

async function copyUrl() {
  if (!imageUrl.value) return
  await navigator.clipboard.writeText(imageUrl.value)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}

async function handleSendNow() {
  if (!isFormValid.value) return

  publishSuccessMessage.value = ''
  publishErrorMessage.value = ''
  isPublishing.value = true

  try {
    let finalImageUrl = imageUrl.value.trim()
    if (platform.value === 'instagram' || platform.value === 'both') {
      // Instagram strictly requires JPEG; convert .png or extensionless URLs to .jpg on Cloudinary
      if (/\.png(?=[\?#]|$)/i.test(finalImageUrl)) {
        finalImageUrl = finalImageUrl.replace(/\.png(?=[\?#]|$)/i, '.jpg')
      } else if (!/\.(jpe?g|png|webp)(?=[\?#]|$)/i.test(finalImageUrl)) {
        finalImageUrl = finalImageUrl.replace(/(?=[?#]|$)/, '.jpg')
      }
    }

    const payload = {
      imageUrl: finalImageUrl,
      caption: caption.value,
      platform: platform.value,
    }

    const response = await fetch('/api/social-posts/publish', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to dispatch to n8n webhook')
    }

    publishSuccessMessage.value =
      data.message || `Post forwarded to n8n webhook successfully! HTTP ${data.status_code}`
  } catch (err) {
    publishErrorMessage.value = err.message || 'Failed to publish post'
  } finally {
    isPublishing.value = false
  }
}
</script>

<style scoped>
.publisher-wrapper {
  max-width: 820px;
  margin: 0;
}

.section-head {
  display: flex;
  align-items: baseline;
  gap: 14px;
  margin-bottom: 8px;
}

.section-head .tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--amber);
  border: 1px solid var(--amber-dim);
  padding: 2px 9px;
  border-radius: 20px;
}

.section-head h2 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 22px;
  margin: 0;
  font-weight: 600;
  color: var(--text);
}

.section-sub {
  color: var(--muted);
  font-size: 14.5px;
  max-width: 680px;
  margin: 0 0 30px;
}

/* Cards */
.post-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 20px 24px;
  margin-bottom: 18px;
  transition: border-color 0.15s;
}

.post-card:hover {
  border-color: rgba(56, 230, 181, 0.3);
}

.card-step-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.dnum {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--signal);
  border: 1px solid var(--signal-dim);
  border-radius: 5px;
  padding: 2px 7px;
  flex-shrink: 0;
  font-weight: 600;
}

.step-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

/* Dropzone */
.dropzone {
  border: 1px dashed var(--line);
  border-radius: 8px;
  padding: 32px 20px;
  text-align: center;
  cursor: pointer;
  background: var(--panel2);
  transition: all 0.2s ease;
}

.dropzone:hover,
.dropzone.is-dragging {
  border-color: var(--signal);
  background: rgba(56, 230, 181, 0.04);
}

.dropzone.is-uploading {
  cursor: wait;
  border-color: var(--amber);
}

.hidden-input {
  display: none;
}

.upload-icon-circle {
  width: 44px;
  height: 44px;
  background: rgba(56, 230, 181, 0.1);
  border: 1px solid var(--signal-dim);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}

.upload-icon {
  width: 22px;
  height: 22px;
  color: var(--signal);
}

.dropzone-title {
  font-size: 13.5px;
  color: var(--signal);
  margin: 0 0 4px;
  font-weight: 500;
}

.dropzone-hint {
  font-size: 12px;
  color: var(--muted2);
  margin: 0;
}

.uploading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--amber);
  font-size: 13px;
}

.spinner {
  width: 26px;
  height: 26px;
  border: 2px solid rgba(255, 180, 84, 0.2);
  border-top-color: var(--amber);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Preview Box */
.preview-box {
  display: flex;
  gap: 18px;
  background: var(--panel2);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 14px;
  align-items: center;
  position: relative;
}

.preview-media {
  flex-shrink: 0;
}

.preview-img {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid var(--line);
}

.preview-details {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chip-status {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  border-radius: 4px;
  padding: 2px 7px;
  font-weight: 600;
}

.chip-status.signal {
  background: rgba(56, 230, 181, 0.1);
  color: var(--signal);
  border: 1px solid var(--signal-dim);
}

.chip-info {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  background: var(--panel);
  border: 1px solid var(--line);
  color: var(--muted);
  border-radius: 4px;
  padding: 2px 7px;
}

.url-bar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.url-label {
  font-size: 11.5px;
  color: var(--muted2);
}

.url-field {
  flex: 1;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 5px;
  padding: 5px 8px;
  color: var(--muted);
  font-size: 12px;
  text-overflow: ellipsis;
  overflow: hidden;
  outline: none;
}

.btn-copy {
  background: var(--panel);
  border: 1px solid var(--line);
  color: var(--signal);
  border-radius: 5px;
  padding: 5px 10px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-copy:hover {
  background: var(--signal);
  color: #04140f;
  border-color: var(--signal);
}

.btn-clear {
  position: absolute;
  top: 8px;
  right: 8px;
  background: transparent;
  border: 1px solid var(--line);
  color: var(--muted2);
  border-radius: 4px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.15s;
}

.btn-clear:hover {
  color: #ff5c5c;
  border-color: #ff5c5c;
}

/* Caption Area */
.input-shell {
  display: flex;
  flex-direction: column;
}

.caption-area {
  width: 100%;
  background: var(--panel2);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 12px 14px;
  color: var(--text);
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 14px;
  resize: vertical;
  outline: none;
  transition: border-color 0.15s;
}

.caption-area:focus {
  border-color: var(--signal);
  box-shadow: 0 0 0 2px rgba(56, 230, 181, 0.12);
}

.char-bar {
  display: flex;
  justify-content: flex-end;
  font-size: 11px;
  color: var(--muted2);
  margin-top: 6px;
}

/* Platform Selectors */
.platform-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.platform-pill {
  background: var(--panel2);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 14px 16px;
  cursor: pointer;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  transition: all 0.15s;
}

.platform-pill:hover {
  border-color: var(--muted2);
}

.platform-pill.selected {
  border-color: var(--signal);
  background: rgba(56, 230, 181, 0.05);
}

.hidden-radio {
  display: none;
}

.pill-indicator {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid var(--line);
  margin-top: 3px;
  flex-shrink: 0;
  transition: all 0.15s;
}

.platform-pill.selected .pill-indicator {
  border-color: var(--signal);
  background: var(--signal);
  box-shadow: 0 0 8px rgba(56, 230, 181, 0.5);
}

.pill-content {
  flex: 1;
}

.pill-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.pill-name {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text);
}

.kind-tag {
  font-size: 9.5px;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 700;
}

.kind-tag.ig {
  background: rgba(255, 180, 84, 0.15);
  color: var(--amber);
  border: 1px solid var(--amber-dim);
}

.kind-tag.fb {
  background: rgba(66, 103, 178, 0.2);
  color: #79a6fe;
  border: 1px solid #2b4987;
}

.kind-tag.both {
  background: rgba(56, 230, 181, 0.15);
  color: var(--signal);
  border: 1px solid var(--signal-dim);
}

.pill-desc {
  font-size: 12px;
  color: var(--muted);
  margin: 0;
  line-height: 1.4;
}

/* Alerts */
.alert-box {
  padding: 14px 18px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 12.5px;
}

.alert-box.success {
  background: rgba(56, 230, 181, 0.08);
  border-left: 3px solid var(--signal);
  color: var(--signal);
}

.alert-box.error {
  background: rgba(255, 92, 92, 0.08);
  border-left: 3px solid #ff5c5c;
  color: #ff8c8c;
}

.alert-title {
  font-weight: 700;
  margin-bottom: 3px;
}

.alert-box p {
  margin: 0;
  color: var(--text);
}

/* Submit Action Row */
.action-row {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-dispatch {
  width: 100%;
  background: var(--signal);
  color: #04140f;
  border: none;
  border-radius: var(--radius);
  padding: 14px 20px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.15s ease;
  letter-spacing: 0.5px;
}

.btn-dispatch:hover:not(:disabled) {
  box-shadow: 0 0 20px rgba(56, 230, 181, 0.4);
  transform: translateY(-1px);
}

.btn-dispatch:disabled {
  background: var(--panel2);
  color: var(--muted2);
  border: 1px solid var(--line);
  cursor: not-allowed;
  box-shadow: none;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(4, 20, 15, 0.3);
  border-top-color: #04140f;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.pipeline-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11.5px;
  color: var(--muted2);
  padding: 0 4px;
}

.pipeline-summary .highlight {
  color: var(--signal);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 640px) {
  .platform-grid {
    grid-template-columns: 1fr;
  }
}
</style>
