<template>
  <nav :class="{ dark }">
    <slot />
  </nav>
</template>

<script lang="ts">
import { createComponent, PropType, computed } from '@vue/composition-api'

export default createComponent({
  name: 'AppNavbar',
  props: {
    onMenuClick: {
      type: Function
    },
    dark: {
      type: Boolean,
      default: true
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
nav {
  width: 100%;

  user-select: none;
  font-size: 1.6rem;
  text-align: center;
  background-color: $dark-font-color;
  color: $font-color;

  padding: 11px 0;

  box-shadow: 0 2px 3px 0 rgba(0, 0, 0, 0.5);

  &.dark {
    background-color: $primary-color;
    color: $dark-font-color;
  }
}
</style>
