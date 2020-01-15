import { ref, Ref, provide, inject, reactive } from '@vue/composition-api'

export const useModal = (defaultOpen = false): [Ref<boolean>, { open: () => void, dismiss: () => void }] => {
  const state = ref(defaultOpen)

  const open = () => {
    state.value = true
  }

  const dismiss = () => {
    state.value = false
  }

  return [
    state,
    {
      open,
      dismiss
    }
  ]
}

const ModalStateSymbol = Symbol('GASymbol')

export const provideModalState = () => {
  const modalState = reactive({
    updateFactorySuccessModal: false
  })

  provide(ModalStateSymbol, modalState)

  return modalState
}

type ModalState = {
  updateFactorySuccessModal: boolean
}

type ModalActions = {
  openUpdateFactorySuccessModal: Function,
  closeUpdateFactorySuccessModal: Function
}

export const useModalState: () => [ModalState, ModalActions] = () => {
  const modalState = inject(ModalStateSymbol) as ModalState

  const openUpdateFactorySuccessModal = () => modalState.updateFactorySuccessModal = true
  const closeUpdateFactorySuccessModal = () => modalState.updateFactorySuccessModal = false

  const modalActions = {
    openUpdateFactorySuccessModal,
    closeUpdateFactorySuccessModal
  }

  return [modalState, modalActions]
}
