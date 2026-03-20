export interface AppSettings {
  library_root: string
  library_name: string
  overwrite: boolean
  project_relative_3d: boolean
  symbol_format: 'v6' | 'v5'
  proxy_url: string
  ca_bundle_path: string
  ignore_ssl_verification: boolean
  request_timeout_seconds: number
}

export interface PartMetadata {
  lcscId: string
  name: string
  package: string
  manufacturer: string
  datasheet: string
}

export interface ModelPreview {
  available: boolean
  name: string | null
  wrlUrl: string | null
  stepAvailable: boolean
}

export interface InspectResponse {
  part: PartMetadata
  symbolSvg: string
  footprintSvg: string
  model3d: ModelPreview
}

export interface ImportResponse {
  success: boolean
  symbolLibrary: string
  footprintFile: string
  modelDirectory: string
  importedSymbolName: string
  importedFootprintName: string
  modelName: string | null
}

export interface ConnectionTestResponse {
  success: boolean
  message: string
}
