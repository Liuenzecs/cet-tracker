<template>
  <div class="page-container">
    <PageHeader title="导入词汇笔记" description="通过单词列表生成结构化词汇笔记，或粘贴 Markdown 导入" />

    <el-alert type="warning" :closable="false" show-icon style="margin-bottom: var(--space-lg)">
      <template #title>
        请勿上传或共享未经授权的真题全文、听力音频、扫描件、出版物内容或完整解析。本工具仅用于记录个人备考笔记和词汇整理。
      </template>
    </el-alert>

    <!-- Flow card -->
    <div class="flow-card" v-if="activeTab === 'generate'">
      <div class="flow-steps">
        <div class="flow-step"><span class="flow-num">1</span> 输入单词</div>
        <el-icon :size="16" color="#D1D5DB"><ArrowRight /></el-icon>
        <div class="flow-step"><span class="flow-num">2</span> AI 生成</div>
        <el-icon :size="16" color="#D1D5DB"><ArrowRight /></el-icon>
        <div class="flow-step"><span class="flow-num">3</span> 预览确认</div>
        <el-icon :size="16" color="#D1D5DB"><ArrowRight /></el-icon>
        <div class="flow-step"><span class="flow-num">4</span> 保存入库</div>
      </div>
    </div>

    <!-- AI status -->
    <div class="ai-status-bar">
      <el-tag :type="aiConfigured ? 'success' : 'info'" size="small">
        AI 生成: {{ aiConfigured ? '已就绪' : '未启用' }}
      </el-tag>
      <span v-if="aiStatusMessage && !aiConfigured" class="ai-status-msg">{{ aiStatusMessage }}</span>
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" class="import-tabs">
      <el-tab-pane label="输入单词生成笔记" name="generate">
        <div class="import-layout">
          <!-- Form -->
          <div class="import-form-card">
            <el-form ref="genFormRef" :model="genForm" :rules="genRules" label-position="top" size="large">
              <!-- Create new / Append toggle -->
              <el-form-item label="操作模式">
                <el-radio-group v-model="saveMode" size="default">
                  <el-radio-button value="new">创建新笔记</el-radio-button>
                  <el-radio-button value="append">追加到已有笔记</el-radio-button>
                </el-radio-group>
              </el-form-item>

              <!-- Append: select note -->
              <el-form-item v-if="saveMode === 'append'" label="选择目标笔记" prop="appendNoteId">
                <el-select v-model="appendNoteId" placeholder="选择要追加的词汇笔记" filterable style="width: 100%">
                  <el-option v-for="n in existingNotes" :key="n.id" :label="`${n.title} (${n.entry_count ?? 0} 词)`" :value="n.id" />
                </el-select>
              </el-form-item>

              <!-- New note: title & metadata -->
              <template v-if="saveMode === 'new'">
                <el-form-item label="笔记标题" prop="title">
                  <el-input v-model="genForm.title" placeholder="如 CET6 阅读生词笔记（留空自动生成）" />
                </el-form-item>

                <el-row :gutter="16">
                  <el-col :span="12">
                    <el-form-item label="考试类型">
                      <el-radio-group v-model="genForm.exam_type">
                        <el-radio-button value="CET4">CET-4</el-radio-button>
                        <el-radio-button value="CET6">CET-6</el-radio-button>
                      </el-radio-group>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="来源模块" prop="source_section">
                      <el-select v-model="genForm.source_section" style="width: 100%">
                        <el-option v-for="ss in SOURCE_SECTIONS" :key="ss.value" :label="ss.label" :value="ss.value" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="16">
                  <el-col :span="12">
                    <el-form-item label="来源训练">
                      <el-select v-model="genForm.source_session_id" placeholder="（可选）选择关联训练" clearable filterable style="width: 100%">
                        <el-option v-for="s in sessions" :key="s.id" :label="`${s.paper_name} (${s.date})`" :value="s.id" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="试卷名称">
                    <el-input v-model="genForm.paper_name" placeholder="（可选）如 2024年6月第一套" />
                  </el-form-item>
                </el-col>
              </el-row>
              </template>

              <el-form-item label="单词或短语列表" prop="words">
                <template #label>
                  <span>单词或短语列表 <span class="word-count-badge">{{ wordCount }} 词</span></span>
                </template>
                <el-input
                  v-model="wordsText"
                  type="textarea"
                  :rows="8"
                  placeholder="每行一个，或用逗号、分号分隔&#10;例如：&#10;pending&#10;materialise&#10;real estate&#10;utmost&#10;negligible"
                  class="words-textarea"
                />
              </el-form-item>

              <!-- Generation options -->
              <el-collapse style="margin-bottom: var(--space-lg)">
                <el-collapse-item title="生成偏好设置" name="options">
                  <el-row :gutter="16">
                    <el-col :span="12">
                      <el-form-item label="详细程度" size="default">
                        <el-select v-model="genForm.options.detail_level" style="width: 100%">
                          <el-option label="简洁 — 只含核心释义和例句" value="brief" />
                          <el-option label="标准 — 释义、用法、例句、易错点" value="standard" />
                          <el-option label="详细 — 全面展开所有字段" value="detailed" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="例句风格" size="default">
                        <el-select v-model="genForm.options.example_style" style="width: 100%">
                          <el-option label="四六级 — 校园和日常生活" value="cet" />
                          <el-option label="学术 — 偏学术场景" value="academic" />
                          <el-option label="日常 — 偏日常口语" value="daily" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="16">
                    <el-col :span="12">
                      <el-form-item label="写作可用句" size="default">
                        <el-switch v-model="genForm.options.include_writing_sentences" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="易混词对比" size="default">
                        <el-switch v-model="genForm.options.include_comparisons" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </el-collapse-item>
              </el-collapse>

              <div class="form-actions">
                <el-button @click="router.back()">取消</el-button>
                <el-button @click="clearWords">清空</el-button>
                <el-button type="primary" :loading="generating" :disabled="wordCount === 0" @click="handleGenerate">
                  <el-icon><MagicStick /></el-icon>
                  AI 生成预览
                </el-button>
              </div>
            </el-form>
          </div>

          <!-- Right: Preview -->
          <div class="right-panel" v-if="genPreview">
            <div class="preview-header-bar">
              <div class="preview-header-left">
                <h3 class="preview-title">预览结果 ({{ genEntries.length }} 词)</h3>
                <el-tag size="small" type="primary">AI 生成</el-tag>
              </div>
              <el-button type="primary" :loading="savingGen" @click="handleSaveGenerated">保存笔记</el-button>
            </div>

            <div v-if="genWarnings.length > 0" class="preview-warnings">
              <el-alert v-for="(w, i) in genWarnings" :key="i" :title="w" type="warning" show-icon :closable="false" style="margin-bottom: 4px" />
            </div>

            <!-- Generated markdown (collapsed) -->
            <el-collapse style="margin-bottom: var(--space-lg)">
              <el-collapse-item title="查看生成的 Markdown">
                <pre class="raw-md-preview">{{ genStandardizedMarkdown }}</pre>
              </el-collapse-item>
            </el-collapse>

            <!-- Entry cards (collapsible) -->
            <div class="gen-entry-list">
              <div v-for="(entry, idx) in genEntries" :key="idx" class="gen-entry-card" :class="{ expanded: expandedSet.has(idx) }">
                <div class="gen-entry-header" @click="toggleExpand(idx)">
                  <span class="gen-entry-idx">{{ idx + 1 }}</span>
                  <span class="gen-entry-term-text">{{ entry.term }}</span>
                  <el-tag size="small">{{ entry.entry_type }}</el-tag>
                  <span class="gen-summary">{{ entrySummary(entry) }}</span>
                  <el-icon class="gen-expand-icon" :class="{ rotated: expandedSet.has(idx) }"><ArrowDown /></el-icon>
                  <el-button size="small" type="danger" text @click.stop="removeGenEntry(idx)"><el-icon><Delete /></el-icon></el-button>
                </div>
                <div v-if="expandedSet.has(idx)" class="gen-entry-body">
                  <div class="gen-edit-row">
                    <el-input v-model="entry.term" size="small" class="gen-term-input" placeholder="词汇" />
                  </div>
                  <div v-if="entry.uk_phonetic || entry.us_phonetic || entry.pronunciation_ipa" class="gen-section">
                    <span class="gen-label">发音</span>
                    <div class="gen-line">
                      <template v-if="entry.uk_phonetic">UK {{ entry.uk_phonetic }}</template>
                      <template v-if="entry.uk_phonetic && entry.us_phonetic"> &middot; </template>
                      <template v-if="entry.us_phonetic">US {{ entry.us_phonetic }}</template>
                      <template v-if="!entry.uk_phonetic && !entry.us_phonetic && entry.pronunciation_ipa">{{ entry.pronunciation_ipa }}</template>
                    </div>
                  </div>
                  <div v-if="entry.meanings?.length" class="gen-section">
                    <span class="gen-label">释义</span>
                    <div v-for="(m, mi) in entry.meanings" :key="mi" class="gen-line">
                      <template v-if="m.pos"><el-tag size="small" type="info" style="margin-right:4px">{{ m.pos }}</el-tag></template>
                      {{ m.zh }}<template v-if="m.en"> ({{ m.en }})</template>
                    </div>
                  </div>
                  <div v-if="entry.usages?.length" class="gen-section">
                    <span class="gen-label">常见用法</span>
                    <div v-for="(u, ui) in entry.usages" :key="ui" class="gen-line">
                      <code>{{ u.pattern }}</code><template v-if="u.meaning"> — {{ u.meaning }}</template>
                    </div>
                  </div>
                  <div v-if="entry.examples?.length" class="gen-section">
                    <span class="gen-label">例句</span>
                    <div v-for="(ex, ei) in entry.examples" :key="ei" class="gen-line">
                      <span class="gen-ex-en">{{ ex.en }}</span>
                      <span v-if="ex.zh" class="gen-ex-zh"> — {{ ex.zh }}</span>
                    </div>
                  </div>
                  <div v-if="entry.mistake_tips?.length" class="gen-section">
                    <span class="gen-label">易错点</span>
                    <div v-for="(t, ti) in entry.mistake_tips" :key="ti" class="gen-line gen-mistake">{{ t }}</div>
                  </div>
                  <div v-if="entry.synonyms?.length" class="gen-section">
                    <span class="gen-label">同义替换</span>
                    <el-tag v-for="(s, si) in entry.synonyms" :key="si" size="small" type="success" style="margin-right:4px;margin-bottom:2px">{{ s }}</el-tag>
                  </div>
                  <div v-if="entry.comparisons?.length" class="gen-section">
                    <span class="gen-label">易混词对比</span>
                    <div v-for="(c, ci) in entry.comparisons" :key="ci" class="gen-line">
                      {{ c.left }} vs {{ c.right }}<template v-if="c.left_meaning"> — {{ c.left_meaning }} / {{ c.right_meaning }}</template>
                    </div>
                  </div>
                  <div v-if="entry.writing_sentences?.length" class="gen-section">
                    <span class="gen-label">写作可用句</span>
                    <div v-for="(ws, wi) in entry.writing_sentences" :key="wi" class="gen-line gen-writing">
                      {{ ws.en }}<template v-if="ws.zh"> — {{ ws.zh }}</template>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty right panel -->
          <div class="right-panel right-empty" v-else>
            <div class="empty-hint">
              <el-icon :size="40" color="#D1D5DB"><MagicStick /></el-icon>
              <p>输入单词列表后，点击「AI 生成预览」</p>
              <p class="empty-sub">AI 会为每个词生成释义、用法、例句、易错点等</p>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Tab 2: Markdown import -->
      <el-tab-pane label="粘贴 Markdown 导入" name="markdown">
        <div class="import-layout">
          <div class="import-form-card">
            <el-form ref="mdFormRef" :model="mdForm" :rules="mdRules" label-position="top" size="large">
              <el-alert type="info" :closable="false" show-icon style="margin-bottom: var(--space-md)">
                <template #title>已有 Markdown 笔记？可以从这里导入。推荐使用「输入单词生成笔记」获得更结构化的结果。</template>
              </el-alert>

              <el-form-item label="笔记标题" prop="title">
                <el-input v-model="mdForm.title" placeholder="如 CET6 听力生词笔记" />
              </el-form-item>

              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="来源训练">
                    <el-select v-model="mdForm.source_session_id" placeholder="（可选）选择关联训练" clearable filterable style="width: 100%">
                      <el-option v-for="s in sessions" :key="s.id" :label="`${s.paper_name} (${s.date})`" :value="s.id" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="来源模块" prop="source_section">
                    <el-select v-model="mdForm.source_section" style="width: 100%">
                      <el-option v-for="ss in SOURCE_SECTIONS" :key="ss.value" :label="ss.label" :value="ss.value" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="考试类型">
                    <el-radio-group v-model="mdForm.exam_type">
                      <el-radio-button value="CET4">CET-4</el-radio-button>
                      <el-radio-button value="CET6">CET-6</el-radio-button>
                    </el-radio-group>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="试卷名称">
                    <el-input v-model="mdForm.paper_name" placeholder="（可选）如 2024年6月第一套" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="Markdown 内容" prop="raw_markdown">
                <el-input v-model="mdForm.raw_markdown" type="textarea" :rows="12" placeholder="## pending&#10;&#10;### 释义&#10;待处理的..." class="md-textarea" />
              </el-form-item>

              <div class="form-actions">
                <el-button @click="router.back()">取消</el-button>
                <el-button :loading="mdParsing" @click="handleLocalPreview">本地解析预览</el-button>
                <el-button :loading="mdAiNormalizing" :disabled="!aiConfigured" @click="handleMdAINormalize">AI 规范化</el-button>
                <el-button type="primary" :loading="mdSaving" @click="handleMdSave">保存笔记</el-button>
              </div>
            </el-form>
          </div>

          <!-- Markdown help panel -->
          <div class="right-panel">
            <el-collapse style="margin-bottom: var(--space-lg)">
              <el-collapse-item title="支持的 Markdown 格式" name="help">
                <div class="help-content">
                  <h4>单词以 # 或 ## 标题开始</h4>
                  <p>每个单词块之间用 <code>---</code> 或空行分隔</p>
                  <h4>支持的字段</h4>
                  <ul>
                    <li><strong>释义:</strong> — 中文释义</li>
                    <li><strong>常见用法:</strong> — 搭配和短语</li>
                    <li><strong>例句:</strong> — 英文 + 中文</li>
                    <li><strong>易错点:</strong> — 常见错误</li>
                    <li><strong>同义替换:</strong> — 近义词</li>
                    <li><strong>写作可用句:</strong> — 写作句</li>
                    <li><strong>易混词对比:</strong> — 近义词对比</li>
                  </ul>
                  <pre class="md-example"># pending

