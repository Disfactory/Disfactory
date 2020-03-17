/* eslint-disable quote-props */
export const FACTORY_TYPE = [
  { value: '2-1', text: '金屬: 沖床、銑床、車床、鏜孔' },
  { value: '2-2', text: '金屬: 焊接、鑄造、熱處理' },
  { value: '2-3', text: '金屬: 金屬表面處理、噴漆' },
  { value: '3', text: '塑膠加工、射出' },
  { value: '4', text: '橡膠加工' },
  { value: '5', text: '非金屬礦物（石材）' },
  { value: '6', text: '食品' },
  { value: '7', text: '皮革' },
  { value: '8', text: '紡織' },
  { value: '9', text: '其他' }
] as const
export type FactoryType = (typeof FACTORY_TYPE)[number]['value']

type CetReportStatus = 'A' | 'B'

export const CetReportStatusText = {
  A: '未舉報',
  B: '已舉報'
}

export enum FactoryStatus {
  NEW = 'NEW',
  EXISTING_INCOMPLETE = 'EXISTING_INCOMPLETE',
  EXISTING_COMPLETE = 'EXISTING_COMPLETE',
  REPORTED = 'REPORTED'
}

export const FactoryStatusText = {
  [FactoryStatus.NEW]: ['民眾回報工廠'],
  [FactoryStatus.EXISTING_COMPLETE]: ['政府盤查工廠'],
  [FactoryStatus.EXISTING_INCOMPLETE]: ['政府盤查工廠', '資料不齊'],
  [FactoryStatus.REPORTED]: ['已舉報違章工廠']
}

export const FACTORY_STATUS_ITEMS: FactoryStatus[] = [
  FactoryStatus.NEW,
  FactoryStatus.EXISTING_COMPLETE,
  FactoryStatus.EXISTING_INCOMPLETE,
  FactoryStatus.REPORTED
]

export type FactoryImage = {
  id: string,
  image_path: string,
  url: string
}

export type FactoryData = {
  id: string,
  lat: number,
  lng: number,
  name: string,
  landcode: string,
  type: FactoryType,
  images: FactoryImage[],
  // TODO: can be one of https://docs.djangoproject.com/en/2.2/ref/settings/#datetime-input-formats
  // eslint-disable-next-line
  reported_at: null | string,
  data_complete: boolean,
  before_release: boolean,
  cet_report_status: CetReportStatus
}

export type FactoriesResponse = Array<FactoryData>

export type FactoryPostData = {
  name: string,
  type: FactoryType,
  images?: string[],
  others?: string,
  lat: number,
  lng: number,
  nickname?: string,
  contact?: string
}
