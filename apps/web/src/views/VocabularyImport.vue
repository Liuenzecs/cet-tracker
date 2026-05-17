<template>
  <div class="page-container">
    <PageHeader title="导入词汇笔记" description="使用 Markdown 格式导入词汇，系统将自动解析条目" />

    <div class="import-layout">
      <!-- Form -->
      <div class="import-form-card">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="large">
          <el-form-item label="笔记标题" prop="title">
            <el-input v-model="form.title" placeholder="如 2024年6月CET6听力生词" />
          </el-form-item>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="来源训练">
                <el-select
                  v-model="form.source_session_id"
                  placeholder="（可选）选择关联训练"
                  clearable
                  filterable
                  style="width: 100%"
                >
                  <el-option
                    v-for="s in sessions"
                    :key="s.id"
                    :label="`${s.paper_name} (${s.date})`"
                    :value="s.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="来源模块" prop="source_section">
                <el-select v-model="form.source_section" style="width: 100%">
                  <el-option
                    v-for="ss in SOURCE_SECTIONS"
                    :key="ss.value"
                    :label="ss.label"
                    :value="ss.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="考试类型">
                <el-radio-group v-model="form.exam_type">
                  <el-radio-button value="CET4">CET-4</el-radio-button>
                  <el-radio-button value="CET6">CET-6</el-radio-button>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="试卷名称">
                <el-input v-model="form.paper_name" placeholder="（可选）如 2024年6月第一套" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="Markdown 内容" prop="raw_markdown">
            <el-input
              v-model="form.raw_markdown"
              type="textarea"
              :rows="16"
              placeholder="# 单词1&#10;&#10;释义：...&#10;常见用法：...&#10;&#10;---&#10;&#10;# 单词2&#10;&#10;..."
              class="md-textarea"
            />
          </el-form-item>

          <div class="form-actions">
            <el-button @click="router.back()">取消</el-button>
            <el-button :loading="parsing" @click="handlePreview">预览解析</el-button>
            <el-button type="primary" :loading="saving" @click="handleSave">保存笔记</el-button>
          </div>
        </el-form>
      </div>

      <!-- Help panel -->
      <div class="help-panel">
        <el-collapse>
          <el-collapse-item title="支持的 Markdown 格式说明" name="help">
            <div class="help-content">
              <h4>单词以 # 标题开始</h4>
              <p>每个单词之间用 <code>---</code> 分隔</p>

              <h4>支持的字段</h4>
              <ul>
                <li><strong>释义:</strong> 或 <strong>词义:</strong> — 单词的中文释义</li>
                <li><strong>常见用法:</strong> — 常见搭配和短语</li>
                <li><strong>例句:</strong> — 英文和中文例句对</li>
                <li><strong>易错点:</strong> — 常见错误和混淆点</li>
                <li><strong>同义替换:</strong> — 近义词和替换词</li>
                <li><strong>写作可用句:</strong> — 可用于写作的句子</li>
                <li><strong>易混词对比:</strong> — 易混淆的词汇对比</li>
              </ul>

              <h4>示例</h4>
              <pre class="md-example"># pending

释义：等待处理的；悬而未决的；即将发生的

常见用法：
- pending decision
- pending approval
- patent pending

例句：
- The case is still pending.
  案件仍在审理中。
- A final decision is pending.
  最终决定尚未作出。

易错点：
- 不是"悬挂"的意思（那是 suspend）
- pending 常放在名词后面

同义替换：
- awaiting
- undecided
- unresolved
- imminent

写作可用句：
- With the final exam pending, students are under increasing pressure.

易混词对比：
- pending | impending
  等待决定/处理 | 即将发生（通常指坏事）
  （中性） | （偏负面）