释义：等待处理的；悬而未决的

常见用法：
- pending decision — 待定的决定
- pending approval — 等待批准</pre>
                </div>
              </el-collapse-item>
            </el-collapse>

            <!-- MD preview -->
            <div v-if="mdPreviewEntries.length > 0" class="preview-section">
              <div class="preview-header-bar">
                <div class="preview-header-left">
                  <h3 class="preview-title">预览 ({{ mdPreviewEntries.length }} 词)</h3>
                  <el-tag size="small">{{ mdPreviewSource === 'ai' ? 'AI' : '本地' }}</el-tag>
                </div>
              </div>
              <div v-if="mdPreviewWarnings.length > 0" class="preview-warnings">
                <el-alert v-for="(w, i) in mdPreviewWarnings" :key="i" :title="w" type="warning" show-icon :closable="false" style="margin-bottom: 2px" />
              </div>
              <div class="preview-list">
                <div v-for="(entry, idx) in mdPreviewEntries" :key="idx" class="preview-item">
                  <div class="preview-item-header">
                    <span class="preview-index">{{ idx + 1 }}</span>
                    <el-input v-model="entry.term" size="small" class="preview-term-input" />
                    <el-tag size="small" type="info">{{ entry.entry_type }}</el-tag>
                    <span class="preview-stats">
                      <template v-if="entry.meanings_json?.length">释义 {{ entry.meanings_json.length }} </template>
                      <template v-if="entry.examples_json?.length">例句 {{ entry.examples_json.length }} </template>
                    </span>
                    <el-button size="small" type="danger" text @click="removeMdPreviewEntry(idx)"><el-icon><Delete /></el-icon></el-button>
                  </div>
                  <div class="preview-item-body">
                    <div v-if="entry.pronunciation_ipa || entry.uk_phonetic || entry.us_phonetic" class="preview-meaning">
                      发音:
                      <template v-if="entry.uk_phonetic">UK {{ entry.uk_phonetic }} </template>
                      <template v-if="entry.us_phonetic">US {{ entry.us_phonetic }} </template>
                      <template v-if="!entry.uk_phonetic && !entry.us_phonetic && entry.pronunciation_ipa">{{ entry.pronunciation_ipa }}</template>
                    </div>
                    <div v-if="entry.meanings_json?.length" class="preview-meaning">释义: {{ (entry.meanings_json || []).join('; ') }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { ArrowRight, ArrowDown, MagicStick, Delete } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { createVocabularyNote, parseMarkdown, normalizeMarkdown, getAIStatus, generateFromWords, saveGeneratedNote, appendEntriesToNote, getVocabularyNotes } from '@/api/vocabulary'
import { getSessions } from '@/api/sessions'
import { SOURCE_SECTIONS } from '@/types'
import type { ExamSession, VocabularyEntry, GeneratedVocabularyEntry, GenerationOptions } from '@/types'

const router = useRouter()
const route = useRoute()

// ── Common state ──
const activeTab = ref('generate')
const sessions = ref<ExamSession[]>([])
const aiConfigured = ref(false)
const aiStatusMessage = ref('')

// ── Tab 1: Word generation ──
const genFormRef = ref<FormInstance>()
const wordsText = ref('')
const generating = ref(false)
const savingGen = ref(false)
const genPreview = ref(false)
const genEntries = ref<GeneratedVocabularyEntry[]>([])
const genWarnings = ref<string[]>([])
const genStandardizedMarkdown = ref('')
const expandedSet = ref<Set<number>>(new Set())
const saveMode = ref<'new' | 'append'>('new')
const appendNoteId = ref<number | null>(null)
const existingNotes = ref<{ id: number; title: string; entry_count: number }[]>([])

function toggleExpand(idx: number) {
  const s = new Set(expandedSet.value)
  if (s.has(idx)) { s.delete(idx) } else { s.add(idx) }
  expandedSet.value = s
}

function entrySummary(entry: GeneratedVocabularyEntry): string {
  const parts: string[] = []
  if (entry.meanings?.length) {
    const m = entry.meanings[0]
    parts.push([m.pos, m.zh].filter(Boolean).join(' '))
  }
  if (entry.usages?.length) parts.push(`${entry.usages.length} 用法`)
  if (entry.examples?.length) parts.push(`${entry.examples.length} 例句`)
  return parts.join('  ·  ')
}
const genForm = reactive({
  title: '',
  exam_type: 'CET6',
  paper_name: '',
  source_section: 'other',
  source_session_id: undefined as number | undefined,
  options: {
    detail_level: 'standard' as const,
    example_style: 'cet' as const,
    include_writing_sentences: true,
    include_comparisons: true,
    language: 'zh-CN',
  },
})
const genRules: FormRules = {
  source_section: [{ required: true, message: '请选择来源模块', trigger: 'change' }],
}

const wordCount = computed(() => {
  if (!wordsText.value.trim()) return 0
  // Count non-empty lines after trimming, dedup for display
  const parts = wordsText.value
    .split(/[\n,;，；]+/)
    .map(s => s.trim())
    .filter(s => s.length > 0)
  return new Set(parts.map(s => s.toLowerCase())).size
})

function clearWords() {
  wordsText.value = ''
  genPreview.value = false
  genEntries.value = []
  expandedSet.value = new Set()
}

function removeGenEntry(idx: number) {
  genEntries.value.splice(idx, 1)
}

async function handleGenerate() {
  if (!wordsText.value.trim()) {
    ElMessage.warning('请输入单词或短语')
    return
  }
  if (!aiConfigured.value) {
    ElMessage.info('AI 生成未启用，请在后端 .env 中配置 AI_NORMALIZER_ENABLED 和 AI_API_KEY')
    return
  }

  // Parse words from text
  const rawWords = wordsText.value
    .split(/[\n,;，；]+/)
    .map(s => s.trim())
    .filter(s => s.length > 0 && s.length <= 100)

  const uniqueWords: string[] = []
  const seen = new Set<string>()
  for (const w of rawWords) {
    const lower = w.toLowerCase()
    if (!seen.has(lower)) {
      seen.add(lower)
      uniqueWords.push(w)
    }
  }

  if (uniqueWords.length === 0) {
    ElMessage.warning('未能解析出有效单词')
    return
  }
  if (uniqueWords.length > 50) {
    ElMessage.warning('一次最多生成 50 个词，已截取前 50 个')
    uniqueWords.splice(50)
  }

  generating.value = true
  genPreview.value = false
  try {
    const res = await generateFromWords({
      title: genForm.title || `${genForm.exam_type} 词汇笔记 ${new Date().toISOString().slice(0, 10)}`,
      exam_type: genForm.exam_type,
      paper_name: genForm.paper_name,
      source_section: genForm.source_section,
      source_session_id: genForm.source_session_id ?? null,
      words: uniqueWords,
      options: genForm.options,
    })

    const data = res.data
    genEntries.value = data?.entries ?? []
    genWarnings.value = data?.warnings ?? []
    genStandardizedMarkdown.value = data?.standardized_markdown ?? ''
    expandedSet.value = new Set()
    genPreview.value = true

    if (genEntries.value.length === 0 && genWarnings.value.length > 0) {
      ElMessage.warning(`AI 生成完成，但有警告: ${genWarnings.value.join('; ')}`)
    } else if (genEntries.value.length === 0) {
      ElMessage.warning('AI 未返回有效词条，请检查输入或尝试重试')
    } else {
      ElMessage.success(`AI 生成完成：${genEntries.value.length} 个词汇`)
    }
  } catch {
    ElMessage.error('AI 生成失败，请确认后端 AI 配置正确')
  } finally {
    generating.value = false
  }
}

async function handleSaveGenerated() {
  if (!genEntries.value.length) {
    ElMessage.warning('没有可保存的词条')
    return
  }
  savingGen.value = true
  try {
    if (saveMode.value === 'append' && appendNoteId.value) {
      // Append to existing note
      const res = await appendEntriesToNote(appendNoteId.value, {
        title: '',
        raw_input: wordsText.value,
        standardized_markdown: genStandardizedMarkdown.value,
        source_section: 'other',
        entries: genEntries.value,
      })
      ElMessage.success(`已追加 ${res.data.appended_count} 个词条`)
      router.push(`/vocabulary/${res.data.note_id}`)
    } else {
      // Create new note
      const res = await saveGeneratedNote({
        title: genForm.title || `${genForm.exam_type} 词汇笔记 ${new Date().toISOString().slice(0, 10)}`,
        raw_input: wordsText.value,
        standardized_markdown: genStandardizedMarkdown.value,
        source_session_id: genForm.source_session_id ?? null,
        exam_type: genForm.exam_type,
        paper_name: genForm.paper_name,
        source_section: genForm.source_section,
        entries: genEntries.value,
      })
      ElMessage.success(`词汇笔记已创建，共 ${res.data.entry_count} 词`)
      router.push(`/vocabulary/${res.data.id}`)
    }
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingGen.value = false
  }
}

// ── Tab 2: Markdown import ──
const mdFormRef = ref<FormInstance>()
const mdParsing = ref(false)
const mdAiNormalizing = ref(false)
const mdSaving = ref(false)
const mdPreviewEntries = ref<VocabularyEntry[]>([])
const mdPreviewWarnings = ref<string[]>([])
const mdPreviewSource = ref('local')
const mdForm = reactive({
  title: '',
  source_session_id: undefined as number | undefined,
  exam_type: '',
  paper_name: '',
  source_section: '',
  raw_markdown: '',
})
const mdRules: FormRules = {
  title: [{ required: true, message: '请输入笔记标题', trigger: 'blur' }],
  source_section: [{ required: true, message: '请选择来源模块', trigger: 'change' }],
  raw_markdown: [{ required: true, message: '请输入 Markdown 内容', trigger: 'blur' }],
}

async function handleLocalPreview() {
  if (!mdForm.raw_markdown.trim()) { ElMessage.warning('请先输入 Markdown 内容'); return }
  mdParsing.value = true; mdPreviewSource.value = 'local'; mdPreviewWarnings.value = []
  try {
    const res = await parseMarkdown(mdForm.raw_markdown)
    mdPreviewEntries.value = (res.data?.entries ?? []).map(e => ({ ...e, id: 0, note_id: 0 } as VocabularyEntry))
    ElMessage.success(mdPreviewEntries.value.length ? `本地解析：${mdPreviewEntries.value.length} 个词汇` : '未能解析出词汇条目')
  } catch { ElMessage.error('本地解析失败') } finally { mdParsing.value = false }
}

async function handleMdAINormalize() {
  if (!mdForm.raw_markdown.trim()) { ElMessage.warning('请先输入 Markdown 内容'); return }
  if (!aiConfigured.value) { ElMessage.info('AI 未启用'); return }
  mdAiNormalizing.value = true; mdPreviewSource.value = 'ai'
  try {
    const res = await normalizeMarkdown(mdForm.raw_markdown)
    const data = res.data
    mdPreviewWarnings.value = data?.warnings ?? []
    mdPreviewEntries.value = (data?.entries ?? []).map(e => ({
      id: 0, note_id: 0, term: e.term, entry_type: e.entry_type,
      meanings_json: e.meanings?.map((m: any) => [m.pos, m.zh].filter(Boolean).join(' ')),
      usages_json: e.usages?.map((u: any) => u.meaning ? `${u.pattern} — ${u.meaning}` : u.pattern),
      examples_json: e.examples?.map((ex: any) => ({ en: ex.en, zh: ex.zh })),
      mistake_tips_json: e.mistake_tips, synonyms_json: e.synonyms,
      comparisons_json: e.comparisons?.map((c: any) => ({ left: c.left, right: c.right, left_meaning: c.left_meaning, right_meaning: c.right_meaning })),
      writing_sentences_json: e.writing_sentences,
      familiarity: 'new', review_count: 0, tags_json: [], created_at: '', updated_at: '',
    })) as VocabularyEntry[]
    ElMessage.success(mdPreviewEntries.value.length ? `AI 规范化：${mdPreviewEntries.value.length} 个词汇` : 'AI 未返回有效词条')
  } catch { ElMessage.error('AI 规范化失败') } finally { mdAiNormalizing.value = false }
}

function removeMdPreviewEntry(idx: number) { mdPreviewEntries.value.splice(idx, 1) }

async function handleMdSave() {
  if (!mdFormRef.value) return
  await mdFormRef.value.validate(async (valid) => {
    if (!valid) return
    mdSaving.value = true
    try {
      const res = await createVocabularyNote({
        title: mdForm.title, raw_markdown: mdForm.raw_markdown,
        source_session_id: mdForm.source_session_id,
        exam_type: mdForm.exam_type || undefined,
        paper_name: mdForm.paper_name || undefined,
        source_section: mdForm.source_section,
      })
      ElMessage.success('词汇笔记已创建')
      router.push(`/vocabulary/${res.data.id}`)
    } catch { ElMessage.error('保存失败') } finally { mdSaving.value = false }
  })
}

// ── Init ──
async function loadSessions() {
  try { sessions.value = (await getSessions({ page_size: 200 })).data?.items ?? [] } catch { /* */ }
}
async function checkAIStatus() {
  try {
    const res = await getAIStatus()
    aiConfigured.value = res.data?.configured ?? false
    aiStatusMessage.value = res.data?.message ?? ''
  } catch { /* */ }
}
async function loadExistingNotes() {
  try {
    const res = await getVocabularyNotes({ page_size: 200 })
    existingNotes.value = (res.data?.items ?? []).map((n: any) => ({
      id: n.id, title: n.title, entry_count: n.entry_count ?? 0,
    }))
  } catch { /* */ }
}

watch(saveMode, (mode) => {
  if (mode === 'append' && existingNotes.value.length === 0) {
    loadExistingNotes()
  }
})

onMounted(async () => {
  await loadSessions()
  checkAIStatus()
  loadExistingNotes()

  // Auto-fill from session_id query param
  const sid = route.query?.session_id
  if (sid) {
    const sessionId = parseInt(sid as string)
    genForm.source_session_id = sessionId
    mdForm.source_session_id = sessionId
    // Look up session to auto-fill exam_type and paper_name
    const session = sessions.value.find(s => s.id === sessionId)
    if (session) {
      genForm.exam_type = session.exam_type
      genForm.paper_name = session.paper_name
      mdForm.exam_type = session.exam_type
      mdForm.paper_name = session.paper_name
    }
  }
})
</script>

<style scoped>
/* Flow card */
.flow-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  padding: var(--space-lg) var(--space-xl);
  margin-bottom: var(--space-lg);
}
.flow-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-lg);
}
.flow-step {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: var(--text-body);
  font-weight: 500;
  color: var(--color-text-primary);
}
.flow-num {
  width: 22px; height: 22px;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
}

