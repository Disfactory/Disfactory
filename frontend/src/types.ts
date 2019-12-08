export const FACTORY_TYPE = {
  1: '金屬',
  '2-1': '沖床、銑床、車床、鏜孔',
  '2-2': '焊接、鑄造、熱處理',
  '2-3': '金屬表面處理、噴漆',
  3: '塑膠加工、射出',
  4: '橡膠加工',
  5: '非金屬礦物（石材）',
  6: '食品',
  7: '皮革',
  8: '紡織',
  9: '其他'
}
export type FactoryType = keyof typeof FACTORY_TYPE

export const FACTORY_STATUS = {
  D: '已舉報',
  F: '資料不齊',
  A: '待審核'
}
export type FactoryStatusType = keyof typeof FACTORY_STATUS

export type FactoryData = {
  id: string,
  lat: number,
  lng: number,
  name: string,
  landcode: string,
  type: FactoryType,
  status: FactoryStatusType,
  images: string[],
  // TODO: can be one of https://docs.djangoproject.com/en/2.2/ref/settings/#datetime-input-formats
  // eslint-disable-next-line
  reported_at: null | string
}

export type FactoriesResponse = Array<FactoryData>

export type FactoryPostData = {
  name: string,
  type: FactoryType,
  images?: string[],
  other?: string,
  lat: number,
  lng: number,
  nickname?: string,
  contact?: string
}
