<template>
  <textarea
    v-bind="$attrs"
    v-model="inputValue"
    rows="7"
  />
</template>

<script>
import { computed, createComponent } from '@vue/composition-api'
export default createComponent({
  name: 'AppTextArea',
  props: {
    value: {
      type: String,
      required: true
    }
  },
  setup (props, context) {
    const inputValue = computed({
      get: () => props.value,
      set: (value) => context.emit('input', value)
    })

    return {
      inputValue
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
textarea {
  border: 1px solid $second-color;
  border-radius: 4px;
  padding: 10px 15px;
  outline: none;
  resize: none;

  width: 100%;

  font-size: $form-font-size;

  &::placeholder {
    color: rgb(186, 186, 186);
  }
}
</style>
