<template>
  <button
    :class="{ outline }"
    @click="click"
  >
    <slot />
  </button>
</template>

<script>
import { createComponent } from '@vue/composition-api'

export default createComponent({
  name: 'AppButton',
  props: {
    outline: {
      type: Boolean,
      default: false
    }
  },
  setup (_, context) {
    const click = () => {
      context.emit('click')
    }

    return {
      click
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
button {
  width: 100%;
  background-color: $primary-color;
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.5);
  border: 1px solid #fff;
  border-radius: 24px;
  padding: 10px 21px;

  color: $dark-font-color;
  font-size: 1.6rem;
  text-align: center;

  &:hover {
    cursor: pointer;
    opacity: 0.8;
  }
}

.outline {
  border: 1px solid $primary-color;
  background-color: #fff;
  color: $font-color;

  &:hover {
    cursor: pointer;
    background-color: $primary-color;
    color: $dark-font-color;
  }
}
</style>
