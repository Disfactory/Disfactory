import { ref, Ref, provide, inject, reactive } from '@vue/composition-api'
import { useGA } from './useGA'

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
    updateFactorySuccessModal: false,
    createFactorySuccessModal: false,
    aboutModalOpen: false,
    contactModalOpen: false,
    safetyModalOpen: false,
    gettingStartedModalOpen: localStorage.getItem('use-app') !== 'true',

    sidebarOpen: false,
    filterModalOpen: false,
  })

  provide(ModalStateSymbol, modalState)

  return modalState
}

type ModalState = {
  updateFactorySuccessModal: boolean,
  createFactorySuccessModal: boolean,
  aboutModalOpen: boolean,
  contactModalOpen: boolean,
  safetyModalOpen: boolean,
  gettingStartedModalOpen: boolean,

  sidebarOpen: boolean,
  filterModalOpen: boolean,
}

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
}

export const useModalState: () => [ModalState, ModalActions] = () => {
  const modalState = inject(ModalStateSymbol) as ModalState
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

    toggleSidebar,
    openFilterModal,
    closeFilterModal
  }

  return [modalState, modalActions]
}
