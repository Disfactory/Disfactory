import { ref, Ref } from '@vue/composition-api'

export const useModal = (defaultOpen: boolean = false) : [Ref<boolean>, { open: () => any, dismiss: () => any }] => {
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