/* AI status */
.ai-status-bar {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
  padding: var(--space-sm) var(--space-md);
  background: var(--color-bg);
  border-radius: var(--radius-md);
  font-size: var(--text-caption);
}
.ai-status-msg { color: var(--color-text-tertiary); }

/* Tabs */
.import-tabs :deep(.el-tabs__header) { margin-bottom: var(--space-lg); }

/* Layout */
.import-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-xl);
  align-items: start;
}
@media (max-width: 1024px) { .import-layout { grid-template-columns: 1fr; } }

.import-form-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border);
  padding: var(--space-2xl);
}

/* Word count badge */
.word-count-badge {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-primary);
  background: var(--color-primary-light);
  padding: 1px 8px;
  border-radius: var(--radius-sm);
  margin-left: var(--space-sm);
}

/* Textareas */
.words-textarea :deep(textarea), .md-textarea :deep(textarea) {
  font-family: 'SF Mono', 'Fira Code', 'Consolas', 'Menlo', monospace;
  font-size: 13px;
  line-height: 1.7;
}

/* Actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
  margin-top: var(--space-lg);
  padding-top: var(--space-xl);
  border-top: 1px solid var(--color-border-light);
}

/* Right panel */
.right-panel { position: sticky; top: var(--space-xl); }
.right-empty { display: flex; flex-direction: column; }

