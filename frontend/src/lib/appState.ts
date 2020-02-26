import { inject, provide, reactive } from '@vue/composition-api'
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

const registerMutator = (appState: AppState) => {
  return {
    updateFactoryData (factory: FactoryData) {
      appState.factoryData = factory
    },

    openCreateFactoryForm () {
      appState.factoryData = null
      appState.formMode = 'create'
      appState.factoryFormOpen = true
    },

    openEditFactoryForm (factory: FactoryData) {
      appState.factoryData = factory
      appState.formMode = 'edit'
      appState.factoryFormOpen = true
    },

    closeFactoryPage () {
      appState.factoryFormOpen = false
    },

    setFactoryLocation (value: [number, number]) {
      appState.factoryLocation = value
    },

    enterSelectFactoryMode () {
      appState.selectFactoryMode = true
    },

    exitSelectFactoryMode () {
      appState.selectFactoryMode = false
    }
  }
}

type AppState = ReturnType<typeof provideAppState>[0]
type AppAction = ReturnType<typeof registerMutator>

export const useAppState: () => [AppState, AppAction] = () => {
  const appState = inject(AppStateSymbol) as AppState

  return [appState, registerMutator(appState)]
}
