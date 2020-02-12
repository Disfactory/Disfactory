import { provide, inject, reactive } from '@vue/composition-api'
import { FactoryData, FACTORY_TYPE, FactoryStatusText } from '../types'
import { getStatusBorderColor, getFactoryStatus } from './map'

const FactoryPopupSymbol = Symbol('FactoryPopup')

export type FactoryPopupState = {
  show: boolean,
}

export const providePopupState = () => {
  const popupState = reactive({
    show: false,
  })

  provide(FactoryPopupSymbol, popupState)

  return [popupState]
}

export const useFactoryPopup = () => {
  const popupState = inject(FactoryPopupSymbol) as FactoryPopupState

  return [popupState]
}

const generateFactorySummary = (factory: FactoryData) => {
  const imageStatus = factory.images.length > 0 ? '已有照片' : '缺照片'

  const type = FACTORY_TYPE.find(type => type.value === factory.type)
  let typeText: string = (type && type.text) || '其他'

  if (typeText.includes('金屬')) {
    typeText = '金屬'
  }

  return [
    imageStatus,
    typeText
  ].filter(Boolean).join('\n')
}

export const getPopupData = (factory: FactoryData) => {
  const status = getFactoryStatus(factory)

  return {
    id: factory.id,
    name: factory.name,
    color: getStatusBorderColor(status),
    status: FactoryStatusText[status][0],
    summary: generateFactorySummary(factory)
  }
}