.empty-hint {
  text-align: center;
  padding: var(--space-3xl) var(--space-xl);
  color: var(--color-text-tertiary);
}
.empty-hint p { margin: var(--space-sm) 0 0; }
.empty-sub { font-size: var(--text-caption); }

/* Preview header */
.preview-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-md);
  gap: var(--space-sm);
}
.preview-header-left { display: flex; align-items: center; gap: var(--space-sm); }
.preview-title { font-size: var(--text-card-title); font-weight: 600; margin: 0; }

/* Preview warnings */
.preview-warnings { margin-bottom: var(--space-md); }

/* Raw markdown preview */
.raw-md-preview {
  background: #1E1E2E;
  color: #CDD6F4;
  padding: var(--space-lg);
  border-radius: var(--radius-md);
  font-size: 11px;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
}

/* Gen entries (collapsible) */
.gen-entry-list { display: flex; flex-direction: column; gap: 6px; }
.gen-entry-card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  overflow: hidden;
  transition: border-color 0.15s;
}
.gen-entry-card:hover { border-color: var(--color-primary); }
.gen-entry-header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 6px var(--space-md);
  cursor: pointer;
  user-select: none;
  min-height: 36px;
}
.gen-entry-card.expanded .gen-entry-header {
  border-bottom: 1px solid var(--color-border-light);
}
.gen-entry-idx {
  width: 20px; height: 20px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}
