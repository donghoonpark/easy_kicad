<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  NAlert,
  NButton,
  NCard,
  NConfigProvider,
  NDrawer,
  NDrawerContent,
  NForm,
  NFormItem,
  NGrid,
  NGridItem,
  NInput,
  NInputNumber,
  NSpace,
  NSwitch,
  NTag,
  NThing,
  NTooltip,
  createDiscreteApi,
} from 'naive-ui'

import { appDescription, appName, appTagline } from '@/branding'
import ModelPreview from '@/components/ModelPreview.vue'
import PreviewCard from '@/components/PreviewCard.vue'
import type {
  AppSettings,
  ConnectionTestResponse,
  ImportResponse,
  InspectResponse,
} from '@/types/api'

const defaultSettings = (): AppSettings => ({
  library_root: '',
  library_name: appName,
  overwrite: false,
  project_relative_3d: false,
  symbol_format: 'v6',
  proxy_url: '',
  ca_bundle_path: '',
  ignore_ssl_verification: false,
  request_timeout_seconds: 20,
})

const settings = ref<AppSettings>(defaultSettings())
const lcscId = ref('C2040')
const preview = ref<InspectResponse | null>(null)
const importResult = ref<ImportResponse | null>(null)
const connectionResult = ref<ConnectionTestResponse | null>(null)
const loading = ref(false)
const importing = ref(false)
const saving = ref(false)
const drawerOpen = ref(false)
const { message } = createDiscreteApi(['message'])

const themeOverrides = {
  common: {
    primaryColor: '#dd6b20',
    primaryColorHover: '#f97316',
    primaryColorPressed: '#c05621',
    borderRadius: '16px',
  },
}

const wrlUrl = computed(() => preview.value?.model3d.wrlUrl ?? null)

const fetchJson = async <T>(url: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...init,
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(payload.detail ?? 'Request failed')
  }
  return (await response.json()) as T
}

const loadSettings = async () => {
  settings.value = await fetchJson<AppSettings>('/api/settings')
}

const saveSettings = async () => {
  saving.value = true
  try {
    settings.value = await fetchJson<AppSettings>('/api/settings', {
      method: 'PUT',
      body: JSON.stringify(settings.value),
    })
    message.success('Settings saved')
  } finally {
    saving.value = false
  }
}

const inspectPart = async () => {
  if (!lcscId.value.trim()) {
    message.warning('Enter an LCSC number first')
    return
  }

  loading.value = true
  importResult.value = null
  try {
    preview.value = await fetchJson<InspectResponse>('/api/parts/inspect', {
      method: 'POST',
      body: JSON.stringify({ lcscId: lcscId.value.trim().toUpperCase() }),
    })
    message.success(`Loaded ${preview.value.part.name}`)
  } catch (error) {
    preview.value = null
    message.error((error as Error).message)
  } finally {
    loading.value = false
  }
}

const importPart = async () => {
  if (!preview.value) {
    message.warning('Inspect a part before importing it')
    return
  }

  importing.value = true
  try {
    await saveSettings()
    importResult.value = await fetchJson<ImportResponse>('/api/parts/import', {
      method: 'POST',
      body: JSON.stringify({ lcscId: preview.value.part.lcscId }),
    })
    message.success('Import completed')
  } catch (error) {
    message.error((error as Error).message)
  } finally {
    importing.value = false
  }
}

const testConnection = async () => {
  try {
    connectionResult.value = await fetchJson<ConnectionTestResponse>(
      '/api/settings/test-connection',
      {
        method: 'POST',
        body: JSON.stringify(settings.value),
      },
    )
    message.success(connectionResult.value.message)
  } catch (error) {
    connectionResult.value = {
      success: false,
      message: (error as Error).message,
    }
    message.error(connectionResult.value.message)
  }
}

onMounted(async () => {
  try {
    await loadSettings()
  } catch (error) {
    message.error((error as Error).message)
  }
})
</script>

