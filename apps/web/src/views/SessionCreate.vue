<template>
  <div class="page-container">
    <PageHeader title="新增训练记录" description="记录一次备考训练" />

    <div class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="top"
        size="large"
        @submit.prevent="handleSubmit"
      >
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="考试类型" prop="exam_type">
              <el-radio-group v-model="form.exam_type">
                <el-radio-button value="CET4">CET-4</el-radio-button>
                <el-radio-button value="CET6">CET-6</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="训练类型" prop="session_type">
              <el-select v-model="form.session_type" placeholder="选择训练类型" style="width: 100%">
                <el-option
                  v-for="st in SESSION_TYPES"
                  :key="st.value"
                  :label="st.label"
                  :value="st.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="试卷名称" prop="paper_name">
          <el-input v-model="form.paper_name" placeholder="如 2024年6月第一套" />
        </el-form-item>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="训练日期" prop="date">
              <el-date-picker
                v-model="form.date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="时长（分钟）" prop="duration_minutes">
              <el-input-number
                v-model="form.duration_minutes"
                :min="1"
                :max="240"
                :step="5"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注" prop="note">
          <el-input
            v-model="form.note"
            type="textarea"
            :rows="3"
            placeholder="可选：训练感受、特殊说明等"
          />
        </el-form-item>

        <div class="form-actions">
          <el-button @click="router.back()">取消</el-button>
          <el-button type="primary" native-type="submit" :loading="submitting">保存记录</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { createSession } from '@/api/sessions'
import { SESSION_TYPES } from '@/types'

const router = useRouter()
const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({
  exam_type: 'CET4',
  paper_name: '',
  session_type: '',
  date: '',
  duration_minutes: 30,
  note: '',
})

const rules: FormRules = {
  exam_type: [{ required: true, message: '请选择考试类型', trigger: 'change' }],
  paper_name: [{ required: true, message: '请输入试卷名称', trigger: 'blur' }],
  session_type: [{ required: true, message: '请选择训练类型', trigger: 'change' }],
  date: [{ required: true, message: '请选择训练日期', trigger: 'change' }],
  duration_minutes: [{ required: true, message: '请输入时长', trigger: 'change' }],
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const res = await createSession({
        exam_type: form.exam_type,
        paper_name: form.paper_name,
        session_type: form.session_type,
        date: form.date,
        duration_minutes: form.duration_minutes,
        note: form.note || undefined,
      })
      ElMessage.success('训练记录已创建')
      router.push(`/sessions/${res.data.id}`)
    } catch {
      // API error handled in interceptor
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
.form-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  border: 1px solid var(--color-border);
  padding: var(--space-2xl);
  max-width: 700px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
  margin-top: var(--space-xl);
  padding-top: var(--space-xl);
  border-top: 1px solid var(--color-border-light);
}
</style>