.gen-entry-term-text {
  font-weight: 600;
  font-size: var(--text-body);
  color: var(--color-text-primary);
  min-width: 80px;
}
.gen-summary {
  flex: 1;
  font-size: 12px;
  color: var(--color-text-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.gen-expand-icon {
  color: var(--color-text-tertiary);
  transition: transform 0.2s;
  flex-shrink: 0;
}
.gen-expand-icon.rotated { transform: rotate(180deg); }
.gen-entry-body {
  padding: var(--space-md) var(--space-lg);
  font-size: var(--text-caption);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}
.gen-edit-row { margin-bottom: var(--space-xs); }
.gen-term-input { width: 180px; }
.gen-section { line-height: 1.7; }
.gen-label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 2px;
}
.gen-line { padding: 2px 0; color: var(--color-text-primary); }
.gen-line code { font-size: 12px; background: var(--color-bg); padding: 1px 5px; border-radius: 3px; }
.gen-line.gen-mistake { color: #92400E; }
.gen-line.gen-writing { font-style: italic; color: var(--color-primary-dark); }
.gen-ex-en { font-weight: 500; }
.gen-ex-zh { color: var(--color-text-tertiary); margin-left: 2px; }

/* Help panel */
.help-content { font-size: var(--text-body); color: var(--color-text-secondary); line-height: 1.8; }
.help-content h4 { font-size: var(--text-body); font-weight: 600; color: var(--color-text-primary); margin: var(--space-md) 0 var(--space-xs); }
.help-content h4:first-child { margin-top: 0; }
.help-content ul { padding-left: var(--space-xl); margin: var(--space-sm) 0; }
.help-content li { margin-bottom: var(--space-xs); }
.help-content code { background: var(--color-primary-light); color: var(--color-primary-dark); padding: 1px 6px; border-radius: var(--radius-sm); font-size: var(--text-caption); }
.md-example {
  background: #1E1E2E; color: #CDD6F4; padding: var(--space-lg); border-radius: var(--radius-md);
  font-size: var(--text-caption); line-height: 1.6; overflow-x: auto; white-space: pre-wrap; margin-top: var(--space-sm);
}

/* Preview section */
.preview-section { margin-top: var(--space-lg); }
.preview-list { display: flex; flex-direction: column; gap: var(--space-sm); }
.preview-item { background: var(--color-surface); border-radius: var(--radius-md); border: 1px solid var(--color-border); padding: var(--space-md); }
.preview-item-header { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-xs); }
.preview-index { width: 20px; height: 20px; background: var(--color-primary-light); color: var(--color-primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; flex-shrink: 0; }
.preview-term-input { width: 150px; }
.preview-stats { flex: 1; font-size: 11px; color: var(--color-text-tertiary); }
.preview-item-body { padding-left: 28px; }
.preview-meaning { font-size: var(--text-caption); color: var(--color-text-primary); line-height: 1.6; }
</style>
