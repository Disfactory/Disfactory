import { inject, provide, reactive } from '@vue/composition-api'
import { useGA } from './useGA'
import { FactoryData } from '../types'

const AppStateSymbol = Symbol('AppState')

// A global state that can be shared across the entire application

export const provideAppState = () => {
  const appState = reactive({
    // Page state
    // TODO: should be rewritten with vue router?
    formMode: 'create',
    factoryFormOpen: false,
    factoryData: null as FactoryData | null,
    factoryLocation: [] as number[],

    // Map state
    selectFactoryMode: false
  })

  provide(AppStateSymbol, appState)

  return [appState]
}

type AppState = ReturnType<typeof provideAppState>[0]

const registerMutator = (appState: AppState) => {
  const { event, pageview } = useGA()

  return {
    openCreateFactoryForm () {
      appState.factoryData = null
      appState.formMode = 'create'
      appState.factoryFormOpen = true
      pageview('/create')
    },

    openEditFactoryForm (factory: FactoryData) {
      appState.factoryData = factory
      appState.formMode = 'edit'
      appState.factoryFormOpen = true
      pageview('/edit')
    },

    closeFactoryPage () {
      appState.factoryFormOpen = false
      event('closeFactoryPage')
    },

    setFactoryLocation (value: [number, number]) {
      appState.factoryLocation = value
      event('setFactoryLocation')
    },

    enterSelectFactoryMode () {
      appState.selectFactoryMode = true
      event('enterSelectFactoryMode')
    },

    exitSelectFactoryMode () {
      appState.selectFactoryMode = false
      event('exitSelectFactoryMode')
    }
  }
}

export const useAppState = () => {
  const appState = inject(AppStateSymbol) as AppState

  return [appState, registerMutator(appState)]
}
