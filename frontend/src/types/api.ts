export interface ApiError {
  message: string
  status?: number
  details?: unknown
}

export type ApiResult<T> = {
  data: T | null
  error: ApiError | null
  loading: boolean
}
