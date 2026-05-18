<template>
  <div class="page-container">
    <PageHeader title="设置" description="数据管理：导出备份或导入恢复" />

    <!-- Export -->
    <SectionCard title="数据导出" style="margin-bottom: var(--space-xl)">
      <p class="setting-desc">
        导出所有训练记录、听力/阅读结果、词汇笔记和词汇条目为 JSON 文件，可用于备份或迁移。
      </p>
      <el-button type="primary" :loading="exporting" @click="handleExport">
        <el-icon><Download /></el-icon>
        导出 JSON
      </el-button>
    </SectionCard>

    <!-- Import -->
    <SectionCard title="数据导入">
      <p class="setting-desc">
        从 JSON 文件导入数据。<span class="warning-text">注意：导入将替换当前全部数据，请先导出备份。</span>
      </p>

      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".json"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        class="import-upload"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将 JSON 文件拖到此处，或<em>点击上传</em>
        </div>
      </el-upload>

      <div v-if="filePreview" class="file-preview">
        <div class="file-info">
          <el-icon><Document /></el-icon>
          <span class="file-name">{{ fileName }}</span>
          <el-tag v-if="previewStats" size="small">预览</el-tag>
        </div>
        <div v-if="previewStats" class="preview-stats">
          <div class="preview-stat">
            <span class="ps-label">训练记录</span>
            <span class="ps-value">{{ previewStats.sessions }}</span>
          </div>
          <div class="preview-stat">
            <span class="ps-label">听力结果</span>
            <span class="ps-value">{{ previewStats.listening }}</span>
          </div>
          <div class="preview-stat">
            <span class="ps-label">阅读结果</span>
            <span class="ps-value">{{ previewStats.reading }}</span>
          </div>
          <div class="preview-stat">
            <span class="ps-label">词汇笔记</span>
            <span class="ps-value">{{ previewStats.notes }}</span>
          </div>
          <div class="preview-stat">
            <span class="ps-label">词汇条目</span>
            <span class="ps-value">{{ previewStats.entries }}</span>
          </div>
        </div>
      </div>

      <div class="import-actions">
        <el-button
          type="primary"
          :disabled="!fileData"
          :loading="importing"
          @click="handleImport"
        >
          <el-icon><Upload /></el-icon>
          确认导入
        </el-button>
      </div>
    </SectionCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, type UploadInstance, type UploadFile } from 'element-plus'
import { Download, Upload, UploadFilled, Document } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import SectionCard from '@/components/SectionCard.vue'
import { exportDataJSON, importDataJSON } from '@/api/data'
import { useConfirm } from '@/composables/useConfirm'
import type { ExportData } from '@/types'

const { confirm } = useConfirm()
const uploadRef = ref<UploadInstance>()

const exporting = ref(false)
const importing = ref(false)
const fileData = ref<ExportData | null>(null)
const fileName = ref('')
const filePreview = ref(false)
const previewStats = ref<any>(null)

function countData(data: ExportData) {
  return {
    sessions: data.sessions?.length ?? 0,
    listening: data.listening_results?.length ?? 0,
    reading: data.reading_results?.length ?? 0,
    notes: data.vocabulary_notes?.length ?? 0,
    entries: data.vocabulary_entries?.length ?? 0,
  }
}

async function handleExport() {
  exporting.value = true
  try {
    const res = await exportDataJSON()
    const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `cet-tracker-export-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch { /* handled */ }
  finally { exporting.value = false }
}

function handleFileChange(uploadFile: UploadFile) {
  const raw = uploadFile.raw
  if (!raw) return

  fileName.value = raw.name
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target?.result as string) as ExportData
      fileData.value = data
      filePreview.value = true
      previewStats.value = countData(data)
    } catch {
      ElMessage.error('JSON 文件格式错误')
      fileData.value = null
      filePreview.value = false
      previewStats.value = null
    }
  }
  reader.readAsText(raw)
}

function handleFileRemove() {
  fileData.value = null
  fileName.value = ''
  filePreview.value = false
  previewStats.value = null
}

async function handleImport() {
  if (!fileData.value) return

  const ok = await confirm(
    '导入将完全替换当前数据库中的所有数据。请确认已导出备份。',
    '确认导入数据',
    { type: 'error', confirmText: '确认导入', cancelText: '取消' }
  )
  if (!ok) return

  importing.value = true
  try {
    await importDataJSON(fileData.value)
    ElMessage.success('数据导入成功，页面将刷新')
    setTimeout(() => window.location.reload(), 1500)
  } catch { /* handled */ }
  finally { importing.value = false }
}
</script>

<style scoped>
.setting-desc {
  font-size: var(--text-body);
  color: var(--color-text-secondary);
  line-height: 1.7;
  margin-bottom: var(--space-xl);
}

.warning-text {
  color: #DC2626;
  font-weight: 600;
}

.import-upload {
  margin-bottom: var(--space-xl);
}

.file-preview {
  background: var(--color-bg);
  border-radius: var(--radius-md);
  padding: var(--space-lg) var(--space-xl);
  margin-bottom: var(--space-xl);
}

.file-info {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
}

.file-name {
  font-size: var(--text-body);
  font-weight: 600;
  color: var(--color-text-primary);
}

.preview-stats {
  display: flex;
  gap: var(--space-xl);
  flex-wrap: wrap;
}

.preview-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
}

.ps-label {
  font-size: var(--text-caption);
  color: var(--color-text-tertiary);
}

.ps-value {
  font-size: var(--text-card-title);
  font-weight: 700;
  color: var(--color-primary);
}

.import-actions {
  display: flex;
  justify-content: flex-end;
}
</style>
