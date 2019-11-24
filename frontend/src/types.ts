export const FACTORY_TYPE = {
  '1': '1',
  '2-1': '沖床、銑床、車床、鏜孔',
  '2-2': '焊接、鑄造、熱處理',
  '2-3': '金屬表面處理、噴漆',
  '3': '塑膠加工、射出',
  '4': '橡膠加工',
  '5': '非金屬礦物（石材）',
  '6': '食品',
  '7': '皮革',
  '8': '紡織',
  '9': '其他'
}

export const FACTORY_STATUS = {
  'D': '已舉報',
  'F': '資料不齊',
  'A': '待審核'
}

export type FactoryData = {
  id: string,
  lat: number,
  lng: number,
  name: string,
  landcode: string,
  // eslint-disable-next-line
  factory_type: keyof typeof FACTORY_TYPE,
  type: keyof typeof FACTORY_STATUS,
  images: string[],
  // TODO: can be one of https://docs.djangoproject.com/en/2.2/ref/settings/#datetime-input-formats
  // eslint-disable-next-line
  reported_at: null | string
}

export type FactoriesResponse = Array<FactoryData>
