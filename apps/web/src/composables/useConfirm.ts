import { ElMessageBox } from 'element-plus'

export function useConfirm() {
  async function confirm(
    message: string,
    title = '确认操作',
    options?: { confirmText?: string; cancelText?: string; type?: 'warning' | 'info' | 'error' }
  ) {
    try {
      await ElMessageBox.confirm(message, title, {
        confirmButtonText: options?.confirmText || '确认',
        cancelButtonText: options?.cancelText || '取消',
        type: options?.type || 'warning',
        confirmButtonClass: options?.type === 'error' ? 'el-button--danger' : '',
      })
      return true
    } catch {
      return false
    }
  }

  return { confirm }
}
