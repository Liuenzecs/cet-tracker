import axios from 'axios'
import { ElMessage } from 'element-plus'

const apiClient = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.response.use(
  (response) => {
    const data = response.data
    if (data && typeof data === 'object' && 'success' in data) {
      if (!data.success) {
        const msg = data.error || '请求失败'
        ElMessage.error(msg)
        return Promise.reject(new Error(msg))
      }
      return { ...response, data: data.data }
    }
    return response
  },
  (error) => {
    const msg = error.response?.data?.error || error.message || '网络请求失败'
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

export default apiClient