<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <div class="app-shell">
      <div class="app-shell__backdrop" />
      <main class="app-shell__content">
          <section class="hero-panel">
            <div class="hero-panel__copy">
              <span class="eyebrow">{{ appTagline }}</span>
              <h1>{{ appName }}</h1>
              <p>{{ appDescription }}</p>
            </div>
            <div class="hero-panel__actions">
              <n-tooltip trigger="hover">
                <template #trigger>
                  <n-button
                    class="settings-trigger"
                    circle
                    size="large"
                    aria-label="Open settings"
                    @click="drawerOpen = true"
                  >
                    <svg
                      viewBox="0 0 24 24"
                      width="20"
                      height="20"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <circle cx="12" cy="12" r="3.2" />
                      <path
                        d="M19.4 15a1 1 0 0 0 .2 1.1l.1.1a1.2 1.2 0 0 1 0 1.7l-1.2 1.2a1.2 1.2 0 0 1-1.7 0l-.1-.1a1 1 0 0 0-1.1-.2 1 1 0 0 0-.6.9V20a1.2 1.2 0 0 1-1.2 1.2h-1.7A1.2 1.2 0 0 1 9.9 20v-.2a1 1 0 0 0-.6-.9 1 1 0 0 0-1.1.2l-.1.1a1.2 1.2 0 0 1-1.7 0l-1.2-1.2a1.2 1.2 0 0 1 0-1.7l.1-.1a1 1 0 0 0 .2-1.1 1 1 0 0 0-.9-.6H4.3A1.2 1.2 0 0 1 3.1 13v-2A1.2 1.2 0 0 1 4.3 9.8h.2a1 1 0 0 0 .9-.6 1 1 0 0 0-.2-1.1l-.1-.1a1.2 1.2 0 0 1 0-1.7l1.2-1.2a1.2 1.2 0 0 1 1.7 0l.1.1a1 1 0 0 0 1.1.2 1 1 0 0 0 .6-.9V4.3A1.2 1.2 0 0 1 11 3.1h2a1.2 1.2 0 0 1 1.2 1.2v.2a1 1 0 0 0 .6.9 1 1 0 0 0 1.1-.2l.1-.1a1.2 1.2 0 0 1 1.7 0l1.2 1.2a1.2 1.2 0 0 1 0 1.7l-.1.1a1 1 0 0 0-.2 1.1 1 1 0 0 0 .9.6h.2A1.2 1.2 0 0 1 20.9 11v2a1.2 1.2 0 0 1-1.2 1.2h-.2a1 1 0 0 0-.9.8Z"
                      />
                    </svg>
                  </n-button>
                </template>
                Settings
              </n-tooltip>
              <n-button
                type="primary"
                size="large"
                :loading="importing"
                :disabled="!preview"
                @click="importPart"
              >
                Import to KiCad
              </n-button>
            </div>
          </section>

          <n-card class="control-card" embedded>
            <n-space justify="space-between" align="center" wrap>
              <div class="search-stack">
                <label class="field-label" for="lcsc-id">LCSC Number</label>
                <n-input
                  id="lcsc-id"
                  v-model:value="lcscId"
                  placeholder="C2040"
                  size="large"
                  clearable
                  @keyup.enter="inspectPart"
                />
              </div>
              <n-space>
                <n-button
                  size="large"
                  type="primary"
                  :loading="loading"
                  @click="inspectPart"
                >
                  Preview
                </n-button>
              </n-space>
            </n-space>

            <n-thing v-if="preview" class="part-summary">
              <template #header>
                {{ preview.part.name }}
              </template>
              <template #description>
                {{ preview.part.manufacturer || 'Unknown manufacturer' }}
              </template>
              <template #header-extra>
                <n-space>
                  <n-tag round type="warning">
                    {{ preview.part.lcscId }}
                  </n-tag>
                  <n-tag round>
                    {{ preview.part.package || 'No package' }}
                  </n-tag>
                </n-space>
              </template>
            </n-thing>
          </n-card>

          <n-grid cols="1 s:1 m:3" responsive="screen" x-gap="20" y-gap="20">
            <n-grid-item>
              <preview-card title="Symbol" subtitle="KiCad-ready SVG preview">
                <div
                  v-if="preview"
                  class="svg-panel"
                  v-html="preview.symbolSvg"
                />
                <div v-else class="empty-state">Search for a part to load its symbol.</div>
              </preview-card>
            </n-grid-item>

            <n-grid-item>
              <preview-card title="Footprint" subtitle="Copper, silkscreen, and drills">
                <div
                  v-if="preview"
                  class="svg-panel"
                  v-html="preview.footprintSvg"
                />
                <div v-else class="empty-state">Footprint preview will appear here.</div>
              </preview-card>
            </n-grid-item>

            <n-grid-item>
              <preview-card title="3D Model" subtitle="Interactive WRL preview">
                <template #header-extra>
                  <n-tag v-if="preview?.model3d.stepAvailable" round size="small">
                    STEP included
                  </n-tag>
                </template>
                <model-preview
                  :available="preview?.model3d.available ?? false"
                  :wrl-url="wrlUrl"
                />
              </preview-card>
            </n-grid-item>
          </n-grid>

          <n-alert
            v-if="importResult"
            type="success"
            class="result-alert"
            title="Import completed"
          >
            <p><strong>Symbol:</strong> {{ importResult.symbolLibrary }}</p>
            <p><strong>Footprint:</strong> {{ importResult.footprintFile }}</p>
            <p><strong>3D models:</strong> {{ importResult.modelDirectory }}</p>
          </n-alert>
      </main>

      <n-drawer v-model:show="drawerOpen" :width="420" placement="right">
        <n-drawer-content title="easy_kicad settings" closable>
          <n-form label-placement="top" :model="settings">
              <n-form-item label="Library root">
                <n-input
                  v-model:value="settings.library_root"
                  placeholder="/Users/name/Documents/KiCad"
                />
              </n-form-item>
              <n-form-item label="Library name">
                <n-input v-model:value="settings.library_name" placeholder="easy_kicad" />
              </n-form-item>
              <n-form-item label="Symbol format">
                <n-space align="center" justify="space-between">
                  <span>{{ settings.symbol_format === 'v6' ? 'KiCad v6+' : 'KiCad v5 legacy' }}</span>
                  <n-switch
                    :value="settings.symbol_format === 'v5'"
                    @update:value="settings.symbol_format = $event ? 'v5' : 'v6'"
                  />
                </n-space>
              </n-form-item>
              <n-form-item label="Request timeout (seconds)">
                <n-input-number
                  v-model:value="settings.request_timeout_seconds"
                  :min="1"
                  :max="120"
                  style="width: 100%"
                />
              </n-form-item>
              <n-form-item label="Proxy URL">
                <n-input
                  v-model:value="settings.proxy_url"
                  placeholder="http://127.0.0.1:7890"
                />
              </n-form-item>
              <n-form-item label="Custom CA bundle">
                <n-input
                  v-model:value="settings.ca_bundle_path"
                  placeholder="/path/to/cacert.pem"
                />
              </n-form-item>
              <n-form-item label="Overwrite existing parts">
                <n-switch v-model:value="settings.overwrite" />
              </n-form-item>
              <n-form-item label="Use project-relative 3D path">
                <n-switch v-model:value="settings.project_relative_3d" />
              </n-form-item>
              <n-form-item label="Ignore SSL verification">
                <n-switch v-model:value="settings.ignore_ssl_verification" />
              </n-form-item>
          </n-form>

          <n-alert
            v-if="connectionResult"
            :type="connectionResult.success ? 'success' : 'error'"
            class="settings-alert"
          >
            {{ connectionResult.message }}
          </n-alert>

          <n-space justify="space-between">
            <n-button secondary @click="testConnection">Test connection</n-button>
            <n-button type="primary" :loading="saving" @click="saveSettings">
              Save settings
            </n-button>
          </n-space>
        </n-drawer-content>
      </n-drawer>
    </div>
  </n-config-provider>
</template>
