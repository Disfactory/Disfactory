import { ref, Ref, provide, inject, reactive, InjectionKey } from '@vue/composition-api'
import { useGA } from './useGA'
import { isNotSupportedIOS } from './browserCheck'

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

const ModalStateSymbol: InjectionKey<ModalState> = Symbol('ModalStateSymbol')

export const provideModalState = () => {
  const modalState = reactive({
    updateFactorySuccessModal: false,
    createFactorySuccessModal: false,
    aboutModalOpen: false,
    contactModalOpen: false,
    safetyModalOpen: false,
    gettingStartedModalOpen: localStorage.getItem('use-app') !== 'true',
    tutorialModalOpen: false,
    supportIOSVersionModalOpen: isNotSupportedIOS(),

    sidebarOpen: false,
    filterModalOpen: false
  })

  provide(ModalStateSymbol, modalState)

  return modalState
}

type ModalState = ReturnType<typeof provideModalState>

type ModalActions = {
  openUpdateFactorySuccessModal: Function,
  closeUpdateFactorySuccessModal: Function,

  openCreateFactorySuccessModal: Function,
  closeCreateFactorySuccessModal: Function,

  openAboutModal: Function,
  closeAboutModal: Function,

  openContactModal: Function,
  closeContactModal: Function,

  openSafetyModal: Function,
  closeSafetyModal: Function,

  openGettingStartedModal: Function,
  closeGettingStartedModal: Function,

  toggleSidebar: Function,

  closeFilterModal: Function,
  openFilterModal: Function,

  closeTutorialModal: Function,
  openTutorialModal: Function,

  closesupportIOSVersionModal: Function
}

export const useModalState: () => [ModalState, ModalActions] = () => {
  const modalState = inject(ModalStateSymbol)

  if (!modalState) {
    throw new Error('Use useModalState before provideModalState')
  }
  const { event } = useGA()

  const openUpdateFactorySuccessModal = () => { modalState.updateFactorySuccessModal = true }
  const closeUpdateFactorySuccessModal = () => { modalState.updateFactorySuccessModal = false }

  const openCreateFactorySuccessModal = () => { modalState.createFactorySuccessModal = true }
  const closeCreateFactorySuccessModal = () => { modalState.createFactorySuccessModal = false }

  const openAboutModal = () => { modalState.aboutModalOpen = true }
  const closeAboutModal = () => { modalState.aboutModalOpen = false }

  const openContactModal = () => { modalState.contactModalOpen = true }
  const closeContactModal = () => { modalState.contactModalOpen = false }

  const openSafetyModal = () => { modalState.safetyModalOpen = true }
  const closeSafetyModal = () => { modalState.safetyModalOpen = false }

  const openGettingStartedModal = () => { modalState.gettingStartedModalOpen = true }
  const closeGettingStartedModal = () => { modalState.gettingStartedModalOpen = false }

  const openTutorialModal = () => { modalState.tutorialModalOpen = true }
  const closeTutorialModal = () => { modalState.tutorialModalOpen = false }

  const closesupportIOSVersionModal = () => { modalState.supportIOSVersionModalOpen = false }

  const toggleSidebar = () => {
    const open = !modalState.sidebarOpen
    event('toggleSidebar', { target: open })
    modalState.sidebarOpen = open
  }

  const closeFilterModal = () => {
    event('closeFilterModal')
    modalState.filterModalOpen = false
  }
  const openFilterModal = () => {
    event('openFilterModal')
    modalState.filterModalOpen = true
  }

  const modalActions = {
    openUpdateFactorySuccessModal,
    closeUpdateFactorySuccessModal,

    openCreateFactorySuccessModal,
    closeCreateFactorySuccessModal,

    openAboutModal,
    closeAboutModal,

    openContactModal,
    closeContactModal,

    openSafetyModal,
    closeSafetyModal,

    openGettingStartedModal,
    closeGettingStartedModal,

    openTutorialModal,
    closeTutorialModal,

    toggleSidebar,
    openFilterModal,
    closeFilterModal,

    closesupportIOSVersionModal
  }

  return [modalState, modalActions]
}