---</pre>
            </div>
          </el-collapse-item>
        </el-collapse>

        <!-- Preview results -->
        <div v-if="previewEntries.length > 0" class="preview-section">
          <h3 class="preview-title">预览解析结果 ({{ previewEntries.length }} 词)</h3>
          <div class="preview-list">
            <div v-for="(entry, idx) in previewEntries" :key="idx" class="preview-item">
              <span class="preview-index">{{ idx + 1 }}</span>
              <strong>{{ entry.term }}</strong>
              <span class="preview-type">{{ entry.entry_type }}</span>
              <span class="preview-meanings">{{ (entry.meanings_json || []).join('; ') }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { createVocabularyNote, parseMarkdown } from '@/api/vocabulary'
import { getSessions } from '@/api/sessions'
import { SOURCE_SECTIONS } from '@/types'
import type { ExamSession, VocabularyEntry } from '@/types'

const router = useRouter()
const formRef = ref<FormInstance>()

const form = reactive({
  title: '',
  source_session_id: undefined as number | undefined,
  exam_type: '',
  paper_name: '',
  source_section: '',
  raw_markdown: '',
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入笔记标题', trigger: 'blur' }],
  source_section: [{ required: true, message: '请选择来源模块', trigger: 'change' }],
  raw_markdown: [{ required: true, message: '请输入 Markdown 内容', trigger: 'blur' }],
}

const sessions = ref<ExamSession[]>([])
const parsing = ref(false)
const saving = ref(false)
const previewEntries = ref<VocabularyEntry[]>([])

async function loadSessions() {
  try {
    const res = await getSessions({ page_size: 200 })
    sessions.value = res.data?.items ?? []
  } catch {
    // Non-critical
  }
}

async function handlePreview() {
  if (!form.raw_markdown.trim()) {
    ElMessage.warning('请先输入 Markdown 内容')
    return
  }
  parsing.value = true
  try {
    const res = await parseMarkdown(form.raw_markdown)
    previewEntries.value = res.data?.entries ?? []
    if (previewEntries.value.length === 0) {
      ElMessage.warning('未能解析出词汇条目，请检查格式')
    } else {
      ElMessage.success(`解析成功：${previewEntries.value.length} 个词汇`)
    }
  } catch { /* handled */ }
  finally { parsing.value = false }
}

async function handleSave() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const res = await createVocabularyNote({
        title: form.title,
        raw_markdown: form.raw_markdown,
        source_session_id: form.source_session_id,
        exam_type: form.exam_type || undefined,
        paper_name: form.paper_name || undefined,
        source_section: form.source_section,
      })
      ElMessage.success('词汇笔记已创建')
      router.push(`/vocabulary/${res.data.id}`)
    } catch { /* handled */ }
    finally { saving.value = false }
  })
}

onMounted(loadSessions)
</script>

<style scoped>
.import-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-xl);
  align-items: start;
}

@media (max-width: 1024px) {
  .import-layout {
    grid-template-columns: 1fr;
  }
}

.import-form-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border);
  padding: var(--space-2xl);
}

.md-textarea :deep(textarea) {
  font-family: 'SF Mono', 'Fira Code', 'Consolas', 'Menlo', monospace;
  font-size: 13px;
  line-height: 1.7;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
  margin-top: var(--space-lg);
  padding-top: var(--space-xl);
  border-top: 1px solid var(--color-border-light);
}

/* Help panel */
.help-panel {
  position: sticky;
  top: var(--space-xl);
}

.help-content {
  font-size: var(--text-body);
  color: var(--color-text-secondary);
  line-height: 1.8;
}

.help-content h4 {
  font-size: var(--text-body);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-top: var(--space-lg);
  margin-bottom: var(--space-xs);
}

.help-content h4:first-child {
  margin-top: 0;
}

.help-content ul {
  padding-left: var(--space-xl);
  margin: var(--space-sm) 0;
}

.help-content li {
  margin-bottom: var(--space-xs);
}

.help-content code {
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  padding: 1px 6px;
  border-radius: var(--radius-sm);
  font-size: var(--text-caption);
}

.md-example {
  background: #1E1E2E;
  color: #CDD6F4;
  padding: var(--space-lg);
  border-radius: var(--radius-md);
  font-size: var(--text-caption);
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  margin-top: var(--space-sm);
}

/* Preview */
.preview-section {
  margin-top: var(--space-xl);
}

.preview-title {
  font-size: var(--text-card-title);
  font-weight: 600;
  margin-bottom: var(--space-md);
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.preview-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  font-size: var(--text-caption);
}

.preview-index {
  width: 20px;
  height: 20px;
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

.preview-type {
  color: var(--color-text-tertiary);
  font-size: var(--text-caption);
}

.preview-meanings {
  color: var(--color-text-secondary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
